"""
Agent智能风险监控管理系统 - 监督协调Agent (Supervisor)
负责任务分解、Agent调度和结果整合
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .risk_identifier import RiskIdentifierAgent
from .risk_assessor import RiskAssessorAgent
from .early_warning import EarlyWarningAgent
from .risk_response import RiskResponseAgent

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """
    监督协调Agent (Supervisor)

    职责：
    1. 编排风险管理全流程
    2. 协调各专业Agent的工作
    3. 整合和汇总分析结果
    4. 对外提供统一的分析接口
    """

    def __init__(self, llm_service=None):
        from .llm_service import get_llm_service
        self.llm = llm_service or get_llm_service()

        # 初始化各专业Agent
        self.identifier = RiskIdentifierAgent(llm_service=self.llm)
        self.assessor = RiskAssessorAgent(llm_service=self.llm)
        self.early_warning = EarlyWarningAgent(llm_service=self.llm)
        self.responder = RiskResponseAgent(llm_service=self.llm)

        # 工作流历史
        self.workflow_history: List[Dict] = []

    def run_full_pipeline(self,
                          enterprise_info: str = "",
                          enterprise_name: str = "",
                          document_text: str = "",
                          risks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        运行完整的风险管理分析流程

        流程：识别 → 评估 → 预警 → 应对

        Args:
            enterprise_info: 企业基本信息文本
            enterprise_name: 企业名称
            document_text: 文档文本（年报等）
            risks: 已有的风险列表（如已识别）

        Returns:
            {
                "risks": [...],           # 识别并评估后的风险列表
                "warnings": [...],        # 预警列表
                "statistics": {...},      # 统计数据
                "matrix_data": {...},     # 风险矩阵数据
                "strategy_summary": {...},# 应对策略摘要
                "priority_actions": [...],# 优先行动事项
                "pipeline_metadata": {...} # 流程元数据
            }
        """
        workflow_id = f"WF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        start_time = datetime.utcnow()

        logger.info(f"SupervisorAgent: 开始全流程分析 [{workflow_id}] - {enterprise_name}")

        # Step 1: 风险识别
        logger.info(f"[{workflow_id}] Step 1/4: 风险识别")
        if risks is None and (enterprise_info or document_text):
            if document_text:
                identified_risks = self.identifier.identify_from_document(
                    document_text, enterprise_name
                )
            else:
                identified_risks = self.identifier.identify(
                    enterprise_info, enterprise_name
                )
        elif risks is not None:
            identified_risks = risks
        else:
            identified_risks = self.identifier.quick_identify(enterprise_name)

        # Step 2: 风险评估
        logger.info(f"[{workflow_id}] Step 2/4: 风险评估 ({len(identified_risks)} 个风险)")
        assessed_risks = self.assessor.assess(identified_risks)

        # Step 3: 预警检查
        logger.info(f"[{workflow_id}] Step 3/4: 预警检查")
        warnings = self.early_warning.check(assessed_risks)

        # Step 4: 风险应对
        logger.info(f"[{workflow_id}] Step 4/4: 风险应对建议")
        responded_risks = self.responder.generate_responses(
            assessed_risks, enterprise_info
        )

        # 汇总结果
        result = {
            "risks": responded_risks,
            "warnings": warnings,
            "statistics": self.assessor.get_statistics(responded_risks),
            "matrix_data": self.assessor.get_matrix_data(responded_risks),
            "strategy_summary": self.responder.get_strategy_summary(responded_risks),
            "priority_actions": self.responder.get_priority_actions(responded_risks),
            "pipeline_metadata": {
                "workflow_id": workflow_id,
                "enterprise_name": enterprise_name,
                "start_time": start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "risks_count": len(responded_risks),
                "warnings_count": len(warnings),
                "critical_count": sum(1 for r in responded_risks if r.get("risk_level") == "critical"),
                "high_count": sum(1 for r in responded_risks if r.get("risk_level") == "high"),
            }
        }

        # 记录工作流历史
        self.workflow_history.append({
            "workflow_id": workflow_id,
            "timestamp": start_time.isoformat(),
            "enterprise_name": enterprise_name,
            "risks_count": len(responded_risks),
            "warnings_count": len(warnings)
        })

        logger.info(f"SupervisorAgent: 全流程分析完成 [{workflow_id}]")
        return result

    def run_identification_only(self, enterprise_info: str,
                                enterprise_name: str = "") -> List[Dict]:
        """仅运行风险识别"""
        return self.identifier.identify(enterprise_info, enterprise_name)

    def run_assessment_only(self, risks: List[Dict]) -> Dict[str, Any]:
        """仅运行风险评估"""
        assessed = self.assessor.assess(risks)
        return {
            "risks": assessed,
            "statistics": self.assessor.get_statistics(assessed),
            "matrix_data": self.assessor.get_matrix_data(assessed)
        }

    def run_warning_only(self, risks: List[Dict]) -> List[Dict]:
        """仅运行预警检查"""
        return self.early_warning.check(risks)

    def run_response_only(self, risks: List[Dict]) -> List[Dict]:
        """仅生成应对建议"""
        return self.responder.generate_responses(risks)

    def re_assess_single_risk(self, risk: Dict, new_probability: int = None,
                              new_impact: int = None) -> Dict:
        """重新评估单个风险"""
        if new_probability is not None:
            risk["probability"] = new_probability
        if new_impact is not None:
            risk["impact"] = new_impact

        risk["risk_score"] = risk.get("probability", 3) * risk.get("impact", 3)
        risk["risk_level"] = self.assessor._calculate_level(risk["risk_score"])
        risk["updated_at"] = datetime.utcnow().isoformat()

        # 重新生成应对建议
        risk = self.responder._rule_based_response([risk])[0]

        return risk

    def get_workflow_summary(self) -> Dict[str, Any]:
        """获取工作流执行摘要"""
        if not self.workflow_history:
            return {"message": "暂无工作流执行记录"}

        last_run = self.workflow_history[-1]
        return {
            "total_workflows": len(self.workflow_history),
            "last_run": last_run,
            "all_runs": self.workflow_history[-10:]  # 最近10次
        }

    def export_results(self, result: Dict[str, Any],
                       format: str = "json") -> str:
        """
        导出分析结果

        Args:
            result: run_full_pipeline的输出
            format: 导出格式 (json/markdown)

        Returns:
            导出文本
        """
        if format == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)

        elif format == "markdown":
            return self._export_markdown(result)

        return json.dumps(result, ensure_ascii=False)

    def _export_markdown(self, result: Dict) -> str:
        """导出为Markdown格式"""
        lines = []
        metadata = result.get("pipeline_metadata", {})
        stats = result.get("statistics", {})

        lines.append(f"# 企业风险分析报告")
        lines.append(f"## {metadata.get('enterprise_name', '企业')}")
        lines.append(f"")
        lines.append(f"**分析时间：** {metadata.get('start_time', '')}")
        lines.append(f"**风险总数：** {stats.get('total', 0)}")
        lines.append(f"**重大风险：** {stats.get('by_level', {}).get('critical', 0)}")
        lines.append(f"")
        lines.append(f"## 风险概览")
        lines.append(f"")
        lines.append(f"| 风险编号 | 风险名称 | 类别 | P | I | 得分 | 等级 | 趋势 | 应对策略 |")
        lines.append(f"|---------|---------|------|---|---|------|------|------|---------|")

        trend_map = {"increasing": "↑上升", "stable": "→稳定", "decreasing": "↓下降"}
        level_map = {"critical": "🔴重大", "high": "🟠高度关注", "medium": "🟡一般", "low": "🟢低"}

        for risk in result.get("risks", []):
            lines.append(
                f"| {risk.get('risk_code', '')} | {risk.get('name', '')} | "
                f"{risk.get('subcategory', '')} | {risk.get('probability', '-')} | "
                f"{risk.get('impact', '-')} | {risk.get('risk_score', '-')} | "
                f"{level_map.get(risk.get('risk_level', ''), risk.get('risk_level', ''))} | "
                f"{trend_map.get(risk.get('trend', ''), risk.get('trend', ''))} | "
                f"{risk.get('response_type', '')} |"
            )

        lines.append(f"")
        lines.append(f"## 预警信息")
        for w in result.get("warnings", []):
            lines.append(f"- {w.get('warning_message', '')}")

        lines.append(f"")
        lines.append(f"## 优先行动事项")
        for i, action in enumerate(result.get("priority_actions", [])):
            lines.append(f"{i+1}. **{action.get('risk_name', '')}** - {action.get('action', '')} "
                       f"(截止: {action.get('deadline', '')})")

        return "\n".join(lines)


# 全局Supervisor实例
_supervisor: Optional[SupervisorAgent] = None


def get_supervisor() -> SupervisorAgent:
    """获取Supervisor单例"""
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor
