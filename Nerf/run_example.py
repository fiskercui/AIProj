"""
NeRF 运行示例
快速入门脚本，生成合成数据并训练简单的 NeRF 模型

运行方式：
    python run_example.py
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
import os

from tiny_nerf import TinyNeRF, train_nerf, render_image, get_rays


# ==================== 合成数据生成 ====================
def generate_synthetic_data(N_images=20, H=100, W=100):
    """
    生成简单的合成场景数据
    场景：一个彩色球体
    
    参数:
        N_images: 图像数量
        H, W: 图像尺寸
    
    返回:
        images: 图像数据 [N_images, H, W, 3]
        poses: 相机位姿 [N_images, 4, 4]
        focal: 焦距
    """
    print("🎨 生成合成场景数据...")
    
    focal = 100.0  # 焦距
    radius = 4.0   # 相机到原点的距离
    
    images = []
    poses = []
    
    # 生成围绕物体的相机轨迹
    for i in range(N_images):
        # 相机位置（圆形轨迹）
        theta = 2.0 * np.pi * i / N_images
        cam_pos = np.array([
            radius * np.cos(theta),
            radius * np.sin(theta),
            0.0
        ])
        
        # 构建相机到世界坐标系的变换矩阵
        # 相机朝向原点
        forward = -cam_pos / np.linalg.norm(cam_pos)  # z 轴
        up = np.array([0.0, 0.0, 1.0])                # 世界 z 轴向上
        right = np.cross(up, forward)                 # x 轴
        right = right / np.linalg.norm(right)
        up = np.cross(forward, right)                 # 重新计算 y 轴
        
        # 组装变换矩阵
        c2w = np.eye(4)
        c2w[:3, 0] = right
        c2w[:3, 1] = up
        c2w[:3, 2] = forward
        c2w[:3, 3] = cam_pos
        
        poses.append(c2w)
        
        # 生成图像（渲染一个简单的球体）
        img = render_synthetic_sphere(H, W, focal, c2w)
        images.append(img)
    
    images = np.stack(images, axis=0)
    poses = np.stack(poses, axis=0)
    
    print(f"  ✓ 生成 {N_images} 张 {H}x{W} 图像")
    
    return torch.from_numpy(images).float(), torch.from_numpy(poses).float(), focal


def render_synthetic_sphere(H, W, focal, c2w):
    """
    渲染一个彩色球体（作为训练数据）
    
    参数:
        H, W: 图像尺寸
        focal: 焦距
        c2w: 相机到世界变换矩阵
    
    返回:
        img: 渲染的图像 [H, W, 3]
    """
    img = np.ones((H, W, 3))  # 白色背景
    
    # 球体参数
    sphere_center = np.array([0.0, 0.0, 0.0])
    sphere_radius = 1.0
    
    # 相机参数
    cam_pos = c2w[:3, 3]
    
    # 遍历每个像素
    for i in range(H):
        for j in range(W):
            # 计算光线方向（相机坐标系）
            x = (j - W * 0.5) / focal
            y = -(i - H * 0.5) / focal
            z = -1.0
            
            ray_dir_cam = np.array([x, y, z])
            
            # 转换到世界坐标系
            ray_dir = c2w[:3, :3] @ ray_dir_cam
            ray_dir = ray_dir / np.linalg.norm(ray_dir)
            
            # 光线-球体相交检测
            oc = cam_pos - sphere_center
            a = np.dot(ray_dir, ray_dir)
            b = 2.0 * np.dot(oc, ray_dir)
            c = np.dot(oc, oc) - sphere_radius * sphere_radius
            discriminant = b * b - 4 * a * c
            
            if discriminant > 0:
                # 相交，计算交点
                t = (-b - np.sqrt(discriminant)) / (2.0 * a)
                if t > 0:
                    # 计算交点位置和法向量
                    hit_point = cam_pos + t * ray_dir
                    normal = (hit_point - sphere_center) / sphere_radius
                    
                    # 简单的着色（基于法向量）
                    color = (normal + 1.0) * 0.5  # 映射到 [0, 1]
                    img[i, j] = color
    
    return img


# ==================== 主程序 ====================
def main():
    """主程序：生成数据、训练模型、渲染结果"""
    
    print("=" * 60)
    print("🚀 NeRF 训练示例")
    print("=" * 60)
    
    # -------------------- 配置参数 --------------------
    # 数据参数
    N_train_images = 20      # 训练图像数量
    H, W = 100, 100         # 图像尺寸（较小以加快速度）
    
    # 模型参数
    pos_L = 6               # 位置编码级别（越大越精细）
    dir_L = 4               # 方向编码级别
    hidden_dim = 128        # 隐藏层维度
    use_viewdir = True      # 是否使用观察方向
    
    # 训练参数
    epochs = 500            # 训练轮数（增加可提高质量）
    batch_size = 1024       # 每批光线数
    lr = 5e-4               # 学习率
    
    # 设备设置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n💻 使用设备: {device}")
    
    if device.type == 'cpu':
        print("   ⚠️  建议使用 GPU 以加快训练速度")
    
    # -------------------- 生成数据 --------------------
    images, poses, focal = generate_synthetic_data(N_train_images, H, W)
    
    print(f"\n📊 数据信息:")
    print(f"  - 图像数量: {images.shape[0]}")
    print(f"  - 图像尺寸: {H} x {W}")
    print(f"  - 焦距: {focal}")
    print(f"  - 总像素数: {images.shape[0] * H * W:,}")
    
    # -------------------- 创建模型 --------------------
    print("\n🏗️  创建 NeRF 模型...")
    model = TinyNeRF(
        pos_L=pos_L,
        dir_L=dir_L,
        hidden_dim=hidden_dim,
        use_viewdir=use_viewdir
    )
    
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  ✓ 模型参数数量: {n_params:,}")
    
    # -------------------- 训练模型 --------------------
    print(f"\n🎓 开始训练 (共 {epochs} 轮)...")
    print("   这可能需要几分钟，请耐心等待...")
    
    losses = train_nerf(
        model=model,
        images=images,
        poses=poses,
        focal=focal,
        H=H,
        W=W,
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
        device=device,
        verbose=True
    )
    
    print("  ✓ 训练完成！")
    
    # -------------------- 可视化训练过程 --------------------
    print("\n📈 保存训练曲线...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    plt.figure(figsize=(10, 5))
    plt.plot(losses)
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.title('NeRF Training Loss')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    training_plot_path = output_dir / "training_loss.png"
    plt.savefig(training_plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 训练曲线已保存: {training_plot_path}")
    
    # -------------------- 渲染测试视角 --------------------
    print("\n🎬 渲染测试视角...")
    
    # 选择几个测试视角
    test_indices = [0, N_train_images // 4, N_train_images // 2, 3 * N_train_images // 4]
    
    fig, axes = plt.subplots(2, len(test_indices), figsize=(15, 7))
    
    for idx, test_idx in enumerate(test_indices):
        # 渲染
        test_pose = poses[test_idx]
        rendered_img = render_image(
            model=model,
            pose=test_pose,
            H=H,
            W=W,
            focal=focal,
            device=device,
            chunk=512
        )
        
        # 显示真实图像
        axes[0, idx].imshow(images[test_idx].numpy())
        axes[0, idx].set_title(f'Ground Truth (View {test_idx})')
        axes[0, idx].axis('off')
        
        # 显示渲染图像
        axes[1, idx].imshow(rendered_img.numpy())
        axes[1, idx].set_title(f'NeRF Render (View {test_idx})')
        axes[1, idx].axis('off')
    
    plt.tight_layout()
    comparison_path = output_dir / "render_comparison.png"
    plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 对比图已保存: {comparison_path}")
    
    # -------------------- 渲染新视角 --------------------
    print("\n🆕 渲染全新视角（模型未见过的角度）...")
    
    # 生成一个新的相机位置
    theta_new = np.pi / 3  # 60 度
    radius = 4.0
    cam_pos_new = np.array([
        radius * np.cos(theta_new),
        radius * np.sin(theta_new),
        0.5  # 稍微向上
    ])
    
    # 构建变换矩阵
    forward = -cam_pos_new / np.linalg.norm(cam_pos_new)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(up, forward)
    right = right / np.linalg.norm(right)
    up = np.cross(forward, right)
    
    c2w_new = np.eye(4)
    c2w_new[:3, 0] = right
    c2w_new[:3, 1] = up
    c2w_new[:3, 2] = forward
    c2w_new[:3, 3] = cam_pos_new
    
    pose_new = torch.from_numpy(c2w_new).float()
    
    # 渲染
    novel_img = render_image(
        model=model,
        pose=pose_new,
        H=H,
        W=W,
        focal=focal,
        device=device,
        chunk=512
    )
    
    plt.figure(figsize=(8, 8))
    plt.imshow(novel_img.numpy())
    plt.title('Novel View Synthesis (新视角合成)')
    plt.axis('off')
    novel_path = output_dir / "novel_view.png"
    plt.savefig(novel_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 新视角渲染已保存: {novel_path}")
    
    # -------------------- 完成 --------------------
    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print("=" * 60)
    print(f"\n📁 输出文件位置: {output_dir.absolute()}")
    print(f"  - {training_plot_path.name}: 训练损失曲线")
    print(f"  - {comparison_path.name}: 真实 vs 渲染对比")
    print(f"  - {novel_path.name}: 新视角合成结果")
    
    print("\n💡 下一步可以尝试:")
    print("  1. 增加训练轮数 (epochs) 以提高质量")
    print("  2. 增加图像分辨率 (H, W) 获得更精细的结果")
    print("  3. 调整模型参数 (hidden_dim, pos_L) 改变容量")
    print("  4. 使用真实数据集（如 NeRF Synthetic Dataset）")
    
    print("\n📚 学习建议:")
    print("  - 阅读 tiny_nerf.py 中的代码和注释")
    print("  - 理解位置编码、体积渲染的作用")
    print("  - 尝试可视化中间结果（密度场、颜色场等）")
    
    print("\n🎉 祝你学习愉快！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  训练被用户中断")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 如需帮助，请检查 README.md 或提 issue")
