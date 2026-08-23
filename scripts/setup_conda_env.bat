@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   燃烧速度仿真软件 - Conda环境配置
echo ========================================
echo.

echo 正在检查Conda环境...
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Conda，请先安装Anaconda或Miniconda
    echo 下载地址: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
) else (
    echo ✅ Conda环境检测成功
)

echo.
echo 正在创建虚拟环境 'combustion_sim'...
conda create -n combustion_sim python=3.9 -y
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
) else (
    echo ✅ 虚拟环境创建成功
)

echo.
echo 正在激活虚拟环境...
call conda activate combustion_sim
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
) else (
    echo ✅ 虚拟环境激活成功
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
) else (
    echo ✅ 依赖包安装成功
)

echo.
echo 正在安装打包工具...
pip install pyinstaller auto-py-to-exe
if %errorlevel% neq 0 (
    echo ❌ 打包工具安装失败
    pause
    exit /b 1
) else (
    echo ✅ 打包工具安装成功
)

echo.
echo ========================================
echo 环境配置完成！
echo ========================================
echo.
echo 使用方法：
echo 1. 激活环境：conda activate combustion_sim
echo 2. 运行软件：python Gui_Main.py 或 python Gui.py
echo 3. 打包软件：python package_with_conda.py
echo.
echo 注意：每次使用前请先激活虚拟环境
echo.
pause
