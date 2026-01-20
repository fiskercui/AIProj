# 第八层：游戏引擎集成

## 📋 本层概述

学习如何在实际游戏引擎中集成DLSS SDK，包括Unreal Engine 5和Unity的详细步骤、常见问题与最佳实践。

**学习目标**：
- 掌握DLSS SDK集成流程
- 了解UE5和Unity的具体集成方法
- 学习运动矢量生成最佳实践
- 掌握常见问题排查方法

**预计学习时间**：2.5-3小时

---

## 1. DLSS SDK概述

### 1.1 SDK组件

```
NVIDIA NGX DLSS SDK包含：
├── Include/
│   ├── nvsdk_ngx.h              # 核心API
│   ├── nvsdk_ngx_defs.h         # 定义和常量
│   └── nvsdk_ngx_helpers.h      # 辅助函数
├── Lib/
│   ├── nvsdk_ngx_s.lib          # 静态库
│   └── nvsdk_ngx_d.lib          # 调试版本
├── Binaries/
│   └── nvngx_dlss.dll           # DLSS运行时
└── Documentation/
    └── DLSS_Programming_Guide.pdf
```

### 1.2 Streamline框架

```
NVIDIA Streamline = 统一集成框架

优势：
✅ 单一API支持多种技术（DLSS, Reflex, DLSS-G）
✅ 自动功能检测
✅ 简化集成流程
✅ 跨平台支持
```

---

## 2. 通用集成步骤

### 2.1 初始化流程

```cpp
// Step 1: 初始化NGX
NVSDK_NGX_Result result;
result = NVSDK_NGX_D3D12_Init(
    appId,                // 应用ID（从NVIDIA获取）
    L"./",                // SDK路径
    d3d12Device,          // D3D12设备
    &ngxParameters        // 输出参数
);

// Step 2: 检查DLSS支持
int dlssSupported = 0;
result = ngxParameters->Get(
    NVSDK_NGX_Parameter_SuperSampling_Available,
    &dlssSupported
);

if (!dlssSupported) {
    // 降级到TAA
}

// Step 3: 创建DLSS Feature
NVSDK_NGX_Parameter* dlssCreateParams;
NVSDK_NGX_Handle* dlssFeature;

dlssCreateParams->Set(NVSDK_NGX_Parameter_Width, renderWidth);
dlssCreateParams->Set(NVSDK_NGX_Parameter_Height, renderHeight);
dlssCreateParams->Set(NVSDK_NGX_Parameter_OutWidth, outputWidth);
dlssCreateParams->Set(NVSDK_NGX_Parameter_OutHeight, outputHeight);
dlssCreateParams->Set(NVSDK_NGX_Parameter_DLSS_Hint_Render_Preset_Quality,
                      NVSDK_NGX_DLSS_Hint_Render_Preset_Quality);

result = NGX_D3D12_CREATE_DLSS_EXT(
    commandList,
    1, 1,  // Creation Node Mask, Visibility Node Mask
    &dlssFeature,
    dlssCreateParams
);
```

### 2.2 每帧调用

```cpp
void RenderFrameWithDLSS() {
    // 1. 应用Jitter
    ApplyJitter(projectionMatrix, jitterOffset);
    
    // 2. 渲染场景（低分辨率）
    RenderScene(lowResTarget);
    
    // 3. 生成运动矢量
    GenerateMotionVectors(motionVectorTarget);
    
    // 4. 设置DLSS参数
    NVSDK_NGX_Parameter* evalParams;
    evalParams->Set(NVSDK_NGX_Parameter_Color, colorTexture);
    evalParams->Set(NVSDK_NGX_Parameter_Depth, depthTexture);
    evalParams->Set(NVSDK_NGX_Parameter_MotionVectors, mvTexture);
    evalParams->Set(NVSDK_NGX_Parameter_Jitter_Offset_X, jitterX);
    evalParams->Set(NVSDK_NGX_Parameter_Jitter_Offset_Y, jitterY);
    evalParams->Set(NVSDK_NGX_Parameter_Reset, sceneChanged);
    evalParams->Set(NVSDK_NGX_Parameter_MV_Scale_X, mvScaleX);
    evalParams->Set(NVSDK_NGX_Parameter_MV_Scale_Y, mvScaleY);
    
    // 5. 执行DLSS
    NGX_D3D12_EVALUATE_DLSS_EXT(
        commandList,
        dlssFeature,
        evalParams
    );
    
    // 6. 后处理（高分辨率）
    PostProcess(highResTarget);
}
```

