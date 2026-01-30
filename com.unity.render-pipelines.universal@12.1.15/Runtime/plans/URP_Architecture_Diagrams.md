# URP架构图表总结

## 核心类图

```mermaid
classDiagram
    class RenderPipeline {
        <<abstract>>
        +Render(context, cameras)
    }
    
    class UniversalRenderPipeline {
        -UniversalRenderPipelineAsset asset
        -ScriptableRenderer[] renderers
        +Render(context, cameras)
        +RenderSingleCamera()
        +RenderCameraStack()
    }
    
    class ScriptableRenderer {
        <<abstract>>
        -List~ScriptableRenderPass~ activeRenderPassQueue
        -List~ScriptableRendererFeature~ rendererFeatures
        +Setup(context, renderingData)
        +Execute(context, renderingData)
        +EnqueuePass(pass)
    }
    
    class UniversalRenderer {
        -RenderingMode renderingMode
        -ForwardLights forwardLights
        -DeferredLights deferredLights
        -PostProcessPasses postProcessPasses
        +Setup(context, renderingData)
        +SetupLights(context, renderingData)
    }
    
    class ScriptableRenderPass {
        <<abstract>>
        +RenderPassEvent renderPassEvent
        +Configure(cmd, descriptor)
        +Execute(context, renderingData)
        +OnCameraSetup(cmd, renderingData)
    }
    
    class ScriptableRendererFeature {
        <<abstract>>
        +Create()
        +AddRenderPasses(renderer, renderingData)
    }
    
    RenderPipeline <|-- UniversalRenderPipeline
    ScriptableRenderer <|-- UniversalRenderer
    UniversalRenderPipeline o-- ScriptableRenderer
    ScriptableRenderer o-- ScriptableRenderPass
    ScriptableRenderer o-- ScriptableRendererFeature
    ScriptableRendererFeature ..> ScriptableRenderPass : creates
```

## 渲染流程时序图

```mermaid
sequenceDiagram
    participant App as Application
    participant URP as UniversalRenderPipeline
    participant Renderer as ScriptableRenderer
    participant Pass as ScriptableRenderPass
    
    App->>URP: Render(context, cameras)
    
    URP->>URP: SetupPerFrameShaderConstants()
    URP->>URP: SortCameras()
    
    loop For each camera
        URP->>URP: InitializeCameraData()
        URP->>URP: Cull(cullingParameters)
        URP->>URP: InitializeRenderingData()
        
        URP->>Renderer: Setup(context, renderingData)
        activate Renderer
        Renderer->>Renderer: AddRenderPasses()
        Renderer->>Renderer: SortRenderPasses()
        deactivate Renderer
        
        URP->>Renderer: Execute(context, renderingData)
        activate Renderer
        
        Renderer->>Renderer: SetupLights()
        Renderer->>Renderer: SetupCameraProperties()
        
        loop For each Pass in queue
            Renderer->>Pass: Configure(cmd, descriptor)
            Renderer->>Pass: Execute(context, renderingData)
            activate Pass
            Pass->>Pass: Render objects
            deactivate Pass
        end
        
        deactivate Renderer
        
        URP->>URP: Submit()
    end
```

## Forward渲染路径流程

```mermaid
graph TD
    A[Start Rendering] --> B[Shadow Passes]
    B --> B1[MainLightShadowCasterPass]
    B --> B2[AdditionalLightsShadowCasterPass]
    
    B1 --> C{Depth Prepass?}
    B2 --> C
    
    C -->|Yes| D1[DepthOnlyPass]
    C -->|No| E[Opaque Rendering]
    D1 --> E
    
    E --> E1[DrawOpaqueObjects<br/>UniversalForward Pass]
    E1 --> F[DrawSkybox]
    
    F --> G{Copy Depth?}
    G -->|Yes| H[CopyDepthPass]
    G -->|No| I
    H --> I{Copy Color?}
    
    I -->|Yes| J[CopyColorPass]
    I -->|No| K[Transparent Rendering]
    J --> K
    
    K --> K1[DrawTransparentObjects<br/>UniversalForward Pass]
    K1 --> L[PostProcessing]
    
    L --> L1[ColorGradingLutPass]
    L1 --> L2[PostProcessPass]
    L2 --> L3[FinalPostProcessPass]
    
    L3 --> M[FinalBlitPass]
    M --> N[End Rendering]
    
    style E1 fill:#90EE90
    style K1 fill:#87CEEB
    style L2 fill:#FFB6C1
```

## Deferred渲染路径流程

