"""
Agent智能风险监控管理系统 - 风险服务
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.database import db, Risk, RiskEvent, EarlyWarning, InternalControl

logger = logging.getLogger(__name__)


class RiskService:
    """风险数据管理服务"""

    @staticmethod
    def get_all_risks() -> List[Dict]:
        """获取所有风险"""
        risks = Risk.query.order_by(Risk.risk_score.desc()).all()
        return [r.to_dict() for r in risks]

    @staticmethod
    def get_risk_by_id(risk_id: int) -> Optional[Dict]:
        """根据ID获取风险"""
        risk = Risk.query.get(risk_id)
        return risk.to_dict() if risk else None

    @staticmethod
    def get_risk_by_code(risk_code: str) -> Optional[Dict]:
        """根据代码获取风险"""
        risk = Risk.query.filter_by(risk_code=risk_code).first()
        return risk.to_dict() if risk else None

    @staticmethod
    def create_risk(data: Dict[str, Any]) -> Dict:
        """创建新风险"""
        risk = Risk(
            risk_code=data.get('risk_code', ''),
            name=data.get('name', ''),
            category=data.get('category', '内部风险'),
            subcategory=data.get('subcategory', ''),
            description=data.get('description', ''),
            possible_consequences=data.get('possible_consequences', ''),
            information_source=data.get('information_source', ''),
            probability=data.get('probability', 3),
            impact=data.get('impact', 3),
            status=data.get('status', 'active'),
            trend=data.get('trend', 'stable'),
            current_response=data.get('current_response', ''),
            suggested_improvement=data.get('suggested_improvement', ''),
            response_type=data.get('response_type', 'reduce'),
            ai_identified=data.get('ai_identified', False),
            ai_assessment_notes=data.get('ai_assessment_notes', ''),
            ai_response_notes=data.get('ai_response_notes', ''),
        )
        risk.calculate_score()

        db.session.add(risk)
        db.session.commit()

        logger.info(f"创建风险: {risk.risk_code} - {risk.name}")
        return risk.to_dict()

    @staticmethod
    def update_risk(risk_id: int, data: Dict[str, Any]) -> Optional[Dict]:
        """更新风险"""
        risk = Risk.query.get(risk_id)
        if not risk:
            return None

        # 更新字段
        updatable_fields = [
            'name', 'category', 'subcategory', 'description',
            'possible_consequences', 'information_source',
            'probability', 'impact', 'status', 'trend',
            'current_response', 'suggested_improvement', 'response_type',
            'ai_assessment_notes', 'ai_response_notes'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(risk, field, data[field])

        # 重新计算得分
        if 'probability' in data or 'impact' in data:
            risk.calculate_score()

        risk.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"更新风险: {risk.risk_code}")
        return risk.to_dict()

    @staticmethod
    def delete_risk(risk_id: int) -> bool:
        """删除风险"""
        risk = Risk.query.get(risk_id)
        if not risk:
            return False

        db.session.delete(risk)
        db.session.commit()

        logger.info(f"删除风险: {risk_id}")
        return True

    @staticmethod
    def bulk_create_risks(risks_data: List[Dict[str, Any]]) -> List[Dict]:
        """批量创建风险"""
        created = []
        for data in risks_data:
            result = RiskService.create_risk(data)
            created.append(result)
        return created

    @staticmethod
    def get_risk_statistics() -> Dict[str, Any]:
        """获取风险统计数据"""
        all_risks = Risk.query.all()

        if not all_risks:
            return {
                "total": 0,
                "by_level": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "by_category": {},
                "by_trend": {"increasing": 0, "stable": 0, "decreasing": 0},
                "average_score": 0,
            }

        total = len(all_risks)
        by_level = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_trend = {"increasing": 0, "stable": 0, "decreasing": 0}
        by_category = {}
        total_score = 0

        for risk in all_risks:
            level = risk.risk_level or 'low'
            by_level[level] = by_level.get(level, 0) + 1

            trend = risk.trend or 'stable'
            by_trend[trend] = by_trend.get(trend, 0) + 1

            cat = risk.subcategory or risk.category or '未分类'
            by_category[cat] = by_category.get(cat, 0) + 1

            total_score += risk.risk_score or 0

        return {
            "total": total,
            "by_level": by_level,
            "by_category": by_category,
            "by_trend": by_trend,
            "average_score": round(total_score / total, 1) if total > 0 else 0,
        }

    @staticmethod
    def get_risk_matrix_data() -> Dict[str, Any]:
        """获取风险矩阵数据"""
        from agents.risk_assessor import RiskAssessorAgent
        agent = RiskAssessorAgent()
        risks = RiskService.get_all_risks()
        return agent.get_matrix_data(risks)

    # ---- 风险事件管理 ----

    @staticmethod
    def get_events(risk_id: int = None) -> List[Dict]:
        """获取风险事件"""
        query = RiskEvent.query
        if risk_id:
            query = query.filter_by(risk_id=risk_id)
        events = query.order_by(RiskEvent.event_date.desc()).all()
        return [e.to_dict() for e in events]

    @staticmethod
    def create_event(data: Dict[str, Any]) -> Dict:
        """创建风险事件"""
        event_date = data.get('event_date')
        if isinstance(event_date, str):
            event_date = datetime.fromisoformat(event_date)

        event = RiskEvent(
            risk_id=data['risk_id'],
            event_name=data['event_name'],
            event_description=data.get('event_description', ''),
            event_date=event_date or datetime.utcnow(),
            severity=data.get('severity', 'medium'),
            financial_impact=data.get('financial_impact'),
            status=data.get('status', 'open'),
        )
        db.session.add(event)
        db.session.commit()
        return event.to_dict()

    # ---- 预警管理 ----

    @staticmethod
    def get_warnings(only_unresolved: bool = False) -> List[Dict]:
        """获取预警列表"""
        query = EarlyWarning.query
        if only_unresolved:
            query = query.filter_by(is_resolved=False)
        warnings = query.order_by(EarlyWarning.created_at.desc()).all()
        return [w.to_dict() for w in warnings]

    @staticmethod
    def create_warning(data: Dict[str, Any]) -> Dict:
        """创建预警"""
        warning = EarlyWarning(
            risk_id=data['risk_id'],
            warning_level=data['warning_level'],
            warning_message=data['warning_message'],
            trigger_reason=data.get('trigger_reason', ''),
        )
        db.session.add(warning)
        db.session.commit()
        return warning.to_dict()

    @staticmethod
    def resolve_warning(warning_id: int) -> Optional[Dict]:
        """解决预警"""
        warning = EarlyWarning.query.get(warning_id)
        if warning:
            warning.is_resolved = True
            db.session.commit()
            return warning.to_dict()
        return None

    # ---- 内部控制管理 ----

    @staticmethod
    def get_all_controls() -> List[Dict]:
        """获取所有内部控制"""
        controls = InternalControl.query.all()
        return [c.to_dict() for c in controls]

    @staticmethod
    def create_control(data: Dict[str, Any]) -> Dict:
        """创建内部控制"""
        control = InternalControl(
            control_code=data['control_code'],
            name=data['name'],
            category=data.get('category', ''),
            description=data.get('description', ''),
            related_risks=data.get('related_risks', ''),
            responsible_dept=data.get('responsible_dept', ''),
            effectiveness=data.get('effectiveness', 'effective'),
        )
        db.session.add(control)
        db.session.commit()
        return control.to_dict()
