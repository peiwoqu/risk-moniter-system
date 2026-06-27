@echo off
chcp 65001 >nul
title Agent智能风险监控管理系统

echo ============================================
echo   Agent智能风险监控管理系统 v2.0
echo ============================================
echo.

cd /d "%~dp0"

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 检查依赖...
pip install -r requirements.txt -q 2>nul
echo       依赖就绪

:: 初始化数据库
echo [2/3] 初始化数据库...
if not exist "data\risk_monitor.db" (
    python -X utf8 data/seed_data.py 2>nul
    echo       数据库已初始化，腾讯案例已加载
) else (
    echo       数据库已存在，跳过初始化
)

:: 启动系统
echo [3/3] 启动系统...
echo.
echo ============================================
echo   系统启动中...
echo   浏览器将自动打开: http://127.0.0.1:5000
echo   按 Ctrl+C 停止服务
echo ============================================
echo.

:: 1秒后自动打开浏览器
start "" http://127.0.0.1:5000

:: 启动 Flask
python -X utf8 run.py

pause
