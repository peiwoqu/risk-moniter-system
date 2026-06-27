# -*- coding: utf-8 -*-
"完整分析流水线 - M1数据接入 -> M2风险分析 -> M3内控评估 -> M4监督建议 -> M5报告"
import logging
from typing import Dict, Any, List
from datetime import datetime
from services.data_ingestion import DataIngestionEngine
from services.auto_analysis import AutoAnalysisEngine

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.ingestion = DataIngestionEngine()
        self.auto_engine = AutoAnalysisEngine()

    def run_complete_analysis(self, enterprise_name: str, enterprise_info: str = '',
                               industry: str = '', filepath: str = '') -> Dict[str, Any]:
        logger.info(f"=== 五步分析: {enterprise_name} ===")
        now = datetime.utcnow().isoformat()

        # Step 1: M1 data
        parsed = None
        if filepath: parsed = self.ingestion.parse_document(filepath)
        elif enterprise_info: parsed = self.ingestion.parse_text_block(enterprise_info, industry)
        pre_extracted = parsed.get('extracted_risks', []) if parsed else []
        financial = parsed.get('financial_data', {}) if parsed else {}

        # Step 2: M2 risks
        from agents.supervisor import get_supervisor
        sup = get_supervisor()
        if pre_extracted: identified = pre_extracted
        else: identified = sup.run_identification_only(enterprise_info, enterprise_name) or self._generic(enterprise_name, industry)
        ar = sup.run_assessment_only(identified); assessed = ar.get('risks', identified)
        warnings = sup.run_warning_only(assessed)
        responded = sup.run_response_only(assessed)

        # Step 3/4: M3 + M4 auto
        m3 = self.auto_engine.analyze_all_m3(enterprise_name, industry, responded, enterprise_info)
        m4 = self.auto_engine.analyze_all_m4(enterprise_name, industry, responded, m3['coverage'])

        # Step 5: M5 report (generated on-demand)
        st = ar.get('statistics', {})
        return {"enterprise_name": enterprise_name, "industry": industry,
            "m1_data": {"summary":"","financial":financial,"pre_extracted_count":len(pre_extracted)},
            "m2_risks": responded, "m2_warnings": warnings, "m2_stats": st,
            "m2_matrix": ar.get('matrix_data', {}),
            "m3_governance": m3['governance'], "m3_three_lines": m3['three_lines'],
            "m3_controls": m3['coverage'],
            "m4_supervision": m4, "m4_issues": m4.get('issues',[]),
            "m4_pdca": m4.get('pdca',{}),
            "pipeline_metadata": {"enterprise_name": enterprise_name, "risks_count": len(responded),
                "warnings_count": len(warnings), "critical_count": st.get('by_level',{}).get('critical',0),
                "high_count": st.get('by_level',{}).get('high',0),
                "coverage_rate": m3['coverage'].get('coverage_rate','N/A'),
                "auto_issues_count": len(m4.get('issues',[])), "analyzed_at": now}}

    def _generic(self, n, i): return [{"risk_code":f"R{j+1}","name":nm,"category":c,"subcategory":s,
        "description":d,"probability":p,"impact":imp,"risk_score":p*imp,
        "risk_level":"critical" if p*imp>=15 else ("high" if p*imp>=10 else "medium"),
        "status":"active","trend":"stable","ai_identified":True}
        for j,(nm,c,s,d,p,imp) in enumerate([
            ("行业竞争风险","外部风险","行业竞争风险",f"{n}面临竞争挑战",3,3),
            ("运营管理风险","内部风险","运营风险",f"{n}的运营风险",3,3),
            ("财务管理风险","内部风险","财务风险",f"{n}的财务风险",2,3),
            ("政策法规风险","外部风险","监管政策风险","政策变化风险",2,4)])]