```mermaid
graph TD
    A[Start Rendering] --> B[Shadow Passes]
    B --> B1[MainLightShadowCasterPass]
    B --> B2[AdditionalLightsShadowCasterPass]
    
    B1 --> C[GBuffer Pass]
    B2 --> C
    
    C --> C1[GBufferPass<br/>Write GBuffer RTs]
    C1 --> D[GBufferCopyDepthPass]
    
    D --> E{Tiled Lighting?}
    E -->|Yes| F1[TileDepthRangePass]
    E -->|No| G[Deferred Lighting]
    F1 --> G
    
    G --> G1[DeferredPass<br/>Read GBuffer<br/>Calculate Lighting]
    
    G1 --> H[Forward Only Pass]
    H --> H1[DrawOpaqueForwardOnlyPass<br/>UniversalForwardOnly Pass]
    
    H1 --> I[DrawSkybox]
    I --> J[Transparent Rendering]
    
    J --> J1[DrawTransparentObjects<br/>UniversalForward Pass]
    J1 --> K[PostProcessing]
    
    K --> K1[ColorGradingLutPass]
    K1 --> K2[PostProcessPass]
    K2 --> K3[FinalPostProcessPass]
    
    K3 --> L[FinalBlitPass]
    L --> M[End Rendering]
    
    style C1 fill:#FFD700
    style G1 fill:#FF8C00
    style H1 fill:#90EE90
    style J1 fill:#87CEEB
    style K2 fill:#FFB6C1
```

## 光照系统架构

```mermaid
graph TD
    A[Light Data] --> B{Rendering Mode?}
    
    B -->|Forward| C[ForwardLights]
    B -->|Deferred| D[DeferredLights]
    
    C --> C1{Light Rendering Mode?}
    C1 -->|PerPixel| C2[Setup Light Buffer<br/>Shader: _ADDITIONAL_LIGHTS]
    C1 -->|PerVertex| C3[Setup Vertex Lights<br/>Shader: _ADDITIONAL_LIGHTS_VERTEX]
    C1 -->|Clustered| C4[Setup Clustered Data<br/>Tile-based culling]
    
    C2 --> E[Main Light Calculation]
    C3 --> E
    C4 --> E
    
    E --> E1[Per-Object Light Culling]
    E1 --> E2[Light Cookie Support]
    E2 --> E3[Shadow Sampling]
    
    D --> D1{Deferred Strategy?}
    D1 -->|Stencil| D2[Stencil Deferred<br/>Light Volume per Light]
    D1 -->|Tiled| D3[Tiled Deferred<br/>Compute Shader based]
    
    D2 --> F[Read GBuffer]
    D3 --> F
    
    F --> F1[Calculate PBR Lighting]
    F1 --> F2[Accumulate to Light Buffer]
    
    style C2 fill:#90EE90
    style C3 fill:#87CEEB
    style C4 fill:#FFD700
    style D2 fill:#FF8C00
    style D3 fill:#FF6347
```

## Pass扩展机制

```mermaid
graph LR
    A[ScriptableRendererFeature] --> B{Create Phase}
    B --> C[Instantiate Custom Pass]
    C --> D[Configure Pass Properties]
    D --> E[Set RenderPassEvent]
    
    E --> F{AddRenderPasses Phase}
    F --> G{Should Add Pass?}
    G -->|Yes| H[renderer.EnqueuePass]
    G -->|No| I[Skip]
    
    H --> J[Pass added to Queue]
    J --> K{Execute Phase}
    K --> L[ScriptableRenderer.Execute]
    L --> M[Sort Pass Queue]
    M --> N[For each Pass]
    N --> O[Pass.Configure]
    O --> P[Pass.Execute]
    P --> Q[Pass.FrameCleanup]
    
    style A fill:#FFD700
    style C fill:#90EE90
    style H fill:#87CEEB
    style P fill:#FFB6C1
```

## 数据流向图

```mermaid
graph TD
    A[UniversalRenderPipelineAsset] --> B[Configuration Data]
    
    B --> C1[Shadow Settings]
    B --> C2[Lighting Settings]
    B --> C3[Post-Processing Settings]
    B --> C4[Quality Settings]
    
    C1 --> D[RenderingData]
    C2 --> D
    C3 --> D
    C4 --> D
    
    E[Camera] --> F[CameraData]
    F --> D
    
    G[Scene Culling] --> H[CullResults]
    H --> D
    
    D --> I[ScriptableRenderer.Setup]
    I --> J[Build Pass Queue]
    
    J --> K[ScriptableRenderer.Execute]
    K --> L[Execute Pass Queue]
    
    L --> M1[Shadow Maps]
    L --> M2[GBuffer / Color Buffer]
    L --> M3[Depth Buffer]
    L --> M4[Light Buffer]
    
    M1 --> N[Post-Processing]
    M2 --> N
    M3 --> N
    M4 --> N
    
    N --> O[Final Frame Buffer]
    
    style D fill:#FFD700
    style J fill:#90EE90
    style L fill:#87CEEB
    style O fill:#FFB6C1
```

