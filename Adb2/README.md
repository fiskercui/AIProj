# Android FPS 监控工具

这是一个用于监控 Android 应用帧率（FPS）的 Python 工具，可以通过 ADB 命令实时采集应用的帧率数据，并生成可视化图表。

## 功能特性

- ✅ 实时监控 Android 应用的帧率
- ✅ 支持自定义监控时长和采样间隔
- ✅ 生成详细的 FPS 时间序列图表
- ✅ 生成 FPS 分布直方图
- ✅ 显示统计信息（平均值、最大值、最小值、标准差）
- ✅ 支持导出 CSV 数据文件
- ✅ 支持保存图表为图片文件（PNG/JPG/PDF）
- ✅ 中文界面支持
- ✅ **支持配置文件自定义 ADB 路径和其他参数**

## 环境要求

### 1. 系统要求
- Windows 10
- Python 3.7+

### 2. Android SDK
确保已安装 Android SDK 并将 ADB 工具添加到系统 PATH 环境变量中。

**验证 ADB 安装：**
```bash
adb version
```

### 3. Python 依赖库
- matplotlib >= 3.5.0
- numpy >= 1.21.0

## 安装步骤

### 1. 克隆或下载项目
```bash
cd e:/AIProj/Adb2
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

或者手动安装：
```bash
pip install matplotlib numpy
```

### 3. 配置 ADB 路径（可选）

如果 ADB 未添加到系统 PATH，需要配置 [`config.ini`](config.ini:1) 文件：

```ini
[adb]
# 修改为你的 ADB 完整路径
adb_path = C:/Users/YourName/AppData/Local/Android/Sdk/platform-tools/adb.exe
```

如果 ADB 已在 PATH 中，保持默认 `adb_path = adb` 即可。

### 4. 连接 Android 设备
- 通过 USB 连接 Android 设备到电脑
- 在 Android 设备上启用 **开发者选项** 和 **USB 调试**
- 验证连接：
```bash
adb devices
```

应该看到类似输出：
```
List of devices attached
XXXXXXXX        device
```

## 使用方法

### 基本用法

```bash
python fps_monitor.py <应用包名> [选项]
```

### 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| package | - | 应用包名（可选，未指定则从配置文件读取） | 从配置文件读取 |
| --package-name | -p | 应用包名（备选方式） | 从配置文件读取 |
| --duration | -d | 监控持续时间（秒） | 从配置文件读取或 60 |
| --interval | -i | 采样间隔（秒） | 从配置文件读取或 1.0 |
| --output | -o | 图表输出文件路径（支持 .png/.jpg/.pdf） | 不指定则显示图表 |
| --csv | - | CSV 数据文件保存路径 | 不指定则不保存 |
| --config | - | 配置文件路径 | config.ini |

### 使用示例

#### 1. 监控微信 60 秒并显示图表
```bash
python fps_monitor.py com.tencent.mm -d 60
```

#### 2. 监控 Chrome 浏览器 120 秒，每 0.5 秒采样一次
```bash
python fps_monitor.py com.android.chrome -d 120 -i 0.5
```

#### 3. 监控应用并保存图表为图片
```bash
python fps_monitor.py com.example.app -d 60 -o fps_chart.png
```

#### 4. 监控应用并同时保存图表和 CSV 数据
```bash
python fps_monitor.py com.tencent.mobileqq -d 90 -o fps_report.png --csv fps_data.csv
```

#### 5. 高频采样（每 0.2 秒一次）
```bash
python fps_monitor.py com.android.settings -d 30 -i 0.2
```

#### 6. 使用自定义配置文件
```bash
python fps_monitor.py com.example.app --config custom_config.ini
```

#### 7. 使用配置文件中的默认包名
首先在 [`config.ini`](config.ini:1) 中设置默认包名：
```ini
[monitor]
default_package = com.tencent.mm
```

然后直接运行（无需指定包名）：
```bash
python fps_monitor.py -d 60
```

或使用 `--package-name` 参数：
```bash
python fps_monitor.py --package-name com.example.app -d 60
```

## 如何获取应用包名

### 方法1：查看当前运行的应用
```bash
adb shell dumpsys window | findstr mCurrentFocus
```

### 方法2：列出所有已安装的应用
```bash
adb shell pm list packages
```

### 方法3：列出第三方应用
```bash
adb shell pm list packages -3
```

### 常见应用包名示例
| 应用名称 | 包名 |
|---------|------|
| 微信 | com.tencent.mm |
| QQ | com.tencent.mobileqq |
| 抖音 | com.ss.android.ugc.aweme |
| Chrome | com.android.chrome |
| 王者荣耀 | com.tencent.tmgp.sgame |
| 和平精英 | com.tencent.tmgp.pubgmhd |
| 原神 | com.miHoYo.Yuanshen |

## 输出说明

### 1. 实时监控输出
运行时会在控制台显示实时监控信息：
```
开始监控应用: com.tencent.mm
监控时长: 60秒
采样间隔: 1.0秒
==================================================
[  1] 时间:    1.0s | FPS:  58.23 | 进度:   1.7%
[  2] 时间:    2.0s | FPS:  59.87 | 进度:   3.3%
[  3] 时间:    3.1s | FPS:  60.12 | 进度:   5.1%
...
==================================================
✓ 数据采集完成，共采集 60 个数据点
```

### 2. 图表输出
生成两个图表：

**上图：FPS 时间序列图**
- 蓝色曲线显示 FPS 随时间变化
- 绿色虚线标记 60 FPS 基准线
- 橙色虚线标记 30 FPS 基准线
- 显示统计信息（平均值、最大值、最小值、标准差）

**下图：FPS 分布直方图**
- 显示 FPS 值的分布情况
- 帮助识别应用性能稳定性

### 3. CSV 数据格式
如果指定了 `--csv` 参数，会生成如下格式的 CSV 文件：
```csv
Time(s),FPS
0.00,58.23
1.01,59.87
2.02,60.12
...
```

## 配置文件说明

项目包含 [`config.ini`](config.ini:1) 配置文件，可以自定义各种参数：

### ADB 设置
```ini
[adb]
# ADB 命令路径（可以是命令名或完整路径）
adb_path = adb
# 或使用完整路径：
# adb_path = C:/Users/YourName/AppData/Local/Android/Sdk/platform-tools/adb.exe

