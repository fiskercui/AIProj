"""
图像处理工具函数
"""

import cv2
import numpy as np
import torch
from PIL import Image
from typing import Union, Tuple


def load_image(image_path: str, mode: str = 'RGB') -> np.ndarray:
    """
    加载图像
    
    Args:
        image_path: 图像路径
        mode: 颜色模式 ('RGB' 或 'BGR')
    
    Returns:
        图像数组 (H, W, C)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法加载图像: {image_path}")
        
        if mode == 'RGB':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        return img
    except Exception as e:
        print(f"加载图像出错: {e}")
        raise


def save_image(image: Union[np.ndarray, torch.Tensor], save_path: str, mode: str = 'RGB'):
    """
    保存图像
    
    Args:
        image: 图像数据 (numpy array 或 torch tensor)
        save_path: 保存路径
        mode: 颜色模式 ('RGB' 或 'BGR')
    """
    try:
        # 如果是 tensor，先转换为 numpy
        if isinstance(image, torch.Tensor):
            image = tensor_to_image(image)
        
        # 确保数据类型正确
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        # 转换颜色空间
        if mode == 'RGB':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        cv2.imwrite(save_path, image)
        print(f"图像已保存到: {save_path}")
    except Exception as e:
        print(f"保存图像出错: {e}")
        raise


def image_to_tensor(image: np.ndarray, normalize: bool = True) -> torch.Tensor:
    """
    将图像转换为 PyTorch tensor
    
    Args:
        image: numpy 图像数组 (H, W, C), 范围 [0, 255]
        normalize: 是否归一化到 [0, 1]
    
    Returns:
        tensor (1, C, H, W)
    """
    # 转换为 float32
    img = image.astype(np.float32)
    
    if normalize:
        img = img / 255.0
    
    # 转换维度: (H, W, C) -> (C, H, W)
    img = np.transpose(img, (2, 0, 1))
    
    # 转换为 tensor 并添加 batch 维度
    tensor = torch.from_numpy(img).unsqueeze(0)
    
    return tensor


def tensor_to_image(tensor: torch.Tensor, denormalize: bool = True) -> np.ndarray:
    """
    将 PyTorch tensor 转换为图像
    
    Args:
        tensor: PyTorch tensor (B, C, H, W) 或 (C, H, W)
        denormalize: 是否从 [0, 1] 反归一化到 [0, 255]
    
    Returns:
        numpy 图像数组 (H, W, C)
    """
    # 移除 batch 维度（如果有）
    if tensor.dim() == 4:
        tensor = tensor.squeeze(0)
    
    # 转移到 CPU 并转换为 numpy
    img = tensor.detach().cpu().numpy()
    
    # 转换维度: (C, H, W) -> (H, W, C)
    img = np.transpose(img, (1, 2, 0))
    
    if denormalize:
        img = img * 255.0
    
    # 裁剪到有效范围并转换为 uint8
    img = np.clip(img, 0, 255).astype(np.uint8)
    
    return img


def resize_image(image: np.ndarray, size: Tuple[int, int], interpolation=cv2.INTER_CUBIC) -> np.ndarray:
    """
    调整图像大小
    
    Args:
        image: 输入图像
        size: 目标大小 (width, height)
        interpolation: 插值方法
    
    Returns:
        调整大小后的图像
    """
    return cv2.resize(image, size, interpolation=interpolation)


def calculate_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    计算 PSNR (峰值信噪比)
    
    Args:
        img1: 第一张图像
        img2: 第二张图像
    
    Returns:
        PSNR 值 (dB)
    """
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr


if __name__ == "__main__":
    # 测试代码
    print("图像处理工具模块加载成功！")
