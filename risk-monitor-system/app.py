# -*- coding: utf-8 -*-
"""Agent智能风险监控管理系统 - 五模块主应用"""
import os, json, logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from config import Config
from models.database import (db, Risk, RiskEvent, EarlyWarning, Enterprise,
    InternalControl, GovernanceStructure, SupervisionMechanism,
    InformationDisclosure, ImprovementIssue, ContinuousImprovement, ControlRiskMapping)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    db.init_app(app)
    for d in ['data','data/reports','data/uploads']:
        os.makedirs(os.path.join(app.config['BASE_DIR'], d), exist_ok=True)

    # ---- 通用：企业选择器 ----
    @app.context_processor
    def inject_enterprises():
        return {'all_enterprises': [e.to_dict() for e in Enterprise.query.order_by(Enterprise.updated_at.desc()).all()]}

    # ---- M1: 数据接入 ----
    @app.route('/module1')
    def module1_data():
        eid = request.args.get('enterprise_id', 1, type=int)
        ent = Enterprise.query.get(eid) if eid else None
        from services.data_ingestion import DataIngestionEngine
        engine = DataIngestionEngine()
        parsed = engine.parse_text_block(ent.raw_data_text or '', ent.industry or '') if ent and ent.raw_data_text else None
        return render_template('module1_data.html', enterprise=ent.to_dict() if ent else None, parsed=parsed)

    # ---- M2: 风险分析 ----
    @app.route('/module2')
    def module2_analysis():
        eid = request.args.get('enterprise_id', 1, type=int)
        ent = Enterprise.query.get(eid) if eid else None
        risks = Risk.query.filter_by(enterprise_id=eid).order_by(Risk.risk_score.desc()).all() if eid else []
        warnings = EarlyWarning.query.join(Risk).filter(Risk.enterprise_id==eid).filter(EarlyWarning.is_resolved==False).all() if eid else []
        return render_template('module2_analysis.html', enterprise=ent.to_dict() if ent else None, risks=[r.to_dict() for r in risks], warnings=[w.to_dict() for w in warnings])

    # ---- M3: 内控机制 (auto-generated with detailed accordion) ----
    @app.route('/module3')
    def module3_control():
        eid = request.args.get('enterprise_id', 1, type=int)
        ent = Enterprise.query.get(eid) if eid else None
        if not ent: return render_template('module3_control.html', enterprise=None)
        risks = [r.to_dict() for r in Risk.query.filter_by(enterprise_id=eid).all()]
        raw = ent.raw_data_text or ''
        from services.auto_analysis import AutoAnalysisEngine
        engine = AutoAnalysisEngine()
        m3 = engine.analyze_all_m3(ent.name, ent.industry or '', risks, raw)
        return render_template('module3_control.html', enterprise=ent.to_dict(),
            m3=m3, risks_count=len(risks))

    # ---- M4: 监督改进 (auto-generated with detailed accordion) ----
    @app.route('/module4')
    def module4_supervision():
        eid = request.args.get('enterprise_id', 1, type=int)
        ent = Enterprise.query.get(eid) if eid else None
        if not ent: return render_template('module4_supervision.html', enterprise=None)
        risks = [r.to_dict() for r in Risk.query.filter_by(enterprise_id=eid).all()]
        from services.auto_analysis import AutoAnalysisEngine, TEMPLATES
        engine = AutoAnalysisEngine()
        ind = engine._match(ent.industry or '')
        m3_cov = engine._analyze_coverage(
            engine._analyze_controls(ind, TEMPLATES[ind], risks), risks)
        m4 = engine.analyze_all_m4(ent.name, ent.industry or '', risks, m3_cov)
        return render_template('module4_supervision.html', enterprise=ent.to_dict(),
            m4=m4, risks_count=len(risks),
            critical_count=sum(1 for r in risks if r.get('risk_score',0)>=15))

    # ---- M5: 报告输出 ----
    @app.route('/module5')
    def module5_report():
        eid = request.args.get('enterprise_id', 1, type=int)
        ent = Enterprise.query.get(eid) if eid else None
        risks = Risk.query.filter_by(enterprise_id=eid).order_by(Risk.risk_score.desc()).all() if eid else []
        gov = GovernanceStructure.query.filter_by(enterprise_id=eid).first()
        controls = InternalControl.query.filter_by(enterprise_id=eid).all() if eid else []
        mechanisms = SupervisionMechanism.query.filter_by(enterprise_id=eid).all() if eid else []
        issues = ImprovementIssue.query.filter_by(enterprise_id=eid).all() if eid else []
        # 计算覆盖率
        all_risk_codes = {r.risk_code for r in risks}
        covered_codes = set()
        for c in controls:
            if c.related_risks:
                for rc in c.related_risks.split(','):
                    covered_codes.add(rc.strip())
        coverage = {
            "total": len(controls), "total_risks": len(risks),
            "covered_risks": len(covered_codes & all_risk_codes),
            "coverage_rate": f"{len(covered_codes & all_risk_codes)/max(len(risks),1)*100:.0f}%",
            "uncovered_risks": [{"risk_code":r.risk_code,"risk_score":r.risk_score} for r in risks if r.risk_code not in covered_codes],
            "improvement_suggestions": ["加强内控制度建设","完善风险覆盖","建立定期审查机制"],
        }
        return render_template('module5_report.html', enterprise=ent.to_dict() if ent else None,
            risks=[r.to_dict() for r in risks],
            governance=gov.to_dict() if gov else {},
            coverage=coverage, mechanisms=[m.to_dict() for m in mechanisms],
            issues=[i.to_dict() for i in issues],
            supervision_assessment="基于风险分析自动生成的监督评估" if risks else "",
            disclosures=[], improvement_suggestions=[])  # 占位

    # ---- 页面路由 API ----
    app.add_url_rule('/', 'index', lambda: __import__('flask').redirect('/module1'))

    # ---- API 路由 ----
    register_api_routes(app)
    register_error_handlers(app)
    register_template_filters(app)

    with app.app_context(): db.create_all()
    return app


