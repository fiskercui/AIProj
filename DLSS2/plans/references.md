# DLSS 3 架构学习参考资料索引

## 📚 官方资源

### NVIDIA Developer Portal
- **DLSS官方页面**: https://developer.nvidia.com/dlss
- **DLSS SDK下载**: https://developer.nvidia.com/nvidia-dlss-getting-started
- **Streamline SDK**: https://github.com/NVIDIAGameWorks/Streamline
- **DLSS编程指南**: 包含在SDK中
- **开发者博客**: https://developer.nvidia.com/blog

### 官方技术文档
- **NVIDIA RTX技术**: https://www.nvidia.com/rtx
- **Tensor Core文档**: CUDA Programming Guide - Tensor Cores章节
- **NGX SDK文档**: SDK内Documentation文件夹

---

## 🎥 技术演讲与视频

### GDC (Game Developers Conference)
- **"DLSS 2.0 - Image Reconstruction for Real-Time Rendering with Deep Learning"** (GDC 2020)
- **"DLSS 3 - Combining Super Resolution & NVIDIA Optical Flow for AI Frame Generation"** (GDC 2023)
- **"Integrating DLSS in Unreal Engine"** (GDC 2021)

### SIGGRAPH
- **"AI-Accelerated Graphics"** (SIGGRAPH 2022)
- **"Real-Time Ray Tracing"** 系列课程

### NVIDIA GTC (GPU Technology Conference)
- **"The Future of Graphics is AI"** - Jensen Huang Keynote
- **"Deep Dive into DLSS Technology"** 技术专场
- **"Ray Reconstruction with AI"** (GTC 2023)

### YouTube资源
- **Digital Foundry** - DLSS深度技术分析
  - "DLSS 2.0 - A Big Leap In AI Rendering"
  - "DLSS 3 Analysis - How Does Frame Generation Work?"
  
- **NVIDIA YouTube频道** - 官方技术视频
  - DLSS技术讲解系列
  - 开发者教程

---

## 📄 学术论文

### 超分辨率基础
1. **"Image Super-Resolution Using Deep Convolutional Networks"** (SRCNN)
   - Chao Dong et al., ECCV 2014
   - 第一个深度学习超分辨率

2. **"Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network"** (ESPCN)
   - Wenzhe Shi et al., CVPR 2016
   - 亚像素卷积技术

3. **"Enhanced Deep Residual Networks for Single Image Super-Resolution"** (EDSR)
   - Bee Lim et al., CVPR 2017
   - 残差网络超分辨率

### 时序超分辨率
4. **"Video Super-Resolution via Recurrent Short-Term Temporal Aggregation"**
   - Temporally Coherent SR

5. **"TDAN: Temporally-Deformable Alignment Network for Video Super-Resolution"**
   - CVPR 2020

### 视频帧插值
6. **"DAIN: Depth-Aware Video Frame Interpolation"**
   - CVPR 2019
   - 深度感知插值

7. **"RIFE: Real-Time Intermediate Flow Estimation for Video Frame Interpolation"**
   - arXiv 2020
   - 实时光流估计

8. **"FILM: Frame Interpolation for Large Motion"**
   - Google Research, 2022

### 光流估计
9. **"PWC-Net: CNNs for Optical Flow Using Pyramid, Warping, and Cost Volume"**
   - CVPR 2018
   - 金字塔光流

10. **"FlowNet: Learning Optical Flow with Convolutional Networks"**
    - ICCV 2015
    - 深度学习光流

### 神经渲染
11. **"NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis"**
    - ECCV 2020
    - 神经辐射场

12. **"Instant Neural Graphics Primitives with a Multiresolution Hash Encoding"** (Instant NGP)
    - NVIDIA, SIGGRAPH 2022
    - 实时NeRF

---

## 📖 书籍与课程

### 图形学基础
- **《Real-Time Rendering, 4th Edition》**
  - Tomas Akenine-Möller et al.
  - 实时渲染圣经

- **《Physically Based Rendering: From Theory To Implementation》**
  - Matt Pharr et al.
  - PBR理论与实践

### 深度学习
- **《Deep Learning》**
  - Ian Goodfellow et al.
  - 深度学习基础

- **CS231n: Convolutional Neural Networks for Visual Recognition**
  - Stanford Online
  - CNN基础课程

### 在线课程
- **GAMES101: 现代计算机图形学入门** (中文)
  - 闫令琪
  - Bilibili可观看

- **GAMES202: 高质量实时渲染** (中文)
  - 闫令琪
  - 光栅化与光追

---

## 🔬 研究机构与实验室

### 学术机构
- **MIT CSAIL** - Computer Vision & Graphics
- **Stanford Graphics Lab**
- **UC Berkeley Vision Group**
- **清华大学图形学实验室**

### 工业研究
- **NVIDIA Research** - https://www.nvidia.com/en-us/research/
- **AMD Research**
- **Intel Labs**

---

## 🛠️ 开发工具与SDK

