"""
三维向量类 - 用于表示点、方向、颜色
"""
import math


class Vector3:
    """三维向量类，支持基本的向量运算"""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __repr__(self):
        return f"Vector3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def __add__(self, other):
        """向量加法"""
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        """向量减法"""
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other):
        """标量乘法或逐元素乘法"""
        if isinstance(other, (int, float)):
            # 标量乘法
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            # 逐元素乘法（用于颜色混合）
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
    
    def __rmul__(self, other):
        """右乘（支持 scalar * vector）"""
        return self.__mul__(other)
    
    def __truediv__(self, scalar):
        """除法"""
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __neg__(self):
        """取负"""
        return Vector3(-self.x, -self.y, -self.z)
    
    def dot(self, other):
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """叉积"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        """向量长度"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def length_squared(self):
        """向量长度的平方（避免开方运算）"""
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def normalize(self):
        """归一化（返回单位向量）"""
        length = self.length()
        if length > 0:
            return self / length
        return Vector3(0, 0, 0)
    
    def near_zero(self):
        """检查向量是否接近零"""
        epsilon = 1e-8
        return abs(self.x) < epsilon and abs(self.y) < epsilon and abs(self.z) < epsilon
    
    @staticmethod
    def random(min_val=0.0, max_val=1.0):
        """生成随机向量"""
        import random
        return Vector3(
            random.uniform(min_val, max_val),
            random.uniform(min_val, max_val),
            random.uniform(min_val, max_val)
        )
    
    @staticmethod
    def random_in_unit_sphere():
        """在单位球内生成随机向量"""
        while True:
            p = Vector3.random(-1, 1)
            if p.length_squared() < 1:
                return p
    
    @staticmethod
    def random_unit_vector():
        """生成随机单位向量"""
        return Vector3.random_in_unit_sphere().normalize()
    
    @staticmethod
    def random_in_hemisphere(normal):
        """在法线所在半球内生成随机向量"""
        in_unit_sphere = Vector3.random_in_unit_sphere()
        if in_unit_sphere.dot(normal) > 0.0:
            return in_unit_sphere
        else:
            return -in_unit_sphere
    
    def reflect(self, normal):
        """反射向量（用于镜面反射）"""
        return self - 2 * self.dot(normal) * normal
    
    def refract(self, normal, etai_over_etat):
        """折射向量（用于透明材质）"""
        cos_theta = min(-self.dot(normal), 1.0)
        r_out_perp = etai_over_etat * (self + cos_theta * normal)
        r_out_parallel = -math.sqrt(abs(1.0 - r_out_perp.length_squared())) * normal
        return r_out_perp + r_out_parallel


# 常用向量常量
ZERO = Vector3(0, 0, 0)
ONE = Vector3(1, 1, 1)
UP = Vector3(0, 1, 0)
RIGHT = Vector3(1, 0, 0)
FORWARD = Vector3(0, 0, 1)