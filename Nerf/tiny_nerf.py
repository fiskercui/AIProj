"""
Tiny NeRF (Neural Radiance Fields) 实现
简化版本，用于学习和理解 NeRF 核心原理

主要组件：
1. 位置编码 (Positional Encoding)
2. NeRF 神经网络模型
3. 体积渲染 (Volume Rendering)
4. 训练函数
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


# ==================== 位置编码 ====================
def positional_encoding(x, L=10):
    """
    位置编码：将输入映射到高频空间
    
    参数:
        x: 输入张量 [..., C]
        L: 编码级别数 (默认 10)
    
    返回:
        编码后的张量 [..., C * (2L + 1)]
    
    原理：
        γ(p) = [p, sin(2^0πp), cos(2^0πp), ..., sin(2^(L-1)πp), cos(2^(L-1)πp)]
        帮助神经网络学习高频细节
    """
    encoding = [x]
    for i in range(L):
        freq = 2.0 ** i
        encoding.append(torch.sin(freq * np.pi * x))
        encoding.append(torch.cos(freq * np.pi * x))
    return torch.cat(encoding, dim=-1)


# ==================== NeRF 神经网络 ====================
class TinyNeRF(nn.Module):
    """
    NeRF 神经网络模型
    
    输入: 3D 坐标 (x, y, z) + 观察方向 (θ, φ)
    输出: RGB 颜色 + 密度 σ
    """
    
    def __init__(self, 
                 pos_L=10,          # 位置编码级别
                 dir_L=4,           # 方向编码级别
                 hidden_dim=256,    # 隐藏层维度
                 use_viewdir=True): # 是否使用观察方向
        """
        初始化 NeRF 模型
        
        参数:
            pos_L: 位置编码的频率级别
            dir_L: 方向编码的频率级别
            hidden_dim: 隐藏层神经元数量
            use_viewdir: 是否考虑观察方向（影响渲染质量）
        """
        super(TinyNeRF, self).__init__()
        
        self.pos_L = pos_L
        self.dir_L = dir_L
        self.use_viewdir = use_viewdir
        
        # 计算输入维度
        # 位置：3D 坐标经过 L 级编码 -> 3 * (2*L + 1)
        pos_input_dim = 3 * (2 * pos_L + 1)
        
        # 第一部分：处理位置信息
        self.pos_net = nn.Sequential(
            nn.Linear(pos_input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        # 密度输出层（只依赖位置）
        self.density_layer = nn.Linear(hidden_dim, 1)
        
        # 第二部分：处理方向信息（如果使用）
        if use_viewdir:
            # 方向：2D 方向向量经过编码 -> 3 * (2*dir_L + 1)
            dir_input_dim = 3 * (2 * dir_L + 1)
            
            self.feature_layer = nn.Linear(hidden_dim, hidden_dim)
            
            # 合并特征和方向
            self.color_net = nn.Sequential(
                nn.Linear(hidden_dim + dir_input_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Linear(hidden_dim // 2, 3),  # RGB
                nn.Sigmoid()  # 输出范围 [0, 1]
            )
        else:
            # 直接从位置特征预测颜色
            self.color_net = nn.Sequential(
                nn.Linear(hidden_dim, 3),
                nn.Sigmoid()
            )
    
    def forward(self, x, d=None):
        """
        前向传播
        
        参数:
            x: 3D 位置 [..., 3]
            d: 观察方向 [..., 3] (可选)
        
        返回:
            rgb: 颜色 [..., 3]
            sigma: 密度 [..., 1]
        """
        # 位置编码
        x_encoded = positional_encoding(x, L=self.pos_L)
        
        # 提取位置特征
        h = self.pos_net(x_encoded)
        
        # 预测密度（始终非负）
        sigma = F.relu(self.density_layer(h))
        
        # 预测颜色
        if self.use_viewdir and d is not None:
            # 使用观察方向
            d_encoded = positional_encoding(d, L=self.dir_L)
            feature = self.feature_layer(h)
            rgb = self.color_net(torch.cat([feature, d_encoded], dim=-1))
        else:
            # 不使用观察方向
            rgb = self.color_net(h)
        
        return rgb, sigma


# ==================== 体积渲染 ====================
def volume_rendering(rgb, sigma, z_vals, white_bkgd=True):
    """
    体积渲染：沿着光线积分颜色和密度
    
    参数:
        rgb: 颜色值 [N_rays, N_samples, 3]
        sigma: 密度值 [N_rays, N_samples, 1]
        z_vals: 深度值 [N_rays, N_samples]
        white_bkgd: 是否使用白色背景
    
    返回:
        rendered_rgb: 渲染的颜色 [N_rays, 3]
        
    原理：
        C(r) = Σ T_i * α_i * c_i
        其中 T_i = exp(-Σ σ_j * δ_j) 是透射率
             α_i = 1 - exp(-σ_i * δ_i) 是不透明度
    """
    # 计算相邻采样点之间的距离
    dists = z_vals[..., 1:] - z_vals[..., :-1]
    dists = torch.cat([dists, torch.ones_like(dists[..., :1]) * 1e10], dim=-1)  # [N_rays, N_samples]
    
    # 计算每个采样点的不透明度
    alpha = 1.0 - torch.exp(-F.relu(sigma[..., 0]) * dists)  # [N_rays, N_samples]
    
    # 计算透射率（累积透明度）
    # T_i = exp(-Σ_{j=1}^{i-1} σ_j * δ_j)
    transmittance = torch.cumprod(
        torch.cat([torch.ones_like(alpha[..., :1]), 1.0 - alpha + 1e-10], dim=-1),
        dim=-1
    )[..., :-1]  # [N_rays, N_samples]
    
    # 加权求和
    weights = alpha * transmittance  # [N_rays, N_samples]
    rgb_map = torch.sum(weights[..., None] * rgb, dim=-2)  # [N_rays, 3]
    
    # 处理背景
    if white_bkgd:
        acc_map = torch.sum(weights, dim=-1)  # 累积权重
        rgb_map = rgb_map + (1.0 - acc_map[..., None])
    
    return rgb_map


# ==================== 光线采样 ====================
def get_rays(H, W, focal, c2w):
    """
    生成相机光线
    
    参数:
        H: 图像高度
        W: 图像宽度
        focal: 焦距
        c2w: 相机到世界坐标系的变换矩阵 [3, 4] 或 [4, 4]
    
    返回:
        rays_o: 光线原点 [H, W, 3]
        rays_d: 光线方向 [H, W, 3]
    """
    # 生成像素坐标网格
    i, j = torch.meshgrid(
        torch.arange(W, dtype=torch.float32),
        torch.arange(H, dtype=torch.float32),
        indexing='xy'
    )
    
    # 转换到相机坐标系（中心在图像中心）
    dirs = torch.stack([
        (i - W * 0.5) / focal,
        -(j - H * 0.5) / focal,  # 负号因为图像 y 轴向下
        -torch.ones_like(i)
    ], dim=-1)  # [H, W, 3]
    
    # 转换到世界坐标系
    rays_d = torch.sum(dirs[..., None, :] * c2w[:3, :3], dim=-1)  # [H, W, 3]
    rays_o = c2w[:3, -1].expand(rays_d.shape)  # [H, W, 3]
    
    return rays_o, rays_d


# ==================== 渲染函数 ====================
def render_rays(model, rays_o, rays_d, near=2.0, far=6.0, N_samples=64, device='cpu'):
    """
    渲染一批光线
    
    参数:
        model: NeRF 模型
        rays_o: 光线原点 [N_rays, 3]
        rays_d: 光线方向 [N_rays, 3]
        near: 近平面距离
        far: 远平面距离
        N_samples: 每条光线采样点数
        device: 设备
    
    返回:
        rgb: 渲染的颜色 [N_rays, 3]
    """
    N_rays = rays_o.shape[0]
    
    # 沿光线均匀采样深度值
    z_vals = torch.linspace(near, far, N_samples, device=device)  # [N_samples]
    z_vals = z_vals.expand(N_rays, N_samples)  # [N_rays, N_samples]
    
    # 添加随机扰动（训练时）
    if model.training:
        mids = 0.5 * (z_vals[..., 1:] + z_vals[..., :-1])
        upper = torch.cat([mids, z_vals[..., -1:]], dim=-1)
        lower = torch.cat([z_vals[..., :1], mids], dim=-1)
        z_vals = lower + (upper - lower) * torch.rand_like(z_vals)
    
    # 计算 3D 采样点位置
    pts = rays_o[..., None, :] + rays_d[..., None, :] * z_vals[..., :, None]  # [N_rays, N_samples, 3]
    
    # 展平进行批量推理
    pts_flat = pts.reshape(-1, 3)  # [N_rays * N_samples, 3]
    
    # 准备观察方向
    if model.use_viewdir:
        viewdirs = rays_d / torch.norm(rays_d, dim=-1, keepdim=True)  # 归一化
        viewdirs_flat = viewdirs[:, None, :].expand(pts.shape).reshape(-1, 3)
        rgb_flat, sigma_flat = model(pts_flat, viewdirs_flat)
    else:
        rgb_flat, sigma_flat = model(pts_flat)
    
    # 恢复形状
    rgb = rgb_flat.reshape(N_rays, N_samples, 3)  # [N_rays, N_samples, 3]
    sigma = sigma_flat.reshape(N_rays, N_samples, 1)  # [N_rays, N_samples, 1]
    
    # 体积渲染
    rgb_map = volume_rendering(rgb, sigma, z_vals)
    
    return rgb_map


# ==================== 训练函数 ====================
def train_nerf(model, images, poses, focal, H, W, 
               epochs=1000, batch_size=1024, lr=5e-4, 
               device='cpu', verbose=True):
    """
    训练 NeRF 模型
    
    参数:
        model: NeRF 模型
        images: 训练图像 [N_images, H, W, 3]
        poses: 相机位姿 [N_images, 4, 4]
        focal: 焦距
        H, W: 图像高度和宽度
        epochs: 训练轮数
        batch_size: 每批光线数量
        lr: 学习率
        device: 设备
        verbose: 是否打印训练信息
    
    返回:
        losses: 损失历史
    """
    model.to(device)
    model.train()
    
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # 预计算所有光线
    all_rays_o, all_rays_d, all_rgb = [], [], []
    
    for img, pose in zip(images, poses):
        rays_o, rays_d = get_rays(H, W, focal, pose)
        all_rays_o.append(rays_o.reshape(-1, 3))
        all_rays_d.append(rays_d.reshape(-1, 3))
        all_rgb.append(img.reshape(-1, 3))
    
    all_rays_o = torch.cat(all_rays_o, dim=0).to(device)  # [N_rays_total, 3]
    all_rays_d = torch.cat(all_rays_d, dim=0).to(device)  # [N_rays_total, 3]
    all_rgb = torch.cat(all_rgb, dim=0).to(device)  # [N_rays_total, 3]
    
    N_total = all_rays_o.shape[0]
    
    losses = []
    
    for epoch in range(epochs):
        # 随机采样一批光线
        indices = torch.randint(0, N_total, (batch_size,))
        
        rays_o_batch = all_rays_o[indices]
        rays_d_batch = all_rays_d[indices]
        rgb_batch = all_rgb[indices]
        
        # 渲染
        rgb_pred = render_rays(model, rays_o_batch, rays_d_batch, device=device)
        
        # 计算损失
        loss = F.mse_loss(rgb_pred, rgb_batch)
        
        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        losses.append(loss.item())
        
        # 打印进度
        if verbose and (epoch % 50 == 0 or epoch == epochs - 1):
            print(f"Epoch {epoch}/{epochs}, Loss: {loss.item():.6f}")
    
    return losses


# ==================== 渲染完整图像 ====================
def render_image(model, pose, H, W, focal, device='cpu', chunk=1024):
    """
    渲染完整图像
    
    参数:
        model: NeRF 模型
        pose: 相机位姿 [4, 4]
        H, W: 图像高度和宽度
        focal: 焦距
        device: 设备
        chunk: 批量大小（防止显存不足）
    
    返回:
        img: 渲染的图像 [H, W, 3]
    """
    model.eval()
    model.to(device)
    
    with torch.no_grad():
        # 生成所有光线
        rays_o, rays_d = get_rays(H, W, focal, pose)
        rays_o = rays_o.reshape(-1, 3).to(device)
        rays_d = rays_d.reshape(-1, 3).to(device)
        
        # 分块渲染
        rgb_list = []
        for i in range(0, rays_o.shape[0], chunk):
            rays_o_chunk = rays_o[i:i+chunk]
            rays_d_chunk = rays_d[i:i+chunk]
            rgb_chunk = render_rays(model, rays_o_chunk, rays_d_chunk, device=device)
            rgb_list.append(rgb_chunk.cpu())
        
        # 合并结果
        rgb = torch.cat(rgb_list, dim=0)
        img = rgb.reshape(H, W, 3)
    
    return img


# ==================== 主程序示例 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("Tiny NeRF - 测试模块")
    print("=" * 50)
    
    # 创建模型
    model = TinyNeRF(pos_L=6, dir_L=4, hidden_dim=128, use_viewdir=True)
    print(f"\n✓ 模型创建成功")
    print(f"  - 参数数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 测试前向传播
    batch_size = 1024
    x = torch.rand(batch_size, 3)  # 随机位置
    d = torch.rand(batch_size, 3)  # 随机方向
    
    rgb, sigma = model(x, d)
    print(f"\n✓ 前向传播测试成功")
    print(f"  - 输入形状: {x.shape}")
    print(f"  - RGB 输出: {rgb.shape}, 范围: [{rgb.min():.3f}, {rgb.max():.3f}]")
    print(f"  - Sigma 输出: {sigma.shape}, 范围: [{sigma.min():.3f}, {sigma.max():.3f}]")
    
    # 测试位置编码
    x_test = torch.tensor([[0.5, 0.5, 0.5]])
    x_encoded = positional_encoding(x_test, L=6)
    print(f"\n✓ 位置编码测试成功")
    print(f"  - 原始维度: {x_test.shape[-1]}")
    print(f"  - 编码后维度: {x_encoded.shape[-1]}")
    
    print("\n" + "=" * 50)
    print("所有测试通过！模块运行正常。")
    print("请运行 run_example.py 查看完整示例。")
    print("=" * 50)
