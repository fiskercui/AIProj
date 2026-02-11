# UE5 Containers 模块类参考

> 路径: `Engine/Source/Runtime/Core/Public/Containers/`
>
> 本文档记录该目录下所有头文件中定义的主要类/结构体及其用途。

---

## 目录

- [数组类](#数组类)
- [集合与映射类](#集合与映射类)
- [队列类](#队列类)
- [链表类](#链表类)
- [哈希表类](#哈希表类)
- [位操作类](#位操作类)
- [字符串类](#字符串类)
- [缓冲区与缓存类](#缓冲区与缓存类)
- [并发容器类](#并发容器类)
- [内存分配与策略类](#内存分配与策略类)
- [迭代器与适配器类](#迭代器与适配器类)
- [其他工具类](#其他工具类)
- [前向声明与辅助头文件](#前向声明与辅助头文件)

---

## 数组类

### Array.h - `TArray`
UE 中最核心的动态数组容器。类似于 `std::vector`，是一个可动态扩容的类型化数组。假定元素类型是可重定位的（relocate-able），即可以透明地移动到新内存而无需调用拷贝构造函数。指向数组元素的指针可能在添加/删除其他元素时失效。删除元素的复杂度为 O(N)。

### ArrayBuilder.h - `TArrayBuilder`
流式数组构建器（Fluent Builder 模式）。提供链式调用 `Add()` 和 `Append()` 方法来逐步构建 `TArray`，最后通过 `Build()` 或隐式转换获取最终数组。

### ArrayView.h - `TArrayView`
数组视图类，对已有连续内存的非拥有（non-owning）引用。类似于 `std::span`，可以指向 `TArray`、C 数组或任何连续容器的元素，不负责分配/释放内存。支持自定义 `SizeType`（默认 `int32`），也有 64 位版本 `TArrayView64`。

### BasicArray.h - `TBasicArray`
基础数组实现，提供了比 `TArray` 更底层的数组抽象。用于带自定义初始预留大小的数组场景，内部管理 `Num`/`Max` 和数据指针，支持指定初始保留大小以避免早期重分配。

### ChunkedArray.h - `TChunkedArray`
分块数组。将元素存储在固定大小的块（chunk）中，而不是单一连续内存。当数组很大时可以减少重新分配和复制的开销，适用于不需要严格连续内存保证的场景。

### IndirectArray.h - `TIndirectArray`
间接数组。与 `TArray` 类似，但内部存储的是指向元素的**指针**而非元素本身。这样在调整数组索引大小时不需要重定位实际元素，已有指针保持有效。

### MRUArray.h - `TMRUArray`
最近使用数组（Most Recently Used Array），继承自 `TArray`。有一个元素数量上限 `MaxItems`，新添加的元素总是移到数组顶部（索引 0），超出上限时从末尾裁剪。适用于维护最近使用项列表的场景。

### PagedArray.h - `TPagedArray`
分页数组。以固定大小的页（page）为单位分配内存，页内元素连续但页之间不连续。相比普通数组，它不要求单一大块连续内存（减少内存碎片影响），且在不 resize 的情况下元素地址是持久稳定的。

### ScriptArray.h - `FScriptArray`
无类型脚本数组。`TArray` 的底层无类型表示（存储 `void*` 和元素计数/容量），用于蓝图/脚本系统在不知道具体元素类型时操作数组数据。

### StaticArray.h - `TStaticArray`
固定大小数组，类似于 `std::array`。模板参数指定元素类型和数组大小，在栈上或对象内部分配固定数量的元素。

### TransArray.h - `TTransArray`
事务性数组，继承自 `TArray`。在执行 `Add`/`Remove`/`Empty` 等操作时，会自动通过全局 Undo 系统（`GUndo`）记录变更，以支持编辑器中的撤销/重做功能。关联一个 `UObject` 作为 Owner。

---

## 集合与映射类

### Set.h - `TSet`
UE 的哈希集合容器。使用 `TSparseArray` 存储元素，并通过哈希桶链表实现快速查找。增删查操作均为 O(1) 平均复杂度。支持自定义 `KeyFuncs` 来定义元素的哈希和比较方式，支持 `ByHash()` 异构查找。

### CompactSet.h - `TCompactSet`
紧凑集合。与 `TSet` 功能类似（O(1) 增删查），但采用更紧凑的内存布局：数据数组中没有空洞（不像 SparseArray），碰撞链表和哈希表紧凑排列。在内存占用上优于 `TSet`，但在频繁增删时可能需要额外的数据搬移。

### CompactSetBase.h - `TCompactSetBase`
`TCompactSet` 的基础实现类，定义紧凑集合的核心数据结构和算法，由 `TCompactSet` 继承使用。

### SparseSet.h - `TSparseSet`
稀疏集合。使用 `TSparseArray` 存储元素并链入哈希桶，与 `TSet` 实现类似。是 `TSet` 的底层变体之一，具有不同的分配器默认配置。

### SortedSet.h - `TSortedSet`
有序集合。基于 `TArray` 存储并保持元素按照指定排序谓词（默认 `TLess`）排列。查找使用二分查找，插入需要保持有序。适用于需要有序遍历的集合场景。

### Map.h - `TMap` / `TMultiMap`
UE 的哈希映射容器。`TMap` 存储唯一键值对，`TMultiMap` 允许重复键。内部基于 `TSet` 实现，键值对以 `TPair<KeyType, ValueType>` 存储。O(1) 平均复杂度的增删查。也定义了 `TSparseMap`/`TSparseMultiMap`、`TCompactMap`/`TCompactMultiMap` 等变体。

### MapBuilder.h - `TMapBuilder`
Map 的流式构建器。通过链式 `Add()` 和 `Append()` 方法逐步构建 `TMap`，然后通过 `Build()` 获取结果。

### SortedMap.h - `TSortedMap`
有序映射。基于有序数组存储键值对，按照指定排序谓词维持键的有序性。查找使用二分查找，适合需要按键有序遍历的场景。

### SetUtilities.h - `FSetElementId`
集合元素 ID 及相关工具。定义了 `FSetElementId`（集合中元素的内部索引标识）以及集合操作的辅助类型和函数。

### SparseSetElement.h - `TSparseSetElement`
稀疏集合元素类型。封装了集合中每个元素的值（`Value`）、哈希桶链表下一个元素 ID（`HashNextId`）、以及所属的哈希桶索引（`HashIndex`）。

### ScriptCompactSet.h - `TScriptCompactSet`
无类型脚本紧凑集合。`TCompactSet` 的无类型版本，用于蓝图/脚本系统在不知道具体元素类型时操作紧凑集合。

### ScriptSparseSet.h - `TScriptSparseSet`
无类型脚本稀疏集合。`TSparseSet` 的无类型版本，供蓝图/脚本系统使用。

---

## 队列类

### Queue.h - `TQueue`
通用队列容器（FIFO）。基于链表实现的先进先出队列，支持线程安全模式（`EQueueMode::Mpsc` 多生产者单消费者，或 `EQueueMode::Spsc` 单生产者单消费者）。

### CircularQueue.h - `TCircularQueue`
环形队列（无锁）。基于固定大小的环形缓冲区实现的 SPSC（单生产者/单消费者）无锁队列。容量在构造时指定。

### SpscQueue.h - `TSpscQueue`
快速单生产者/单消费者无界并发队列。基于链表节点实现，无锁设计。不会在销毁前释放已消费节点的内存（而是回收复用），直到析构时统一释放。

### MpscQueue.h - `TMpscQueue`
快速多生产者/单消费者无界并发队列。基于原子操作实现无锁入队，单消费者线程出队。

### ClosableMpscQueue.h - `TClosableMpscQueue`
可关闭的多生产者/单消费者队列。在 `TMpscQueue` 基础上增加了"关闭"语义，一旦关闭，后续的入队操作会返回失败。

### ConsumeAllMpmcQueue.h - `TConsumeAllMpmcQueue`
全量消费式多生产者/多消费者队列。消费者每次取出队列中**所有**当前元素（而非单个），适用于批量处理的场景。

### DepletableMpmcQueue.h - `TDepletableMpmcQueue`
可耗尽的多生产者/多消费者队列。支持检测队列是否已被完全消费殆尽（depletable 语义），适用于需要知道"所有工作已完成"的场景。

### DepletableMpscQueue.h - `TDepletableMpscQueue`
可耗尽的多生产者/单消费者队列。与 `TDepletableMpmcQueue` 类似，但限制为单消费者。

### TransactionallySafeSpscQueue.h - `TTransactionallySafeSpscQueue`
事务安全的单生产者/单消费者无界并发队列。基于 `TSpscQueue` 设计，但使用互斥锁（`TransactionallySafeMutex`）代替原子操作以确保与 AutoRTFM 事务系统兼容。

### Deque.h - `TDeque`
双端队列（Deque）。支持在头部和尾部高效地添加/移除元素，内部通常基于环形缓冲区实现。

---

## 链表类

### List.h - `TDoubleLinkedList` / `TLinkedList`
双向链表和侵入式单向链表。`TDoubleLinkedList` 是非侵入式双向链表（节点包含元素拷贝），`TLinkedList` 是侵入式单向链表（元素继承节点类型）。

### IntrusiveDoubleLinkedList.h - `TIntrusiveDoubleLinkedList` / `TIntrusiveDoubleLinkedListNode`
侵入式双向链表。元素类型需要继承 `TIntrusiveDoubleLinkedListNode`，支持 O(1) 的插入/删除操作。可通过不同 `ContainerType` 模板参数让同一元素同时存在于多个链表中。

### LinkedListBuilder.h - `TLinkedListBuilder`
链表构建器辅助类，用于方便地构建 `TLinkedList`。

---

## 哈希表类

### HashTable.h - `TStaticHashTable` / `FHashTable`
哈希表实现，用于为其他数据结构建立索引。`TStaticHashTable` 是编译期固定大小的哈希表，`FHashTable` 是动态大小的哈希表。比 `TMap` 简单得多也更快，通过链式哈希解决冲突。

### CompactHashTable.h - `FCompactHashTable`
紧凑哈希表。采用更节省内存的哈希表实现。

---

## 位操作类

### BitArray.h - `TBitArray`
动态大小的位数组。每个元素占用 1 位，支持位级操作（AND、OR、NOT 等），提供设置/清除/查找位的迭代器。类似于 `std::bitset` 但大小可变。包含 `FBitSet` 辅助结构。

### StaticBitArray.h - `TStaticBitArray`
固定大小的位数组。编译期确定位数，所有存储在栈上。与 `TBitArray` 类似但大小不可变。

---

## 字符串类

### UnrealString.h - `FString`
UE 的核心动态字符串类，基于 `TArray<TCHAR>` 实现。类似于 `std::wstring`，是 UE 中使用最广泛的字符串类型。支持格式化（`Printf`）、查找、替换、大小写转换、数值转换等丰富操作。同时提供 `BytesToString`/`StringToBytes` 等辅助函数。

### AnsiString.h - `FAnsiString`
ANSI 编码的动态字符串类。通过与 `FString` 相同的宏模板机制（`UnrealString.h.inl`）实现，但底层字符类型为 `ANSICHAR`。

### Utf8String.h - `FUtf8String`
UTF-8 编码的动态字符串类。底层字符类型为 `UTF8CHAR`，通过宏模板复用 `FString` 的实现。`Printf` 格式字符串为 ANSI 类型但参数可接受 UTF-8 字符串。

### SharedString.h - `FSharedString`
共享字符串。通过引用计数或内部共享机制减少字符串拷贝开销，适用于大量重复字符串的场景。

### StringView.h - `FStringView` / `FAnsiStringView` / `FUtf8StringView`
字符串视图。对已有字符串数据的非拥有引用（类似 `std::string_view`），不分配内存。支持 TCHAR、ANSI 和 UTF-8 三种字符类型。

### StringConv.h
字符串编码转换工具。提供 TCHAR、ANSI、UTF-8、UTF-16 等编码之间的转换功能类和宏，如 `TCHAR_TO_ANSI`、`ANSI_TO_TCHAR` 等。

### StringFwd.h
字符串类型的前向声明。声明 `FString`、`FAnsiString`、`FUtf8String`、`TString<CharType>` 等类型的前向引用，减少头文件依赖。

### StringOverload.h
字符串重载辅助。提供对不同字符串类型之间运算符和函数重载的辅助模板。

### LazyPrintf.h - `FLazyPrintf`
延迟格式化工具。允许预设一组替换参数（`%0`、`%1` 等占位符），在需要时才执行格式化拼接，避免不必要的字符串构造开销。

---

## 缓冲区与缓存类

### CircularBuffer.h - `TCircularBuffer`
环形缓冲区。固定大小的循环数组，新写入覆盖最旧数据。适用于日志、采样数据等滚动窗口场景。

### RingBuffer.h - `TRingBuffer`
环形缓冲区。与 `TCircularBuffer` 类似的环形数组实现，支持头尾入队/出队操作。

### TripleBuffer.h - `TTripleBuffer`
三重缓冲区。使用三个缓冲区实现生产者/消费者之间的无锁读写：一个用于写入、一个用于读取、一个用于交换。支持脏标记检查（`IsDirty`）和缓冲区交换。

### LruCache.h - `TLruCache`
LRU 缓存（Least Recently Used）。维护一个最大容量的键值缓存，当超出容量时自动淘汰最近最少使用的条目。内部使用哈希集合 + 双向链表实现。

### DiscardableKeyValueCache.h - `TDiscardableKeyValueCache`
可丢弃的键值缓存。一种允许在内存压力下丢弃缓存条目的键值缓存实现。

---

## 并发容器类

### LockFreeList.h - `TLockFreePointerListUnordered` 等
无锁链表集合。提供多种无锁数据结构（无序链表、LIFO 栈、FIFO 队列等），用于高性能多线程场景。

### LockFreeFixedSizeAllocator.h - `TLockFreeFixedSizeAllocator`
无锁固定大小内存分配器。通过无锁空闲列表管理固定大小的内存块，用于高频分配/释放场景（如无锁链表的节点分配）。

### StripedMap.h - `TStripedMap`
分条映射。将数据分布到多个内部桶（stripe）中，每个桶有独立的锁，以减少多线程环境下的锁竞争。

---

## 内存分配与策略类

### ContainerAllocationPolicies.h
容器分配策略集合。定义了 UE 容器使用的各种内存分配策略类，包括：
- `TSizedDefaultAllocator` - 默认堆分配器
- `TSizedNonshrinkingAllocator` - 不会自动缩小的分配器
- `TInlineAllocator` - 内联分配器（小数据栈上分配，超出后转堆）
- `TFixedAllocator` - 固定大小分配器
- `FDefaultSetAllocator` - 集合默认分配器
- `FDefaultBitArrayAllocator` - 位数组默认分配器
- 以及容器增长策略（slack growth factor）的配置宏

### AllocatorFixedSizeFreeList.h - `TAllocatorFixedSizeFreeList`
固定大小空闲列表分配器。维护一个空闲块链表，用于高效地分配和释放固定大小的内存块，减少频繁的系统内存分配调用。

### AllowShrinking.h - `EAllowShrinking`
收缩策略枚举。定义容器在移除元素时是否允许收缩内存（`Yes`/`No`）。

---

## 迭代器与适配器类

### IteratorAdapter.h - `TIteratorAdapter`
迭代器适配器（CRTP 模式）。提供 UE 兼容迭代器的标准接口，只需子类实现 `Dereference()`、`Increment()`、`Equals()` 等最少方法，适配器自动补全 `++`、`--`、`*`、`->` 等运算符。

### ArrowWrapper.h - `FArrowWrapper`
箭头运算符包装器。为不直接支持 `->` 运算符的类型提供 `operator->()` 的包装。

### AdderRef.h - `TAdderRef`
加法器引用辅助。用于在容器操作中提供"添加元素"的引用语义。

---

## 其他工具类

### SparseArray.h - `TSparseArray`
稀疏数组。类似于 `TArray` 但允许中间有空洞（已删除的元素位置保留为空闲槽位）。使用位数组 `TBitArray` 标记每个槽位是否已分配。删除是 O(1)，遍历跳过空洞。用作 `TSet` 和 `TMap` 的底层存储。

### SparseSet.h - `TSparseSet`
稀疏集合的实现，基于 `TSparseArray` 和哈希桶链表。

### BinaryHeap.h - `FBinaryHeap`
二叉堆（优先队列）。最小键在堆顶，用于为其他数据结构建立优先级索引。`KeyType` 必须实现 `operator<`。

### DirectoryTree.h - `TDirectoryTree`
目录树结构。以树形结构存储路径到值的映射，支持按路径层级导航和查询，适用于虚拟文件系统或资产路径管理。

### DynamicRHIResourceArray.h - `TDynamicRHIResourceArray`
动态 RHI 资源数组。继承自 `TResourceArray`，用于存储需要上传到 GPU 的资源数据（如顶点/索引缓冲），实现 `FResourceArrayInterface` 接口。

### ResourceArray.h - `TResourceArray`
资源数组。`TArray` 的扩展版本，实现了 `FResourceArrayInterface`，支持将数组数据批量提交为 RHI（渲染硬件接口）资源。

### EnumAsByte.h - `TEnumAsByte`
枚举值包装器。将枚举类型存储为单个字节（`uint8`），用于蓝图可见的旧式枚举属性（UE4 遗留兼容）。新代码应使用 `enum class` + `UENUM()` 而非此类。

### ContainerElementTypeCompatibility.h - `TContainerElementTypeCompatibility`
容器元素类型兼容性。用于裸指针与包装指针（如 `TObjectPtr`）之间的容器元素转换兼容，属于临时兼容机制。

### ContainerHelpers.h
容器辅助函数。提供容器内部使用的工具函数，如无效数组/集合数量的错误处理（`OnInvalidArrayNum`、`OnInvalidSetNum`）。

### ContainersFwd.h
容器类型前向声明。集中声明 `TArray`、`TMap`、`TSet`、`FString` 等所有主要容器类型的前向引用及常用别名（如 `FDefaultAllocator`、`FWideString`、`TString<CharType>`）。

### BackgroundableTicker.h - `FBackgroundableTicker`
可后台运行的定时器。与 `FTicker` 类似，但支持在后台线程上触发回调。

### Ticker.h - `FTicker` / `FTSTicker`
定时器/心跳管理器。注册定期回调函数，在每帧或指定间隔触发。`FTSTicker` 是线程安全版本。

### StackTracker.h - `FStackTracker`
堆栈追踪器。用于捕获和统计调用栈信息，常用于内存分析和性能调试。

### StridedView.h - `TStridedView`
跨步视图。以非连续步长（stride）访问内存中的元素序列，适用于结构体数组中按特定偏移访问某个成员字段的场景。

### Union.h - `TUnion`
联合类型。类型安全的联合体实现，可存储多个子类型之一的值。通过内部类型索引跟踪当前有效的子类型。**已废弃**，新代码应使用 `TVariant`。

### VersePath.h - `UE::Core::FVersePath`
Verse 路径类。存储和操作 Verse 语言的资源路径（格式如 `/domain/path/leaf`）。支持路径有效性验证、比较、基路径判断（`IsBaseOf`）、域名提取等操作。

### VersePathFwd.h - `FVersePath` 前向声明
Verse 路径类型的前向声明头文件。声明 `UE::Core::FVersePath` 及相关运算符，用于减少头文件依赖。

---

## 说明

| 后缀 | 含义 |
|-------|------|
| `.h` | 标准头文件 |
| `.h.inl` | 内联实现文件，通过宏模板机制被多个头文件包含以生成不同的类特化（如 `FString`/`FAnsiString`/`FUtf8String` 共用 `UnrealString.h.inl`；`TSet`/`TSparseSet`/`TCompactSet` 共用各自的 `.h.inl`） |
| `.tps` | 第三方软件信息文件 |

> 本文档由自动分析工具生成，基于 UE5 源码中各头文件的类声明和注释。
