# 快速开始指南

## 第一步：安装依赖

打开命令提示符（CMD）或 PowerShell，执行：

```bash
pip install -r requirements.txt
```

## 第二步：配置参数（可选）

编辑 [`config.ini`](config.ini:1) 配置常用参数：

### 配置 ADB 路径（如果 ADB 未在 PATH 中）
```ini
[adb]
adb_path = C:/你的路径/Android/Sdk/platform-tools/adb.exe
```

### 配置默认包名（简化命令行操作）
```ini
[monitor]
default_package = com.tencent.mm
```

配置后可以直接运行 `python fps_monitor.py` 而无需每次输入包名。

## 第三步：连接 Android 设备

1. 用 USB 线连接 Android 设备到电脑
2. 在手机上启用 **开发者选项** 和 **USB 调试**
3. 验证连接：

```bash
adb devices
```

应该看到：
```
List of devices attached
XXXXXXXX        device
```

## 第四步：运行监控

### 方法一：使用交互式脚本（推荐新手）

双击运行 `run_monitor.bat`，按照提示输入信息即可。

### 方法二：使用命令行

#### 方式 A：直接指定包名
```bash
# 监控微信 60 秒
python fps_monitor.py com.tencent.mm -d 60

# 监控 Chrome 并保存图表
python fps_monitor.py com.android.chrome -d 60 -o chrome_fps.png

# 完整示例：监控并保存图表和数据
python fps_monitor.py com.tencent.mobileqq -d 90 -o qq_fps.png --csv qq_fps.csv
```

#### 方式 B：使用配置文件中的默认包名
```bash
# 先在 config.ini 中设置 default_package
# 然后直接运行
python fps_monitor.py -d 60 -o fps_chart.png
```

## 常见应用包名

| 应用 | 包名 |
|-----|------|
| 微信 | com.tencent.mm |
| QQ | com.tencent.mobileqq |
| Chrome | com.android.chrome |
| 抖音 | com.ss.android.ugc.aweme |
| 王者荣耀 | com.tencent.tmgp.sgame |
| 和平精英 | com.tencent.tmgp.pubgmhd |

## 获取其他应用的包名

### 方法1：查看当前运行的应用
```bash
adb shell dumpsys window | findstr mCurrentFocus
```

### 方法2：列出所有第三方应用
```bash
adb shell pm list packages -3
```

## 问题排查

### 问题：未找到 adb 命令
**解决方法：**
- 在 [`config.ini`](config.ini:1) 中配置 ADB 完整路径
- 或安装 Android SDK 并将 platform-tools 目录添加到系统 PATH

### 问题：FPS 全为 0
**解决方法：** 
- 确保应用正在运行并在前台
- 在应用中进行一些操作（滚动、点击等）
- 检查应用包名是否正确

### 问题：设备连接失败
**解决方法：**
```bash
adb kill-server
adb start-server
adb devices
```

## 输出文件

- **PNG 图表**：包含 FPS 时间序列图和分布直方图
- **CSV 数据**：可用 Excel 打开的原始数据文件

## 更多信息

详细文档请查看 [README.md](README.md)
