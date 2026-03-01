# 全自动AI小说生成系统 - NovelForge v5.0

基于 [Anthropic 长运行代理最佳实践](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 构建的全自动AI小说生成系统。

**最新版本: NovelForge v5.0** - DDD领域驱动设计架构，依赖倒置，统一CLI入口，模块化PyQt6 UI。

[English](README.md)

## v5.0 新特性

- **v4.2 所有功能** (见下文)
- **DDD领域驱动设计重构**:
  - `NovelProject` 类封装所有文件系统操作
  - 依赖倒置：UI不再依赖原始 `Path` 操作
  - `core/__init__.py` Facade模式，为未来文件重组做准备

- **统一入口点** (argparse 子命令):
  ```bash
  python main.py gui                    # 启动GUI（默认项目）
  python main.py gui -p novels/我的项目  # 指定项目启动GUI
  python main.py cli -p novels/proj -c 100    # CLI生成模式
  python main.py init -t "标题" -g 玄幻 -n 50   # 初始化项目
  ```

- **UI模块化**:
  - `ui/views.py` 使用 `NovelProject` 处理 PreProductionView 和 ProjectVaultView
  - `ui/worker_thread.py` 使用 `NovelProject` 处理配置和情绪账本

---

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
- 规划章节结构

### 2. NovelForge v4.0 编排器
- **EmotionWriter**: 单次API调用场景写作
- **CreativeDirector**: 熔断机制+仲裁
- **EmotionTracker**: Python情绪债务账本
- **WorldBible**: 事件溯源存储
- **PromptAssembler**: 多技能Prompt聚合

### 3. Writer Agent V2（写作代理）
- 五阶段管道：大纲 → 草稿 → 一致性检查 → 润色 → 终稿
- 集成 TimeAwareRAG 上下文检索
- 保存前实时验证

### 4. Reviewer Agent（审查代理）
- 评估章节质量的多个维度
- 提供具体的修改建议

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
│   ├── writer_agent_v2.py    # 主管道写作代理
│   ├── creative_director.py  # 熔断仲裁器
│   └── emotion_writer.py      # 单次API写作
├── core/                      # 核心模块
│   ├── project_context.py     # [v5.0] NovelProject DDD模型
│   ├── __init__.py           # [v5.0] Facade模式
│   ├── novel_generator.py    # 主控制器
│   ├── orchestrator.py       # 主循环组装
│   ├── agent_manager.py      # 智能体调度
│   ├── emotion_tracker.py    # 情绪债务
│   ├── world_bible.py        # 事件溯源
│   └── prompt_assembler.py   # Prompt聚合
├── ui/                        # UI组件（模块化）
│   ├── views.py              # [v5.0] 使用NovelProject
│   ├── worker_thread.py      # [v5.0] 使用NovelProject
│   ├── components.py         # UI组件
│   ├── dialogs.py            # 对话框
│   ├── main_window.py        # 主窗口
│   └── themes.py              # 主题系统
├── config/                    # 配置模块
├── novels/                   # 生成的小说项目
└── .env                      # 环境变量
```

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
| Moonshot | Kimi | `MOONSHOT_API_KEY` |
| DeepSeek | DeepSeek Chat | `DEEPSEEK_API_KEY` |
| 自定义 | 任意兼容API | `CUSTOM_API_KEY` |

---

## 使用方法 (v5.0)

### 1. GUI模式（推荐）

```bash
# 启动GUI（使用默认项目）
python main.py gui

# 启动GUI（指定项目）
python main.py gui -p novels/我的项目
```

### 2. CLI模式

```bash
# 初始化新项目
python main.py init -t "我的小说" -g 玄幻 -n 50

# 运行无头生成
python main.py cli -p novels/我的小说 -c 100

# 指定批次大小
python main.py cli -p novels/我的小说 -c 50 --batch-size 10
```

### 3. 兼容旧命令

```bash
# 交互式模式
python main.py --interactive

# 从检查点恢复
python main.py --project novels/my_novel --batch-size 20
```

---

## NovelProject API (v5.0)

```python
from core import NovelProject

# 创建项目实例
project = NovelProject("novels/我的项目")

# 配置操作
config = project.load_config()
project.save_config({"title": "我的小说", "genre": "玄幻"})

# 大纲操作
outline = project.load_outline()
project.save_outline("# 故事大纲...")

# 人物操作
characters = project.load_characters()
project.save_characters('{"characters": [...]}')

# 章节操作
chapter = project.load_chapter(1)
project.save_chapter(1, "章节内容...")
chapters = project.list_chapters()

# 进度操作
progress = project.load_progress()
project.save_progress({"current": 5, "total": 50})

# 情绪账本
ledger = project.load_emotion_ledger()
project.save_emotion_ledger({"records": [...]})
```

---

## 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | 必填 | 小说标题 |
| genre | string | general | 小说类型 |
| target_chapters | int | 10 | 目标章节数 |
| words_per_chapter | int | 3000 | 每章字数 |
| description | string | "" | 故事简介 |

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
