# ADB Memory Monitor - 开发聊天记录

## 2026-01-20 开发过程

### 用户需求
我需要使用 "指定目录的adb命令" 通过adb 命令 使用" .\adb.exe shell ps -A" 获得所有进程 ，找到进程中名字包含 com.android.webview:sandboxed_process0 进程， 获得完成的进程名A， 然后对进程名A使用 .\adb.exe shell dumpsys meminfo 进程名A， 并且每隔1s执行1s， 将执行得到的内容输出到文件，  要求使用python，操作系统是windows10

### 第一版实现
创建了 [`adb_meminfo_monitor.py`](adb_meminfo_monitor.py) 脚本，实现基本功能：
- 使用 `adb shell ps -A` 查找目标进程
- 使用 `dumpsys meminfo` 获取内存信息
- 每秒执行一次
- 输出到文本文件

### 遇到的问题 1：编码和路径错误
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb2 in position 13: invalid start byte
命令执行失败: F : \ P r o g r a m   F i l e s \ N e t e a s e \ M u M u \ n x _ m a i n \ a d b . e x e   s h e l l   p s   - A
```

**问题分析**：
1. Windows中文环境输出使用GBK编码，不是UTF-8
2. 路径中包含空格，在命令中需要加引号

**解决方案**：
- 将 `encoding='utf-8'` 改为 `encoding='gbk'`
- 添加 `errors='ignore'` 处理无法解码的字符
- 为ADB路径添加双引号：`'"{ADB_PATH}" shell ps -A'`
- 自动识别MuMu模拟器的ADB路径：`F:\Program Files\Netease\MuMu\nx_main\adb.exe`

### 需求升级 1：Markdown格式输出
用户要求将dumpsys meminfo的信息使用markdown格式化输出。

**实现方案**：
1. 将输出文件扩展名改为 `.md`
2. 添加 [`format_meminfo_to_markdown()`](adb_meminfo_monitor.py:100) 函数
3. 自动识别并格式化：
   - 节标题转为 Markdown 标题 (`###`)
   - 键值对转为加粗格式 (`**key**: value`)
   - 数值数据转为表格
4. 文件头使用 Markdown 格式

### 遇到的问题 2：表头格式识别
```
Pss  Private  Private  SwapPss      Rss     Heap     Heap     Heap
                 Total    Dirty    Clean    Dirty    Total     Size    Alloc     Free
```

**问题描述**：
1. dumpsys meminfo的表头分为两行
   - 第一行：`Pss  Private  Private  SwapPss  Rss  Heap  Heap  Heap`
   - 第二行：`Total    Dirty    Clean    Dirty Total Size  Alloc Free`
   - 应该合并为：`Pss Total`, `Private Dirty`, `Private Clean` 等
2. 数据行中 "Native Heap" 应该作为一个整体，不应该被分开

**解决方案**：
修改 [`format_meminfo_to_markdown()`](adb_meminfo_monitor.py:100) 函数：
1. **两行表头合并**：
   - 检测连续两行是否为表头格式
   - 智能组合两行内容（如 `Pss` + `Total` → `Pss Total`）
   - 生成正确的 Markdown 表格头

2. **多词标签识别**：
   - 查找每行第一个数字的位置
   - 第一个数字之前的所有词作为标签（如 "Native Heap"）
   - 从第一个数字开始的部分作为数据列

3. **表格对齐**：
   - 确保数据列数与表头列数匹配
   - 正确对齐每一列数据

### 关键代码片段

#### 表头合并逻辑
```python
if (re.search(r'\b(Pss|Private|Shared|SwapPss|Rss|Heap)\b', line) and 
    re.search(r'\b(Total|Dirty|Clean|Size|Alloc|Free)\b', next_line)):
    
    # 合并两行表头
    parts1 = line.split()
    parts2 = next_line.split()
    
    headers = []
    j1, j2 = 0, 0
    
    while j1 < len(parts1) or j2 < len(parts2):
        if j1 < len(parts1):
            if j2 < len(parts2) and parts2[j2] not in ['Pss', 'Private', ...]:
                headers.append(f"{parts1[j1]} {parts2[j2]}")
                j2 += 1
            else:
                headers.append(parts1[j1])
            j1 += 1
```

#### 多词标签识别
```python
# 查找第一个数字的位置
first_num_idx = -1
for idx, part in enumerate(data_parts):
    if part.replace(',', '').isdigit():
        first_num_idx = idx
        break

if first_num_idx > 0:
    # 标签是第一个数字之前的所有词
    label = ' '.join(data_parts[:first_num_idx])
    values = data_parts[first_num_idx:]
```

### 最终功能特点

