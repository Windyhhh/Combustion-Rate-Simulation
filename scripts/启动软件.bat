@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   燃烧速度仿真软件 - 侧边栏导航版
echo ========================================
echo.
echo 正在启动软件...
echo.

REM 检查是否存在EXE文件
if exist "../build/燃烧速度仿真软件.exe" (
    echo 使用EXE文件启动...
    start "" "../build/燃烧速度仿真软件.exe"
) else (
    echo EXE文件不存在，使用Python脚本启动...
    call conda activate combustion_sim
    cd ../src/gui && python Gui.py
)

echo.
echo 软件已启动！
echo.
pause

