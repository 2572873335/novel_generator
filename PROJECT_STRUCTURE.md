# NovelForge 项目结构文档

## 项目概述

| 项目 | 内容 |
|------|------|
| 项目名称 | NovelForge - AI小说生成系统 |
| 版本 | v5.1 |
| 技术栈 | Python, PyQt6, DeepSeek/MiniMax API |
| 项目目录 | `C:\Users\XiaoXin\Desktop\novel_generator` |

---

## 目录结构

```
novel_generator/
├── .claude/                    # Claude Code 配置
│   └── settings.local.json
│
├── .opencode/                  # OpenCode 技能系统
│   └── skills/               # 27个技能（写作、编辑、类型专家等）
│       ├── chapter-architect/
│       ├── character-designer/
│       ├── cultivation-designer/
│       ├── currency-expert/
│       ├── editor/
│       ├── geopolitics-expert/
│       ├── novel-coordinator/
│       ├── opening-diagnostician/
│       ├── outline-architect/
│       ├── plot-architect-coordinator/
│       ├── rhythm-designer/
│       ├── scene-writer/
│       ├── senior-editor/
│       ├── society-expert/
│       └── style-*/           # 7种文风技能
│
├── agents/                     # Agent 实现
│   ├── consistency_checker.py  # 一致性检查器
│   ├── creative_director.py    # 创意导演（熔断机制）
│   ├── emotion_writer.py      # 情感作家
│   ├── initializer_agent.py   # 初始化 Agent
│   ├── market_analyzer.py     # 市场分析 Agent
│   ├── rag_consistency_checker.py # RAG 一致性检查
│   ├── reviewer_agent.py      # 审核 Agent
│   ├── senior_editor_agent.py # 资深编辑 Agent
│   ├── senior_editor_v2.py    # 资深编辑 v2
│   └── writer_agent_v2.py     # 写作 Agent (主)
│
├── config/                     # 配置文件
│   ├── consistency_rules.yaml  # 一致性规则
│   └── genre_templates.yaml    # 类型模板
│
├── core/                       # 核心系统
│   ├── __init__.py
│   │
│   ├── NovelForge v4.0 核心模块
│   │   ├── orchestrator.py       # 主编排器（含检查点）
│   │   ├── emotion_tracker.py     # 情感追踪器
│   │   ├── world_bible.py         # 世界圣经（事件溯源）
│   │   └── prompt_assembler.py   # Prompt 聚合器
│   │
│   ├── 核心管理模块
│   │   ├── novel_generator.py     # 主生成器
│   │   ├── agent_manager.py       # Agent 管理
│   │   ├── model_manager.py       # 模型管理（API调用）
│   │   ├── quality_gate.py       # 质量门
│   │   ├── checkpoint_manager.py  # 检查点管理
│   │   └── progress_manager.py    # 进度管理
│   │
│   ├── 一致性系统
│   │   ├── consistency_tracker.py    # 一致性追踪
│   │   ├── hybrid_checker.py          # 混合检查（正则+相似度+LLM）
│   │   ├── constraint_arbiter.py      # 约束仲裁
│   │   ├── constraint_template_manager.py # 约束模板管理
│   │   └── writing_constraint_manager.py  # 写作约束管理
│   │
│   ├── 角色与世界
│   │   ├── character_manager.py          # 角色管理
│   │   ├── character_state_machine.py    # 角色状态机
│   │   ├── entity_graph.py               # 实体关系图
│   │   ├── world_bible.py                # 世界观数据库
│   │   └── genre_detector.py            # 类型检测
│   │
│   ├── 数据索引
│   │   ├── local_vector_store.py    # 本地向量存储
│   │   ├── time_aware_rag.py        # 时间感知 RAG
│   │   ├── summary_indexer.py       # 摘要索引
│   │   └── chapter_state_store.py   # 章节状态存储
│   │
│   ├── 期望与质量
│   │   ├── expectation_tracker.py   # 期望追踪
│   │   ├── reader_expectation.py    # 读者期望
│   │   └── state_snapshot.py        # 状态快照
│   │
│   └── 其他模块
│       ├── v7_integrator.py          # V7 类型集成
│       ├── skill_context_bus.py     # 技能上下文总线
│       ├── chapter_manager.py        # 章节管理
│       └── log_manager.py            # 日志管理
│
├── ui/                          # PyQt6 UI (v5.1 Slate Dark 主题)
│   ├── __init__.py              # 包导出
│   ├── main_window.py           # 主窗口
│   ├── views.py                 # 视图组件 (含 SkillMarketView)
│   ├── components.py            # UI 组件
│   ├── dialogs.py               # 对话框 (含 ToolGeneratorDialog, SkillEditorDialog)
│   ├── themes.py                # 主题系统 (Slate Dark)
│   ├── worker_thread.py         # 工作线程 (含 ToolWorker, AgenticChatWorker)
│   ├── ui_controller.py         # UIDriver (AI 控制 UI)
│   ├── producer_dashboard.py     # 仪表盘入口
│   └── avatars/                 # Agent 头像
│
├── novels/                      # 生成的小说项目
│   ├── 西行封龙录/            # 当前项目（17章已完成）
│   └── ...                     # 其他项目
│
├── config/                     # 配置文件
│
├── logs/                       # 日志文件
│
├── tools/                      # 工具脚本
│   ├── search_tool.py          # 搜索工具
│   ├── diagnose.py            # 诊断工具
│   └── ppt_generator.py        # PPT 生成
│
├── .env                        # 环境变量配置
├── .env.example               # 环境变量示例
├── main.py                    # CLI 入口
├── gui_entry.py               # GUI 入口
├── requirements.txt           # Python 依赖
├── CLAUDE.md                  # Claude Code 指南
├── README.md                  # 英文文档
├── README.zh_CN.md           # 中文文档
├── BUILD.md                   # 构建指南
├── CHANGELOG.md               # 更新日志
├── UI_OPTIMIZATION_PLAN.md    # UI 优化计划
└── NovelForge.spec            # 打包配置
```