1. **自动进程查找**：找到包含特定关键字的进程完整名称
2. **定时监控**：每秒执行一次内存信息采集
3. **Markdown输出**：格式化为易读的Markdown表格
4. **智能表头处理**：正确合并两行表头
5. **多词标签支持**：保持 "Native Heap" 等标签的完整性
6. **编码兼容**：支持Windows GBK编码
7. **路径处理**：正确处理包含空格的路径
8. **实时写入**：使用 `flush()` 确保数据不丢失
9. **优雅中断**：支持 Ctrl+C 停止，并记录统计信息

### 配置说明

可以修改以下配置：
- `ADB_PATH`：ADB可执行文件路径
- `TARGET_PROCESS_KEYWORD`：要监控的进程关键字
- `OUTPUT_FILE`：输出文件名（自动带时间戳）

### 使用方法

```bash
python adb_meminfo_monitor.py
```

输出示例：
```
============================================================
ADB 内存信息监控工具
============================================================
ADB路径: F:\Program Files\Netease\MuMu\nx_main\adb.exe
目标进程关键字: com.android.webview:sandboxed_process0
输出文件: meminfo_output_20260120_184312.md
============================================================
正在查找包含 'com.android.webview:sandboxed_process0' 的进程...
找到目标进程: com.android.webview:sandboxed_process0:org.chromium.content.app.SandboxedProcessService0:2

开始监控进程: com.android.webview:sandboxed_process0:...
每1秒获取一次内存信息...
按 Ctrl+C 停止监控
```

### 技术要点

1. **subprocess 模块**：执行外部命令
2. **正则表达式**：识别表头和数据格式
3. **文本解析**：智能分析 meminfo 输出结构
4. **Markdown 生成**：动态生成表格和格式化文本
5. **异常处理**：处理编码、进程未找到等异常情况
6. **文件 I/O**：实时写入并刷新缓冲区

### 改进建议

1. 可以添加配置文件支持
2. 可以添加数据可视化（图表）
3. 可以添加内存告警功能
4. 可以支持同时监控多个进程
5. 可以导出为其他格式（JSON、CSV等）

---

**开发时间**：2026-01-20  
**开发工具**：Python 3.10, VS Code  
**测试环境**：Windows 10, MuMu模拟器

---

## 2026-01-20 内存数据可视化开发

### 新需求：数据可视化
用户要求读取 [`meminfo_output_20260120_184312.md`](meminfo_output_20260120_184312.md) 文件，将Native Heap、Dalvik Heap、Dalvik Other等多个内存信息的PSS Total和Private Dirty绘制成曲线图，并生成可显示的网页，支持：
- 内存类型过滤（Native Heap, Dalvik Heap, Dalvik Other等）
- 指标曲线过滤（PSS Total, Private Dirty）
- 从网页选择MD文件
- 使用Python和Windows 10

### 实现方案

创建了三个核心文件：

#### 1. [`meminfo_visualizer.py`](meminfo_visualizer.py:1) - Python解析脚本
**主要功能**：
- **`parse_meminfo_md(file_path)`** 函数：解析MD文件
  - 使用正则表达式提取每个Execution的时间戳
  - 提取Native Heap、Dalvik Heap等14种内存类型的数据
  - 提取PSS Total和Private Dirty两个指标
  - 返回结构化的数据列表

- **`generate_html_viewer()`** 函数：生成HTML查看器
  - 创建完整的交互式HTML页面
  - 集成Chart.js图表库
  - 包含文件选择器和过滤器

**关键代码**：
```python
def parse_meminfo_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则提取Execution信息
    execution_pattern = r'## Execution #(\d+)\s+\*\*Time\*\*: ([^\n]+)'
    executions = re.finditer(execution_pattern, content)
    
    # 提取内存数据
    memory_line_pattern = r'\s+(Native Heap|Dalvik Heap|...)\s+(\d+)\s+(\d+)'
    
    return data
```

#### 2. [`meminfo_viewer.html`](meminfo_viewer.html:1) - 通用HTML查看器 ⭐
**核心功能**：
- **文件选择器**：通过HTML5 File API选择MD文件
- **JavaScript解析器**：在浏览器中解析MD文件内容
- **Chart.js可视化**：绘制交互式线图
- **双重过滤器**：
  - 左侧：内存类型复选框（14种类型）
  - 右侧：指标复选框（PSS Total, Private Dirty）
- **实时更新**：选择/取消选择时图表立即更新
- **统计卡片**：显示总执行次数、内存类型数量、时间范围

**JavaScript核心逻辑**：
```javascript
function parseMemInfoMD(content) {
    const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\n]+)/g;
    const memoryLinePattern = /\s+(Native Heap|Dalvik Heap|...)\s+(\d+)\s+(\d+)/g;
    
    // 解析并返回数据
    return data;
}

function updateChart() {
    // 获取选中的内存类型和指标
    const selectedMemoryTypes = [...];
    const selectedMetrics = [...];
    
    // 生成Chart.js数据集
    datasets.push({
        label: `${memType} - ${metricLabel}`,
        data: data,
        borderColor: COLORS[colorIndex],
        // ...
    });
    
    // 创建/更新图表
    chartInstance = new Chart(ctx, {...});
}
```

