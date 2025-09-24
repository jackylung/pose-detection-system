@echo off
REM 姿勢檢測系統打包腳本
REM 用於在Windows上創建可執行文件

chcp 65001 >nul

echo ================================
echo 姿勢檢測系統打包工具
echo ================================

REM 檢查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: 未找到Python。請先安裝Python 3.10或更高版本。
    echo 請確保Python已添加到系統PATH環境變量中。
    pause
    exit /b 1
)

echo 發現Python環境...

REM 安裝PyInstaller（如果尚未安裝）
echo 檢查PyInstaller...
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安裝PyInstaller...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo 錯誤: 無法安裝PyInstaller
        pause
        exit /b 1
    )
)

echo PyInstaller已準備就緒

REM 運行打包腳本
echo 正在構建可執行文件...
python build_executable.py

if %errorlevel% neq 0 (
    echo 打包過程中發生錯誤
    pause
    exit /b 1
)

echo.
echo ================================
echo 打包完成！
echo.
echo 可執行文件位置: dist\姿勢檢測系統.exe
echo 分發包位置: 姿勢檢測系統_分發包\
echo.
echo 請將分發包複製到目標電腦使用
echo ================================

pause