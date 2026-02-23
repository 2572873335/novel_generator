# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Novel Generator - A fully automated AI novel generation system based on Anthropic's long-running agent architecture. Supports multiple AI providers (Anthropic Claude, OpenAI, Moonshot, DeepSeek).

## Commands

```bash
# Web UI (recommended)
streamlit run app.py

# CLI modes
python main.py --interactive                    # Interactive mode
python main.py --config config.json            # Use config file
python main.py --title "My Novel" --genre "Fantasy" --chapters 20
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NovelGenerator                            │
│                      (core/novel_generator.py)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│  AgentManager │    │ V7Integrator    │    │ WritingConstraint   │
│  (Skill Load) │    │ (Genre-Aware)   │    │ Manager (Pre-write) │
└───────────────┘    └─────────────────┘    └─────────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WriterAgentV2                               │
│             (5-stage Pipeline: Outline→Draft→Check→Polish)     │
└─────────────────────────────────────────────────────────────────┘
        │
        ├─→ HybridChecker (3-layer consistency)
        ├─→ ConsistencyTracker (state tracking)
        ├─→ SkillContextBus (cross-skill context)
        ├─→ TimeAwareRAG (temporal retrieval)
        └─→ CheckpointManager (recovery)
```

## Directory Structure

```
novel_generator/
├── agents/                    # Agent implementations
│   ├── writer_agent_v2.py    # Main writing agent (pipeline)
│   ├── consistency_checker.py # Strict consistency check
│   ├── reviewer_agent.py      # Review agent
│   ├── senior_editor_v2.py   # Senior editor agent
│   ├── market_analyzer.py     # Market analysis
│   ├── rag_consistency_checker.py # RAG consistency
│   └── initializer_agent.py  # Initializer
│
├── core/                      # Core systems
│   ├── novel_generator.py     # Main orchestration
│   ├── agent_manager.py       # Agent & skill management
│   ├── v7_integrator.py      # V7 genre-aware system
│   ├── genre_detector.py     # Genre detection
│   ├── constraint_template_manager.py # Constraint templates
│   ├── constraint_arbiter.py  # Constraint arbitration
│   ├── writing_constraint_manager.py # Pre-write constraints
│   ├── consistency_tracker.py # Consistency tracking
│   ├── hybrid_checker.py      # Hybrid checker (regex+sim+LLM)
│   ├── skill_context_bus.py   # Skill context bus
│   ├── checkpoint_manager.py  # Checkpoint & recovery
│   ├── time_aware_rag.py      # Time-aware RAG
│   ├── local_vector_store.py  # Local vector store
│   ├── expectation_tracker.py # Expectation tracking
│   ├── reader_expectation.py  # Reader expectation
│   ├── entity_graph.py        # Entity relationship graph
│   ├── character_state_machine.py # Character state machine
│   ├── state_snapshot.py      # State snapshots
│   ├── summary_indexer.py     # Summary indexer
│   ├── chapter_manager.py     # Chapter management
│   ├── character_manager.py   # Character management
│   ├── progress_manager.py   # Progress tracking
│   ├── model_manager.py       # Model management
│   └── config_manager.py      # Config management
│
├── config/                    # Configuration files
│   ├── consistency_rules.yaml # Consistency rules
│   └── genre_templates.yaml   # Genre templates
│
├── .opencode/skills/          # Skill system (27 skills)
│   ├── level1_coordinator/    # L1: Coordinators (3)
│   ├── level2_architect/      # L2: Architects (5)
│   ├── level3_expert/         # L3: Experts (6)
│   ├── level4_auditor/        # L4: Auditors (3)
│   ├── style_*/               # Style skills (7)
│   └── genre_expert/         # Genre experts (3)
│
├── novels/                    # Generated novel projects
├── main.py                    # CLI entry point
└── app.py                     # Web UI (Streamlit)
```

## Core Components

### Agents (`agents/`)

| Agent | File | Description |
|-------|------|-------------|
| WriterAgentV2 | `writer_agent_v2.py` | Main writing agent with 5-stage pipeline |
| ConsistencyChecker | `consistency_checker.py` | Strict consistency verification |
| SeniorEditorV2 | `senior_editor_v2.py` | Senior editor for quality review |
| ReviewerAgent | `reviewer_agent.py` | Chapter review agent |
| MarketAnalyzer | `market_analyzer.py` | Market trend analysis |
| RAGConsistencyChecker | `rag_consistency_checker.py` | RAG-based consistency |
| InitializerAgent | `initializer_agent.py` | Project initialization |

### Core Modules (`core/`)

| Module | File | Description |
|--------|------|-------------|
| NovelGenerator | `novel_generator.py` | Main orchestration |
| AgentManager | `agent_manager.py` | Agent & skill management |
| V7Integrator | `v7_integrator.py` | Genre-aware system |
| GenreDetector | `genre_detector.py` | Genre detection |
| WritingConstraintManager | `writing_constraint_manager.py` | Pre-write constraints |
| ConsistencyTracker | `consistency_tracker.py` | Real-time state tracking |
| HybridChecker | `hybrid_checker.py` | 3-layer consistency |
| SkillContextBus | `skill_context_bus.py` | Cross-skill context |
| CheckpointManager | `checkpoint_manager.py` | Enhanced checkpoints |
| TimeAwareRAG | `time_aware_rag.py` | Temporal RAG retrieval |