def register_api_routes(app):
    """注册所有API路由"""
    from services.risk_service import RiskService
    from services.enterprise_service import EnterpriseService
    from services.analysis_service import AnalysisService
    from services.control_service import ControlService
    from services.supervision_service import SupervisionService

    # ---- M1: 数据接入 API ----
    @app.route('/api/enterprises', methods=['GET'])
    def api_enterprises():
        return jsonify({'success':True,'data':[e.to_dict() for e in Enterprise.query.order_by(Enterprise.updated_at.desc()).all()]})

    @app.route('/api/enterprises', methods=['POST'])
    def api_create_enterprise():
        if request.is_json:
            d = request.get_json()
            if not d.get('name','').strip(): return jsonify({'success':False,'error':'企业名称不能为空'}), 400
            ent = EnterpriseService.create(d['name'].strip(), d.get('stock_code',''), d.get('industry',''), d.get('description',''), d.get('raw_data_text',''))
            return jsonify({'success':True,'data':ent}), 201
        # multipart
        name = request.form.get('name','').strip()
        if not name: return jsonify({'success':False,'error':'企业名称不能为空'}), 400
        ent = EnterpriseService.create(name, request.form.get('stock_code',''), request.form.get('industry',''), request.form.get('description',''), request.form.get('raw_data_text',''))
        files_ok = []
        if 'files' in request.files:
            for file in request.files.getlist('files'):
                if file.filename:
                    fp = os.path.join(app.config['BASE_DIR'],'data','uploads',file.filename)
                    os.makedirs(os.path.dirname(fp), exist_ok=True)
                    file.save(fp)
                    files_ok.append(EnterpriseService.import_file(ent['id'], fp))
        return jsonify({'success':True,'data':ent,'files_uploaded':files_ok}), 201

    @app.route('/api/enterprises/<int:eid>', methods=['GET'])
    def api_get_enterprise(eid):
        ent = Enterprise.query.get(eid)
        if not ent: return jsonify({'success':False,'error':'企业不存在'}), 404
        risks = Risk.query.filter_by(enterprise_id=eid).order_by(Risk.risk_score.desc()).all()
        return jsonify({'success':True,'data':ent.to_dict(),'risks':[r.to_dict() for r in risks],'risk_count':len(risks)})

    @app.route('/api/enterprises/<int:eid>', methods=['DELETE'])
    def api_delete_enterprise(eid):
        return jsonify({'success':True} if EnterpriseService.delete(eid) else ({'success':False,'error':'不存在'},404))

    @app.route('/api/enterprises/<int:eid>/import-text', methods=['POST'])
    def api_import_text(eid):
        text = (request.get_json() or {}).get('text','')
        return jsonify(EnterpriseService.import_text_data(eid, text))

    @app.route('/api/enterprises/<int:eid>/import-file', methods=['POST'])
    def api_import_file(eid):
        if 'file' not in request.files: return jsonify({'success':False,'error':'未选择文件'}), 400
        file = request.files['file']
        fp = os.path.join(app.config['BASE_DIR'],'data','uploads',file.filename)
        os.makedirs(os.path.dirname(fp), exist_ok=True); file.save(fp)
        return jsonify(EnterpriseService.import_file(eid, fp))

    @app.route('/api/enterprises/<int:eid>/analyze', methods=['POST'])
    def api_analyze(eid):
        return jsonify(EnterpriseService.run_full_analysis(eid))

    @app.route('/api/enterprises/seed-tencent', methods=['POST'])
    def api_seed(): return jsonify(EnterpriseService.seed_tencent())

    # ---- M2: 风险分析 API ----
    @app.route('/api/risks', methods=['GET'])
    def api_risks():
        eid = request.args.get('enterprise_id', type=int)
        q = Risk.query.filter_by(enterprise_id=eid) if eid else Risk.query
        risks = q.order_by(Risk.risk_score.desc()).all()
        return jsonify({'success':True,'data':[r.to_dict() for r in risks],'count':len(risks)})

    @app.route('/api/risks', methods=['POST'])
    def api_create_risk():
        return jsonify({'success':True,'data':RiskService.create_risk(request.get_json())}), 201

    @app.route('/api/risks/<int:rid>', methods=['PUT','DELETE'])
    def api_risk(rid):
        if request.method == 'DELETE': return jsonify({'success':True} if RiskService.delete_risk(rid) else ({'success':False},404))
        return jsonify({'success':True,'data':RiskService.update_risk(rid, request.get_json())})

    @app.route('/api/analysis/full', methods=['POST'])
    def api_full_analysis():
        d = request.get_json() or {}
        service = AnalysisService()
        result = service.run_complete_analysis(d.get('enterprise_name','企业'), d.get('enterprise_info',''), d.get('industry',''))
        return jsonify({'success':True,'data':result})

    @app.route('/api/warnings', methods=['GET'])
    def api_warnings():
        eid = request.args.get('enterprise_id', type=int)
        only = request.args.get('unresolved','false').lower()=='true'
        q = EarlyWarning.query.join(Risk).filter(Risk.enterprise_id==eid) if eid else EarlyWarning.query
        if only: q = q.filter(EarlyWarning.is_resolved==False)
        warnings = q.order_by(EarlyWarning.created_at.desc()).all()
        return jsonify({'success':True,'data':[w.to_dict() for w in warnings],'count':len(warnings)})

    # ---- M3: 内控机制 API ----
    @app.route('/api/controls', methods=['GET'])
    def api_controls():
        eid = request.args.get('enterprise_id', type=int)
        return jsonify({'success':True,'data':ControlService.get_controls(eid) if eid else []})

    @app.route('/api/controls', methods=['POST'])
    def api_create_control():
        d = request.get_json()
        return jsonify({'success':True,'data':ControlService.create_control(d['enterprise_id'], d)}), 201

    @app.route('/api/controls/<int:cid>', methods=['PUT','DELETE'])
    def api_control(cid):
        if request.method=='DELETE': return jsonify({'success':ControlService.delete_control(cid)})
        return jsonify({'success':True,'data':ControlService.update_control(cid, request.get_json())})

    @app.route('/api/governance', methods=['GET','POST'])
    def api_governance():
        eid = request.args.get('enterprise_id', type=int) if request.method=='GET' else request.get_json().get('enterprise_id')
        if request.method=='GET': return jsonify({'success':True,'data':ControlService.get_governance(eid)})
        return jsonify({'success':True,'data':ControlService.save_governance(eid, request.get_json())})

    @app.route('/api/control-mappings', methods=['GET'])
    def api_mappings():
        eid = request.args.get('enterprise_id', type=int)
        return jsonify({'success':True,'data':ControlService.get_mappings(eid) if eid else []})

    @app.route('/api/control-mappings', methods=['POST'])
    def api_create_mapping():
        d = request.get_json()
        return jsonify({'success':True,'data':ControlService.create_mapping(d['enterprise_id'], d)}), 201

    @app.route('/api/control-mappings/<int:mid>', methods=['DELETE'])
    def api_delete_mapping(mid):
        return jsonify({'success':ControlService.delete_mapping(mid)})

    @app.route('/api/coverage-stats')
    def api_coverage():
        eid = request.args.get('enterprise_id', type=int)
        return jsonify({'success':True,'data':ControlService.get_coverage_stats(eid) if eid else {}})

    # ---- M4: 监督改进 API ----
    @app.route('/api/mechanisms', methods=['GET','POST'])
    def api_mechanisms():
        if request.method=='GET':
            eid = request.args.get('enterprise_id', type=int)
            return jsonify({'success':True,'data':SupervisionService.get_mechanisms(eid) if eid else []})
        d = request.get_json()
        return jsonify({'success':True,'data':SupervisionService.create_mechanism(d['enterprise_id'], d)}), 201

    @app.route('/api/mechanisms/<int:mid>', methods=['PUT','DELETE'])
    def api_mechanism(mid):
        if request.method=='DELETE': return jsonify({'success':SupervisionService.delete_mechanism(mid)})
        return jsonify({'success':True,'data':SupervisionService.update_mechanism(mid, request.get_json())})

    @app.route('/api/disclosures', methods=['GET','POST'])
    def api_disclosures():
        if request.method=='GET':
            eid = request.args.get('enterprise_id', type=int)
            return jsonify({'success':True,'data':SupervisionService.get_disclosures(eid) if eid else []})
        d = request.get_json()
        return jsonify({'success':True,'data':SupervisionService.create_disclosure(d['enterprise_id'], d)}), 201

    @app.route('/api/disclosures/<int:did>', methods=['DELETE'])
    def api_disclosure(did):
        return jsonify({'success':SupervisionService.delete_disclosure(did)})

    @app.route('/api/issues', methods=['GET','POST'])
    def api_issues():
        if request.method=='GET':
            eid = request.args.get('enterprise_id', type=int)
            sf = request.args.get('status','')
            return jsonify({'success':True,'data':SupervisionService.get_issues(eid, sf) if eid else []})
        d = request.get_json()
        return jsonify({'success':True,'data':SupervisionService.create_issue(d['enterprise_id'], d)}), 201

    @app.route('/api/issues/<int:iid>', methods=['PUT','DELETE'])
    def api_issue(iid):
        if request.method=='DELETE': return jsonify({'success':SupervisionService.delete_issue(iid)})
        return jsonify({'success':True,'data':SupervisionService.update_issue(iid, request.get_json())})

    @app.route('/api/improvements', methods=['GET','POST'])
    def api_improvements():
        if request.method=='GET':
            eid = request.args.get('enterprise_id', type=int)
            return jsonify({'success':True,'data':SupervisionService.get_improvements(eid) if eid else []})
        d = request.get_json()
        return jsonify({'success':True,'data':SupervisionService.create_improvement(d['enterprise_id'], d)}), 201

    @app.route('/api/improvements/<int:imid>', methods=['PUT','DELETE'])
    def api_improvement(imid):
        if request.method=='DELETE': return jsonify({'success':SupervisionService.delete_improvement(imid)})
        return jsonify({'success':True,'data':SupervisionService.update_improvement(imid, request.get_json())})

    # ---- M5: 报告 API ----
    @app.route('/api/reports/generate', methods=['POST'])
    def api_generate_report():
        d = request.get_json() or {}
        eid = d.get('enterprise_id', 1)
        ent = Enterprise.query.get(eid)
        if not ent: return jsonify({'success':False,'error':'企业不存在'}), 404

        from services.report_service import ReportService
        rs = ReportService()
        risks = [r.to_dict() for r in Risk.query.filter_by(enterprise_id=eid).order_by(Risk.risk_score.desc()).all()]
        coverage = ControlService.get_coverage_stats(eid)
        issues = SupervisionService.get_issues(eid)
        mechs = SupervisionService.get_mechanisms(eid)
        disclosures = SupervisionService.get_disclosures(eid)
        gov = ControlService.get_governance(eid)
        controls = ControlService.get_controls(eid)

        if d.get('report_type') == 'excel':
            filepath = rs.generate_excel_report(ent.name, risks, {'total':len(risks)})
            return jsonify({'success':True,'data':{'filepath':filepath,'filename':os.path.basename(filepath)}})
        else:
            filepath = rs.generate_full_five_section_report(
                enterprise_name=ent.name, risks=risks,
                governance=gov, controls=controls, coverage=coverage,
                mechanisms=mechs, disclosures=disclosures, issues=issues
            )
            return jsonify({'success':True,'data':{'filepath':filepath,'filename':os.path.basename(filepath)}})

    @app.route('/api/reports/download/<filename>')
    def api_download(filename):
        from services.report_service import ReportService
        fp = os.path.join(ReportService.REPORT_DIR, filename)
        return send_file(fp, as_attachment=True) if os.path.exists(fp) else ({'success':False,'error':'文件不存在'},404)

    # ---- 系统 ----
    @app.route('/api/system/info')
    def api_sys():
        import sys
        return jsonify({'success':True,'data':{'version':'2.0','python':sys.version.split()[0],'enterprises':Enterprise.query.count(),'risks':Risk.query.count(),'controls':InternalControl.query.count()}})


