# DLSS 项目使用指南

这是一个完整的深度学习超分辨率（类似 NVIDIA DLSS）项目的使用教程。

## 📋 目录

1. [环境准备](#环境准备)
2. [快速开始](#快速开始)
3. [测试模型](#测试模型)
4. [训练模型](#训练模型)
5. [推理使用](#推理使用)
6. [常见问题](#常见问题)

---

## 🚀 环境准备

### 第一步：安装 Python

确保你的系统已安装 **Python 3.8 或更高版本**。

检查 Python 版本：
```bash
python --version
```

### 第二步：安装依赖

在项目根目录下运行：

```bash
pip install -r requirements.txt
```

**如果你有 NVIDIA GPU（推荐）：**

确保安装了 CUDA 版本的 PyTorch。访问 [PyTorch 官网](https://pytorch.org/) 获取安装命令。

例如（CUDA 11.8）：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**检查 GPU 是否可用：**

```bash
python -c "import torch; print('CUDA 可用:', torch.cuda.is_available())"
```

---

## ⚡ 快速开始

### 测试模型结构

运行测试脚本验证环境：

```bash
python test_model.py
```

你应该看到类似输出：
```
✓ 模型创建成功
  总参数: 16,697,987
  可训练参数: 16,697,987
```

### 推理演示（使用随机权重）

即使没有训练，你也可以测试推理流程：

```bash
# 放一张测试图片到 data/test/ 目录
# 然后运行推理（注意：未训练的模型输出质量会很差）
python inference.py --input data/test/your_image.png
```

---

## 🧪 测试模型

运行完整的测试套件：

```bash
python test_model.py
```

测试内容包括：
- ✓ 模型结构验证
- ✓ 前向传播测试
- ✓ GPU 推理性能（如果有 GPU）
- ✓ 图像质量指标计算

---

## 🎓 训练模型

### 准备训练数据

1. **收集高质量图像**
   - 图像格式：JPG, PNG, BMP 等
   - 建议数量：至少 1000 张
   - 建议尺寸：大于 512x512

2. **放置数据**
   ```
   DLSS/
   └── data/
       └── train/
           ├── image001.jpg
           ├── image002.jpg
           ├── image003.jpg
           └── ...
   ```

### 开始训练

**基础训练命令：**

```bash
python train.py
```

**自定义训练参数：**

```bash
python train.py --epochs 100 --config config.yaml
```

**从检查点恢复训练：**

```bash
python train.py --resume ./checkpoints/checkpoint_epoch_50.pth
```

### 训练参数说明

在 [`config.yaml`](config.yaml:1) 中可以调整：

- `epochs`: 训练轮数（默认 100）
- `batch_size`: 批次大小（默认 16，GPU 显存不足时可调小）
- `learning_rate`: 学习率（默认 0.0001）
- `scale`: 放大倍数（2, 4, 8）

### 训练监控

使用 TensorBoard 查看训练进度：

```bash
tensorboard --logdir runs/
```

然后在浏览器打开 http://localhost:6006

---

## 🖼️ 推理使用

### 处理单张图像

```bash
python inference.py --input path/to/your/image.png --checkpoint checkpoints/final_model.pth
```

### 批量处理

```bash
python inference.py --input path/to/input/folder --batch --checkpoint checkpoints/final_model.pth
```

### 指定输出路径

```bash
python inference.py --input image.png --output result.png --checkpoint checkpoints/final_model.pth
```

### 使用 CPU（无 GPU）

```bash
python inference.py --input image.png --device cpu --checkpoint checkpoints/final_model.pth
```

### 推理参数说明

- `--input`: 输入图像或目录路径（必需）
- `--output`: 输出路径（可选，默认保存到 results/）
- `--checkpoint`: 模型权重文件路径
- `--device`: 计算设备（cuda 或 cpu）
- `--batch`: 批量处理模式

---

## 📊 评估模型质量

### 计算 PSNR

PSNR（峰值信噪比）是衡量图像质量的常用指标：
- 值越大越好
- 通常 30-40 dB 表示良好质量
- 40+ dB 表示优秀质量

使用内置函数：

```python
from utils import calculate_psnr, load_image

img1 = load_image('original.png')
img2 = load_image('upscaled.png')
psnr = calculate_psnr(img1, img2)
print(f"PSNR: {psnr:.2f} dB")
```

---

## 🎯 使用场景

### 1. 游戏画质增强
将低分辨率游戏画面放大到高分辨率，提升视觉效果。

### 2. 老照片修复
将低质量的老照片放大并增强细节。

### 3. 视频超分辨率
逐帧处理视频，提升视频分辨率。

### 4. 医学图像增强
提升医学影像的分辨率和清晰度。

---

## 🔧 性能优化建议

### GPU 推理优化

1. **使用半精度推理**（需要修改代码）
   ```python
   model.half()  # 转换为 FP16
   ```

2. **批处理**
   同时处理多张图像可以提升吞吐量

3. **CUDA 优化**
   确保使用最新的 CUDA 和 cuDNN

### CPU 推理优化

1. **减少模型块数**
   在 config.yaml 中将 `num_blocks` 从 23 减少到 16

2. **使用多线程**
   设置 `torch.set_num_threads(4)`

---

## ❓ 常见问题

### Q1: 推理输出的图像模糊怎么办？

**原因**: 使用的是未训练或训练不足的模型。

**解决方案**:
1. 训练自己的模型（需要大量数据和时间）
2. 下载预训练模型（推荐）
3. 增加训练轮数和数据量

### Q2: 训练时提示 CUDA out of memory

**解决方案**:
- 减小 batch_size（在 config.yaml 中修改）
- 减小输入图像尺寸（hr_size）
- 减少模型块数（num_blocks）

### Q3: 训练速度很慢

**原因**: 
- 没有使用 GPU
- 数据加载瓶颈

**解决方案**:
- 使用 NVIDIA GPU
- 增加 num_workers（Windows 建议设为 0）
- 使用 SSD 存储训练数据

### Q4: 如何获取预训练模型？

你可以：
1. 访问 [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) 项目下载官方预训练权重
2. 自己训练模型（推荐用于学习）
3. 使用迁移学习，在预训练模型基础上微调

### Q5: 支持哪些图像格式？

支持常见的图像格式：
- JPG / JPEG
- PNG
- BMP
- TIF / TIFF

### Q6: 可以处理视频吗？

需要额外开发：
1. 使用 ffmpeg 提取视频帧
2. 逐帧处理
3. 合成回视频

示例脚本（需要安装 ffmpeg）:
```bash
# 提取帧
ffmpeg -i video.mp4 frames/frame_%04d.png

# 批量处理
python inference.py --input frames --batch

# 合成视频
ffmpeg -i results/frame_%04d.png -c:v libx264 output.mp4
```

---

## 📚 扩展学习

### 推荐论文

1. **ESRGAN**: [Enhanced Super-Resolution GAN](https://arxiv.org/abs/1809.00219)
2. **Real-ESRGAN**: [Practical Algorithms for General Image Restoration](https://arxiv.org/abs/2107.10833)

### 相关项目

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [BasicSR](https://github.com/XPixelGroup/BasicSR)
- [NVIDIA DLSS](https://www.nvidia.com/en-us/geforce/technologies/dlss/)

### 数据集推荐

- [DIV2K](https://data.vision.ee.ethz.ch/cvl/DIV2K/): 高质量图像数据集
- [Flickr2K](http://cv.snu.ac.kr/research/EDSR/Flickr2K.tar): Flickr 高清图像
- [COCO](https://cocodataset.org/): 通用物体检测数据集

---

## 🤝 贡献与反馈

如果你在使用过程中遇到问题或有改进建议，欢迎提出 Issue 或 Pull Request！

---

## 📄 许可证

MIT License

---

**祝你使用愉快！🎉**
