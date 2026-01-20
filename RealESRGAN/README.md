# RealESRGAN 图像无损缩放项目

使用预训练的RealESRGAN模型实现图像超分辨率（无损放大）

## 项目结构

```
RealESRGAN/
├── models/           # 存储预训练模型
├── inputs/           # 输入图像文件夹
├── outputs/          # 输出放大后的图像
├── inference.py      # 主推理脚本
├── requirements.txt  # Python依赖包
└── README.md         # 项目说明文档
```

## 环境要求

- Python 3.7+
- Windows 10
- （可选）NVIDIA GPU + CUDA 用于加速

## 安装步骤

### 步骤1: 安装依赖包

```bash
pip install -r requirements.txt
```

**注意**: 如果你有NVIDIA GPU，建议先安装PyTorch的GPU版本以获得更快的处理速度：

```bash
# 安装PyTorch GPU版本（根据你的CUDA版本选择）
# 访问 https://pytorch.org/ 获取适合你系统的安装命令
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 步骤2: 下载预训练模型

模型会在首次运行时自动下载到 `models/` 文件夹。

可用的模型：
- **RealESRGAN_x4plus**: 通用4倍放大模型（默认）
- **RealESRGAN_x4plus_anime_6B**: 动漫图像专用4倍放大模型
- **RealESRGAN_x2plus**: 通用2倍放大模型

## 使用方法

### 方法1: 单张图像放大

```bash
python inference.py -i inputs/your_image.jpg -o outputs/output.jpg
```

### 方法2: 批量处理文件夹

```bash
python inference.py -i inputs/ -o outputs/
```

### 方法3: 指定模型和放大倍数

```bash
# 使用动漫模型，4倍放大
python inference.py -i inputs/anime.jpg -o outputs/anime_upscaled.jpg -m RealESRGAN_x4plus_anime_6B -s 4

# 使用2倍放大模型
python inference.py -i inputs/photo.jpg -o outputs/photo_upscaled.jpg -m RealESRGAN_x2plus -s 2
```

### 方法4: 使用GPU加速

```bash
# 使用第0号GPU
python inference.py -i inputs/image.jpg -o outputs/output.jpg -g 0
```

## 命令行参数说明

| 参数 | 简写 | 说明 | 必需 | 默认值 |
|------|------|------|------|--------|
| --input | -i | 输入图像或文件夹路径 | 是 | - |
| --output | -o | 输出图像或文件夹路径 | 是 | - |
| --model | -m | 模型名称 | 否 | RealESRGAN_x4plus |
| --scale | -s | 放大倍数 (2或4) | 否 | 4 |
| --gpu-id | -g | GPU设备ID | 否 | None (使用CPU) |

## 示例

### 示例1: 放大单张照片

```bash
# 将一张照片放大4倍
python inference.py -i inputs/photo.jpg -o outputs/photo_4x.jpg
```

### 示例2: 处理动漫图片

```bash
# 使用动漫专用模型
python inference.py -i inputs/anime.png -o outputs/anime_4x.png -m RealESRGAN_x4plus_anime_6B
```

### 示例3: 批量处理

```bash
# 批量处理inputs文件夹中的所有图片
python inference.py -i inputs/ -o outputs/ -s 4
```

## 常见问题

### Q1: 出现CUDA out of memory错误

**解决方案**: 修改 [`inference.py`](inference.py) 中的 `tile` 参数（第86行），将400改为更小的值，如256或128。

### Q2: 处理速度很慢

**解决方案**: 
1. 确保已安装GPU版本的PyTorch
2. 使用 `-g 0` 参数启用GPU加速

### Q3: 模型下载失败

**解决方案**: 手动从GitHub下载模型并放到 `models/` 文件夹：
- https://github.com/xinntao/Real-ESRGAN/releases

## 模型信息

| 模型名称 | 适用场景 | 放大倍数 | 模型大小 |
|----------|----------|----------|----------|
| RealESRGAN_x4plus | 通用图像 | 4x | ~65MB |
| RealESRGAN_x4plus_anime_6B | 动漫/插画 | 4x | ~17MB |
| RealESRGAN_x2plus | 通用图像 | 2x | ~65MB |

## 参考资源

- [RealESRGAN GitHub](https://github.com/xinntao/Real-ESRGAN)
- [RealESRGAN 论文](https://arxiv.org/abs/2107.10833)

## 技术栈

- **PyTorch**: 深度学习框架
- **BasicSR**: 超分辨率基础库
- **RealESRGAN**: 预训练模型
- **OpenCV**: 图像处理

## License

本项目基于RealESRGAN开源项目，遵循其原始许可证。
