#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent智能风险监控管理系统 - Python一键启动器"""
import subprocess, sys, os, time, webbrowser

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("=" * 50)
print("  Agent智能风险监控管理系统 v2.0")
print("=" * 50)

# 1. Check Python
v = sys.version_info
if v.major < 3 or (v.major == 3 and v.minor < 10):
    print("[错误] 需要 Python 3.10+, 当前: " + sys.version)
    input("按回车退出...")
    sys.exit(1)
print(f"[OK] Python {v.major}.{v.minor}.{v.micro}")

# 2. Install dependencies
print("[1/3] 检查依赖...")
try:
    import flask, sqlalchemy, docx, openpyxl
    print("      依赖已就绪")
except ImportError:
    print("      正在安装依赖...")
    r = run(f'"{sys.executable}" -m pip install -r requirements.txt -q')
    if r.returncode != 0:
        print(r.stderr)
        input("安装失败，按回车退出...")
        sys.exit(1)
    print("      安装完成")

# 3. Initialize database
print("[2/3] 初始化数据库...")
db_path = os.path.join(BASE, "data", "risk_monitor.db")
if not os.path.exists(db_path):
    r = run(f'"{sys.executable}" -X utf8 data/seed_data.py')
    print("      数据库已初始化，腾讯案例已加载")
else:
    print("      数据库已存在，跳过初始化")

# 4. Start
print("[3/3] 启动系统...")
print()
print("=" * 50)
print("  浏览器访问: http://127.0.0.1:5000")
print("  关闭此窗口即可停止服务")
print("=" * 50)

# Open browser
time.sleep(0.5)
webbrowser.open("http://127.0.0.1:5000")

# Start Flask
from app import app
app.run(debug=False, host="127.0.0.1", port=5000)