#### 3. [`meminfo_demo.html`](meminfo_demo.html:1) - 演示版本
- 预加载 [`meminfo_output_20260120_184312.md`](meminfo_output_20260120_184312.md) 的数据
- 包含完整的4次执行记录
- 立即展示所有功能

### 遇到的问题：正则表达式错误

**问题描述**：
浏览器控制台报错：
```
meminfo_viewer.html:276 Uncaught SyntaxError: Invalid regular expression: missing /
```

**问题分析**：
在生成HTML时，正则表达式被Python写入到HTML中，出现了换行问题：
```javascript
const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^
]+)/g;  // 错误：[^ 后面被换行了
```

应该是：
```javascript
const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\n]+)/g;
```

**解决方案**：
修改 [`meminfo_viewer.html`](meminfo_viewer.html:276) 第276行，将被分割的正则表达式合并为一行：
```python
const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\n]+)/g;
```

### 技术栈

#### 后端（Python）
- **re模块**：正则表达式解析MD文件
- **文件I/O**：读取MD文件和生成HTML文件
- **数据结构**：字典和列表组织内存数据

#### 前端（HTML/JavaScript）
- **HTML5 File API**：浏览器端文件选择和读取
- **Chart.js 4.4.0**：专业图表库
  - 线图（line chart）
  - 交互式工具提示（tooltip）
  - 图例（legend）
  - 响应式设计
- **CSS Grid布局**：现代化的响应式布局
- **渐变背景**：美观的UI设计
- **动态DOM操作**：JavaScript生成复选框和图表

### 支持的内存类型（14种）

1. **Native Heap**：原生堆内存
2. **Dalvik Heap**：Dalvik虚拟机堆内存
3. **Dalvik Other**：Dalvik其他内存
4. **Stack**：栈内存
5. **Ashmem**：匿名共享内存
6. **Other dev**：其他设备内存
7. **.so mmap**：共享库内存映射
8. **.jar mmap**：JAR文件内存映射
9. **.apk mmap**：APK文件内存映射
10. **.ttf mmap**：字体文件内存映射
11. **.dex mmap**：DEX文件内存映射
12. **.oat mmap**：OAT文件内存映射
13. **.art mmap**：ART运行时内存映射
14. **Other mmap**：其他内存映射
15. **Unknown**：未知内存

### 图表功能特性

#### 坐标轴
- **X轴**：执行序号（#1, #2, #3, #4...）
- **Y轴**：内存大小（KB），自动格式化带千分位

#### 交互功能
- **鼠标悬停**：显示详细信息
  - 执行序号和时间戳
  - 内存类型和指标名称
  - 精确的内存值（KB）
- **图例点击**：隐藏/显示特定曲线（Chart.js内置功能）
- **响应式**：自动适应窗口大小

#### 视觉设计
- **彩色线条**：14种颜色区分不同数据系列
- **数据点标记**：每个数据点有圆形标记
- **渐变卡片**：统计信息用紫色渐变卡片显示
- **现代化UI**：圆角、阴影、过渡动画

### 使用流程

#### 方法一：通用查看器
1. 双击打开 [`meminfo_viewer.html`](meminfo_viewer.html:1)
2. 点击"选择文件"按钮
3. 选择任意meminfo MD文件
4. 自动解析并显示图表
5. 使用过滤器自定义显示

#### 方法二：演示版本
1. 直接打开 [`meminfo_demo.html`](meminfo_demo.html:1)
2. 立即查看预加载的数据
3. 测试所有过滤功能

#### 方法三：Python生成
```bash
python meminfo_visualizer.py
```
自动生成 `meminfo_viewer.html`

### 过滤器使用

#### 内存类型过滤器（左侧）
- 默认选中：Native Heap, Dalvik Heap, Dalvik Other
- 可以勾选/取消任意类型
- "Select All" 按钮：全选所有类型
- "Deselect All" 按钮：取消所有选择

#### 指标过滤器（右侧）
- PSS Total：总PSS内存
- Private Dirty：私有脏页内存
- 可以同时选择或单独选择

#### 实时更新
- 改变任何过滤器，图表立即更新
- 至少需要选择1个内存类型和1个指标
- 否则显示提示信息

### 数据格式要求

MD文件应包含如下结构：
```markdown
## Execution #1

**Time**: 2026-01-20 18:43:12

| Pss Total | Private Dirty | ...
| --- | --- | ...
  Native Heap     4426     4308       40      ...
  Dalvik Heap     1956     1356      208      ...
  ...
```

