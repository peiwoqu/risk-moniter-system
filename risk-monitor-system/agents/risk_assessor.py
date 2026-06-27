# -*- coding: utf-8 -*-
"""
Agent智能风险监控管理系统 - 风险评估Agent
对已识别的风险进行量化评估（PxI 风险矩阵）
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskAssessorAgent:
    """风险评估Agent - PxI评估、等级判定、矩阵数据生成"""

    PROBABILITY_LEVELS = {
        1: "极低 - 几乎不可能发生（<5%）",
        2: "低 - 不太可能发生（5%-25%）",
        3: "中等 - 可能发生（25%-50%）",
        4: "高 - 很可能发生（50%-75%）",
        5: "极高 - 几乎肯定会发生（>75%）"
    }

    IMPACT_LEVELS = {
        1: "极小 - 财务影响<1亿元，无品牌影响",
        2: "小 - 财务影响1-10亿元，品牌影响有限",
        3: "中等 - 财务影响10-50亿元，品牌短期受损",
        4: "大 - 财务影响50-200亿元，品牌严重受损",
        5: "极大 - 财务影响>200亿元，威胁企业生存"
    }

    def __init__(self, llm_service=None):
        from .llm_service import get_llm_service
        self.llm = llm_service or get_llm_service()
        self.assessment_history: Dict[str, List[Dict]] = {}

    def assess(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行风险评估"""
        logger.info(f"RiskAssessorAgent: assessing {len(risks)} risks")
        assessed = self._rule_based_assess(risks)

        try:
            user_msg = f"请评估以下风险列表：\n{json.dumps(risks, ensure_ascii=False, indent=2)}"
            llm_response = self.llm.chat(self._build_system_prompt(), user_msg)
            llm_assessed = self._parse_response(llm_response)
            if llm_assessed:
                assessed = self._merge_assessments(assessed, llm_assessed)
        except Exception as e:
            logger.warning(f"LLM assessment failed, using rule engine: {e}")

        for risk in assessed:
            risk["risk_score"] = risk.get("probability", 3) * risk.get("impact", 3)
            risk["risk_level"] = self._calculate_level(risk["risk_score"])
            risk["assessed_at"] = datetime.utcnow().isoformat()

        self._record_history(assessed)
        logger.info("RiskAssessorAgent: assessment complete")
        return assessed

    def _build_system_prompt(self) -> str:
        return """你是一个企业风险评估专家。请对给定的风险列表进行评估。
对每个风险评估可能性和影响程度（均采用1-5分制）：
可能性: 1=极低 2=低 3=中等 4=高 5=极高
影响程度: 1=极小 2=小 3=中等 4=大 5=极大
同时评估风险趋势：increasing/stable/decreasing
输出JSON格式，在原风险数据基础上增加 probability, impact, trend 字段。"""

    def _rule_based_assess(self, risks: List[Dict]) -> List[Dict]:
        """基于规则的快速评估"""
        for risk in risks:
            if "probability" not in risk or risk.get("probability") is None:
                risk["probability"] = self._estimate_probability(risk)
            if "impact" not in risk or risk.get("impact") is None:
                risk["impact"] = self._estimate_impact(risk)
            if "trend" not in risk or not risk.get("trend"):
                risk["trend"] = self._estimate_trend(risk)
        return risks

    def _estimate_probability(self, risk: Dict) -> int:
        desc = (risk.get("description", "") + risk.get("name", "")).lower()
        high_kw = ["持续", "频繁", "已发生", "多次", "严峻", "激烈", "不断", "目前", "当前", "正在"]
        med_kw = ["面临", "存在", "可能", "需要关注", "压力"]
        low_kw = ["潜在", "远期", "未来可能", "尚未", "如果"]
        if any(kw in desc for kw in high_kw):
            return 4
        if any(kw in desc for kw in low_kw):
            return 2
        if any(kw in desc for kw in med_kw):
            return 3
        return 3

    def _estimate_impact(self, risk: Dict) -> int:
        desc = risk.get("description", "") + risk.get("name", "")
        if any(kw in desc for kw in ["生存", "生死", "颠覆", "致命"]):
            return 5
        if any(kw in desc for kw in ["重大", "严重", "核心", "关键", "系统", "全局"]):
            return 4
        if any(kw in desc for kw in ["明显", "压力", "挑战", "下降", "损失"]):
            return 3
        if any(kw in desc for kw in ["有限", "可控", "轻微", "较小", "次要"]):
            return 2
        return 3

    def _estimate_trend(self, risk: Dict) -> str:
        desc = (risk.get("description", "") + risk.get("name", "")).lower()
        inc_kw = ["加剧", "上升", "恶化", "增加", "不断", "越来越", "日益", "首次超过", "持续扩大"]
        dec_kw = ["缓和", "改善", "下降", "缓解", "减弱"]
        if any(kw in desc for kw in inc_kw):
            return "increasing"
        if any(kw in desc for kw in dec_kw):
            return "decreasing"
        return "stable"

    def _calculate_level(self, score: int) -> str:
        if score >= 15:
            return "critical"
        elif score >= 10:
            return "high"
        elif score >= 5:
            return "medium"
        return "low"

    def _record_history(self, risks: List[Dict]):
        timestamp = datetime.utcnow().isoformat()[:10]
        for risk in risks:
            code = risk.get("risk_code", "")
            if code not in self.assessment_history:
                self.assessment_history[code] = []
            self.assessment_history[code].append({
                "date": timestamp,
                "probability": risk.get("probability"),
                "impact": risk.get("impact"),
                "risk_score": risk.get("risk_score"),
                "risk_level": risk.get("risk_level")
            })

    def get_matrix_data(self, risks: List[Dict]) -> Dict[str, Any]:
        """生成风险矩阵可视化数据"""
        matrix = [[None for _ in range(5)] for _ in range(5)]
        for risk in risks:
            p = risk.get("probability", 3) - 1
            i = risk.get("impact", 3) - 1
            if 0 <= p < 5 and 0 <= i < 5:
                if matrix[4 - i][p] is None:
                    matrix[4 - i][p] = []
                matrix[4 - i][p].append({
                    "risk_code": risk.get("risk_code", ""),
                    "name": risk.get("name", ""),
                    "risk_score": risk.get("risk_score", 0),
                    "risk_level": risk.get("risk_level", "low")
                })
        return {
            "matrix": matrix,
            "x_labels": ["极低(1)", "低(2)", "中等(3)", "高(4)", "极高(5)"],
            "y_labels": ["极大(5)", "大(4)", "中等(3)", "小(2)", "极小(1)"],
            "levels": {
                "critical": {"min": 15, "color": "#DC3545", "label": "重大风险"},
                "high": {"min": 10, "color": "#FD7E14", "label": "高度关注风险"},
                "medium": {"min": 5, "color": "#FFC107", "label": "一般风险"},
                "low": {"min": 1, "color": "#28A745", "label": "低风险"}
            }
        }

    def get_statistics(self, risks: List[Dict]) -> Dict[str, Any]:
        """生成风险评估统计数据"""
        total = len(risks)
        if total == 0:
            return {"total": 0}
        by_level = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_trend = {"increasing": 0, "stable": 0, "decreasing": 0}
        by_category = {}
        total_score = 0
        for risk in risks:
            level = risk.get("risk_level", "low")
            by_level[level] = by_level.get(level, 0) + 1
            trend = risk.get("trend", "stable")
            by_trend[trend] = by_trend.get(trend, 0) + 1
            cat = risk.get("subcategory", risk.get("category", "未分类"))
            by_category[cat] = by_category.get(cat, 0) + 1
            total_score += risk.get("risk_score", 0)
        return {
            "total": total,
            "by_level": by_level,
            "by_category": by_category,
            "by_trend": by_trend,
            "average_score": round(total_score / total, 1)
        }

    def _parse_response(self, response: str) -> Optional[List[Dict]]:
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            import re
            match = re.search(r'\[[\s\S]*\]', response)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return None

    def _merge_assessments(self, rule_based: List[Dict], llm_based: List[Dict]) -> List[Dict]:
        for i, risk in enumerate(rule_based):
            if i < len(llm_based) and isinstance(llm_based[i], dict):
                llm = llm_based[i]
                risk["probability"] = llm.get("probability", risk.get("probability", 3))
                risk["impact"] = llm.get("impact", risk.get("impact", 3))
                risk["trend"] = llm.get("trend", risk.get("trend", "stable"))
        return rule_based
