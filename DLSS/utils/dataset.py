"""
数据集处理模块
"""

import os
import random
import numpy as np
import torch
from torch.utils.data import Dataset
from typing import Tuple, Optional
from .image_utils import load_image, image_to_tensor, resize_image
import cv2


class ImageDataset(Dataset):
    """
    超分辨率数据集类
    用于加载高分辨率图像并自动生成对应的低分辨率图像
    """
    
    def __init__(
        self, 
        image_dir: str, 
        scale: int = 4,
        hr_size: int = 256,
        augment: bool = True
    ):
        """
        Args:
            image_dir: 图像目录路径
            scale: 放大倍数
            hr_size: 高分辨率图像裁剪大小
            augment: 是否进行数据增强
        """
        self.image_dir = image_dir
        self.scale = scale
        self.hr_size = hr_size
        self.lr_size = hr_size // scale
        self.augment = augment
        
        # 获取所有图像文件
        self.image_files = self._get_image_files()
        
        if len(self.image_files) == 0:
            print(f"警告: 在 {image_dir} 中未找到图像文件")
        else:
            print(f"加载了 {len(self.image_files)} 张图像")
    
    def _get_image_files(self):
        """获取目录中所有图像文件"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
        image_files = []
        
        if not os.path.exists(self.image_dir):
            print(f"警告: 目录不存在 {self.image_dir}")
            return image_files
        
        for root, _, files in os.walk(self.image_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_extensions:
                    image_files.append(os.path.join(root, file))
        
        return sorted(image_files)
    
    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        获取一对低分辨率和高分辨率图像
        
        Returns:
            lr_tensor: 低分辨率图像 tensor (C, H, W)
            hr_tensor: 高分辨率图像 tensor (C, H, W)
        """
        # 加载图像
        img_path = self.image_files[idx]
        hr_img = load_image(img_path, mode='RGB')
        
        # 随机裁剪
        hr_img = self._random_crop(hr_img, self.hr_size)
        
        # 数据增强
        if self.augment:
            hr_img = self._augment(hr_img)
        
        # 生成低分辨率图像
        lr_img = self._generate_lr(hr_img)
        
        # 转换为 tensor
        hr_tensor = image_to_tensor(hr_img, normalize=True).squeeze(0)
        lr_tensor = image_to_tensor(lr_img, normalize=True).squeeze(0)
        
        return lr_tensor, hr_tensor
    
    def _random_crop(self, image: np.ndarray, size: int) -> np.ndarray:
        """随机裁剪图像"""
        h, w = image.shape[:2]
        
        if h < size or w < size:
            # 如果图像太小，先放大
            scale = max(size / h, size / w)
            new_h, new_w = int(h * scale) + 1, int(w * scale) + 1
            image = resize_image(image, (new_w, new_h))
            h, w = image.shape[:2]
        
        # 随机选择裁剪位置
        top = random.randint(0, h - size)
        left = random.randint(0, w - size)
        
        return image[top:top+size, left:left+size]
    
    def _augment(self, image: np.ndarray) -> np.ndarray:
        """数据增强：随机翻转和旋转"""
        # 随机水平翻转
        if random.random() > 0.5:
            image = np.fliplr(image)
        
        # 随机垂直翻转
        if random.random() > 0.5:
            image = np.flipud(image)
        
        # 随机旋转 90 度
        if random.random() > 0.5:
            image = np.rot90(image)
        
        return image.copy()
    
    def _generate_lr(self, hr_img: np.ndarray) -> np.ndarray:
        """
        从高分辨率图像生成低分辨率图像
        模拟下采样过程
        """
        h, w = hr_img.shape[:2]
        lr_h, lr_w = h // self.scale, w // self.scale
        
        # 使用双三次插值下采样
        lr_img = resize_image(hr_img, (lr_w, lr_h), cv2.INTER_CUBIC)
        
        return lr_img


class SingleImageDataset(Dataset):
    """
    单图像测试数据集
    用于推理时处理单张图像
    """
    
    def __init__(self, image_path: str):
        """
        Args:
            image_path: 图像路径
        """
        self.image = load_image(image_path, mode='RGB')
    
    def __len__(self):
        return 1
    
    def __getitem__(self, idx: int) -> torch.Tensor:
        """返回图像 tensor"""
        tensor = image_to_tensor(self.image, normalize=True).squeeze(0)
        return tensor


if __name__ == "__main__":
    # 测试代码
    print("数据集模块加载成功！")
