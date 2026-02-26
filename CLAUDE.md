# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Novel Generator - A fully automated AI novel generation system based on Anthropic's long-running agent architecture. Supports multiple AI providers (Anthropic Claude, OpenAI, Moonshot, DeepSeek).

**Latest: NovelForge v4.2** - Production-ready with circuit breaker mechanism, emotion tracking, single-API-call architecture, and enhanced PyQt6 UI.

## Commands

```bash
# PyQt6 Dashboard (recommended)
python -m ui.producer_dashboard novels/my_project

# CLI modes
python main.py --interactive                    # Interactive mode
python main.py --config config.json            # Use config file
python main.py --title "My Novel" --genre "Fantasy" --chapters 20

# Batch mode (recommended for long novels)
python main.py --title "My Novel" --genre "Fantasy" --chapters 1000 --batch-size 20

# Resume from checkpoint
python main.py --project novels/my_novel --batch-size 20
```

## System Architecture

### NovelForge v4.0 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator (core/orchestrator.py)          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ NovelForge v4.0 Core (7-Module Architecture)             │  │
│  │ 1. EmotionWriter (单次API调用场景写作)                    │  │
│  │ 2. CreativeDirector (熔断仲裁机制)                       │  │
│  │ 3. PromptAssembler (Prompt聚合层)                        │  │
│  │ 4. EmotionTracker (情绪债务账本)                          │  │
│  │ 5. WorldBible (事件溯源存储)                             │  │
│  │ 6. ConsistencyGuardian (一致性检查)                      │  │
│  │ 7. StyleAnchor (文风锁定)                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│  Emotion     │    │ Circuit         │    │ Producer           │
│  Tracker     │    │ Breaker         │    │ Dashboard          │
│  (Python)    │    │ Monitor         │    │ (PyQt6 UI)         │
└───────────────┘    └─────────────────┘    └─────────────────────┘
```

### Legacy Architecture (v3.x)

```
┌─────────────────────────────────────────────────────────────────┐
│                        NovelGenerator                            │
│                      (core/novel_generator.py)                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 4-Level Skills Architecture (闭环)                       │  │
│  │ Level 1: Coordinator (novel-coordinator)                  │  │
│  │ Level 2: Architect (outline, character, chapter)          │  │
│  │ Level 3: Expert (scene-writer + QualityGate)             │  │
│  │ Level 4: Auditor (senior-editor + ConsistencyChecker)     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────────┐
│  AgentManager │    │ V7Integrator    │    │ QualityGate        │
│  (Skill Load) │    │ (Genre-Aware)   │    │ (Level 3+4 Check)  │
└───────────────┘    └─────────────────┘    └─────────────────────┘
```

## Directory Structure

```
novel_generator/
├── agents/                    # Agent implementations
│   ├── writer_agent_v2.py     # Main writing agent (pipeline)
│   ├── consistency_checker.py # Sliding window consistency
│   ├── reviewer_agent.py      # Review agent
│   ├── senior_editor_v2.py    # Senior editor (semantic)
│   ├── market_analyzer.py     # Market analysis
│   ├── rag_consistency_checker.py # RAG consistency
│   ├── initializer_agent.py   # Initializer
│   │
│   ├── creative_director.py  # [NEW v4.0] Circuit breaker + arbitration
│   └── emotion_writer.py      # [NEW v4.0] Single-API-call writer
│
├── core/                      # Core systems
│   ├── novel_generator.py     # Main orchestration
│   ├── orchestrator.py       # [NEW v4.0] Main loop assembly
│   ├── quality_gate.py        # Quality gate
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
│   ├── config_manager.py      # Config management
│   │
│   ├── emotion_tracker.py     # [NEW v4.0] Emotion debt ledger
│   ├── world_bible.py         # [NEW v4.0] Event traceability
│   └── prompt_assembler.py    # [NEW v4.0] Prompt aggregation
│
├── ui/                        # [NEW v4.0] UI components
│   └── producer_dashboard.py  # Circuit breaker visualization
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
│   └── genre_expert/          # Genre experts (3)
│
├── novels/                    # Generated novel projects
├── main.py                    # CLI entry point
└── app.py                     # Web UI (Streamlit)
```

## Core Components

### NovelForge v4.0 Components (`core/` + `agents/`)

| Component | File | Description |
|-----------|------|-------------|
| **Orchestrator** | `orchestrator.py` | [NEW v4.0] Main loop with checkpoint support |
| **EmotionWriter** | `emotion_writer.py` | [NEW v4.0] Single-API-call scene writer |
| **CreativeDirector** | `creative_director.py` | [NEW v4.0] Circuit breaker + arbitration |
| **EmotionTracker** | `emotion_tracker.py` | [NEW v4.0] Python-based emotion debt ledger |
| **WorldBible** | `world_bible.py` | [NEW v4.0] Event traceability storage |
| **PromptAssembler** | `prompt_assembler.py` | [NEW v4.0] Multi-skill prompt aggregation |

### Legacy Agents (`agents/`)

| Agent | File | Description |
|-------|------|-------------|
| WriterAgentV2 | `writer_agent_v2.py` | Main writing agent with 5-stage pipeline + feedback loop |
| ConsistencyChecker | `consistency_checker.py` | Sliding window consistency (last 5 chapters) |
| SeniorEditorV2 | `senior_editor_v2.py` | Semantic quality review (6 dimensions) |
| ReviewerAgent | `reviewer_agent.py` | Chapter review agent |
| MarketAnalyzer | `market_analyzer.py` | Market trend analysis |
| RAGConsistencyChecker | `rag_consistency_checker.py` | RAG-based consistency |
| InitializerAgent | `initializer_agent.py` | Project initialization |

### Legacy Core Modules (`core/`)

| Module | File | Description |
|--------|------|-------------|
| NovelGenerator | `novel_generator.py` | Main orchestration with batch processing |
| QualityGate | `quality_gate.py` | Unified quality check with Skills architecture |
| AgentManager | `agent_manager.py` | Agent & skill management |
| V7Integrator | `v7_integrator.py` | Genre-aware system |
| GenreDetector | `genre_detector.py` | Genre detection |
| WritingConstraintManager | `writing_constraint_manager.py` | Pre-write constraints |
| ConsistencyTracker | `consistency_tracker.py` | Real-time state tracking |
| HybridChecker | `hybrid_checker.py` | 3-layer consistency |
| SkillContextBus | `skill_context_bus.py` | Cross-skill context |
| CheckpointManager | `checkpoint_manager.py` | Enhanced checkpoints |
| TimeAwareRAG | `time_aware_rag.py` | Temporal RAG retrieval |

## NovelForge v4.0 Key Features

### 1. Anti-Token-Blackhole: Prompt Aggregation

**Problem**: L1→L2→L3→L4 each calls API (8-12 calls/chapter)
**Solution**: Merge L2+L3 into single prompt assembly

```python
# core/prompt_assembler.py
class PromptAssembler:
    def assemble_emotion_writer_prompt(self, chapter, world_state, emotional_debt):
        # 1. ElasticArchitect: Near clear, far fuzzy
        components.append(self._get_elastic_outline(chapter))

        # 2. RhythmDesigner: Emotion debt reminder
        components.append(f"[情绪债务]: {emotional_debt}")

        # 3. EmotionalContinuityGuardian
        components.append(self._get_emotional_continuity_check())

        # 4. StyleSkill: Auto-matching
        components.append(self._get_style_signature())

        return master_prompt  # Single API call
