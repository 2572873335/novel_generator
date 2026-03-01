# AI Novel Generator - NovelForge v5.0

A fully automated AI novel generation system built based on [Anthropic's best practices for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

**Latest Version: NovelForge v5.0** - DDD architecture with dependency inversion, unified CLI entry point, and modularized PyQt6 UI.

[中文文档](README.zh_CN.md)

## What's New in v5.0

- **All v4.2 Features** (see below)
- **Domain-Driven Design Refactoring**:
  - `NovelProject` class encapsulates all file system operations
  - Dependency inversion: UI no longer depends on raw `Path` operations
  - `core/__init__.py` facade pattern for future file reorganization

- **Unified Entry Point** (argparse subcommands):
  ```bash
  python main.py gui                    # Launch GUI (default project)
  python main.py gui -p novels/my_proj # Launch GUI with project
  python main.py cli -p novels/proj -c 100    # CLI generation
  python main.py init -t "Title" -g Fantasy -n 50  # Initialize project
  ```

- **UI Modularization**:
  - `ui/views.py` uses `NovelProject` for PreProductionView and ProjectVaultView
  - `ui/worker_thread.py` uses `NovelProject` for config and emotion ledger

---

## Core Features (v4.0)

- **Single-API-Call Writing**: Reduced API calls from 8-12 to 1 per chapter
- **Circuit Breaker**: Prevents infinite rewrite loops (force SUSPEND after threshold)
- **Python Arithmetic**: Emotion calculations done in Python, LLM receives text only
- **Event Traceability**: World Bible tracks all key events
- **Producer Dashboard**: PyQt6 UI for monitoring circuit breaker status

---

## Core Concepts

This system implements the **long-running agent** solution proposed by Anthropic:

### 1. Initializer Agent
- Sets up complete novel project environment on first run
- Creates detailed novel outline
- Designs complete character settings
- Plans chapter structure
- Sets worldview and writing style guide

### 2. NovelForge v4.0 Orchestrator
- **EmotionWriter**: Single-API-call scene writer with prompt aggregation
- **CreativeDirector**: Circuit breaker + arbitration
- **EmotionTracker**: Python-based emotion debt ledger
- **WorldBible**: Event traceability storage
- **PromptAssembler**: Multi-skill prompt aggregation

### 3. Writer Agent V2 (Pipeline Architecture)
- Five-stage pipeline: Outline → Draft → Consistency Check → Polish → Final
- Integrates TimeAwareRAG for context retrieval
- Real-time validation before save
- Automatic constraint injection

### 4. Reviewer Agent
- Evaluates multiple dimensions of chapter quality
- Provides specific modification suggestions
- Ensures quality standards before marking complete

### 5. Progress Management System (via NovelProject)
- **project_config.json**: Project configuration
- **outline.md**: Novel outline
- **characters.json**: Character settings
- **chapters/**: Chapter files
- **emotion_ledger.json**: Emotion debt tracking
- **world_bible.json**: Event traceability
- **novel-progress.txt**: Writing progress

---

## System Architecture

```
novel_generator/
├── .opencode/skills/          # Skills System (27 skills)
│   ├── Level 1 - Coordinator
│   ├── Level 2 - Architect
│   ├── Level 3 - Expert
│   └── Level 4 - Auditor
├── agents/                     # Agent modules
│   ├── writer_agent_v2.py     # Main writer with pipeline
│   ├── creative_director.py   # Circuit breaker
│   └── emotion_writer.py      # Single-API writer
├── core/                      # Core modules
│   ├── project_context.py     # [NEW v5.0] NovelProject DDD model
│   ├── __init__.py            # [NEW v5.0] Facade pattern
│   ├── novel_generator.py     # Main orchestrator
│   ├── orchestrator.py        # Main loop assembly
│   ├── agent_manager.py       # Skills management
│   ├── emotion_tracker.py     # Emotion debt
│   ├── world_bible.py         # Event traceability
│   └── prompt_assembler.py    # Prompt aggregation
├── ui/                        # UI components (modularized)
│   ├── views.py               # [v5.0] Uses NovelProject
│   ├── worker_thread.py       # [v5.0] Uses NovelProject
│   ├── components.py          # UI components
│   ├── dialogs.py             # Dialogs
│   ├── main_window.py         # Main window
│   └── themes.py              # Theme system
├── config/                    # Configuration
├── novels/                    # Generated novels
├── main.py                    # [v5.0] Unified CLI entry (argparse)
└── .env                       # Environment variables
```

---

## Installation

```bash
# Clone repository
git clone https://github.com/2572873335/novel_generator.git
cd novel_generator

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file and add your API keys
```

### Supported AI Models

| Provider | Model | Environment Variable |
|----------|-------|---------------------|
| Anthropic | Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` |
| OpenAI | GPT-4o, GPT-4o-mini | `OPENAI_API_KEY` |
| Moonshot | Kimi | `MOONSHOT_API_KEY` |
| DeepSeek | DeepSeek Chat | `DEEPSEEK_API_KEY` |
| Custom | Any compatible API | `CUSTOM_API_KEY` |

---

## Usage (v5.0)

### 1. GUI Mode (Recommended)

```bash
# Launch GUI with default project
python main.py gui

# Launch GUI with specific project
python main.py gui -p novels/my_project
```

### 2. CLI Mode

```bash
# Initialize new project
python main.py init -t "My Novel" -g Fantasy -n 50

# Run headless generation
python main.py cli -p novels/my_project -c 100

# With batch size
python main.py cli -p novels/my_project -c 50 --batch-size 10
```

### 3. Legacy Commands (Still Supported)

```bash
# Interactive mode
python main.py --interactive

# Resume from checkpoint
python main.py --project novels/my_novel --batch-size 20
```

---

## NovelProject API (v5.0)

```python
from core import NovelProject

# Create project instance
project = NovelProject("novels/my_project")

# Config operations
config = project.load_config()
project.save_config({"title": "My Novel", "genre": "Fantasy"})

# Outline operations
outline = project.load_outline()
project.save_outline("# Story Outline...")

# Character operations
characters = project.load_characters()
project.save_characters('{"characters": [...]}')

# Chapter operations
chapter = project.load_chapter(1)
project.save_chapter(1, "Chapter content...")
chapters = project.list_chapters()

# Progress operations
progress = project.load_progress()
project.save_progress({"current": 5, "total": 50})

# Emotion ledger
ledger = project.load_emotion_ledger()
project.save_emotion_ledger({"records": [...]})
```

---

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| title | string | required | Novel title |
| genre | string | general | Novel genre (xianxia, scifi, urban, etc.) |
| target_chapters | int | 10 | Target chapter count |
| words_per_chapter | int | 3000 | Words per chapter |
| description | string | "" | Story summary |

---

## Testing

```bash
# Run circuit breaker tests
python test_circuit_breaker.py
```

---

## License

MIT License

## Acknowledgments

This system is built on Anthropic's research:
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
