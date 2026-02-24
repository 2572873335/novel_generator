# AGENTS.md

Coding agent instructions for the Novel Generator AI system.

## 项目概述

AI Novel Generator 是一个基于 Anthropic 长运行代理架构的全自动 AI 小说生成系统。支持多 AI 提供商（Anthropic Claude, OpenAI, Moonshot, DeepSeek）。

### 核心特性

- **多模型支持**: Claude, GPT, Kimi, DeepSeek
- **27 专业技能**: 4级层级架构
- **3层一致性防御**: 事前约束 → 事中校验 → 事后审核
- **V7 类型感知**: 自动检测小说类型并应用约束模板
- **RAG 上下文检索**: 时间感知 + 向量检索
- **NovelForge v4.0**: 单次API调用 + 熔断机制 + 情绪追踪

---

## 系统架构

### NovelForge v4.0 架构
```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator (core/orchestrator.py)          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ NovelForge v4.0 核心 (7模块)                              │  │
│  │ 1. EmotionWriter (单次API调用)                           │  │
│  │ 2. CreativeDirector (熔断仲裁)                           │  │
│  │ 3. PromptAssembler (Prompt聚合)                          │  │
│  │ 4. EmotionTracker (情绪债务账本)                          │  │
│  │ 5. WorldBible (事件溯源)                                 │  │
│  │ 6. ConsistencyGuardian (一致性检查)                       │  │
│  │ 7. StyleAnchor (文风锁定)                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│  Emotion     │    │ Circuit         │    │ Producer           │
│  Tracker     │    │ Breaker         │    │ Dashboard          │
│  (Python)    │    │ Monitor         │    │ (PyQt6 UI)         │
└───────────────┘    └─────────────────┘    └─────────────────────┘
```

### Legacy v3.x 架构
```
┌─────────────────────────────────────────────────────────────────┐
│                        NovelGenerator                            │
│                      (core/novel_generator.py)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│  AgentManager │    │ V7Integrator    │    │ WritingConstraint  │
│  (技能加载)    │    │ (类型感知)       │    │ Manager (约束注入)   │
└───────────────┘    └─────────────────┘    └─────────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WriterAgentV2                               │
│                  (5阶段管道写作: 大纲→草稿→校验→润色→终稿)        │
└─────────────────────────────────────────────────────────────────┘
        │
        ├─→ HybridChecker (3层一致性检测)
        ├─→ ConsistencyTracker (状态追踪)
        ├─→ SkillContextBus (跨技能上下文)
        ├─→ TimeAwareRAG (时间感知检索)
        └─→ CheckpointManager (检查点恢复)
```

---

## 目录结构

