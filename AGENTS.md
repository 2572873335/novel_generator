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
- `/写作 [章节号]` - 撰写指定章节
- `/编辑 [章节号]` - 编辑指定章节
- `/状态` - 查看项目状态

### 工作流程
1. 用户提出需求 → 初始化项目
2. `/世界观` → 构建世界观
3. `/人物` → 设计人物
4. `/大纲` → 生成大纲
5. `/卷纲` → 细化卷纲
6. `/章纲` → 细化章纲
7. `/写作` → 撰写章节
8. `/编辑` → 润色章节

### 质量标准
- 逻辑自洽，设定一致
- 人物立体，动机清晰
- 情节紧凑，节奏流畅
- 文字生动，画面感强

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

# 运行单个测试（当存在测试时）
pytest tests/test_file.py::test_function -v

# 运行所有测试
pytest tests/ -v

# 代码格式化（可选）
black .

# 代码检查（可选）
flake8 .
ruff check .
```

## Project Structure

```
novel_generator/
├── agents/                 # Agent实现
│   ├── initializer_agent.py
│   ├── writer_agent.py
│   ├── reviewer_agent.py
│   └── *.md               # 专业智能体提示词(WorldBuilder, CharacterDesigner等)
├── .opencode/              # Skills目录
│   └── skills/
│       ├── worldbuilder-coordinator/
│       │   └── SKILL.md
│       ├── currency-expert/
│       │   └── SKILL.md
│       ├── geopolitics-expert/
│       │   └── SKILL.md
│       ├── society-expert/
│       │   └── SKILL.md
│       ├── cultivation-designer/
│       │   └── SKILL.md
│       ├── plot-architect-coordinator/
│       │   └── SKILL.md
│       ├── outline-architect/
│       │   └── SKILL.md
│       ├── volume-architect/
│       │   └── SKILL.md
│       ├── chapter-architect/
│       │   └── SKILL.md
│       ├── character-designer/
│       │   └── SKILL.md
│       ├── scene-writer/
│       │   └── SKILL.md
│       ├── editor/
│       │   └── SKILL.md
│       └── novel-coordinator/
│           └── SKILL.md
├── core/                   # 核心功能
│   ├── novel_generator.py  # 主控制器
│   ├── progress_manager.py # 进度管理
│   ├── chapter_manager.py  # 章节管理
│   ├── character_manager.py
│   ├── agent_manager.py    # 智能体调度
│   ├── model_manager.py    # AI模型管理
│   ├── config_manager.py   # 配置/API密钥管理
│   └── log_manager.py      # 日志系统
├── config/                 # 配置模块
│   └── settings.py         # NovelConfig, AgentPrompts
├── novels/                 # 生成的小说项目目录
├── logs/                   # 日志文件
├── app.py                  # Web UI界面（Streamlit）
├── main.py                 # 命令行入口
├── .env                    # 环境变量（API密钥等）
├── .env.example            # 环境变量示例
└── requirements.txt        # 依赖配置
```

## 小说项目文档结构

```
novel-project/
├── AGENTS.md               # AI行为准则
├── world/                  # 世界观文档
├── characters/             # 人物文档
├── plot/                   # 剧情文档
└── manuscript/             # 正文稿件
```

## Code Style Guidelines

### Imports
- Standard library imports first (os, json, sys, time)
- Third-party imports second (streamlit, pathlib)
- Local module imports last
- Use try/except for optional dependencies
- Handle both relative and absolute imports

```python
import os
import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

try:
    from progress_manager import ProgressManager
except ImportError:
    from .progress_manager import ProgressManager
```

### Type Hints
- Use type hints for all function parameters and return types
- Use `Optional[Type]` for nullable values
- Use `Dict[str, Any]` for JSON-like data and config dictionaries
- Use `List[Type]` for collections
- Import from `typing` module explicitly

```python
def process_chapter(self, chapter_number: int, content: str) -> Dict[str, Any]:
    result: Optional[ChapterProgress] = self.get_chapter(chapter_number)

def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    ...

def get_available_agents(self) -> List[Dict[str, str]]:
    ...
