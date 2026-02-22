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

系统采用四级层级架构，17个专业技能协同工作：

```
Level 1: Coordinator (协调员) - 3个
├── worldbuilder-coordinator    世界观总控
├── plot-architect-coordinator  剧情总控
└── novel-coordinator           项目协调

Level 2: Architect (架构师) - 5个
├── outline-architect   故事大纲
├── volume-architect    卷纲设计
├── chapter-architect   章纲设计
├── character-designer  人物设计
└── rhythm-designer     节奏设计 (新增)

Level 3: Expert (专家) - 6个
├── scene-writer         场景写作
├── cultivation-designer 修炼体系
├── currency-expert      货币经济
├── geopolitics-expert   地缘政治
├── society-expert       社会结构
└── web-novel-methodology 网文方法论

Level 4: Auditor (审计) - 3个
├── editor               编辑润色
├── senior-editor        资深审稿
└── opening-diagnostician 开篇诊断 (新增)
```

### 新增核心功能

#### 1. 开篇诊断 (opening-diagnostician)
基于起点"黄金三章"法则，对前三章进行严苛诊断：
- **三秒定律**：前500字必须出现主角名
- **钩子密度**：每300字至少一个悬念点
- **毒点扫描**：检测绿帽、圣母、虐主过度等致命问题
- **金手指亮相**：第1章必须展示核心优势
- **冲突爆发**：3000字内首场核心冲突
- **信息密度**：禁止大段世界观说明文

评级标准：S/A/B/C/F（F级拒绝生成）

#### 2. 节奏设计 (rhythm-designer)
为每个章节设计精确的节奏地图：
- **爽点密度**：每3000字至少1个小爽点
- **压抑释放比**：7:3
- **章末钩子**：最后200字必须是cliffhanger
- **情绪曲线**：波浪形情绪变化
- **信息密度**：禁止连续500字无剧情推进

输出：YAML格式节奏地图

---

## 四层防御一致性系统

基于起点编辑审稿意见，系统内置严格的一致性检查，防止常见致命缺陷：

### 1. WritingConstraintManager (core/writing_constraint_manager.py)
写作时注入约束，防止生成违规内容：
- 宗门名称白名单锁定
- 人物姓名锁定
- 战力体系规则（禁止跨大境界战斗）
- 修炼速度限制（小境界7天，大境界30天）
- 体质设定锁定

### 2. ConsistencyTracker (core/consistency_tracker.py)
实时追踪状态变化：
- RealmState - 境界突破时间线
- ConstitutionState - 体质变更记录
- LocationState - 地点移动历史
- FactionState - 宗门变更记录

**阈值设置**：
- 高威胁敌人：威胁等级 ≥ 6 必须有代价才能击败
- 主角能力上限：核心能力不超过 4 个

### 3. ConsistencyChecker (agents/consistency_checker.py)
严格检测6大类问题：
1. 宗门名称一致性（防止精神分裂）
2. 人物姓名一致性（防止姓名混乱）
3. 战力体系一致性（防止战力崩坏）
4. 修为进度一致性（防止坐火箭）
5. 体质设定一致性（防止设定变更）
6. 情节逻辑一致性（防止逻辑硬伤）

### 4. WriterAgent 集成
写作流程中自动验证：
- 加载上下文时获取约束提示
- 写作完成后验证章节内容
- 自动检测境界/地点/宗门变化

### 配置文件
- `config/consistency_rules.yaml` - 验证规则

---

## Build & Test Commands

```bash
# 运行命令行程序（交互模式）
python main.py --interactive

# 使用配置文件运行
python main.py --config my_novel.json

# 使用命令行参数
python main.py --title "我的小说" --genre "科幻" --chapters 10

# 查看项目进度
python main.py --progress novels/my_novel

# 启动Web UI界面
streamlit run app.py
```

---

## Project Structure

```
novel_generator/
├── .opencode/skills/         # Skills技能目录 (17个)
│   ├── worldbuilder-coordinator/
│   ├── plot-architect-coordinator/
│   ├── novel-coordinator/
│   ├── outline-architect/
│   ├── volume-architect/
│   ├── chapter-architect/
│   ├── character-designer/
│   ├── rhythm-designer/          # 新增
│   ├── scene-writer/
│   ├── cultivation-designer/
│   ├── currency-expert/
│   ├── geopolitics-expert/
│   ├── society-expert/
│   ├── web-novel-methodology/
│   ├── editor/
│   ├── senior-editor/
│   └── opening-diagnostician/    # 新增
├── agents/                   # Agent实现
│   ├── initializer_agent.py
│   ├── writer_agent.py
│   ├── reviewer_agent.py
│   └── consistency_checker.py
├── core/                     # 核心功能
│   ├── novel_generator.py    # 主控制器
│   ├── agent_manager.py      # 智能体调度 (含层级架构)
│   ├── consistency_tracker.py # 设定追踪
│   ├── writing_constraint_manager.py # 约束管理
│   ├── progress_manager.py
│   ├── chapter_manager.py
│   ├── character_manager.py
│   ├── model_manager.py
│   └── log_manager.py
├── config/                   # 配置模块
│   ├── settings.py
│   └── consistency_rules.yaml
├── novels/                   # 生成的小说项目
├── app.py                    # Web UI (Streamlit)
├── main.py                   # 命令行入口
├── .env                      # 环境变量
└── requirements.txt          # 依赖配置
```

---

## 小说项目文档结构

```
novel-project/
├── outline.md               # 小说大纲
├── characters.json          # 角色设定
├── chapter-list.json        # 章节列表
├── world-rules.json         # 世界观规则（含修炼体系）
├── novel-progress.txt       # 进度跟踪
├── chapters/                # 章节内容
│   ├── chapter-001.md
│   └── ...
├── reviews/                 # 审查报告
│   ├── review-001.md
│   └── ...
├── consistency_reports/     # 一致性检查报告
│   └── consistency_005.md
└── agent_outputs/           # 智能体输出
    ├── worldbuilder_output.md
    └── ...
```

---

## Code Style Guidelines

### Imports
```python
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

try:
    from .consistency_tracker import ConsistencyTracker
except ImportError:
    from consistency_tracker import ConsistencyTracker
```

### Type Hints
```python
def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    ...

def get_skill_hierarchy(self) -> Dict[str, Any]:
    hierarchy: Dict[str, List[Dict]] = {...}
    return hierarchy
```

### Naming Conventions
- Classes: `PascalCase` (AgentManager, ConsistencyTracker)
- Functions: `snake_case` (get_skill_hierarchy, validate_triggers)
- Private: `_leading_underscore` (_parse_skill_metadata)
- Constants: `UPPER_SNAKE_CASE`

### Data Classes
```python
@dataclass
class SkillMetadata:
    name: str
    level: str = "expert"
    triggers: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    subordinates: List[str] = field(default_factory=list)
```

---

## Environment Configuration

- API keys stored in `.env` file (never commit)
- Use `.env.example` as template
- Key variables: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MOONSHOT_API_KEY`, `DEEPSEEK_API_KEY`
- Custom model: `CUSTOM_MODEL_NAME`, `CUSTOM_BASE_URL`, `CUSTOM_API_KEY_ENV`
