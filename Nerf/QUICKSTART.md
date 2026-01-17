# 🚀 NeRF 快速开始指南

这是一份详细的步骤说明，帮助你从零开始运行 NeRF 项目。

---

## 📋 项目结构

```
Nerf/
├── README.md              # 详细文档
├── QUICKSTART.md         # 本文件：快速入门
├── requirements.txt       # Python 依赖
├── tiny_nerf.py          # NeRF 核心实现
├── run_example.py        # 运行示例
├── data/                 # 数据目录（可选）
└── output/               # 输出目录（自动生成）
```

---

## 步骤 1️⃣：检查 Python 环境

### 1.1 检查 Python 版本

打开终端（VSCode 可以用 `Ctrl + ~` 打开），运行：

```bash
python --version
```

**要求**：Python 3.9 或更高版本

如果版本过低或未安装，请：
- Windows：从 [python.org](https://www.python.org/downloads/) 下载安装
- 已有 Anaconda：`conda create -n nerf python=3.10`

---

## 步骤 2️⃣：安装依赖包

### 2.1 基础安装（推荐）

在项目目录下运行：

```bash
pip install -r requirements.txt
```

### 2.2 如果网络慢，使用国内镜像

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.3 验证安装

检查 PyTorch 是否安装成功：

```bash
python -c "import torch; print('PyTorch version:', torch.__version__)"
```

应该输出类似：`PyTorch version: 2.x.x`

---

## 步骤 3️⃣：运行示例

### 3.1 直接运行

```bash
python run_example.py
```

### 3.2 预期输出

你会看到类似这样的输出：

```
============================================================
🚀 NeRF 训练示例
============================================================

💻 使用设备: cuda (或 cpu)

🎨 生成合成场景数据...
  ✓ 生成 20 张 100x100 图像

🏗️  创建 NeRF 模型...
  ✓ 模型参数数量: 123,456

🎓 开始训练 (共 500 轮)...
   这可能需要几分钟，请耐心等待...

Epoch 0/500, Loss: 0.234567
Epoch 50/500, Loss: 0.123456
...
```

### 3.3 训练时间

- **CPU**：约 5-10 分钟
- **GPU**：约 2-3 分钟

### 3.4 查看结果

训练完成后，检查 `output/` 目录：

- `training_loss.png` - 训练损失曲线
- `render_comparison.png` - 真实 vs NeRF 渲染对比
- `novel_view.png` - 新视角合成（最精彩的部分！）

**在 VSCode 中查看图片**：双击图片文件即可打开预览

---

## 步骤 4️⃣：理解代码（可选但推荐）

### 4.1 阅读核心代码

打开 [`tiny_nerf.py`](tiny_nerf.py)，按顺序阅读：

1. **位置编码** (`positional_encoding`)
   - 为什么需要？让网络能学习高频细节

2. **NeRF 网络** (`TinyNeRF`)
   - 输入：3D 位置 + 观察方向
   - 输出：RGB 颜色 + 密度

3. **体积渲染** (`volume_rendering`)
   - 沿光线积分颜色和密度
   - 核心公式：C(r) = Σ T_i * α_i * c_i

### 4.2 修改参数试试

编辑 [`run_example.py`](run_example.py) 中的参数：

```python
# 训练参数
epochs = 500            # 改成 1000 → 更高质量
batch_size = 1024       # 减小 → 节省内存
lr = 5e-4               # 学习率

# 模型参数
pos_L = 6               # 改成 10 → 更精细（但更慢）
hidden_dim = 128        # 改成 256 → 更大容量
```

---

## 常见问题 ❓

### Q1: 显示 "No module named 'torch'"

**解决**：PyTorch 未安装成功

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

如果有 NVIDIA GPU：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Q2: 训练很慢

**原因**：在用 CPU 训练

**检查**：
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

如果输出 `False`，说明没有 GPU 或未安装 CUDA 版 PyTorch。

**解决**：
- 减少训练轮数 (`epochs = 200`)
- 减少图像尺寸 (`H, W = 50, 50`)
- 或者耐心等待

### Q3: 内存不足 / Out of Memory

**解决**：减小批量大小

编辑 `run_example.py`：
```python
batch_size = 512  # 改小一些
```

### Q4: 渲染结果模糊

**原因**：训练不够充分

**解决**：
1. 增加训练轮数 (`epochs = 1000` 或更多)
2. 增加模型容量 (`hidden_dim = 256`)
3. 等待更长时间

### Q5: 如何使用真实图像？

需要：
1. 相机内参（焦距等）
2. 每张图像的相机位姿（位置和朝向）

推荐工具：
- **COLMAP**：从多张图像重建相机位姿
- **NeRF Synthetic Dataset**：官方提供的现成数据

---

## 下一步学习 📚

### 初级

1. ✅ 运行示例，看到结果
2. ✅ 阅读代码注释，理解流程
3. ✅ 调整参数，观察变化

### 中级

1. 📖 阅读 NeRF 论文：[arXiv:2003.08934](https://arxiv.org/abs/2003.08934)
2. 🎥 观看讲解视频（YouTube 搜索 "NeRF explained"）
3. 📊 可视化中间结果（密度场、深度图等）

### 高级

1. 🗂️ 使用官方数据集：[NeRF Synthetic Dataset](https://drive.google.com/drive/folders/128yBriW1IG_3NJ5Rp7APSTZsJqdJdfc1)
2. 🚀 尝试改进版本：Instant-NGP, Mip-NeRF, NeRF++
3. 🎨 扩展功能：编辑场景、动态 NeRF、大场景 NeRF

---

## 命令速查表 📝

```bash
# 安装依赖
pip install -r requirements.txt

# 运行示例
python run_example.py

# 测试核心模块
python tiny_nerf.py

# 检查 PyTorch
python -c "import torch; print(torch.__version__)"

# 检查 GPU
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 获取帮助 🆘

1. **查看详细文档**：[`README.md`](README.md)
2. **检查代码注释**：每个函数都有详细说明
3. **搜索错误信息**：复制错误信息到 Google/Stack Overflow

---

## 成功标志 ✅

完成以下即表示成功：

- [x] 成功安装所有依赖
- [x] 运行 `python run_example.py` 无错误
- [x] 在 `output/` 目录看到 3 张图片
- [x] 新视角图像看起来像彩色球体

---

**🎉 祝贺你！你已经成功运行了一个 NeRF 模型！**

现在你可以：
- 调整参数探索效果
- 阅读代码深入理解
- 尝试真实数据集
- 学习更高级的 NeRF 变种

**继续加油，探索 3D 世界的魅力！** 🌟
