# -*- coding: utf-8 -*-
"""M3: 内控机制服务 - 治理结构、内控制度、内控-风险关联"""
import json, logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from models.database import (db, Enterprise, InternalControl,
    GovernanceStructure, ControlRiskMapping, Risk)

logger = logging.getLogger(__name__)

class ControlService:
    """M3 内控机制业务逻辑"""

    # ---- 治理结构 ----
    @staticmethod
    def get_governance(enterprise_id: int) -> Optional[Dict]:
        gs = GovernanceStructure.query.filter_by(enterprise_id=enterprise_id).first()
        return gs.to_dict() if gs else None

    @staticmethod
    def save_governance(enterprise_id: int, data: Dict) -> Dict:
        gs = GovernanceStructure.query.filter_by(enterprise_id=enterprise_id).first()
        if not gs:
            gs = GovernanceStructure(enterprise_id=enterprise_id)
            db.session.add(gs)
        gs.structure_type = data.get('structure_type', gs.structure_type)
        gs.board_size = data.get('board_size', gs.board_size)
        gs.independent_directors = data.get('independent_directors', gs.independent_directors)
        gs.committees = data.get('committees', gs.committees)
        gs.description = data.get('description', gs.description)
        gs.org_chart_text = data.get('org_chart_text', gs.org_chart_text)
        gs.updated_at = datetime.utcnow()
        db.session.commit()
        return gs.to_dict()

    # ---- 内控制度 CRUD ----
    @staticmethod
    def get_controls(enterprise_id: int) -> List[Dict]:
        return [c.to_dict() for c in InternalControl.query.filter_by(
            enterprise_id=enterprise_id).order_by(InternalControl.control_code).all()]

    @staticmethod
    def create_control(enterprise_id: int, data: Dict) -> Dict:
        ctrl = InternalControl(enterprise_id=enterprise_id,
            control_code=data.get('control_code',''), name=data.get('name',''),
            category=data.get('category','管理制度'),
            description=data.get('description',''),
            related_risks=data.get('related_risks',''),
            responsible_dept=data.get('responsible_dept',''),
            effectiveness=data.get('effectiveness','effective'))
        db.session.add(ctrl); db.session.commit()
        return ctrl.to_dict()

    @staticmethod
    def update_control(control_id: int, data: Dict) -> Optional[Dict]:
        ctrl = InternalControl.query.get(control_id)
        if not ctrl: return None
        for f in ['control_code','name','category','description','related_risks','responsible_dept','effectiveness']:
            if f in data: setattr(ctrl, f, data[f])
        ctrl.last_tested = datetime.utcnow() if data.get('effectiveness') else ctrl.last_tested
        db.session.commit()
        return ctrl.to_dict()

    @staticmethod
    def delete_control(control_id: int) -> bool:
        ctrl = InternalControl.query.get(control_id)
        if not ctrl: return False
        ControlRiskMapping.query.filter_by(control_id=control_id).delete()
        db.session.delete(ctrl); db.session.commit()
        return True

    # ---- 内控-风险关联 ----
    @staticmethod
    def get_mappings(enterprise_id: int) -> List[Dict]:
        return [m.to_dict() for m in ControlRiskMapping.query.filter_by(
            enterprise_id=enterprise_id).all()]

    @staticmethod
    def create_mapping(enterprise_id: int, data: Dict) -> Dict:
        m = ControlRiskMapping(enterprise_id=enterprise_id,
            control_id=data['control_id'], risk_id=data['risk_id'],
            coverage_level=data.get('coverage_level','full'),
            notes=data.get('notes',''))
        db.session.add(m); db.session.commit()
        return m.to_dict()

    @staticmethod
    def delete_mapping(mapping_id: int) -> bool:
        m = ControlRiskMapping.query.get(mapping_id)
        if not m: return False
        db.session.delete(m); db.session.commit()
        return True

    # ---- 综合统计 ----
    @staticmethod
    def get_coverage_stats(enterprise_id: int) -> Dict:
        risks = Risk.query.filter_by(enterprise_id=enterprise_id).all()
        mappings = ControlRiskMapping.query.filter_by(enterprise_id=enterprise_id).all()
        controls = InternalControl.query.filter_by(enterprise_id=enterprise_id).all()
        mapped_risk_ids = set(m.risk_id for m in mappings)
        return {
            'total_risks': len(risks), 'total_controls': len(controls),
            'total_mappings': len(mappings),
            'covered_risks': len(mapped_risk_ids),
            'uncovered_risks': len(risks) - len(mapped_risk_ids),
            'coverage_rate': f"{len(mapped_risk_ids)/max(len(risks),1)*100:.0f}%",
            'uncovered_list': [{'risk_code':r.risk_code,'name':r.name,'risk_score':r.risk_score}
                              for r in risks if r.id not in mapped_risk_ids],
            'controls_by_effectiveness': {
                'effective': sum(1 for c in controls if c.effectiveness=='effective'),
                'partial': sum(1 for c in controls if c.effectiveness=='partial'),
                'ineffective': sum(1 for c in controls if c.effectiveness=='ineffective'),
            }
        }
