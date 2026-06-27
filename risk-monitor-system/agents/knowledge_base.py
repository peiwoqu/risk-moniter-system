# -*- coding: utf-8 -*-
"""
Agent智能风险监控管理系统 - 知识库
包含COSO ERM框架、行业风险分类、腾讯预置数据
"""

import os
from typing import Dict, Any


def get_knowledge_base() -> Dict[str, Any]:
    """获取知识库数据"""

    # COSO ERM 2017 框架
    coso_erm_framework = {
        "components": [
            {
                "name": "治理与文化",
                "principles": [
                    "董事会执行风险监督", "建立运营架构",
                    "定义所需文化", "展示对核心价值观的承诺",
                    "吸引、培养和留住有能力的个人"
                ]
            },
            {
                "name": "战略与目标设定",
                "principles": [
                    "分析业务环境", "定义风险偏好",
                    "评估备选战略", "制定业务目标"
                ]
            },
            {
                "name": "绩效",
                "principles": [
                    "识别风险", "评估风险的严重程度",
                    "对风险进行排序", "实施风险应对", "发展组合视图"
                ]
            },
            {
                "name": "审阅与修订",
                "principles": [
                    "评估重大变化", "审阅风险和绩效", "追求风险管理的改进"
                ]
            },
            {
                "name": "信息、沟通与报告",
                "principles": [
                    "利用信息系统", "沟通风险信息", "汇报风险、文化和绩效"
                ]
            }
        ]
    }

    # 风险分类体系
    risk_categories = {
        "external": {
            "name": "外部风险",
            "subcategories": [
                "监管政策风险", "行业竞争风险", "地缘政治风险",
                "技术变革风险", "法律合规风险", "社会文化风险",
                "宏观经济风险", "自然灾害风险"
            ]
        },
        "internal": {
            "name": "内部风险",
            "subcategories": [
                "战略风险", "运营风险", "财务风险", "技术风险",
                "人力资源风险", "合规风险", "声誉风险"
            ]
        }
    }

    # 风险应对4T策略
    response_4t = {
        "avoid": {
            "name": "风险规避",
            "description": "停止或避免高风险活动，退出高风险市场"
        },
        "reduce": {
            "name": "风险降低",
            "description": "采取控制措施降低风险可能性或影响程度"
        },
        "transfer": {
            "name": "风险转移",
            "description": "通过保险、外包、合同条款等转移风险"
        },
        "accept": {
            "name": "风险接受",
            "description": "在风险偏好范围内接受剩余风险"
        }
    }

    # 腾讯8大风险预置数据
    tencent_risks = [
        {
            "risk_code": "R1",
            "name": "监管政策不确定性风险",
            "category": "外部风险",
            "subcategory": "监管政策风险",
            "description": (
                "互联网行业处于严格监管环境中，涉及游戏版号审批、未成年人保护、"
                "数据安全与隐私保护、反垄断、平台经济治理、算法透明度要求等多个维度。"
                "2021-2023年行业经历运动式监管后逐渐转为常态化监管，"
                "但新的监管议题（如算法备案、AIGC合规、短视频内容审核）仍在不断涌现。"
                "2024年11月网信办发布算法治理专项行动，要求公开算法机制。"
                "2025年王者荣耀匹配算法侵权案开庭，"
                "标志着监管关注从事后处罚延伸至事前治理。"
            ),
            "possible_consequences": (
                "游戏版号审批延迟导致新品上线减少15%-30%；"
                "合规成本持续上升每年增加10-20亿元；"
                "算法商业机密被强制公开损害竞争优势；"
                "监管处罚导致业务暂停或产品下架"
            ),
            "information_source": (
                "腾讯2024年报「风险因素」章节；"
                "网信办算法治理专项行动通知（2024.11）；"
                "《网络游戏管理办法（草案征求意见稿）》（2023.12）；"
                "腾讯2024年ESG报告"
            ),
            "probability": 4, "impact": 4, "risk_score": 16,
            "risk_level": "critical", "status": "active", "trend": "increasing",
            "response_type": "reduce",
            "current_response": (
                "建立了覆盖游戏、内容、数据、金融等多个维度的专业合规团队；"
                "全面实施游戏未成年人保护体系（实名认证+人脸识别+时段+消费限额），"
                "未成年人游戏时长流水占比已降至极低水平（ESG报告披露<1%）；"
                "签署了人工智能安全承诺书，参与制定AI安全行业标准；"
                "通过行业协会、人大/政协提案等多渠道与监管层沟通"
            ),
            "suggested_improvement": (
                "(1)建立监管沙盒机制：变被动合规为主动尝试，率先推出经认证的算法"
                "公平性评估体系，以技术手段回应监管关切；(2)设立专门的政策前瞻"
                "研究部门，系统跟踪全球互联网监管趋势，提前6-12个月预判政策方向；"
                "(3)加强学术界和智库合作，对核心算法机制进行学术化公开阐释"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于年报和公开监管文件自动识别"
        },
        {
            "risk_code": "R2",
            "name": "行业竞争加剧风险",
            "category": "外部风险",
            "subcategory": "行业竞争风险",
            "description": (
                "字节跳动在多维度对腾讯形成全面挑战。用户层面，字节系用户时长"
                "占比于2026年1月首次超过腾讯系，抖音人均使用时长已超越微信。"
                "AI应用层面，字节豆包月活约为腾讯元宝的3倍。盈利层面，字节跳动"
                "2025年净利润首次突破500亿美元，超越腾讯。游戏层面，网易"
                "《蛋仔派对》、米哈游《原神》等产品持续抢占市场份额。"
            ),
            "possible_consequences": (
                "微信用户粘性进一步下滑，广告变现效率承压；"
                "AI时代后发劣势可能导致新一波用户流失；"
                "资本市场估值溢价收窄；核心用户基数被侵蚀"
            ),
            "information_source": (
                "QuestMobile 2026年1月监测数据；AI产品榜全球榜单；"
                "科技媒体/36氪/财经报道；腾讯2025年Q4业绩发布会"
            ),
            "probability": 4, "impact": 4, "risk_score": 16,
            "risk_level": "critical", "status": "active", "trend": "increasing",
            "response_type": "reduce",
            "current_response": (
                "强化微信生态（视频号、小程序、搜一搜等功能），提升用户停留时长"
                "和商业化效率（视频号广告收入同比+60%）；AI层面重组大模型研发体系，"
                "引进高端人才；游戏方面执行长青游戏策略，14款年流水超40亿元游戏"
                "提供稳定现金流支撑"
            ),
            "suggested_improvement": (
                "(1)加速AI投资节奏：建议将AI基础设施投资提升至每年1,000亿元以上；"
                "(2)聚焦微信+AI差异化路线，利用13亿+用户的场景优势；"
                "(3)游戏行业寻求AI+游戏创新突破；(4)国际化加速全球布局"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于行业监测数据和竞争对手分析自动识别"
        },
        {
            "risk_code": "R3",
            "name": "地缘政治制裁风险",
            "category": "外部风险",
            "subcategory": "地缘政治风险",
            "description": (
                "2025年1月6日，美国国防部将腾讯列入1260H清单（中国军事企业清单"
                "/CMC清单）。虽然CMC清单不同于制裁/出口管制清单，对腾讯美国业务"
                "直接影响有限（美国业务收入占比仅约5%），但存在禁止投资令（类似"
                "2020年特朗普签署的行政命令）升级的风险。此外，在中美科技竞争背景下，"
                "GPU等关键硬件的出口管制可能进一步收紧。"
            ),
            "possible_consequences": (
                "最坏情况下：外资被动减持导致腾讯股价下跌20%-40%；"
                "美国游戏业务受阻；国际合作关系紧张；"
                "高端GPU供应受限导致AI基础设施扩展速度被迫放缓"
            ),
            "information_source": (
                "美国国防部CMC清单更新公告（2025.01.06）；"
                "腾讯官方回应声明（2025.01.07）；"
                "券商报告；特朗普2020年投资禁令行政命令"
            ),
            "probability": 3, "impact": 5, "risk_score": 15,
            "risk_level": "critical", "status": "active", "trend": "stable",
            "response_type": "reduce",
            "current_response": (
                "被列入CMC清单后迅速启动应对：(1)官方声明反驳指控；"
                "(2)启动法律程序向美国当局提交说明和证据；"
                "(3)表态愿意与相关部门共同解决误解；"
                "(4)加大股份回购力度（2025年1月合共15亿港元）稳定市场信心；"
                "(5)与投行分析师密集沟通输出影响评估"
            ),
            "suggested_improvement": (
                "(1)制定并公开地缘政治风险分级应急预案；"
                "(2)降低外资持股比例；(3)业务全球化布局的Plan B；"
                "(4)设立地缘政治风险官职位直接向董事会汇报"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于美国国防部公告和券商分析报告自动识别"
        },
        {
            "risk_code": "R4",
            "name": "AI战略转型风险",
            "category": "内部风险",
            "subcategory": "战略风险",
            "description": (
                "腾讯在AI领域的策略定位面临市场质疑。2024年AI资本开支767.6亿元"
                "创历史新高，但2025年计划仅为792亿元（+3%），远低于字节跳动和"
                "阿里巴巴。AI原生应用方面，腾讯元宝经历多次战略摇摆推广后，"
                "日活跃留存率不足20%，尚未出现真正意义上的杀手级应用。"
            ),
            "possible_consequences": (
                "AI基础设施投资不足导致技术代差扩大；"
                "元宝等AI应用无法在大模型竞争中取得领先地位；"
                "投资者质疑导致估值承压（PE < 15倍）"
            ),
            "information_source": (
                "腾讯2024年Q4业绩公告；2025年Q4业绩公告（2026年3月）；"
                "科技媒体/36氪/财经报道；马化腾2024年Q4业绩电话会发言"
            ),
            "probability": 3, "impact": 4, "risk_score": 12,
            "risk_level": "high", "status": "active", "trend": "increasing",
            "response_type": "reduce",
            "current_response": (
                "2024-2025年在AI领域进行战略调整和加速：组织层面重组大模型研发"
                "体系，设立AI Infra和AI Data部门；技术层面自研混元大模型持续迭代，"
                "参数已超7000亿；AI推理平台帮助广告业务效率提升20%；"
                "产品层面腾讯元宝重新推广，混元模型API已对外开放"
            ),
            "suggested_improvement": (
                "(1)大幅提升AI资本开支至每年1,000-1,200亿元；"
                "(2)聚焦微信+AI差异化路线，停止与字节跳动的通用AI助手正面对抗；"
                "(3)适当降低股票回购力度释放资金用于AI研发；"
                "(4)建立AI投资委员会统一管理和安全治理"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于财报分析和科技媒体报道自动识别"
        },
        {
            "risk_code": "R5",
            "name": "游戏业务集中度风险",
            "category": "内部风险",
            "subcategory": "运营风险",
            "description": (
                "腾讯游戏收入高度依赖少数核心产品——《王者荣耀》（运营超10年）、"
                "《和平精英》、《英雄联盟》系列等在国内外面临用户疲劳和竞争压力。"
                "新品表现不及预期，海外工作室新品产出效率不足。"
            ),
            "possible_consequences": (
                "核心产品用户流失导致游戏收入下滑；新品不及预期影响增长预期；"
                "爆款缺失导致市盈率进一步下调"
            ),
            "information_source": "腾讯2024年报游戏业务分部分析；Sensor Tower/NPD/伽马数据行业报告",
            "probability": 3, "impact": 3, "risk_score": 9,
            "risk_level": "medium", "status": "active", "trend": "stable",
            "response_type": "reduce",
            "current_response": (
                "执行长青游戏策略，拥有14款年流水超40亿元游戏；"
                "加大海外游戏工作室投资和发行力度（Level Infinite平台）；探索AI+游戏创新"
            ),
            "suggested_improvement": (
                "加速AI+游戏融合创新（AI生成内容、动态剧情、智能NPC等）；"
                "增加游戏研发管线投入，降低对少数核心产品的依赖"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于游戏行业分析自动识别"
        },
        {
            "risk_code": "R6",
            "name": "数据安全与隐私合规风险",
            "category": "内部风险",
            "subcategory": "技术风险",
            "description": (
                "作为拥有13亿+用户的社交平台，腾讯面临严峻的数据安全和隐私保护"
                "挑战。算法透明度要求、用户隐私保护、数据跨境传输合规（特别是"
                "WeChat国际版）等问题日益突出。AI大模型训练涉及的数据版权和隐私"
                "问题也带来新的合规挑战。"
            ),
            "possible_consequences": (
                "数据泄露事件导致用户信任危机和监管重罚（最高可达年营收5%）；"
                "算法被强制公开损害商业竞争力；跨境数据传输受限影响国际业务"
            ),
            "information_source": (
                "腾讯2024年报；《个人信息保护法》《数据安全法》；"
                "网信办算法治理专项行动通知；腾讯2024年ESG报告"
            ),
            "probability": 3, "impact": 4, "risk_score": 12,
            "risk_level": "high", "status": "active", "trend": "increasing",
            "response_type": "reduce",
            "current_response": (
                "建立了用户隐私和数据安全管理制度体系，遵循《个人信息保护法》"
                "《数据安全法》等法规要求，实施数据分类分级、权限管理、安全审计"
                "等机制。2024年ESG报告特别增加了AI治理和气候变化应对等新兴议题"
            ),
            "suggested_improvement": (
                "建议发布年度AI透明度报告，向投资者和社会公众披露AI治理进展、"
                "挑战和关键指标；建立AI算法审计委员会，对AI模型的公平性、安全性"
                "和可解释性进行定期审查"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于数据安全法规和ESG报告自动识别"
        },
        {
            "risk_code": "R7",
            "name": "财务与投资管理风险",
            "category": "内部风险",
            "subcategory": "财务风险",
            "description": (
                "大规模AI资本开支（2024年768亿元）对现金流的挤压效应显现，"
                "现金储备同比下降7%。投资组合公允价值波动较大（投资公司权益"
                "公允价值5,698亿元），大规模回购（2024年1,120亿港元）与AI投资"
                "之间存在资金平衡的紧张关系。"
            ),
            "possible_consequences": (
                "现金流持续承压影响战略灵活性；投资组合减值影响报表利润；"
                "AI投资回报周期不确定性影响股价"
            ),
            "information_source": "腾讯2024年年度报告财务报表；2025年Q4业绩公告",
            "probability": 3, "impact": 3, "risk_score": 9,
            "risk_level": "medium", "status": "active", "trend": "stable",
            "response_type": "reduce",
            "current_response": (
                "保持稳健财务政策（净负债率40.8%）；经营活动现金流2,585亿元"
                "（+16.5%）；持有现金4,154亿元；适度降低回购节奏以平衡AI投资"
            ),
            "suggested_improvement": (
                "优化资本配置结构，适当降低回购力度（从800亿降至400-500亿港元），"
                "释放资金用于AI研发；建立投资组合压力测试机制，定期评估公允价值波动影响"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于财务报表分析自动识别"
        },
        {
            "risk_code": "R8",
            "name": "人才与组织管理风险",
            "category": "内部风险",
            "subcategory": "人力资源风险",
            "description": (
                "AI领域高端人才竞争激烈，字节跳动、百度、DeepSeek、阿里巴巴等"
                "竞争对手均在争夺顶级AI研究和工程人才。2024年查处触高压线案件"
                "100余起、解聘100余人，反映内部人员管理的合规压力。频繁的组织"
                "架构调整（2025年末重组大模型研发体系）可能带来管理不稳定。"
            ),
            "possible_consequences": (
                "核心AI人才流失至竞争对手；内部反腐案件损害公司声誉和员工士气；"
                "组织频繁调整导致执行效率下降"
            ),
            "information_source": "腾讯2024年报员工数据；腾讯阳光行为准则；科技媒体报道",
            "probability": 2, "impact": 3, "risk_score": 6,
            "risk_level": "medium", "status": "active", "trend": "stable",
            "response_type": "reduce",
            "current_response": (
                "通过引进前OpenAI研究员等高端人才强化团队；发布腾讯阳光行为准则"
                "建立高压线制度（舞弊/商业贿赂等一经发现立即解聘）；2025年首次"
                "将AI管理系统嵌入反腐和内部控制流程"
            ),
            "suggested_improvement": (
                "建立AI人才专项激励计划（包括薪酬竞争、学术研究自由度和创业孵化"
                "支持）；将风险管理文化融入组织DNA，在员工绩效考核中增加风险管理权重"
            ),
            "ai_identified": True,
            "ai_assessment_notes": "基于人力资源数据分析自动识别"
        }
    ]

    # 内控机制预设数据
    internal_controls = [
        {
            "control_code": "IC01",
            "name": "董事会审计委员会风险监督",
            "category": "治理结构",
            "description": "审计委员会由独立非执行董事组成，负责监督财务报告、外部审计、风险管理和内部控制有效性",
            "related_risks": "R1,R2,R3,R4,R5,R6,R7,R8",
            "responsible_dept": "董事会审计委员会",
            "effectiveness": "effective"
        },
        {
            "control_code": "IC02",
            "name": "三道防线模型",
            "category": "治理结构",
            "description": "第一道防线（业务部门日常风险管理）-> 第二道防线（风险管理和合规部门）-> 第三道防线（内部审计独立监督）",
            "related_risks": "R1,R2,R3,R4,R5,R6,R7,R8",
            "responsible_dept": "风险管理部",
            "effectiveness": "effective"
        },
        {
            "control_code": "IC03",
            "name": "反舞弊管理制度",
            "category": "管理制度",
            "description": "设立独立的反舞弊调查部门，2024年查处案件100余起，2025年首次将AI管理系统嵌入反腐流程",
            "related_risks": "R8",
            "responsible_dept": "反舞弊调查部",
            "effectiveness": "effective"
        },
        {
            "control_code": "IC04",
            "name": "用户隐私与数据安全管理制度",
            "category": "合规制度",
            "description": "遵循《个人信息保护法》《数据安全法》等法规，建立数据分类分级、权限管理、安全审计等机制",
            "related_risks": "R6",
            "responsible_dept": "数据合规部",
            "effectiveness": "partial"
        },
        {
            "control_code": "IC05",
            "name": "全面风险管理年度评估制度",
            "category": "管理制度",
            "description": "每年开展企业级风险评估，ESG关键议题纳入全面风险管理体系，覆盖经营、用户、产业、环境和社会维度",
            "related_risks": "R1,R2,R3,R4,R5,R6,R7,R8",
            "responsible_dept": "风险管理部",
            "effectiveness": "effective"
        }
    ]

    return {
        "coso_erm": coso_erm_framework,
        "risk_categories": risk_categories,
        "response_4t": response_4t,
        "tencent_risks": tencent_risks,
        "internal_controls": internal_controls
    }
