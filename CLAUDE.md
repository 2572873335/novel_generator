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

## Architecture

### Core Components

- **agents/**: Agent implementations
  - `writer_agent_v2.py` - Main writing agent with pipeline architecture
  - `consistency_checker.py` - Strict consistency verification
  - `market_analyzer.py` - Market analysis
  - `rag_consistency_checker.py` - RAG-based consistency checking
  - `senior_editor_v2.py` - Senior editor agent

- **core/**: Core systems
  - `novel_generator.py` - Main orchestration
  - `agent_manager.py` - Agent coordination and skills loading
  - `v7_integrator.py` - Genre-aware system
  - `writing_constraint_manager.py` - Pre-writing constraint injection
  - `consistency_tracker.py` - Real-time state tracking
  - `hybrid_checker.py` - 3-layer consistency checking
  - `skill_context_bus.py` - Skill context bus (solves skill island problem)
  - `checkpoint_manager.py` - Enhanced checkpoint with recovery support

- **config/**: Settings and configuration
- **.opencode/skills/**: 17+ specialized skills in 4-level hierarchy
- **novels/**: Generated novel projects

### 3-Layer Consistency Defense System

The system now implements a robust 3-layer consistency defense:

1. **Pre-writing (事前)**: WritingConstraintManager
   - Injects strict constraints into LLM prompts
   - Locks faction names, character names, realm system
   - Prevents generation of non-compliant content

2. **Real-time (事中)**: _pre_save_validation()
   - Validates chapter before saving
   - Uses WritingConstraintManager.validate_chapter()
   - Triggers rewrite if critical violations found

3. **Post-writing (事后)**: Senior-editor audit
   - Every 5 chapters: calls senior-editor skill
   - Multi-dimensional quality review
   - Detects issues missed by automated checks

### Key Files

- `main.py`: CLI entry point
- `app.py`: Streamlit web UI
- `core/novel_generator.py`: Main orchestration
- `core/agent_manager.py`: Agent coordination
- `core/v7_integrator.py`: Genre-aware system

## Skills System

Located in `.opencode/skills/`, organized in 4 levels:

| Level | Type | Skills |
|-------|------|--------|
| **Level 1** | Coordinator | worldbuilder-coordinator, plot-architect-coordinator, novel-coordinator |
| **Level 2** | Architect | outline-architect, volume-architect, chapter-architect, character-designer, rhythm-designer |
| **Level 3** | Expert | scene-writer, cultivation-designer, currency-expert, geopolitics-expert, society-expert, web-novel-methodology |
| **Level 4** | Auditor | editor, senior-editor, opening-diagnostician |

Plus style skills (style-blood-punch, style-cowboy, etc.) and genre experts.

## Environment

Configure `.env` with API keys:
- `ANTHROPIC_API_KEY` (Claude)
- `OPENAI_API_KEY` (GPT-4o)
- `MOONSHOT_API_KEY` (Kimi)
- `DEEPSEEK_API_KEY`

## Consistency Checker Components

### WritingConstraintManager (`core/writing_constraint_manager.py`)
- Loads constraints from `writing_constraints.json`
- Generates constraint prompts with `get_constraint_prompt()`
- Validates chapters with `validate_chapter()`
- Updates state after each chapter

### ConsistencyTracker (`core/consistency_tracker.py`)
- Tracks realm progression
- Tracks constitution changes
- Tracks location/faction changes
- Monitors timeline consistency

### ConsistencyChecker (`agents/consistency_checker.py`)
- `check_chapter()`: Check single chapter content
- `check_all_chapters()`: Full project consistency check
- 6 major detection categories

### HybridChecker (`core/hybrid_checker.py`)
- `check_chapter()`: Real-time chapter validation
- 3-layer detection: regex → similarity → LLM
- Faction name whitelist enforcement