### 关键技术实现

#### 1. 文件读取（前端）
```javascript
document.getElementById('fileInput').addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        parsedData = parseMemInfoMD(content);
        // 更新UI和图表
    };
    reader.readAsText(file);
}
```

#### 2. 正则表达式解析
```javascript
// 提取Execution块
const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\n]+)/g;

// 提取内存数据行
const memoryLinePattern = /\s+(Native Heap|Dalvik Heap|...)\s+(\d+)\s+(\d+)/g;
```

#### 3. Chart.js配置
```javascript
new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            title: { display: true, text: 'Memory Usage Over Time' },
            legend: { display: true, position: 'top' },
            tooltip: { callbacks: {...} }
        },
        scales: {
            y: { beginAtZero: true, title: {...} },
            x: { title: {...} }
        }
    }
});
```

#### 4. 动态过滤器生成
```javascript
Array.from(memoryTypes).sort().forEach(type => {
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = ['Native Heap', 'Dalvik Heap', 'Dalvik Other'].includes(type);
    checkbox.addEventListener('change', updateChart);
    // 添加到DOM
});
```

### 文件清单

1. **[`meminfo_visualizer.py`](meminfo_visualizer.py:1)** - 主Python脚本
2. **[`meminfo_viewer.html`](meminfo_viewer.html:1)** - 通用查看器（推荐使用）
3. **[`meminfo_demo.html`](meminfo_demo.html:1)** - 演示版本
4. **[`README_meminfo_visualizer.md`](README_meminfo_visualizer.md:1)** - 详细使用说明

### 测试结果

✅ 成功读取MD文件  
✅ 正确解析4次Execution数据  
✅ 绘制Native Heap、Dalvik Heap、Dalvik Other曲线  
✅ PSS Total和Private Dirty双指标显示  
✅ 内存类型过滤功能正常  
✅ 指标过滤功能正常  
✅ 选择/取消过滤实时更新图表  
✅ 悬停显示详细信息  
✅ 统计信息正确显示  
✅ Windows 10浏览器完美运行  
✅ 正则表达式错误已修复

### 优点与特色

1. **零依赖部署**：HTML文件可以直接在浏览器打开，无需服务器
2. **纯前端解析**：JavaScript在浏览器中解析MD文件，速度快
3. **响应式设计**：适配不同屏幕尺寸
4. **美观UI**：渐变背景、圆角设计、阴影效果
5. **易于使用**：拖拽或点击选择文件即可
6. **实时交互**：过滤器改变立即更新图表
7. **专业图表**：使用Chart.js专业图表库
8. **完整文档**：中文README详细说明

### 改进建议

1. 可以添加数据导出功能（CSV、JSON）
2. 可以支持多文件对比
3. 可以添加内存趋势分析
4. 可以添加告警阈值设置
5. 可以支持更多图表类型（柱状图、面积图等）
6. 可以添加数据缓存功能
7. 可以支持深色主题切换

---

**开发时间**：2026-01-20  
**开发工具**：Python 3.x, VS Code, Chart.js 4.4.0  
**测试环境**：Windows 10, Chrome/Edge浏览器  
**主要技术**：Python正则表达式、HTML5 File API、JavaScript、Chart.js、CSS Grid

---

## 2026-01-20 配置文件重构

### 新需求：配置外部化
用户要求将 [`adb_meminfo_monitor.py`](adb_meminfo_monitor.py) 中的以下硬编码配置改为从配置文件读取：
- `ADB_PATH`：ADB可执行文件路径
- `TARGET_PROCESS_KEYWORD`：目标进程关键字
- 监控间隔：从硬编码的1秒改为可配置

### 实现方案

#### 1. 创建配置文件
创建了 [`adb_meminfo_config.json`](adb_meminfo_config.json:1) JSON配置文件：

```json
{
  "adb_path": "F:\\Program Files\\Netease\\MuMu\\nx_main\\adb.exe",
  "target_process_keyword": "com.android.webview:sandboxed_process0",
  "monitor_interval_seconds": 1
}
```

**设计要点**：
- 使用JSON格式，简单易读易编辑
- 配置文件放在当前目录，与脚本在同一位置
- 键名使用小写下划线命名法（Python风格）
- Windows路径使用双反斜杠转义

#### 2. 修改Python脚本

**新增导入**：
```python
import json  # 用于解析JSON配置文件
```

**定义配置常量**：
```python
# 配置文件路径
CONFIG_FILE = "adb_meminfo_config.json"

# 默认配置值（当配置文件不存在或读取失败时使用）
DEFAULT_CONFIG = {
    "adb_path": "adb.exe",
    "target_process_keyword": "com.android.webview:sandboxed_process0",
    "monitor_interval_seconds": 1
}

# 全局配置变量（由load_config()函数填充）
ADB_PATH = None
TARGET_PROCESS_KEYWORD = None
MONITOR_INTERVAL = None
```

