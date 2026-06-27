"""
Agent智能风险监控管理系统 - 预警Agent
基于风险评估结果自动触发预警
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EarlyWarningAgent:
    """
    预警Agent

    职责：
    1. 基于预设阈值检测高风险项
    2. 生成红/橙/黄三级预警
    3. 追踪预警历史
    4. 提供预警统计分析
    """

    # 预警阈值配置
    DEFAULT_THRESHOLDS = {
        "red": {
            "risk_score": 15,      # 风险得分 >= 15
            "probability": 4,       # 可能性 >= 4
            "impact": 4,            # 影响 >= 4
            "trend_trigger": True   # 趋势上升时升级预警
        },
        "orange": {
            "risk_score": 10,       # 风险得分 >= 10
            "probability": 3,       # 可能性 >= 3
            "impact": 3,            # 影响 >= 3
        },
        "yellow": {
            "risk_score": 5,        # 风险得分 >= 5
            "probability": 2,       # 可能性 >= 2
        }
    }

    def __init__(self, thresholds: Optional[Dict] = None, llm_service=None):
        from .llm_service import get_llm_service
        self.llm = llm_service or get_llm_service()
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.warning_history: List[Dict] = []

    def check(self, risks: List[Dict[str, Any]],
              previous_assessments: Optional[Dict[str, List[Dict]]] = None) -> List[Dict[str, Any]]:
        """
        执行预警检查

        Args:
            risks: 风险评估列表
            previous_assessments: 历史评估数据（用于趋势分析）

        Returns:
            预警列表
        """
        logger.info(f"EarlyWarningAgent: 开始预警检查，共 {len(risks)} 个风险")
        warnings = []

        for risk in risks:
            warning = self._check_single_risk(risk, previous_assessments)
            if warning:
                warnings.append(warning)

        # 按严重程度排序：红 > 橙 > 黄
        level_order = {"red": 0, "orange": 1, "yellow": 2}
        warnings.sort(key=lambda w: level_order.get(w.get("warning_level", "yellow"), 99))

        # 记录预警历史
        self.warning_history.extend(warnings)

        logger.info(f"EarlyWarningAgent: 发现 {len(warnings)} 个预警 "
                   f"(红:{sum(1 for w in warnings if w['warning_level']=='red')} "
                   f"橙:{sum(1 for w in warnings if w['warning_level']=='orange')} "
                   f"黄:{sum(1 for w in warnings if w['warning_level']=='yellow')})")

        return warnings

    def _check_single_risk(self, risk: Dict[str, Any],
                           history: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        检查单个风险的预警状态

        Returns:
            预警信息字典，如果不需要预警则返回None
        """
        score = risk.get("risk_score", 0)
        prob = risk.get("probability", 0)
        impact = risk.get("impact", 0)
        trend = risk.get("trend", "stable")
        risk_code = risk.get("risk_code", "")
        risk_name = risk.get("name", "")

        warning_level = None
        reasons = []

        # 红色预警检查
        if (score >= self.thresholds["red"]["risk_score"] or
                prob >= self.thresholds["red"]["probability"] or
                impact >= self.thresholds["red"]["impact"]):
            warning_level = "red"
            if score >= 15:
                reasons.append(f"风险得分{score}≥15（P{prob}×I{impact}）")
            if prob >= 4:
                reasons.append(f"发生可能性极高({prob}/5)")
            if impact >= 4:
                reasons.append(f"影响程度极大({impact}/5)")

        # 橙色预警检查
        elif (score >= self.thresholds["orange"]["risk_score"] or
              prob >= self.thresholds["orange"]["probability"]):
            warning_level = "orange"
            if score >= 10:
                reasons.append(f"风险得分{score}≥10")
            if prob >= 3:
                reasons.append(f"发生可能性较高({prob}/5)")

        # 黄色预警检查
        elif score >= self.thresholds["yellow"]["risk_score"]:
            warning_level = "yellow"
            reasons.append(f"风险得分{score}≥5，需持续关注")

        if warning_level is None:
            return None

        # 趋势升级：如果风险趋势为上升，且已经是橙色或黄色，升级一级
        if trend == "increasing" and self.thresholds.get("red", {}).get("trend_trigger", True):
            if warning_level == "orange":
                warning_level = "red"
                reasons.append("风险趋势上升，预警升级为红色")
            elif warning_level == "yellow":
                warning_level = "orange"
                reasons.append("风险趋势上升，预警升级为橙色")

        # 检查历史数据，如果分数比上次增加，增加预警信息
        if history and risk_code in history:
            prev = history[risk_code][-1]  # 最近一次评估
            prev_score = prev.get("risk_score", 0)
            if score > prev_score:
                reasons.append(f"较上次评估上升{score - prev_score}分")

        warning_message = self._generate_warning_message(
            warning_level, risk_name, score, prob, impact, trend
        )

        return {
            "risk_code": risk_code,
            "risk_name": risk_name,
            "warning_level": warning_level,
            "warning_message": warning_message,
            "trigger_reason": "；".join(reasons),
            "risk_score": score,
            "probability": prob,
            "impact": impact,
            "trend": trend,
            "is_read": False,
            "is_resolved": False,
            "created_at": datetime.utcnow().isoformat(),
            "suggested_action": self._suggest_action(warning_level)
        }

    def _generate_warning_message(self, level: str, name: str, score: int,
                                   prob: int, impact: int, trend: str) -> str:
        """生成预警消息文本"""
        level_text = {"red": "🔴 红色预警", "orange": "🟠 橙色预警", "yellow": "🟡 黄色预警"}

        trend_text = {"increasing": "↑上升", "stable": "→稳定", "decreasing": "↓下降"}

        return (f"{level_text.get(level, '预警')}：{name}\n"
                f"风险得分：{score}分（可能性P={prob} × 影响I={impact}）\n"
                f"趋势：{trend_text.get(trend, trend)}\n"
                f"建议：{self._suggest_action(level)}")

    def _suggest_action(self, level: str) -> str:
        """根据预警等级建议行动"""
        actions = {
            "red": "立即启动应急预案，报告董事会和风险管理委员会，24小时内制定应对方案",
            "orange": "48小时内召开风险管理专题会议，制定缓解措施并明确责任人和时间节点",
            "yellow": "纳入月度风险监控清单，持续跟踪风险变化，准备应对预案"
        }
        return actions.get(level, "持续监控")

    def get_warning_statistics(self) -> Dict[str, int]:
        """获取预警统计"""
        stats = {"red": 0, "orange": 0, "yellow": 0, "total": 0, "unresolved": 0}
        for w in self.warning_history:
            stats[w.get("warning_level", "yellow")] = stats.get(w.get("warning_level", "yellow"), 0) + 1
            stats["total"] += 1
            if not w.get("is_resolved", False):
                stats["unresolved"] += 1
        return stats

    def clear_history(self):
        """清除预警历史"""
        self.warning_history = []

    def get_unresolved_warnings(self) -> List[Dict]:
        """获取未解决的预警"""
        return [w for w in self.warning_history if not w.get("is_resolved", False)]

    def resolve_warning(self, risk_code: str):
        """标记预警为已解决"""
        for w in self.warning_history:
            if w.get("risk_code") == risk_code and not w["is_resolved"]:
                w["is_resolved"] = True
                w["resolved_at"] = datetime.utcnow().isoformat()