## Pass事件时间轴

```
Timeline: RenderPassEvent
│
├─── < 0 ───────────────────────────────────────────────────────
│    BeforeRendering Block
│    ├── BeforeRenderingShadows (-50)
│    │   └── MainLightShadowCasterPass
│    │   └── AdditionalLightsShadowCasterPass
│    └── BeforeRenderingPrePasses (0)
│        └── DepthPrepass / DepthNormalPrepass
│
├─── 0 - 150 ───────────────────────────────────────────────────
│    MainRenderingOpaque Block
│    ├── BeforeRenderingGbuffer (50)
│    │   └── GBufferPass (Deferred)
│    ├── BeforeRenderingDeferredLights (75)
│    │   └── TileDepthRangePass (Deferred)
│    ├── AfterRenderingGbuffer (85)
│    │   └── DeferredPass
│    │   └── DrawOpaqueForwardOnlyPass (Deferred)
│    ├── BeforeRenderingOpaques (100)
│    │   └── DrawOpaqueObjectsPass (Forward)
│    └── AfterRenderingOpaques (150)
│        └── CopyDepthPass
│
├─── 150 - 250 ─────────────────────────────────────────────────
│    MainRenderingTransparent Block
│    ├── BeforeRenderingSkybox (200)
│    │   └── DrawSkyboxPass
│    ├── AfterRenderingSkybox (210)
│    │   └── CopyColorPass (Opaque Texture)
│    ├── BeforeRenderingTransparents (250)
│    │   └── DrawTransparentObjectsPass
│    └── AfterRenderingTransparents (300)
│
├─── > 250 ─────────────────────────────────────────────────────
│    AfterRendering Block
│    ├── BeforeRenderingPostProcessing (400)
│    │   └── ColorGradingLutPass
│    │   └── PostProcessPass
│    ├── AfterRenderingPostProcessing (500)
│    │   └── FinalPostProcessPass (FXAA/FSR)
│    └── AfterRendering (600)
│        └── FinalBlitPass
│        └── CapturePass
└────────────────────────────────────────────────────────────────
```

## GBuffer布局

```
Deferred Rendering GBuffer Layout:
┌────────────────────────────────────────┐
│ RT0: Albedo + MaterialFlags            │
│  - RGB: Base Color (sRGB)              │
│  - A: Material Flags (Unlit/Metallic)  │
├────────────────────────────────────────┤
│ RT1: Specular + Occlusion              │
│  - RGB: Specular Color                 │
│  - A: Occlusion                        │
├────────────────────────────────────────┤
│ RT2: Normal + Smoothness               │
│  - RGB: World Space Normal (Oct or XYZ)│
│  - A: Smoothness                       │
├────────────────────────────────────────┤
│ RT3: Emission + Lightmap               │
│  - RGB: Emission + Baked GI            │
│  - A: Reserved                         │
├────────────────────────────────────────┤
│ Depth Buffer                           │
│  - D32 or D24S8                        │
│  - Camera Depth + Stencil              │
└────────────────────────────────────────┘

Notes:
- RT Format: R8G8B8A8_UNorm or higher
- Normal可选择Oct编码节省带宽
- Stencil用于标记材质类型和光照区域
```

## 关键性能指标

```
Performance Metrics by Rendering Path:

Forward Rendering:
├── Advantages:
│   ├── MSAA support (移动端重要)
│   ├── Lower memory bandwidth
│   ├── Simpler pipeline
│   └── Better for few lights
└── Limitations:
    ├── Light count per object limited (8)
    ├── Multiple shading per pixel
    └── No light accumulation

Deferred Rendering:
├── Advantages:
│   ├── Unlimited light count
│   ├── Single shading per pixel
│   ├── Better for many lights
│   └── Light accumulation
└── Limitations:
    ├── No MSAA (need resolve)
    ├── Higher memory bandwidth
    ├── No transparency in GBuffer
    └── More complex pipeline

Recommended Usage:
├── Mobile: Forward + MSAA
├── PC/Console (Few Lights): Forward
├── PC/Console (Many Lights): Deferred
└── VR/XR: Forward + Native RenderPass
```