**新增 [`load_config()`](adb_meminfo_monitor.py:27) 函数**：
```python
def load_config():
    """
    从配置文件加载配置
    
    Returns:
        配置字典
    """
    global ADB_PATH, TARGET_PROCESS_KEYWORD, MONITOR_INTERVAL
    
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
            print(f"已从配置文件加载: {CONFIG_FILE}")
        except Exception as e:
            print(f"警告: 读取配置文件失败，使用默认配置: {e}")
    else:
        print(f"警告: 未找到配置文件 '{CONFIG_FILE}'，使用默认配置")
        print(f"您可以创建 {CONFIG_FILE} 来自定义配置")
    
    ADB_PATH = config["adb_path"]
    TARGET_PROCESS_KEYWORD = config["target_process_keyword"]
    MONITOR_INTERVAL = config["monitor_interval_seconds"]
    
    return config
```

**修改 [`main()`](adb_meminfo_monitor.py:285) 函数**：
1. 在开始时调用 `load_config()` 加载配置
2. 更新输出信息，显示监控间隔
3. 使用 `MONITOR_INTERVAL` 替换硬编码的1秒

```python
def main():
    print("=" * 60)
    print("ADB 内存信息监控工具")
    print("=" * 60)
    
    # 加载配置
    load_config()
    
    print(f"ADB路径: {ADB_PATH}")
    print(f"目标进程关键字: {TARGET_PROCESS_KEYWORD}")
    print(f"监控间隔: {MONITOR_INTERVAL}秒")  # 新增
    print(f"输出文件: {OUTPUT_FILE}")
    print("=" * 60)
    
    # ... 其他代码 ...
    
    print(f"\n开始监控进程: {process_name}")
    print(f"每{MONITOR_INTERVAL}秒获取一次内存信息...")  # 修改
    print(f"输出将保存到: {OUTPUT_FILE}")
    print("按 Ctrl+C 停止监控\n")
    
    # 监控循环中使用配置的间隔
    try:
        while True:
            # ... 获取内存信息 ...
            
            # 等待指定时间间隔
            time.sleep(MONITOR_INTERVAL)  # 修改
    except KeyboardInterrupt:
        # ...
```

### 技术要点

#### 1. JSON配置管理
- **解析**：使用 `json.load()` 读取JSON文件
- **合并**：`config.update(user_config)` 合并用户配置和默认配置
- **容错**：配置文件不存在或解析失败时使用默认配置
- **编码**：使用 `utf-8` 编码读取，确保中文兼容

#### 2. 全局变量管理
```python
global ADB_PATH, TARGET_PROCESS_KEYWORD, MONITOR_INTERVAL
```
- 使用 `global` 关键字在函数中修改全局变量
- 初始化为 `None`，由 `load_config()` 填充
- 其他函数直接使用全局变量

#### 3. 默认配置策略
- 提供合理的默认值
- 配置文件不存在时不报错，只警告
- 允许部分配置（未设置的项使用默认值）

#### 4. 用户友好提示
```python
print(f"已从配置文件加载: {CONFIG_FILE}")
print(f"警告: 未找到配置文件 '{CONFIG_FILE}'，使用默认配置")
print(f"您可以创建 {CONFIG_FILE} 来自定义配置")
```

### 优势与好处

1. **易于配置**：修改配置文件即可，无需修改代码
2. **多环境支持**：不同机器使用不同配置文件
3. **版本控制友好**：配置与代码分离，可以单独管理
4. **用户友好**：提供清晰的错误提示和默认值
5. **向后兼容**：即使没有配置文件也能运行
6. **灵活性高**：可以轻松添加新的配置项

### 使用方法

#### 方法一：使用配置文件（推荐）
1. 创建 [`adb_meminfo_config.json`](adb_meminfo_config.json:1)
2. 修改配置项：
   ```json
   {
     "adb_path": "你的ADB路径",
     "target_process_keyword": "你的进程关键字",
     "monitor_interval_seconds": 2
   }
   ```
3. 运行脚本：`python adb_meminfo_monitor.py`

#### 方法二：使用默认配置
- 直接运行脚本，使用内置默认配置
- 脚本会提示创建配置文件

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `adb_path` | string | `"adb.exe"` | ADB可执行文件的完整路径（Windows使用双反斜杠） |
| `target_process_keyword` | string | `"com.android.webview:sandboxed_process0"` | 要监控的进程名关键字 |
| `monitor_interval_seconds` | number | `1` | 监控间隔（秒），支持小数（如0.5表示500毫秒） |

