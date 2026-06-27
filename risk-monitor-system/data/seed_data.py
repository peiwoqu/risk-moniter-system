# -*- coding: utf-8 -*-
"""种子数据 - 预置腾讯案例的完整五模块数据"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from models.database import (db, Enterprise, Risk, EarlyWarning, InternalControl,
    GovernanceStructure, SupervisionMechanism, InformationDisclosure,
    ImprovementIssue, ContinuousImprovement)
from agents.knowledge_base import get_knowledge_base
from datetime import datetime

def main():
    with app.app_context():
        db.create_all()
        kb = get_knowledge_base()

        # 检查是否已有腾讯
        if Enterprise.query.filter_by(name="腾讯控股").first():
            print("腾讯案例已存在，跳过种子数据")
            return

        # 创建腾讯企业
        ent = Enterprise(name="腾讯控股", stock_code="0700.HK", industry="互联网科技",
                        description="中国领先的互联网科技企业，主营社交、游戏、金融科技、云计算与AI")
        db.session.add(ent); db.session.commit()
        eid = ent.id

        # ---- M2: 风险数据 ----
        for rd in kb.get("tencent_risks", []):
            risk = Risk(enterprise_id=eid, risk_code=rd["risk_code"], name=rd["name"],
                       category=rd["category"], subcategory=rd["subcategory"],
                       description=rd.get("description",""), possible_consequences=rd.get("possible_consequences",""),
                       information_source=rd.get("information_source",""),
                       probability=rd.get("probability",3), impact=rd.get("impact",3),
                       status="active", trend=rd.get("trend","stable"),
                       current_response=rd.get("current_response",""),
                       suggested_improvement=rd.get("suggested_improvement",""),
                       response_type=rd.get("response_type","reduce"))
            risk.calculate_score(); db.session.add(risk); db.session.flush()
            if (risk.risk_score or 0) >= 10:
                db.session.add(EarlyWarning(risk_id=risk.id,
                    warning_level="red" if risk.risk_score>=15 else "orange",
                    warning_message=f"{'【红色预警】' if risk.risk_score>=15 else '【橙色预警】'}{risk.name}",
                    trigger_reason=f"P={risk.probability} x I={risk.impact}={risk.risk_score}"))

        # ---- M3: 内控机制 ----
        # 治理结构
        gs = GovernanceStructure(enterprise_id=eid, structure_type="混合制", board_size=8,
                                independent_directors=5, committees="审计委员会,企业管治委员会,投资委员会,薪酬委员会,提名委员会",
                                description="腾讯采用独立董事会架构，董事会由8名董事组成，包含1名执行董事（马化腾/主席/CEO）、2名非执行董事（来自Naspers集团）、5名独立非执行董事（占比62.5%）")
        db.session.add(gs)

        # 内控制度
        for cd in kb.get("internal_controls", []):
            db.session.add(InternalControl(enterprise_id=eid, control_code=cd["control_code"],
                name=cd["name"], category=cd["category"], description=cd["description"],
                related_risks=cd["related_risks"], responsible_dept=cd["responsible_dept"],
                effectiveness=cd.get("effectiveness","effective")))

        # ---- M4: 监督改进 ----
        # 监督机制
        for mech in [
            ("董事会审计委员会监督", "board", "审计委员会由5名独立非执行董事组成，每季度审阅风险管理现状，每年评估内部控制有效性", "每季度", "审计委员会"),
            ("内部审计部门", "internal_audit", "独立于业务部门的内部审计团队，直接向审计委员会汇报，制定年度审计计划并执行专项审计", "持续", "内部审计部"),
            ("外部审计师", "external", "聘请普华永道(PwC)担任独立审计师，对财务报表和内控有效性提供独立意见", "每年", "普华永道"),
            ("反舞弊调查部", "compliance", "独立的反舞弊调查部门，通过举报邮箱和微信公众号接收举报，2024年查处案件100余起", "持续", "反舞弊调查部"),
            ("监管机构监督", "supervisory", "接受香港证监会(SFC)、中国人民银行、国家网信办等监管机构的定期检查和专项检查", "不定期", "合规部"),
        ]:
            db.session.add(SupervisionMechanism(enterprise_id=eid, mechanism_name=mech[0],
                mechanism_type=mech[1], description=mech[2], frequency=mech[3], responsible_party=mech[4]))

        # 信息披露
        for disc in [
            ("annual", "腾讯控股2024年度报告", "2025-03-20",
             "披露了监管政策、行业竞争、地缘政治、AI转型等重大风险因素及应对措施", "compliant"),
            ("esg", "腾讯控股2024年ESG报告", "2025-04-15",
             "披露了AI治理、气候变化、数据隐私、未成年人保护等ESG风险议题", "compliant"),
            ("quarterly", "腾讯控股2024年Q4业绩公告", "2025-03-20",
             "披露了各业务板块的经营表现和风险提示", "compliant"),
            ("timely", "关于被列入美国CMC清单的澄清公告", "2025-01-07",
             "声明公司不是军工企业，启动法律程序，加大回购力度稳定市场", "compliant"),
        ]:
            pub_date = datetime.fromisoformat(disc[2])
            db.session.add(InformationDisclosure(enterprise_id=eid, disclosure_type=disc[0],
                title=disc[1], publish_date=pub_date, risk_content_summary=disc[3],
                compliance_status=disc[4]))

        # 发现问题与改进
        for iss in [
            ("ISSUE-001", "被列入CMC清单的风险应对不足", "internal_audit", "high",
             "open", "制定地缘政治风险分级应急预案，设立专职地缘风险官", "风险管理部",
             datetime(2025, 6, 30)),
            ("ISSUE-002", "AI投资力度与竞争对手差距扩大", "self_assessment", "critical",
             "in_progress", "提升AI资本开支至每年1000亿元以上，聚焦微信+AI差异化", "战略发展部",
             datetime(2025, 9, 30)),
            ("ISSUE-003", "算法透明度与监管要求存在差距", "regulatory", "high",
             "open", "建立算法审计委员会，发布年度AI透明度报告", "合规部",
             datetime(2025, 8, 31)),
            ("ISSUE-004", "员工反舞弊教育覆盖率不足", "internal_audit", "medium",
             "resolved", "完成全员反舞弊在线培训，覆盖率达100%", "人力资源部",
             datetime(2025, 4, 30)),
        ]:
            db.session.add(ImprovementIssue(enterprise_id=eid, issue_code=iss[0], title=iss[1],
                source=iss[2], severity=iss[3], status=iss[4], proposed_action=iss[5],
                responsible_person=iss[6], deadline=iss[7],
                resolved_at=datetime(2025,4,15) if iss[4]=='resolved' else None))

        # 持续改进PDCA
        db.session.add(ContinuousImprovement(enterprise_id=eid, cycle_name="2024年度风险管理改进周期",
            phase="A", start_date=datetime(2024,1,1), end_date=datetime(2024,12,31),
            review_summary="2024年完成AI系统嵌入内控流程、ESG关键议题纳入ERM体系，整体风险可控",
            improvements_made="建立AI反腐系统；完成全面风险评估更新；优化三道防线协作机制",
            lessons_learned="地缘政治风险的预警机制需要加强；AI治理的透明度需要提升",
            next_cycle_plan="2025年重点：设立CRO职位；建立AI算法审计；加强跨境合规协同"))

        ent.risk_count = len(kb.get("tencent_risks", []))
        ent.last_analyzed = datetime.utcnow()
        db.session.commit()

        print(f"种子数据导入完成！")
        print(f"  企业: 1 (腾讯控股)")
        print(f"  风险: {Risk.query.filter_by(enterprise_id=eid).count()} 项")
        print(f"  预警: {EarlyWarning.query.join(Risk).filter(Risk.enterprise_id==eid).count()} 条")
        print(f"  治理结构: 1 项")
        print(f"  内控制度: {InternalControl.query.filter_by(enterprise_id=eid).count()} 项")
        print(f"  监督机制: {SupervisionMechanism.query.filter_by(enterprise_id=eid).count()} 项")
        print(f"  信息披露: {InformationDisclosure.query.filter_by(enterprise_id=eid).count()} 条")
        print(f"  问题改进: {ImprovementIssue.query.filter_by(enterprise_id=eid).count()} 项")
        print(f"  持续改进: {ContinuousImprovement.query.filter_by(enterprise_id=eid).count()} 项")

if __name__ == "__main__":
    main()
