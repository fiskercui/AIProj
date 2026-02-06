@echo off
chcp 65001 >nul
echo ========================================
echo   Android FPS 监控工具 - 快速测试
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查ADB是否安装
adb version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到ADB工具，请安装Android SDK并添加到PATH
    pause
    exit /b 1
)

echo [✓] Python 已安装
echo [✓] ADB 已安装
echo.

REM 检查依赖
echo 正在检查Python依赖...
pip show matplotlib >nul 2>&1
if errorlevel 1 (
    echo [提示] 未安装matplotlib，正在安装依赖...
    pip install -r requirements.txt
) else (
    echo [✓] Python 依赖已安装
)

echo.
echo 正在检查设备连接...
adb devices
echo.

REM 获取当前运行的应用
echo 获取当前前台应用...
for /f "tokens=*" %%i in ('adb shell dumpsys window ^| findstr mCurrentFocus') do set CURRENT_APP=%%i
echo 当前应用: %CURRENT_APP%
echo.

echo ========================================
echo   请输入要监控的应用包名
echo   (常见应用包名请参考 README.md)
echo ========================================
echo.
echo 示例:
echo   - 微信: com.tencent.mm
echo   - Chrome: com.android.chrome
echo   - QQ: com.tencent.mobileqq
echo.
set /p PACKAGE_NAME=请输入应用包名: 

if "%PACKAGE_NAME%"=="" (
    echo [错误] 包名不能为空
    pause
    exit /b 1
)

echo.
set /p DURATION=监控时长(秒，默认30): 
if "%DURATION%"=="" set DURATION=30

set /p INTERVAL=采样间隔(秒，默认1.0): 
if "%INTERVAL%"=="" set INTERVAL=1.0

echo.
echo ========================================
echo   开始监控
echo ========================================
echo   应用包名: %PACKAGE_NAME%
echo   监控时长: %DURATION% 秒
echo   采样间隔: %INTERVAL% 秒
echo ========================================
echo.

REM 生成带时间戳的文件名
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set OUTPUT_PNG=fps_report_%TIMESTAMP%.png
set OUTPUT_CSV=fps_data_%TIMESTAMP%.csv

REM 运行监控
python fps_monitor.py %PACKAGE_NAME% -d %DURATION% -i %INTERVAL% -o %OUTPUT_PNG% --csv %OUTPUT_CSV%

echo.
echo ========================================
echo   监控完成！
echo ========================================
if exist %OUTPUT_PNG% echo   图表文件: %OUTPUT_PNG%
if exist %OUTPUT_CSV% echo   数据文件: %OUTPUT_CSV%
echo ========================================
echo.

pause
