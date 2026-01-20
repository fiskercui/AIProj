"""
简单的测试脚本 - 创建一个测试图像并进行放大
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    """创建一个测试图像"""
    # 创建一个小图像用于测试
    width, height = 200, 200
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 绘制一些图形
    # 绘制红色矩形
    draw.rectangle([20, 20, 80, 80], fill=(255, 0, 0), outline=(0, 0, 0), width=2)
    
    # 绘制绿色圆形
    draw.ellipse([120, 20, 180, 80], fill=(0, 255, 0), outline=(0, 0, 0), width=2)
    
    # 绘制蓝色三角形
    draw.polygon([(50, 120), (20, 180), (80, 180)], fill=(0, 0, 255), outline=(0, 0, 0))
    
    # 绘制黄色星形
    draw.polygon([(150, 120), (160, 145), (185, 145), (165, 160), (175, 185), 
                  (150, 170), (125, 185), (135, 160), (115, 145), (140, 145)], 
                 fill=(255, 255, 0), outline=(0, 0, 0))
    
    # 保存图像
    os.makedirs('inputs', exist_ok=True)
    test_image_path = 'inputs/test_image.png'
    img.save(test_image_path)
    print(f"✓ 测试图像已创建: {test_image_path}")
    print(f"  图像大小: {width}x{height} pixels")
    return test_image_path

if __name__ == '__main__':
    create_test_image()
    print("\n下一步：运行以下命令进行图像放大测试：")
    print("python inference.py -i inputs/test_image.png -o outputs/test_image_upscaled.png")
