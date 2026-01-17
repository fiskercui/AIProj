"""
数据集检查工具
验证训练数据是否准备就绪
"""

import os
import sys
from pathlib import Path

# 设置输出编码为 UTF-8（解决 Windows 终端编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check_dataset():
    """检查数据集状态"""
    print("="*60)
    print("数据集检查工具")
    print("="*60)
    
    train_dir = Path("data/train")
    
    # 检查目录是否存在
    print(f"\n1. 检查目录: {train_dir.absolute()}")
    
    if not train_dir.exists():
        print(f"   ❌ 目录不存在")
        print(f"\n创建目录...")
        train_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ 目录已创建: {train_dir.absolute()}")
    else:
        print(f"   ✓ 目录存在")
    
    # 支持的格式
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    
    # 统计图像
    print(f"\n2. 扫描图像文件...")
    images = []
    for ext in valid_extensions:
        images.extend(train_dir.glob(f"*{ext}"))
        images.extend(train_dir.glob(f"*{ext.upper()}"))
    
    num_images = len(images)
    print(f"   找到 {num_images} 张图像")
    
    # 评估数据集规模
    print(f"\n3. 数据集评估:")
    
    if num_images == 0:
        print("   ❌ 数据集为空")
        print("\n" + "="*60)
        print("如何准备训练数据？")
        print("="*60)
        print("\n方案 1: 下载公开数据集（推荐）")
        print("  → DIV2K: https://data.vision.ee.ethz.ch/cvl/DIV2K/")
        print("    - 下载 DIV2K_train_HR.zip")
        print("    - 解压到 data/train/ 目录")
        print("    - 约 800 张高质量图像")
        
        print("\n方案 2: 使用自己的图像")
        print("  → 收集 100+ 张高清照片")
        print("  → 放入 data/train/ 目录")
        print("  → 支持格式: JPG, PNG, BMP, TIF")
        
        print("\n方案 3: 快速测试")
        print("  → 从电脑中找 10-50 张图片")
        print("  → 复制到 data/train/")
        print("  → 运行 python train.py --epochs 10")
        
        print("\n详细教程: DATASET_GUIDE.md")
        
        return False
        
    elif num_images < 100:
        print(f"   ⚠️  数据集较小（{num_images} 张）")
        print("   可以开始训练，但效果可能有限")
        print("   建议：")
        print("     - 收集更多图像（至少 100 张）")
        print("     - 或下载 DIV2K 数据集（800 张）")
        
    elif num_images < 1000:
        print(f"   ✓ 数据集中等（{num_images} 张）")
        print("   可以获得不错的训练效果")
        
    else:
        print(f"   ✅ 数据集充足（{num_images} 张）")
        print("   数据量充足，可以训练出高质量模型")
    
    # 显示图像信息
    if num_images > 0:
        print(f"\n4. 图像信息:")
        
        # 统计格式分布
        formats = {}
        for img in images:
            ext = img.suffix.lower()
            formats[ext] = formats.get(ext, 0) + 1
        
        for ext, count in formats.items():
            print(f"   {ext}: {count} 张")
        
        # 显示示例
        print(f"\n5. 示例图像:")
        for i, img in enumerate(images[:5], 1):
            # 获取文件大小
            size_mb = img.stat().st_size / 1024 / 1024
            print(f"   {i}. {img.name} ({size_mb:.2f} MB)")
        
        if num_images > 5:
            print(f"   ... 还有 {num_images - 5} 张图像")
        
        # 计算总大小
        total_size = sum(img.stat().st_size for img in images) / 1024 / 1024
        print(f"\n   总大小: {total_size:.2f} MB")
    
    # 检查图像质量
    if num_images > 0:
        print(f"\n6. 质量检查:")
        try:
            from PIL import Image
            
            # 检查第一张图像
            first_img = Image.open(images[0])
            width, height = first_img.size
            
            print(f"   示例尺寸: {width}x{height}")
            
            if width < 256 or height < 256:
                print(f"   ⚠️  图像尺寸较小")
                print(f"   建议使用至少 512x512 的图像")
            else:
                print(f"   ✓ 图像尺寸合适")
            
        except Exception as e:
            print(f"   ⚠️  无法读取图像: {e}")
    
    # 总结
    print("\n" + "="*60)
    if num_images >= 100:
        print("✅ 数据集准备就绪！")
        print("="*60)
        print("\n可以开始训练:")
        print("  → python train.py")
        print("\n或查看更多选项:")
        print("  → python train.py --help")
        return True
    elif num_images > 0:
        print("⚠️  数据集可用但较小")
        print("="*60)
        print("\n可以开始快速测试:")
        print("  → python train.py --epochs 10")
        print("\n建议添加更多图像以获得更好效果")
        print("  → 查看 DATASET_GUIDE.md 了解如何准备数据")
        return True
    else:
        print("❌ 需要准备训练数据")
        print("="*60)
        print("\n请查看详细教程:")
        print("  → DATASET_GUIDE.md")
        return False


if __name__ == "__main__":
    import sys
    success = check_dataset()
    sys.exit(0 if success else 1)
