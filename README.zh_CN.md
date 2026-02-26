# 全自动AI小说生成系统 - NovelForge v4.2

基于 [Anthropic 长运行代理最佳实践](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 构建的全自动AI小说生成系统。

**最新版本: NovelForge v4.2** - 工业级生产环境就绪版本，包含熔断机制、情绪追踪、单次API调用架构和增强版PyQt6 UI。

[English](README.md)

## v4.2 新特性

- **v4.0 所有功能** (见下文)
- **增强版生产者仪表板 UI (v4.2)**:
  - 赛博朋克主题 v2.0，优化色彩对比度
  - 顶部状态栏，含主题选择器
  - 高级日志面板，支持搜索和过滤
  - 情绪波浪图，含阈值线
  - 熔断面板，含回滚历史图表
  - 前期筹备室，含自动保存指示器
  - 4套内置主题: 赛博朋克、霓虹蓝、日落、森林

## v4.0 核心功能

- **单次API调用**: 每章API调用从8-12次减少到1次
- **熔断机制**: 防止无限重写循环（超过阈值强制暂停）
- **Python算术**: 情绪计算在Python中完成，LLM只接收文本
- **事件溯源**: World Bible 追踪所有关键事件
- **生产者仪表板**: PyQt6熔断可视化UI

---

## 核心概念

本系统借鉴了 Anthropic 文章中提出的**长运行代理**解决方案：

### 1. Initializer Agent（初始化代理）
- 首次运行时设置完整的小说项目环境
- 创建详细的小说大纲
- 设计完整的角色设定
- 规划章节结构（Feature List）
- 设定世界观和写作风格指南

### 2. NovelForge v4.0 编排器（新增）
- **EmotionWriter**: 单次API调用场景写作
- **CreativeDirector**: 熔断机制+仲裁
- **EmotionTracker**: Python情绪债务账本
- **WorldBible**: 事件溯源存储
- **PromptAssembler**: 多技能Prompt聚合

### 3. Writer Agent（写作代理）
- 每次会话进行增量式进展
- 一次只专注于一个章节
- 阅读进度文件了解已完成内容
- 创作完成后更新进度文件
- 使用Git进行版本控制

### 4. Reviewer Agent（审查代理）
- 评估章节质量的多个维度
- 提供具体的修改建议
- 确保质量达标后才标记完成

### 5. 进度管理系统
- **novel-progress.txt**: 记录整体进度和每个章节的状态
- **chapter-list.json**: 章节列表（对应文章中的 feature list）
- **characters.json**: 角色设定
- **outline.md**: 小说大纲
- **emotion_ledger.json**: 情绪债务追踪 (v4.0)
- **world_bible.json**: 事件溯源 (v4.0)

---

## 三层一致性防御系统

基于起点编辑审稿意见，系统内置严格的一致性检查：

### 第1层: 写作前约束 (WritingConstraintManager)
- 写作时注入约束，防止生成违规内容
- 锁定宗门名、角色名、境界体系

### 第2层: 实时验证 (_pre_save_validation)
- 保存前验证章节
- 检测到严重违规则触发重写

### 第3层: 写作后审查 (Senior-editor)
- 每5章调用一次资深编辑技能
- 多维度质量审查
- 检测自动化检查遗漏的问题

---

## NovelForge v4.0 核心特性

### 1. 防Token黑洞: Prompt聚合
将L2+L3技能合并为单次Prompt，减少API调用从8-12次/章到1次/章。

### 2. 防LLM计算灾难: Python算术
所有情绪计算在Python中完成，LLM只接收文本指令。

### 3. 防无限循环: 熔断机制
```
第1-3章:  最多3次回滚 → 强制暂停
第4-10章: 最多5次回滚 → 强制暂停
第11章+:  最多8次回滚 → 强制暂停
```

### 4. 事件溯源: World Bible
记录关键事件（死亡、复活、境界升级）用于一致性检查。

---

## 系统架构

```
novel_generator/
├── .opencode/skills/          # Skills技能系统 (27个)
│   ├── Level 1 - Coordinator (协调员)
│   ├── Level 2 - Architect (架构师)
│   ├── Level 3 - Expert (专家)
│   └── Level 4 - Auditor (审计)
├── agents/                    # 代理模块
│   ├── writer_agent_v2.py     # 主管道写作代理
│   ├── consistency_checker.py # 严格一致性检查
│   ├── senior_editor_v2.py   # 资深编辑
│   ├── creative_director.py  # [v4.0] 熔断仲裁器
│   └── emotion_writer.py     # [v4.0] 单次API写作
├── core/                      # 核心模块
│   ├── novel_generator.py    # 主控制器
│   ├── orchestrator.py       # [v4.0] 主循环组装
│   ├── agent_manager.py      # 智能体调度
│   ├── writing_constraint_manager.py # 写作约束
│   ├── consistency_tracker.py # 实时追踪
│   ├── hybrid_checker.py     # 3层检查
│   ├── v7_integrator.py      # 类型感知系统
│   ├── emotion_tracker.py    # [v4.0] 情绪债务
│   ├── world_bible.py        # [v4.0] 事件溯源
│   ├── prompt_assembler.py   # [v4.0] Prompt聚合
│   └── ...
├── ui/                        # [v4.0] UI组件
│   └── producer_dashboard.py # 熔断可视化
├── config/                    # 配置模块
│   └── consistency_rules.yaml
├── novels/                   # 生成的小说项目
├── app.py                    # Web UI界面（Streamlit）
├── main.py                   # 命令行入口
├── .env                      # 环境变量
└── requirements.txt           # 依赖配置
```

---

## Skills 层级架构

系统采用四级层级架构，27个专业技能协同工作：

| 层级 | 类型 | Skills | 数量 |
|------|------|--------|------|
| **Level 1** | Coordinator | worldbuilder-coordinator, plot-architect-coordinator, novel-coordinator | 3 |
| **Level 2** | Architect | outline-architect, volume-architect, chapter-architect, character-designer, rhythm-designer | 5 |
| **Level 3** | Expert | scene-writer, cultivation-designer, currency-expert, geopolitics-expert, society-expert, web-novel-methodology | 6 |
| **Level 4** | Auditor | editor, senior-editor, opening-diagnostician | 3 |

### 新增核心功能

#### 开篇诊断 (opening-diagnostician)
基于起点"黄金三章"法则，对前三章进行严苛诊断：
- 三秒定律、钩子密度、毒点扫描
- 金手指亮相、冲突爆发，信息密度
- 评级：S/A/B/C/F（F级拒绝生成）

#### 节奏设计 (rhythm-designer)
为每个章节设计精确的节奏地图：
- 爽点密度：每3000字至少1个
- 压抑释放比：7:3
- 章末钩子：最后200字必须是cliffhanger

---

## 安装

```bash
# 克隆仓库
git clone https://github.com/2572873335/novel_generator.git
cd novel_generator

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 支持的AI模型

| 提供商 | 模型 | 环境变量 |
|--------|------|----------|
| Anthropic | Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` |
| OpenAI | GPT-4o, GPT-4o-mini | `OPENAI_API_KEY` |
| Moonshot | Kimi for Coding, Kimi K2.5 | `MOONSHOT_API_KEY` |
| DeepSeek | DeepSeek Chat, DeepSeek Coder | `DEEPSEEK_API_KEY` |
| 自定义 | 任意兼容API | `CUSTOM_API_KEY` |

---

## 使用方法

### 1. 命令行模式

```bash
# 交互式模式
python main.py --interactive

# 使用配置文件
python main.py --config my_novel.json

# 使用命令行参数
python main.py --title "我的小说" --genre "玄幻" --chapters 20

# 批量模式（推荐长篇小说）
python main.py --title "我的小说" --genre "玄幻" --chapters 1000 --batch-size 20

# 从检查点恢复
python main.py --project novels/my_novel --batch-size 20

# 查看进度
python main.py --progress novels/my_novel
```

### 2. 生产者仪表板 (v4.0)

```bash
# 运行熔断可视化UI
python -m ui.producer_dashboard novels/my_project
```

---

## NovelForge v4.0 组件

### EmotionTracker (core/emotion_tracker.py)
- Python情绪债务账本
- 自动衰减（每章30%）
- 生成文本指令给LLM

### WorldBible (core/world_bible.py)
- 事件溯源存储
- 记录：死亡、复活、境界升级
- 支持事件反转

### PromptAssembler (core/prompt_assembler.py)
- 聚合多技能为单次Prompt
- 弹性大纲（近景清晰，远景模糊）
- 情绪连续性检查

### CreativeDirector (agents/creative_director.py)
- 熔断机制带可配置阈值
- 仲裁：PASS / REWRITE / ROLLBACK / SUSPEND
- 触发时生成.suspended.json

### EmotionWriter (agents/emotion_writer.py)
- 单次API调用场景写作
- 集成PromptAssembler + EmotionTracker + WorldBible
- 自动事件提取

### Orchestrator (core/orchestrator.py)
- 带检查点支持的主循环
- 协调所有v4.0组件
- 处理重试逻辑

---

## 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | 必填 | 小说标题 |
| genre | string | general | 小说类型 |
| target_chapters | int | 10 | 目标章节数 |
| words_per_chapter | int | 3000 | 每章字数 |
| description | string | "" | 故事简介 |
| enable_self_review | bool | true | 启用自我审查 |
| min_chapter_quality_score | float | 7.0 | 最低质量分数 |

---

## 工作流程

```
1. 初始化
   └── WorldBuilder + 专家团队构建世界观

2. 角色设计
   └── CharacterDesigner 设计人物

3. 剧情架构
   └── PlotArchitect + Outline/Volume/Chapter 层层细化

4. 节奏设计
   └── RhythmDesigner 为每章设计节奏地图

5. 写作（管道）
   └── WriterAgentV2: 大纲 → 草稿 → 一致性 → 润色 → 终稿

6. v4.0 写作（单次API）
   └── EmotionWriter: Prompt组装 → LLM → 情绪追踪 → 事件记录

7. 实时验证
   └── 保存前验证

8. 定期审查（每5章）
   └── 资深编辑审查

9. 开篇诊断（前3章）
   └── OpeningDiagnostician 进行黄金三章诊断

10. 熔断检查 (v4.0)
    └── CreativeDirector: 检查阈值 → 触发则暂停
```

---

## 核心优势

### 1. 三层一致性防御
- 写作约束、状态追踪、一致性检查、自动验证

### 2. 增量式进展
- 每次会话只处理一个章节
- 确保每个章节的质量

### 3. 层级化智能体
- 27个专业技能，4个层级
- Coordinator → Architect → Expert → Auditor

### 4. 黄金三章诊断
- 基于起点编辑标准
- 6维度严苛检测

### 5. 节奏设计系统
- 情绪曲线设计
- 爽点密度控制

### 6. NovelForge v4.0 生产特性
- 单次API调用降低成本和延迟
- 熔断防止无限循环
- Python算术确保计算准确
- 事件溯源防止时间线问题

---

## 测试

```bash
# 运行熔断机制测试
python test_circuit_breaker.py
```

---

## 许可证

MIT License

## 致谢

本系统基于 Anthropic 的研究成果：
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
