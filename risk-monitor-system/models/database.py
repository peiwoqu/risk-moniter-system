# -*- coding: utf-8 -*-
"""Agent智能风险监控管理系统 - 数据库模型 (五模块完整版)"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ==================== 基础模型 ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'username':self.username,'role':self.role,'email':self.email,'created_at':self.created_at.isoformat() if self.created_at else None}

class Enterprise(db.Model):
    __tablename__ = 'enterprises'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    stock_code = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    raw_data_text = db.Column(db.Text)
    source_files = db.Column(db.Text)
    risk_count = db.Column(db.Integer, default=0)
    last_analyzed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    risks = db.relationship('Risk', backref='enterprise', lazy=True, cascade='all, delete-orphan')
    controls = db.relationship('InternalControl', backref='enterprise', lazy=True, cascade='all, delete-orphan')
    gov_structures = db.relationship('GovernanceStructure', backref='enterprise', lazy=True, cascade='all, delete-orphan')
    supervision_mechanisms = db.relationship('SupervisionMechanism', backref='enterprise', lazy=True, cascade='all, delete-orphan')
    disclosures = db.relationship('InformationDisclosure', backref='enterprise', lazy=True, cascade='all, delete-orphan')
    improvement_issues = db.relationship('ImprovementIssue', backref='enterprise', lazy=True, cascade='all, delete-orphan')
    improvements = db.relationship('ContinuousImprovement', backref='enterprise', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {'id':self.id,'name':self.name,'stock_code':self.stock_code,'industry':self.industry,'description':(self.description or '')[:200],'raw_data_length':len(self.raw_data_text or ''),'risk_count':self.risk_count,'last_analyzed':self.last_analyzed.isoformat() if self.last_analyzed else None,'created_at':self.created_at.isoformat() if self.created_at else None}

# ==================== M2: 风险分析模块 ====================

class Risk(db.Model):
    __tablename__ = 'risks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=True)
    risk_code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    description = db.Column(db.Text)
    possible_consequences = db.Column(db.Text)
    information_source = db.Column(db.Text)
    probability = db.Column(db.Integer, default=3)
    impact = db.Column(db.Integer, default=3)
    risk_score = db.Column(db.Integer)
    risk_level = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    trend = db.Column(db.String(20), default='stable')
    current_response = db.Column(db.Text)
    suggested_improvement = db.Column(db.Text)
    response_type = db.Column(db.String(50))
    ai_identified = db.Column(db.Boolean, default=False)
    ai_assessment_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    events = db.relationship('RiskEvent', backref='risk', lazy=True, cascade='all, delete-orphan')
    warnings = db.relationship('EarlyWarning', backref='risk', lazy=True, cascade='all, delete-orphan')

    def calculate_score(self):
        self.risk_score = self.probability * self.impact
        self.risk_level = 'critical' if self.risk_score>=15 else ('high' if self.risk_score>=10 else ('medium' if self.risk_score>=5 else 'low'))
        return self.risk_score

    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'risk_code':self.risk_code,'name':self.name,'category':self.category,'subcategory':self.subcategory,'description':self.description,'possible_consequences':self.possible_consequences,'information_source':self.information_source,'probability':self.probability,'impact':self.impact,'risk_score':self.risk_score,'risk_level':self.risk_level,'status':self.status,'trend':self.trend,'current_response':self.current_response,'suggested_improvement':self.suggested_improvement,'response_type':self.response_type,'ai_identified':self.ai_identified,'created_at':self.created_at.isoformat() if self.created_at else None}

class RiskEvent(db.Model):
    __tablename__ = 'risk_events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('risks.id'), nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    event_description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    severity = db.Column(db.String(20))
    financial_impact = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'risk_id':self.risk_id,'event_name':self.event_name,'event_description':self.event_description,'event_date':self.event_date.isoformat() if self.event_date else None,'severity':self.severity,'financial_impact':self.financial_impact,'status':self.status}

class EarlyWarning(db.Model):
    __tablename__ = 'early_warnings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('risks.id'), nullable=False)
    warning_level = db.Column(db.String(20), nullable=False)
    warning_message = db.Column(db.Text, nullable=False)
    trigger_reason = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'risk_id':self.risk_id,'warning_level':self.warning_level,'warning_message':self.warning_message,'trigger_reason':self.trigger_reason,'is_read':self.is_read,'is_resolved':self.is_resolved,'created_at':self.created_at.isoformat() if self.created_at else None}

# ==================== M3: 内控机制模块 ====================

class GovernanceStructure(db.Model):
    """治理结构"""
    __tablename__ = 'governance_structures'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    structure_type = db.Column(db.String(100))  # 单层制/双层制/混合制
    board_size = db.Column(db.Integer)
    independent_directors = db.Column(db.Integer)
    committees = db.Column(db.Text)  # JSON数组: ["审计委员会","薪酬委员会",...]
    description = db.Column(db.Text)  # 治理结构详细描述
    org_chart_text = db.Column(db.Text)  # 组织架构文字描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'structure_type':self.structure_type,'board_size':self.board_size,'independent_directors':self.independent_directors,'committees':self.committees,'description':self.description,'org_chart_text':self.org_chart_text,'created_at':self.created_at.isoformat() if self.created_at else None}

class InternalControl(db.Model):
    """内控制度（企业级）"""
    __tablename__ = 'internal_controls'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    control_code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # 治理结构/管理制度/合规制度/监督机制
    description = db.Column(db.Text)
    related_risks = db.Column(db.String(500))
    responsible_dept = db.Column(db.String(100))
    effectiveness = db.Column(db.String(20), default='effective')
    last_tested = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'control_code':self.control_code,'name':self.name,'category':self.category,'description':self.description,'related_risks':self.related_risks,'responsible_dept':self.responsible_dept,'effectiveness':self.effectiveness,'last_tested':self.last_tested.isoformat() if self.last_tested else None,'created_at':self.created_at.isoformat() if self.created_at else None}

class ControlRiskMapping(db.Model):
    """内控-风险关联映射"""
    __tablename__ = 'control_risk_mappings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('internal_controls.id'), nullable=False)
    risk_id = db.Column(db.Integer, db.ForeignKey('risks.id'), nullable=False)
    coverage_level = db.Column(db.String(20), default='full')  # full/partial/none
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    control = db.relationship('InternalControl', backref='mappings')
    risk = db.relationship('Risk', backref='control_mappings')
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'control_id':self.control_id,'risk_id':self.risk_id,'coverage_level':self.coverage_level,'notes':self.notes,'control_code':self.control.control_code if self.control else '','risk_code':self.risk.risk_code if self.risk else '','risk_name':self.risk.name if self.risk else ''}

# ==================== M4: 监督改进模块 ====================

class SupervisionMechanism(db.Model):
    """监督机制"""
    __tablename__ = 'supervision_mechanisms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    mechanism_name = db.Column(db.String(200), nullable=False)
    mechanism_type = db.Column(db.String(50))  # board/internal_audit/external/supervisory/compliance
    description = db.Column(db.Text)
    frequency = db.Column(db.String(50))  # 持续/每日/每周/每月/每季度/每年
    responsible_party = db.Column(db.String(100))
    scope = db.Column(db.Text)  # 监督范围
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'mechanism_name':self.mechanism_name,'mechanism_type':self.mechanism_type,'description':self.description,'frequency':self.frequency,'responsible_party':self.responsible_party,'scope':self.scope,'created_at':self.created_at.isoformat() if self.created_at else None}

class InformationDisclosure(db.Model):
    """信息披露记录"""
    __tablename__ = 'information_disclosures'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    disclosure_type = db.Column(db.String(50))  # annual/esg/quarterly/timely/regulatory
    title = db.Column(db.String(300), nullable=False)
    publish_date = db.Column(db.DateTime)
    risk_content_summary = db.Column(db.Text)  # 披露中涉及风险的内容摘要
    compliance_status = db.Column(db.String(20), default='compliant')  # compliant/partial/non_compliant
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'disclosure_type':self.disclosure_type,'title':self.title,'publish_date':self.publish_date.isoformat() if self.publish_date else None,'risk_content_summary':self.risk_content_summary,'compliance_status':self.compliance_status,'notes':self.notes,'created_at':self.created_at.isoformat() if self.created_at else None}

class ImprovementIssue(db.Model):
    """发现问题与改进"""
    __tablename__ = 'improvement_issues'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    issue_code = db.Column(db.String(20))
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    source = db.Column(db.String(100))  # internal_audit/regulatory/self_assessment/incident/external
    severity = db.Column(db.String(20))  # critical/high/medium/low
    status = db.Column(db.String(20), default='open')  # open/in_progress/resolved/closed
    proposed_action = db.Column(db.Text)
    responsible_person = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    resolution_summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'issue_code':self.issue_code,'title':self.title,'description':self.description,'source':self.source,'severity':self.severity,'status':self.status,'proposed_action':self.proposed_action,'responsible_person':self.responsible_person,'deadline':self.deadline.isoformat() if self.deadline else None,'resolved_at':self.resolved_at.isoformat() if self.resolved_at else None,'resolution_summary':self.resolution_summary,'created_at':self.created_at.isoformat() if self.created_at else None}

class ContinuousImprovement(db.Model):
    """持续改进PDCA循环"""
    __tablename__ = 'continuous_improvements'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprises.id'), nullable=False)
    cycle_name = db.Column(db.String(200))
    phase = db.Column(db.String(20))  # P(plan)/D(do)/C(check)/A(act)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    review_summary = db.Column(db.Text)  # 评审总结
    improvements_made = db.Column(db.Text)  # 已完成的改进
    lessons_learned = db.Column(db.Text)  # 经验教训
    next_cycle_plan = db.Column(db.Text)  # 下一周期计划
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'enterprise_id':self.enterprise_id,'cycle_name':self.cycle_name,'phase':self.phase,'start_date':self.start_date.isoformat() if self.start_date else None,'end_date':self.end_date.isoformat() if self.end_date else None,'review_summary':self.review_summary,'improvements_made':self.improvements_made,'lessons_learned':self.lessons_learned,'next_cycle_plan':self.next_cycle_plan,'created_at':self.created_at.isoformat() if self.created_at else None}