---

## 核心模块说明

### 1. 主入口

| 文件 | 说明 |
|------|------|
| `main.py` | CLI 入口，支持交互式/配置文件/命令行参数模式 |
| `gui_entry.py` | GUI 入口 |

### 2. 核心系统 (`core/`)

#### v4.0 核心架构
- **Orchestrator**: 主循环组装，支持检查点恢复
- **EmotionWriter**: 单次API调用的场景写作
- **CreativeDirector**: 熔断仲裁机制
- **EmotionTracker**: 情感债务账本
- **WorldBible**: 事件溯源存储
- **PromptAssembler**: 多技能Prompt聚合

#### 质量保障
- **QualityGate**: 统一质量检查
- **HybridChecker**: 三层一致性检查（正则+相似度+LLM）
- **ConsistencyTracker**: 滑动窗口一致性

### 3. Agent 系统 (`agents/`)

| Agent | 功能 |
|-------|------|
| WriterAgentV2 | 主写作Agent，5阶段流水线 |
| SeniorEditorV2 | 资深编辑，6维度语义审查 |
| ConsistencyChecker | 滑动窗口一致性 |
| CreativeDirector | 熔断仲裁 |
| EmotionWriter | 单次API场景写作 |

### 4. UI 系统 (`ui/`)

**v5.0 模块化架构**：
- **Themes**: 赛博朋克主题、字体、间距
- **Views**: 全局状态栏、主导航、前期筹备、生产监控
- **Components**: Agent卡片、情感面板、日志面板
- **Dialogs**: 设置、进度、反馈对话框

---

## 数据流

```
用户输入
    ↓
main.py / UI
    ↓
NovelGenerator / Orchestrator
    ↓
AgentManager (Skill加载)
    ↓
WriterAgent (5阶段流水线)
    ├─ Outline (大纲)
    ├─ Draft (草稿)
    ├─ Consistency Check (一致性检查)
    ├─ Polish (润色)
    └─ Final (最终)
    ↓
QualityGate (质量门)
    ↓
保存章节 + 更新进度
```

---

## 配置文件

### 环境变量 (.env)
```bash
DEFAULT_MODEL_ID=minimax-m2.5
ANTHROPIC_AUTH_TOKEN=sk-cp-...
DEEPSEEK_API_KEY=sk-...
```

### 项目配置 (project-config.json)
```json
{
  "title": "西行封龙录",
  "genre": "玄幻",
  "target_chapters": 100
}
```

---

## 生成命令

```bash
# CLI 模式
python main.py --title "我的小说" --genre "玄幻" --chapters 100

# 配置文件模式
python main.py --config config.json

# 项目续传
python main.py --project "novels/西行封龙录" --batch-size 20

# PyQt6 UI
python -m ui.producer_dashboard "novels/西行封龙录"
```

---

## 特性亮点

1. **单次API调用架构**: EmotionWriter 减少 API 调用次数
2. **熔断机制**: CreativeDirector 防止无限重写
3. **情感追踪**: Python 精确计算，LLM 只接收文本
4. **一致性检查**: 三层检查（正则+相似度+LLM）
5. **检查点恢复**: 支持断点续传
6. **PyQt6 UI**: v5.0 模块化架构

---

## 当前项目状态

- **西行封龙录**: 17章已完成 / 100章目标
- **API**: MiniMax-M2.5
- **生成速度**: 每章约3-5分钟
