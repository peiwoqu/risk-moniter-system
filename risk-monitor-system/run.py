# -*- coding: utf-8 -*-
"""
Agent智能风险监控管理系统 - 启动脚本
"""

import os
import sys
import subprocess


def main():
    """启动系统"""
    print("=" * 60)
    print("Agent智能风险监控管理系统 v1.0")
    print("基于 COSO ERM 2017 & ISO 31000")
    print("=" * 60)

    # 设置UTF-8编码
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'reports'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'uploads'), exist_ok=True)

    # 检查依赖
    try:
        import flask
        import sqlalchemy
    except ImportError:
        print("\nInstalling dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                             os.path.join(base_dir, 'requirements.txt')])

    # 首次运行初始化数据库
    db_path = os.path.join(data_dir, 'risk_monitor.db')
    if not os.path.exists(db_path):
        print("\nFirst run: initializing database...")
        subprocess.run([sys.executable, '-X', 'utf8',
                      os.path.join(base_dir, 'data', 'seed_data.py')])

    print("\nStarting web application...")
    print("URL: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()
