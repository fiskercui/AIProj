# NeRF (Neural Radiance Fields) 神经辐射场实现

这是一个简化版的 NeRF 实现，基于 PyTorch，用于学习和理解 NeRF 的核心原理。

## 📖 什么是 NeRF？

NeRF (Neural Radiance Fields) 是一种革命性的 3D 场景表示方法，通过神经网络学习场景的体积表示，能够从多张 2D 图像合成任意视角的高质量 3D 渲染图像。

### 核心原理：
- **输入**：3D 空间坐标 (x, y, z) 和观察方向 (θ, φ)
- **输出**：该点的颜色 (RGB) 和密度 (σ)
- **训练**：通过多张不同视角的图像进行监督学习
- **渲染**：使用体积渲染技术生成新视角图像

## 🛠️ 技术栈

- **Python**: 3.9+
- **PyTorch**: 深度学习框架
- **NumPy**: 数值计算
- **Matplotlib**: 可视化
- **imageio**: 图像读取

## 📦 安装步骤

### 1. 确保已安装 Python 3.9+

检查 Python 版本：
```bash
python --version
```

### 2. 安装依赖包

在项目目录下运行：
```bash
pip install -r requirements.txt
```

如果遇到网络问题，可以使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 下载示例数据（可选）

我们提供了简化的合成数据生成，无需额外下载。如果需要使用 NeRF 官方数据集：

- 访问：https://drive.google.com/drive/folders/128yBriW1IG_3NJ5Rp7APSTZsJqdJdfc1
- 下载 `lego.zip` 并解压到 `data/lego/` 目录

## 🚀 快速开始

### 运行简化示例（推荐新手）

```bash
python run_example.py
```

这将：
1. 生成一个简单的合成场景数据
2. 训练一个小型 NeRF 模型（约 5-10 分钟）
3. 渲染并保存结果图像到 `output/` 目录
4. 显示训练过程和结果

### 直接使用 NeRF 模块

```python
from tiny_nerf import TinyNeRF, train_nerf, render_image

# 创建模型
model = TinyNeRF()

# 训练（需要准备数据）
# train_nerf(model, images, poses, focal, epochs=1000)

# 渲染新视角
# img = render_image(model, pose, H, W, focal)
```

## 📂 项目结构

```
Nerf/
├── README.md              # 本文件
├── requirements.txt       # Python 依赖
├── tiny_nerf.py          # 核心 NeRF 实现
├── run_example.py        # 运行示例
├── data/                 # 数据目录
│   └── lego/            # （可选）官方数据集
└── output/               # 输出目录
    ├── training.png      # 训练过程可视化
    └── render_*.png      # 渲染结果
```

## 🎯 代码说明

### tiny_nerf.py
包含核心实现：
- `TinyNeRF`: NeRF 神经网络模型
- `positional_encoding`: 位置编码
- `render_rays`: 体积渲染
- `train_nerf`: 训练函数

### run_example.py
运行示例，包含：
- 合成数据生成
- 模型训练循环
- 结果可视化

## 💡 学习建议

1. **先运行示例**：直接运行 `run_example.py` 看效果
2. **阅读代码**：理解 `tiny_nerf.py` 中的核心函数
3. **调整参数**：尝试修改网络层数、训练轮次等
4. **使用真实数据**：下载官方数据集进行实验

## 📊 预期效果

- **训练时间**：5-10 分钟（简化版）/ 几小时（完整版）
- **显存需求**：2GB+（简化版）/ 8GB+（完整版）
- **输出质量**：学习版足够理解原理，完整版可达论文效果

## 🔧 常见问题

### Q: 显存不足怎么办？
A: 减小批量大小或图像分辨率，在 `run_example.py` 中修改 `batch_size` 参数。

### Q: 训练很慢？
A: 
- 确保安装了 GPU 版本的 PyTorch
- 减少训练轮次 (epochs)
- 降低图像分辨率

### Q: 如何使用自己的图像？
A: 需要相机位姿（poses）信息，建议使用 COLMAP 进行重建，或参考官方数据格式。

## 📚 参考资料

- **论文**：[NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis](https://arxiv.org/abs/2003.08934)
- **项目主页**：https://www.matthewtancik.com/nerf
- **官方代码**：https://github.com/bmild/nerf

## 📝 许可证

本项目仅供学习使用，基于 MIT 许可证。

## 🤝 贡献

欢迎提出问题和改进建议！

---

**祝你学习愉快！如有问题，请查看代码注释或提 issue。** 🎉
