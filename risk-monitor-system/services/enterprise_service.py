# -*- coding: utf-8 -*-
"""企业数据服务"""
import json, os, logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from models.database import (db, Enterprise, Risk, RiskEvent, EarlyWarning,
    InternalControl, GovernanceStructure, ControlRiskMapping,
    SupervisionMechanism, InformationDisclosure, ImprovementIssue)
logger = logging.getLogger(__name__)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads')

class EnterpriseService:
    @staticmethod
    def get_all(): return [e.to_dict() for e in Enterprise.query.order_by(Enterprise.updated_at.desc()).all()]
    @staticmethod
    def get_by_id(eid): return Enterprise.query.get(eid)
    @staticmethod
    def create(name, stock_code="", industry="", description="", raw_data_text=""):
        ent = Enterprise(name=name, stock_code=stock_code, industry=industry, description=description, raw_data_text=raw_data_text)
        db.session.add(ent); db.session.commit(); return ent.to_dict()
    @staticmethod
    def update(eid, data):
        ent = Enterprise.query.get(eid)
        if not ent: return None
        for f in ['name','stock_code','industry','description','raw_data_text','source_files']:
            if f in data: setattr(ent, f, data[f])
        ent.updated_at = datetime.utcnow(); db.session.commit(); return ent.to_dict()
    @staticmethod
    def delete(eid):
        ent = Enterprise.query.get(eid)
        if not ent: return False
        for risk in Risk.query.filter_by(enterprise_id=eid).all():
            EarlyWarning.query.filter_by(risk_id=risk.id).delete()
            RiskEvent.query.filter_by(risk_id=risk.id).delete()
        Risk.query.filter_by(enterprise_id=eid).delete()
        InternalControl.query.filter_by(enterprise_id=eid).delete()
        GovernanceStructure.query.filter_by(enterprise_id=eid).delete()
        ControlRiskMapping.query.filter_by(enterprise_id=eid).delete()
        SupervisionMechanism.query.filter_by(enterprise_id=eid).delete()
        InformationDisclosure.query.filter_by(enterprise_id=eid).delete()
        ImprovementIssue.query.filter_by(enterprise_id=eid).delete()
        db.session.delete(ent); db.session.commit(); return True

    @staticmethod
    def import_text_data(eid, text):
        ent = Enterprise.query.get(eid)
        if not ent: return {"success": False, "error": "企业不存在"}
        ent.raw_data_text = (ent.raw_data_text or '') + "\n\n" + text if ent.raw_data_text else text
        ent.updated_at = datetime.utcnow(); db.session.commit()
        return {"success": True, "length": len(text), "total_length": len(ent.raw_data_text or '')}

    @staticmethod
    def import_file(eid, filepath):
        ent = Enterprise.query.get(eid)
        if not ent: return {"success": False, "error": "企业不存在"}
        from services.data_ingestion import DataIngestionEngine
        text = DataIngestionEngine()._extract_text(filepath)
        if text:
            ent.raw_data_text = (ent.raw_data_text or '') + "\n\n--- " + os.path.basename(filepath) + " ---\n\n" + text if ent.raw_data_text else text
        files = json.loads(ent.source_files) if ent.source_files else []
        files.append(filepath); ent.source_files = json.dumps(files, ensure_ascii=False)
        ent.updated_at = datetime.utcnow(); db.session.commit()
        return {"success": True, "file": os.path.basename(filepath), "extracted_chars": len(text or '')}

    @staticmethod
    def run_full_analysis(eid):
        """运行完整五步分析，结果存入数据库"""
        ent = Enterprise.query.get(eid)
        if not ent: return {"success": False, "error": "企业不存在"}

        info = ent.raw_data_text or (f"企业：{ent.name}\n行业：{ent.industry or '未知'}\n{ent.description or ''}")
        from services.analysis_service import AnalysisService
        service = AnalysisService()
        result = service.run_complete_analysis(ent.name, info, ent.industry or '')

        # 清空旧数据
        for risk in Risk.query.filter_by(enterprise_id=eid).all():
            EarlyWarning.query.filter_by(risk_id=risk.id).delete()
            RiskEvent.query.filter_by(risk_id=risk.id).delete()
        Risk.query.filter_by(enterprise_id=eid).delete()
        InternalControl.query.filter_by(enterprise_id=eid).delete()
        GovernanceStructure.query.filter_by(enterprise_id=eid).delete()
        ControlRiskMapping.query.filter_by(enterprise_id=eid).delete()
        SupervisionMechanism.query.filter_by(enterprise_id=eid).delete()
        ImprovementIssue.query.filter_by(enterprise_id=eid).delete()

        # M2: 风险数据
        for rd in result.get('m2_risks', []):
            risk = Risk(enterprise_id=eid, risk_code=rd.get('risk_code',''), name=rd.get('name',''),
                       category=rd.get('category',''), subcategory=rd.get('subcategory',''),
                       description=rd.get('description',''), possible_consequences=rd.get('possible_consequences',''),
                       information_source=rd.get('information_source',''),
                       probability=rd.get('probability',3), impact=rd.get('impact',3),
                       status='active', trend=rd.get('trend','stable'),
                       current_response=rd.get('current_response',''),
                       suggested_improvement=rd.get('suggested_improvement',''),
                       response_type=rd.get('response_type','reduce'), ai_identified=True)
            risk.calculate_score(); db.session.add(risk); db.session.flush()
            if (risk.risk_score or 0) >= 10:
                db.session.add(EarlyWarning(risk_id=risk.id,
                    warning_level="red" if risk.risk_score>=15 else "orange",
                    warning_message=f"{'【红色预警】' if risk.risk_score>=15 else '【橙色预警】'}{risk.name}",
                    trigger_reason=f"P={risk.probability}xI={risk.impact}={risk.risk_score}"))

        # M3: 内控——保存自动生成的分析结果
        gov_data = result.get('m3_governance', {})
        gs = GovernanceStructure(enterprise_id=eid,
            structure_type=gov_data.get('structure_type',''), board_size=gov_data.get('typical_board',''),
            committees=gov_data.get('committees',''), description=gov_data.get('description',''),
            org_chart_text=gov_data.get('recommendation',''))
        db.session.add(gs)
        db.session.flush()

        # 保存自动生成的内控制度列表
        for ctrl in result.get('m3_controls', {}).get('controls', []):
            db.session.add(InternalControl(enterprise_id=eid,
                control_code=ctrl.get('control_code',''), name=ctrl.get('name',''),
                category=ctrl.get('category',''), description=ctrl.get('description',''),
                related_risks=','.join(ctrl.get('covers_risks',[])),
                responsible_dept='风险管理部', effectiveness=ctrl.get('effectiveness','有效')))

        # M4: 监督改进——保存自动生成的监督数据和问题
        sup = result.get('m4_supervision', {})
        for mech in sup.get('mechanisms', []):
            db.session.add(SupervisionMechanism(enterprise_id=eid,
                mechanism_name=mech.get('mechanism_name',''), mechanism_type=mech.get('mechanism_type',''),
                description=mech.get('description',''), frequency=mech.get('frequency',''),
                responsible_party=mech.get('responsible_party','')))

        for iss in result.get('m4_issues', []):
            db.session.add(ImprovementIssue(enterprise_id=eid,
                issue_code=f"ISS-{ImprovementIssue.query.filter_by(enterprise_id=eid).count()+1:03d}",
                title=iss.get('title',''), description=iss.get('description',''),
                source=iss.get('source','auto_analysis'), severity=iss.get('severity','medium'),
                status='open', proposed_action=iss.get('proposed_action',''),
                deadline=datetime.utcnow() if '立即' in iss.get('deadline','') else None))

        ent.risk_count = len(result.get('m2_risks', []))
        ent.last_analyzed = datetime.utcnow()
        db.session.commit()

        return {"success": True, "enterprise_id": eid, "enterprise_name": ent.name,
                "risk_count": ent.risk_count, "result": result}

    @staticmethod
    def seed_tencent():
        existing = Enterprise.query.filter_by(name="腾讯控股").first()
        if existing: return {"success": True, "enterprise_id": existing.id, "message": "已存在"}
        ent = Enterprise(name="腾讯控股", stock_code="0700.HK", industry="互联网科技",
                        description="中国领先的互联网科技企业，主营社交、游戏、金融科技、云计算与AI")
        db.session.add(ent); db.session.commit()
        from agents.knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        for rd in kb.get("tencent_risks", []):
            risk = Risk(enterprise_id=ent.id, risk_code=rd["risk_code"], name=rd["name"],
                       category=rd["category"], subcategory=rd["subcategory"],
                       description=rd.get("description",""), possible_consequences=rd.get("possible_consequences",""),
                       information_source=rd.get("information_source",""),
                       probability=rd.get("probability",3), impact=rd.get("impact",3),
                       status="active", trend=rd.get("trend","stable"),
                       current_response=rd.get("current_response",""),
                       suggested_improvement=rd.get("suggested_improvement",""),
                       response_type=rd.get("response_type","reduce"))
            risk.calculate_score(); db.session.add(risk)
        db.session.commit()
        ent.risk_count = len(kb.get("tencent_risks",[])); ent.last_analyzed = datetime.utcnow(); db.session.commit()
        return {"success": True, "enterprise_id": ent.id, "message": "腾讯案例已创建"}