### 示例配置

#### 配置1：MuMu模拟器，每1秒监控
```json
{
  "adb_path": "F:\\Program Files\\Netease\\MuMu\\nx_main\\adb.exe",
  "target_process_keyword": "com.android.webview:sandboxed_process0",
  "monitor_interval_seconds": 1
}
```

#### 配置2：Genymotion，每2秒监控
```json
{
  "adb_path": "C:\\Program Files\\Genymobile\\Genymotion\\tools\\adb.exe",
  "target_process_keyword": "com.example.myapp",
  "monitor_interval_seconds": 2
}
```

#### 配置3：Android SDK，每0.5秒监控
```json
{
  "adb_path": "C:\\Users\\YourName\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe",
  "target_process_keyword": "com.tencent.mm",
  "monitor_interval_seconds": 0.5
}
```

### 输出示例

**有配置文件时**：
```
============================================================
ADB 内存信息监控工具
============================================================
已从配置文件加载: adb_meminfo_config.json
ADB路径: F:\Program Files\Netease\MuMu\nx_main\adb.exe
目标进程关键字: com.android.webview:sandboxed_process0
监控间隔: 1秒
输出文件: meminfo_output_20260120_202136.md
============================================================
```

**无配置文件时**：
```
============================================================
ADB 内存信息监控工具
============================================================
警告: 未找到配置文件 'adb_meminfo_config.json'，使用默认配置
您可以创建 adb_meminfo_config.json 来自定义配置
ADB路径: adb.exe
目标进程关键字: com.android.webview:sandboxed_process0
监控间隔: 1秒
输出文件: meminfo_output_20260120_202136.md
============================================================
```

### 改进建议

1. **配置验证**：添加配置项有效性检查（如路径存在性、间隔合理性）
2. **配置生成**：提供命令行参数生成配置文件
3. **环境变量支持**：支持从环境变量读取配置
4. **配置文件搜索**：支持多个配置文件位置（当前目录、用户目录等）
5. **配置热重载**：监控配置文件变化，自动重新加载
6. **加密支持**：敏感配置项加密存储

---

**修改时间**：2026-01-20  
**修改文件**：[`adb_meminfo_monitor.py`](adb_meminfo_monitor.py:1)  
**新增文件**：[`adb_meminfo_config.json`](adb_meminfo_config.json:1)  
**开发工具**：Python 3.x, VS Code  
**主要技术**：JSON解析、全局变量管理、默认配置模式

---

## 2026-01-20 正则表达式和内存指标完善

### 问题1：正则表达式转义问题

**问题描述**：
用户提供的内存信息文件格式示例：
```markdown
## Execution #1

**Time**: 2026-01-20 18:43:12
```

用户询问匹配此格式的正则表达式，并发现在生成HTML时，JavaScript中的正则表达式 `/## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\n]+)/g` 被错误转义为 `/## Execution #(\d+)\s+\*\*Time\*\*:\s*([^<换行>]+)/g`，导致 `\n` 字符在HTML/JavaScript中被解释为换行而不是正则表达式的字符类。

**正则表达式说明**：

基本匹配模式：
```regex
## Execution #\d+\s+\*\*Time\*\*:\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}
```

带捕获组版本：
```regex
## Execution #(\d+)\s+\*\*Time\*\*:\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})
```

**模式解析**：
- `## Execution #` - 字面文本
- `\d+` - 执行编号（一个或多个数字）
- `\s+` - 空白字符（换行/空格）
- `\*\*Time\*\*:` - 加粗的"Time"（星号需要转义）
- `\d{4}-\d{2}-\d{2}` - 日期格式 (YYYY-MM-DD)
- `\d{2}:\d{2}:\d{2}` - 时间格式 (HH:MM:SS)

**解决方案**：
修改 [`meminfo_visualizer.py`](meminfo_visualizer.py:336) 第336行，将JavaScript中的 `\n` 改为 `\\n`（双反斜杠转义）：

```javascript
// 修改前（错误）：
const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\n]+)/g;

// 修改后（正确）：
const executionPattern = /## Execution #(\d+)\s+\*\*Time\*\*:\s*([^\\n]+)/g;
```

这样在Python字符串中写入HTML时，`\\n` 会被保留为 `\n` 写入HTML文件，在JavaScript中正确解释为换行符的字符类。

### 问题2：缺失的内存指标

**需求描述**：
用户指出内存数据包含8个指标，但当前只显示了2个：
- ✅ Pss Total（已有）
- ✅ Private Dirty（已有）
- ❌ Private Clean（缺失）
- ❌ SwapPss Dirty（缺失）
- ❌ Rss Total（缺失）
- ❌ Heap Size（缺失）
- ❌ Heap Alloc（缺失）
- ❌ Heap Free（缺失）

