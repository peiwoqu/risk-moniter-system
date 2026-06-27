# Agent智能风险监控管理系统

基于 **Multi-Agent 架构** 的企业智能风险监控管理系统。将 COSO ERM 2017 风险管理框架落地为可运行的 Web 系统原型，通过五个功能模块实现对企业公开信息的自动接入、风险识别、量化评估、内控分析和监督改进。

## 项目构成

| 文件 | 说明 |
|------|------|
| `risk-monitor-system/` | 系统全部源代码 |
| `腾讯企业全面风险管理报告.docx` | 基于公开信息的腾讯控股全面风险管理报告（主报告） |
| `Agent智能风险监控系统技术报告.docx` | 系统技术报告（含架构设计、Agent实现、测试验证） |
| `期末报告.docx` | 课程要求文档 |

## 五个功能模块

```
  M1 数据接入  →  M2 风险分析  →  M3 内控机制  →  M4 监督改进  →  M5 报告输出
      ↓                ↓               ↓               ↓               ↓
 录入企业公开    识别→评估→       治理结构分析      监督机制评估      8节完整报告
 信息+智能解析   预警→应对建议     +内控覆盖评估    +问题识别改进     +Word/Excel下载
```

| 模块 | 核心功能 |
|------|----------|
| **M1 数据接入** | 企业信息录入、公开文本粘贴、DOCX/Excel/TXT 文件上传、智能解析提取风险章节 |
| **M2 风险分析** | 风险识别 → P×I 量化评估 → 红/橙/黄三级预警 → 4T策略应对建议 |
| **M3 内控机制** | 治理结构分析、三道防线模型、内控制度与风险覆盖映射、改进建议（按行业自动适配） |
| **M4 监督改进** | 监督机制评估、信息披露分析、问题自动识别、PDCA持续改进循环 |
| **M5 报告输出** | 匹配主报告结构的完整Word报告 + Excel风险清单，一键下载 |

## 快速开始

### 环境要求

- Python 3.10+
- Windows / macOS / Linux

### 安装与启动

```bash
# 1. 进入系统目录
cd risk-monitor-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化种子数据（腾讯控股案例）
python -X utf8 data/seed_data.py

# 4. 启动系统
python run.py
```

打开浏览器访问 **http://127.0.0.1:5000** 即可使用。

### 手动录入企业数据

1. 在 M1「数据接入」页面点击「添加企业」
2. 输入企业名称、选择行业、粘贴（或上传）企业公开信息文本（年报摘要、风险因素章节等）
3. 点击「创建并分析」—— 系统自动完成 M1→M2→M3→M4→M5 全流程

> **输入越详细，AI 分析越准确。** 建议至少录入企业年报中「风险因素」或「重大风险提示」章节的内容。

## 系统架构

```
                              ┌─────────────────────────┐
用户 → M1 数据接入 ──────────→│  企业公开信息文本存储    │
                              └───────────┬─────────────┘
                                          ↓
                              ┌─────────────────────────┐
        M2 风险分析 ←─────────│  Multi-Agent 分析引擎     │
        ┌── 识别Agent ─────────┤  (Supervisor 调度)      │
        ├── 评估Agent ────────│  + 规则引擎双轨回退      │
        ├── 预警Agent ────────│                         │
        └── 应对Agent ────────└───────────┬─────────────┘
                                          ↓
                    ┌─────────────────────┼─────────────────────┐
                    ↓                     ↓                     ↓
              M3 内控机制            M4 监督改进            M5 报告输出
         (AutoAnalysisEngine)  (AutoAnalysisEngine)    (ReportService)
         · 治理结构分析         · 监督机制评估          · Word完整报告
         · 三道防线             · 信息披露分析          · Excel风险清单
         · 内控制度覆盖         · 问题自动识别          · 8节结构匹配
         · 覆盖率评估           · PDCA循环              · 一键下载
```

## 项目目录

```
risk-monitor-system/
├── agents/                    # Multi-Agent 智能分析引擎
│   ├── supervisor.py          # 监督协调Agent（任务编排）
│   ├── risk_identifier.py     # 风险识别Agent
│   ├── risk_assessor.py       # 风险评估Agent（P×I矩阵）
│   ├── early_warning.py       # 预警Agent（红/橙/黄）
│   ├── risk_response.py       # 风险应对Agent（4T策略）
│   ├── llm_service.py         # LLM服务封装（Claude/OpenAI/本地/规则引擎）
│   └── knowledge_base.py      # COSO ERM知识库+腾讯预置数据
│
├── services/                  # 业务服务层
│   ├── analysis_service.py    # 完整五步分析流水线
│   ├── auto_analysis.py       # M3/M4自动分析引擎（5行业模板）
│   ├── data_ingestion.py      # 数据智能解析（文本剖析+风险提取）
│   ├── enterprise_service.py  # 企业数据管理
│   ├── report_service.py      # Word/Excel报告生成
│   └── ...
│
├── templates/                 # 前端页面（Jinja2 + Bootstrap 5）
│   ├── base.html              # 企业选择器 + 5模块导航
│   ├── module1_data.html      # M1: 数据接入
│   ├── module2_analysis.html  # M2: 风险分析
│   ├── module3_control.html   # M3: 内控机制（可展开详情）
│   ├── module4_supervision.html # M4: 监督改进（可展开详情）
│   └── module5_report.html    # M5: 报告输出
│
├── models/database.py         # 14张数据表（SQLAlchemy ORM）
├── static/js/charts.js        # Canvas风险矩阵 + Chart.js图表
├── app.py                     # Flask主应用
├── config.py                  # 配置（风险等级阈值/预警参数）
├── run.py                     # 启动脚本
└── requirements.txt           # Python依赖
```

## LLM 配置

系统支持多 LLM 后端，按优先级自动选择。**无需任何 API 也可使用**（自动回退规则引擎）。

```bash
# Claude API
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI API
export OPENAI_API_KEY="sk-..."

# 本地模型（Ollama / vLLM）
export LOCAL_LLM_ENDPOINT="http://localhost:11434"

# 不配置任何 API → 自动使用规则引擎，功能完整可用
```

## 预置案例

系统预置了腾讯控股（0700.HK）的案例数据，启动即可直接查看全部五个模块的完整分析结果。

## 技术栈

- **后端**: Python 3.10+ / Flask / SQLAlchemy / SQLite
- **前端**: Bootstrap 5 / Chart.js / Canvas 2D
- **AI**: Claude / OpenAI / 本地模型 / 规则引擎（四选一）
- **报告**: python-docx / openpyxl
- **架构**: Supervisor + Specialized Agents（自研轻量Agent框架）

## License

教育用途，风险管理课程期末项目。
