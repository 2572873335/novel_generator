# AGENTS.md

Coding agent instructions for the Novel Generator AI system.

## 小说创作AI团队

这是一个专业的AI小说创作团队，包含世界观构建、人物设计、剧情架构、场景写作、编辑润色等多个专业角色。

### 可用指令
- `/世界观` - 启动世界观构建流程
- `/人物` - 启动人物设计流程
- `/大纲` - 启动大纲架构
- `/卷纲` - 启动卷纲架构
- `/章纲` - 启动章纲架构
- `/节奏` - 启动节奏设计流程
- `/开篇诊断` - 对前三章进行黄金三章诊断
- `/写作 [章节号]` - 撰写指定章节
- `/编辑 [章节号]` - 编辑指定章节
- `/审稿 [章节号]` - 资深编辑审稿
- `/状态` - 查看项目状态

### 工作流程
1. 用户提出需求 → 初始化项目
2. `/世界观` → 构建世界观
3. `/人物` → 设计人物
4. `/大纲` → 生成大纲
5. `/卷纲` → 细化卷纲
6. `/章纲` → 细化章纲
7. `/节奏` → 设计章节节奏
8. `/写作` → 撰写章节
9. `/开篇诊断` → 诊断前三章（可选）
10. `/审稿` → 资深编辑审稿
11. `/编辑` → 润色章节

### 质量标准
- 逻辑自洽，设定一致
- 人物立体，动机清晰
- 情节紧凑，节奏流畅
- 文字生动，画面感强
- 开篇合规，符合黄金三章

---

## Skills 层级架构

系统采用四级层级架构，17+个专业技能协同工作：

```
Level 1: Coordinator (协调员) - 3个
├── worldbuilder-coordinator    世界观总控
├── plot-architect-coordinator  剧情总控
└── novel-coordinator         小说总控

Level 2: Architect (架构师) - 5个
├── outline-architect         大纲架构
├── volume-architect           卷纲架构
├── chapter-architect          章纲架构
├── character-designer        人物设计
└── rhythm-designer           节奏设计

Level 3: Expert (专家) - 6个
├── scene-writer              场景写作
├── cultivation-designer      修炼体系设计
├── currency-expert           货币体系专家
├── geopolitics-expert        地缘政治专家
├── society-expert           社会结构专家
└── web-novel-methodology    网文方法论

Level 4: Auditor (审核) - 3个
├── editor                    编辑
├── senior-editor             资深编辑
└── opening-diagnostician    开篇诊断
```

---

## Agent 模块

### 核心 Agent

| Agent | 文件 | 功能 |
|-------|------|------|
| WriterAgentV2 | agents/writer_agent_v2.py | 主管道写作，五阶段流水线 |
| ConsistencyChecker | agents/consistency_checker.py | 严格一致性检查 |
| SeniorEditorV2 | agents/senior_editor_v2.py | 资深编辑审核 |
| MarketAnalyzer | agents/market_analyzer.py | 市场分析 |

### 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| NovelGenerator | core/novel_generator.py | 主控协调器 |
| AgentManager | core/agent_manager.py | 智能体管理与技能加载 |
| WritingConstraintManager | core/writing_constraint_manager.py | 写作约束管理器 |
| ConsistencyTracker | core/consistency_tracker.py | 设定一致性追踪器 |
| HybridChecker | core/hybrid_checker.py | 混合检查器 |
| V7Integrator | core/v7_integrator.py | 类型感知系统 |

---

## 三层一致性防御系统

### 第一层：事前约束 (WritingConstraintManager)
- 将约束注入LLM提示词
- 锁定宗门名称、人物姓名、境界体系
- 防止生成不符合设定的内容

### 第二层：事中校验 (_pre_save_validation)
- 章节保存前实时校验
- 使用WritingConstraintManager.validate_chapter()
- 发现问题立即触发重写

### 第三层：事后审核 (Senior-editor)
- 每5章调用资深编辑审核
- 多维度质量审查
- 检测自动化检查遗漏的问题

---

## 配置说明

### 环境变量 (.env)
```
ANTHROPIC_API_KEY=       # Claude API
OPENAI_API_KEY=          # GPT-4o API
MOONSHOT_API_KEY=        # Kimi API
DEEPSEEK_API_KEY=        # DeepSeek API
```

### 配置文件
- `config/consistency_rules.yaml` - 一致性规则配置
- `writing_constraints.json` - 项目约束配置（自动生成）

---

## 使用示例

### 命令行模式
```bash
# 交互模式
python main.py --interactive

# 使用配置文件
python main.py --config config.json

# 指定参数
python main.py --title "我的小说" --genre "仙侠" --chapters 20
```

### Web界面
```bash
streamlit run app.py
```

---

## 开发指南

### 添加新的Skill
1. 在 `.opencode/skills/` 下创建新文件夹
2. 添加 `SKILL.md` 文件
3. 在 `core/agent_manager.py` 中注册

### 添加新的Agent
1. 在 `agents/` 下创建新文件
2. 实现标准的Agent接口
3. 在 `core/novel_generator.py` 中集成

---

## 许可证

MIT License
