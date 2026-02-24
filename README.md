# AI Novel Generator

A fully automated AI novel generation system built based on [Anthropic's best practices for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

[中文文档](README.zh_CN.md)

## Core Concepts

This system implements the **long-running agent** solution proposed by Anthropic:

### 1. Initializer Agent
- Sets up complete novel project environment on first run
- Creates detailed novel outline
- Designs complete character settings
- Plans chapter structure
- Sets worldview and writing style guide

### 2. Writer Agent V2 (Pipeline Architecture)
- Five-stage pipeline: Outline → Draft → Consistency Check → Polish → Final
- Integrates TimeAwareRAG for context retrieval
- Real-time validation before save
- Automatic constraint injection

### 3. Reviewer Agent
- Evaluates multiple dimensions of chapter quality
- Provides specific modification suggestions
- Ensures quality standards before marking complete

### 4. Progress Management System
- **novel-progress.txt**: Records overall progress and each chapter's status
- **chapter-list.json**: Chapter list
- **characters.json**: Character settings
- **outline.md**: Novel outline
- **writing_constraints.json**: Locked consistency constraints

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
│   └── ...
├── core/                      # Core modules
│   ├── novel_generator.py     # Main orchestrator
│   ├── agent_manager.py       # Skills management
│   ├── writing_constraint_manager.py  # Pre-writing constraints
│   ├── consistency_tracker.py # Real-time tracking
│   ├── hybrid_checker.py      # 3-layer checking
│   ├── v7_integrator.py      # Genre-aware system
│   └── ...
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

# View progress
python main.py --progress novels/my_novel
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

## Consistency Components

### WritingConstraintManager
- Located: `core/writing_constraint_manager.py`
- Loads constraints from `writing_constraints.json`
- Generates constraint prompts: `get_constraint_prompt(chapter_number)`
- Validates chapters: `validate_chapter(chapter_number, content)`

### ConsistencyTracker
- Located: `core/consistency_tracker.py`
- Tracks: realm, constitution, location, faction, timeline
- Methods: `track_realm_breakthrough()`, `track_constitution_change()`, etc.

### ConsistencyChecker
- Located: `agents/consistency_checker.py`
- Methods: `check_chapter()`, `check_all_chapters()`
- 6 detection categories

### HybridChecker
- Located: `core/hybrid_checker.py`
- 3-layer detection: regex → similarity → LLM
- Method: `check_chapter()`

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

5. Real-time Validation
   └── _pre_save_validation() before each save

6. Periodic Audit (every 5 chapters)
   └── senior-editor skill review

7. Opening Diagnosis (first 3 chapters)
   └── OpeningDiagnostician performs Golden Three Chapters diagnosis
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

---

## License

MIT License

## Acknowledgments

This system is built on Anthropic's research:
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
