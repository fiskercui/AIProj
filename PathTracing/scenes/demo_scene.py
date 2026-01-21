"""
演示场景 - 包含不同材质的球体
"""
from src.vector3 import Vector3
from src.objects import HittableList, Sphere
from src.material import Lambertian, Metal, Dielectric


def create_demo_scene():
    """
    创建一个包含多种材质球体的演示场景
    
    Returns:
        HittableList - 场景对象
    """
    scene = HittableList()
    
    # 地面（大球体）
    ground_material = Lambertian(Vector3(0.5, 0.5, 0.5))
    scene.add(Sphere(Vector3(0, -100.5, -1), 100, ground_material))
    
    # 中心球体 - 漫反射（红色）
    material_center = Lambertian(Vector3(0.7, 0.3, 0.3))
    scene.add(Sphere(Vector3(0, 0, -1), 0.5, material_center))
    
    # 左侧球体 - 玻璃（透明）
    material_left = Dielectric(1.5)
    scene.add(Sphere(Vector3(-1, 0, -1), 0.5, material_left))
    
    # 右侧球体 - 金属（金色）
    material_right = Metal(Vector3(0.8, 0.6, 0.2), 0.0)
    scene.add(Sphere(Vector3(1, 0, -1), 0.5, material_right))
    
    return scene


def create_simple_scene():
    """
    创建一个简单场景（用于快速测试）
    
    Returns:
        HittableList - 场景对象
    """
    scene = HittableList()
    
    # 地面
    ground_material = Lambertian(Vector3(0.8, 0.8, 0.0))
    scene.add(Sphere(Vector3(0, -100.5, -1), 100, ground_material))
    
    # 一个红色球体
    center_material = Lambertian(Vector3(0.7, 0.3, 0.3))
    scene.add(Sphere(Vector3(0, 0, -1), 0.5, center_material))
    
    return scene


def create_metal_scene():
    """
    创建一个展示金属材质的场景
    
    Returns:
        HittableList - 场景对象
    """
    scene = HittableList()
    
    # 地面
    ground_material = Lambertian(Vector3(0.8, 0.8, 0.8))
    scene.add(Sphere(Vector3(0, -100.5, -1), 100, ground_material))
    
    # 左：模糊金属
    material_left = Metal(Vector3(0.8, 0.8, 0.8), 0.3)
    scene.add(Sphere(Vector3(-1, 0, -1), 0.5, material_left))
    
    # 中：完美镜面
    material_center = Metal(Vector3(0.8, 0.6, 0.2), 0.0)
    scene.add(Sphere(Vector3(0, 0, -1), 0.5, material_center))
    
    # 右：很模糊的金属
    material_right = Metal(Vector3(0.8, 0.8, 0.8), 1.0)
    scene.add(Sphere(Vector3(1, 0, -1), 0.5, material_right))
    
    return scene