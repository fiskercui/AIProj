"""
DLSS 项目使用示例
展示如何在 Python 代码中使用模型
"""

import torch
from models import ESRGAN
from utils import load_image, save_image, image_to_tensor, tensor_to_image


def example_1_basic_inference():
    """
    示例 1: 基础推理
    对单张图像进行超分辨率处理
    """
    print("="*60)
    print("示例 1: 基础推理")
    print("="*60)
    
    # 1. 创建模型
    model = ESRGAN(scale=4, num_blocks=23)
    model.eval()
    
    # 2. 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    print(f"使用设备: {device}")
    
    # 3. 加载图像（假设图像存在）
    try:
        lr_image = load_image('data/test/input.png', mode='RGB')
        print(f"输入尺寸: {lr_image.shape}")
    except:
        print("提示: 请将测试图像放到 data/test/input.png")
        return
    
    # 4. 图像转 tensor
    lr_tensor = image_to_tensor(lr_image, normalize=True).to(device)
    
    # 5. 推理
    with torch.no_grad():
        sr_tensor = model(lr_tensor)
    
    # 6. tensor 转图像
    sr_image = tensor_to_image(sr_tensor, denormalize=True)
    print(f"输出尺寸: {sr_image.shape}")
    
    # 7. 保存结果
    save_image(sr_image, 'results/output_basic.png', mode='RGB')
    print("✓ 结果已保存到 results/output_basic.png")


def example_2_load_pretrained():
    """
    示例 2: 加载预训练模型
    """
    print("\n" + "="*60)
    print("示例 2: 加载预训练模型")
    print("="*60)
    
    # 1. 创建模型
    model = ESRGAN(scale=4)
    
    # 2. 加载预训练权重
    checkpoint_path = 'checkpoints/final_model.pth'
    
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        print(f"✓ 成功加载模型: {checkpoint_path}")
        
        # 显示训练信息（如果有）
        if 'epoch' in checkpoint:
            print(f"  训练轮数: {checkpoint['epoch']}")
        
    except FileNotFoundError:
        print(f"✗ 模型文件不存在: {checkpoint_path}")
        print("  请先训练模型或下载预训练权重")


def example_3_batch_processing():
    """
    示例 3: 批量处理多张图像
    """
    print("\n" + "="*60)
    print("示例 3: 批量处理")
    print("="*60)
    
    # 创建模型
    model = ESRGAN(scale=4, num_blocks=23)
    model.eval()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # 批量加载图像
    image_paths = [
        'data/test/image1.png',
        'data/test/image2.png',
        'data/test/image3.png',
    ]
    
    for i, path in enumerate(image_paths, 1):
        try:
            # 加载图像
            lr_image = load_image(path, mode='RGB')
            
            # 转换并推理
            lr_tensor = image_to_tensor(lr_image, normalize=True).to(device)
            
            with torch.no_grad():
                sr_tensor = model(lr_tensor)
            
            # 保存结果
            sr_image = tensor_to_image(sr_tensor, denormalize=True)
            output_path = f'results/output_{i}.png'
            save_image(sr_image, output_path, mode='RGB')
            
            print(f"✓ 处理完成: {path} -> {output_path}")
            
        except Exception as e:
            print(f"✗ 处理失败 {path}: {e}")


def example_4_quality_comparison():
    """
    示例 4: 图像质量对比
    计算 PSNR 指标
    """
    print("\n" + "="*60)
    print("示例 4: 图像质量对比")
    print("="*60)
    
    from utils import calculate_psnr
    
    # 加载原始高分辨率图像和超分辨率结果
    try:
        hr_image = load_image('data/test/ground_truth.png', mode='RGB')
        sr_image = load_image('results/output_basic.png', mode='RGB')
        
        # 计算 PSNR
        psnr = calculate_psnr(hr_image, sr_image)
        
        print(f"图像质量指标:")
        print(f"  PSNR: {psnr:.2f} dB")
        
        if psnr > 40:
            print("  评价: 优秀 ⭐⭐⭐⭐⭐")
        elif psnr > 35:
            print("  评价: 良好 ⭐⭐⭐⭐")
        elif psnr > 30:
            print("  评价: 一般 ⭐⭐⭐")
        else:
            print("  评价: 较差 ⭐⭐")
            
    except Exception as e:
        print(f"提示: {e}")
        print("需要提供 ground truth 图像用于对比")


def example_5_custom_config():
    """
    示例 5: 自定义模型配置
    """
    print("\n" + "="*60)
    print("示例 5: 自定义模型配置")
    print("="*60)
    
    # 创建不同配置的模型
    configs = [
        {'scale': 2, 'num_blocks': 16, 'num_features': 64, 'desc': '轻量级 2x'},
        {'scale': 4, 'num_blocks': 23, 'num_features': 64, 'desc': '标准 4x'},
        {'scale': 8, 'num_blocks': 23, 'num_features': 64, 'desc': '高倍 8x'},
    ]
    
    for cfg in configs:
        model = ESRGAN(
            scale=cfg['scale'],
            num_blocks=cfg['num_blocks'],
            num_features=cfg['num_features']
        )
        
        total, trainable = model.count_parameters()
        
        print(f"\n{cfg['desc']}:")
        print(f"  放大倍数: {cfg['scale']}x")
        print(f"  网络块数: {cfg['num_blocks']}")
        print(f"  特征通道: {cfg['num_features']}")
        print(f"  总参数: {total:,}")


def example_6_performance_test():
    """
    示例 6: 性能测试
    测量推理速度
    """
    print("\n" + "="*60)
    print("示例 6: 性能测试")
    print("="*60)
    
    import time
    
    # 创建模型
    model = ESRGAN(scale=4)
    model.eval()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # 测试不同尺寸
    test_sizes = [
        (1, 3, 64, 64),
        (1, 3, 128, 128),
        (1, 3, 256, 256),
    ]
    
    for size in test_sizes:
        # 创建随机输入
        x = torch.randn(size).to(device)
        
        # 预热
        with torch.no_grad():
            _ = model(x)
        
        # 测试
        num_runs = 10
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(num_runs):
                _ = model(x)
        
        total_time = time.time() - start_time
        avg_time = total_time / num_runs
        
        print(f"\n输入尺寸: {size[2]}x{size[3]}")
        print(f"  输出尺寸: {size[2]*4}x{size[3]*4}")
        print(f"  平均时间: {avg_time*1000:.2f} ms")
        print(f"  FPS: {1/avg_time:.2f}")


def main():
    """运行所有示例"""
    print("\n" + "#"*60)
    print("# DLSS 项目使用示例")
    print("#"*60 + "\n")
    
    # 示例 1: 基础推理
    example_1_basic_inference()
    
    # 示例 2: 加载预训练模型
    example_2_load_pretrained()
    
    # 示例 3: 批量处理
    # example_3_batch_processing()  # 需要多张图像
    
    # 示例 4: 质量对比
    # example_4_quality_comparison()  # 需要 ground truth
    
    # 示例 5: 自定义配置
    example_5_custom_config()
    
    # 示例 6: 性能测试
    example_6_performance_test()
    
    print("\n" + "="*60)
    print("所有示例运行完成！")
    print("="*60)
    print("\n更多用法请参考 USAGE_GUIDE.md")


if __name__ == "__main__":
    main()
