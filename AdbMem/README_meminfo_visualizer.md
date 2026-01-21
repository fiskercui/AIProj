# Memory Info Visualizer - 使用说明

## 📋 概述

这是一个用于可视化Android dumpsys meminfo数据的工具，可以将多个meminfo数据绘制成交互式图表。

## 📁 文件说明

### 1. `meminfo_visualizer.py`
Python脚本，用于生成HTML查看器和解析MD文件。

### 2. `meminfo_viewer.html` ⭐ 推荐使用
**通用的HTML查看器**，可以选择任意meminfo MD文件进行可视化。

### 3. `meminfo_demo.html`
演示版本，自动加载 `meminfo_output_20260120_184312.md` 文件的数据。

## 🚀 使用方法

### 方法一：使用通用查看器（推荐）

1. **双击打开** `meminfo_viewer.html` 文件（或在浏览器中打开）
2. **点击 "选择文件" 按钮**，选择您的meminfo MD文件（如 `meminfo_output_20260120_184312.md`）
3. **等待数据加载**，会自动显示图表和过滤器
4. **使用过滤器**：
   - 左侧：选择要显示的内存类型（Native Heap, Dalvik Heap等）
   - 右侧：选择要显示的指标（PSS Total, Private Dirty）
   - 点击 "Select All" / "Deselect All" 快速选择/取消

### 方法二：查看演示

1. 直接打开 `meminfo_demo.html`
2. 自动显示预加载的数据
3. 可以立即测试过滤功能

### 方法三：使用Python脚本

```bash
python meminfo_visualizer.py
```
这会生成 `meminfo_viewer.html` 文件。

## 📊 功能特性

### ✅ 已实现功能

1. **多数据源支持**：可以解析包含多个dumpsys meminfo执行结果的MD文件
2. **多种内存类型**：
   - Native Heap（原生堆）
   - Dalvik Heap（Dalvik堆）
   - Dalvik Other（Dalvik其他）
   - Stack（栈）
   - Ashmem（匿名共享内存）
   - .so mmap（共享库映射）
   - .jar mmap（JAR文件映射）
   - .apk mmap（APK文件映射）
   - .ttf mmap（字体文件映射）
   - .dex mmap（DEX文件映射）
   - .oat mmap（OAT文件映射）
   - .art mmap（ART运行时映射）
   - Other dev（其他设备）
   - Other mmap（其他映射）
   - Unknown（未知）

3. **双指标显示**：
   - PSS Total（PSS总计）
   - Private Dirty（私有脏页）

4. **交互式过滤**：
   - 内存类型过滤（可多选）
   - 指标类型过滤（可多选）
   - 实时更新图表

5. **图表功能**：
   - 横坐标：执行序号（#1, #2, #3...）
   - 纵坐标：内存大小（KB）
   - 彩色线条区分不同类型
   - 鼠标悬停显示详细信息（执行时间、精确数值）
   - 图例说明

6. **统计信息**：
   - 总执行次数
   - 内存类型数量
   - 时间范围

## 🎨 界面说明

### 顶部卡片
显示数据摘要：总执行次数、内存类型数量、时间范围

### 左侧过滤器 - Memory Types（内存类型）
- 显示所有可用的内存类型
- 勾选要在图表中显示的类型
- 默认选中 Native Heap、Dalvik Heap、Dalvik Other
- "Select All" 按钮：全选
- "Deselect All" 按钮：全部取消

### 右侧过滤器 - Metrics（指标）
- PSS Total：总PSS值
- Private Dirty：私有脏页大小
- 可同时选择两个或其中一个

### 图表区域
- 显示所有选中的内存类型和指标组合
- 每条线表示一个"内存类型-指标"组合
- 鼠标悬停查看详细数值

## 🔧 系统要求

- **操作系统**：Windows 10（已测试）
- **浏览器**：现代浏览器（Chrome, Edge, Firefox等）
- **Python**：Python 3.x（仅用于运行脚本，HTML文件可直接打开）

## 📝 数据格式要求

MD文件应包含如下格式的内容：

```markdown
## Execution #1

**Time**: 2026-01-20 18:43:12

| Pss Total | Private Dirty | ...
| --- | --- | ...
  Native Heap     4426     4308       40      ...
  Dalvik Heap     1956     1356      208      ...
  ...
```

## 🐛 常见问题

### Q: 选择文件后没有反应？
A: 确保您选择的是包含正确格式的MD文件，文件中应该包含 "## Execution #" 和内存数据。

### Q: 图表不显示？
A: 请检查至少选择了一个内存类型和一个指标。

### Q: 浏览器报错？
A: 确保使用现代浏览器（Chrome 90+, Edge 90+, Firefox 88+等）。

## 📄 许可

本工具用于Android内存分析，可自由使用和修改。