```

### 2. Anti-LLM-Math-Disaster: Python Arithmetic

**Problem**: LLM not good at precise calculation
**Solution**: All calculations in Python, LLM receives text only

```python
# core/emotion_tracker.py
class EmotionalDebtLedger:
    def calculate_emotion_from_text(self, text, chapter_num):
        # Python exact calculation
        payoff_value = sum(weight for kw, weight in self.PAYOFF_KEYWORDS if kw in text)
        pressure_value = sum(weight for kw, weight in self.PRESSURE_KEYWORDS if kw in text)

        # LLM only receives text
        return self.to_prompt_text()  # e.g., "情绪债务极高(80)！必须爽点爆发！"
```

### 3. Anti-Infinite-Loop: Circuit Breaker

**Problem**: Unlimited rollback causes Chapter 1 rewritten 100 times
**Solution**: Global circuit breaker, force SUSPEND after threshold

```python
# agents/creative_director.py
class CreativeDirector:
    CIRCUIT_BREAKER_THRESHOLDS = {
        (1, 3): 3,    # Chapters 1-3: max 3 rollbacks
        (4, 10): 5,   # Chapters 4-10: max 5 rollbacks
        (11, 100): 8, # Chapters 11+: max 8 rollbacks
    }

    def arbitrate(self, chapter, draft, reports):
        if self._check_circuit_breaker(chapter):
            self.create_suspended_state(chapter)
            return Decision.SUSPEND
