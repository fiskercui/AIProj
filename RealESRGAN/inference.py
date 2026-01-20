"""
RealESRGAN Image Upscaling Inference Script
使用预训练的RealESRGAN模型进行图像无损缩放
"""

import os
import cv2
import torch
import numpy as np
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
import argparse


def download_model(model_name, model_path):
    """下载预训练模型"""
    from urllib.request import urlretrieve
    
    model_urls = {
        'RealESRGAN_x4plus': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
        'RealESRGAN_x4plus_anime_6B': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth',
        'RealESRGAN_x2plus': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth',
    }
    
    if model_name not in model_urls:
        raise ValueError(f"Model {model_name} not found. Available models: {list(model_urls.keys())}")
    
    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model...")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        urlretrieve(model_urls[model_name], model_path)
        print(f"Model downloaded to {model_path}")


def upscale_image(input_path, output_path, model_name='RealESRGAN_x4plus', scale=4, gpu_id=None):
    """
    使用RealESRGAN模型放大图像
    
    Args:
        input_path: 输入图像路径
        output_path: 输出图像路径
        model_name: 模型名称 ('RealESRGAN_x4plus', 'RealESRGAN_x4plus_anime_6B', 'RealESRGAN_x2plus')
        scale: 放大倍数 (2 or 4)
        gpu_id: GPU ID，如果为None则使用CPU
    """
    
    # 确定模型路径
    model_path = os.path.join('models', f'{model_name}.pth')
    
    # 下载模型（如果不存在）
    try:
        download_model(model_name, model_path)
    except Exception as e:
        print(f"Warning: Could not download model automatically: {e}")
        print("Please download the model manually from GitHub and place it in the 'models' folder")
        return
    
    # 设置设备
    if gpu_id is not None and torch.cuda.is_available():
        device = torch.device(f'cuda:{gpu_id}')
        print(f"Using GPU: {gpu_id}")
    else:
        device = torch.device('cpu')
        print("Using CPU")
    
    # 根据模型名称选择网络架构
    if model_name == 'RealESRGAN_x4plus':
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name == 'RealESRGAN_x4plus_anime_6B':
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
    elif model_name == 'RealESRGAN_x2plus':
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        netscale = 2
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    
    # 创建upsampler
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        model=model,
        tile=400,  # 瓦片大小，如果内存不足可以调小
        tile_pad=10,
        pre_pad=0,
        half=False if device.type == 'cpu' else True,  # CPU不支持half精度
        device=device
    )
    
    # 读取输入图像
    print(f"Reading image: {input_path}")
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {input_path}")
    
    # 执行超分辨率
    print("Upscaling image...")
    try:
        output, _ = upsampler.enhance(img, outscale=scale)
    except RuntimeError as error:
        print(f'Error: {error}')
        print('If you encounter CUDA out of memory, try reducing the tile size')
        return
    
    # 保存输出图像
    print(f"Saving image: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, output)
    print(f"Successfully upscaled image saved to {output_path}")


def batch_upscale(input_dir, output_dir, model_name='RealESRGAN_x4plus', scale=4, gpu_id=None):
    """
    批量处理文件夹中的所有图像
    
    Args:
        input_dir: 输入图像文件夹
        output_dir: 输出图像文件夹
        model_name: 模型名称
        scale: 放大倍数
        gpu_id: GPU ID
    """
    
    # 支持的图像格式
    img_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # 获取所有图像文件
    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in img_extensions:
                image_files.append(os.path.join(root, file))
    
    if not image_files:
        print(f"No images found in {input_dir}")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    # 处理每个图像
    for i, img_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {img_path}")
        
        # 生成输出路径
        rel_path = os.path.relpath(img_path, input_dir)
        output_path = os.path.join(output_dir, rel_path)
        output_path = os.path.splitext(output_path)[0] + '_upscaled' + os.path.splitext(output_path)[1]
        
        try:
            upscale_image(img_path, output_path, model_name, scale, gpu_id)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue


def main():
    parser = argparse.ArgumentParser(description='RealESRGAN Image Upscaling')
    parser.add_argument('-i', '--input', type=str, required=True, 
                        help='Input image or folder path')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output image or folder path')
    parser.add_argument('-m', '--model', type=str, default='RealESRGAN_x4plus',
                        choices=['RealESRGAN_x4plus', 'RealESRGAN_x4plus_anime_6B', 'RealESRGAN_x2plus'],
                        help='Model name')
    parser.add_argument('-s', '--scale', type=int, default=4,
                        help='Upscaling factor (2 or 4)')
    parser.add_argument('-g', '--gpu-id', type=int, default=None,
                        help='GPU device ID (default: use CPU)')
    
    args = parser.parse_args()
    
    # 检查输入是文件还是文件夹
    if os.path.isfile(args.input):
        # 单个文件处理
        upscale_image(args.input, args.output, args.model, args.scale, args.gpu_id)
    elif os.path.isdir(args.input):
        # 批量处理
        batch_upscale(args.input, args.output, args.model, args.scale, args.gpu_id)
    else:
        print(f"Error: {args.input} is not a valid file or directory")


if __name__ == '__main__':
    main()
