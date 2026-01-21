"""
材质系统 - 定义物体表面的光学属性
"""
import random
from src.vector3 import Vector3


class Material:
    """材质基类"""
    
    def scatter(self, ray_in, hit_record):
        """
        计算光线散射
        
        Args:
            ray_in: Ray - 入射光线
            hit_record: HitRecord - 碰撞信息
            
        Returns:
            (scattered_ray, attenuation) 或 None
        """
        raise NotImplementedError


class Lambertian(Material):
    """漫反射材质（粗糙表面）"""
    
    def __init__(self, albedo):
        """
        Args:
            albedo: Vector3 - 反照率（颜色）
        """
        self.albedo = albedo
    
    def scatter(self, ray_in, hit_record):
        """漫反射散射：随机方向"""
        from src.ray import Ray
        
        # 在法线方向的半球内随机散射
        scatter_direction = hit_record.normal + Vector3.random_unit_vector()
        
        # 防止散射方向为零向量
        if scatter_direction.near_zero():
            scatter_direction = hit_record.normal
        
        scattered = Ray(hit_record.point, scatter_direction.normalize())
        attenuation = self.albedo
        
        return scattered, attenuation


class Metal(Material):
    """金属材质（镜面反射）"""
    
    def __init__(self, albedo, fuzz=0.0):
        """
        Args:
            albedo: Vector3 - 反照率（颜色）
            fuzz: float - 模糊度 [0, 1]，0表示完美镜面
        """
        self.albedo = albedo
        self.fuzz = min(fuzz, 1.0)
    
    def scatter(self, ray_in, hit_record):
        """镜面反射"""
        from src.ray import Ray
        
        reflected = ray_in.direction.reflect(hit_record.normal)
        
        # 添加模糊（在反射方向周围随机偏移）
        scattered = Ray(
            hit_record.point,
            (reflected + self.fuzz * Vector3.random_in_unit_sphere()).normalize()
        )
        attenuation = self.albedo
        
        # 只有反射方向在表面上方时才散射
        if scattered.direction.dot(hit_record.normal) > 0:
            return scattered, attenuation
        else:
            return None


class Dielectric(Material):
    """电介质材质（透明，如玻璃）"""
    
    def __init__(self, refractive_index):
        """
        Args:
            refractive_index: float - 折射率（空气=1.0, 玻璃≈1.5, 水≈1.33）
        """
        self.refractive_index = refractive_index
    
    def scatter(self, ray_in, hit_record):
        """折射和反射"""
        from src.ray import Ray
        
        attenuation = Vector3(1.0, 1.0, 1.0)  # 玻璃不吸收光
        
        # 判断光线是从外部进入还是从内部射出
        if hit_record.front_face:
            etai_over_etat = 1.0 / self.refractive_index
        else:
            etai_over_etat = self.refractive_index
        
        unit_direction = ray_in.direction.normalize()
        
        # 计算折射
        cos_theta = min(-unit_direction.dot(hit_record.normal), 1.0)
        sin_theta = (1.0 - cos_theta * cos_theta) ** 0.5
        
        # 全反射判断
        cannot_refract = etai_over_etat * sin_theta > 1.0
        
        # Schlick近似（菲涅尔反射）
        reflectance = self._reflectance(cos_theta, etai_over_etat)
        
        if cannot_refract or reflectance > random.random():
            # 反射
            direction = unit_direction.reflect(hit_record.normal)
        else:
            # 折射
            direction = unit_direction.refract(hit_record.normal, etai_over_etat)
        
        scattered = Ray(hit_record.point, direction)
        return scattered, attenuation
    
    @staticmethod
    def _reflectance(cosine, ref_idx):
        """Schlick近似计算反射率"""
        r0 = (1 - ref_idx) / (1 + ref_idx)
        r0 = r0 * r0
        return r0 + (1 - r0) * ((1 - cosine) ** 5)