```

### 4. Event Traceability: World Bible

```python
# core/world_bible.py
class WorldBible:
    def record_event(self, event):
        # Records key events: death, rebirth, realm upgrade, etc.
        # Supports event reversal (resurrection)

    def check_consistency_violations(self, new_text, chapter):
        # Detects: resurrection inconsistencies, power level changes
```

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

## Data Structures (v4.0)

### Emotional Vector
```python
EmotionalVector = {
    "base_tone": str,        # "极度压抑", "谨慎", "狂喜"
    "tension": float,        # 0-100
    "decay_rate": float,     # Chapter decay rate
    "triggers": List[str]    # Triggers
}
```

### Event Record
```python
Event = {
    "event_id": str,
    "chapter": int,
    "event_type": str,       # "REALM_UPGRADE", "EMOTION_SHIFT"
    "entity_id": str,
    "emotional_impact": float  # Positive=payoff, Negative=pressure
}
```

### Arbitration Result
```python
ArbitrationResult = {
    "decision": "PASS" | "REWRITE" | "ROLLBACK" | "SUSPEND",
    "target_chapter": int,
    "actionable_feedback": str,
    "emotion_gap": float
}
```

## Circuit Breaker Threshold

| Chapter Range | Max Rollbacks | Action |
|---------------|---------------|--------|
| 1-3 | 3 | Force SUSPEND |
| 4-10 | 5 | Force SUSPEND |
| 11+ | 8 | Force SUSPEND |

## Files Generated

| File | Description |
|------|-------------|
| `emotion_ledger.json` | Emotion debt tracking |
| `world_bible.json` | Event traceability |
| `.suspended.json` | Circuit breaker triggered |
| `.checkpoint.json` | Writing progress |
| `rollback_log.json` | Rollback history |

## Environment

Configure `.env` with API keys:
```bash
ANTHROPIC_API_KEY=      # Claude API
OPENAI_API_KEY=         # GPT-4o API
MOONSHOT_API_KEY=       # Kimi API
DEEPSEEK_API_KEY=       # DeepSeek API
DEFAULT_MODEL_ID=       # Default model
```

## CLI Commands

```bash
# Interactive mode
python main.py --interactive

# New project with batch (recommended for long novels)
python main.py --title "My Novel" --genre "Fantasy" --chapters 1000 --batch-size 20

# Resume from checkpoint
python main.py --project novels/my_novel --batch-size 20

# With config file
python main.py --config config.json

# Producer Dashboard
python -m ui.producer_dashboard novels/my_project
```

## Development Guide

### Using NovelForge v4.0

```python
from core.orchestrator import create_orchestrator

config = {
    "project_dir": "novels/my_project",
    "target_chapters": 50,
    "checkpoint_interval": 5
}

orchestrator = create_orchestrator(config)
orchestrator.run()
```

### Adding New Skills
1. Create new folder under `.opencode/skills/`
2. Add `SKILL.md` file (follow skill metadata format)
3. Register in `core/agent_manager.py`

### Adding New Agents
1. Create new file under `agents/`
2. Implement standard agent interface
3. Integrate in `core/novel_generator.py` or `core/orchestrator.py`

### QualityGate Integration
1. Import `QualityGate` and `QualityViolationException` from `core.quality_gate`
2. Initialize in NovelGenerator: `self.quality_gate = QualityGate(project_dir, llm_client)`
3. Call validation: `self.quality_gate.validate_or_raise(chapter_number, content)`
4. Handle exceptions for rewrite/suspension

## Testing

```bash
# Run circuit breaker tests
python test_circuit_breaker.py
```

## License

MIT License
