"""
相机系统 - 生成穿过像素的光线
"""
import math
from src.vector3 import Vector3
from src.ray import Ray


class Camera:
    """相机类：定义视角和投影"""
    
    def __init__(self, look_from, look_at, vup, vfov, aspect_ratio):
        """
        初始化相机
        
        Args:
            look_from: Vector3 - 相机位置
            look_at: Vector3 - 观察目标点
            vup: Vector3 - 向上方向
            vfov: float - 垂直视场角（度）
            aspect_ratio: float - 宽高比
        """
        self.origin = look_from
        
        # 计算视场参数
        theta = math.radians(vfov)
        h = math.tan(theta / 2)
        viewport_height = 2.0 * h
        viewport_width = aspect_ratio * viewport_height
        
        # 构建相机坐标系
        w = (look_from - look_at).normalize()  # 相机朝向（反方向）
        u = vup.cross(w).normalize()           # 相机右方向
        v = w.cross(u)                         # 相机上方向
        
        self.horizontal = viewport_width * u
        self.vertical = viewport_height * v
        self.lower_left_corner = self.origin - self.horizontal / 2 - self.vertical / 2 - w
    
    def get_ray(self, u, v):
        """
        生成穿过像素的光线
        
        Args:
            u: float - 水平坐标 [0, 1]
            v: float - 垂直坐标 [0, 1]
            
        Returns:
            Ray - 从相机发出的光线
        """
        direction = self.lower_left_corner + u * self.horizontal + v * self.vertical - self.origin
        return Ray(self.origin, direction.normalize())