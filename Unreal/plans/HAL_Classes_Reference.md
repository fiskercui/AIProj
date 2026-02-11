# UE5 HAL 模块类参考

> 路径: `Engine/Source/Runtime/Core/Public/HAL/`
>
> 本文档记录该目录下所有头文件中定义的主要类/结构体及其用途。

---

## 目录

- [虚拟内存页分配器 (Allocators 子目录)](#虚拟内存页分配器-allocators-子目录)
- [内存分配器 -- 生产级实现](#内存分配器----生产级实现)
- [内存分配器 -- 调试/诊断代理](#内存分配器----调试诊断代理)
- [内存系统核心](#内存系统核心)
- [平台抽象层](#平台抽象层)
- [文件系统](#文件系统)
- [控制台变量/命令系统](#控制台变量命令系统)
- [线程同步原语](#线程同步原语)
- [线程管理](#线程管理)
- [线程安全工具](#线程安全工具)
- [预处理器工具](#预处理器工具)
- [输出设备和异常处理](#输出设备和异常处理)
- [模块基础设施](#模块基础设施)

---

## 虚拟内存页分配器 (Allocators 子目录)

### Allocators/CachedOSPageAllocator.h - `TCachedOSPageAllocator<NumCachedPages>`
模板类，用于缓存已释放的操作系统内存页，避免频繁调用操作系统的内存分配/释放接口。通过维护一个固定大小的缓存池来复用页面，减少系统调用开销。

### Allocators/CachedOSVeryLargePageAllocator.h - `FCachedOSVeryLargePageAllocator`
大页面缓存分配器。专门针对大块内存（超大页面）进行缓存管理，用于减少大块内存的操作系统分配开销。支持 Commit/Decommit 操作来管理物理内存的实际使用。

### Allocators/PooledVirtualMemoryAllocator.h - `FPooledVirtualMemoryAllocator`
池化虚拟内存分配器。将虚拟内存地址空间按池（Pool）方式管理，通过预留虚拟地址空间并按需提交物理内存来优化大量中等大小内存块的分配。

---

## 内存分配器 -- 生产级实现

### MallocAnsi.h - `FMallocAnsi`
基于标准 ANSI C `malloc`/`free`/`realloc` 的内存分配器包装。继承自 `FMalloc`，作为最简单的分配器实现，通常用作后备方案或参考基线。

### MallocBinned.h - `FMallocBinned`
第一代分箱（Binned）内存分配器。将内存分为多个大小类别的"箱"（bin），每个箱管理特定大小范围的分配请求。通过预分配内存池减少碎片和系统调用。

### MallocBinned2.h - `FMallocBinned2`
第二代分箱内存分配器。相比第一代有更好的性能和内存利用率，支持 fork 操作（`OnPreFork`/`OnPostFork`），是多数平台的默认分配器。

### MallocBinned3.h - `FMallocBinned3`
第三代分箱内存分配器。基于虚拟内存技术，使用大块虚拟地址空间预留+按需提交的策略。仅在支持 `PLATFORM_HAS_FPlatformVirtualMemoryBlock` 的64位平台上可用。

### MallocBinnedCommon.h
分箱分配器公共基础设施（池大小表定义、`FBitTree` 位图树等）。为所有分箱分配器（Binned/Binned2/Binned3）提供共享的常量定义、池大小配置和数据结构。

### MallocBinnedCommonUtils.h - `FNoAllocScopeCycleCounter`
分箱分配器的公共工具类。提供不进行内存分配的作用域性能计数器，用于在分配器内部进行性能剖析而不递归触发分配。

### MallocBinnedGPU.h - `FArenaParams`
GPU 专用的分箱内存分配器。`FArenaParams` 定义了 Arena（内存竞技场）的参数配置，包括最大内存大小、对齐要求等，用于 GPU 内存管理场景。

### MallocTBB.h - `FMallocTBB`
基于 Intel TBB（Threading Building Blocks）可扩展内存分配器的包装。利用 TBB 的 `scalable_malloc` 系列函数提供高性能线程安全分配。

### MallocJemalloc.h - `FMallocJemalloc`
基于 jemalloc 的内存分配器包装。jemalloc 以其优秀的多线程性能和低碎片率著称。

### MallocMimalloc.h - `FMallocMimalloc`
基于 mimalloc 的64位可扩展内存分配器。mimalloc 是微软开源的高性能通用分配器，支持零初始化分配（`MallocZeroed`）和 `TryMalloc` 安全分配接口。

### MallocLibpas.h - `FMallocLibpas`
基于 libpas（Phil's Awesome System）的内存分配器包装。libpas 是一个高性能分配器，通过 `PLATFORM_BUILDS_LIBPAS` 宏控制可用性。

---

## 内存分配器 -- 调试/诊断代理

### MallocDebug.h - `FMallocDebug`
调试用内存分配器。在每次分配前后添加标记（pre-tag/post-tag），释放时填充特定模式（`0xfe`），用于检测内存越界写和使用已释放内存等错误。

### MallocStomp.h - `FMallocStomp`
页保护踩踏（Stomp）分配器。通过在分配的内存后（或前，取决于模式）放置不可访问的保护页，使缓冲区溢出立即触发异常。通过 `-stompmalloc` 命令行参数启用。

### MallocStomp2.h - `FMallocStomp2` / `FScopeDisableMallocStomp2`
改进版踩踏分配器（仅限 Windows 编辑器）。预留巨大虚拟地址空间（最高 32TB），释放内存时只解除物理页映射而保留虚拟地址，使释放后访问立即崩溃。`FScopeDisableMallocStomp2` 提供作用域内禁用追踪的能力。比第一版更适合长时间运行的编辑器场景。

### MallocPoisonProxy.h - `FMallocPoisonProxy`
内存毒化代理。包装底层分配器，对新分配的内存填充 `0xcd`，对释放的内存填充 `0xdd`，帮助发现使用未初始化内存或已释放内存的问题。在 Debug/Development 构建中默认启用。

### MallocThreadSafeProxy.h - `FMallocThreadSafeProxy`
线程安全代理分配器。通过临界区（Critical Section）包装非线程安全的底层分配器，使其所有操作变为线程安全。

### MallocReplayProxy.h - `FMallocReplayProxy`
分配回放代理。记录所有内存分配/释放/重分配操作到磁盘文件，用于后续回放测试不同分配器实现的性能和正确性。默认在 Linux 非 Shipping 构建中可用。

### MallocCallstackHandler.h - `FMallocCallstackHandler` / `FScopeDisableMallocCallstackHandler`
调用栈追踪代理分配器基类。为每次分配记录完整调用栈信息，是 `FMallocDoubleFreeFinder` 等诊断工具的基础。`FScopeDisableMallocCallstackHandler` 提供作用域内禁用追踪的能力。

### MallocDoubleFreeFinder.h - `FMallocDoubleFreeFinder`
双重释放检测器。继承自 `FMallocCallstackHandler`，追踪所有分配和释放操作，当检测到对同一指针重复释放时触发断言，并输出两次释放的调用栈信息。

### MallocFrameProfiler.h - `FMallocFrameProfiler`
逐帧内存分配剖析器。继承自 `FMallocCallstackHandler`，记录每帧的分配数量、大小和调用栈，用于分析内存分配模式和优化热点。

### MallocLeakDetection.h - `FMallocLeakDetection` / `FMallocLeakDetectionIgnoreScope` / `FMallocLeakScopedContext`
内存泄漏检测系统。维护所有当前分配指针的列表和唯一调用栈映射，支持按大小/速率过滤，进行线性拟合分析检测持续增长的分配（潜在泄漏）。`FMallocLeakDetectionIgnoreScope` 允许忽略特定代码范围的分配。

### MallocTimer.h - `FScopedVirtualMallocTimer`
虚拟内存操作计时器。用于测量虚拟内存分配/释放操作的耗时，帮助识别内存操作的性能瓶颈。

---

## 内存系统核心

### MemoryBase.h - `FMalloc` / `FUseSystemMallocForNew`
内存分配器的抽象基类。`FMalloc` 定义了 `Malloc`/`Realloc`/`Free`/`GetAllocationSize` 等纯虚接口。`FUseSystemMallocForNew` 是让派生类使用系统 malloc 的 operator new/delete 基类。全局指针 `GMalloc` 指向当前使用的分配器实例。

### Memory.h
根据平台配置选择内联的 GMalloc 实现（Binned2 或 Binned3 或动态），并包含 `FMemory.inl` 内联实现。决定了编译时使用哪种分配器的快速路径。

### UnrealMemory.h - `FMemory`
Unreal 内存操作的核心接口。`FMemory` 提供静态方法：`Malloc`/`Realloc`/`Free`/`MallocZeroed`/`QuantizeSize`/`Trim` 以及 `Memcpy`/`Memmove`/`Memset`/`Memzero`/`Memswap`/`BigBlockMemcpy`/`StreamingMemcpy`/`ParallelMemcpy` 等内存操作函数。也提供 `SystemMalloc`/`SystemFree` 直接调用 C 运行时。

### FMemory.inl
FMemory 核心操作的内联实现。包含 AutoRTFM（自动事务内存）支持逻辑：事务代码中 malloc 在 "open" 模式下调用以避免追踪分配器内部数据结构的写入，realloc 在事务中被转化为 malloc+memcpy+free 以支持回滚，free 延迟到事务提交时执行。

### MemoryMisc.h - `FGenericMemoryStats` / `FScopedMemoryStats` / `FSharedMemoryTracker`
内存统计辅助类。`FGenericMemoryStats` 用于收集通用内存统计数据，`FScopedMemoryStats` 在作用域内追踪内存变化，`FSharedMemoryTracker` 追踪共享内存池的使用情况。

### LowLevelMemTracker.h - `FLowLevelMemTracker` (LLM)
低级内存追踪器。在分配器级别追踪每次内存分配并按标签（Tag）分类，能精确报告引擎各子系统的内存使用量。是引擎内存分析的核心基础设施。

### LowLevelMemTrackerDefines.h
LLM 系统的编译期开关和配置。定义了 `ALLOW_LOW_LEVEL_MEM_TRACKER_IN_TEST`、`LLM_ENABLED_IN_CONFIG` 等宏，控制 LLM 在不同构建配置下的启用状态。

### LowLevelMemStats.h
低级内存统计数据的收集和报告基础设施，与 LLM 配合使用。

### PageCache.h - `FPageCache`
页面提交/解提交缓存。管理虚拟内存页面的 Commit（提交物理内存）和 Decommit（释放物理内存）操作，通过缓存已提交页面来减少操作系统调用频率。

### VirtualAllocator.h - `FVirtualAllocator`
虚拟地址空间分配器。在预留的虚拟地址范围内以2的幂次大小为单位管理虚拟页面的分配和回收。使用空闲链表进行回收，按块大小分组管理。可配置为 malloc 的后端或使用 malloc 管理自身数据结构。

### PlatformMallocCrash.h - `FPlatformMallocCrash`
崩溃安全内存分配器的平台特定 typedef。在崩溃处理期间使用，避免依赖可能已损坏的常规分配器。

---

## 平台抽象层

### Platform.h - `FPlatformTypes`
引擎最核心的平台定义文件。定义了所有基础类型别名（`uint8`/`int32`/`uint64`/`TCHAR`/`SIZE_T` 等）、平台特性宏（如 `PLATFORM_WINDOWS`/`PLATFORM_64BITS`/`PLATFORM_LITTLE_ENDIAN`）、编译器宏、`TEXT()` 宏、对齐宏、DLL 导入导出宏、分支预测提示等。是整个引擎跨平台编译的基石。

### PlatformMemory.h
重定向到平台特定的内存管理接口。通过 `COMPILED_PLATFORM_HEADER` 宏包含平台特定实现（如 `Windows/WindowsPlatformMemory.h`），提供 `FPlatformMemory` 的平台实现（包括 `BinnedAllocFromOS`、`OnOutOfMemory`、虚拟内存块等）。

### PlatformMemoryHelpers.h - `PlatformMemoryHelpers`
平台内存辅助函数。`GetFrameMemoryStats()` 返回当前帧的平台内存统计信息，同一帧内缓存结果以避免重复的高开销平台调用。

### PlatformMisc.h - `FScopedNamedEvent` / `FScopedNamedEventStatic`
平台杂项功能和性能剖析命名事件。包含平台特定的 `FPlatformMisc` 重定向，以及 `SCOPED_NAMED_EVENT` 系列宏用于在外部剖析工具（如 PIX、Instruments）中标记代码区域。

### PlatformAtomics.h
重定向到平台特定的原子操作实现。提供 `InterlockedIncrement`/`InterlockedExchange`/`AtomicRead` 等原子操作接口。

### PlatformCrt.h
统一包含标准 C 运行时头文件（`<new>`、`<wchar.h>`、`<stddef.h>`、`<stdlib.h>`、`<stdio.h>`、`<stdarg.h>`、`<math.h>` 等），确保跨平台一致性。

### PlatformMath.h
重定向到平台特定数学函数（`FPlatformMath`），提供 sin/cos/sqrt/floor/ceil 等基础数学运算的平台优化实现。

### PlatformString.h
重定向到平台特定字符串操作（`FPlatformString`），包含 `Strlen`/`Strcpy`/`Strcmp` 等函数的平台优化版本。

### PlatformTime.h
重定向到平台时间相关功能（`FPlatformTime`），包含 `Seconds()`/`Cycles()`/`Cycles64()` 等高精度计时函数的平台实现。

### PlatformProcess.h - `UE::HAL::FProcess` / `UE::HAL::FPipe`
平台进程管理。除了重定向 `FPlatformProcess` 外，还定义了 RAII 风格的进程和管道封装类：`FPipe` 管理进程间通信管道的生命周期，`FProcess` 封装外部进程的创建、等待、终止等操作。

### PlatformProperties.h
重定向到平台属性（`FPlatformProperties`）定义，包含平台是否支持窗口、触屏、多线程等静态属性查询。

### PlatformStackWalk.h
重定向到平台栈回溯（`FPlatformStackWalk`）接口，提供 `CaptureStackBackTrace`/`StackWalkAndDump` 等函数用于崩溃诊断和调试。

### PlatformTLS.h
重定向到平台线程本地存储（TLS）接口（`FPlatformTLS`），提供 `AllocTlsSlot`/`GetTlsValue`/`SetTlsValue`/`GetCurrentThreadId` 等函数。

### PlatformMutex.h
重定向到平台互斥量的具体实现，提供平台原生互斥量的封装。

### PlatformOutputDevices.h
重定向到平台输出设备（`FPlatformOutputDevices`），用于获取平台特定的日志输出、错误输出设备。

### PlatformCrashContext.h
重定向到崩溃上下文（`FPlatformCrashContext`），提供崩溃时的系统状态信息收集。

### PlatformIncludes.h
集中包含所有平台相关头文件的聚合头文件。

### PlatformNamedPipe.h
Windows 平台特定的命名管道支持，非 Windows 平台为空实现。

### PlatformAffinity.h - `FThreadAffinity`
线程亲和性定义。`FThreadAffinity` 包含 `ThreadAffinityMask`（线程亲和掩码）和 `ProcessorGroup`（处理器组），用于将线程绑定到特定 CPU 核心。

### PlatformFile.h
通过 `COMPILED_PLATFORM_HEADER` 包含平台文件系统接口的具体实现。

---

## 文件系统

### FileManager.h - `IFileManager`
文件管理器抽象接口。定义了文件创建、读写、删除、复制、移动、遍历目录等核心文件操作。是引擎文件 I/O 的统一入口点。

### FileManagerGeneric.h - `FFileManagerGeneric`
`IFileManager` 的通用平台实现。基于 `IPlatformFile` 接口实现文件操作，提供跨平台的文件管理功能。

### PlatformFileManager.h - `FPlatformFileManager`
平台文件管理器单例。管理 `IPlatformFile` 的包装链（wrapper chain），允许在底层平台文件系统上叠加缓存、日志、加密等层。

### PlatformFileCommon.h - `FFileHandleRegistry`
平台文件句柄注册和管理。`FFileHandleRegistry` 管理有限的操作系统文件句柄资源，当句柄超出限制时自动关闭和重新打开文件，对上层透明。`FFileHandleRegistryReadTracker` 追踪读取操作的统计。

### IPlatformFileCachedWrapper.h
`IPlatformFile` 的缓存层包装。在底层文件系统之上添加读取缓存，减少对底层存储的直接访问次数。

### IPlatformFileLogWrapper.h
`IPlatformFile` 的日志层包装。记录所有文件操作（打开/关闭/读/写）的日志，用于调试和性能分析。

### IPlatformFileManagedStorageWrapper.h
`IPlatformFile` 的托管存储层包装。用于管理受限存储空间（如主机平台的本地存储配额），监控和限制存储使用。

### IPlatformFileModule.h - `IPlatformFileModule`
平台文件模块接口。定义了 `GetPlatformFile()` 方法，允许通过模块系统加载自定义文件系统实现（如 Pak 文件系统）。

### IPlatformFileOpenLogWrapper.h
`IPlatformFile` 的文件打开日志层。专门记录文件打开操作，用于追踪文件访问模式和优化加载顺序。

### DiskUtilizationTracker.h - `FDiskUtilizationTracker`
磁盘 I/O 利用率追踪器。监控磁盘读写操作的频率和耗时，用于识别 I/O 瓶颈和优化磁盘访问模式。

---

## 控制台变量/命令系统

### IConsoleManager.h - `IConsoleManager` / `IConsoleVariable` / `IConsoleCommand` / `FAutoConsoleVariable`
引擎控制台系统的核心接口。`IConsoleManager` 是控制台变量/命令注册和查找的中央管理器。`IConsoleVariable` 表示可在运行时修改的配置变量（支持 int/float/string/bool 类型），`IConsoleCommand` 表示可执行的控制台命令。`FAutoConsoleVariable` 系列提供自动注册的便捷包装。支持变量变更回调、优先级层级（默认 < 用户设置 < 命令行 < 代码）等。

### ConsoleManager.h
简单的转发头文件，包含 `IConsoleManager.h`。

---

## 线程同步原语

### CriticalSection.h
重定向到平台特定的临界区实现。`FCriticalSection` 提供互斥访问共享资源的基本同步机制。

### Event.h - `FEvent`
事件同步原语抽象。提供 `Create`/`Trigger`/`Reset`/`Wait` 接口，支持手动和自动复位模式。是线程间信号通知的基础机制。

### PThreadEvent.h - `FPThreadEvent`
基于 PThreads 的事件实现。使用 `pthread_mutex_t` 和 `pthread_cond_t` 模拟 Windows 事件语义（支持单次触发和广播触发模式），用于 Unix/Linux/Mac 平台。

### PThreadSemaphore.h - `FPThreadSemaphore`
基于 PThreads 的信号量实现。封装 POSIX `sem_t`，提供 `Acquire`/`TryAcquire`/`Release` 接口，支持超时等待。

### PThreadsRecursiveMutex.h - `UE::FPThreadsRecursiveMutex`
基于 PThreads 的递归互斥量实现。使用 `PTHREAD_MUTEX_RECURSIVE` 属性创建允许同一线程多次加锁的互斥量。

### PThreadsSharedMutex.h - `UE::FPThreadsSharedMutex`
基于 PThreads 的读写锁实现。使用 `pthread_rwlock_t` 提供共享读锁和独占写锁，支持 `TryLock`/`Lock`/`Unlock`/`TryLockShared`/`LockShared`/`UnlockShared` 接口。

### UESemaphore.h
通过 `COMPILED_PLATFORM_HEADER(Semaphore.h)` 包含平台特定的信号量实现。

### PooledSyncEvent.h - `FPooledSyncEvent`
池化同步事件的 RAII 包装。从 `FPlatformProcess::GetSynchEventFromPool` 获取事件对象，析构时自动归还池中，避免频繁创建/销毁事件的开销。

---

## 线程管理

### Runnable.h - `FRunnable`
可运行对象抽象基类。定义了线程执行的生命周期方法：`Init()` 初始化、`Run()` 执行主体逻辑、`Stop()` 请求停止、`Exit()` 清理。`GetSingleThreadInterface()` 支持单线程模式下的 tick 执行。

### RunnableThread.h - `FRunnableThread`
可运行线程封装。工厂方法 `Create()` 创建并启动执行 `FRunnable` 的系统线程。提供 `SetThreadPriority`/`SetThreadAffinity`/`Suspend`/`Kill`/`WaitForCompletion` 等线程控制方法。支持 Real/Fake/Forkable 三种线程类型。

### Thread.h - `FThread`
简化的系统线程 API。相比 `FRunnable`/`FRunnableThread` 更简洁，直接接受 `TUniqueFunction<void()>` 作为线程函数。使用后必须 `Join()` 或 `Detach()`。大多数并行处理应优先使用 TaskGraph。

### ThreadManager.h - `FThreadManager`
线程管理器单例。维护所有已注册 `FRunnableThread` 的列表，提供按线程 ID 查询线程名的功能。在单线程模式下负责 tick 所有 Fake 线程。支持获取所有线程的栈回溯（仅 Windows/Mac）。

### ThreadHeartBeat.h - `FThreadHeartBeat` / `FGameThreadHitchHeartBeatThreaded`
线程心跳检测系统。`FThreadHeartBeat` 监控各线程是否在规定时间内发送心跳，超时则判定为线程挂起（hang）并触发崩溃报告。`FGameThreadHitchHeartBeatThreaded` 专门检测游戏线程的帧间卡顿（hitch）。`FThreadHeartBeatClock` 提供不受系统挂起影响的本地时钟。各种 Scope 类（`FSlowHeartBeatScope`/`FFunctionHeartBeatScope`/`FDisableHitchDetectorScope`）允许临时暂停心跳检测。

### ThreadingBase.h
线程基础设施聚合头文件，集中包含 `CriticalSection`、`Event`、`Runnable`、`RunnableThread`、`ThreadManager`、`ThreadSafe*`、`ThreadSingleton`、`TlsAutoCleanup`、`UnrealMemory`、`ScopeLock`、`QueuedThreadPool` 等。

---

## 线程安全工具

### ThreadSafeBool.h - `FThreadSafeBool`
线程安全布尔值。基于 `FThreadSafeCounter` 实现原子读写的布尔变量。**已废弃**，建议使用 `std::atomic<bool>`。

### ThreadSafeCounter.h - `FThreadSafeCounter`
线程安全32位计数器。通过平台原子操作提供线程安全的计数功能。**已废弃**，建议使用 `std::atomic<int32>`。

### ThreadSafeCounter64.h - `FThreadSafeCounter64`
线程安全64位计数器。与 `FThreadSafeCounter` 功能相同但使用 `int64` 类型。**已废弃**，建议使用 `std::atomic<int64>`。

### ThreadSingleton.h - `TThreadSingleton<T>`
线程单例模板。确保每个线程拥有独立的单例实例，通过 TLS 存储。`Get()` 方法线程安全，首次调用时自动创建实例。

### TlsAutoCleanup.h - `FTlsAutoCleanup` / `TTlsAutoCleanupValue<T>`
TLS 自动清理基类。存储在线程本地存储中的对象继承此类后，线程退出时会被自动多态删除。`TTlsAutoCleanupValue<T>` 是值包装器模板。

---

## 预处理器工具

### PreprocessorHelpers.h
预处理器辅助宏集合。提供 `UE_STRINGIZE`（字符串化）、`UE_JOIN`（令牌拼接）、`UE_IF`（条件选择）、`UE_VA_ARG_COUNT`（可变参数计数）、`COMPILED_PLATFORM_HEADER`（平台头文件路径生成）等预处理器元编程工具。`COMPILED_PLATFORM_HEADER` 是整个 HAL 平台重定向机制的核心。

### AllowTCHAR.h
允许 `TCHAR` 宏定义。与 `HideTCHAR.h` 配合使用，在包含可能冲突的第三方头文件前后控制 `TCHAR` 宏的可见性。

### HideTCHAR.h
隐藏 `TCHAR` 宏定义。在包含第三方头文件时临时取消 `TCHAR` 定义以避免命名冲突。

---

## 输出设备和异常处理

### OutputDevices.h
聚合包含各种输出设备相关头文件的便捷头文件。

### FeedbackContextAnsi.h - `FFeedbackContextAnsi`
ANSI 终端反馈上下文。提供向标准输出（控制台）写入进度信息、警告和错误的能力，用于命令行工具和无 GUI 环境。

### ExceptionHandling.h
结构化异常处理（SEH）相关的工具和宏定义，用于在发生崩溃时捕获和处理异常。

---

## 模块基础设施

### PerModuleInline.inl
每个模块必须包含的内联文件。定义了调试可视化辅助（`UE_VISUALIZERS_HELPERS`）、全局 operator new/delete 重载（`REPLACEMENT_OPERATOR_NEW_AND_DELETE`，使引擎所有模块统一使用 `FMemory` 进行内存分配）、`FMemory` 包装函数（`UE_DEFINE_FMEMORY_WRAPPERS`），以及非单体构建中的模块标识导出函数（`ThisIsAnUnrealEngineModule()`）。

---

## 说明

| 后缀 | 含义 |
|-------|------|
| `.h` | 标准头文件 |
| `.inl` | 内联实现文件 |

> 本文档由自动分析工具生成，基于 UE5 源码中各头文件的类声明和注释。
