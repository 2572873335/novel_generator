# AGENTS.md

Coding agent instructions for the Novel Generator AI system.

## Build & Test Commands

```bash
# 运行命令行程序
python main.py --interactive
python main.py --config my_novel.json

# 启动Web UI界面
streamlit run app.py

# 运行单个测试（当存在测试时）
pytest tests/test_file.py::test_function -v

# 运行所有测试
pytest tests/ -v

# 代码格式化（可选，来自requirements.txt）
black .

# 代码检查（可选，来自requirements.txt）
flake8 .
```

## Project Structure

```
novel_generator/
├── agents/           # Agent实现
│   ├── initializer_agent.py
│   ├── writer_agent.py
│   └── reviewer_agent.py
├── core/            # 核心功能
│   ├── novel_generator.py
│   ├── progress_manager.py
│   ├── chapter_manager.py
│   └── character_manager.py
├── config/          # 配置模块
│   └── settings.py
├── app.py           # Web UI界面（Streamlit）
├── main.py          # 命令行入口
└── requirements.txt # 依赖配置
```

## Code Style Guidelines

### Imports
- Standard library imports first (os, json, typing)
- Third-party imports second
- Local module imports last
- Use try/except for optional dependencies
- Handle both relative and absolute imports

```python
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from progress_manager import ProgressManager
except ImportError:
    from .progress_manager import ProgressManager
```

### Type Hints
- Use type hints for all function parameters and return types
- Use `Optional[Type]` for nullable values
- Use `Dict[str, Any]` for JSON-like data
- Use `List[Type]` for collections

```python
def process_chapter(self, chapter_number: int, content: str) -> Dict[str, Any]:
    result: Optional[ChapterProgress] = self.get_chapter(chapter_number)
```

### Naming Conventions
- Classes: `PascalCase` (NovelGenerator, WriterAgent)
- Functions/Variables: `snake_case` (write_session, chapter_number)
- Private methods: `_leading_underscore` (_load_progress)
- Constants: `UPPER_SNAKE_CASE` (DEFAULT_CONFIG)
- Type variables: descriptive names (chapter_number, not ch)

### Docstrings
- Use triple-quoted docstrings for all public classes and methods
- Document Args and Returns sections
- Include type information in docstrings

```python
def run(self) -> Dict[str, Any]:
    """Run the complete novel generation workflow.
    
    Returns:
        Dict containing generation statistics and results
    """
```

### Data Classes
- Use `@dataclass` for configuration and data models
- Implement `__post_init__` for default value initialization
- Use `asdict()` for serialization

```python
@dataclass
class NovelProgress:
    title: str
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

```python
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### Error Handling
- Use try-except for file operations and external calls
- Return `Optional[Type]` when operations might fail
- Log errors with descriptive messages
- Use specific exception types when possible

```python
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
except FileNotFoundError:
    return None
except json.JSONDecodeError as e:
    print(f"Invalid JSON in {filepath}: {e}")
    return None
```

### Project Conventions
- Progress files: `novel-progress.txt` (JSON format)
- Chapter files: `chapter-{number:03d}.md`
- Project directories: `novels/{title.replace(' ', '_').lower()}/`
- Status values: pending, writing, reviewing, completed, revision_needed
- Quality scores: 1.0 to 10.0 scale

### Architecture Patterns
- Agents handle business logic
- Managers handle data persistence
- Use clear separation between initialization, writing, and review phases
- Each session should update progress files
- Git-style commits are logged for each chapter completion
