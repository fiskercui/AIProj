"""
快速测试脚本 - 低质量快速渲染
"""
from src.vector3 import Vector3
from src.camera import Camera
from src.renderer import Renderer
from scenes.demo_scene import create_simple_scene


def main():
    """快速测试主函数"""
    
    print("="*50)
    print("快速测试渲染器")
    print("="*50)
    
    # 低分辨率参数（快速测试）
    aspect_ratio = 16.0 / 9.0
    image_width = 200  # 小尺寸
    image_height = int(image_width / aspect_ratio)
    
    # 低采样数（快速渲染）
    samples_per_pixel = 10  # 只用10个样本
    max_depth = 10          # 较低深度
    
    # 创建相机
    camera = Camera(
        look_from=Vector3(0, 0, 0),
        look_at=Vector3(0, 0, -1),
        vup=Vector3(0, 1, 0),
        vfov=90,
        aspect_ratio=aspect_ratio
    )
    
    # 创建简单场景（只有2个球体）
    print("\n创建简单场景...")
    scene = create_simple_scene()
    
    # 创建渲染器
    renderer = Renderer(
        max_depth=max_depth,
        samples_per_pixel=samples_per_pixel
    )
    
    # 渲染
    print("\n开始快速测试渲染...")
    pixels = renderer.render(scene, camera, image_width, image_height)
    
    # 保存
    output_path = "output/test_render.png"
    renderer.save_image(pixels, output_path)
    
    print("\n" + "="*50)
    print("快速测试完成！")
    print(f"输出: {output_path}")
    print("="*50)


if __name__ == "__main__":
    main()