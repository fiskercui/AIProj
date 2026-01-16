"""
GPU 诊断工具
快速检查 GPU 配置是否正确
"""

import torch
import sys


def check_gpu():
    """检查 GPU 状态"""
    print("="*60)
    print("GPU 诊断工具")
    print("="*60)
    
    # 1. PyTorch 版本
    print(f"\n1. PyTorch 版本: {torch.__version__}")
    
    if '+cpu' in torch.__version__:
        print("   ⚠️  这是 CPU 版本的 PyTorch")
        print("   建议重新安装 GPU 版本")
    elif '+cu' in torch.__version__:
        print(f"   ✓ 这是 GPU 版本的 PyTorch")
    
    # 2. CUDA 可用性
    cuda_available = torch.cuda.is_available()
    print(f"\n2. CUDA 可用: {cuda_available}")
    
    if not cuda_available:
        print("\n" + "="*60)
        print("⚠️  GPU 不可用")
        print("="*60)
        print("\n可能的原因:")
        print("  1. 你的电脑没有 NVIDIA GPU")
        print("  2. 安装了 CPU 版本的 PyTorch")
        print("  3. NVIDIA 驱动未安装或版本太旧")
        print("  4. CUDA 工具包未正确安装")
        
        print("\n解决方案:")
        print("  → 查看详细教程: GPU_SETUP_GUIDE.md")
        print("  → 或运行: python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        
        print("\n如果确认没有 GPU:")
        print("  → 项目仍可在 CPU 上运行（速度较慢）")
        print("  → 或使用 Google Colab 免费 GPU")
        
        return False
    
    # 3. CUDA 版本
    print(f"3. CUDA 版本: {torch.version.cuda}")
    
    # 4. GPU 信息
    gpu_count = torch.cuda.device_count()
    print(f"4. GPU 数量: {gpu_count}")
    
    for i in range(gpu_count):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"   - GPU {i}: {gpu_name}")
        
        # 显存信息
        total_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f"     显存: {total_memory:.2f} GB")
    
    # 5. GPU 计算测试
    print(f"\n5. GPU 计算测试: ", end='')
    try:
        # 简单的矩阵乘法测试
        x = torch.randn(1000, 1000).cuda()
        y = x @ x
        torch.cuda.synchronize()
        print("✅ 通过")
        
        # 显存使用
        memory_allocated = torch.cuda.memory_allocated(0) / 1024**2
        memory_reserved = torch.cuda.memory_reserved(0) / 1024**2
        print(f"   当前显存使用: {memory_allocated:.2f} MB")
        print(f"   当前显存保留: {memory_reserved:.2f} MB")
        
    except Exception as e:
        print(f"❌ 失败")
        print(f"   错误: {e}")
        return False
    
    # 6. 性能简测
    print(f"\n6. 性能测试:")
    import time
    
    # CPU 测试
    x_cpu = torch.randn(1000, 1000)
    start = time.time()
    for _ in range(10):
        y_cpu = x_cpu @ x_cpu
    cpu_time = (time.time() - start) * 1000
    print(f"   CPU 10次矩阵乘法: {cpu_time:.2f} ms")
    
    # GPU 测试
    x_gpu = torch.randn(1000, 1000).cuda()
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(10):
        y_gpu = x_gpu @ x_gpu
    torch.cuda.synchronize()
    gpu_time = (time.time() - start) * 1000
    print(f"   GPU 10次矩阵乘法: {gpu_time:.2f} ms")
    print(f"   加速比: {cpu_time/gpu_time:.1f}x")
    
    # 总结
    print("\n" + "="*60)
    print("✅ GPU 配置正常！")
    print("="*60)
    print("\n你可以:")
    print("  1. 运行测试: python test_model.py")
    print("  2. 开始训练: python train.py")
    print("  3. 图像推理: python inference.py --input <图像路径>")
    
    return True


if __name__ == "__main__":
    success = check_gpu()
    sys.exit(0 if success else 1)
