# 更新日志 (Changelog)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.2.1] - 2026-02-26

### Added
- **UI 全面优化 (v4.2)**

- **赛博朋克主题 v2.0**:
  - 增强对比度的色彩系统 (WCAG 4.5:1)
  - 新增字体系统 (Typography)
  - 新增间距系统 (Spacing)
  - 新增布局常量 (Layout)

- **顶部状态栏**:
  - 显示系统状态、项目名称、进度、当前模型
  - 集成主题选择器
  - 设置按钮

- **组件级优化**:
  - **Agent工牌**: 边框发光效果、脉冲动画、进度环、3D翻转
  - **日志面板**: 语法高亮、级别过滤按钮、日志计数、HTML导出
  - **情绪波浪图**: 阈值线、发光曲线、数据点标记、动态颜色
  - **熔断面板**: 红色警报动画、回滚历史条形图、重置按钮、状态指示灯
  - **前期筹备室**: 可折叠面板、自动保存指示器、卡片式评估展示

- **高级功能**:
  - **日志搜索过滤**: 关键词实时搜索 + Agent筛选 + 级别筛选
  - **自定义主题**: 4套主题 (赛博朋克、霓虹蓝、日落、森林)
  - 主题切换器集成到顶部状态栏

- **布局优化**:
  - 面板位置调整: 日志(左) | Agent(中) | 可视化(右)
  - 窗口尺寸调整: 1600x900 (默认), 1400x800 (最小)

### Fixed
- 修复 Agent 工牌翻转动画
- 修复日志面板全屏时崩溃问题 (QRadialGradient QPointF 兼容性)
- 修复项目配置加载顺序问题

---

## [4.2.0] - 2026-02-25

### Added
- **PyQt6 Dashboard 全面升级 (v4.1)**

- **UI布局重构**:
  - 重新设计三栏布局：左侧Agent工牌+详情面板，中间日志，右侧情绪曲线
  - Agent工牌使用GridLayout排列（每行3个），避免重叠
  - Agent工牌点击可查看详细信息
  - 新增 `AgentDetailPanel` 显示选中Agent的完整信息和工作日志

- **前期筹备增强**:
  - 评估结果显示后增加"采纳建议并修改"和"手动修改"按钮
  - 添加"重新评估"按钮支持循环优化大纲和人物设定
  - 支持分步骤显示生成过程

- **断点续写功能**:
  - 启动时自动检测历史进度
  - 弹窗询问"继续写作"或"重新开始"
  - 支持从指定章节继续生成

- **用户反馈与文档查看**:
  - 章节完成后弹窗显示摘要、质量分数、Agent日志
  - 新增菜单"查看文档"可查看大纲、人物、任意章节
  - 日志面板增加Agent筛选下拉框
  - 添加日志导出按钮

- **删除Web UI**:
  - 删除 `app.py` (Streamlit Web界面)
  - 统一使用 PyQt6 Dashboard

### Changed
- 更新 CLAUDE.md 命令说明，移除 streamlit 命令

---

## [4.1.1] - 2026-02-25

### Fixed
- **Issue 1: 章节截断问题修复**
  - 在Prompt中添加防截断规则: `<rule>你必须完整地结束本章，严禁在句子中间或对话中间截断！...</rule>`
  - 增加max_tokens到8192确保完整输出
  - 添加后处理函数 `_clean_incomplete_sentences` 清理不完整句子

- **Issue 2: 前期筹备UI标签页**
  - 在ProducerDashboard中添加QTabWidget
  - Tab 1: "前期筹备 (Pre-Production)" - 大纲和人物设定编辑器
  - Tab 2: "生产监控 (Production Dashboard)" - 现有UI
  - 添加"生成设置"、"评估设置"、"批准并开始写作"按钮
  - **实现评估功能**：调用LLM进行资深编辑评估（开篇、人物、世界观、剧情结构、商业性）

- **Issue 3: Agent状态键匹配**
  - UI Agent列表添加: `ElasticArchitect`, `PayoffAuditor`
  - Orchestrator统一使用正确的agent名称
  - 在所有Agent操作阶段触发状态更新

---

## [4.1.0] - 2026-02-25

### Added
- **Issue 3 修复**: 新增项目初始化功能 (`_initialize_project_if_needed`)
  - 自动生成 `outline.md` (故事大纲)
  - 自动生成 `characters.json` (人物设定)
  - 在第1章写作前自动调用LLM生成

- **Agent状态回调**: 在写作流程各阶段主动触发UI状态更新
  - 大纲阶段: `PromptAssembler`, `ElasticArchitect`
  - 写作阶段: `EmotionWriter`
  - 仲裁阶段: `ConsistencyGuardian`, `PayoffAuditor`, `CreativeDirector`

### Changed
- **Issue 1 修复**: 章节保存格式从JSON改为Markdown
  - 主文件: `chapter_001.md`, `chapter_002.md` 等
  - 元数据: `chapter_001.json` (情绪数据)
  - 文件名格式: `chapter_XXX.md` (3位数字)

- **目录结构优化**:
  - 核心代码: `core/`
  - Agent代码: `agents/`
  - UI组件: `ui/`
  - 配置文件: `config/`
  - 文档: 保留在根目录

### Fixed
- 修复章节元数据JSON中存储为旧格式的问题
- 修复初始化时缺少world-rules.json的问题

---

## [4.0.0] - 2026-02-20

### Added
- **NovelForge v4.0 架构**
  - 单次API调用场景写作 (EmotionWriter)
  - 熔断仲裁机制 (CreativeDirector)
  - Prompt聚合层 (PromptAssembler)
  - 情绪债务账本 (EmotionTracker)
  - 事件溯源存储 (WorldBible)
  - 一致性检查 (ConsistencyGuardian)
  - 文风锁定 (StyleAnchor)

- **Producer Dashboard UI** (PyQt6)
  - 赛博朋克主题
  - Agent状态指示灯
  - 情绪波浪图
  - 实时裁决日志

### Changed
- 重构核心架构，从多Agent调用改为单次调用
- 新增checkpoint机制支持断点续写

---

## [3.x] - 更早版本

### Added
- 多级Skills架构 (L1-L4)
- V7类型检测与约束系统
- RAG一致性检查
- 质量门控 (QualityGate)

---

## 目录结构说明

```
novel_generator/
├── core/           # 核心组件
├── agents/         # Agent实现
├── ui/             # UI组件
├── config/         # 配置文件
├── novels/        # 生成的小说项目
├── main.py        # CLI入口
├── app.py         # Web UI入口
├── CLAUDE.md      # 项目说明(重要!)
├── README.md      # 使用说明
└── CHANGELOG.md   # 本文件
```

---

## 如何贡献更新

1. 修改代码后，在对应位置添加功能说明
2. 更新版本号并添加新的 `[版本]` 章节
3. 使用以下标签:
   - `Added` - 新功能
   - `Changed` - 功能变更
   - `Deprecated` - 已废弃功能
   - `Removed` - 已移除功能
   - `Fixed` - Bug修复
   - `Security` - 安全更新