**实现方案**：

#### 1. 更新Python解析逻辑

修改 [`meminfo_visualizer.py`](meminfo_visualizer.py:34) 的 `parse_meminfo_md()` 函数：

**原始代码**（只提取2个指标）：
```python
memory_line_pattern = r'\s+(Native Heap|Dalvik Heap|...)\s+(\d+)\s+(\d+)'

memory_items[mem_type] = {
    'pss_total': pss_total,
    'private_dirty': private_dirty
}
```

**更新代码**（提取8个指标）：
```python
memory_line_pattern = r'\s+(Native Heap|Dalvik Heap|...)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+)\s+(\d+)\s+(\d+))?'

memory_items[mem_type] = {
    'pss_total': int(mem_match.group(2)),
    'private_dirty': int(mem_match.group(3)),
    'private_clean': int(mem_match.group(4)),
    'swappss_dirty': int(mem_match.group(5)),
    'rss_total': int(mem_match.group(6)),
    'heap_size': int(mem_match.group(7)) if mem_match.group(7) else None,
    'heap_alloc': int(mem_match.group(8)) if mem_match.group(8) else None,
    'heap_free': int(mem_match.group(9)) if mem_match.group(9) else None
}
```

**关键点**：
- 使用 `(?:...)? ` 非捕获组表示Heap相关字段可选（某些内存类型没有Heap数据）
- Heap字段为None时需要特殊处理

#### 2. 更新JavaScript解析逻辑

修改 [`meminfo_visualizer.py`](meminfo_visualizer.py:354) HTML中的JavaScript解析代码：

**原始代码**（只提取2个指标）：
```javascript
const memoryLinePattern = /\s+(Native Heap|...)\s+(\d+)\s+(\d+)/g;

memory[memType] = {
    pss_total: parseInt(memMatch[2]),
    private_dirty: parseInt(memMatch[3])
};
```

**更新代码**（提取8个指标）：
```javascript
const memoryLinePattern = /\s+(Native Heap|...)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+)\s+(\d+)\s+(\d+))?/g;

memory[memType] = {
    pss_total: parseInt(memMatch[2]),
    private_dirty: parseInt(memMatch[3]),
    private_clean: parseInt(memMatch[4]),
    swappss_dirty: parseInt(memMatch[5]),
    rss_total: parseInt(memMatch[6]),
    heap_size: memMatch[7] ? parseInt(memMatch[7]) : null,
    heap_alloc: memMatch[8] ? parseInt(memMatch[8]) : null,
    heap_free: memMatch[9] ? parseInt(memMatch[9]) : null
};
```

#### 3. 更新指标复选框

修改 [`meminfo_visualizer.py`](meminfo_visualizer.py:429) 的指标过滤器定义：

**原始代码**（只有2个指标）：
```javascript
const metrics = [
    { id: 'pss_total', label: 'PSS Total', checked: true },
    { id: 'private_dirty', label: 'Private Dirty', checked: true }
];
```

**更新代码**（8个指标）：
```javascript
const metrics = [
    { id: 'pss_total', label: 'Pss Total', checked: true },
    { id: 'private_dirty', label: 'Private Dirty', checked: true },
    { id: 'private_clean', label: 'Private Clean', checked: false },
    { id: 'swappss_dirty', label: 'SwapPss Dirty', checked: false },
    { id: 'rss_total', label: 'Rss Total', checked: false },
    { id: 'heap_size', label: 'Heap Size', checked: false },
    { id: 'heap_alloc', label: 'Heap Alloc', checked: false },
    { id: 'heap_free', label: 'Heap Free', checked: false }
];
```

**设计考虑**：
- 默认只勾选 Pss Total 和 Private Dirty（避免图表过于拥挤）
- 用户可以自行勾选其他指标

#### 4. 更新图表渲染逻辑

修改 [`meminfo_visualizer.py`](meminfo_visualizer.py:498) 的图表数据生成代码：

**新增指标标签映射**：
```javascript
const metricLabels = {
    'pss_total': 'Pss Total',
    'private_dirty': 'Private Dirty',
    'private_clean': 'Private Clean',
    'swappss_dirty': 'SwapPss Dirty',
    'rss_total': 'Rss Total',
    'heap_size': 'Heap Size',
    'heap_alloc': 'Heap Alloc',
    'heap_free': 'Heap Free'
};
```

**处理null值**：
```javascript
const data = parsedData.map(item => {
    if (item.memory[memType] && item.memory[memType][metric] !== null && item.memory[memType][metric] !== undefined) {
        return item.memory[memType][metric];
    }
    return null;
});

// 跳过全部为null的数据集
const hasData = data.some(val => val !== null);
if (!hasData) return;
```

