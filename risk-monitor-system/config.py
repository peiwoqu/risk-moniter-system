"""
Agent智能风险监控管理系统 - 配置文件
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置"""
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'risk-monitor-secret-key-2025')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "data", "risk_monitor.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI Agent 配置
    AI_MODEL = os.environ.get('AI_MODEL', 'claude-opus-4-8')
    AI_TEMPERATURE = 0.3

    # 风险评估参数
    RISK_MATRIX_LEVELS = {
        'critical': {'range': (15, 25), 'label': '重大风险', 'color': '#DC3545'},
        'high': {'range': (10, 14), 'label': '高度关注风险', 'color': '#FD7E14'},
        'medium': {'range': (5, 9), 'label': '一般风险', 'color': '#FFC107'},
        'low': {'range': (1, 4), 'label': '低风险', 'color': '#28A745'},
    }

    # 预警阈值
    EARLY_WARNING_THRESHOLD = {
        'probability_trigger': 3,  # 可能性 >= 3 触发预警
        'impact_trigger': 4,       # 影响程度 >= 4 触发预警
        'risk_score_trigger': 10,  # 风险得分 >= 10 触发预警
    }

    # 报告生成配置
    REPORT_TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates', 'reports')