```
novel_generator/
├── agents/                    # Agent 实现
│   ├── writer_agent_v2.py    # 主写作 Agent (管道架构)
│   ├── consistency_checker.py # 严格一致性检查
│   ├── reviewer_agent.py      # 审查 Agent
│   ├── senior_editor_v2.py   # 资深编辑 Agent
│   ├── market_analyzer.py     # 市场分析 Agent
│   ├── rag_consistency_checker.py # RAG 一致性检查
│   ├── initializer_agent.py  # 初始化 Agent
│   ├── creative_director.py  # [v4.0] 熔断仲裁器
│   └── emotion_writer.py     # [v4.0] 单次API写作
│
├── core/                      # 核心系统
│   ├── novel_generator.py     # 主控协调器
│   ├── orchestrator.py       # [v4.0] 主循环组装
│   ├── agent_manager.py       # Agent 管理和技能加载
│   ├── v7_integrator.py      # V7 类型感知系统
│   ├── genre_detector.py     # 类型检测器
│   ├── constraint_template_manager.py # 约束模板管理
│   ├── constraint_arbiter.py  # 约束仲裁器
│   ├── writing_constraint_manager.py # 写作约束管理
│   ├── consistency_tracker.py # 设定一致性追踪
│   ├── hybrid_checker.py      # 混合检查器 (regex+相似度+LLM)
│   ├── skill_context_bus.py   # 技能上下文总线
│   ├── checkpoint_manager.py  # 检查点管理器
│   ├── time_aware_rag.py      # 时间感知 RAG
│   ├── local_vector_store.py  # 本地向量存储
│   ├── expectation_tracker.py # 期待感追踪
│   ├── reader_expectation.py  # 读者期待分析
│   ├── entity_graph.py        # 实体关系图
│   ├── character_state_machine.py # 角色状态机
│   ├── state_snapshot.py      # 状态快照
│   ├── summary_indexer.py     # 摘要索引
│   ├── chapter_manager.py     # 章节管理
│   ├── character_manager.py   # 角色管理
│   ├── progress_manager.py    # 进度管理
│   ├── model_manager.py       # 模型管理
│   ├── config_manager.py      # 配置管理
│   ├── emotion_tracker.py     # [v4.0] 情绪债务账本
│   ├── world_bible.py        # [v4.0] 事件溯源
│   └── prompt_assembler.py   # [v4.0] Prompt聚合
│
├── ui/                        # [v4.0] UI组件
│   └── producer_dashboard.py # 熔断可视化
│
├── config/                    # 配置文件
│   ├── consistency_rules.yaml # 一致性规则
│   └── genre_templates.yaml   # 类型模板
│
├── .opencode/skills/          # 技能系统 (27个)
│   ├── level1_coordinator/    # L1: 协调员 (3个)
│   ├── level2_architect/      # L2: 架构师 (5个)
│   ├── level3_expert/         # L3: 专家 (6个)
│   ├── level4_auditor/        # L4: 审核 (3个)
│   ├── style_*/               # 文风技能 (7个)
│   └── genre_expert/          # 类型专家 (3个)
│
├── novels/                    # 生成的小说项目
├── main.py                    # CLI 入口
└── app.py                     # Web UI (Streamlit)
```

---

## Skills 层级架构 (27个)

### Level 1: Coordinator (协调员) - 3个
| Skill | 功能 |
|-------|------|
| `worldbuilder-coordinator` | 世界观总控 |
| `plot-architect-coordinator` | 剧情总控 |
| `novel-coordinator` | 小说总控 |

### Level 2: Architect (架构师) - 5个
| Skill | 功能 |
|-------|------|
| `outline-architect` | 大纲架构 |
| `volume-architect` | 卷纲架构 |
| `chapter-architect` | 章纲架构 |
| `character-designer` | 人物设计 |
| `rhythm-designer` | 节奏设计 |

### Level 3: Expert (专家) - 6个
| Skill | 功能 |
|-------|------|
| `scene-writer` | 场景写作 |
| `cultivation-designer` | 修炼体系设计 |
| `currency-expert` | 货币体系专家 |
| `geopolitics-expert` | 地缘政治专家 |
| `society-expert` | 社会结构专家 |
| `web-novel-methodology` | 网文方法论 |

### Level 4: Auditor (审核) - 3个
| Skill | 功能 |
|-------|------|
| `editor` | 编辑 |
| `senior-editor` | 资深编辑 |
| `opening-diagnostician` | 开篇诊断 |

### Style Skills (文风) - 7个
| Skill | 功能 |
|-------|------|
| `style-blood-punch` | 热血文风 |
| `style-cowboy` | 西部文风 |
| `style-dark` | 黑暗文风 |
| `style-infinity` | 无限流 |
| `style-building` | 经营文风 |
| `style-serious` | 严肃文风 |
| `style-sweet` | 甜宠文风 |

### Genre Experts (类型专家) - 3个
| Skill | 功能 |
|-------|------|
| `scifi-expert` | 科幻专家 |
| `suspense-expert` | 悬疑专家 |
| `urban-expert` | 都市专家 |

---

## 三层一致性防御系统

### 第一层：事前约束 (Pre-writing)
**组件**: `WritingConstraintManager`
- 将约束注入 LLM 提示词
- 锁定宗门名称、人物姓名、境界体系
- 防止生成不符合设定的内容
- 动态加载 world-rules.json 中的境界

### 第二层：事中校验 (Real-time)
**组件**: `_pre_save_validation()` in WriterAgentV2
- 章节保存前实时校验
- 使用 WritingConstraintManager.validate_chapter()
- 发现严重问题立即触发重写

