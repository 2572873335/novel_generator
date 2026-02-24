# 全自动AI小说生成系统

基于 [Anthropic 长运行代理最佳实践](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 构建的全自动AI小说生成系统。

[English](README.md)

## 核心概念

本系统借鉴了 Anthropic 文章中提出的**长运行代理**解决方案：

### 1. Initializer Agent（初始化代理）
- 首次运行时设置完整的小说项目环境
- 创建详细的小说大纲
- 设计完整的角色设定
- 规划章节结构（Feature List）
- 设定世界观和写作风格指南

### 2. Writer Agent（写作代理）
- 每次会话进行增量式进展
- 一次只专注于一个章节
- 阅读进度文件了解已完成内容
- 创作完成后更新进度文件
- 使用Git进行版本控制

### 3. Reviewer Agent（审查代理）
- 评估章节质量的多个维度
- 提供具体的修改建议
- 确保质量达标后才标记完成

### 4. 进度管理系统
- **novel-progress.txt**: 记录整体进度和每个章节的状态
- **chapter-list.json**: 章节列表（对应文章中的 feature list）
- **characters.json**: 角色设定
- **outline.md**: 小说大纲

### 5. 一致性防御系统
- **WritingConstraintManager**: 写作时注入约束，防止违规内容生成
- **ConsistencyTracker**: 实时追踪境界、体质、地点、宗门变化
- **ConsistencyChecker**: 严格检测6大类一致性问题

---

## 系统架构

```
novel_generator/
├── .opencode/skills/          # Skills技能系统 (27个)
│   ├── Level 1 - Coordinator (协调员)
│   │   ├── worldbuilder-coordinator/
│   │   ├── plot-architect-coordinator/
│   │   └── novel-coordinator/
│   ├── Level 2 - Architect (架构师)
│   │   ├── outline-architect/
│   │   ├── volume-architect/
│   │   ├── chapter-architect/
│   │   ├── character-designer/
│   │   └── rhythm-designer/        # 新增
│   ├── Level 3 - Expert (专家)
│   │   ├── scene-writer/
│   │   ├── cultivation-designer/
│   │   ├── currency-expert/
│   │   ├── geopolitics-expert/
│   │   ├── society-expert/
│   │   └── web-novel-methodology/
│   └── Level 4 - Auditor (审计)
│       ├── editor/
│       ├── senior-editor/
│       └── opening-diagnostician/  # 新增
├── agents/                    # 代理模块
│   ├── initializer_agent.py
│   ├── writer_agent.py
│   ├── reviewer_agent.py
│   └── consistency_checker.py
├── core/                      # 核心模块
│   ├── novel_generator.py    # 主控制器
│   ├── agent_manager.py      # 智能体调度 (含层级架构)
│   ├── consistency_tracker.py
│   └── ...
├── config/                    # 配置模块
│   ├── settings.py
│   └── consistency_rules.yaml
├── novels/                    # 生成的小说项目
├── app.py                     # Web UI界面（Streamlit）
├── main.py                    # 命令行入口
├── .env                       # 环境变量
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
- 金手指亮相、冲突爆发、信息密度
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

### 1. Web UI 界面（推荐）

```bash
streamlit run app.py
```

然后在浏览器中打开 http://localhost:8501

功能包括：
- 🏠 **首页** - 项目概览和快速导航
- ➕ **创建新项目** - 填写小说配置并初始化
- 💬 **对话创作** - 通过对话引导完成小说设定
- 📚 **设定库管理** - 管理世界观、人物、组织等设定
- ✍️ **写作控制** - 启动写作、质量审查、合并导出
- 📊 **进度监控** - 实时查看项目进度和章节状态
- 🤖 **智能体管理** - 查看和协调专业智能体

### 2. 命令行模式

```bash
# 交互式模式
python main.py --interactive

# 使用配置文件
python main.py --config my_novel.json

# 使用命令行参数
python main.py --title "我的小说" --genre "玄幻" --chapters 20

# 查看进度
python main.py --progress novels/my_novel
```

---

## 四层防御一致性系统

基于起点编辑审稿意见，系统内置严格的一致性检查：

### 1. WritingConstraintManager
写作时注入约束，防止生成违规内容

### 2. ConsistencyTracker
实时追踪状态变化：
- 境界突破时间线
- 体质变更记录
- 地点移动历史
- 宗门变更记录

### 3. ConsistencyChecker
严格检测6大类问题：
1. 宗门名称一致性
2. 人物姓名一致性
3. 战力体系一致性
4. 修为进度一致性
5. 体质设定一致性
6. 情节逻辑一致性

### 4. WriterAgent 集成
写作流程中自动验证，检测境界/地点/宗门变化

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

5. 写作
   └── SceneWriter 按节奏地图撰写章节

6. 开篇诊断（前3章）
   └── OpeningDiagnostician 进行黄金三章诊断

7. 审稿
   └── SeniorEditor 进行6维度审稿

8. 编辑润色
   └── Editor 润色文字
```

---

## 核心优势

### 1. 增量式进展
- 每次会话只处理一个章节
- 确保每个章节的质量

### 2. 四层一致性防御
- 写作约束、状态追踪、一致性检查、自动验证

### 3. 层级化智能体
- 27个专业技能，4个层级
- Coordinator → Architect → Expert → Auditor

### 4. 黄金三章诊断
- 基于起点编辑标准
- 6维度严苛检测

### 5. 节奏设计系统
- 情绪曲线设计
- 爽点密度控制

---

## 许可证

MIT License

## 致谢

本系统基于 Anthropic 的研究成果：
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
