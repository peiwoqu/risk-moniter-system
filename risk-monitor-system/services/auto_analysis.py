# -*- coding: utf-8 -*-
"""M3/M4 自动分析引擎 — 基于企业风险数据生成针对性内控评估和监督改进建议"""
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# === 行业模板 ===
TEMPLATES = {
    "互联网科技": {
        "gov":    ("混合制", "7-11人/独董>=50%", "审计委员会,薪酬委员会,提名委员会,管治委员会,投资委员会",
                   "采用独立董事会架构，审计委员会由独立非执行董事组成，直接监督财务报告和内部控制有效性"),
        "lines":  [("第一道防线","各事业群(BG)","日常风险管理、操作风险识别、流程合规"),
                   ("第二道防线","风险管理部/合规部","建立风控框架、制定合规政策、KRI监控"),
                   ("第三道防线","内部审计部","独立审计、评估内控有效性")],
        "ctrls":  [("反舞弊管理","管理制度","独立调查部门+举报渠道，对舞弊零容忍"),
                   ("数据安全与隐私保护","合规制度","遵循个保法/数安法，分类分级+权限管理+安全审计"),
                   ("AI安全治理","管理制度","AI安全护栏+算法审计+公平性评估，定期发布透明度报告"),
                   ("全面风险管理","管理制度","年度企业级评估，ESG纳入ERM，覆盖经营/用户/产业/环境/社会"),
                   ("供应商ESG管理","合规制度","ESG标准纳入准入，覆盖环保/劳工/反腐")],
        "improve":["设立CRO直接向董事会汇报","建立AI风险管理专项委员会","加强跨境合规协同平台","风险管理文化融入绩效考核"],
        "sup_mechs": [("董事会审计委员会监督","board","每季度审阅风险管理现状"),("内部审计部门","internal_audit","持续审计，直接向审计委员会汇报"),
                      ("外部审计师","external","年度审计，独立意见"),("监管机构监督","supervisory","接受证监会/网信办等检查"),("举报与合规调查","compliance","独立反舞弊部门+举报渠道")],
        "disc_types": ["年度报告","ESG报告","季度公告","临时公告","反舞弊通报"],
        "sup_improve":["设立CRO向董事会汇报","建立AI风险管理专项委员会","建立举报人保护制度","加强跨境合规协同","风险管理纳入绩效考核"],
    },
    "制造业": {
        "gov":    ("双层制/混合制", "7-15人/独董>=1/3", "审计委员会,薪酬委员会,提名委员会,战略委员会",
                   "设立专门委员会进行专业化治理，大型企业设有战略委员会指导长期发展"),
        "lines":  [("第一道防线","各工厂/事业部","现场安全管理、质量控制、生产风险识别"),
                   ("第二道防线","风险管理部/EHS部","质量安全管理体系、风险监测、应急演练"),
                   ("第三道防线","内部审计/第三方审核","定期审计、安全检查、体系认证审核")],
        "ctrls":  [("安全生产管理","管理制度","HSE体系+定期检查+应急演练，责任到人"),
                   ("供应链风险管理","管理制度","多源供应+关键供应商评估+中断应急预案"),
                   ("质量管理","管理制度","ISO9001体系+全过程质控+追溯召回机制"),
                   ("环境与ESG管理","合规制度","碳排放监测+碳中和路线图+定期ESG披露"),
                   ("技术研发管理","管理制度","知识产权保护+核心技术专利布局+下一代技术跟踪")],
        "improve":["建立供应链风险实时预警系统","设立技术风险评估专项团队","加强海外工厂本地化合规","完善产能规划与市场需求预测"],
        "sup_mechs": [("董事会审计委员会监督","board","每季度审阅"),("安全生产委员会","board","每月安全审查"),
                      ("内部审计部","internal_audit","持续审计"),("第三方认证审核","external","年度ISO审核"),("政府安监环保督查","supervisory","不定期检查")],
        "disc_types": ["年度报告","ESG报告","季度报告","环境信息披露","安全生产报告"],
        "sup_improve":["建立供应链风险实时监控预警","完善产能规划市场预测","加强海外工厂本地化合规","建立产品全生命周期追溯召回体系"],
    },
    "金融": {
        "gov":    ("独立董事制度+外部监管", "10-19人/独董>=1/3", "审计委员会,风险管理委员会,薪酬委员会,提名委员会,关联交易控制委员会",
                   "金融机构受严格监管治理要求，需设立独立的风险管理委员会和关联交易控制委员会"),
        "lines":  [("第一道防线","各业务条线","客户尽调、交易监控、信用评估"),
                   ("第二道防线","风险管理部/合规部","风险政策、限额监控、AML管理"),
                   ("第三道防线","内部审计/外部审计/监管","独立审计、压力测试、合规检查")],
        "ctrls":  [("信用风险管理","管理制度","内部评级体系+授信审批+压力测试"),
                   ("市场风险管理","管理制度","VaR模型+风险限额+利率汇率监控"),
                   ("操作风险管理","管理制度","损失数据库+KRI监控"),
                   ("反洗钱AML","合规制度","KYC程序+交易监控+可疑报告"),
                   ("流动性风险管理","管理制度","LCR监控+应急预案+压力测试")],
        "improve":["加强金融科技风险管理","完善资本充足率前瞻规划","提升数字化风控能力"],
        "sup_mechs": [("董事会风险管理委员会","board","每季度审批风险偏好"),("首席风险官CRO","board","持续独立汇报"),
                      ("内部审计部","internal_audit","全覆盖审计"),("外部审计师","external","年度审计"),("监管机构","supervisory","持续监管")],
        "disc_types": ["年度报告","资本充足率报告","风险管理制度报告","季度报告","重大事项公告"],
        "sup_improve":["提升压力测试覆盖范围和频次","加强金融科技第三方风险管理","完善气候和环境风险评估披露"],
    },
    "消费": {
        "gov":    ("独立董事制度", "7-11人/独董>=1/3", "审计委员会,薪酬委员会,提名委员会,战略委员会",
                   "治理重点在于品牌保护、质量安全和渠道管理"),
        "lines":  [("第一道防线","各品牌事业部/区域","质量检测、渠道合规、投诉处理"),
                   ("第二道防线","质量部/法务部","质量体系、品牌保护、合规审查"),
                   ("第三道防线","内部审计/第三方","定期审计、飞行检查、满意度调查")],
        "ctrls":  [("食品安全管理","管理制度","HACCP+原料追溯+成品检验"),
                   ("品牌与声誉管理","管理制度","舆情监控+危机公关+防伪管理"),
                   ("渠道管理","管理制度","经销商准入考核+库存监控+防窜货"),
                   ("消费者数据保护","合规制度","遵循个保法+加密存储+脱敏处理"),
                   ("产品研发管理","管理制度","新品流程+消费者洞察+市场趋势跟踪")],
        "improve":["建立全渠道数字化追溯系统","完善消费者投诉快速响应机制","加强线上渠道价格管控"],
        "sup_mechs": [("董事会审计委员会监督","board","每季度审阅"),("内部审计部","internal_audit","持续审计"),
                      ("外部审计师","external","年度审计"),("市场监管部门","supervisory","不定期检查"),("消费者投诉热线","compliance","持续受理")],
        "disc_types": ["年度报告","ESG报告","季度报告","食品安全报告","品牌建设报告"],
        "sup_improve":["建立全渠道数字化追溯系统","完善消费者投诉快速响应","加强线上渠道价格管控","强化品牌危机公关能力"],
    },
    "能源": {
        "gov":    ("双层制", "9-15人", "审计委员会,薪酬委员会,提名委员会,战略委员会,安全环保委员会",
                   "面临安全生产和环境保护的严格要求，设立专门的安全环保委员会"),
        "lines":  [("第一道防线","各矿区/油田/电站","安全操作、设备维护、环境监测"),
                   ("第二道防线","HSE部/风险管理部","HSE管理+风险评估+应急演练"),
                   ("第三道防线","内部审计/政府安监","安全检查、环保督查、体系审核")],
        "ctrls":  [("安全生产责任制","管理制度","从管理层到一线层层落实，安全一票否决"),
                   ("环境保护管理","合规制度","碳排放监测+减排计划+污染物达标+环境预案"),
                   ("能源价格风险管理","管理制度","期货期权对冲+价格预警机制"),
                   ("海外业务风险管理","管理制度","地缘风险评估+海外资产保护"),
                   ("承包商管理","管理制度","准入考核+定期安全环保评估")],
        "improve":["加快能源转型战略落地","建立智能化安全生产监控","加强海外资产合规管理"],
        "sup_mechs": [("董事会审计委员会监督","board","每季度审阅"),("安全环保委员会","board","每月审查"),
                      ("内部审计部","internal_audit","持续审计"),("政府安监环保督查","supervisory","不定期"),("第三方HSE审核","external","年度")],
        "disc_types": ["年度报告","ESG报告","环境信息披露","安全生产报告","碳排报告"],
        "sup_improve":["加快能源转型战略落地","建立智能化安全生产监控系统","加强海外资产合规管理","建立统一的全球HSE标准"],
    },
}


