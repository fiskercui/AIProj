@echo off
echo 正在编译项目...

REM 检查 g++ 是否可用
where g++ >nul 2>nul
if errorlevel 1 (
    echo 找不到 g++ 编译器，请确保已安装 MinGW
    pause
    exit /b 1
)

REM 创建输出目录
if not exist "bin" mkdir bin

REM 编译
g++ -std=c++17 -O2 -Iexternal -Isrc src/main.cpp -o bin/path_tracer.exe

if errorlevel 1 (
    echo 编译失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 编译成功！
echo ========================================
echo.
echo 运行程序：
bin\path_tracer.exe

pause