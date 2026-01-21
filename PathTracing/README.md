# 路径追踪渲染器 (Path Tracing Renderer)

一个使用Python实现的离线路径追踪渲染器。

## 特性

- ✅ 基于物理的路径追踪算法
- ✅ 多种材质支持（漫反射、金属、玻璃）
- ✅ 多重采样抗锯齿（MSAA）
- ✅ 递归光线追踪
- ✅ 简洁易懂的代码结构

## 项目结构

```
PathTracing/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── vector3.py         # 三维向量运算
│   ├── ray.py             # 光线类
│   ├── camera.py          # 相机系统
│   ├── objects.py         # 几何体（球体等）
│   ├── material.py        # 材质系统
│   └── renderer.py        # 渲染器核心
├── scenes/                # 场景定义
│   └── demo_scene.py      # 演示场景
├── output/                # 渲染输出目录
├── main.py                # 主程序入口
├── requirements.txt       # Python依赖
└── README.md              # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install numpy pillow
```

## 使用方法

### 基础使用

直接运行主程序：
```bash
python main.py
```

渲染结果将保存在 `output/render.png`

### 调整渲染参数

编辑 `main.py` 中的参数：

```python
# 图像尺寸
image_width = 400          # 宽度（像素）
aspect_ratio = 16.0 / 9.0  # 宽高比

# 渲染质量
samples_per_pixel = 100    # 每像素采样数（越大越清晰，但越慢）
max_depth = 50             # 最大光线反弹次数
```

### 选择不同场景

在 `main.py` 中切换场景：

```python
scene = create_demo_scene()      # 完整演示场景（漫反射+金属+玻璃）
# scene = create_simple_scene()  # 简单场景（只有漫反射）
# scene = create_metal_scene()   # 金属材质展示
```

## 渲染时间估算

| 图像尺寸 | 采样数 | 预计时间 |
|---------|--------|---------|
| 400x225 | 10     | ~30秒   |
| 400x225 | 100    | ~5分钟  |
| 800x450 | 100    | ~20分钟 |
| 1920x1080 | 100  | ~2小时  |

## 核心概念

### 1. 路径追踪算法

每个像素发射多条光线，递归追踪光线与场景的交互，累积颜色信息。

### 2. 材质系统

- **Lambertian（漫反射）**：粗糙表面，光线随机散射
- **Metal（金属）**：镜面反射，可调节模糊度
- **Dielectric（电介质）**：透明材质，支持折射

### 3. 多重采样

对每个像素发射多条随机光线并平均，实现抗锯齿效果。

## 示例代码

### 创建自定义场景

```python
from src.vector3 import Vector3
from src.objects import HittableList, Sphere
from src.material import Lambertian, Metal

def my_scene():
    scene = HittableList()
    
    # 添加地面
    ground = Lambertian(Vector3(0.5, 0.5, 0.5))
    scene.add(Sphere(Vector3(0, -100.5, -1), 100, ground))
    
    # 添加红色球体
    red_ball = Lambertian(Vector3(0.8, 0.2, 0.2))
    scene.add(Sphere(Vector3(0, 0, -1), 0.5, red_ball))
    
    return scene
```

### 调整相机视角

```python
camera = Camera(
    look_from=Vector3(3, 3, 2),    # 相机位置
    look_at=Vector3(0, 0, -1),     # 观察目标
    vup=Vector3(0, 1, 0),          # 向上方向
    vfov=20,                        # 视场角（度）
    aspect_ratio=16.0/9.0
)
```

## 优化建议

### 快速预览

降低渲染质量用于快速预览：
```python
image_width = 200
samples_per_pixel = 10
```

### 高质量渲染

提高参数获得更好的效果：
```python
image_width = 1920
samples_per_pixel = 500
```

## 技术细节

### 光线方程
```
P(t) = Origin + t * Direction
```

### 球体相交
```
(P - C)·(P - C) = r²
```

### 反射公式
```
R = V - 2(V·N)N
```

### Snell折射定律
```
η₁ sin θ₁ = η₂ sin θ₂
```

## 扩展功能（未来）

- [ ] 三角形网格支持
- [ ] BVH加速结构
- [ ] 多线程渲染
- [ ] 重要性采样
- [ ] 景深效果
- [ ] 运动模糊
- [ ] 纹理贴图

## 参考资料

- [Ray Tracing in One Weekend](https://raytracing.github.io/)
- [Physically Based Rendering](https://pbr-book.org/)

## 许可证

MIT License

## 作者

Created with ❤️ using Python