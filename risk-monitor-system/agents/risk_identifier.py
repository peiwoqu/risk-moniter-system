# -*- coding: utf-8 -*-
"""
Agent智能风险监控管理系统 - 风险识别Agent
基于输入的企业信息，自动识别和提取风险
"""

import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RiskIdentifierAgent:
    """风险识别Agent - 分析企业信息，识别主要风险"""

    def __init__(self, llm_service=None):
        from .llm_service import get_llm_service
        self.llm = llm_service or get_llm_service()

    def _build_system_prompt(self) -> str:
        return """你是一个企业风险管理专家，精通COSO ERM 2017框架和ISO 31000标准。
你的任务是基于提供的企业信息，识别该企业面临的主要风险。

请按以下JSON格式输出风险列表：
[
  {
    "risk_code": "R1",
    "name": "风险名称（简洁明确）",
    "category": "外部风险/内部风险",
    "subcategory": "监管政策风险/行业竞争风险/地缘政治风险/...",
    "description": "详细的风险描述（包括背景、现状、趋势）",
    "possible_consequences": "可能导致的具体后果",
    "information_source": "信息来源（年报、公告、媒体报道等）"
  }
]

要求：
1. 每个风险必须有具体的描述，避免空泛
2. 必须包含可能后果和信息来源
3. 覆盖外部和内部两类风险
4. 按重要性排序，一般识别6-10个风险
5. 针对互联网科技企业，重点关注：监管政策、行业竞争、数据安全、AI技术、地缘政治等维度"""

    def identify(self, enterprise_info: str,
                 enterprise_name: str = "",
                 existing_risks: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """执行风险识别"""
        logger.info(f"RiskIdentifierAgent: identifying risks for {enterprise_name}")

        user_message = f"企业名称：{enterprise_name}\n\n企业信息：\n{enterprise_info}\n\n请识别该企业面临的主要风险。"
        if existing_risks:
            user_message += f"\n\n已有风险列表（请补充优化）：\n{json.dumps(existing_risks, ensure_ascii=False, indent=2)}"

        try:
            response = self.llm.chat(self._build_system_prompt(), user_message)
            risks = self._parse_response(response)
            if risks:
                for i, risk in enumerate(risks):
                    if not risk.get("risk_code"):
                        risk["risk_code"] = f"R{i + 1}"
                logger.info(f"RiskIdentifierAgent: identified {len(risks)} risks")
                return risks
            else:
                logger.warning("RiskIdentifierAgent: could not parse LLM response, using KB fallback")
                return self._fallback_identify(enterprise_name)
        except Exception as e:
            logger.error(f"RiskIdentifierAgent: identification error - {e}")
            return self._fallback_identify(enterprise_name)

    def _parse_response(self, response: str) -> Optional[List[Dict]]:
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "risks" in data:
                return data["risks"]
        except json.JSONDecodeError:
            pass
        import re
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return None

    def _fallback_identify(self, enterprise_name: str) -> List[Dict]:
        from .knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        if "腾讯" in enterprise_name or "Tencent" in enterprise_name:
            return kb.get("tencent_risks", [])
        # 对于非腾讯企业，返回空列表，让后续的规则引擎重新分析
        return []

    def identify_from_document(self, document_text: str,
                               enterprise_name: str = "") -> List[Dict[str, Any]]:
        """从文档文本中识别风险"""
        max_length = 8000
        if len(document_text) > max_length:
            risk_keywords = ["风险", "risk", "不确定", "挑战", "监管",
                           "竞争", "合规", "安全", "数据", "技术"]
            paragraphs = document_text.split('\n')
            high_priority = []
            low_priority = []
            for p in paragraphs:
                if any(kw in p.lower() for kw in risk_keywords):
                    high_priority.append(p)
                else:
                    low_priority.append(p)
            doc_text = '\n'.join(high_priority)[:max_length]
        else:
            doc_text = document_text
        return self.identify(doc_text, enterprise_name)

    def quick_identify(self, enterprise_name: str) -> List[Dict[str, Any]]:
        """快速识别（直接使用知识库，不调用LLM）"""
        logger.info(f"RiskIdentifierAgent: quick identify {enterprise_name}")
        return self._fallback_identify(enterprise_name)
