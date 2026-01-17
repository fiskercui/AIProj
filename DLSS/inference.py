"""
ESRGAN 推理脚本
用于使用训练好的模型进行图像超分辨率处理
"""

import os
import argparse
import time
import torch
import yaml

from models import ESRGAN
from utils import load_image, save_image, image_to_tensor, tensor_to_image, calculate_psnr


class Inferencer:
    """推理器类"""
    
    def __init__(self, checkpoint_path, config_path='config.yaml', device=None):
        """
        初始化推理器
        
        Args:
            checkpoint_path: 模型权重文件路径
            config_path: 配置文件路径
            device: 计算设备 ('cuda' 或 'cpu')
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 设置设备
        if device is None:
            device = self.config['inference']['device']
        
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
        # 创建模型
        self.model = self._create_model()
        
        # 加载权重
        self._load_checkpoint(checkpoint_path)
        
        print("推理器初始化完成！")
    
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
        
        model.eval()  # 设置为评估模式
        
        return model
    
    def _load_checkpoint(self, checkpoint_path):
        """加载模型权重"""
        if not os.path.exists(checkpoint_path):
            print(f"警告: 权重文件不存在: {checkpoint_path}")
            print("将使用随机初始化的权重（输出质量会很差）")
            print("\n提示: 你可以:")
            print("  1. 训练自己的模型: python train.py")
            print("  2. 下载预训练模型并放到 checkpoints/ 目录")
            return
        
        try:
            checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
            
            # 处理不同格式的权重文件
            state_dict = None
            
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'params_ema' in checkpoint:
                # Real-ESRGAN 格式
                state_dict = checkpoint['params_ema']
            elif 'params' in checkpoint:
                state_dict = checkpoint['params']
            else:
                state_dict = checkpoint
            
            # 智能转换键名
            converted_state_dict = {}
            for k, v in state_dict.items():
                new_k = k
                
                # 移除 generator 前缀
                if new_k.startswith('generator.'):
                    new_k = new_k.replace('generator.', '')
                
                # 转换 body -> rrdb_blocks
                if '.body.' in new_k:
                    new_k = new_k.replace('.body.', '.rrdb_blocks.')
                elif new_k.startswith('body.'):
                    new_k = new_k.replace('body.', 'generator.rrdb_blocks.')
                
                # 转换 conv_body -> conv_body
                if 'conv_body' in new_k and not new_k.startswith('generator.'):
                    new_k = 'generator.' + new_k
                    
                # 转换 conv_first
                if 'conv_first' in new_k and not new_k.startswith('generator.'):
                    new_k = 'generator.' + new_k
                
                # 转换上采样层
                if 'upconv' in new_k and not new_k.startswith('generator.'):
                    new_k = 'generator.' + new_k
                if 'conv_hr' in new_k and not new_k.startswith('generator.'):
                    new_k = 'generator.' + new_k
                if 'conv_last' in new_k and not new_k.startswith('generator.'):
                    new_k = 'generator.' + new_k
                
                converted_state_dict[new_k] = v
            
            state_dict = converted_state_dict
            
            # 尝试加载权重
            try:
                self.model.load_state_dict(state_dict, strict=True)
                print(f"成功加载模型权重: {checkpoint_path}")
            except RuntimeError as e:
                # 如果严格模式失败，尝试非严格模式
                print(f"警告: 权重部分不匹配，尝试非严格加载...")
                missing_keys, unexpected_keys = self.model.load_state_dict(state_dict, strict=False)
                
                if missing_keys:
                    print(f"  缺失的键 ({len(missing_keys)}): {missing_keys[:5]}...")
                if unexpected_keys:
                    print(f"  意外的键 ({len(unexpected_keys)}): {unexpected_keys[:5]}...")
                
                print("已加载兼容的权重部分")
                
        except Exception as e:
            print(f"加载权重时出错: {e}")
            print("将使用随机初始化的权重")
    
    def upscale(self, image_path, output_path=None):
        """
        对单张图像进行超分辨率处理
        
        Args:
            image_path: 输入图像路径
            output_path: 输出图像路径（如果为 None，自动生成）
        
        Returns:
            output_path: 输出图像的保存路径
        """
        print(f"\n处理图像: {image_path}")
        
        # 加载图像
        try:
            lr_image = load_image(image_path, mode='RGB')
        except Exception as e:
            print(f"无法加载图像: {e}")
            return None
        
        print(f"输入尺寸: {lr_image.shape[1]}x{lr_image.shape[0]}")
        
        # 转换为 tensor
        lr_tensor = image_to_tensor(lr_image, normalize=True).to(self.device)
        
        # 推理
        start_time = time.time()
        
        with torch.no_grad():
            sr_tensor = self.model(lr_tensor)
        
        inference_time = time.time() - start_time
        
        # 转换回图像
        sr_image = tensor_to_image(sr_tensor, denormalize=True)
        
        print(f"输出尺寸: {sr_image.shape[1]}x{sr_image.shape[0]}")
        print(f"推理用时: {inference_time:.3f} 秒")
        
        # 保存图像
        if output_path is None:
            # 自动生成输出路径
            output_dir = self.config['inference']['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_sr{ext}")
        else:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        save_image(sr_image, output_path, mode='RGB')
        
        return output_path
    
    def upscale_batch(self, input_dir, output_dir=None):
        """
        批量处理目录中的所有图像
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
        """
        if output_dir is None:
            output_dir = self.config['inference']['output_dir']
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有图像文件
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
        image_files = []
        
        for file in os.listdir(input_dir):
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_extensions:
                image_files.append(os.path.join(input_dir, file))
        
        if len(image_files) == 0:
            print(f"在 {input_dir} 中未找到图像文件")
            return
        
        print(f"\n找到 {len(image_files)} 张图像")
        print("="*50)
        
        # 批量处理
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}]")
            
            filename = os.path.basename(image_path)
            output_path = os.path.join(output_dir, filename)
            
            self.upscale(image_path, output_path)
        
        print("\n" + "="*50)
        print(f"批量处理完成！结果已保存到: {output_dir}")
    
    def compare_quality(self, lr_image_path, hr_image_path):
        """
        比较超分辨率结果与原始高分辨率图像的质量
        
        Args:
            lr_image_path: 低分辨率图像路径
            hr_image_path: 高分辨率图像路径（ground truth）
        """
        # 加载图像
        lr_image = load_image(lr_image_path, mode='RGB')
        hr_image = load_image(hr_image_path, mode='RGB')
        
        # 推理
        lr_tensor = image_to_tensor(lr_image, normalize=True).to(self.device)
        
        with torch.no_grad():
            sr_tensor = self.model(lr_tensor)
        
        sr_image = tensor_to_image(sr_tensor, denormalize=True)
        
        # 计算 PSNR
        if sr_image.shape[:2] != hr_image.shape[:2]:
            print("警告: 超分辨率图像和原始高分辨率图像尺寸不匹配")
            print(f"SR: {sr_image.shape[:2]}, HR: {hr_image.shape[:2]}")
        else:
            psnr = calculate_psnr(sr_image, hr_image)
            print(f"\nPSNR: {psnr:.2f} dB")
        
        return sr_image


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ESRGAN 图像超分辨率推理')
    parser.add_argument('--input', type=str, required=True, help='输入图像路径或目录')
    parser.add_argument('--output', type=str, default=None, help='输出路径')
    parser.add_argument('--checkpoint', type=str, default='./checkpoints/final_model.pth', 
                       help='模型权重路径')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--device', type=str, default=None, choices=['cuda', 'cpu'],
                       help='计算设备')
    parser.add_argument('--batch', action='store_true', help='批量处理目录')
    
    args = parser.parse_args()
    
    # 创建推理器
    inferencer = Inferencer(
        checkpoint_path=args.checkpoint,
        config_path=args.config,
        device=args.device
    )
    
    # 推理
    if args.batch or os.path.isdir(args.input):
        # 批量处理
        inferencer.upscale_batch(args.input, args.output)
    else:
        # 单张图像
        output_path = inferencer.upscale(args.input, args.output)
        
        if output_path:
            print(f"\n✓ 处理完成！")
            print(f"  输入: {args.input}")
            print(f"  输出: {output_path}")


if __name__ == "__main__":
    main()