### 第三层：事后审核 (Post-writing)
**组件**: `SeniorEditorV2` / `senior-editor` skill
- 每5章调用资深编辑审核
- 多维度质量审查
- 检测自动化检查遗漏的问题

---

## 优化特性 (2024)

### 1. 强制开篇诊断
- 第1-3章自动调用 `opening-diagnostician` skill
- 综合评级 D/F 触发强制重写
- 诊断报告保存到 `opening_diagnosis/`

### 2. 爽点密度监控
- 20个爽点关键词实时检测
- 阈值: 0.3/千字
- 低于阈值触发警告

### 3. Skill 上下文总线
- 解决 27 个 Skill 孤岛问题
- 跨 Skill 状态传递 (境界、势力、爽点密度)
- 上下文持久化到 `skill_context.json`

### 4. 动态战力检测
- LLM 提取本章境界描述
- 检测战力崩坏和境界跳跃
- 与前文对比异常预警

### 5. 增强检查点机制
- 支持从任意检查点恢复
- LLM 调用超时自动重试
- 人工干预点支持暂停确认

---

## NovelForge v4.0 核心特性

### 1. 防Token黑洞: Prompt聚合
- **问题**: L1→L2→L3→L4 每层都调API (8-12次调用/章)
- **解决**: L2+L3 合并为单次Prompt组装
- 核心组件: `core/prompt_assembler.py`

### 2. 防LLM计算灾难: Python算术
- **问题**: LLM不擅长精确计算
- **解决**: 所有计算在Python中完成，LLM只接收文本化结果
- 核心组件: `core/emotion_tracker.py`
- 情绪债务自动衰减 (默认30%/章)

### 3. 防无限循环: 熔断机制
- **问题**: 无限制回滚导致第1章重写100次
- **解决**: 全局熔断器，超过阈值强制SUSPEND
- 阈值配置:
  - 第1-3章: 最多3次回滚
  - 第4-10章: 最多5次回滚
  - 第11章+: 最多8次回滚
- 核心组件: `agents/creative_director.py`
- 生成文件: `.suspended.json`

### 4. 事件溯源: World Bible
- **问题**: 时间线混乱、战力崩坏、人物状态丢失
- **解决**: 记录所有关键事件用于一致性检查
- 核心组件: `core/world_bible.py`
- 事件类型: 死亡、复活、境界升级、势力变化

### 5. 单次API调用: EmotionWriter
- **问题**: 多层Skill调用导致Token爆炸
- **解决**: 整合PromptAssembler + EmotionTracker + WorldBible
- 核心组件: `agents/emotion_writer.py`

### 6. 生产者仪表板
- **功能**: 熔断状态实时显示、情绪债务可视化
- 核心组件: `ui/producer_dashboard.py` (PyQt6)

---

## 配置说明

### 环境变量 (.env)
```bash
ANTHROPIC_API_KEY=      # Claude API
OPENAI_API_KEY=         # GPT-4o API
MOONSHOT_API_KEY=       # Kimi API
DEEPSEEK_API_KEY=       # DeepSeek API
DEFAULT_MODEL_ID=       # 默认模型
```

### 配置文件
| 文件 | 功能 |
|------|------|
| `config/consistency_rules.yaml` | 一致性规则配置 |
| `config/genre_templates.yaml` | 类型模板配置 |
| `writing_constraints.json` | 项目约束配置 (自动生成) |

---

## 使用方式

### 命令行
```bash
# 交互模式
python main.py --interactive

# 使用配置文件
python main.py --config config.json

# 指定参数
python main.py --title "我的小说" --genre "仙侠" --chapters 20
```

### Web 界面
```bash
streamlit run app.py
```

---

## 开发指南

### 添加新的 Skill
1. 在 `.opencode/skills/` 下创建新文件夹
2. 添加 `SKILL.md` 文件（遵循 skill 元数据格式）
3. 在 `core/agent_manager.py` 中注册

### 添加新的 Agent
1. 在 `agents/` 下创建新文件
2. 实现标准的 Agent 接口
3. 在 `core/novel_generator.py` 中集成

---

## 许可证

MIT License