# ADB 命令超时时间（秒）
command_timeout = 5
```

### 监控参数
```ini
[monitor]
# 默认应用包名（留空则必须通过命令行指定）
default_package = com.tencent.mm

# 默认监控持续时间（秒）
default_duration = 60

# 默认采样间隔（秒）
default_interval = 1.0
```

### 图表设置
```ini
[chart]
# 图表尺寸（英寸）
figure_width = 12
figure_height = 8

# 图表 DPI（分辨率）
dpi = 300

# 基准线颜色
fps_60_color = green
fps_30_color = orange

# 中文字体
font_family = Microsoft YaHei
```

### 数据过滤
```ini
[filter]
# 帧时间过滤范围（毫秒）
min_frame_time = 1
max_frame_time = 100

# 是否自动过滤 FPS 为 0 的数据点
filter_zero_fps = true
```

## 常见问题

### 1. "未找到 adb 命令"
**解决方法：**
- 确保已安装 Android SDK
- 在 [`config.ini`](config.ini:1) 中配置 ADB 完整路径：
  ```ini
  [adb]
  adb_path = C:/Users/你的用户名/AppData/Local/Android/Sdk/platform-tools/adb.exe
  ```
- 或将 ADB 工具路径添加到系统 PATH 环境变量

### 2. "未找到已连接的设备"
**解决方法：**
- 检查 USB 连接
- 确保手机已开启 USB 调试模式
- 重新授权 USB 调试（拔插 USB 线）
- 尝试命令：`adb kill-server` 然后 `adb start-server`

### 3. FPS 数据全为 0
**可能原因：**
- 应用包名不正确
- 应用未在前台运行
- 应用没有图形渲染活动
- 需要 root 权限（部分设备）

**解决方法：**
- 确认应用包名正确
- 确保应用在监控期间处于活动状态
- 在应用中进行一些操作（滚动、动画等）

### 4. 中文乱码
脚本已配置中文字体支持（微软雅黑、黑体），如果仍有乱码：
- 确保系统已安装中文字体
- 或修改 [`fps_monitor.py`](fps_monitor.py:20) 中的字体设置

### 5. 采样间隔太短导致数据不准确
**建议：**
- 对于普通应用，使用 0.5-1.0 秒的采样间隔
- 对于游戏或高帧率应用，可以使用 0.2-0.5 秒
- 间隔太短可能导致 ADB 命令执行不完整

## 技术原理

该工具使用以下 ADB 命令获取帧率数据：

### 主要方法：dumpsys gfxinfo
```bash
adb shell dumpsys gfxinfo <package_name> framestats
```
- 获取应用的图形渲染帧统计信息
- 解析帧时间数据计算 FPS
- 适用于大部分应用

### 备用方法：SurfaceFlinger
```bash
adb shell dumpsys SurfaceFlinger --latency <package_name>
```
- 获取 Surface 层的帧延迟数据
- 当主要方法失败时自动切换
- 需要较新的 Android 版本

## 高级用法

### 1. 监控游戏性能测试
```bash
# 监控 5 分钟，每 0.5 秒采样，保存完整数据
python fps_monitor.py com.tencent.tmgp.sgame -d 300 -i 0.5 -o game_fps.png --csv game_fps.csv
```

### 2. 批量测试不同应用
创建批处理脚本 `test_apps.bat`：
```batch
@echo off
python fps_monitor.py com.tencent.mm -d 60 -o wechat_fps.png --csv wechat_fps.csv
python fps_monitor.py com.android.chrome -d 60 -o chrome_fps.png --csv chrome_fps.csv
python fps_monitor.py com.tencent.mobileqq -d 60 -o qq_fps.png --csv qq_fps.csv
echo All tests completed!
```

### 3. 中断监控
如果需要提前停止监控，按 `Ctrl+C`，程序会保存已采集的数据。

## 输出示例

运行 `python fps_monitor.py com.android.chrome -d 60 -o fps_chart.png` 后：

```
✓ 找到 1 个设备

开始监控应用: com.android.chrome
监控时长: 60秒
采样间隔: 1.0秒
==================================================
[  1] 时间:    1.0s | FPS:  59.23 | 进度:   1.7%
[  2] 时间:    2.0s | FPS:  60.15 | 进度:   3.3%
...
[ 60] 时间:   60.0s | FPS:  58.92 | 进度: 100.0%
==================================================
✓ 数据采集完成，共采集 60 个数据点
✓ 图表已保存到: fps_chart.png
```

## 项目结构

```
Adb2/
├── fps_monitor.py      # 主程序脚本
├── config.ini          # 配置文件
├── requirements.txt    # Python 依赖
├── run_monitor.bat     # Windows 交互式批处理脚本
├── README.md          # 使用说明（本文件）
├── QUICKSTART.md      # 快速开始指南
└── .gitignore         # Git 忽略文件
```

## 许可证

本项目供学习和个人使用。

## 贡献

欢迎提交问题和改进建议！

## 更新日志

### v1.0.0 (2026-01-21)
- 初始版本发布
- 支持基本的 FPS 监控功能
- 支持图表绘制和数据导出
- 中文界面支持
