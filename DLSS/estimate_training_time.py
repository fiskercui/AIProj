"""
训练时间估算工具
根据数据集大小和硬件配置估算训练时间
"""

import os
import sys
from pathlib import Path
import torch

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def estimate_time():
    """估算训练时间"""
    print("="*60)
    print("训练时间估算工具")
    print("="*60)
    
    # 1. 检查数据集
    train_dir = Path("data/train")
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    
    images = []
    if train_dir.exists():
        for ext in valid_extensions:
            images.extend(train_dir.glob(f"*{ext}"))
            images.extend(train_dir.glob(f"*{ext.upper()}"))
    
    num_images = len(images)
    
    print(f"\n1. 数据集信息:")
    print(f"   图像数量: {num_images} 张")
    
    if num_images == 0:
        print("\n错误: 未找到训练图像！")
        print("请先准备数据集，运行: python check_dataset.py")
        return
    
    # 2. 检查硬件
    has_gpu = torch.cuda.is_available()
    print(f"\n2. 硬件配置:")
    
    if has_gpu:
        gpu_name = torch.cuda.get_device_name(0)
        print(f"   GPU: {gpu_name}")
        
        # 根据 GPU 型号估算性能系数
        if "4090" in gpu_name or "4080" in gpu_name:
            gpu_factor = 1.0  # 最快
        elif "3090" in gpu_name or "3080" in gpu_name:
            gpu_factor = 1.5
        elif "3070" in gpu_name or "3060" in gpu_name:
            gpu_factor = 2.0
        elif "2080" in gpu_name or "2070" in gpu_name:
            gpu_factor = 2.5
        elif "1080" in gpu_name or "1070" in gpu_name:
            gpu_factor = 3.0
        elif "1060" in gpu_name or "1050" in gpu_name:
            gpu_factor = 4.0
        else:
            gpu_factor = 3.0  # 默认中等速度
    else:
        print(f"   GPU: 不可用")
        print(f"   CPU: 将使用 CPU 训练")
        gpu_factor = 50.0  # CPU 比 GPU 慢 50 倍左右
    
    # 3. 读取配置
    import yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    batch_size = config['train']['batch_size']
    epochs = config['train']['epochs']
    
    print(f"\n3. 训练配置:")
    print(f"   批次大小: {batch_size}")
    print(f"   训练轮数: {epochs}")
    
    # 4. 估算时间
    print(f"\n4. 时间估算:")
    
    # 每个 epoch 的迭代次数
    iterations_per_epoch = num_images // batch_size
    
    # 基准时间（RTX 4090, batch_size=16）
    # 约 0.5 秒每次迭代
    base_time_per_iter = 0.5  # 秒
    
    # 调整因子
    time_per_iter = base_time_per_iter * gpu_factor
    
    # 每个 epoch 的时间
    time_per_epoch = iterations_per_epoch * time_per_iter / 60  # 转换为分钟
    
    # 总时间
    total_time_minutes = time_per_epoch * epochs
    total_time_hours = total_time_minutes / 60
    
    print(f"\n   每轮迭代数: {iterations_per_epoch}")
    print(f"   每次迭代时间: {time_per_iter:.2f} 秒")
    print(f"   每轮训练时间: {time_per_epoch:.1f} 分钟")
    print(f"\n   总训练时间 ({epochs} 轮):")
    print(f"     约 {total_time_minutes:.0f} 分钟")
    print(f"     约 {total_time_hours:.1f} 小时")
    
    if total_time_hours > 24:
        print(f"     约 {total_time_hours/24:.1f} 天")
    
    # 5. 建议
    print(f"\n5. 建议:")
    
    if not has_gpu:
        print("   !!! CPU 训练非常慢 !!!")
        print("   建议:")
        print("     - 安装 GPU 版本的 PyTorch")
        print("     - 或使用 Google Colab 免费 GPU")
        print("     - 或减少训练轮数和数据量")
        
        # 给出快速测试的建议
        quick_epochs = max(1, int(60 / time_per_epoch))  # 1小时内能完成的轮数
        print(f"\n   快速测试建议:")
        print(f"     python train.py --epochs {quick_epochs}")
        print(f"     (约 1 小时)")
    
    elif total_time_hours > 10:
        print("   训练时间较长，建议:")
        print("     - 使用 GPU 训练（如果还没有）")
        print("     - 可以先用较少轮数测试: --epochs 20")
        print("     - 训练过程可以暂停和恢复")
    
    elif total_time_hours > 3:
        print("   训练时间适中")
        print("     - 可以睡前开始训练，早上完成")
        print("     - 或周末进行完整训练")
    
    else:
        print("   训练时间较短，可以直接开始！")
    
    # 6. 不同场景的估算
    print(f"\n6. 其他训练场景:")
    
    scenarios = [
        (10, "快速测试"),
        (20, "初步训练"),
        (50, "中等训练"),
        (100, "完整训练"),
        (200, "高质量训练")
    ]
    
    for ep, desc in scenarios:
        if ep <= epochs:
            continue
        est_hours = time_per_epoch * ep / 60
        if est_hours < 1:
            time_str = f"{est_hours*60:.0f} 分钟"
        else:
            time_str = f"{est_hours:.1f} 小时"
        print(f"   {desc} ({ep} 轮): {time_str}")
    
    # 7. 开始命令
    print(f"\n7. 开始训练:")
    print(f"   python train.py")
    print(f"\n   或自定义轮数:")
    print(f"   python train.py --epochs <轮数>")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        estimate_time()
    except Exception as e:
        print(f"\n错误: {e}")
        print("请确保:")
        print("  1. 已安装 PyTorch: pip install torch")
        print("  2. config.yaml 文件存在")
        print("  3. 已准备训练数据")
