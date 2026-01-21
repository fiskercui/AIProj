"""
渲染器 - 路径追踪核心算法
"""
import random
from src.vector3 import Vector3
from src.ray import Ray


class Renderer:
    """路径追踪渲染器"""
    
    def __init__(self, max_depth=50, samples_per_pixel=10):
        """
        Args:
            max_depth: int - 最大递归深度
            samples_per_pixel: int - 每像素采样数（用于抗锯齿）
        """
        self.max_depth = max_depth
        self.samples_per_pixel = samples_per_pixel
    
    def render(self, scene, camera, image_width, image_height):
        """
        渲染场景
        
        Args:
            scene: HittableList - 场景
            camera: Camera - 相机
            image_width: int - 图像宽度
            image_height: int - 图像高度
            
        Returns:
            list of list of Vector3 - 像素颜色数组
        """
        pixels = []
        
        print(f"开始渲染 {image_width}x{image_height} 图像...")
        print(f"每像素采样数: {self.samples_per_pixel}")
        print(f"最大递归深度: {self.max_depth}")
        
        for j in range(image_height - 1, -1, -1):
            if (image_height - j) % 10 == 0:
                print(f"进度: {image_height - j}/{image_height} 行")
            
            row = []
            for i in range(image_width):
                pixel_color = Vector3(0, 0, 0)
                
                # 多重采样抗锯齿
                for _ in range(self.samples_per_pixel):
                    # 添加随机偏移
                    u = (i + random.random()) / (image_width - 1)
                    v = (j + random.random()) / (image_height - 1)
                    
                    ray = camera.get_ray(u, v)
                    pixel_color = pixel_color + self.ray_color(ray, scene, self.max_depth)
                
                # 平均颜色
                pixel_color = pixel_color / self.samples_per_pixel
                row.append(pixel_color)
            
            pixels.append(row)
        
        print("渲染完成！")
        return pixels
    
    def ray_color(self, ray, scene, depth):
        """
        计算光线的颜色（递归路径追踪）
        
        Args:
            ray: Ray - 光线
            scene: HittableList - 场景
            depth: int - 当前递归深度
            
        Returns:
            Vector3 - 颜色
        """
        # 递归终止条件：达到最大深度
        if depth <= 0:
            return Vector3(0, 0, 0)  # 黑色
        
        # 检测光线与场景的碰撞
        # 使用0.001而不是0，避免"shadow acne"（阴影痤疮）问题
        hit_record = scene.hit(ray, 0.001, float('inf'))
        
        if hit_record:
            # 击中物体：根据材质散射光线
            scatter_result = hit_record.material.scatter(ray, hit_record)
            
            if scatter_result:
                scattered_ray, attenuation = scatter_result
                
                # 递归追踪散射光线
                scattered_color = self.ray_color(scattered_ray, scene, depth - 1)
                
                # 返回 材质颜色 * 反射光颜色
                return attenuation * scattered_color
            else:
                # 材质吸收所有光线（如金属反射到表面下方）
                return Vector3(0, 0, 0)
        
        # 未击中任何物体：返回天空/背景色
        return self._sky_color(ray)
    
    def _sky_color(self, ray):
        """
        天空颜色（渐变背景）
        
        从白色渐变到蓝色
        """
        unit_direction = ray.direction.normalize()
        t = 0.5 * (unit_direction.y + 1.0)  # 映射到[0, 1]
        
        # 线性插值：白色(1,1,1) -> 天蓝色(0.5,0.7,1.0)
        white = Vector3(1.0, 1.0, 1.0)
        blue = Vector3(0.5, 0.7, 1.0)
        
        return (1.0 - t) * white + t * blue
    
    @staticmethod
    def save_image(pixels, filename):
        """
        保存渲染结果为PNG图像
        
        Args:
            pixels: list of list of Vector3 - 像素数据
            filename: str - 输出文件名
        """
        from PIL import Image
        import numpy as np
        
        height = len(pixels)
        width = len(pixels[0]) if height > 0 else 0
        
        # 创建图像数组
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        for j in range(height):
            for i in range(width):
                color = pixels[j][i]
                
                # 伽马校正（gamma = 2.0）
                r = color.x ** 0.5
                g = color.y ** 0.5
                b = color.z ** 0.5
                
                # 裁剪到[0, 1]并转换到[0, 255]
                r = int(256 * max(0, min(0.999, r)))
                g = int(256 * max(0, min(0.999, g)))
                b = int(256 * max(0, min(0.999, b)))
                
                img_array[j, i] = [r, g, b]
        
        # 保存图像
        img = Image.fromarray(img_array)
        img.save(filename)
        print(f"图像已保存到: {filename}")