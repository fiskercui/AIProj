"""
光线类 - 表示3D空间中的射线
"""
from src.vector3 import Vector3


class Ray:
    """光线类：由起点和方向定义"""
    
    def __init__(self, origin, direction):
        """
        初始化光线
        
        Args:
            origin: Vector3 - 光线起点
            direction: Vector3 - 光线方向（应该是归一化的）
        """
        self.origin = origin
        self.direction = direction
    
    def at(self, t):
        """
        计算光线上的点
        
        光线方程: P(t) = origin + t * direction
        
        Args:
            t: float - 距离参数
            
        Returns:
            Vector3 - 光线上距离起点为t的点
        """
        return self.origin + t * self.direction
    
    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"