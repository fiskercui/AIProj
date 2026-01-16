# GPU 设置指南

如果你在运行测试时看到 "✗ 未检测到 GPU，跳过此测试"，这个指南将帮你启用 GPU 加速。

## 📋 前提条件检查

### 第一步：确认你有 NVIDIA GPU

1. **打开设备管理器**（Windows 系统）
   - 按 `Win + X`，选择"设备管理器"
   - 展开"显示适配器"

2. **查看显卡型号**
   - 如果看到 NVIDIA GeForce / RTX / GTX / Quadro → ✅ 继续
   - 如果只看到 Intel / AMD → ❌ 无法使用 CUDA

### 第二步：检查当前 PyTorch 版本

运行命令：
```bash
python -c "import torch; print('PyTorch 版本:', torch.__version__); print('CUDA 可用:', torch.cuda.is_available())"
```

**如果输出：**
```
PyTorch 版本: 2.x.x+cpu
CUDA 可用: False
```
说明安装的是 **CPU 版本**，需要重新安装。

---

## 🔧 解决方案

### 方案 A：重新安装 GPU 版本的 PyTorch（推荐）

#### 1. 卸载当前 PyTorch
```bash
pip uninstall torch torchvision torchaudio
```

#### 2. 确认 CUDA 版本

**方法 1：使用 nvidia-smi 命令**
```bash
nvidia-smi
```
查看右上角的 CUDA Version（例如：12.1）

**方法 2：如果没有 nvidia-smi**
- 访问 [NVIDIA 驱动下载页面](https://www.nvidia.com/Download/index.aspx)
- 下载并安装最新驱动

#### 3. 安装对应版本的 PyTorch

访问 [PyTorch 官网](https://pytorch.org/get-started/locally/)，或直接使用：

**CUDA 12.1**（最新）
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**CUDA 11.8**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CUDA 11.7**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

#### 4. 验证安装

```bash
python -c "import torch; print('CUDA 可用:', torch.cuda.is_available()); print('GPU 名称:', torch.cuda.get_device_name(0))"
```

**成功输出示例：**
```
CUDA 可用: True
GPU 名称: NVIDIA GeForce RTX 3060
```

---

### 方案 B：使用云 GPU（免费）

如果你的电脑没有 NVIDIA GPU，可以使用云服务：

#### Google Colab（推荐，免费）

1. 访问 [Google Colab](https://colab.research.google.com/)
2. 上传你的项目文件
3. 启用 GPU：
   - 点击 "运行时" → "更改运行时类型"
   - 硬件加速器选择 "GPU"
4. 运行代码

#### Kaggle Notebooks（免费）

1. 访问 [Kaggle](https://www.kaggle.com/)
2. 创建新 Notebook
3. 右侧设置中启用 GPU
4. 上传代码运行

---

## 🐛 常见问题排查

### 问题 1：nvidia-smi 找不到命令

**原因**: 没有安装 NVIDIA 驱动

**解决**:
1. 访问 [NVIDIA 驱动下载](https://www.nvidia.com/Download/index.aspx)
2. 选择你的显卡型号
3. 下载并安装驱动
4. 重启电脑

### 问题 2：torch.cuda.is_available() 返回 False

**检查步骤**:

1. **确认驱动安装正确**
   ```bash
   nvidia-smi
   ```
   
2. **确认安装的是 GPU 版本 PyTorch**
   ```bash
   python -c "import torch; print(torch.__version__)"
   ```
   - 如果看到 `+cpu`，说明安装错了
   - 应该看到 `+cu118` 或 `+cu121`

3. **重新安装正确版本**
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### 问题 3：CUDA out of memory

**解决方法**:

1. **减小 batch_size**
   在 `config.yaml` 中修改：
   ```yaml
   train:
     batch_size: 4  # 从 16 改为 4
   ```

2. **减小模型块数**
   ```yaml
   model:
     num_blocks: 16  # 从 23 改为 16
   ```

3. **清理 GPU 缓存**
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

---

## ✅ 验证 GPU 正常工作

运行完整测试：
```bash
python test_model.py
```

如果 GPU 设置成功，你应该看到：
```
============================================================
测试 3: GPU 推理性能
============================================================

GPU: NVIDIA GeForce RTX 3060

推理性能 (256x256 -> 1024x1024):
  运行次数: 10
  总时间: 2.345 秒
  平均时间: 234.50 ms
  FPS: 4.26

GPU 显存:
  已分配: 1245.67 MB
  已保留: 1536.00 MB
```

---

## 📊 性能对比

| 硬件 | 256x256 推理时间 | 训练速度（每 epoch） |
|------|----------------|-------------------|
| CPU (i7) | ~2000 ms | ~2 小时 |
| GTX 1060 | ~200 ms | ~20 分钟 |
| RTX 3060 | ~100 ms | ~10 分钟 |
| RTX 4090 | ~30 ms | ~3 分钟 |

---

## 🎯 快速诊断脚本

创建一个快速检查脚本：

```python
# check_gpu.py
import torch
import sys

print("="*60)
print("GPU 诊断工具")
print("="*60)

print(f"\n1. PyTorch 版本: {torch.__version__}")

cuda_available = torch.cuda.is_available()
print(f"2. CUDA 可用: {cuda_available}")

if cuda_available:
    print(f"3. CUDA 版本: {torch.version.cuda}")
    print(f"4. GPU 数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"   - GPU {i}: {torch.cuda.get_device_name(i)}")
    
    # 测试 GPU
    try:
        x = torch.randn(1000, 1000).cuda()
        y = x @ x
        print(f"5. GPU 计算测试: ✅ 通过")
    except Exception as e:
        print(f"5. GPU 计算测试: ❌ 失败 - {e}")
else:
    print("\n⚠️ GPU 不可用")
    print("\n可能的原因:")
    print("  1. 没有 NVIDIA GPU")
    print("  2. 安装了 CPU 版本的 PyTorch")
    print("  3. NVIDIA 驱动未安装")
    print("\n请参考 GPU_SETUP_GUIDE.md 解决")
```

运行：
```bash
python check_gpu.py
```

---

## 💡 建议

### 如果你有 NVIDIA GPU
- ✅ 强烈建议配置 GPU 加速
- 训练速度提升 10-100 倍
- 推理速度提升 5-20 倍

### 如果你没有 NVIDIA GPU
- ✅ 仍可以使用项目（CPU 模式）
- ✅ 推荐使用 Google Colab 免费 GPU
- ✅ 或使用预训练模型进行推理（CPU 可接受）

---

需要帮助？请提供以下信息：
1. `nvidia-smi` 的输出
2. `python -c "import torch; print(torch.__version__)"` 的输出
3. 你的显卡型号
