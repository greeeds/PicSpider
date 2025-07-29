@echo off
chcp 65001 >nul
title PicSpider 写真爬取展示系统

echo.
echo ========================================
echo   PicSpider 写真爬取展示系统
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查是否首次运行
if not exist "config.json" (
    echo 检测到首次运行，正在安装依赖...
    python install.py
    if errorlevel 1 (
        echo 安装失败，请检查网络连接或手动安装依赖
        pause
        exit /b 1
    )
)

REM 启动应用
echo 启动PicSpider...
python run.py

pause