def register_error_handlers(app):
    @app.errorhandler(404)
    def nf(e):
        return (jsonify({'success':False,'error':'资源不存在'}),404) if request.path.startswith('/api/') else (render_template('error.html',code=404,message='页面不存在'),404)
    @app.errorhandler(500)
    def se(e):
        return (jsonify({'success':False,'error':'服务器错误'}),500) if request.path.startswith('/api/') else (render_template('error.html',code=500,message='服务器错误'),500)


def register_template_filters(app):
    @app.template_filter('risk_level_color')
    def rlc(l): return {'critical':'danger','high':'warning','medium':'info','low':'success'}.get(l,'secondary')
    @app.template_filter('risk_level_badge')
    def rlb(l): return {'critical':'🔴 重大风险','high':'🟠 高度关注','medium':'🟡 一般风险','low':'🟢 低风险'}.get(l,l)
    @app.template_filter('trend_icon')
    def ti(t): return {'increasing':'↑ 上升','stable':'→ 稳定','decreasing':'↓ 下降'}.get(t,t)
    @app.template_filter('format_date')
    def fd(d):
        if not d: return ''
        try: return datetime.fromisoformat(str(d)).strftime('%Y-%m-%d %H:%M')
        except: return str(d)


app = create_app()
if __name__ == '__main__': app.run(debug=True, host='0.0.0.0', port=5000)
