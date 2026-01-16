@echo off
echo 正在编译项目...

REM 设置 Visual Studio 环境（根据你的 VS 版本调整路径）
REM VS 2022
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" 2>nul
if errorlevel 1 (
    REM VS 2019
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" 2>nul
)
if errorlevel 1 (
    echo 找不到 Visual Studio，请确保已安装 Visual Studio
    pause
    exit /b 1
)

REM 创建输出目录
if not exist "bin" mkdir bin

REM 编译
cl /EHsc /std:c++17 /O2 /Iexternal /Isrc src\main.cpp /Fe:bin\path_tracer.exe

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