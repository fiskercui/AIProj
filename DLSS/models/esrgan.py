"""
ESRGAN (Enhanced Super-Resolution Generative Adversarial Networks) 模型实现
基于论文: https://arxiv.org/abs/1809.00219
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualDenseBlock(nn.Module):
    """残差密集块 (Residual Dense Block, RDB)"""
    
    def __init__(self, num_features=64, num_grow_channels=32):
        super(ResidualDenseBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(num_features, num_grow_channels, 3, 1, 1)
        self.conv2 = nn.Conv2d(num_features + num_grow_channels, num_grow_channels, 3, 1, 1)
        self.conv3 = nn.Conv2d(num_features + 2 * num_grow_channels, num_grow_channels, 3, 1, 1)
        self.conv4 = nn.Conv2d(num_features + 3 * num_grow_channels, num_grow_channels, 3, 1, 1)
        self.conv5 = nn.Conv2d(num_features + 4 * num_grow_channels, num_features, 3, 1, 1)
        
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)
        
        # 初始化
        self._initialize_weights()
    
    def _initialize_weights(self):
        """权重初始化"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='leaky_relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """前向传播"""
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        
        # 残差缩放
        return x5 * 0.2 + x


class RRDB(nn.Module):
    """残差中的残差密集块 (Residual in Residual Dense Block)"""
    
    def __init__(self, num_features, num_grow_channels=32):
        super(RRDB, self).__init__()
        
        self.rdb1 = ResidualDenseBlock(num_features, num_grow_channels)
        self.rdb2 = ResidualDenseBlock(num_features, num_grow_channels)
        self.rdb3 = ResidualDenseBlock(num_features, num_grow_channels)
    
    def forward(self, x):
        """前向传播"""
        out = self.rdb1(x)
        out = self.rdb2(out)
        out = self.rdb3(out)
        
        # 残差缩放
        return out * 0.2 + x


class RRDBNet(nn.Module):
    """
    RRDB 网络（生成器）
    ESRGAN 的核心网络结构
    """
    
    def __init__(
        self, 
        in_channels=3, 
        out_channels=3, 
        num_features=64,
        num_blocks=23,
        num_grow_channels=32,
        scale=4
    ):
        """
        Args:
            in_channels: 输入通道数
            out_channels: 输出通道数
            num_features: 特征通道数
            num_blocks: RRDB 块数量
            num_grow_channels: 密集块增长通道数
            scale: 上采样倍数 (2, 4, 8)
        """
        super(RRDBNet, self).__init__()
        
        self.scale = scale
        
        # 第一层卷积
        self.conv_first = nn.Conv2d(in_channels, num_features, 3, 1, 1)
        
        # RRDB 块
        self.rrdb_blocks = nn.Sequential(
            *[RRDB(num_features, num_grow_channels) for _ in range(num_blocks)]
        )
        
        # 中间卷积
        self.conv_body = nn.Conv2d(num_features, num_features, 3, 1, 1)
        
        # 上采样层
        self.upsampler = self._make_upsampler(scale, num_features)
        
        # 重建层
        self.conv_hr = nn.Conv2d(num_features, num_features, 3, 1, 1)
        self.conv_last = nn.Conv2d(num_features, out_channels, 3, 1, 1)
        
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)
    
    def _make_upsampler(self, scale, num_features):
        """创建上采样层"""
        layers = []
        
        if scale == 2 or scale == 4 or scale == 8:
            for _ in range(int(torch.log2(torch.tensor(scale)).item())):
                layers.append(nn.Conv2d(num_features, num_features * 4, 3, 1, 1))
                layers.append(nn.PixelShuffle(2))
                layers.append(nn.LeakyReLU(negative_slope=0.2, inplace=True))
        else:
            raise ValueError(f"不支持的缩放倍数: {scale}")
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入低分辨率图像 tensor (B, C, H, W)
        
        Returns:
            输出高分辨率图像 tensor (B, C, H*scale, W*scale)
        """
        # 第一层
        feat = self.conv_first(x)
        
        # RRDB 主体
        body_feat = self.rrdb_blocks(feat)
        body_feat = self.conv_body(body_feat)
        
        # 全局残差连接
        feat = feat + body_feat
        
        # 上采样
        feat = self.upsampler(feat)
        
        # 重建
        out = self.conv_last(self.lrelu(self.conv_hr(feat)))
        
        return out


class ESRGAN(nn.Module):
    """
    ESRGAN 完整模型
    包含生成器（Generator）
    """
    
    def __init__(
        self,
        in_channels=3,
        out_channels=3,
        num_features=64,
        num_blocks=23,
        scale=4
    ):
        """
        Args:
            in_channels: 输入通道数
            out_channels: 输出通道数
            num_features: 特征通道数
            num_blocks: RRDB 块数量
            scale: 上采样倍数
        """
        super(ESRGAN, self).__init__()
        
        self.generator = RRDBNet(
            in_channels=in_channels,
            out_channels=out_channels,
            num_features=num_features,
            num_blocks=num_blocks,
            scale=scale
        )
    
    def forward(self, x):
        """前向传播"""
        return self.generator(x)
    
    def load_pretrained(self, checkpoint_path):
        """加载预训练权重"""
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        if 'model_state_dict' in checkpoint:
            self.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.load_state_dict(checkpoint)
        
        print(f"成功加载预训练模型: {checkpoint_path}")
    
    def count_parameters(self):
        """统计模型参数数量"""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        print(f"总参数数: {total:,}")
        print(f"可训练参数数: {trainable:,}")
        
        return total, trainable


def test_model():
    """测试模型"""
    print("="*50)
    print("测试 ESRGAN 模型")
    print("="*50)
    
    # 创建模型
    model = ESRGAN(scale=4, num_blocks=23)
    model.eval()
    
    # 统计参数
    model.count_parameters()
    
    # 测试前向传播
    with torch.no_grad():
        # 创建随机输入 (batch_size=1, channels=3, height=64, width=64)
        x = torch.randn(1, 3, 64, 64)
        print(f"\n输入形状: {x.shape}")
        
        # 前向传播
        output = model(x)
        print(f"输出形状: {output.shape}")
        
        # 验证输出尺寸
        expected_h = x.shape[2] * 4
        expected_w = x.shape[3] * 4
        assert output.shape[2] == expected_h and output.shape[3] == expected_w
        print(f"\n✓ 模型测试通过！")
        print(f"  输入: {x.shape[2]}x{x.shape[3]}")
        print(f"  输出: {output.shape[2]}x{output.shape[3]}")
        print(f"  放大倍数: 4x")


if __name__ == "__main__":
    test_model()
