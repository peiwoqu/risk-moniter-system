# -*- coding: utf-8 -*-
"""M4: 监督改进服务 - 监督机制、信息披露、问题改进、持续改进PDCA"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from models.database import (db, Enterprise, SupervisionMechanism,
    InformationDisclosure, ImprovementIssue, ContinuousImprovement)

logger = logging.getLogger(__name__)

class SupervisionService:
    """M4 监督改进业务逻辑"""

    # ---- 监督机制 ----
    @staticmethod
    def get_mechanisms(enterprise_id: int) -> List[Dict]:
        return [m.to_dict() for m in SupervisionMechanism.query.filter_by(
            enterprise_id=enterprise_id).order_by(SupervisionMechanism.mechanism_type).all()]

    @staticmethod
    def create_mechanism(enterprise_id: int, data: Dict) -> Dict:
        m = SupervisionMechanism(enterprise_id=enterprise_id,
            mechanism_name=data['mechanism_name'], mechanism_type=data.get('mechanism_type','internal_audit'),
            description=data.get('description',''), frequency=data.get('frequency','每季度'),
            responsible_party=data.get('responsible_party',''), scope=data.get('scope',''))
        db.session.add(m); db.session.commit()
        return m.to_dict()

    @staticmethod
    def update_mechanism(mech_id: int, data: Dict) -> Optional[Dict]:
        m = SupervisionMechanism.query.get(mech_id)
        if not m: return None
        for f in ['mechanism_name','mechanism_type','description','frequency','responsible_party','scope']:
            if f in data: setattr(m, f, data[f])
        db.session.commit()
        return m.to_dict()

    @staticmethod
    def delete_mechanism(mech_id: int) -> bool:
        m = SupervisionMechanism.query.get(mech_id)
        if not m: return False
        db.session.delete(m); db.session.commit()
        return True

    # ---- 信息披露 ----
    @staticmethod
    def get_disclosures(enterprise_id: int) -> List[Dict]:
        return [d.to_dict() for d in InformationDisclosure.query.filter_by(
            enterprise_id=enterprise_id).order_by(InformationDisclosure.publish_date.desc()).all()]

    @staticmethod
    def create_disclosure(enterprise_id: int, data: Dict) -> Dict:
        pub_date = data.get('publish_date')
        if isinstance(pub_date, str): pub_date = datetime.fromisoformat(pub_date) if pub_date else None
        d = InformationDisclosure(enterprise_id=enterprise_id, disclosure_type=data.get('disclosure_type','annual'),
            title=data.get('title',''), publish_date=pub_date,
            risk_content_summary=data.get('risk_content_summary',''),
            compliance_status=data.get('compliance_status','compliant'),
            notes=data.get('notes',''))
        db.session.add(d); db.session.commit()
        return d.to_dict()

    @staticmethod
    def delete_disclosure(disc_id: int) -> bool:
        d = InformationDisclosure.query.get(disc_id)
        if not d: return False
        db.session.delete(d); db.session.commit()
        return True

    # ---- 问题发现与改进 ----
    @staticmethod
    def get_issues(enterprise_id: int, status_filter: str = '') -> List[Dict]:
        q = ImprovementIssue.query.filter_by(enterprise_id=enterprise_id)
        if status_filter: q = q.filter_by(status=status_filter)
        return [i.to_dict() for i in q.order_by(ImprovementIssue.severity.desc(), ImprovementIssue.created_at.desc()).all()]

    @staticmethod
    def create_issue(enterprise_id: int, data: Dict) -> Dict:
        deadline = data.get('deadline')
        if isinstance(deadline, str): deadline = datetime.fromisoformat(deadline) if deadline else None
        # auto-generate issue code
        count = ImprovementIssue.query.filter_by(enterprise_id=enterprise_id).count()
        code = data.get('issue_code', f'ISSUE-{count+1:03d}')
        iss = ImprovementIssue(enterprise_id=enterprise_id, issue_code=code,
            title=data.get('title',''), description=data.get('description',''),
            source=data.get('source','internal_audit'), severity=data.get('severity','medium'),
            status=data.get('status','open'), proposed_action=data.get('proposed_action',''),
            responsible_person=data.get('responsible_person',''), deadline=deadline)
        db.session.add(iss); db.session.commit()
        return iss.to_dict()

    @staticmethod
    def update_issue(issue_id: int, data: Dict) -> Optional[Dict]:
        iss = ImprovementIssue.query.get(issue_id)
        if not iss: return None
        for f in ['title','description','source','severity','status','proposed_action','responsible_person','resolution_summary']:
            if f in data: setattr(iss, f, data[f])
        if data.get('deadline'):
            dl = data['deadline']
            if isinstance(dl, str): dl = datetime.fromisoformat(dl)
            iss.deadline = dl
        if data.get('status') == 'resolved' and not iss.resolved_at:
            iss.resolved_at = datetime.utcnow()
        iss.updated_at = datetime.utcnow()
        db.session.commit()
        return iss.to_dict()

    @staticmethod
    def delete_issue(issue_id: int) -> bool:
        iss = ImprovementIssue.query.get(issue_id)
        if not iss: return False
        db.session.delete(iss); db.session.commit()
        return True

    @staticmethod
    def get_issue_stats(enterprise_id: int) -> Dict:
        issues = ImprovementIssue.query.filter_by(enterprise_id=enterprise_id).all()
        return {
            'total': len(issues),
            'open': sum(1 for i in issues if i.status=='open'),
            'in_progress': sum(1 for i in issues if i.status=='in_progress'),
            'resolved': sum(1 for i in issues if i.status=='resolved'),
            'closed': sum(1 for i in issues if i.status=='closed'),
            'critical': sum(1 for i in issues if i.severity=='critical'),
            'high': sum(1 for i in issues if i.severity=='high'),
            'overdue': sum(1 for i in issues if i.deadline and i.deadline < datetime.utcnow() and i.status not in ('resolved','closed')),
        }

    # ---- 持续改进PDCA ----
    @staticmethod
    def get_improvements(enterprise_id: int) -> List[Dict]:
        return [i.to_dict() for i in ContinuousImprovement.query.filter_by(
            enterprise_id=enterprise_id).order_by(ContinuousImprovement.start_date.desc()).all()]

    @staticmethod
    def create_improvement(enterprise_id: int, data: Dict) -> Dict:
        start = data.get('start_date'); end = data.get('end_date')
        if isinstance(start, str): start = datetime.fromisoformat(start) if start else None
        if isinstance(end, str): end = datetime.fromisoformat(end) if end else None
        imp = ContinuousImprovement(enterprise_id=enterprise_id,
            cycle_name=data.get('cycle_name',''), phase=data.get('phase','P'),
            start_date=start, end_date=end,
            review_summary=data.get('review_summary',''),
            improvements_made=data.get('improvements_made',''),
            lessons_learned=data.get('lessons_learned',''),
            next_cycle_plan=data.get('next_cycle_plan',''))
        db.session.add(imp); db.session.commit()
        return imp.to_dict()

    @staticmethod
    def update_improvement(imp_id: int, data: Dict) -> Optional[Dict]:
        imp = ContinuousImprovement.query.get(imp_id)
        if not imp: return None
        for f in ['cycle_name','phase','review_summary','improvements_made','lessons_learned','next_cycle_plan']:
            if f in data: setattr(imp, f, data[f])
        db.session.commit()
        return imp.to_dict()

    @staticmethod
    def delete_improvement(imp_id: int) -> bool:
        imp = ContinuousImprovement.query.get(imp_id)
        if not imp: return False
        db.session.delete(imp); db.session.commit()
        return True
