@echo off
chcp 65001 >nul
echo ========================================
echo 燃烧速度仿真软件 v2.0 - 打包脚本
echo ========================================
echo.

echo [1/4] 清理旧的打包文件...
if exist ../build rmdir /s /q ../build
if exist ../dist rmdir /s /q ../dist
echo 清理完成！
echo.

echo [2/4] 激活conda环境...
call C:\ProgramData\anaconda3\Scripts\activate.bat combustion_sim
if errorlevel 1 (
    echo 错误：无法激活conda环境
    echo 请确保已安装conda环境：combustion_sim
    pause
    exit /b 1
)
echo 环境激活成功！
echo.

echo [3/4] 开始打包（这可能需要2-5分钟）...
cd ../config && pyinstaller 燃烧速度仿真软件.spec && cd ../scripts
if errorlevel 1 (
    echo.
    echo ========================================
    echo 错误：打包失败
    echo ========================================
    pause
    exit /b 1
)
echo.

echo [4/4] 打包完成！
echo.
echo ========================================
echo ✅ 打包成功！
echo ========================================
echo.
echo 可执行文件位置: ../build/燃烧速度仿真软件.exe
echo.
echo 请测试以下功能：
echo   1. 双击运行程序
echo   2. 步骤二：双击化学名称列选择组分
echo   3. 步骤二：序号自动更新
echo   4. 步骤四：批量添加工况
echo   5. 步骤四：智能删除功能
echo   6. 步骤五：运行计算
echo.
pause

