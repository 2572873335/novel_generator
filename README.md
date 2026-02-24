# AI Novel Generator - NovelForge v4.0

A fully automated AI novel generation system built based on [Anthropic's best practices for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

**Latest Version: NovelForge v4.0** - Production-ready with circuit breaker mechanism, emotion tracking, and single-API-call architecture.

[中文文档](README.zh_CN.md)

## What's New in v4.0

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

### 2. NovelForge v4.0 Orchestrator (NEW)
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

### 5. Progress Management System
- **novel-progress.txt**: Records overall progress and each chapter's status
- **chapter-list.json**: Chapter list
- **characters.json**: Character settings
- **outline.md**: Novel outline
- **writing_constraints.json**: Locked consistency constraints
- **emotion_ledger.json**: Emotion debt tracking (v4.0)
- **world_bible.json**: Event traceability (v4.0)

---

## Three-Layer Consistency Defense System

The system implements a robust 3-layer defense to prevent consistency issues:

### Layer 1: Pre-Writing (WritingConstraintManager)
- Injects strict constraints into LLM prompts
- Locks faction names, character names, realm system
- Prevents generation of non-compliant content

**Features:**
- Faction whitelist enforcement
- Character name locking
- Realm hierarchy rules
- Cultivation speed limits
- Constitution locking
- Timeline constraints
- Weapon naming rules

### Layer 2: Real-time Validation (_pre_save_validation)
- Validates chapter before saving
- Uses WritingConstraintManager.validate_chapter()
- Triggers rewrite if critical violations found

**Checks:**
- Faction name consistency
- Character name variants
- Cross-realm combat violations
- Cultivation speed violations
- Constitution change violations

### Layer 3: Post-Writing (Senior-editor Audit)
- Every 5 chapters: calls senior-editor skill
- Multi-dimensional quality review
- Detects issues missed by automated checks

---

## NovelForge v4.0 Key Features

### 1. Anti-Token-Blackhole: Prompt Aggregation
Merge L2+L3 skills into single prompt assembly, reducing API calls from 8-12 to 1 per chapter.

### 2. Anti-LLM-Math-Disaster: Python Arithmetic
All emotion calculations done in Python, LLM receives only text instructions.

### 3. Anti-Infinite-Loop: Circuit Breaker
```
Chapters 1-3:  Max 3 rollbacks → Force SUSPEND
Chapters 4-10: Max 5 rollbacks → Force SUSPEND
Chapters 11+:  Max 8 rollbacks → Force SUSPEND
```

### 4. Event Traceability: World Bible
Records key events (deaths, resurrections, realm upgrades) for consistency checking.

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
│   ├── consistency_checker.py # Strict consistency checker
│   ├── senior_editor_v2.py    # Senior editor
│   ├── creative_director.py   # [NEW v4.0] Circuit breaker
│   └── emotion_writer.py      # [NEW v4.0] Single-API writer
├── core/                      # Core modules
│   ├── novel_generator.py     # Main orchestrator
│   ├── orchestrator.py        # [NEW v4.0] Main loop assembly
│   ├── agent_manager.py       # Skills management
│   ├── writing_constraint_manager.py  # Pre-writing constraints
│   ├── consistency_tracker.py # Real-time tracking
│   ├── hybrid_checker.py      # 3-layer checking
│   ├── v7_integrator.py      # Genre-aware system
│   ├── emotion_tracker.py     # [NEW v4.0] Emotion debt
│   ├── world_bible.py        # [NEW v4.0] Event traceability
│   ├── prompt_assembler.py   # [NEW v4.0] Prompt aggregation
│   └── ...
├── ui/                        # [NEW v4.0] UI components
│   └── producer_dashboard.py # Circuit breaker visualization
├── config/                    # Configuration
│   └── consistency_rules.yaml
├── novels/                    # Generated novels
├── app.py                     # Web UI (Streamlit)
├── main.py                    # CLI entry point
├── .env                       # Environment variables
└── requirements.txt           # Dependencies
```

---

## Skills Hierarchy

The system uses a 4-level hierarchy with 27 specialized skills:

| Level | Type | Skills | Count |
|-------|------|--------|-------|
| **Level 1** | Coordinator | worldbuilder-coordinator, plot-architect-coordinator, novel-coordinator | 3 |
| **Level 2** | Architect | outline-architect, volume-architect, chapter-architect, character-designer, rhythm-designer | 5 |
| **Level 3** | Expert | scene-writer, cultivation-designer, currency-expert, geopolitics-expert, society-expert, web-novel-methodology | 6 |
| **Level 4** | Auditor | editor, senior-editor, opening-diagnostician | 3 |

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

## Usage

### 1. Web UI (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### 2. Command Line Mode

```bash
# Interactive mode
python main.py --interactive

# Use config file
python main.py --config my_novel.json

# Use command line arguments
python main.py --title "My Novel" --genre "Fantasy" --chapters 20

# Batch mode (recommended for long novels)
python main.py --title "My Novel" --genre "Fantasy" --chapters 1000 --batch-size 20

# Resume from checkpoint
python main.py --project novels/my_novel --batch-size 20

# View progress
python main.py --progress novels/my_novel
```

### 3. Producer Dashboard (v4.0)

```bash
# Run circuit breaker visualization UI
python -m ui.producer_dashboard novels/my_project
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
| enable_self_review | bool | true | Enable self-review |
| min_chapter_quality_score | float | 7.0 | Minimum quality score |

---

## NovelForge v4.0 Components

### EmotionTracker (core/emotion_tracker.py)
- Python-based emotion debt ledger
- Automatic decay (30% per chapter)
- Generates text instructions for LLM

### WorldBible (core/world_bible.py)
- Event traceability storage
- Records: deaths, resurrections, realm upgrades
- Supports event reversal

### PromptAssembler (core/prompt_assembler.py)
- Aggregates multiple skills into single prompt
- Elastic outline (near clear, far fuzzy)
- Emotion continuity checking

### CreativeDirector (agents/creative_director.py)
- Circuit breaker with configurable thresholds
- Arbitration: PASS / REWRITE / ROLLBACK / SUSPEND
- Generates .suspended.json when triggered

### EmotionWriter (agents/emotion_writer.py)
- Single-API-call scene writer
- Integrates PromptAssembler + EmotionTracker + WorldBible
- Automatic event extraction

### Orchestrator (core/orchestrator.py)
- Main loop with checkpoint support
- Coordinates all v4.0 components
- Handles retry logic

---

## Workflow

```
1. Initialization
   └── WorldBuilder + expert team builds worldview

2. Character Design
   └── CharacterDesigner designs characters

3. Plot Architecture
   └── PlotArchitect + Outline/Volume/Chapter layer-by-layer refinement

4. Writing (Pipeline)
   └── WriterAgentV2: Outline → Draft → Consistency → Polish → Final

5. v4.0 Writing (Single-API)
   └── EmotionWriter: PromptAssembly → LLM → EmotionTrack → EventRecord

6. Real-time Validation
   └── _pre_save_validation() before each save

7. Periodic Audit (every 5 chapters)
   └── senior-editor skill review

8. Circuit Breaker Check (v4.0)
   └── CreativeDirector: Check threshold → SUSPEND if triggered
```

---

## Core Advantages

### 1. Three-Layer Consistency Defense
- Pre-writing: Constraint injection
- Real-time: Validation before save
- Post-writing: Senior-editor audit

### 2. Incremental Progress
- Each session handles only one chapter
- Ensures quality of each chapter

### 3. Hierarchical Agents
- 27 specialized skills, 4 levels
- Coordinator → Architect → Expert → Auditor

### 4. Genre-Aware System (V7)
- Auto-detects 6 genre types
- Genre-specific constraint templates

### 5. NovelForge v4.0 Production Features
- Single-API-call reduces cost and latency
- Circuit breaker prevents infinite loops
- Python arithmetic ensures calculation accuracy
- Event traceability prevents timeline issues

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
