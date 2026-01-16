"""
ESRGAN 训练脚本
"""

import os
import argparse
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import time

from models import ESRGAN
from utils import ImageDataset


class PerceptualLoss(nn.Module):
    """
    感知损失 (Perceptual Loss)
    使用 VGG 网络提取的特征计算损失
    """
    
    def __init__(self):
        super(PerceptualLoss, self).__init__()
        # 这里可以加载 VGG 网络，为简化暂时使用 L1 损失
        self.criterion = nn.L1Loss()
    
    def forward(self, pred, target):
        return self.criterion(pred, target)


class Trainer:
    """训练器类"""
    
    def __init__(self, config_path='config.yaml'):
        """
        初始化训练器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 设置设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        if self.device.type == 'cpu':
            print("警告: 未检测到 GPU，训练将非常缓慢。建议使用 NVIDIA GPU。")
        
        # 创建模型
        self.model = self._create_model()
        
        # 创建数据加载器
        self.train_loader = self._create_dataloader()
        
        # 损失函数
        self.pixel_loss = nn.L1Loss()
        self.perceptual_loss = PerceptualLoss()
        
        # 优化器
        self.optimizer = self._create_optimizer()
        
        # 学习率调度器
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer, 
            step_size=50, 
            gamma=0.5
        )
        
        # TensorBoard
        self.writer = SummaryWriter('runs/esrgan_training')
        
        # 训练状态
        self.epoch = 0
        self.global_step = 0
        
        print("训练器初始化完成！")
    
    def _create_model(self):
        """创建模型"""
        model_cfg = self.config['model']
        
        model = ESRGAN(
            in_channels=model_cfg['num_channels'],
            out_channels=model_cfg['num_channels'],
            num_features=model_cfg['num_features'],
            num_blocks=model_cfg['num_blocks'],
            scale=model_cfg['scale']
        ).to(self.device)
        
        # 统计参数
        total, trainable = model.count_parameters()
        
        return model
    
    def _create_dataloader(self):
        """创建数据加载器"""
        train_cfg = self.config['train']
        data_cfg = self.config['data']
        
        dataset = ImageDataset(
            image_dir=data_cfg['train_dir'],
            scale=self.config['model']['scale'],
            hr_size=data_cfg['hr_size'],
            augment=True
        )
        
        if len(dataset) == 0:
            print("错误: 训练数据集为空！")
            print(f"请将训练图像放入: {data_cfg['train_dir']}")
            print("支持的格式: .jpg, .png, .bmp, .tif")
            raise ValueError("训练数据集为空")
        
        dataloader = DataLoader(
            dataset,
            batch_size=train_cfg['batch_size'],
            shuffle=True,
            num_workers=train_cfg['num_workers'],
            pin_memory=True if self.device.type == 'cuda' else False
        )
        
        print(f"训练数据集大小: {len(dataset)}")
        print(f"批次数量: {len(dataloader)}")
        
        return dataloader
    
    def _create_optimizer(self):
        """创建优化器"""
        train_cfg = self.config['train']
        opt_cfg = self.config['optimizer']
        
        optimizer = optim.Adam(
            self.model.parameters(),
            lr=train_cfg['learning_rate'],
            betas=opt_cfg['betas']
        )
        
        return optimizer
    
    def train_epoch(self):
        """训练一个 epoch"""
        self.model.train()
        
        epoch_pixel_loss = 0.0
        epoch_perceptual_loss = 0.0
        epoch_total_loss = 0.0
        
        # 进度条
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.epoch+1}")
        
        for batch_idx, (lr_imgs, hr_imgs) in enumerate(pbar):
            # 数据移到设备
            lr_imgs = lr_imgs.to(self.device)
            hr_imgs = hr_imgs.to(self.device)
            
            # 前向传播
            sr_imgs = self.model(lr_imgs)
            
            # 计算损失
            loss_cfg = self.config['loss']
            
            pixel_loss = self.pixel_loss(sr_imgs, hr_imgs)
            perceptual_loss = self.perceptual_loss(sr_imgs, hr_imgs)
            
            total_loss = (
                loss_cfg['pixel_weight'] * pixel_loss +
                loss_cfg['perceptual_weight'] * perceptual_loss
            )
            
            # 反向传播
            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()
            
            # 统计
            epoch_pixel_loss += pixel_loss.item()
            epoch_perceptual_loss += perceptual_loss.item()
            epoch_total_loss += total_loss.item()
            
            # 更新进度条
            pbar.set_postfix({
                'loss': f"{total_loss.item():.4f}",
                'pixel': f"{pixel_loss.item():.4f}",
                'percep': f"{perceptual_loss.item():.4f}"
            })
            
            # TensorBoard 记录
            if self.global_step % 10 == 0:
                self.writer.add_scalar('Loss/pixel', pixel_loss.item(), self.global_step)
                self.writer.add_scalar('Loss/perceptual', perceptual_loss.item(), self.global_step)
                self.writer.add_scalar('Loss/total', total_loss.item(), self.global_step)
            
            self.global_step += 1
        
        # 计算平均损失
        num_batches = len(self.train_loader)
        avg_pixel_loss = epoch_pixel_loss / num_batches
        avg_perceptual_loss = epoch_perceptual_loss / num_batches
        avg_total_loss = epoch_total_loss / num_batches
        
        return avg_pixel_loss, avg_perceptual_loss, avg_total_loss
    
    def save_checkpoint(self, filename='checkpoint.pth'):
        """保存检查点"""
        checkpoint_dir = './checkpoints'
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_path = os.path.join(checkpoint_dir, filename)
        
        checkpoint = {
            'epoch': self.epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': self.config
        }
        
        torch.save(checkpoint, checkpoint_path)
        print(f"检查点已保存: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path):
        """加载检查点"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.epoch = checkpoint['epoch']
        self.global_step = checkpoint['global_step']
        
        print(f"成功加载检查点: {checkpoint_path}")
        print(f"从 epoch {self.epoch} 继续训练")
    
    def train(self, num_epochs=None):
        """
        开始训练
        
        Args:
            num_epochs: 训练轮数，如果为 None 则使用配置文件中的值
        """
        if num_epochs is None:
            num_epochs = self.config['train']['epochs']
        
        save_interval = self.config['train']['save_interval']
        
        print("\n" + "="*50)
        print("开始训练 ESRGAN 模型")
        print("="*50)
        print(f"总 epoch 数: {num_epochs}")
        print(f"保存间隔: 每 {save_interval} epoch")
        print(f"设备: {self.device}")
        print("="*50 + "\n")
        
        start_time = time.time()
        
        try:
            for epoch in range(self.epoch, num_epochs):
                self.epoch = epoch
                
                # 训练一个 epoch
                pixel_loss, perceptual_loss, total_loss = self.train_epoch()
                
                # 更新学习率
                self.scheduler.step()
                current_lr = self.optimizer.param_groups[0]['lr']
                
                # 打印信息
                print(f"\nEpoch {epoch+1}/{num_epochs}:")
                print(f"  Pixel Loss: {pixel_loss:.4f}")
                print(f"  Perceptual Loss: {perceptual_loss:.4f}")
                print(f"  Total Loss: {total_loss:.4f}")
                print(f"  Learning Rate: {current_lr:.6f}")
                
                # TensorBoard
                self.writer.add_scalar('Epoch/pixel_loss', pixel_loss, epoch)
                self.writer.add_scalar('Epoch/perceptual_loss', perceptual_loss, epoch)
                self.writer.add_scalar('Epoch/total_loss', total_loss, epoch)
                self.writer.add_scalar('Epoch/learning_rate', current_lr, epoch)
                
                # 定期保存
                if (epoch + 1) % save_interval == 0:
                    self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth')
            
            # 训练完成
            elapsed_time = time.time() - start_time
            print("\n" + "="*50)
            print("训练完成！")
            print(f"总用时: {elapsed_time/3600:.2f} 小时")
            print("="*50)
            
            # 保存最终模型
            self.save_checkpoint('final_model.pth')
            
        except KeyboardInterrupt:
            print("\n训练被中断！")
            self.save_checkpoint('interrupted_checkpoint.pth')
        
        finally:
            self.writer.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='训练 ESRGAN 模型')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--epochs', type=int, default=None, help='训练轮数')
    parser.add_argument('--resume', type=str, default=None, help='恢复训练的检查点路径')
    
    args = parser.parse_args()
    
    # 创建训练器
    trainer = Trainer(config_path=args.config)
    
    # 恢复训练（如果指定）
    if args.resume:
        trainer.load_checkpoint(args.resume)
    
    # 开始训练
    trainer.train(num_epochs=args.epochs)


if __name__ == "__main__":
    main()
