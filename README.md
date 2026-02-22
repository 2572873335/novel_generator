# AI Novel Generator

A fully automated AI novel generation system built based on [Anthropic's best practices for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

[中文文档](README.zh_CN.md)

## Core Concepts

This system implements the **long-running agent** solution proposed by Anthropic:

### 1. Initializer Agent
- Sets up complete novel project environment on first run
- Creates detailed novel outline
- Designs complete character settings
- Plans chapter structure (Feature List)
- Sets worldview and writing style guide

### 2. Writer Agent
- Incremental progress per session
- Focuses on one chapter at a time
- Reads progress files to understand completed content
- Updates progress files after creation
- Uses Git for version control

### 3. Reviewer Agent
- Evaluates multiple dimensions of chapter quality
- Provides specific modification suggestions
- Ensures quality standards before marking complete

### 4. Progress Management System
- **novel-progress.txt**: Records overall progress and each chapter's status
- **chapter-list.json**: Chapter list (Feature List)
- **characters.json**: Character settings
- **outline.md**: Novel outline

### 5. Consistency Defense System
- **WritingConstraintManager**: Injects constraints during writing
- **ConsistencyTracker**: Real-time tracking of realm, constitution, location, faction changes
- **ConsistencyChecker**: Strictly detects 6 major categories of consistency issues

---

## System Architecture

```
novel_generator/
├── .opencode/skills/          # Skills System (17 skills)
│   ├── Level 1 - Coordinator
│   │   ├── worldbuilder-coordinator/
│   │   ├── plot-architect-coordinator/
│   │   └── novel-coordinator/
│   ├── Level 2 - Architect
│   │   ├── outline-architect/
│   │   ├── volume-architect/
│   │   ├── chapter-architect/
│   │   ├── character-designer/
│   │   └── rhythm-designer/
│   ├── Level 3 - Expert
│   │   ├── scene-writer/
│   │   ├── cultivation-designer/
│   │   ├── currency-expert/
│   │   ├── geopolitics-expert/
│   │   ├── society-expert/
│   │   └── web-novel-methodology/
│   └── Level 4 - Auditor
│       ├── editor/
│       ├── senior-editor/
│       └── opening-diagnostician/
├── agents/                    # Agent modules
│   ├── initializer_agent.py
│   ├── writer_agent.py
│   ├── reviewer_agent.py
│   └── consistency_checker.py
├── core/                      # Core modules
│   ├── novel_generator.py
│   ├── agent_manager.py
│   ├── consistency_tracker.py
│   └── ...
├── config/                    # Configuration
│   ├── settings.py
│   └── consistency_rules.yaml
├── novels/                    # Generated novel projects
├── app.py                     # Web UI (Streamlit)
├── main.py                    # CLI entry point
├── .env                       # Environment variables
└── requirements.txt           # Dependencies
```

---

## Skills Hierarchy

The system uses a 4-level hierarchy with 17 specialized skills:

| Level | Type | Skills | Count |
|-------|------|--------|-------|
| **Level 1** | Coordinator | worldbuilder-coordinator, plot-architect-coordinator, novel-coordinator | 3 |
| **Level 2** | Architect | outline-architect, volume-architect, chapter-architect, character-designer, rhythm-designer | 5 |
| **Level 3** | Expert | scene-writer, cultivation-designer, currency-expert, geopolitics-expert, society-expert, web-novel-methodology | 6 |
| **Level 4** | Auditor | editor, senior-editor, opening-diagnostician | 3 |

### Key Features

#### Opening Diagnostician
Based on the "Golden Three Chapters" rule from Qidian, performs strict diagnosis on the first three chapters:
- 3-second rule, hook density, toxin scanning
- Gold finger reveal, conflict explosion, info density
- Rating: S/A/B/C/F (F-grade rejected)

#### Rhythm Designer
Designs precise rhythm maps for each chapter:
- Payoff density: At least 1 per 3000 words
- Compression:Release ratio: 7:3
- Chapter-end hook: Last 200 words must be a cliffhanger

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
| Moonshot | Kimi for Coding, Kimi K2.5 | `MOONSHOT_API_KEY` |
| DeepSeek | DeepSeek Chat, DeepSeek Coder | `DEEPSEEK_API_KEY` |
| Custom | Any compatible API | `CUSTOM_API_KEY` |

---

## Usage

### 1. Web UI (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

Features:
- 🏠 **Home** - Project overview and quick navigation
- ➕ **Create Project** - Configure and initialize novel project
- 💬 **Dialogue Creation** - Guide novel settings through conversation
- 📚 **Settings Library** - Manage worldview, characters, organizations
- ✍️ **Writing Control** - Start writing, quality review, export
- 📊 **Progress Monitor** - Real-time project progress and chapter status
- 🤖 **Agent Management** - View and coordinate specialized agents

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

## Four-Layer Consistency Defense System

Built-in strict consistency checks based on Qidian editor review standards:

### 1. WritingConstraintManager
Injects constraints during writing to prevent generating non-compliant content

### 2. ConsistencyTracker
Real-time tracking of state changes:
- Realm breakthrough timeline
- Constitution change records
- Location movement history
- Faction change records

### 3. ConsistencyChecker
Strictly detects 6 major categories of issues:
1. Faction name consistency
2. Character name consistency
3. Power system consistency
4. Cultivation progress consistency
5. Constitution setting consistency
6. Plot logic consistency

### 4. WriterAgent Integration
Automatic verification during writing process, detecting realm/location/faction changes

---

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| title | string | required | Novel title |
| genre | string | general | Novel genre |
| target_chapters | int | 10 | Target chapter count |
| words_per_chapter | int | 3000 | Words per chapter |
| description | string | "" | Story summary |
| enable_self_review | bool | true | Enable self-review |
| min_chapter_quality_score | float | 7.0 | Minimum quality score |

---

## Workflow

```
1. Initialization
   └── WorldBuilder + expert team builds worldview

2. Character Design
   └── CharacterDesigner designs characters

3. Plot Architecture
   └── PlotArchitect + Outline/Volume/Chapter layer-by-layer refinement

4. Rhythm Design
   └── RhythmDesigner creates rhythm map for each chapter

5. Writing
   └── SceneWriter writes chapters following rhythm map

6. Opening Diagnosis (first 3 chapters)
   └── OpeningDiagnostician performs Golden Three Chapters diagnosis

7. Review
   └── SeniorEditor performs 6-dimension review

8. Editing
   └── Editor polishes the text
```

---

## Core Advantages

### 1. Incremental Progress
- Each session handles only one chapter
- Ensures quality of each chapter

### 2. Four-Layer Consistency Defense
- Writing constraints, state tracking, consistency checking, automatic verification

### 3. Hierarchical Agents
- 17 specialized skills, 4 levels
- Coordinator → Architect → Expert → Auditor

### 4. Golden Three Chapters Diagnosis
- Based on Qidian editor standards
- 6-dimension strict inspection

### 5. Rhythm Design System
- Emotion curve design
- Payoff density control

---

## License

MIT License

## Acknowledgments

This system is built on Anthropic's research:
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)