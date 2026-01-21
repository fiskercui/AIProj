"""
几何体 - 可被光线追踪的3D物体
"""
import math
from src.vector3 import Vector3


class HitRecord:
    """碰撞记录：存储光线与物体相交的信息"""
    
    def __init__(self):
        self.point = None      # 交点位置
        self.normal = None     # 表面法线
        self.t = 0.0           # 光线参数t
        self.front_face = True # 是否从外部击中
        self.material = None   # 材质
    
    def set_face_normal(self, ray, outward_normal):
        """
        设置法线方向（始终指向光线来源侧）
        
        Args:
            ray: Ray - 入射光线
            outward_normal: Vector3 - 向外的法线
        """
        self.front_face = ray.direction.dot(outward_normal) < 0
        self.normal = outward_normal if self.front_face else -outward_normal


class Hittable:
    """可碰撞对象基类"""
    
    def hit(self, ray, t_min, t_max):
        """
        检测光线是否击中物体
        
        Args:
            ray: Ray - 光线
            t_min: float - t的最小值
            t_max: float - t的最大值
            
        Returns:
            HitRecord 或 None
        """
        raise NotImplementedError


class Sphere(Hittable):
    """球体"""
    
    def __init__(self, center, radius, material):
        """
        Args:
            center: Vector3 - 球心
            radius: float - 半径
            material: Material - 材质
        """
        self.center = center
        self.radius = radius
        self.material = material
    
    def hit(self, ray, t_min, t_max):
        """
        光线-球体相交检测
        
        数学原理：
        球体方程: (P - C)·(P - C) = r²
        光线方程: P(t) = O + t*D
        
        代入得到二次方程：
        (O + t*D - C)·(O + t*D - C) = r²
        
        展开：
        t²(D·D) + 2t*D·(O-C) + (O-C)·(O-C) - r² = 0
        
        使用求根公式求解t
        """
        oc = ray.origin - self.center
        
        # 二次方程系数
        a = ray.direction.dot(ray.direction)
        half_b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        
        # 判别式
        discriminant = half_b * half_b - a * c
        
        if discriminant < 0:
            return None  # 无交点
        
        # 找到在[t_min, t_max]范围内的最近交点
        sqrtd = math.sqrt(discriminant)
        
        # 尝试较小的根
        root = (-half_b - sqrtd) / a
        if root < t_min or root > t_max:
            # 尝试较大的根
            root = (-half_b + sqrtd) / a
            if root < t_min or root > t_max:
                return None  # 两个根都不在范围内
        
        # 创建碰撞记录
        rec = HitRecord()
        rec.t = root
        rec.point = ray.at(rec.t)
        outward_normal = (rec.point - self.center) / self.radius
        rec.set_face_normal(ray, outward_normal)
        rec.material = self.material
        
        return rec


class HittableList(Hittable):
    """物体列表（场景）"""
    
    def __init__(self):
        self.objects = []
    
    def add(self, obj):
        """添加物体到场景"""
        self.objects.append(obj)
    
    def clear(self):
        """清空场景"""
        self.objects.clear()
    
    def hit(self, ray, t_min, t_max):
        """
        检测光线与场景中所有物体的碰撞
        返回最近的碰撞点
        """
        hit_anything = None
        closest_so_far = t_max
        
        for obj in self.objects:
            rec = obj.hit(ray, t_min, closest_so_far)
            if rec:
                hit_anything = rec
                closest_so_far = rec.t
        
        return hit_anything