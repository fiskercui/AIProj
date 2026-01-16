"""
测试模型脚本
验证模型的正确性和性能
"""

import torch
import time
from models import ESRGAN


def test_model_structure():
    """测试模型结构"""
    print("="*60)
    print("测试 1: 模型结构验证")
    print("="*60)
    
    # 创建模型
    model = ESRGAN(scale=4, num_blocks=23)
    model.eval()
    
    # 统计参数
    total, trainable = model.count_parameters()
    
    print(f"\n✓ 模型创建成功")
    print(f"  总参数: {total:,}")
    print(f"  可训练参数: {trainable:,}")
    
    return model


def test_forward_pass(model):
    """测试前向传播"""
    print("\n" + "="*60)
    print("测试 2: 前向传播验证")
    print("="*60)
    
    # 测试不同尺寸的输入
    test_sizes = [
        (1, 3, 64, 64),    # 小图
        (1, 3, 128, 128),  # 中图
        (1, 3, 256, 256),  # 大图
    ]
    
    with torch.no_grad():
        for i, size in enumerate(test_sizes, 1):
            print(f"\n测试 {i}:")
            print(f"  输入尺寸: {size}")
            
            # 创建随机输入
            x = torch.randn(size)
            
            # 前向传播
            start_time = time.time()
            output = model(x)
            inference_time = time.time() - start_time
            
            # 验证输出尺寸
            expected_h = size[2] * 4
            expected_w = size[3] * 4
            
            print(f"  输出尺寸: {output.shape}")
            print(f"  推理时间: {inference_time*1000:.2f} ms")
            
            assert output.shape[0] == size[0], "批次大小错误"
            assert output.shape[1] == size[1], "通道数错误"
            assert output.shape[2] == expected_h, "高度错误"
            assert output.shape[3] == expected_w, "宽度错误"
            
            print(f"  ✓ 输出尺寸正确")


def test_gpu_inference():
    """测试 GPU 推理"""
    print("\n" + "="*60)
    print("测试 3: GPU 推理性能")
    print("="*60)
    
    if not torch.cuda.is_available():
        print("\n✗ 未检测到 GPU，跳过此测试")
        return
    
    device = torch.device('cuda')
    print(f"\nGPU: {torch.cuda.get_device_name(0)}")
    
    # 创建模型并移到 GPU
    model = ESRGAN(scale=4, num_blocks=23).to(device)
    model.eval()
    
    # 测试推理速度
    input_size = (1, 3, 256, 256)
    x = torch.randn(input_size).to(device)
    
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
    
    print(f"\n推理性能 ({input_size[2]}x{input_size[3]} -> {input_size[2]*4}x{input_size[3]*4}):")
    print(f"  运行次数: {num_runs}")
    print(f"  总时间: {total_time:.3f} 秒")
    print(f"  平均时间: {avg_time*1000:.2f} ms")
    print(f"  FPS: {1/avg_time:.2f}")
    
    # 显存占用
    memory_allocated = torch.cuda.memory_allocated(device) / 1024**2
    memory_reserved = torch.cuda.memory_reserved(device) / 1024**2
    
    print(f"\nGPU 显存:")
    print(f"  已分配: {memory_allocated:.2f} MB")
    print(f"  已保留: {memory_reserved:.2f} MB")


def test_image_quality():
    """测试图像质量指标"""
    print("\n" + "="*60)
    print("测试 4: 图像质量验证")
    print("="*60)
    
    from utils import calculate_psnr
    import numpy as np
    
    # 创建模拟图像
    img1 = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    img2 = img1.copy()
    
    # 测试完全相同的图像
    psnr = calculate_psnr(img1, img2)
    print(f"\n相同图像 PSNR: {psnr:.2f} dB")
    assert psnr == float('inf'), "相同图像的 PSNR 应该是无穷大"
    print("✓ 相同图像测试通过")
    
    # 测试不同的图像
    img3 = img1 + np.random.randint(-10, 10, img1.shape, dtype=np.int16)
    img3 = np.clip(img3, 0, 255).astype(np.uint8)
    
    psnr = calculate_psnr(img1, img3)
    print(f"\n添加噪声后 PSNR: {psnr:.2f} dB")
    assert 30 < psnr < 50, f"PSNR 值异常: {psnr}"
    print("✓ 噪声图像测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# ESRGAN 模型测试套件")
    print("#"*60)
    
    try:
        # 测试 1: 模型结构
        model = test_model_structure()
        
        # 测试 2: 前向传播
        test_forward_pass(model)
        
        # 测试 3: GPU 推理
        test_gpu_inference()
        
        # 测试 4: 图像质量
        test_image_quality()
        
        # 总结
        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        print("\n✓ 所有测试通过！")
        print("\n模型已准备就绪，可以用于:")
        print("  1. 训练: python train.py")
        print("  2. 推理: python inference.py --input <图像路径>")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
