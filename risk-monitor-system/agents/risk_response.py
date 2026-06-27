"""
Agent智能风险监控管理系统 - 风险应对Agent
基于4T策略生成风险应对建议
"""

import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RiskResponseAgent:
    """
    风险应对Agent

    职责：
    1. 基于4T策略（Avoid/Reduce/Transfer/Accept）生成应对建议
    2. 评估现有应对措施的有效性
    3. 提出改进建议
    4. 生成风险应对报告
    """

    # 4T策略模板
    STRATEGY_TEMPLATES = {
        "avoid": {
            "name": "风险规避",
            "icon": "🚫",
            "description": "停止或避免高风险活动，退出高风险市场或业务线",
            "applicable_when": "风险超出企业风险偏好、风险收益比不合理、企业无能力管理"
        },
        "reduce": {
            "name": "风险降低",
            "icon": "🛡️",
            "description": "采取控制措施降低风险发生的可能性或影响程度",
            "applicable_when": "风险在可管理范围内、风险与业务机会共存、可通过控制措施有效降低"
        },
        "transfer": {
            "name": "风险转移",
            "icon": "🔄",
            "description": "通过保险、外包、合同条款、金融工具等方式将风险转移给第三方",
            "applicable_when": "风险可被定价和转移、第三方更擅长管理该风险、保险市场成熟"
        },
        "accept": {
            "name": "风险接受",
            "icon": "✅",
            "description": "在风险偏好范围内接受剩余风险，不做额外应对",
            "applicable_when": "风险在承受范围内、应对成本大于收益、无有效应对措施"
        }
    }

    # 不同风险类别的推荐应对策略
    CATEGORY_STRATEGY_MAP = {
        "监管政策风险": {
            "primary": "reduce",
            "measures": [
                "建立政策前瞻研究机制，提前6-12个月预判政策方向",
                "加强政府关系维护和行业沟通渠道",
                "完善合规管理体系，确保业务流程合规",
                "主动参与行业标准制定和监管沙盒试点",
                "建立「监管沙盒」机制，以技术手段回应监管关切"
            ]
        },
        "行业竞争风险": {
            "primary": "reduce",
            "measures": [
                "加大核心技术和产品研发投入",
                "巩固核心竞争壁垒（用户基础、生态优势）",
                "差异化产品策略，避免同质化竞争",
                "加速国际化布局，开拓新市场",
                "建立竞争情报监测系统，快速响应市场变化"
            ]
        },
        "地缘政治风险": {
            "primary": "reduce",
            "measures": [
                "制定分级应急预案（维持现状/投资禁令/出口管制）",
                "分散供应链风险，建立多源供应体系",
                "降低外资持股比例，减少资本市场依赖",
                "业务全球化布局，分散区域集中风险",
                "加强自主技术研发，降低外部依赖"
            ],
            "secondary": "transfer",
            "transfer_measures": [
                "购买政治风险保险",
                "通过合同条款分散合规风险"
            ]
        },
        "战略风险": {
            "primary": "reduce",
            "measures": [
                "明确战略定位，聚焦核心优势领域",
                "建立战略评估和动态调整机制",
                "控制投资节奏，确保战略资源聚焦",
                "加强战略执行的监控和考核",
                "定期进行战略复盘和情景规划"
            ]
        },
        "运营风险": {
            "primary": "reduce",
            "measures": [
                "优化业务流程，提升运营效率",
                "建立业务连续性管理体系",
                "加强供应链管理和质量控制",
                "完善产品生命周期管理",
                "建立运营风险关键指标(KRI)监控体系"
            ]
        },
        "技术风险": {
            "primary": "reduce",
            "measures": [
                "加大信息安全投入，建立多层防护体系",
                "建立数据分类分级管理制度",
                "实施定期安全审计和渗透测试",
                "建立AI安全护栏和算法审计机制",
                "制定数据泄露应急预案"
            ],
            "secondary": "transfer",
            "transfer_measures": [
                "购买网络安全保险",
                "通过合同条款约定安全责任"
            ]
        },
        "财务风险": {
            "primary": "reduce",
            "measures": [
                "优化资本结构，控制负债水平",
                "建立现金流预警机制",
                "实施投资组合压力测试",
                "加强汇率和利率风险管理",
                "建立财务风险指标体系"
            ]
        },
        "人力资源风险": {
            "primary": "reduce",
            "measures": [
                "完善薪酬激励和股权激励体系",
                "建立人才梯队和继任计划",
                "加强合规文化和企业价值观建设",
                "优化组织架构，减少管理层级",
                "建立核心人才保留机制"
            ]
        }
    }

    def __init__(self, llm_service=None):
        from .llm_service import get_llm_service
        self.llm = llm_service or get_llm_service()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return """你是一个企业风险应对专家。请基于4T策略框架为每个风险生成应对建议。

应对策略包括：
1. Avoid（规避）：停止或避免高风险活动
2. Reduce（降低）：采取控制措施降低风险
3. Transfer（转移）：通过保险、外包等转移风险
4. Accept（接受）：在风险偏好内接受剩余风险

对每个风险，请提供：
- response_type: 主要应对策略类型
- current_response: 当前已有的应对措施（3-5条，用分号分隔）
- suggested_improvement: 改进建议（3-5条，用分号分隔）
- effectiveness_assessment: 现有措施有效性评估（effective/partial/ineffective）

输出JSON格式，在原风险数据基础上增加上述字段。"""

    def generate_responses(self, risks: List[Dict[str, Any]],
                          enterprise_context: str = "") -> List[Dict[str, Any]]:
        """
        为风险列表生成应对建议

        Args:
            risks: 风险评估列表
            enterprise_context: 企业背景信息

        Returns:
            包含应对建议的风险列表
        """
        logger.info(f"RiskResponseAgent: 为 {len(risks)} 个风险生成应对建议")

        # 首先使用规则引擎快速生成
        responded = self._rule_based_response(risks)

        # 如果有LLM可用，用LLM优化
        try:
            user_message = json.dumps(risks, ensure_ascii=False, indent=2)
            if enterprise_context:
                user_message = f"企业背景：{enterprise_context}\n\n风险列表：{user_message}"

            llm_response = self.llm.chat(self.system_prompt, user_message)
            llm_responded = self._parse_response(llm_response)

            if llm_responded:
                responded = self._merge_responses(responded, llm_responded)
        except Exception as e:
            logger.warning(f"RiskResponseAgent: LLM建议生成失败，使用规则引擎 - {e}")

        logger.info(f"RiskResponseAgent: 应对建议生成完成")
        return responded

    def _rule_based_response(self, risks: List[Dict]) -> List[Dict]:
        """基于规则引擎生成应对建议"""
        for risk in risks:
            category = risk.get("subcategory", risk.get("category", ""))

            # 查找匹配的策略
            strategy = self.CATEGORY_STRATEGY_MAP.get(category)
            if strategy is None:
                # 尝试模糊匹配
                for key in self.CATEGORY_STRATEGY_MAP:
                    if key in category or category in key:
                        strategy = self.CATEGORY_STRATEGY_MAP[key]
                        break

            if strategy is None:
                strategy = self.CATEGORY_STRATEGY_MAP["运营风险"]  # 默认

            risk["response_type"] = strategy["primary"]
            risk["current_response"] = "；".join(strategy["measures"][:4])

            # 生成改进建议
            improvements = self._generate_improvements(risk, strategy)
            risk["suggested_improvement"] = "；".join(improvements[:4])

            # 评估现有措施有效性
            risk["effectiveness_assessment"] = self._assess_effectiveness(risk)

        return risks

    def _generate_improvements(self, risk: Dict, strategy: Dict) -> List[str]:
        """根据风险特征生成改进建议"""
        improvements = []
        score = risk.get("risk_score", 10)
        trend = risk.get("trend", "stable")

        # 基于风险得分和趋势的改进建议
        if score >= 15:
            improvements.append("建立专项风险管理团队和应急预案")
            improvements.append("提升该风险的监控频率至每日/每周")
        if trend == "increasing":
            improvements.append("增加资源投入以遏制风险上升趋势")
            improvements.append("进行根因分析，识别风险上升的驱动因素")

        # 基于类别的定制改进
        category = risk.get("subcategory", "")
        if "监管" in category:
            improvements.append("建立监管政策数据库和自动追踪系统")
        if "竞争" in category:
            improvements.append("建立竞争对手动态监测和快速响应机制")
        if "地缘" in category:
            improvements.append("聘请专业国际法顾问团队")
        if "战略" in category:
            improvements.append("定期进行战略情景规划和压力测试")
        if "技术「 in category or 」数据" in category:
            improvements.append("加大技术安全基础设施投资")
            improvements.append("建立AI安全治理委员会")

        return improvements

    def _assess_effectiveness(self, risk: Dict) -> str:
        """评估现有应对措施有效性"""
        score = risk.get("risk_score", 10)
        status = risk.get("status", "active")

        if score >= 15 and status == "active":
            return "partial"
        elif score >= 10:
            return "partial"
        elif score >= 5:
            return "effective"
        return "effective"

    def get_strategy_summary(self, risks: List[Dict]) -> Dict[str, Any]:
        """获取应对策略摘要"""
        summary = {
            "avoid": {"count": 0, "risks": []},
            "reduce": {"count": 0, "risks": []},
            "transfer": {"count": 0, "risks": []},
            "accept": {"count": 0, "risks": []}
        }

        for risk in risks:
            resp_type = risk.get("response_type", "reduce")
            if resp_type in summary:
                summary[resp_type]["count"] += 1
                summary[resp_type]["risks"].append({
                    "risk_code": risk.get("risk_code", ""),
                    "name": risk.get("name", ""),
                    "risk_score": risk.get("risk_score", 0)
                })

        return summary

    def get_priority_actions(self, risks: List[Dict], top_n: int = 5) -> List[Dict]:
        """获取优先行动事项"""
        # 按风险得分排序，取前N个
        sorted_risks = sorted(risks, key=lambda r: r.get("risk_score", 0), reverse=True)

        actions = []
        for risk in sorted_risks[:top_n]:
            actions.append({
                "priority": len(actions) + 1,
                "risk_code": risk.get("risk_code", ""),
                "risk_name": risk.get("name", ""),
                "risk_score": risk.get("risk_score", 0),
                "action": risk.get("suggested_improvement", "").split("；")[0] if risk.get("suggested_improvement") else "",
                "response_type": risk.get("response_type", "reduce"),
                "deadline": "立即" if risk.get("risk_score", 0) >= 15 else "本月内" if risk.get("risk_score", 0) >= 10 else "本季度内"
            })

        return actions

    def _parse_response(self, response: str) -> Optional[List[Dict]]:
        """解析LLM响应"""
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

    def _merge_responses(self, rule_based: List[Dict],
                         llm_based: List[Dict]) -> List[Dict]:
        """合并规则引擎和LLM建议"""
        for i, risk in enumerate(rule_based):
            if i < len(llm_based):
                llm_risk = llm_based[i]
                if isinstance(llm_risk, dict):
                    risk["response_type"] = llm_risk.get("response_type", risk.get("response_type"))
                    risk["current_response"] = llm_risk.get("current_response", risk.get("current_response"))
                    risk["suggested_improvement"] = llm_risk.get("suggested_improvement", risk.get("suggested_improvement"))
                    risk["effectiveness_assessment"] = llm_risk.get("effectiveness_assessment", risk.get("effectiveness_assessment"))
        return rule_based