class AutoAnalysisEngine:

    def __init__(self):
        pass

    # ==================== M3: 内控机制 ====================

    def analyze_all_m3(self, enterprise_name: str, industry: str,
                       risks: List[Dict], raw_text: str = '') -> Dict:
        """生成M3全部四个子模块的详细分析"""
        ind = self._match(industry)
        t = TEMPLATES[ind]
        rlist = sorted(risks, key=lambda r: r.get('risk_score', 0), reverse=True)
        critical = [r for r in rlist if r.get('risk_score', 0) >= 15]
        high = [r for r in rlist if r.get('risk_score', 0) >= 10]

        # 6.1 治理结构
        g = self._analyze_gov(enterprise_name, ind, t, rlist, critical)

        # 6.2 三道防线
        lines = self._analyze_lines(ind, t, rlist, critical)

        # 6.3 内控制度
        ctrls = self._analyze_controls(ind, t, rlist)

        # 6.4 覆盖评估
        cov = self._analyze_coverage(ctrls, rlist)

        return {"governance": g, "three_lines": lines, "controls": ctrls, "coverage": cov,
                "industry": ind}

    def _analyze_gov(self, name, ind, t, rlist, critical):
        gt = t["gov"]
        risk_cats = list(set(r.get('subcategory','') for r in rlist))

        # 判断是否需要额外委员会
        extra = []
        if any('监管' in c or '合规' in c or '政策' in c for c in risk_cats):
            extra.append({"name":"合规与风险管理委员会","reason":f"鉴于{name}面临监管政策风险（得分{next((r.get('risk_score',0) for r in rlist if '监管' in r.get('subcategory','') or '合规' in r.get('subcategory','')),'?')}），"
                         "需设立专门的合规与风险管理委员会，定期审查合规体系和监管变化趋势"})
        if any('技术' in c or '变革' in c or '创新' in c or 'AI' in c for c in risk_cats):
            extra.append({"name":"技术与创新委员会","reason":f"鉴于{name}面临技术迭代风险，需设立技术与创新委员会，"
                         "监督研发投入方向和核心技术布局，评估下一代技术对现有业务的颠覆风险"})
        if any('安全' in c or '生产' in c for c in risk_cats):
            extra.append({"name":"安全生产委员会","reason":"鉴于安全生产风险的重大性，需设立专门的安全生产委员会"})

        # 独董占比建议
        if len(critical) >= 3:
            indep_advice = "建议将独立董事占比提升至2/3以上，以增强对重大风险的独立监督能力"
        elif len(critical) >= 1:
            indep_advice = "建议独立董事占比维持在50%以上，确保审计委员会由独立董事组成"
        else:
            indep_advice = "建议至少1/3独立董事，确保治理制衡"

        # 董事会规模建议
        board_advice = f"建议董事会规模{gt[1]}，根据{name}的业务复杂度和风险敞口，" \
                       f"当前{'高风险环境' if len(critical)>=3 else '正常风险环境'}下宜设{'较大规模' if len(critical)>=3 else '适中规模'}董事会"

        return {
            "structure_type": gt[0],
            "typical_board": gt[1],
            "committees": gt[2],
            "description": gt[3],
            "independence_ratio": ">=50%" if ind in ["互联网科技","金融"] else ">=1/3",
            "board_advice": board_advice,
            "indep_advice": indep_advice,
            "extra_committees": extra,
            "critical_risks_impact": f"当前{len(critical)}项重大风险对治理结构提出的要求：需确保董事会层面有足够专业能力"
                                   f"监督{'、'.join(r.get('name','')[:10] for r in critical[:3])}等关键风险领域",
            "recommendation": self._gov_recommendation(name, ind, critical),
        }

    def _gov_recommendation(self, name, ind, critical):
        if len(critical) >= 3:
            return (f"鉴于{name}面临{len(critical)}项重大风险，建议：①立即评估董事会专门委员会的设置是否充分；"
                    f"②确保审计委员会具有风险管理专业能力；③考虑设立首席风险官(CRO)职位直接向董事会汇报；"
                    f"④增加董事会对重大风险的审阅频次至每月一次")
        return (f"建议{name}：①定期评估治理结构的有效性；②确保各专门委员会充分履职；"
                f"③建立董事会层面的风险报告机制；④将风险管理纳入董事会年度议程")

    def _analyze_lines(self, ind, t, rlist, critical):
        lines = []
        for i, (ln, ld, lr) in enumerate(t["lines"]):
            # 根据风险定制各防线
            if i == 0:  # 第一道
                duty = lr
                if critical:
                    top_cats = list(set(r.get('subcategory','') for r in critical[:3]))
                    duty += f"。基于{len(critical)}项重大风险，需重点嵌入{'、'.join(top_cats)}的识别与控制流程"
                improve = "各业务单元应建立风险自查清单，将重大风险指标纳入日常运营KPI考核"
            elif i == 1:  # 第二道
                duty = lr
                if critical:
                    duty += f"。针对{len(critical)}项重大风险需建立专项KRI（关键风险指标），实时监控风险变化"
                improve = "应建立风险指标仪表盘，实现重大风险的实时可视化监控和自动预警"
            else:  # 第三道
                duty = lr
                if critical:
                    duty += f"。建议对{'、'.join(r.get('name','')[:12] for r in critical[:2])}等重大风险增加专项审计频次"
                improve = "建议制定基于风险水平的差异化审计频次：重大风险每季度审计，高度关注风险每半年审计"

            lines.append({"line": i+1, "name": ln, "department": ld, "responsibility": duty,
                         "effectiveness": "需持续加强" if i<2 else "有效",
                         "improvement": improve,
                         "risk_focus": f"重点关注{len(critical)}项重大风险和{len([r for r in rlist if r.get('risk_score',0)>=10])}项高度关注风险"})
        return lines

    def _analyze_controls(self, ind, t, rlist):
        ctrls = []
        for i, (name, cat, desc) in enumerate(t["ctrls"]):
            code = f"IC-{ind[0]}{i+1:02d}"
            # 匹配覆盖的风险
            covered = []
            for r in rlist:
                rc = r.get('risk_code',''); rn = r.get('name',''); sc = r.get('subcategory','')
                if any(kw.lower() in (rn+sc+desc).lower() for kw in self._ctrl_kw(name)):
                    covered.append(rc)
            unique = list(set(covered))[:5]

            # 有效性评估
            score = sum(r.get('risk_score',0) for r in rlist if r.get('risk_code','') in unique)
            if len(unique) >= 2 and score >= 30:
                eff = "需紧急加强"; eff_class = "danger"
                eff_detail = f"该制度覆盖了{len(unique)}项高风险（合计{score}分），但现有控制力度不足。建议立即评估控制有效性，增加资源投入，提升监控频次至每周。"
            elif len(unique) >= 1:
                eff = "部分有效"; eff_class = "warning"
                eff_detail = f"覆盖{len(unique)}项风险，控制措施基本到位，但存在优化空间。建议完善控制流程文档化，定期测试控制有效性。"
            else:
                eff = "待评估"; eff_class = "secondary"
                eff_detail = "该制度与当前识别风险的直接关联度较低，建议评估其适用性，或将其与具体风险建立明确关联。"

            # 针对性改进建议
            imp = self._ctrl_improvement(name, unique, rlist)

            ctrls.append({"control_code": code, "name": name, "category": cat, "description": desc,
                         "covers_risks": unique,
                         "covers_risk_details": [{"code":r.get('risk_code',''),"name":r.get('name',''),"score":r.get('risk_score',0)}
                                                  for r in rlist if r.get('risk_code','') in unique],
                         "effectiveness": eff, "effectiveness_class": eff_class,
                         "effectiveness_detail": eff_detail, "improvement": imp})
        return ctrls

    def _ctrl_kw(self, name):
        m = {
            "反舞弊管理": ["舞弊","腐败","合规","人力资源","内部"],
            "数据安全": ["数据","隐私","安全","信息","技术","合规"],
            "AI安全": ["AI","人工智","算法","模型","技术"],
            "安全生产": ["安全","生产","事故","HSE","运营"],
            "供应链": ["供应链","供应商","原材料","采购","运营","中断"],
            "质量管理": ["质量","品控","产品","召回","运营"],
            "环境": ["环境","ESG","碳","排放","可持续","合规"],
            "技术研发": ["技术","研发","创新","专利","知识","迭代","颠覆"],
            "信用风险": ["信用","违约","坏账","不良","财务"],
            "市场风险": ["市场","汇率","利率","波动","财务"],
            "操作风险": ["操作","内控","流程","欺诈","合规"],
            "反洗钱": ["洗钱","AML","KYC","合规","监管"],
            "流动性": ["流动","资金","存款","兑付","财务"],
            "食品安全": ["食品","安全","质量","卫生","召回"],
            "品牌": ["品牌","声誉","舆情","口碑"],
            "渠道": ["渠道","经销商","库存","分销","窜货"],
            "消费者": ["消费者","数据","隐私","个保"],
            "全面风险": ["风险","评估","监控"],
            "供应商": ["供应","ESG","环保","劳工"],
            "能源价格": ["价格","波动","汇率","期货"],
            "海外业务": ["海外","地缘","政治","国际"],
            "承包商": ["承包","外包","供应","安全"],
            "产品研发": ["研发","创新","市场","趋势"],
        }
        for k, v in m.items():
            if k in name: return v
        return [name]

    def _ctrl_improvement(self, name, covered, rlist):
        risk_names = [r.get('name','') for r in rlist if r.get('risk_code','') in covered]
        if not risk_names:
            return f"建议将「{name}」制度与具体风险建立明确的关联映射，明确责任部门和监控指标"

        top_risk = risk_names[0] if risk_names else "主要风险"
        improvements = {
            "反舞弊管理": f"针对{'、'.join(risk_names[:2])}等风险，建立AI驱动的异常行为检测系统，将合规培训覆盖率提升至100%，每年至少进行一次全员反舞弊认证",
            "数据安全": f"针对{'、'.join(risk_names[:2])}等风险，实施数据分类分级保护，建立数据泄露72小时应急响应机制，每季度进行渗透测试和安全审计",
            "AI安全": f"针对{'、'.join(risk_names[:2])}等风险，建立AI模型全生命周期安全评估流程，每半年发布AI治理透明度报告，设立独立AI伦理审查委员会",
            "安全生产": f"针对{'、'.join(risk_names[:2])}等风险，建立IoT实时安全监控系统，实施安全一票否决制，每季度进行全场景应急演练",
            "供应链": f"针对{'、'.join(risk_names[:2])}等风险，建立关键原材料价格预警系统，发展备选供应商（至少2家），建立供应链中断三级应急预案",
            "质量管理": f"针对{'、'.join(risk_names[:2])}等风险，建立全流程数字化质量追溯系统，实施供应商质量飞检制度，完善产品召回预案",
            "环境": f"针对{'、'.join(risk_names[:2])}等风险，制定科学碳中和路线图和时间表，建立碳排放实时监测系统，每季度披露ESG关键指标进展",
            "技术研发": f"针对{'、'.join(risk_names[:2])}等风险，建立技术路线图定期评审机制（每半年），加大前沿技术预研投入（营收3%以上），建立核心专利防御组合",
            "信用风险": f"针对{'、'.join(risk_names[:2])}等风险，优化内部信用评级模型，实施动态授信调整，每季度进行信用风险压力测试",
            "市场风险": f"针对{'、'.join(risk_names[:2])}等风险，建立VaR日监控体系，设置多级风险限额并自动预警，定期回测和模型验证",
            "流动性": f"针对{'、'.join(risk_names[:2])}等风险，建立LCR/NSFR日监控，制定分级流动性应急预案，定期进行流动性压力测试",
            "食品安全": f"针对{'、'.join(risk_names[:2])}等风险，建立从原料到终端的全链条追溯，实施飞行检查制度，完善问题产品2小时内启动召回",
            "品牌": f"针对{'、'.join(risk_names[:2])}等风险，建立7×24小时舆情监控系统，制定分级危机公关预案，定期进行品牌健康度评估",
            "渠道": f"针对{'、'.join(risk_names[:2])}等风险，建立经销商数字化管理平台，实时监控渠道库存和价格，实施窜货自动预警",
            "消费者": f"针对{'、'.join(risk_names[:2])}等风险，实施数据加密和脱敏处理，定期进行隐私合规审计，建立用户数据泄露应急响应机制",
        }

        for k, v in improvements.items():
            if k in name:
                return v
        return f"针对{'、'.join(risk_names[:2])}等风险，建立专项管理制度，明确责任人和监控指标，每季度评估制度有效性"

    def _analyze_coverage(self, ctrls, rlist):
        all_codes = {r.get('risk_code','') for r in rlist}
        covered_codes = set()
        for c in ctrls:
            for rc in c["covers_risks"]:
                covered_codes.add(rc)

        uncovered = [r for r in rlist if r.get('risk_code','') not in covered_codes]
        cov_rate = len(covered_codes & all_codes) / max(len(rlist), 1) * 100

        if cov_rate >= 80:
            cov_assess = "内控覆盖率较高，整体风险管控体系基本完善。但仍需关注未覆盖的风险领域。"
        elif cov_rate >= 50:
            cov_assess = "内控覆盖率处于中等水平，存在明显的管理真空区域，需尽快建立缺失的控制制度。"
        else:
            cov_assess = "内控覆盖率严重不足，大量风险处于无管理状态，需立即进行全面内控制度建设。"

        # 针对性建议
        suggestions = []
        if uncovered:
            uncovered_names = [r.get('name','') for r in uncovered[:3]]
            suggestions.append(f"针对未覆盖的风险（{'、'.join(uncovered_names)}），需尽快制定专项内控制度")
        critical_uncovered = [r for r in uncovered if r.get('risk_level')=='critical']
        if critical_uncovered:
            suggestions.append(f"⚠️ {len(critical_uncovered)}项重大风险（{'、'.join(r.get('name','') for r in critical_uncovered)}）未被任何内控制度覆盖，需立即处理")

        # 行业通用建议
        ind = self._match('')
        suggestions.append("定期（至少每年一次）进行内控有效性的全面评估和更新")
        suggestions.append("建立内控制度与风险的双向追溯机制，确保新增风险及时纳入内控体系")
        suggestions.append("推动内控流程的数字化和自动化，减少人工操作风险")

        return {"controls": ctrls, "total": len(ctrls), "total_risks": len(rlist),
                "covered_risks": len(covered_codes & all_codes),
                "coverage_rate": f"{cov_rate:.0f}%",
                "coverage_assessment": cov_assess,
                "uncovered_risks": [{"risk_code":r.get('risk_code',''),"name":r.get('name',''),"risk_score":r.get('risk_score',0),"risk_level":r.get('risk_level','')} for r in uncovered],
                "improvement_suggestions": suggestions}

    # ==================== M4: 监督改进 ====================

    def analyze_all_m4(self, enterprise_name: str, industry: str,
                       risks: List[Dict], m3_coverage: Dict) -> Dict:
        ind = self._match(industry)
        t = TEMPLATES[ind]
        rlist = sorted(risks, key=lambda r: r.get('risk_score', 0), reverse=True)
        crit = [r for r in rlist if r.get('risk_score', 0) >= 15]
        high = [r for r in rlist if r.get('risk_score', 0) >= 10]

        # 7.1 监督机制
        mechs = self._analyze_mechanisms(ind, t, crit, rlist, enterprise_name)

        # 7.2 信息披露
        discs = self._analyze_disclosures(ind, t, rlist, enterprise_name)

        # 7.3 问题与改进
        issues = self._identify_issues(rlist, m3_coverage, enterprise_name)

        # 7.4 PDCA
        pdca = self._analyze_pdca(rlist, issues, crit, enterprise_name)

        # 监督评估
        if len(crit) >= 3:
            assess = (f"基于{len(crit)}项重大风险和{len(high)}项高度关注风险的综合分析，{enterprise_name}的监督体系面临严峻挑战。"
                      f"重大风险的高集中度表明现有监督机制可能存在盲区。建议立即：①提升监督层级至董事会层面；"
                      f"②增加监督频次；③建立实时风险监控仪表盘；④引入外部独立评估。")
        elif len(crit) >= 1:
            assess = (f"基于{len(crit)}项重大风险的分析，{enterprise_name}的监督体系基本有效，但存在改进空间。"
                      f"建议：①对重大风险建立专项监督机制；②优化监督频次；③完善信息披露的定量化程度。")
        else:
            assess = (f"{enterprise_name}当前未识别出重大风险（>=15分），监督体系运行正常。"
                      f"建议保持现有监督频次，重点关注风险趋势变化，防止风险升级。")

        return {"mechanisms": mechs, "disclosures": discs, "issues": issues,
                "pdca": pdca, "supervision_assessment": assess,
                "industry": ind}

    def _analyze_mechanisms(self, ind, t, crit, rlist, name):
        mechs = []
        for mn, mt, desc in t["sup_mechs"]:
            # 高风险时调整频率和建议
            if len(crit) >= 3:
                if mt == "board":
                    freq = "建议增至每月"
                    eff = "需立即加强"
                    detail = f"鉴于{name}面临{len(crit)}项重大风险，董事会层面的监督频次需从常规水平提升至每月一次，重点审查重大风险的应对进展和控制效果。建议每次会议预留专门时段讨论风险议题。"
                elif mt == "internal_audit":
                    freq = "持续（建议增加专项审计）"
                    eff = "需加强"
                    detail = f"针对{len(crit)}项重大风险，内部审计需增加专项审计项目，优先覆盖{'、'.join(r.get('name','')[:15] for r in crit[:2])}等高风险领域。建议采用风险导向审计方法，动态调整审计计划。"
                else:
                    freq = "建议增加频次"
                    eff = "有效"
                    detail = f"在{len(crit)}项重大风险的背景下，建议适当增加监督频次或深度，确保全面覆盖高风险领域。"
            elif len(crit) >= 1:
                freq = "建议保持或适度增加"
                eff = "基本有效"
                detail = f"当前风险态势下，该监督机制基本满足需要，但建议关注{name}面临的主要风险变化，适时调整监督力度。"
            else:
                freq = "保持常规频次"
                eff = "有效"
                detail = "当前风险态势可控，该监督机制运行正常，建议保持现有监督安排。"

            mechs.append({"mechanism_name": mn, "mechanism_type": mt,
                         "description": desc, "frequency": freq,
                         "effectiveness": eff, "effectiveness_detail": detail,
                         "responsible_party": mn.split("监督")[0] if "监督" in mn else "风险管理部"})
        return mechs

    def _analyze_disclosures(self, ind, t, rlist, name):
        crit_count = len([r for r in rlist if r.get('risk_score', 0) >= 15])
        discs = []
        for dt in t["disc_types"]:
            if crit_count >= 3:
                status, advice = "需加强", f"建议在{dt}中大幅增加风险因素的定量披露（包括具体的风险敞口数据、压力测试结果、应对措施的时间表）"
            elif crit_count >= 1:
                status, advice = "基本合规", f"建议在{dt}中增加风险分析的深度，提供更具体的量化指标和应对进展"
            else:
                status, advice = "合规", f"保持现有披露水平，关注行业最佳实践，适时提升披露质量"
            discs.append({"disclosure_type": dt, "risk_disclosure_status": status,
                         "recommendation": advice})
        return discs

    def _identify_issues(self, rlist, coverage, name):
        issues = []
        iss_id = 1
        crit = [r for r in rlist if r.get('risk_level') == 'critical']
        high = [r for r in rlist if r.get('risk_level') == 'high']

        # 1. 每项重大风险→自动生成一个问题
        for r in crit:
            sc = r.get('risk_score', 0)
            p = r.get('probability', 0)
            imp = r.get('impact', 0)
            desc = (f"「{r.get('name','')}」风险得分{sc}分（P={p}×I={imp}），达到重大风险水平。"
                    f"该风险的高可能性（{p}/5）{'和极端影响（' + str(imp) + '/5）' if imp>=4 else ''}表明这不是一个可以常规管理的一般风险，"
                    f"需要企业最高管理层的直接关注和专项资源投入。")
            action = (f"①建立「{r.get('name','')}」专项风险管理团队，明确负责人和汇报线（建议直接向CEO/董事会汇报）；"
                     f"②制定分级应急预案（蓝色/黄色/橙色/红色），明确各等级的触发条件和响应措施；"
                     f"③设立KRI（关键风险指标），{'每日' if sc >= 16 else '每周'}监控，超过阈值自动预警；"
                     f"④进行压力测试和情景分析，量化最坏情况下的财务和运营影响；"
                     f"⑤{'立即' if sc >= 16 else '30日内'}启动应对方案，60日内完成首轮全面评估。")
            issues.append({"auto_generated": True, "id": iss_id,
                          "title": f"重大风险应对不足：{r.get('risk_code','')} {r.get('name','')}",
                          "severity": "critical", "source": "auto_analysis",
                          "description": desc, "proposed_action": action,
                          "deadline": "立即启动，30日内提交方案" if sc >= 16 else "30日内启动，60日内提交方案",
                          "related_risk": r.get('risk_code','')})
            iss_id += 1

        # 2. 高度关注风险
        for r in high:
            if len(crit) >= 3:
                continue  # 重大风险太多时跳过
            sc = r.get('risk_score', 0)
            action = (f"①将「{r.get('name','')}」纳入月度风险管理报告；②建立KRI指标并每月监控；"
                     f"③制定应对预案，防止风险升级为重大风险")
            issues.append({"auto_generated": True, "id": iss_id,
                          "title": f"加强风险监控：{r.get('risk_code','')} {r.get('name','')}",
                          "severity": "high", "source": "auto_analysis",
                          "description": f"风险得分{sc}，属于高度关注级别，需建立常态化监控机制，防止进一步恶化。",
                          "proposed_action": action, "deadline": "60日内完成",
                          "related_risk": r.get('risk_code','')})
            iss_id += 1

        # 3. 内控覆盖率不足
        uncovered = coverage.get('uncovered_risks', [])
        if uncovered:
            crit_uncovered = [u for u in uncovered if u.get('risk_level') == 'critical']
            names = [u.get('name','') for u in uncovered[:3]]
            action = (f"①针对{'、'.join(names)}制定专项内控制度，明确控制目标、控制活动和验证方法；"
                     f"②将未覆盖风险纳入下一期内控体系建设计划；"
                     f"③{'⚠️ 优先处理重大风险的制度覆盖，这属于紧急事项。' if crit_uncovered else '按计划推进，90日内完成制度初稿。'}")
            issues.append({"auto_generated": True, "id": iss_id,
                          "title": f"内控制度未完全覆盖风险（覆盖率{coverage.get('coverage_rate','?')}）",
                          "severity": "critical" if crit_uncovered else "high",
                          "source": "auto_analysis",
                          "description": f"当前内控制度覆盖率{coverage.get('coverage_rate','?')}，未覆盖{len(uncovered)}项风险，其中{'包含重大风险' if crit_uncovered else '不包含重大风险'}。风险管理的基本原则要求所有重大风险必须有对应的控制措施。",
                          "proposed_action": action,
                          "deadline": "立即处理" if crit_uncovered else "90日内",
                          "related_risk": ",".join(u.get('risk_code','') for u in uncovered[:3])})
            iss_id += 1

        # 4. 趋势上升风险
        increasing = [r for r in rlist if r.get('trend') == 'increasing']
        if len(increasing) >= 2:
            inc_names = [r.get('name','')[:20] for r in increasing[:4]]
            action = (f"①对{'、'.join(inc_names)}等{len(increasing)}项上升趋势风险进行根因分析，"
                     f"区分外部环境变化和内部控制弱化两类原因；"
                     f"②对因内部控制弱化导致的风险上升，立即制定控制强化计划；"
                     f"③将上升趋势风险纳入月度重点监控清单，设定趋势反转目标。")
            issues.append({"auto_generated": True, "id": iss_id,
                          "title": f"{len(increasing)}项风险呈上升趋势需重点遏制",
                          "severity": "high", "source": "auto_analysis",
                          "description": f"以下{len(increasing)}项风险的趋势为上升：{'、'.join(inc_names)}。风险趋势持续上升可能预示控制体系存在薄弱环节，需进行系统性排查。",
                          "proposed_action": action, "deadline": "30日内完成根因分析"})
            iss_id += 1

        # 5. 风险评级集中问题
        if len(crit) >= 3:
            issues.append({"auto_generated": True, "id": iss_id,
                          "title": "重大风险集中度过高，风险管理体系承压",
                          "severity": "critical", "source": "auto_analysis",
                          "description": f"当前识别出{len(crit)}项重大风险（>=15分），同时存在{len(high)}项高度关注风险。重大风险的集中度表明企业面临系统性挑战，单一风险之间的关联效应可能放大整体风险敞口。",
                          "proposed_action": f"①进行风险关联性分析，识别风险之间的传导和放大机制；②建立企业级风险仪表盘，实现所有重大风险的一屏统览；③制定综合风险应对方案，而非逐项独立应对；④考虑设立首席风险官(CRO)统筹全局风险管理。",
                          "deadline": "立即启动"})

        return issues

    def _analyze_pdca(self, rlist, issues, crit, name):
        now = datetime.now()
        total = len(rlist)

        phases = [
            ("P-计划", f"基于{total}项风险的全面评估（{len(crit)}项重大、{len([r for r in rlist if r.get('risk_level')=='high'])}项高度关注），制定{now.year}年度风险管理改进计划。优先排序：①重大风险专项应对方案；②内控体系强化；③监督机制优化。"),
            ("D-执行", f"实施改进方案：①建立健全{len(crit)}项重大风险的KRI监控体系；②完善内控制度覆盖全部风险；③开展全员风险管理培训；④建立风险管理信息系统（RMIS）。"),
            ("C-检查", f"效果评估：①重大风险指标变化趋势（期望≥70%的风险趋势由上升转为稳定/下降）；②内控覆盖率从当前水平提升至≥85%；③自动识别问题按期整改率≥90%。"),
            ("A-改进", f"基于检查结果持续优化：①总结{len(issues)}项自动识别问题的整改经验；②将有效措施固化为制度；③制定下一年度改进计划；④推动风险管理从被动合规向主动预防转型。"),
        ]

        lessons = [
            f"共识别{total}项风险，覆盖{len(set(r.get('subcategory','') for r in rlist))}个类别，反映{name}面临多维度的风险挑战",
            f"重大风险{len(crit)}项需最高管理层直接介入，一般性应对不足以有效控制",
            f"内控覆盖度和监督频次需与风险等级匹配，高风领域需更强力度",
            f"风险管理需要从「事后应对」转向「事前预防」，建立前瞻性风险预警能力",
        ]

        return {"current_cycle": f"{now.year}年度风险管理改进周期",
                "phases": phases, "lessons_learned": lessons}

    # ==================== 工具 ====================

    def _match(self, industry):
        if not industry: return "互联网科技"
        for k in TEMPLATES:
            if k in industry or industry in k: return k
        return "互联网科技"
