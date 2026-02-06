# Nanite Architecture and Underlying Principles

## Overview

This document provides detailed architectural structure diagrams, timing diagrams, and the underlying principles behind Unreal Engine 5's Nanite virtualized geometry system. It serves as a complement to the existing documentation by focusing on the theoretical foundations and complete system architecture.

## Table of Contents

1. [Complete System Architecture](#complete-system-architecture)
2. [Build-Time Pipeline Architecture](#build-time-pipeline-architecture)
3. [Runtime Pipeline Architecture](#runtime-pipeline-architecture)
4. [Frame Timing Diagrams](#frame-timing-diagrams)
5. [Underlying Principles](#underlying-principles)
6. [Mathematical Foundations](#mathematical-foundations)
7. [References](#references)

---

## Complete System Architecture

### High-Level System Overview

```mermaid
flowchart TB
    subgraph BuildTime[Build-Time Processing]
        direction TB
        SourceMesh[Source Mesh<br/>High-poly geometry]
        
        subgraph Clustering[Clustering Stage]
            GraphPart[Graph Partitioning]
            ClusterGen[Cluster Generation<br/>128 triangles each]
            AdjBuild[Adjacency Building]
        end
        
        subgraph DAGConstruction[DAG Construction]
            GroupForm[Group Formation]
            Simplify[Mesh Simplification]
            ParentCreate[Parent LOD Creation]
            BVHBuild[BVH Hierarchy Build]
        end
        
        subgraph Encoding[Encoding Stage]
            PageOrg[Page Organization]
            DataCompress[Data Compression]
            StreamPrep[Streaming Preparation]
        end
        
        NaniteResource[FResources<br/>Nanite Asset]
    end
    
    subgraph Runtime[Runtime System]
        direction TB
        
        subgraph CPUSide[CPU-Side Processing]
            SceneProxy[FNaniteSceneProxy]
            StreamMgr[Streaming Manager]
            ViewSetup[View Setup]
        end
        
        subgraph GPUSide[GPU-Side Processing]
            subgraph Culling[Culling Pipeline]
                InstCull[Instance Culling]
                HierTraverse[Hierarchy Traversal]
                NodeCull[Node Culling]
                ClusterCull[Cluster Culling]
                OccCull[Occlusion Culling]
            end
            
            subgraph Rasterization[Rasterization Pipeline]
                SWHWBinning[SW/HW Binning]
                SWRaster[Software Rasterization<br/>Small Triangles]
                HWRaster[Hardware Rasterization<br/>Large Triangles]
            end
            
            subgraph Output[Output Generation]
                VisBuffer[Visibility Buffer 64-bit]
                DepthBuffer[Depth Buffer]
                MaterialEval[Material Evaluation]
                GBuffer[GBuffer Output]
            end
        end
    end
    
    SourceMesh --> Clustering
    Clustering --> DAGConstruction
    DAGConstruction --> Encoding
    Encoding --> NaniteResource
    NaniteResource --> CPUSide
    CPUSide --> GPUSide
```

### Module Dependency Graph

```mermaid
flowchart LR
    subgraph BuildModules[Build-Time Modules]
        NaniteBuilder[NaniteBuilder<br/>Developer Module]
    end
    
    subgraph RuntimeModules[Runtime Modules]
        EngineModule[Engine Module<br/>NaniteResources.h<br/>NaniteStreamingManager.h]
        RenderCore[RenderCore<br/>Platform Support]
        Renderer[Renderer Module<br/>Nanite Rendering]
    end
    
    subgraph Shaders[GPU Shaders]
        CullingShaders[Culling Shaders<br/>NaniteHierarchyTraversal.ush<br/>NaniteClusterCulling.usf]
        RasterShaders[Raster Shaders<br/>NaniteRasterizer.ush]
        MaterialShaders[Material Shaders<br/>NaniteShading]
    end
    
    NaniteBuilder --> EngineModule
    EngineModule --> RenderCore
    RenderCore --> Renderer
    Renderer --> CullingShaders
    Renderer --> RasterShaders
    Renderer --> MaterialShaders
```

---

## Build-Time Pipeline Architecture

### Cluster DAG Construction

```mermaid
flowchart TB
    subgraph Input[Input Mesh]
        Vertices[Vertices Array]
        Indices[Index Buffer]
        Materials[Material Slots]
    end
    
    subgraph Level0[LOD Level 0 - Full Detail]
        Part0[Graph Partitioning]
        Clusters0[128-Triangle Clusters]
        Adj0[Build Adjacency]
    end
    
    subgraph Level1[LOD Level 1]
        Group1[Group 8-32 Clusters]
        Simplify1[Simplify to 50%]
        Clusters1[Parent Clusters]
    end
    
    subgraph Level2[LOD Level 2]
        Group2[Group Parent Clusters]
        Simplify2[Simplify to 25%]
        Clusters2[Grandparent Clusters]
    end
    
    subgraph LevelN[LOD Level N - Root]
        Root[Root Cluster<br/>Coarsest LOD]
    end
    
    Input --> Level0
    Level0 --> Level1
    Level1 --> Level2
    Level2 -.->|Repeat| LevelN
    
    subgraph DAGStructure[Final DAG Structure]
        direction TB
        DAGRoot[Root Node]
        DAGMid1[Intermediate Nodes]
        DAGMid2[Intermediate Nodes]
        DAGLeaves[Leaf Clusters]
        
        DAGRoot --> DAGMid1
        DAGMid1 --> DAGMid2
        DAGMid2 --> DAGLeaves
    end
```

### Page Organization

```mermaid
flowchart TB
    subgraph Hierarchy[BVH Hierarchy]
        HierNodes[Hierarchy Nodes<br/>FPackedHierarchyNode]
    end
    
    subgraph PageLayout[Page Layout]
        RootPages[Root Pages<br/>Always Resident<br/>Coarsest LOD]
        StreamPages[Streaming Pages<br/>On-Demand Loading<br/>Fine Detail]
        
        RootPages --> StreamPages
    end
    
    subgraph PageContent[Page Content]
        ClusterData[Cluster Data<br/>Geometry + Attributes]
        IndexData[Compressed Indices]
        VertexData[Quantized Positions]
        MaterialInfo[Material References]
    end
    
    Hierarchy --> PageLayout
    PageLayout --> PageContent
```

---

## Runtime Pipeline Architecture

### GPU Culling Pipeline

```mermaid
flowchart TB
    subgraph InputStage[Input Stage]
        GPUScene[GPU Scene Buffer]
        PrevHZB[Previous Frame HZB]
        ViewData[Packed View Data]
    end
    
    subgraph PersistentThreads[Persistent Thread Architecture]
        direction TB
        
        subgraph NodeQueue[Node Queue - MPMC]
            NodeWrite[Node Write Offset]
            NodeRead[Node Read Offset]
            NodeCount[Active Node Count]
        end
        
        subgraph ClusterQueue[Cluster Queue - MPMC]
            ClusterWrite[Cluster Write Offset]
            ClusterRead[Cluster Read Offset]
            ClusterBatches[Cluster Batch Ready Counts]
        end
        
        Workers[Persistent Worker Threads<br/>Process Nodes Priority<br/>Process Clusters When Idle]
    end
    
    subgraph CullingStages[Culling Stages]
        FrustumCull[Frustum Culling<br/>AABB Test]
        LODSelect[LOD Selection<br/>Screen-Space Error]
        OcclusionCull[Occlusion Culling<br/>HZB Test]
        BackfaceCull[Backface Culling]
    end
    
    subgraph Output[Output Lists]
        SWList[Software Raster List<br/>Small Triangles]
        HWList[Hardware Raster List<br/>Large Triangles]
    end
    
    InputStage --> PersistentThreads
    PersistentThreads --> CullingStages
    CullingStages --> Output
```

### Hybrid Rasterization

```mermaid
flowchart TB
    subgraph Classification[Triangle Classification]
        VisibleClusters[Visible Clusters]
        SizeCalc[Calculate Screen Size]
        
        SmallTri[Small Triangles<br/>Less than ~32 pixels]
        LargeTri[Large Triangles<br/>More than ~32 pixels]
    end
    
    subgraph SoftwareRaster[Software Rasterization Path]
        TileSetup[Triangle Setup<br/>Half-Edge Equations]
        
        subgraph RasterMethods[Rasterization Methods]
            ScanlineRaster[Scanline Rasterization<br/>Wide Triangles]
            RectRaster[Rect Iteration<br/>Small Triangles]
            AdaptiveRaster[Adaptive Selection<br/>Based on Width]
        end
        
        AtomicWrite[Atomic Depth Compare<br/>64-bit Visibility Write]
    end
    
    subgraph HardwareRaster[Hardware Rasterization Path]
        VSStage[Vertex Shader<br/>Transform Positions]
        HWRast[Fixed-Function Rasterizer]
        PSStage[Pixel Shader<br/>Write Visibility ID]
    end
    
    subgraph OutputMerge[Output Merge]
        VisBuffer64[Visibility Buffer 64-bit<br/>Depth + ClusterID + TriID]
        DepthOut[Depth Buffer]
    end
    
    VisibleClusters --> SizeCalc
    SizeCalc --> SmallTri
    SizeCalc --> LargeTri
    
    SmallTri --> SoftwareRaster
    LargeTri --> HardwareRaster
    
    SoftwareRaster --> OutputMerge
    HardwareRaster --> OutputMerge
```

---

## Frame Timing Diagrams

### Single Frame Rendering Sequence

```mermaid
sequenceDiagram
    participant CPU as CPU Thread
    participant RT as Render Thread
    participant GPU as GPU
    participant SM as Streaming Manager
    
    Note over CPU,SM: Frame N Begin
    
    CPU->>RT: Submit Scene Updates
    RT->>GPU: Upload Instance Data
    
    rect rgb(200, 220, 255)
        Note over GPU: Main Rendering Pass
        GPU->>GPU: Pack Views FPackedView
        GPU->>GPU: Instance Culling
        
        rect rgb(180, 200, 240)
            Note over GPU: Persistent Thread Culling
            GPU->>GPU: Initialize Node Queue with Roots
            loop Until Queues Empty
                GPU->>GPU: Process Nodes - Priority
                GPU->>GPU: Frustum + LOD Culling
                GPU->>GPU: Add Children to Queue
                GPU->>GPU: Process Clusters - When Idle
            end
        end
        
        GPU->>GPU: Two-Pass Occlusion
        GPU->>GPU: Build Initial HZB
        GPU->>GPU: Test Occluded Candidates
    end
    
    rect rgb(220, 255, 220)
        Note over GPU: Rasterization Pass
        GPU->>GPU: Bin Clusters SW/HW
        par Software Raster
            GPU->>GPU: Compute Shader Rasterization
        and Hardware Raster
            GPU->>GPU: VS/PS Rasterization
        end
        GPU->>GPU: Write Visibility Buffer
    end
    
    rect rgb(255, 220, 220)
        Note over GPU: Material Pass
        GPU->>GPU: Read Visibility Buffer
        GPU->>GPU: Decode Attributes
        GPU->>GPU: Evaluate Materials
        GPU->>GPU: Write GBuffer
    end
    
    GPU->>SM: Streaming Feedback Buffer
    SM->>SM: Process Page Requests
    SM->>GPU: Upload New Pages Next Frame
    
    Note over CPU,SM: Frame N End
```

### Streaming System Timing

```mermaid
sequenceDiagram
    participant GPU as GPU Rendering
    participant FB as Feedback Buffer
    participant CPU as CPU Processing
    participant IO as IO System
    participant Cache as Page Cache
    
    Note over GPU,Cache: Continuous Streaming Loop
    
    GPU->>FB: Write Page Requests<br/>FStreamingRequest
    FB->>CPU: Readback Previous Frame
    
    CPU->>CPU: Parse Requests
    CPU->>CPU: Calculate Priorities
    CPU->>CPU: Add Parent Dependencies
    
    CPU->>IO: Issue Async IO Requests
    IO->>IO: Load from Disk/DDC
    IO->>Cache: Decompress Pages
    
    Cache->>CPU: Mark Pages Ready
    CPU->>GPU: Upload to GPU Memory
    
    GPU->>GPU: Update Page Table
    GPU->>GPU: Apply Fixups
    
    Note over GPU,Cache: LRU Eviction When Full
    Cache->>Cache: Identify Least Used
    Cache->>CPU: Mark for Eviction
    CPU->>GPU: Update Page Table
```

### Two-Pass Occlusion Culling

```mermaid
sequenceDiagram
    participant Main as Main Pass
    participant HZB as HZB Buffer
    participant Post as Post Pass
    participant Raster as Rasterization
    
    Note over Main,Raster: Two-Pass Occlusion Strategy
    
    Main->>Main: Load Previous Frame Visibility
    Main->>Main: Cull with Previous HZB
    Main->>Raster: Render Known Visible
    Raster->>HZB: Build New HZB
    
    Post->>HZB: Read Updated HZB
    Post->>Post: Test Occluded Candidates
    Post->>Raster: Render Newly Visible
    
    Note over Main,Raster: Minimizes Overdraw
```

---

## Underlying Principles

### 1. Virtualized Geometry Principle

The fundamental principle behind Nanite is treating geometry similar to virtual texturing:

```
Traditional Rendering:
- All mesh LODs loaded into memory
- CPU selects discrete LOD level
- Entire mesh rendered at selected LOD

Nanite Virtualized Geometry:
- Only visible geometry regions loaded
- GPU selects continuous LOD per-cluster
- Fine-grained streaming based on visibility
```

**Key Insight**: Just as virtual texturing streams texture pages based on screen coverage, Nanite streams geometry pages based on visibility and screen-space error.

### 2. Cluster-Based Architecture Principle

```mermaid
flowchart LR
    subgraph Traditional[Traditional LOD]
        Mesh0[Full Mesh LOD0]
        Mesh1[Full Mesh LOD1]
        Mesh2[Full Mesh LOD2]
        Mesh0 -.->|Switch| Mesh1
        Mesh1 -.->|Switch| Mesh2
    end
    
    subgraph Nanite[Nanite Clusters]
        C1[Cluster 1]
        C2[Cluster 2]
        C3[Cluster 3]
        C4[Cluster 4]
        
        C1 --> P1[Parent 1-2]
        C2 --> P1
        C3 --> P2[Parent 3-4]
        C4 --> P2
        
        P1 --> Root[Root]
        P2 --> Root
    end
```

**Principle**: Decomposing meshes into small clusters enables:
- Independent LOD selection per cluster
- Fine-grained streaming
- Efficient GPU culling
- Smooth LOD transitions without popping

### 3. GPU-Driven Rendering Principle

```
CPU-Driven (Traditional):
1. CPU traverses scene graph
2. CPU performs culling
3. CPU issues draw calls
4. GPU executes draws

GPU-Driven (Nanite):
1. CPU uploads scene data once
2. GPU performs all culling
3. GPU determines what to render
4. GPU rasterizes directly
```

**Benefits**:
- Eliminates CPU bottleneck
- Scales with GPU parallelism
- Handles millions of instances
- No draw call overhead

### 4. Persistent Thread Architecture

The persistent thread model solves the problem of dynamic work distribution on GPUs:

```cpp
// Traditional GPU Model
// Fixed number of threads mapped to fixed work
// Cannot dynamically spawn new threads

// Persistent Thread Model
// Fixed pool of worker threads
// Threads continuously consume from work queues
// Work items can add new items to queues
```

**Key Algorithm** from [`NaniteHierarchyTraversal.ush`](../Engine/Shaders/Private/Nanite/NaniteHierarchyTraversal.ush#L251):

```
while (queues not empty):
    if (node queue has work):
        process nodes (high priority)
        add visible children to node queue
        add leaf clusters to cluster queue
    else:
        process clusters (fill GPU while waiting)
```

### 5. Hybrid Rasterization Principle

```mermaid
flowchart TB
    subgraph TriangleSizes[Triangle Size Distribution]
        Large[Large Triangles<br/>Efficient in HW]
        Medium[Medium Triangles<br/>OK in both]
        Small[Small Triangles<br/>Efficient in SW]
    end
    
    subgraph HWLimitations[Hardware Rasterizer Limitations]
        FixedCost[Fixed Per-Triangle Cost]
        QuadOverdraw[Quad-Based Overdraw]
        SetupOverhead[Setup Overhead]
    end
    
    subgraph SWAdvantages[Software Rasterizer Advantages]
        NoQuadOverdraw[No Quad Overdraw]
        AtomicDepth[Atomic Depth Test]
        ComputeScale[Scales with Compute]
    end
    
    Large --> HWLimitations
    Small --> SWAdvantages
```

**Principle**: Hardware rasterizers have fixed per-triangle overhead that dominates for small triangles. Software rasterization using compute shaders can be more efficient for sub-pixel or few-pixel triangles.

---

## Mathematical Foundations

### 1. LOD Error Metric

The LOD selection is based on screen-space error:

```
ScreenError = ObjectSpaceError × ProjectedScale

Where:
- ObjectSpaceError = Simplification error from mesh reduction
- ProjectedScale = ObjectSize / Distance × ScreenWidth / FOV

Selection Rule:
- If ScreenError < MaxPixelsPerEdge: Use this LOD
- Else: Traverse to children for finer LOD
```

### 2. Software Rasterization Mathematics

From [`NaniteRasterizer.ush`](../Engine/Shaders/Private/Nanite/NaniteRasterizer.ush#L5):

**Half-Edge Function**:
```
Edge(P) = (V1 - V0) × (P - V0)
       = Edge.x × (P.y - V0.y) - Edge.y × (P.x - V0.x)

Point P is inside triangle if:
Edge01(P) ≥ 0 AND Edge12(P) ≥ 0 AND Edge20(P) ≥ 0
```

**Barycentric Coordinates**:
```
λ0 = Edge12(P) / (Edge01(P) + Edge12(P) + Edge20(P))
λ1 = Edge20(P) / (Edge01(P) + Edge12(P) + Edge20(P))
λ2 = Edge01(P) / (Edge01(P) + Edge12(P) + Edge20(P))

Attribute interpolation:
Attr(P) = λ0 × Attr0 + λ1 × Attr1 + λ2 × Attr2
```

**Depth Interpolation**:
```
Depth(P) = Z0 + (Z1 - Z0) × λ1 + (Z2 - Z0) × λ2
```

### 3. Cluster Grouping for Simplification

The DAG construction uses graph partitioning based on:

```
Cost(Cluster1, Cluster2) = SharedEdges / (Perimeter1 + Perimeter2)

Goal: Maximize internal edges, minimize boundary edges
This enables efficient simplification with minimal seams
```

### 4. BVH Node Structure

From [`NaniteResources.h`](../Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h#L50):

```
Node contains up to NANITE_MAX_BVH_NODE_FANOUT children

For each child:
- LODBounds: Sphere for LOD selection
- BoxBounds: AABB for frustum culling
- MinLODError: Minimum error in subtree
- MaxParentLODError: Maximum error at parent level
- ChildStartReference: Index to children or cluster group
```

### 5. Visibility Buffer Format

```
64-bit Visibility Buffer Layout:
┌─────────────────────────────────────────────────────────────────┐
│ Bits 63-32: Depth (32-bit float)                                │
├─────────────────────────────────────────────────────────────────┤
│ Bits 31-7: Visible Cluster Index (25 bits)                      │
├─────────────────────────────────────────────────────────────────┤
│ Bits 6-0: Triangle Index (7 bits, max 128 per cluster)          │
└─────────────────────────────────────────────────────────────────┘
```

### 6. Streaming Priority Calculation

```
Priority = (PriorityCategory << 30) | (ScreenCoverage >> 2)

Where:
- PriorityCategory: 0-3 based on view importance
- ScreenCoverage: Estimated pixel coverage

Higher priority = Load first
LRU eviction when cache full
```

---

## References

### Academic Papers

1. **Cluster-Based Rendering**
   - Burley, B., & Lacewell, D. (2008). "Ptex: Per-Face Texture Mapping for Production Rendering"
   - Foundation for understanding cluster/page-based data organization

2. **GPU-Driven Rendering**
   - Wihlidal, G. (2015). "Optimizing the Graphics Pipeline with Compute"
   - GDC presentation on GPU-driven rendering techniques

3. **Software Rasterization**
   - Pineda, J. (1988). "A Parallel Algorithm for Polygon Rasterization"
   - Original half-edge rasterization algorithm used in Nanite

4. **Virtual Texturing**
   - Waveren, J. M. P. van (2009). "id Tech 5 Challenges: From Texture Virtualization to Massive Parallelization"
   - Conceptual foundation for virtualized geometry

5. **Mesh Simplification**
   - Garland, M., & Heckbert, P. S. (1997). "Surface Simplification Using Quadric Error Metrics"
   - Basis for LOD generation algorithms

6. **Hierarchical Occlusion Culling**
   - Greene, N., Kass, M., & Miller, G. (1993). "Hierarchical Z-Buffer Visibility"
   - Foundation for HZB-based occlusion culling

### Epic Games Resources

1. **GDC 2021: Nanite Deep Dive**
   - Karis, B., & Wihlidal, G. (2021)
   - Official presentation on Nanite architecture

2. **Unreal Engine Documentation**
   - [Nanite Virtualized Geometry](https://docs.unrealengine.com/5.0/en-US/nanite-virtualized-geometry-in-unreal-engine/)

3. **Unreal Engine Source Code**
   - [`Engine/Source/Runtime/Renderer/Private/Nanite/`](../Engine/Source/Runtime/Renderer/Private/Nanite/)
   - [`Engine/Shaders/Private/Nanite/`](../Engine/Shaders/Private/Nanite/)
   - [`Engine/Source/Developer/NaniteBuilder/`](../Engine/Source/Developer/NaniteBuilder/)

### Related Technologies

1. **Virtual Shadow Maps**
   - Closely integrated with Nanite for efficient shadow rendering
   - Uses same visibility buffer and culling infrastructure

2. **Lumen Global Illumination**
   - Uses Nanite for surface cache capture
   - Leverages Nanite's efficient geometry representation

3. **World Partition**
   - Streaming system works alongside Nanite page streaming
   - Level streaming integrated with geometry streaming

---

## Related Documents

- [01_Overview.md](01_Overview.md) - High-level introduction
- [02_DataStructures.md](02_DataStructures.md) - Detailed data structure documentation
- [03_RenderingPipeline.md](03_RenderingPipeline.md) - Rendering pipeline details
- [04_StreamingSystem.md](04_StreamingSystem.md) - Streaming system documentation
- [05_MaterialsAndShading.md](05_MaterialsAndShading.md) - Material handling
- [plans/nanite-deep-dive.md](plans/nanite-deep-dive.md) - Source code deep dive