```

### Naming Conventions
- Classes: `PascalCase` (NovelGenerator, WriterAgent, ProgressManager)
- Functions/Methods: `snake_case` (write_session, load_progress, update_chapter_status)
- Private methods: `_leading_underscore` (_load_progress, _save_progress, _mock_execute)
- Constants: `UPPER_SNAKE_CASE` (DEFAULT_CONFIG, INITIALIZER_SYSTEM_PROMPT)
- Variables: descriptive `snake_case` (chapter_number, not ch; novel_config, not nc)
- File names: `snake_case.py` (novel_generator.py, agent_manager.py)

### Docstrings
- Use triple-quoted docstrings for all public classes and methods
- Document Args and Returns sections
- Include type information in docstrings
- Chinese docstrings are acceptable

```python
def initialize_progress(self, title: str, genre: str, total_chapters: int,
                       chapter_titles: List[str]) -> NovelProgress:
    """初始化小说进度
    
    Args:
        title: 小说标题
        genre: 小说类型
        total_chapters: 总章节数
        chapter_titles: 章节标题列表
        
    Returns:
        NovelProgress: 初始化后的进度对象
    """

def run(self) -> Dict[str, Any]:
    """Run the complete novel generation workflow.
    
    Returns:
        Dict containing generation statistics and results
    """
```

### Data Classes
- Use `@dataclass` for configuration and data models
- Implement `__post_init__` for default value initialization
- Use `asdict()` for serialization to JSON

```python
@dataclass
class ChapterProgress:
    chapter_number: int
    title: str
    status: str  # pending, writing, reviewing, completed, revision_needed
    word_count: int = 0
    quality_score: float = 0.0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class NovelProgress:
    title: str
    genre: str
    total_chapters: int
    chapters: List[ChapterProgress] = None
    
    def __post_init__(self):
        if self.chapters is None:
            self.chapters = []
```

### File Operations
- Always specify `encoding='utf-8'` for text files
- Use context managers (with statements)
- Handle file existence checks before operations
- Use JSON with `ensure_ascii=False` for Chinese text
- Use `Path` from pathlib for path operations

```python
# Writing files
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Reading files
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Using pathlib
from pathlib import Path
chapters_dir = Path(project_dir) / "chapters"
if chapters_dir.exists():
    chapter_files = sorted(chapters_dir.glob("chapter-*.md"))

# Check existence before reading
if not os.path.exists(progress_file):
    return None
```

### Error Handling
- Use try-except for file operations and external calls
- Return `Optional[Type]` when operations might fail
- Log errors with descriptive messages (use log_manager)
- Use specific exception types when possible
- Print user-friendly error messages

```python
# File operations
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
except FileNotFoundError:
    return None
except json.JSONDecodeError as e:
    print(f"Invalid JSON in {filepath}: {e}")
    return None

# General operations
try:
    result = create_novel(config)
    if result['success']:
        print(f"Success: {result['project_dir']}")
except Exception as e:
    st.error(f"Error: {str(e)}")
    logger.log_error_with_traceback(e, "create_novel")
```

### Project Conventions
- Progress files: `novel-progress.txt` (JSON format)
- Chapter files: `chapter-{number:03d}.md` (e.g., chapter-001.md)
- Chapter list: `chapter-list.json`
- Project directories: `novels/{title.replace(' ', '_').lower()}/`
- Status values: pending, writing, reviewing, completed, revision_needed
- Quality scores: 1.0 to 10.0 scale (7.0 is minimum passing score)
- Review files: `reviews/review-{number:03d}.md`

### Architecture Patterns
- Agents handle business logic and AI interactions
- Managers handle data persistence and state
- Use clear separation: initialization → writing → review → merge
- Each session should update progress files
- Git-style commits are logged for each chapter completion
- Coordinator pattern: AgentManager orchestrates multiple specialized agents

### Agent System
- Core agents (Python): InitializerAgent, WriterAgent, ReviewerAgent
- Specialized agents (Markdown prompts): WorldBuilder, CharacterDesigner, PlotArchitect, OutlineArchitect, SceneWriter, Editor, VolumeArchitect, ChapterArchitect, CultivationDesigner, CurrencyExpert, GeopoliticsExpert, SocietyExpert
- Agents receive context dict and return result dict
- Use `AgentManager` to coordinate multi-agent workflows

### Environment Configuration
- API keys stored in `.env` file (never commit)
- Use `.env.example` as template
- Key environment variables: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MOONSHOT_API_KEY`, `DEEPSEEK_API_KEY`, `DEFAULT_MODEL_ID`, `DEFAULT_TEMPERATURE`, `DEFAULT_MAX_TOKENS`
- Custom model support via `CUSTOM_MODEL_NAME`, `CUSTOM_BASE_URL`, `CUSTOM_API_KEY_ENV`

### Streamlit UI Patterns
- Use `st.session_state` for state management
- Initialize session state in dedicated function
- Use `st.columns()` for layouts
- Custom CSS via `st.markdown()` with `unsafe_allow_html=True`
- Form submissions use `st.form()` context manager