**图表配置**：
```javascript
datasets.push({
    label: `${memType} - ${metricLabel}`,
    data: data,
    borderColor: COLORS[colorIndex % COLORS.length],
    backgroundColor: COLORS[colorIndex % COLORS.length] + '20',
    borderWidth: 2,
    fill: false,
    tension: 0.1,
    pointRadius: 4,
    pointHoverRadius: 6,
    spanGaps: false  // 不跨越null值
});
```

### 数据格式说明

内存数据表格包含8列：

| 列序号 | 字段名 | 说明 |
|--------|--------|------|
| 1 | Pss Total | 总PSS内存（包含共享内存的比例部分） |
| 2 | Private Dirty | 私有脏页内存（已修改且仅此进程使用） |
| 3 | Private Clean | 私有干净页内存（未修改且仅此进程使用） |
| 4 | SwapPss Dirty | 交换区PSS脏页内存 |
| 5 | Rss Total | 总常驻内存（物理内存占用） |
| 6 | Heap Size | 堆大小（仅部分内存类型有此字段） |
| 7 | Heap Alloc | 堆已分配大小（仅部分内存类型有此字段） |
| 8 | Heap Free | 堆空闲大小（仅部分内存类型有此字段） |

**示例数据行**：
```
  Native Heap     4426     4308       40      216     4636    21368     2107     7970
```

解析为：
- 类型：Native Heap
- Pss Total: 4426 KB
- Private Dirty: 4308 KB
- Private Clean: 40 KB
- SwapPss Dirty: 216 KB
- Rss Total: 4636 KB
- Heap Size: 21368 KB
- Heap Alloc: 2107 KB
- Heap Free: 7970 KB

### 技术要点

#### 1. 可选捕获组
```regex
(?:\s+(\d+)\s+(\d+)\s+(\d+))?
```
- `(?:...)` - 非捕获组（不创建捕获编号）
- `?` - 整个组可选（出现0次或1次）
- 用于处理Heap字段缺失的情况

#### 2. Null值处理
```javascript
heap_size: memMatch[7] ? parseInt(memMatch[7]) : null
```
- 三元运算符检查匹配组是否存在
- 不存在时赋值为null而不是undefined
- 图表渲染时跳过null值

#### 3. 数据集过滤
```javascript
const hasData = data.some(val => val !== null);
if (!hasData) return;
```
- 检查数据数组是否至少有一个非null值
- 全null数据集不添加到图表（避免空曲线）

#### 4. Chart.js配置
```javascript
spanGaps: false
```
- 不连接null值两侧的数据点
- 保持数据真实性（避免误导性的连线）

### 使用效果

#### 过滤器UI
```
📈 Memory Types
[Select All] [Deselect All]
☑ Native Heap
☑ Dalvik Heap
☐ Dalvik Other
☐ Stack
...

📉 Metrics
☑ Pss Total
☑ Private Dirty
☐ Private Clean
☐ SwapPss Dirty
☐ Rss Total
☐ Heap Size
☐ Heap Alloc
☐ Heap Free
```

#### 图表显示
- 默认显示：Native Heap/Dalvik Heap 的 Pss Total 和 Private Dirty（4条曲线）
- 用户可以勾选其他指标，最多可显示 14种内存类型 × 8个指标 = 112条曲线
- 建议选择 2-5 条曲线以保持图表清晰

### 文件修改清单

修改了 [`meminfo_visualizer.py`](meminfo_visualizer.py) 的以下部分：
1. **行336**：修复JavaScript正则表达式转义 `\n` → `\\n`
2. **行34-52**：Python解析器提取8个指标
3. **行354-378**：JavaScript解析器提取8个指标
4. **行429-437**：指标复选框定义（2个→8个）
5. **行498-530**：图表渲染逻辑（添加指标映射和null处理）

### 测试验证

✅ 正则表达式不再报错  
✅ 成功提取8个内存指标  
✅ 指标过滤器显示8个选项  
✅ Heap字段的null值正确处理  
✅ 图表正确显示选中的指标曲线  
✅ 全null数据集不显示在图表中  
✅ 悬停提示显示正确的指标名称

### 改进建议

1. **批量操作**：添加"选择所有指标"按钮
2. **预设组合**：提供常用指标组合（如"内存基础指标"、"堆分析指标"）
3. **颜色管理**：指标类型使用相近颜色（如所有Heap相关指标用蓝色系）
4. **数据导出**：导出选中指标的CSV数据
5. **对比模式**：同一内存类型的多个指标在同一子图中显示

---

**更新时间**：2026-01-20  
**修改文件**：[`meminfo_visualizer.py`](meminfo_visualizer.py:1)  
**开发工具**：Python 3.x, VS Code, Chart.js 4.4.0  
**主要技术**：正则表达式转义、可选捕获组、null值处理、动态UI生成
