# UE5 Templates 模块类参考

> 路径: `Engine/Source/Runtime/Core/Public/Templates/`
>
> 本文档记录该目录下所有头文件中定义的主要模板类/结构体/工具及其用途。

---

## 目录

- [类型特征 -- 基础判断](#类型特征----基础判断)
- [类型特征 -- 复合/特殊判断](#类型特征----复合特殊判断)
- [类型变换](#类型变换)
- [智能指针](#智能指针)
- [引用计数](#引用计数)
- [函数对象与调用](#函数对象与调用)
- [比较与排序](#比较与排序)
- [内存操作](#内存操作)
- [原子操作](#原子操作)
- [工具模板](#工具模板)
- [前向声明与辅助](#前向声明与辅助)

---

## 类型特征 -- 基础判断

### IsArithmetic.h - `TIsArithmetic<T>`
判断类型是否为算术类型（整数或浮点数）。等价于 `std::is_arithmetic`。

### IsIntegral.h - `TIsIntegral<T>`
判断类型是否为整数类型。等价于 `std::is_integral`。

### IsFloatingPoint.h - `TIsFloatingPoint<T>`
判断类型是否为浮点类型。等价于 `std::is_floating_point`。

### IsSigned.h - `TIsSigned<T>`
判断类型是否为有符号类型。等价于 `std::is_signed`。

### IsPointer.h - `TIsPointer<T>`
判断类型是否为指针类型。等价于 `std::is_pointer`。

### IsArray.h - `TIsArray<T>`
判断类型是否为 C 数组类型。等价于 `std::is_array`。

### IsEnum.h - `TIsEnum<T>`
判断类型是否为枚举类型。等价于 `std::is_enum`。

### IsEnumClass.h - `TIsEnumClass<T>`
判断类型是否为强类型枚举（`enum class`）。通过 `TIsEnum` + 非隐式转换为 `int` 来判断。

### IsClass.h - `TIsClass<T>`
判断类型是否为类/结构体类型。等价于 `std::is_class`。

### IsConst.h - `TIsConst<T>`
判断类型是否带有 `const` 限定符。等价于 `std::is_const`。

### IsAbstract.h - `TIsAbstract<T>`
判断类型是否为抽象类（含纯虚函数）。等价于 `std::is_abstract`。

### IsPolymorphic.h - `TIsPolymorphic<T>`
判断类型是否为多态类型（含虚函数）。等价于 `std::is_polymorphic`。

### IsMemberPointer.h - `TIsMemberPointer<T>`
判断类型是否为成员指针（成员函数指针或数据成员指针）。等价于 `std::is_member_pointer`。

### IsInitializerList.h - `TIsInitializerList<T>`
判断类型是否为 `std::initializer_list<T>` 类型。

---

## 类型特征 -- 复合/特殊判断

### AreTypesEqual.h - `TAreTypesEqual<A, B>`
判断两个类型是否相同。等价于 `std::is_same`。**已废弃**，建议使用 `std::is_same_v`。

### IsTrivial.h - `TIsTrivial<T>`
判断类型是否为平凡（trivial）类型。等价于 `std::is_trivial`。

### IsTriviallyCopyAssignable.h - `TIsTriviallyCopyAssignable<T>`
判断类型是否支持平凡拷贝赋值。等价于 `std::is_trivially_copy_assignable`。

### IsTriviallyCopyConstructible.h - `TIsTriviallyCopyConstructible<T>`
判断类型是否支持平凡拷贝构造。等价于 `std::is_trivially_copy_constructible`。

### IsTriviallyDestructible.h - `TIsTriviallyDestructible<T>`
判断类型是否支持平凡析构。等价于 `std::is_trivially_destructible`。

### IsConstructible.h - `TIsConstructible<T, Args...>`
判断类型是否可用给定参数列表构造。等价于 `std::is_constructible`。

### IsPODType.h - `TIsPODType<T>`
判断类型是否为 POD（Plain Old Data）类型。UE 自定义的特征，可以通过模板特化为自定义类型声明 POD 属性。

### IsUECoreType.h - `TIsUECoreType<T>`
判断类型是否为 UE 核心类型。用于区分 UE 引擎类型和第三方类型，影响某些模板的行为选择。

### IsArrayOrRefOfType.h - `TIsArrayOrRefOfType<T, ElemType>`
判断类型是否为特定元素类型的 C 数组或数组引用。用于函数模板中限制字符数组参数。

### IsArrayOrRefOfTypeByPredicate.h - `TIsArrayOrRefOfTypeByPredicate<T, Predicate>`
使用谓词判断类型是否为满足条件的 C 数组或数组引用。

### IsValidVariadicFunctionArg.h - `TIsValidVariadicFunctionArg<T>`
判断类型是否可作为 C 可变参数函数的参数。排除不能安全传递给 `printf` 等函数的类型。

### IsInvocable.h - `TIsInvocable<Callable, Args...>`
判断可调用对象是否可用给定参数调用。等价于 `std::is_invocable`。

### PointerIsConvertibleFromTo.h - `TPointerIsConvertibleFromTo<From, To>`
判断 `From*` 是否可隐式转换为 `To*`。用于在模板中检查指针类型的可转换性。

### LosesQualifiersFromTo.h - `TLosesQualifiersFromTo<From, To>`
判断从 `From` 到 `To` 的转换是否会丢失 cv 限定符。

---

## 类型变换

### Decay.h - `TDecay<T>`
类型衰减。移除引用、const/volatile 限定符、数组转指针、函数转函数指针。等价于 `std::decay`。

### RemoveCV.h - `TRemoveCV<T>`
移除 const 和 volatile 限定符。等价于 `std::remove_cv`。

### RemoveReference.h - `TRemoveReference<T>`
移除引用（左值引用和右值引用）。等价于 `std::remove_reference`。

### RemoveExtent.h - `TRemoveExtent<T>`
移除数组的第一维度。等价于 `std::remove_extent`。

### MakeSigned.h - `TMakeSigned<T>`
将无符号整数类型转换为对应的有符号类型。等价于 `std::make_signed`。

### MakeUnsigned.h - `TMakeUnsigned<T>`
将有符号整数类型转换为对应的无符号类型。等价于 `std::make_unsigned`。

### CopyQualifiersFromTo.h - `TCopyQualifiersFromTo<From, To>`
将 `From` 类型的 cv 限定符复制到 `To` 类型上。

### CopyQualifiersAndRefsFromTo.h - `TCopyQualifiersAndRefsFromTo<From, To>`
将 `From` 类型的 cv 限定符和引用类型复制到 `To` 类型上。

### ChooseClass.h - `TChooseClass<Condition, TrueType, FalseType>`
编译期条件类型选择。等价于 `std::conditional`。

### IntegralConstant.h - `TIntegralConstant<T, V>`
编译期整数常量。等价于 `std::integral_constant`。

### MaxSizeof.h - `TMaxSizeof<Types...>`
计算可变参数类型列表中最大的 `sizeof` 值。

---

## 智能指针

### UniquePtr.h - `TUniquePtr<T>`
独占所有权智能指针。类似 `std::unique_ptr`，管理动态分配对象的生命周期。支持自定义删除器、`MakeUnique<T>()` 工厂函数、数组特化。不可拷贝但可移动。

### SharedPointer.h - `TSharedPtr<T>` / `TSharedRef<T>` / `TWeakPtr<T>`
UE 自定义共享指针系统，核心特点：

- **`TSharedPtr<T>`** — 共享所有权智能指针。类似 `std::shared_ptr`，通过引用计数管理对象生命周期。可以为 null。
- **`TSharedRef<T>`** — 非空共享引用。保证始终指向有效对象，不能为 null。在 API 中表达"非空"语义。
- **`TWeakPtr<T>`** — 弱引用。不增加引用计数，通过 `Pin()` 尝试提升为 `TSharedPtr`。

支持两种线程安全模式：`ESPMode::NotThreadSafe`（默认，性能更好）和 `ESPMode::ThreadSafe`（原子引用计数）。提供 `MakeShared<T>()` 和 `MakeShareable()` 工厂函数。

### SharedPointerFwd.h
共享指针系统的前向声明。声明 `TSharedPtr`、`TSharedRef`、`TWeakPtr` 和 `ESPMode` 枚举。

### SharedPointerInternals.h
共享指针的内部实现细节。定义引用计数器、控制块等内部数据结构，不应直接使用。

### SharedPointerTesting.inl
共享指针系统的单元测试实现。

### PimplPtr.h - `TPimplPtr<T>`
Pimpl（指向实现）智能指针。类似 `TUniquePtr` 但专为 Pimpl 惯用法设计。析构函数不要求类型完整（在头文件中声明时），但必须在实现文件中定义（类型完整时）。

### UniqueObj.h - `TUniqueObj<T>`
唯一对象包装器。与 `TUniquePtr` 不同，`TUniqueObj` 总是持有一个有效对象（不能为 null）。拷贝时深拷贝底层对象，移动时转移所有权。

---

## 引用计数

### RefCounting.h - `FRefCountBase` / `FRefCountedObject` / `TRefCountPtr<T>`
UE 的侵入式引用计数系统。

- **`FRefCountBase`** — 引用计数基类（非虚析构）。提供 `AddRef()`/`Release()` 方法，引用计数归零时调用 `delete this`。
- **`FRefCountedObject`** — 引用计数基类（虚析构版本）。适用于需要多态删除的对象。
- **`TRefCountPtr<T>`** — 侵入式引用计数智能指针。自动管理 `AddRef`/`Release` 调用。要求 T 类型自身提供引用计数（继承自 `FRefCountBase`）。

### RetainedRef.h - `TRetainedRef<T>`
保持引用包装器。类似于 `TRefCountPtr` 但用于在 lambda 捕获中自动保持引用计数，避免手动管理 `AddRef`/`Release`。

---

## 函数对象与调用

### Function.h - `TFunction<Signature>` / `TFunctionRef<Signature>` / `TUniqueFunction<Signature>`
UE 的类型擦除函数对象系统：

- **`TFunctionRef<Ret(Args...)>`** — 非拥有函数引用。类似于函数指针但可绑定 lambda、成员函数等。不拥有可调用对象的所有权，适用于同步回调参数。
- **`TFunction<Ret(Args...)>`** — 可拷贝的类型擦除函数对象。类似 `std::function`，拥有可调用对象的所有权。小对象优化（32字节内联存储）。
- **`TUniqueFunction<Ret(Args...)>`** — 不可拷贝的类型擦除函数对象。可以绑定不可拷贝的可调用对象（如带有 `TUniquePtr` 捕获的 lambda）。

### FunctionFwd.h
`TFunction`/`TFunctionRef`/`TUniqueFunction` 的前向声明。

### FunctionWithContext.h - `TFunctionWithContext<Signature>`
带上下文的函数对象。在 `TFunction` 基础上附加一个上下文参数，常用于 AutoRTFM 事务感知的回调。

### Invoke.h - `Invoke(Callable, Args...)`
统一调用接口。等价于 `std::invoke`，可以统一调用普通函数、函数指针、成员函数指针和成员数据指针。

### Projection.h - `Projection(Invocable...)`
投影函数。将可调用对象转换为普通可调用形式。支持链式投影（`Projection(A, B, C)(Args...)` 等价于 `C(B(A(Args...)))`）。常用于排序算法的投影参数（如 `Algo::SortBy(Array, Projection(&FObj::Member))`）。

### Identity.h - `FIdentity`
恒等函数对象。`operator()` 返回参数本身。等价于 `std::identity`。

### IdentityFunctor.h - `FIdentityFunctor`
恒等函数子。与 `FIdentity` 功能相同，返回传入的参数本身。

---

## 比较与排序

### EqualTo.h - `TEqualTo<T>`
相等比较函数对象。默认使用 `operator==`。

### Less.h - `TLess<T>`
小于比较函数对象。默认使用 `operator<`。等价于 `std::less`。

### Greater.h - `TGreater<T>`
大于比较函数对象。默认使用 `operator>`。等价于 `std::greater`。

### ReversePredicate.h - `TReversePredicate<Predicate>`
反转谓词包装器。将给定比较谓词的参数顺序反转，即 `TReversePredicate<TLess>` 的行为等价于 `TGreater`。

### Sorting.h - `Sort()` / `StableSort()` / `IntroSort()`
UE 排序算法集合：

- **`Sort()`** — 通用排序，基于内省排序（Introsort = 快速排序 + 堆排序回退）。
- **`StableSort()`** — 稳定排序，保持相等元素的原始相对顺序。基于归并排序实现。
- **`IntroSort()`** — 内省排序，快排递归深度超限时切换到堆排序。

所有排序函数支持自定义比较谓词和投影。

---

## 内存操作

### MemoryOps.h
容器底层内存操作函数集合。提供：

- **`DefaultConstructItems<T>()`** — 默认构造元素数组（零初始化可构造类型用 `Memset`，否则逐个调用构造函数）
- **`DestructItem<T>()` / `DestructItems<T>()`** — 析构单个/多个元素
- **`ConstructItems<T>()`** — 从源数据拷贝构造元素数组
- **`MoveConstructItems<T>()`** — 移动构造元素数组
- **`RelocateConstructItems<T>()`** — 重定位元素（对可位拷贝类型用 `Memmove`）
- **`BitwiseRelocateContiguousItems<T>()`** — 按位重定位连续元素

这些函数根据类型特征选择最优实现路径（位拷贝 vs 逐个操作）。

### TypeCompatibleBytes.h - `TTypeCompatibleBytes<T>` / `TAlignedBytes<Size, Alignment>`
提供与指定类型大小和对齐方式匹配的原始字节存储。用于手动管理对象生命周期的场景（placement new）。`TAlignedBytes` 提供指定大小和对齐的原始存储。

---

## 原子操作

### Atomic.h - `TAtomic<T>`
UE 的原子类型模板。类似 `std::atomic<T>`，提供线程安全的 `Load`/`Store`/`Exchange`/`IncrementExchange`/`DecrementExchange`/`AddExchange`/`CompareExchange` 操作。使用 UE 平台层原子操作实现。**部分 API 已废弃**，建议使用 `std::atomic`。

---

## 工具模板

### UnrealTemplate.h
UE 核心模板工具集合（大型头文件），包含：

- **`Forward<T>()`** — 完美转发。等价于 `std::forward`。
- **`MoveTemp()`** — 移动语义。等价于 `std::move`，但在 Debug 构建中有额外检查。
- **`MoveTempIfPossible()`** — 条件移动，无法移动时退化为拷贝。
- **`CopyTemp()`** — 显式拷贝。确保产生右值拷贝。
- **`Swap()`** — 交换两个值。
- **`Exchange()`** — 赋新值并返回旧值。等价于 `std::exchange`。
- **`GetTypeHash()`** — 获取类型哈希值（为基础类型提供默认实现）。
- **`TGuardValue<T>`** — 作用域值守卫。构造时保存旧值并设新值，析构时恢复旧值。
- **`TScopeCounter<T>`** — 作用域计数器。构造时递增，析构时递减。
- **`TKeyValuePair<K, V>`** — 键值对类型。
- **`TIsBitwiseConstructible<Dest, Src>`** — 判断是否可从 Src 按位构造 Dest（如 `uint8` 可按位构造 `int8`）。
- **`TIsZeroConstructType<T>`** — 判断默认构造是否等价于零填充。
- **`TIsContiguousContainer<T>`** — 判断容器是否提供连续内存访问（如 `TArray`）。

### UnrealTypeTraits.h
UE 类型特征扩展集合，包含：

- **`TCallTraits<T>`** — 调用特征。根据类型大小决定最优参数传递方式（值传递 vs 常引用传递）。
- **`TIsReferenceType<T>`** / **`TIsLValueReferenceType<T>`** / **`TIsRValueReferenceType<T>`** — 引用类型判断。
- **`TIsVoidType<T>`** — void 类型判断。
- **`TIsFundamentalType<T>`** — 基本类型判断。
- **`TFormatSpecifier<T>`** — 格式化说明符，为基础类型提供 `printf` 格式字符串。
- **`TIsCharType<T>`** — 字符类型判断（`ANSICHAR`/`WIDECHAR`/`UTF8CHAR`/`UTF16CHAR`/`UTF32CHAR`）。
- **`TIsCharEncodingCompatibleWith<Enc1, Enc2>`** — 字符编码兼容性判断。

### TypeHash.h - `GetTypeHash()`
类型哈希函数。为基础类型（整数、浮点、指针、枚举等）提供 `GetTypeHash()` 默认实现，是 `TSet`/`TMap` 等哈希容器的基础。使用 `HashCombineFast()` 组合多个哈希值。

### Tuple.h - `TTuple<Types...>`
元组类型。类似 `std::tuple`，可存储任意类型的值列表。支持：

- `Get<Index>()` — 按索引访问元素
- `MakeTuple()` — 创建元组的工厂函数
- `Apply(Func)` — 将元组元素展开为函数参数
- 结构化绑定（C++17 structured bindings）支持

### ValueOrError.h - `TValueOrError<ValueType, ErrorType>`
值或错误类型。表示操作结果要么是成功值，要么是错误值。类似于 `std::expected`（C++23）。通过 `MakeValue()`/`MakeError()` 工厂函数创建。

### Overload.h - `UE::Core::Overload(Functors...)`
重载函数对象组合器。将多个可调用对象组合为一个，通过重载决议选择合适的调用。常与 `Visit` 和变体类型配合使用。

### ScopedCallback.h - `TScopedCallback<Func>`
作用域回调。构造时接受一个可调用对象，析构时自动调用。用于确保清理逻辑在作用域退出时执行。

### GuardValueAccessors.h
Guard 值访问器辅助工具。提供在 `TGuardValue` 中使用的值访问和恢复逻辑。

### DontCopy.h - `FDontCopy`
禁止拷贝基类。继承此类可禁止拷贝构造和拷贝赋值。等价于 `boost::noncopyable`。

### NoDestroy.h - `TNoDestroy<T>`
不析构包装器。持有一个 T 类型的对象但永远不调用其析构函数。用于全局/静态对象避免静态析构顺序问题。

### Models.h - `UE::Core::Private::Models`
概念模型检测工具。使用 SFINAE 技术检测类型是否满足某种"模型"（即是否具有特定的成员函数或运算符）。

### Requires.h - `UE_REQUIRES(...)`
约束宏。`UE_REQUIRES(Condition)` 展开为 `typename = std::enable_if_t<Condition>` 形式的模板约束，用于在模板声明中施加编译期条件。

### ResolveTypeAmbiguity.h - `TResolveTypeAmbiguity<T, Types...>`
类型歧义解决工具。当函数重载存在歧义时，帮助编译器选择最匹配的重载。

---

## 指针工具

### NonNullPointer.h - `TNonNullPointer<T>`
非空指针包装。编译期确保指针不为 null，构造时检查。

### NotNull.h - `TNotNull<T>`
非空指针/引用标记。比 `TNonNullPointer` 更通用，可用于任何"类指针"类型。

### GSLNotNull.h
GSL（Guidelines Support Library）风格的非空指针包装。

### PointerVariants.h - `TPointerVariants<Types...>`
指针变体。类似 `TVariant` 但专门用于指针类型，使用指针的低位或标签位来区分变体。

### AlignmentTemplates.h - `Align()` / `AlignDown()` / `AlignArbitrary()`
对齐辅助函数：

- **`Align(Val, Alignment)`** — 向上对齐到指定边界
- **`AlignDown(Val, Alignment)`** — 向下对齐到指定边界
- **`AlignArbitrary(Val, Alignment)`** — 对齐到任意值（非2的幂）
- **`IsAligned(Val, Alignment)`** — 检查是否对齐

---

## 逻辑运算

### AndOrNot.h - `TAnd<...>` / `TOr<...>` / `TNot<T>`
编译期逻辑运算模板：

- **`TAnd<Conditions...>`** — 逻辑与，所有条件为真时结果为真
- **`TOr<Conditions...>`** — 逻辑或，任一条件为真时结果为真
- **`TNot<Condition>`** — 逻辑非，反转条件

等价于 `std::conjunction`/`std::disjunction`/`std::negation`。

### EnableIf.h - `TEnableIf<Condition, T>`
SFINAE 条件启用。等价于 `std::enable_if`。**已废弃**，建议使用 `std::enable_if_t`。

---

## 前向声明与辅助

### SharedPointerFwd.h
共享指针前向声明（已在智能指针章节说明）。

### FunctionFwd.h
函数对象前向声明（已在函数对象章节说明）。

---

## 说明

| 后缀 | 含义 |
|-------|------|
| `.h` | 标准头文件 |
| `.inl` | 内联实现/测试文件 |

> 本文档由自动分析工具生成，基于 UE5 源码中各头文件的类声明和注释。
