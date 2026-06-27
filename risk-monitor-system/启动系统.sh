#!/bin/bash
# Agent智能风险监控管理系统 - 一键启动脚本 (macOS/Linux)

echo "============================================"
echo "  Agent智能风险监控管理系统 v2.0"
echo "============================================"

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 安装依赖
echo "[1/3] 检查依赖..."
pip3 install -r requirements.txt -q 2>/dev/null
echo "      依赖就绪"

# 初始化数据库
echo "[2/3] 初始化数据库..."
if [ ! -f "data/risk_monitor.db" ]; then
    python3 data/seed_data.py 2>/dev/null
    echo "      数据库已初始化，腾讯案例已加载"
else
    echo "      数据库已存在，跳过初始化"
fi

# 启动
echo "[3/3] 启动系统..."
echo
echo "============================================"
echo "  浏览器访问: http://127.0.0.1:5000"
echo "  按 Ctrl+C 停止服务"
echo "============================================"

sleep 1
open http://127.0.0.1:5000 2>/dev/null || xdg-open http://127.0.0.1:5000 2>/dev/null

python3 run.py
