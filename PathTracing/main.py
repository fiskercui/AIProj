"""
路径追踪渲染器 - 主程序入口

使用方法:
    python main.py
"""
from src.vector3 import Vector3
from src.camera import Camera
from src.renderer import Renderer
from scenes.demo_scene import create_demo_scene, create_simple_scene, create_metal_scene


def main():
    """主函数"""
    
    # 图像参数
    aspect_ratio = 16.0 / 9.0
    image_width = 400
    image_height = int(image_width / aspect_ratio)
    
    # 渲染参数
    samples_per_pixel = 100  # 每像素采样数（越大质量越好，但速度越慢）
    max_depth = 50           # 最大递归深度
    
    # 创建相机
    camera = Camera(
        look_from=Vector3(0, 0, 0),    # 相机位置
        look_at=Vector3(0, 0, -1),     # 观察目标
        vup=Vector3(0, 1, 0),          # 向上方向
        vfov=90,                        # 垂直视场角
        aspect_ratio=aspect_ratio
    )
    
    # 创建场景（可选择不同的场景）
    print("创建场景...")
    scene = create_demo_scene()      # 完整演示场景
    # scene = create_simple_scene()  # 简单测试场景（渲染更快）
    # scene = create_metal_scene()   # 金属材质展示场景
    
    # 创建渲染器
    renderer = Renderer(
        max_depth=max_depth,
        samples_per_pixel=samples_per_pixel
    )
    
    # 渲染场景
    print("\n" + "="*50)
    pixels = renderer.render(scene, camera, image_width, image_height)
    
    # 保存图像
    output_path = "output/render.png"
    print("\n保存图像...")
    renderer.save_image(pixels, output_path)
    
    print("\n" + "="*50)
    print("渲染完成！")
    print(f"输出文件: {output_path}")
    print("="*50)


if __name__ == "__main__":
    main()