## Skills System (27 Skills)

Located in `.opencode/skills/`, organized in 4 levels + styles + genre experts:

| Level | Type | Count | Skills |
|-------|------|-------|--------|
| **Level 1** | Coordinator | 3 | worldbuilder-coordinator, plot-architect-coordinator, novel-coordinator |
| **Level 2** | Architect | 5 | outline-architect, volume-architect, chapter-architect, character-designer, rhythm-designer |
| **Level 3** | Expert | 6 | scene-writer, cultivation-designer, currency-expert, geopolitics-expert, society-expert, web-novel-methodology |
| **Level 4** | Auditor | 3 | editor, senior-editor, opening-diagnostician |
| **Styles** | 文风 | 7 | style-blood-punch, style-cowboy, style-dark, style-infinity, style-building, style-serious, style-sweet |
| **Genre** | 类型 | 3 | scifi-expert, suspense-expert, urban-expert |

**Total: 27 skills**

## 3-Layer Consistency Defense System

The system implements a robust 3-layer consistency defense:

### Layer 1: Pre-writing (事前)
**Component**: `WritingConstraintManager`
- Injects strict constraints into LLM prompts
- Locks faction names, character names, realm system
- Prevents generation of non-compliant content

### Layer 2: Real-time (事中)
**Component**: `_pre_save_validation()` in WriterAgentV2
- Validates chapter before saving
- Uses WritingConstraintManager.validate_chapter()
- Triggers rewrite if critical violations found

### Layer 3: Post-writing (事后)
**Component**: `SeniorEditorV2` / `senior-editor` skill
- Every 5 chapters: calls senior-editor skill
- Multi-dimensional quality review
- Detects issues missed by automated checks

## Key Optimizations (2024)

### 1. Opening Diagnosis Enforcement
- Chapters 1-3 auto-call `opening-diagnostician` skill
- Grade D/F triggers forced rewrite
- Reports saved to `opening_diagnosis/`

### 2. Payoff Density Monitoring
- 20 payoff keywords real-time detection
- Threshold: 0.3/千字
- Warning triggered below threshold

### 3. Skill Context Bus
- Solves 17-skill island problem
- Cross-skill state transfer (realm, faction, payoff density)
- Persisted to `skill_context.json`

### 4. Dynamic Power Detection
- LLM extracts realm descriptions per chapter
- Detects power anomalies and realm jumps
- Compares with previous chapters for warnings

### 5. Enhanced Checkpoint System
- Recovery from any checkpoint
- LLM timeout auto-retry
- Human-in-loop pause points

## Environment

Configure `.env` with API keys:
```bash
ANTHROPIC_API_KEY=      # Claude API
OPENAI_API_KEY=         # GPT-4o API
MOONSHOT_API_KEY=       # Kimi API
DEEPSEEK_API_KEY=       # DeepSeek API
DEFAULT_MODEL_ID=       # Default model
```

## Configuration Files

| File | Description |
|------|-------------|
| `config/consistency_rules.yaml` | Consistency rule configuration |
| `config/genre_templates.yaml` | Genre template configuration |
| `writing_constraints.json` | Project constraints (auto-generated) |

## Consistency Checker Components

### WritingConstraintManager (`core/writing_constraint_manager.py`)
- Loads constraints from `writing_constraints.json`
- Generates constraint prompts with `get_constraint_prompt()`
- Validates chapters with `validate_chapter()`
- Updates state after each chapter
- Dynamic realm hierarchy loading from world-rules.json

### ConsistencyTracker (`core/consistency_tracker.py`)
- Tracks realm progression
- Tracks constitution changes
- Tracks location/faction changes
- Monitors timeline consistency

### HybridChecker (`core/hybrid_checker.py`)
- `check_chapter()`: Real-time chapter validation
- 3-layer detection: regex → similarity → LLM
- Faction name whitelist enforcement
- `extract_realm_with_llm()`: Dynamic realm extraction

### SkillContextBus (`core/skill_context_bus.py`)
- Cross-skill state sharing
- `update()`: Update skill context
- `get_full_context()`: Get complete context
- `get_recent_context()`: Query recent contexts

### CheckpointManager (`core/checkpoint_manager.py`)
- Recoverable checkpoints
- `create_checkpoint()`: Create new checkpoint
- `recover_content()`: Recover from checkpoint
- RetryableLLMCall for error handling
- HumanInLoop for pause points

## CLI Commands

```bash
# Interactive mode
python main.py --interactive

# With config file
python main.py --config config.json

# With parameters
python main.py --title "My Novel" --genre "Fantasy" --chapters 20

# Web UI
streamlit run app.py
```

## Development Guide

### Adding New Skills
1. Create new folder under `.opencode/skills/`
2. Add `SKILL.md` file (follow skill metadata format)
3. Register in `core/agent_manager.py`

### Adding New Agents
1. Create new file under `agents/`
2. Implement standard agent interface
3. Integrate in `core/novel_generator.py`

## License

MIT License
