# -*- coding: utf-8 -*-
"""
Agent智能风险监控管理系统 - LLM服务封装
支持 OpenAI / Claude / 本地模型切换
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class LLMService:
    """统一的LLM服务接口，封装不同模型的调用"""

    def __init__(self, model: str = None, temperature: float = 0.3):
        self.model = model or os.environ.get('AI_MODEL', 'claude-opus-4-8')
        self.temperature = temperature
        self.openai_key = os.environ.get('OPENAI_API_KEY', '')
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.local_endpoint = os.environ.get('LOCAL_LLM_ENDPOINT', '')

    def chat(self, system_prompt: str, user_message: str,
             response_format: Optional[Dict] = None) -> str:
        """发送对话请求，自动选择可用模型"""
        if self.anthropic_key:
            return self._call_claude(system_prompt, user_message)
        if self.openai_key:
            return self._call_openai(system_prompt, user_message, response_format)
        if self.local_endpoint:
            return self._call_local(system_prompt, user_message)
        logger.warning("未检测到任何LLM API，使用规则引擎模式")
        return self._rule_based_response(system_prompt, user_message)

    def _call_claude(self, system_prompt: str, user_message: str) -> str:
        """调用 Claude API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._rule_based_response(system_prompt, user_message)

    def _call_openai(self, system_prompt: str, user_message: str,
                     response_format: Optional[Dict] = None) -> str:
        """调用 OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            kwargs = {
                "model": "gpt-4o",
                "temperature": self.temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            }
            if response_format:
                kwargs["response_format"] = response_format
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._rule_based_response(system_prompt, user_message)

    def _call_local(self, system_prompt: str, user_message: str) -> str:
        """调用本地模型（兼容 Ollama / vLLM 等）"""
        try:
            import requests
            resp = requests.post(
                f"{self.local_endpoint}/v1/chat/completions",
                json={
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                },
                timeout=120
            )
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            return self._rule_based_response(system_prompt, user_message)

    def _rule_based_response(self, system_prompt: str, user_message: str) -> str:
        """基于规则引擎的智能响应（无需LLM API）"""
        from .knowledge_base import get_knowledge_base
        kb = get_knowledge_base()

        sp = system_prompt.lower() + system_prompt  # 同时支持中英文匹配

        # 通过prompt内容和user_message内容双重判断任务类型
        if "风险识别" in sp or "识别" in sp or "identify" in sp:
            return self._identify_risks_from_text(user_message, kb)
        if "风险评估" in sp or "assess" in sp:
            return self._assess_risks_from_text(user_message, kb)
        if "预警" in sp or "early_warning" in sp:
            return self._warn_risks_from_text(user_message, kb)
        if "风险应对" in sp or "response" in sp:
            return self._respond_risks_from_text(user_message, kb)

        # 通过user_message判断
        um = user_message.lower()
        if "请识别" in um or "识别风险" in um:
            return self._identify_risks_from_text(user_message, kb)
        if "请评估" in um or "评估风险" in um:
            return self._assess_risks_from_text(user_message, kb)
        if "预警" in um:
            return self._warn_risks_from_text(user_message, kb)
        if "应对" in um:
            return self._respond_risks_from_text(user_message, kb)

        return json.dumps({"message": "规则引擎处理完成"}, ensure_ascii=False)

    def _identify_risks_from_text(self, user_message: str, kb: Dict) -> str:
        """基于输入文本智能识别风险（非腾讯专用）"""
        # 从文本中提取风险信息
        identified = []
        text = user_message.lower()

        # 行业特定关键词映射（通用版，不限于腾讯）
        generic_keywords = {
            "监管政策风险": ["监管", "政策", "法规", "合规", "牌照", "许可", "审批",
                          "反垄断", "未成年人", "版号", "数据安全法", "个人信息保护",
                          "碳排放", "环保", "排放标准"],
            "行业竞争风险": ["竞争", "市场份额", "价格战", "内卷", "竞争对手",
                          "新进入者", "替代品", "差异化", "护城河", "龙头"],
            "地缘政治风险": ["美国", "制裁", "实体清单", "关税", "贸易战", "出口管制",
                          "芯片", "脱钩", "地缘", "调查", "反倾销"],
            "技术变革风险": ["AI", "人工智能", "大模型", "技术迭代", "颠覆", "固态电池",
                          "自动驾驶", "智能化", "数字化", "chatgpt", "新技术路线"],
            "运营风险": ["供应链", "原材料", "物流", "产能", "利用率", "库存", "交付",
                      "品控", "良率", "生产", "外包", "依赖"],
            "财务风险": ["现金流", "负债", "减值", "汇兑", "汇率", "应收账款",
                      "成本上升", "毛利", "亏损", "融资", "偿债"],
            "人力资源风险": ["人才", "招聘", "薪酬", "流失", "罢工", "劳工", "用工",
                         "技术工人", "裁员", "劳动纠纷"],
            "市场风险": ["消费者", "需求", "销量", "渗透率", "换机", "增速放缓",
                      "宏观经济", "经济下行", "消费降级", "全球化"],
            "ESG风险": ["ESG", "碳中和", "碳排放", "环境", "社会责任", "公司治理",
                     "可持续", "碳足迹", "绿色"],
            "数据安全风险": ["数据安全", "隐私", "信息泄露", "网络攻击", "黑客",
                         "用户数据", "个人信息", "GDPR", "等保", "加密"],
        }

        risk_name_templates = {
            "监管政策风险": "监管政策风险",
            "行业竞争风险": "行业竞争加剧风险",
            "地缘政治风险": "地缘政治风险",
            "技术变革风险": "技术迭代风险",
            "运营风险": "供应链与运营风险",
            "财务风险": "财务管理风险",
            "人力资源风险": "人才与用工风险",
            "市场风险": "市场需求波动风险",
            "ESG风险": "ESG合规风险",
            "数据安全风险": "数据安全与隐私合规风险",
        }

        risk_consequences = {
            "监管政策风险": "监管处罚导致业务暂停或合规成本大幅增加；产品准入受限影响市场拓展",
            "行业竞争风险": "市场份额被侵蚀；价格战导致利润率下降；竞争优势被削弱",
            "地缘政治风险": "海外市场准入受限；关税成本增加；国际供应链中断",
            "技术变革风险": "技术路线被颠覆；研发投入回报不及预期；产品竞争力下降",
            "运营风险": "供应链中断导致生产停滞；原材料成本波动影响毛利；交付延迟损害客户关系",
            "财务风险": "现金流承压影响战略投资；汇率波动侵蚀利润；融资成本上升",
            "人力资源风险": "核心人才流失影响研发和运营；用工成本上升；劳资纠纷损害声誉",
            "市场风险": "市场需求萎缩导致营收下降；产品滞销；产能过剩",
            "ESG风险": "ESG评级下降影响融资和品牌；碳排放超标面临罚款；社会责任缺失损害声誉",
            "数据安全风险": "数据泄露导致用户信任危机和监管重罚；系统被攻击导致业务中断",
        }

        # 关键词匹配
        matched_categories = []
        for cat, keywords in generic_keywords.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score >= 2:  # 至少匹配2个关键词
                matched_categories.append((cat, score))

        # 按匹配度排序，取前8个
        matched_categories.sort(key=lambda x: x[1], reverse=True)
        top_matches = matched_categories[:8]

        if not top_matches:
            # 如果没有任何匹配，至少识别一些通用风险
            top_matches = [
                ("行业竞争风险", 1), ("运营风险", 1),
                ("财务风险", 1), ("市场风险", 1)
            ]

        for i, (cat, score) in enumerate(top_matches):
            # 从用户消息中提取相关句子作为描述
            desc_sentences = []
            for kw in generic_keywords[cat][:5]:
                for line in user_message.split('\n'):
                    if kw.lower() in line.lower() and len(line) > 10:
                        desc_sentences.append(line.strip()[:200])
                        break
                if len(desc_sentences) >= 2:
                    break

            description = "；".join(desc_sentences[:3]) if desc_sentences else f"基于企业公开信息识别的{cat}"

            probability = 4 if score >= 4 else (3 if score >= 2 else 2)
            impact = 4 if any(kw in text for kw in ["重大", "严重", "关键", "核心"]) else 3

            risk = {
                "risk_code": f"R{i + 1}",
                "name": risk_name_templates.get(cat, cat),
                "category": "外部风险" if cat in ["监管政策风险", "行业竞争风险", "地缘政治风险", "技术变革风险", "市场风险"] else "内部风险",
                "subcategory": cat,
                "description": description[:500] if description else f"基于企业信息自动识别的{cat}",
                "possible_consequences": risk_consequences.get(cat, "可能对企业经营产生不利影响"),
                "information_source": "企业公开信息（年报、公告等）",
                "probability": probability,
                "impact": impact,
                "risk_score": probability * impact,
                "risk_level": "critical" if probability * impact >= 15 else ("high" if probability * impact >= 10 else ("medium" if probability * impact >= 5 else "low")),
                "status": "active",
                "trend": "stable",
                "ai_identified": True,
                "ai_assessment_notes": f"基于规则引擎自动识别，匹配度: {score}/10"
            }
            identified.append(risk)

        return json.dumps(identified, ensure_ascii=False)

    def _assess_risks_from_text(self, user_message: str, kb: Dict) -> str:
        """基于规则的风险评估"""
        try:
            risks = json.loads(user_message) if isinstance(user_message, str) else user_message
        except json.JSONDecodeError:
            risks = kb.get("tencent_risks", [])

        if not risks:
            risks = kb.get("tencent_risks", [])

        for risk in risks:
            desc = risk.get("description", "")

            p_keywords_high = ["持续", "频繁", "已发生", "多次", "严峻", "激烈"]
            p_keywords_low = ["潜在", "可能", "未来", "远期", "尚未"]

            p_score = 3
            if any(kw in desc for kw in p_keywords_high):
                p_score = 4
            if any(kw in desc for kw in p_keywords_low):
                p_score = 2

            i_keywords_high = ["重大", "严重", "核心", "关键", "生存", "系统"]
            i_keywords_low = ["有限", "轻微", "可控", "较小"]

            i_score = 3
            if any(kw in desc for kw in i_keywords_high):
                i_score = 4
            if any(kw in desc for kw in i_keywords_low):
                i_score = 2

            risk["probability"] = risk.get("probability", p_score)
            risk["impact"] = risk.get("impact", i_score)
            risk["risk_score"] = risk["probability"] * risk["impact"]

            score = risk["risk_score"]
            if score >= 15:
                risk["risk_level"] = "critical"
            elif score >= 10:
                risk["risk_level"] = "high"
            elif score >= 5:
                risk["risk_level"] = "medium"
            else:
                risk["risk_level"] = "low"

        return json.dumps(risks, ensure_ascii=False)

    def _warn_risks_from_text(self, user_message: str, kb: Dict) -> str:
        """基于规则的预警检测"""
        try:
            risks = json.loads(user_message) if isinstance(user_message, str) else user_message
        except json.JSONDecodeError:
            risks = kb.get("tencent_risks", [])

        warnings = []
        for risk in risks:
            score = risk.get("risk_score", risk.get("probability", 3) * risk.get("impact", 3))
            prob = risk.get("probability", 3)
            impact = risk.get("impact", 3)

            if score >= 15:
                warnings.append({
                    "risk_code": risk.get("risk_code", ""),
                    "risk_name": risk.get("name", ""),
                    "warning_level": "red",
                    "message": f"红色预警：{risk.get('name', '')} 风险得分{score}，需立即处理",
                    "trigger": f"风险得分{score} >= 15 (P={prob} x I={impact})"
                })
            elif score >= 10 or prob >= 4:
                warnings.append({
                    "risk_code": risk.get("risk_code", ""),
                    "risk_name": risk.get("name", ""),
                    "warning_level": "orange",
                    "message": f"橙色预警：{risk.get('name', '')} 风险得分{score}，需重点关注",
                    "trigger": f"风险得分{score} >= 10 或 P={prob} >= 4"
                })
            elif prob >= 3:
                warnings.append({
                    "risk_code": risk.get("risk_code", ""),
                    "risk_name": risk.get("name", ""),
                    "warning_level": "yellow",
                    "message": f"黄色预警：{risk.get('name', '')} 风险需持续监控",
                    "trigger": f"P={prob} >= 3"
                })

        return json.dumps(warnings, ensure_ascii=False)

    def _respond_risks_from_text(self, user_message: str, kb: Dict) -> str:
        """基于规则的风险应对建议"""
        try:
            risks = json.loads(user_message) if isinstance(user_message, str) else user_message
        except json.JSONDecodeError:
            risks = kb.get("tencent_risks", [])

        response_strategies = {
            "监管政策": {
                "type": "reduce",
                "measures": "加强政策前瞻研究；建立政府关系沟通机制；完善合规管理体系；参与行业标准制定",
                "improvement": "建议设立政策前瞻研究部门，变被动合规为主动引领"
            },
            "行业竞争": {
                "type": "reduce",
                "measures": "加大AI技术投入；巩固社交平台护城河；差异化产品策略；加速国际化布局",
                "improvement": "建议AI资本开支提升至每年1000亿元以上，聚焦微信+AI差异化路线"
            },
            "地缘政治": {
                "type": "reduce",
                "measures": "分散供应链风险；建立多地上市预案；加大自主技术研发；完善法律应对机制",
                "improvement": "建议制定地缘政治风险分级应急预案，设立专职地缘风险官"
            },
            "战略风险": {
                "type": "reduce",
                "measures": "明确AI战略定位；优化资本配置结构；加强对外投资管理；完善战略评估机制",
                "improvement": "建议设立AI投资委员会，统一管理AI基础设施、研发和应用"
            },
            "运营风险": {
                "type": "reduce",
                "measures": "丰富产品矩阵；加强游戏研发管线；提升运营效率；完善生命周期管理",
                "improvement": "建议通过AI+游戏创新开辟下一代游戏形态"
            },
            "技术风险": {
                "type": "reduce",
                "measures": "加强数据安全投入；完善算法审计机制；建设AI安全护栏；强化供应链安全",
                "improvement": "建议发布年度AI透明度报告，披露AI治理进展"
            },
            "财务风险": {
                "type": "reduce",
                "measures": "优化资本结构；控制投资节奏；加强现金流管理；完善财务预警",
                "improvement": "建议适当降低股票回购力度，释放资金用于AI研发"
            },
            "人力资源": {
                "type": "reduce",
                "measures": "完善人才激励机制；加强合规文化建设；优化组织架构；建立人才储备池",
                "improvement": "建议将风险管理权重纳入员工绩效考核体系"
            }
        }

        for risk in risks:
            category = risk.get("category", risk.get("subcategory", ""))
            for key in response_strategies:
                if key in category:
                    strategy = response_strategies[key]
                    risk["response_type"] = strategy["type"]
                    risk["current_response"] = strategy["measures"]
                    risk["suggested_improvement"] = strategy["improvement"]
                    break
            else:
                default = response_strategies["运营风险"]
                risk["response_type"] = default["type"]
                risk["current_response"] = default["measures"]
                risk["suggested_improvement"] = default["improvement"]

        return json.dumps(risks, ensure_ascii=False)


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