---

## 3. Unreal Engine 5集成

### 3.1 内置DLSS插件

```
UE5已内置DLSS支持：
1. 启用插件
   Edit → Plugins → 搜索"NVIDIA DLSS"
   勾选启用，重启编辑器

2. 项目设置
   Project Settings → Engine → Rendering
   - 勾选"Support DLSS"
   - 设置最小质量等级

3. 使用
   Post Process Volume:
   - Anti-Aliasing Method: None或TAA
   - 开启DLSS选项
   - 选择质量模式
```

### 3.2 自定义集成（C++）

```cpp
// 在GameMode或PlayerController中
void AMyGameMode::EnableDLSS() {
    // 获取DLSS设置
    UDLSSSettings* DLSSSettings = GetMutableDefault<UDLSSSettings>();
    
    // 设置质量模式
    DLSSSettings->DLSSMode = EDLSSMode::Quality;
    
    // 启用帧生成（如果支持）
    if (FDLSSLibrary::IsDLSSGSupported()) {
        DLSSSettings->bEnableDLSSG = true;
    }
    
    // 应用设置
    DLSSSettings->SaveConfig();
}

// 运行时切换
void AMyPlayerController::ToggleDLSSQuality() {
    UDLSSLibrary* DLSSLib = UDLSSLibrary::GetDLSSLibrary();
    
    EDLSSMode CurrentMode = DLSSLib->GetDLSSMode();
    EDLSSMode NewMode;
    
    switch (CurrentMode) {
        case EDLSSMode::Off:
            NewMode = EDLSSMode::Quality;
            break;
        case EDLSSMode::Quality:
            NewMode = EDLSSMode::Balanced;
            break;
        // ... 其他模式
    }
    
    DLSSLib->SetDLSSMode(NewMode);
}
```

### 3.3 运动矢量处理

```
UE5自动生成运动矢量：
- Velocity Pass自动输出
- 支持骨骼动画
- 支持World Position Offset

注意事项：
1. 半透明物体
   Material → Translucency → Output Velocity: True
   
2. 自定义顶点动画
   确保提供Previous Frame Position
   
3. Niagara粒子
   Niagara System → Velocity Module
```

---

## 4. Unity集成

### 4.1 Unity DLSS包

```
安装：
1. Package Manager → Add package from git URL
   com.unity.render-pipelines.universal
   
2. 添加NVIDIA包
   https://github.com/Unity-Technologies/Graphics.git?path=/Packages/com.nvidia.dlss

3. 项目配置
   Project Settings → Quality
   - Anti-Aliasing: None
   - DLSS: Enabled
```

### 4.2 URP集成

```csharp
using UnityEngine.Rendering.Universal;
using UnityEngine.Experimental.Rendering.DLSS;

public class DLSSController : MonoBehaviour {
    void Start() {
        // 检查DLSS支持
        if (DLSSContext.IsDeviceSupported()) {
            // 启用DLSS
            DLSSContext.Create();
            
            // 设置质量模式
            DLSSContext.quality = DLSSQuality.Balanced;
        }
    }
    
    void OnRenderImage(RenderTexture src, RenderTexture dest) {
        // DLSS处理
        if (DLSSContext.isActive) {
            DLSSContext.Execute(commandBuffer, src, dest);
        } else {
            Graphics.Blit(src, dest);
        }
    }
}
```

### 4.3 HDRP集成

```csharp
// HDRP Volume组件
using UnityEngine.Rendering.HighDefinition;

public void SetupDLSSVolume() {
    // 创建Volume
    GameObject volumeGO = new GameObject("DLSS Volume");
    Volume volume = volumeGO.AddComponent<Volume>();
    volume.isGlobal = true;
    
    // 添加DLSS设置
    VolumeProfile profile = volume.profile;
    DLSSSettings dlss;
    
    if (!profile.TryGet(out dlss)) {
        dlss = profile.Add<DLSSSettings>();
    }
    
    // 配置DLSS
    dlss.quality.value = DLSSQualityMode.Balanced;
    dlss.active = true;
}
```