### Graphics APIs
- **DirectX 12** - Microsoft
- **Vulkan** - Khronos Group
- **OpenGL** - Khronos Group

### 游戏引擎
- **Unreal Engine 5** - Epic Games
  - 内置DLSS插件
- **Unity** - Unity Technologies
  - DLSS包支持

### 调试工具
- **NVIDIA Nsight Graphics** - GPU调试与分析
- **RenderDoc** - 开源帧捕获工具
- **PIX** - DirectX调试工具

### AI框架
- **PyTorch** - Meta
- **TensorFlow** - Google
- **ONNX** - 开放神经网络交换格式

---

## 💬 社区与论坛

### 开发者社区
- **NVIDIA Developer Forums**
  - https://forums.developer.nvidia.com/
  
- **Beyond3D Forum**
  - 图形技术讨论
  
- **Reddit**
  - r/GraphicsProgramming
  - r/gamedev
  - r/computergraphics

### Discord服务器
- **Graphics Programming Discord**
- **Unreal Engine Discord**
- **NVIDIA GameWorks Discord**

---

## 📰 技术博客与媒体

### 技术博客
- **NVIDIA Technical Blog**
  - https://developer.nvidia.com/blog

- **Real-Time Rendering Blog**
  - http://www.realtimerendering.com/blog/

- **Interplay of Light**
  - Krzysztof Narkowicz技术博客

### 媒体分析
- **Digital Foundry** (Eurogamer)
  - 深度技术分析
  
- **GamersNexus**
  - 硬件与技术评测

- **TechPowerUp**
  - GPU技术新闻

---

## 🎮 示例游戏与Demo

### 支持DLSS的代表性游戏
- **《赛博朋克2077》** - 路径追踪 + DLSS 3.5
- **《控制》** - DLSS 2.0早期典范
- **《Portal RTX》** - 完全路径追踪
- **《霍格沃茨之遗》** - DLSS 3集成

### NVIDIA官方Demo
- **Marbles RTX Demo**
- **Unreal Engine 5 Tech Demos**
- **RTX技术演示合集**

---

## 📊 数据集与Benchmark

### 超分辨率数据集
- **DIV2K** - 高质量图像
- **BSD** - Berkeley Segmentation Dataset
- **Urban100** - 城市场景

### 视频数据集
- **Vimeo-90K** - 视频帧插值
- **REDS** - 视频去噪和超分辨率

### Benchmark工具
- **3DMark** - Port Royal (光追)
- **Unigine Superposition**
- **游戏内置Benchmark**

---

## 🔗 相关技术标准

### API标准
- **DirectX Raytracing (DXR)**
- **Vulkan Ray Tracing**
- **Microsoft DirectSR** - 统一超采样API

### 硬件标准
- **PCIe 4.0/5.0**
- **GDDR6/6X**
- **DisplayPort 2.0 / HDMI 2.1**

---

## 📅 会议与活动

### 重要会议
- **GDC** - 每年3月，旧金山
- **SIGGRAPH** - 每年8月
- **GTC** - NVIDIA GPU技术大会
- **I3D** - Interactive 3D Graphics

### 在线活动
- **NVIDIA GTC Digital** - 在线免费
- **SIGGRAPH Talks** - 部分免费观看

---

## 🆕 持续更新资源

### 新闻聚合
- **AnandTech** - 硬件技术新闻
- **Tom's Hardware** - GPU评测
- **Phoronix** - Linux图形栈

### arXiv监控
- **Computer Vision (cs.CV)**
- **Graphics (cs.GR)**
- **Machine Learning (cs.LG)**

关键词：
- "Super Resolution"
- "Frame Interpolation"
- "Neural Rendering"
- "Real-time Rendering"

---

## 🎓 学习路径建议

### 初学者
1. 观看Digital Foundry DLSS视频
2. 阅读本项目第1-3层文档
3. 体验支持DLSS的游戏
4. 阅读NVIDIA官方博客

### 进阶者
1. 学习Real-Time Rendering书
2. 阅读DLSS相关论文
3. 实验SDK示例代码
4. 参与开发者论坛讨论

### 研究者
1. 深入学习深度学习（CS231n）
2. 阅读SIGGRAPH/CVPR论文
3. 实现学术算法对比
4. 探索改进方向

---

## ⚠️ 注意事项

### 版权声明
- 本参考资料列表仅用于学术学习
- NVIDIA、DLSS、RTX等为NVIDIA Corporation商标
- 引用论文请遵循学术规范
- 商业应用需获得相应授权

### 资源可用性
- 部分资源可能需要注册或订阅
- GDC Vault部分内容需要会员
- 学术论文优先查找开放获取版本
- 善用Google Scholar和Sci-Hub（合法范围内）

---

## 🔄 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-01-20 | 初始版本，创建完整参考索引 |

---

**持续更新中... 欢迎补充更多优质资源！**

**→ [返回学习计划主页](./DLSS3_Architecture_Study.md)**
