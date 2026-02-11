# UE5 Memory 模块类参考

> 路径: `Engine/Source/Runtime/Core/Public/Memory/`
>
> 本文档记录该目录下所有头文件中定义的主要类/结构体及其用途。

---

## 目录

- [前向声明](#前向声明)
- [内存视图](#内存视图)
- [共享缓冲区](#共享缓冲区)
- [复合缓冲区](#复合缓冲区)
- [线性分配器](#线性分配器)
- [内存竞技场](#内存竞技场)
- [虚拟栈分配器](#虚拟栈分配器)

---

## 前向声明

### MemoryFwd.h
内存模块的前向声明文件。声明了 `FMemoryView`、`FMutableMemoryView`、`FUniqueBuffer`、`FSharedBuffer`、`FCompositeBuffer` 等核心类型的前向引用，用于减少头文件间的依赖关系。

---

## 内存视图

### MemoryView.h - `FMemoryView` / `FMutableMemoryView`
对一段连续内存的非拥有（non-owning）引用，类似于 `std::span<const std::byte>` / `std::span<std::byte>`。

- **`FMemoryView`** — 只读内存视图。存储指向内存的 `const void*` 指针和字节大小。支持子视图（`Left`/`Mid`/`Right`）、相等比较（`EqualBytes`/`CompareBytes`）、前缀判断等操作。
- **`FMutableMemoryView`** — 可写内存视图。继承自 `FMemoryView`，额外提供 `void*` 的可写访问。支持 `CopyFrom`/`FillZero`/`FillByte` 等写入操作。

两个视图类型均不负责内存的分配和释放，仅提供对已有内存区域的类型安全包装。常用于函数参数中替代 `(void* Data, size_t Size)` 的参数对。

---

## 共享缓冲区

### SharedBuffer.h - `FBufferOwner` / `FUniqueBuffer` / `FSharedBuffer` / `FWeakSharedBuffer`
引擎的核心缓冲区所有权管理系统，提供类似智能指针的缓冲区生命周期管理。

- **`FBufferOwner`** — 缓冲区所有者基类。管理一段内存（`Data` + `Size`）的生命周期，使用原子引用计数（共享计数 + 弱计数，打包在一个 `uint64` 中）控制释放。支持延迟物化（materialization）机制，即缓冲区数据可在首次访问时才真正生成。子类需实现 `FreeBuffer()` 和可选的 `MaterializeBuffer()` 方法。
- **`FUniqueBuffer`** — 独占所有权的可变缓冲区。类似 `std::unique_ptr`，同一时间只有一个引用拥有缓冲区。支持 `Clone()` 深拷贝、`TakeOwnership()` 接管外部内存（带自定义删除函数）。可通过 `MoveToShared()` 转换为共享缓冲区。
- **`FSharedBuffer`** — 共享所有权的不可变缓冲区。类似 `std::shared_ptr<const void>`，多个引用可共享同一缓冲区。支持 `Clone()`/`MakeView()`（在已有缓冲区内创建子视图）/`TakeOwnership()` 等工厂方法。可通过 `MoveToUnique()` 在最后一个引用时转为独占缓冲区（否则克隆）。
- **`FWeakSharedBuffer`** — 弱引用。不延长缓冲区生命周期，通过 `Pin()` 尝试提升为 `FSharedBuffer`。

辅助函数 `MakeUniqueBufferFromArray()` / `MakeSharedBufferFromArray()` 可从 `TArray` 接管内存创建缓冲区。

---

## 复合缓冲区

### CompositeBuffer.h - `FCompositeBuffer`
复合缓冲区，表示由多个 `FSharedBuffer` 段组成的逻辑连续数据。

物理上数据分散在多个独立的共享缓冲区中，但对外提供统一的逻辑视图。支持：
- `GetSize()` — 所有段的总大小
- `GetSegments()` — 获取段数组
- 迭代器遍历各段
- `Mid()`/`Left()`/`Right()` — 逻辑子区间切片
- `ToShared()` — 如果只有一段则直接返回，否则合并为单一 `FSharedBuffer`

适用于网络接收、分块 I/O 等数据天然分段的场景，避免不必要的内存拷贝和合并。

---

## 线性分配器

### LinearAllocator.h - `FLinearAllocator` / `TLinearAllocator<PageSize>`
线性（Bump）分配器。从预分配的内存页中顺序分配，不支持单独释放单个分配，只能一次性释放所有分配。

- **`FLinearAllocator`** — 运行时指定页大小的线性分配器。维护一个页链表，当前页耗尽时分配新页。`Allocate(Size, Alignment)` 从当前页尾部推进指针分配内存。
- **`TLinearAllocator<PageSize>`** — 编译期固定页大小的线性分配器模板。

特点：
- 分配速度极快（仅指针推进 + 对齐计算）
- 不可逐个释放，适用于帧内临时分配、构建器模式等场景
- 支持移动语义和 `Swap` 操作

---

## 内存竞技场

### MemoryArena.h - `FMemoryArena`
内存竞技场（Arena）分配器，是线性分配器的进一步封装。

在大块预分配内存（Arena）中快速分配小块内存，同样不支持单独释放。相比 `FLinearAllocator`，`FMemoryArena` 更侧重于：
- 提供更灵活的策略配置
- 支持对齐控制
- 适用于高频小对象分配场景（如语法树节点、临时计算数据等）

---

## 虚拟栈分配器

### VirtualStackAllocator.h - `FVirtualStackAllocator`
虚拟内存栈分配器。利用虚拟内存地址空间预留（reserve）+ 按需提交（commit）的策略模拟栈式内存分配。

- 预留大块虚拟地址空间（不消耗物理内存）
- 按需提交物理页面，随着分配增长
- 释放时解提交物理页面，但保留虚拟地址
- 类似栈的 LIFO 分配/释放模式

适用于需要大量临时内存但实际使用量不确定的场景，避免预先分配过多物理内存。

---

## 说明

| 后缀 | 含义 |
|-------|------|
| `.h` | 标准头文件 |

> 本文档由自动分析工具生成，基于 UE5 源码中各头文件的类声明和注释。
