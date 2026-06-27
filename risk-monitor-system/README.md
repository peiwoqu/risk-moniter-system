# Agent智能风险监控管理系统

基于 Multi-Agent 架构的企业智能风险监控管理系统，将 COSO ERM 2017 风险管理框架落地为可运行的系统原型。

## 特性

- **Multi-Agent 协作**：Supervisor + 4个专业Agent（识别、评估、预警、应对）
- **智能风险分析**：基于LLM的企业风险自动识别、量化评估、预警检测和应对建议生成
- **风险矩阵可视化**：P×I 风险矩阵热力图、趋势图、类别分布图
- **报告自动生成**：Word/Excel/JSON 格式的完整风险管理报告
- **Web管理界面**：基于 Bootstrap 5 的现代化管理后台

## 系统架构

```
用户输入 → SupervisorAgent → ┌─ RiskIdentifierAgent (风险识别)
                              ├─ RiskAssessorAgent  (风险评估)
                              ├─ EarlyWarningAgent  (预警检测)
                              └─ RiskResponseAgent  (应对建议)
                                    ↓
                              报告生成 & 数据持久化
```

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
# 1. 进入项目目录
cd risk-monitor-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库和种子数据（首次运行）
python data/seed_data.py

# 4. 启动应用
python run.py
```

访问 http://localhost:5000 即可使用。

### 使用Docker（可选）

```bash
docker build -t risk-monitor .
docker run -p 5000:5000 risk-monitor
```

## 页面说明

| 页面 | 路径 | 功能 |
|------|------|------|
| 仪表盘 | `/` | 风险概览、统计卡片、风险矩阵、预警列表 |
| 风险管理 | `/risks` | 风险列表、筛选、CRUD操作 |
| 风险详情 | `/risks/<id>` | 单个风险的完整信息、事件和预警历史 |
| 内控管理 | `/controls` | COSO ERM三道防线和内部控制清单 |
| AI分析 | `/analysis` | 逐步/完整AI分析流程执行 |
| 报告生成 | `/reports` | 生成和下载Word/Excel/JSON报告 |

## LLM配置

系统支持多LLM后端，按优先级自动选择：

1. **Claude API** - 设置环境变量 `ANTHROPIC_API_KEY`
2. **OpenAI API** - 设置环境变量 `OPENAI_API_KEY`
3. **本地模型** - 设置环境变量 `LOCAL_LLM_ENDPOINT`（兼容 Ollama/vLLM）
4. **规则引擎** - 无需任何API，使用内置知识库（默认回退方案）

```bash
# 示例：使用OpenAI
export OPENAI_API_KEY="sk-..."
export AI_MODEL="gpt-4o"

# 示例：使用本地Ollama
export LOCAL_LLM_ENDPOINT="http://localhost:11434"
export AI_MODEL="qwen2.5:7b"
```

## 项目结构

```
risk-monitor-system/
├── agents/             # Agent模块
│   ├── supervisor.py       # 监督协调Agent
│   ├── risk_identifier.py  # 风险识别Agent
│   ├── risk_assessor.py    # 风险评估Agent
│   ├── early_warning.py    # 预警Agent
│   ├── risk_response.py    # 风险应对Agent
│   ├── llm_service.py      # LLM服务封装
│   └── knowledge_base.py   # 内置知识库
├── services/           # 服务层
│   ├── risk_service.py     # 风险数据服务
│   ├── analysis_service.py # 分析服务
│   ├── report_service.py   # 报告生成服务
│   └── data_service.py     # 数据导入导出服务
├── models/             # 数据模型
│   └── database.py
├── templates/          # Jinja2模板
│   ├── base.html           # 基础布局
│   ├── index.html          # 仪表盘
│   ├── risks.html          # 风险管理
│   ├── risk_detail.html    # 风险详情
│   ├── risk_form.html      # 风险表单
│   ├── controls.html       # 内控管理
│   ├── analysis.html       # AI分析
│   ├── reports.html        # 报告生成
│   └── error.html          # 错误页面
├── static/             # 静态资源
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       └── charts.js
├── data/               # 数据
│   ├── seed_data.py        # 种子数据脚本
│   └── tencent_data.json   # 腾讯案例数据
├── app.py              # Flask主应用
├── config.py           # 配置文件
├── run.py              # 启动脚本
└── requirements.txt    # 依赖列表
```

## 技术栈

- **后端**: Python 3.10+ / Flask 3.0 / SQLAlchemy
- **前端**: Bootstrap 5 / Chart.js / Vanilla JS
- **数据库**: SQLite（默认）/ PostgreSQL
- **AI**: 支持 Claude / OpenAI / 本地模型 / 规则引擎
- **报告**: python-docx / openpyxl / matplotlib

## 许可

本项目为教育用途，风险管理课程期末项目。