---

## 5. 运动矢量最佳实践

### 5.1 正确生成MV

```cpp
// 顶点着色器示例（HLSL）
struct VSInput {
    float3 position : POSITION;
    float3 prevPosition : PREVPOSITION;  // 关键！
};

struct VSOutput {
    float4 position : SV_POSITION;
    float4 currentPos : CURRENT_POS;
    float4 previousPos : PREVIOUS_POS;
};

VSOutput VS_Main(VSInput input) {
    VSOutput output;
    
    // 当前帧位置
    output.currentPos = mul(float4(input.position, 1), viewProj);
    output.position = output.currentPos;
    
    // 前一帧位置
    output.previousPos = mul(float4(input.prevPosition, 1), prevViewProj);
    
    return output;
}

// 像素着色器
float2 PS_MotionVector(VSOutput input) : SV_TARGET {
    // 透视除法
    float2 currentUV = input.currentPos.xy / input.currentPos.w;
    float2 previousUV = input.previousPos.xy / input.previousPos.w;
    
    // 转换到0-1范围
    currentUV = currentUV * 0.5 + 0.5;
    previousUV = previousUV * 0.5 + 0.5;
    
    // 计算运动矢量
    float2 motionVector = currentUV - previousUV;
    
    return motionVector;
}
```

### 5.2 特殊情况处理

```
1. 骨骼动画
   - 存储前一帧的骨骼变换
   - Skinning时使用前一帧权重

2. 顶点动画（WPO）
   - 在顶点着色器中计算前一帧位置
   - 考虑时间参数

3. 相机剪辑
   - 场景切换时设置Reset标志
   - DLSS将重置历史缓冲

4. 传送/瞬移
   - 检测大幅度位置变化
   - 触发历史重置
```

---

## 6. 常见问题与调试

### 6.1 鬼影（Ghosting）

```
症状：运动物体后有拖影

原因：
1. 运动矢量不正确
2. 历史权重过高
3. 深度不匹配

解决：
✓ 验证运动矢量生成
✓ 检查前一帧位置是否正确存储
✓ 确保深度缓冲格式正确
```

### 6.2 模糊

```
症状：画面整体偏模糊

原因：
1. Jitter未正确应用
2. 输入分辨率过低
3. 锐化参数不当

解决：
✓ 检查投影矩阵Jitter
✓ 尝试更高质量模式
✓ 调整锐化强度
```

### 6.3 闪烁

```
症状：细小物体闪烁

原因：
1. 抗锯齿不足
2. 时序不稳定
3. 透明物体MV缺失

解决：
✓ 确保输入已经过一定AA处理
✓ 检查透明物体MV输出
✓ 使用更高质量模式
```

### 6.4 调试工具

```
NVIDIA Nsight Graphics:
1. 捕获帧
2. 检查DLSS输入
   - 可视化运动矢量（RGB模式）
   - 检查深度范围
   - 验证Jitter应用
3. 分析性能
   - DLSS执行时间
   - Tensor Core使用率
```

---

## 7. 性能优化建议

```
1. 分辨率选择
   4K输出：Quality或Balanced（推荐）
   1440p输出：Quality
   1080p输出：DLAA或不使用

2. 渲染优化
   - 降低基础渲染分辨率
   - 保持后处理在高分辨率

3. 内存管理
   - 及时释放不用的纹理
   - 复用中间缓冲区

4. CPU/GPU平衡
   - 使用Reflex降低延迟
   - 异步资源加载
```

---

## 8. 学习检查点

- [ ] 理解DLSS SDK初始化流程
- [ ] 掌握UE5插件使用方法
- [ ] 了解Unity集成步骤
- [ ] 能够正确生成运动矢量
- [ ] 掌握常见问题调试方法

---

## 下一步

**→ 继续学习 [第九层：性能分析与对比](./09_performance_analysis.md)**

学习如何评估DLSS性能和画质，以及与竞品的对比。

---

**学习进度**：[■■■■■■■■□□] 80% (8/10层完成)
