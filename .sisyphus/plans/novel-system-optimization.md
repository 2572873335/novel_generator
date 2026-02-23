# Novel Writing AI System Optimization Plan

## TL;DR

> **优化目标**: 修复资深编辑诊断的10项关键缺陷，将系统从"规则执行机器"升级为"AI创作协作系统"
>
> **核心架构**: 分层混合RAG (L1卷摘要 + L2章RAG + L3实体图谱 + L4状态快照)
>
> **关键特性**: 
> - 时间感知检索（防止剧透未来）
> - 实体链接（精确追踪设定）
> - 期待感管理（网文生命线）
> - 纯本地实现（无外部向量DB依赖）
>
> **执行波次**: 3 Waves, 17 Tasks, 预计总工时 40-60 hours
>
> **优先级**: Wave 1 (紧急) > Wave 2 (架构) > Wave 3 (增强)

---

## Context

### Original Request
基于起点金牌编辑 + AI系统架构师的双重诊断，对小说生成AI系统进行深度优化。

### Diagnosis Summary
诊断报告识别了10项关键问题：
1. **CRITICAL**: ConsistencyChecker基于正则的"文字狱" - 误报率高
2. **CRITICAL**: WriterAgent的Prompt Engineering灾难 - 全量灌输无RAG
3. **MEDIUM**: SeniorEditorAgent机械化伪编辑 - 缺乏语义理解
4. **CRITICAL**: 缺失ExpectationTracker - 无期待感管理
5. **MEDIUM**: 节奏设计数字化暴政 - 硬性冲突密度
6. **MEDIUM**: 无竞品对标机制
7. **MEDIUM**: 进度文件JSON Hell - 单文件性能瓶颈
8. **CRITICAL**: 设定追踪失忆症 - 无状态快照
9. **MEDIUM**: Prompt堆叠反模式
10. **LOW**: 无风格指纹学习

### User Requirements Confirmed
- **优先级**: 3个CRITICAL问题都重要（Consistency修复、ExpectationTracker、Prompt重构）
- **范围**: B - 通用系统（非特定项目）
- **基础设施**: B - 纯本地实现（无外部向量DB）
- **上下文策略**: **分层混合RAG**（用户详细指定4层架构）
- **宗门检测**: 混合式（Regex+LLM fallback）
- **期待感追踪**: 读者面向 + 故事内部双轨

### Architecture Decisions (User-Specified)
- **RAG核心**: 本地SQLite + 简单向量相似度（无Chroma/Weaviate）
- **四层索引**: L1卷级摘要 + L2章级RAG + L3实体图谱 + L4状态快照
- **时间感知**: 所有检索附加`chapter <= current`约束
- **分块策略**: 按"场景(Scene)"分块，非固定字数

---

## Work Objectives

### Core Objective
重构系统架构，实现200万字超长篇网文的精确设定追踪、动态上下文检索、期待感管理，同时保持纯本地部署。

### Concrete Deliverables
- `core/hybrid_checker.py` - 混合式一致性检查器 (Regex+LLM)
- `core/expectation_tracker.py` - 期待感追踪系统
- `core/entity_graph.py` - 实体图谱管理
- `core/time_aware_rag.py` - 时间感知RAG检索
- `core/chapter_state_store.py` - 章节级状态快照存储
- `core/summary_indexer.py` - 分层摘要索引器
- `agents/writer_agent_v2.py` - Pipeline架构写作Agent
- `agents/senior_editor_v2.py` - 语义化审稿Agent
- `agents/market_analyzer.py` - 市场分析Agent
- Refactored `consistency_checker.py` - 移除纯正则硬编码
- Refactored progress storage - YAML per chapter

### Definition of Done
- [ ] Wave 1所有任务完成并通过QA
- [ ] Wave 2所有任务完成并通过QA
- [ ] Wave 3所有任务完成并通过QA
- [ ] 端到端测试：生成3章测试小说，无一致性报错
- [ ] 性能测试：200章项目检索<2秒

### Must Have
- 混合式ConsistencyChecker（降低误报率80%+）
- ExpectationTracker（追踪未兑现承诺）
- 分层RAG检索（4层索引体系）
- 时间感知过滤（防止未来内容泄露）
- 章节级YAML存储（替代单文件JSON）

### Must NOT Have (Guardrails)
- ❌ 外部向量数据库依赖（Chroma/Weaviate/Pinecone）
- ❌ 实时多Agent协作（避免复杂度爆炸）
- ❌ 自动情节生成（保持大纲驱动）
- ❌ 音频/视频生成（纯文本专注）
- ❌ 超过2次的自编辑循环
- ❌ 未诊断问题的"功能膨胀"

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest available)
- **Automated tests**: Tests-after (架构稳定后补测试)
- **Framework**: pytest
- **Agent-Executed QA**: MANDATORY for all tasks

### QA Policy
Every task includes agent-executed QA scenarios:
- **Code validation**: Python import test, type check
- **Functional test**: Run agent with test data
- **Integration test**: Verify interaction with existing modules
- **Evidence saved to**: `.sisyphus/evidence/task-{N}-{scenario}/`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - Foundation Fixes):
├── Task 1: Hybrid ConsistencyChecker (Regex+LLM)
├── Task 2: Chapter-level YAML Storage
├── Task 3: Soften Rhythm Metrics
├── Task 4: Scene-based Text Splitter
└── Task 5: Local Vector Similarity (SQLite-based)

Wave 2 (After Wave 1 - Core Architecture):
├── Task 6: Entity Graph Data Structure
├── Task 7: Time-Aware RAG Retriever
├── Task 8: Hierarchical Summary Indexer (L1-L2)
├── Task 9: ExpectationTracker Core
├── Task 10: State Snapshot Manager (L4)
├── Task 11: WriterAgent Pipeline Refactor
└── Task 12: SeniorEditor Semantic Upgrade

Wave 3 (After Wave 2 - Advanced Features):
├── Task 13: MarketAnalyzer (Genre Benchmarking)
├── Task 14: CharacterStateMachine
├── Task 15: Consistency Checker 2.0 (RAG-based)
├── Task 16: A/B Testing Framework
└── Task 17: End-to-End Integration & Validation

Wave FINAL (After ALL tasks):
├── Task F1: Comprehensive Test Suite
├── Task F2: Documentation Update
├── Task F3: Performance Benchmark
└── Task F4: Migration Guide
```

### Dependency Matrix

| Task | Depends On | Blocks | Category |
|------|-----------|--------|----------|
| 1 | - | 15 | deep |
| 2 | - | 6,7,8,10 | deep |
| 3 | - | 11,12 | quick |
| 4 | - | 7,8 | quick |
| 5 | - | 7 | quick |
| 6 | 2 | 9,14 | deep |
| 7 | 2,4,5 | 11,15 | deep |
| 8 | 2,4 | 11 | unspecified-high |
| 9 | 2,6 | 11,14 | deep |
| 10 | 2 | 11 | deep |
| 11 | 1,3,7,8,9,10 | 17 | unspecified-high |
| 12 | 3 | 17 | unspecified-high |
| 13 | - | 17 | unspecified-high |
| 14 | 6,9 | 17 | deep |
| 15 | 1,6,7 | 17 | deep |
| 16 | 11 | 17 | unspecified-high |
| 17 | All 1-16 | F1-F4 | deep |
| F1-F4 | 17 | - | oracle/unspecified-high |

### Critical Path
Task 2 → Task 6 → Task 9 → Task 11 → Task 17 → F1-F4

---

## TODOs

- [ ] 1. Hybrid ConsistencyChecker (Regex+LLM)

  **What to do**:
  - Create `core/hybrid_checker.py` implementing 3-layer detection:
    - Layer 1: Fast regex pre-filtering with whitelist matching
    - Layer 2: LLM semantic validation for suspicious content
    - Layer 3: Similarity matching for faction name variants ("青云剑宗" vs "天剑宗")
  - Refactor `agents/consistency_checker.py` to use HybridChecker as fallback
  - Implement similarity algorithm for faction variant detection (Levenshtein or Jaccard)
  - Add confidence scoring: high (regex exact) / medium (similarity) / low (LLM verify)

  **Must NOT do**:
  - ❌ Remove existing regex entirely (keep for fast path)
  - ❌ Add external vector DB dependency
  - ❌ Increase latency >500ms per chapter check

  **Recommended Agent Profile**:
  - **Category**: `deep` - Complex logic requiring careful algorithm design
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: With Tasks 2,3,4,5
  - **Blocks**: Task 15
  - **Blocked By**: None

  **References**:
  - `agents/consistency_checker.py:193-245` - Current regex faction detection
  - `agents/consistency_checker.py:246-299` - Name variant detection (similar logic)
  - `core/writing_constraint_manager.py` - Constraint loading patterns

  **Acceptance Criteria**:
  - [ ] `from core.hybrid_checker import HybridChecker` imports successfully
  - [ ] Test: "宗教" → NOT flagged as faction (was false positive)
  - [ ] Test: "青云宗" (in whitelist) → flagged correctly
  - [ ] Test: "青云剑宗" (similar to whitelisted "天剑宗") → flagged as variant
  - [ ] Performance: Check 1000-word chapter < 500ms (with LLM caching)

  **QA Scenarios**:
  ```
  Scenario: False positive reduction (happy path)
    Tool: Bash (python)
    Preconditions: HybridChecker initialized with whitelist ["青云宗", "天剑门"]
    Steps:
      1. Run: checker.check("这是一个宗教会议，在联合国大厦举行")
      2. Assert: No factions flagged
    Expected Result: Empty violations list
    Evidence: .sisyphus/evidence/task-1-false-positive.json

  Scenario: Variant detection (edge case)
    Tool: Bash (python)
    Preconditions: Whitelist contains "青云宗"
    Steps:
      1. Run: checker.check("他加入了青云剑宗")
      2. Assert: Flags "青云剑宗" as variant of "青云宗"
    Expected Result: Violation with type="faction_name_variant"
    Evidence: .sisyphus/evidence/task-1-variant-detection.json

  Scenario: Unknown faction (error case)
    Tool: Bash (python)
    Preconditions: Standard whitelist
    Steps:
      1. Run: checker.check("神秘的暗影宗出现了")
      2. Assert: Flags "暗影宗" as undefined_faction
    Expected Result: Violation with severity="warning" (not critical)
    Evidence: .sisyphus/evidence/task-1-unknown-faction.json
  ```

  **Commit**: YES (Wave 1)
  - Message: `feat(core): add HybridChecker with regex+LLM hybrid detection`
  - Files: `core/hybrid_checker.py`, `agents/consistency_checker.py`
  - Pre-commit: `python -c "from core.hybrid_checker import HybridChecker; print('OK')"`

- [ ] 2. Chapter-level YAML Storage

  **What to do**:
  - Create `core/chapter_state_store.py` for atomic chapter-level storage
  - Design YAML schema: status, word_count, quality_score, key_events, entity_changes
  - Implement atomic write operations (write temp → rename for safety)
  - Create migration script from JSON to YAML format
  - Add backward compatibility layer for old projects
  - Implement bulk operations for batch updates

  **Must NOT do**:
  - ❌ Break existing API (keep `novel-progress.txt` as index)
  - ❌ Lose data during migration
  - ❌ Increase storage by >200%

  **Recommended Agent Profile**:
  - **Category**: `deep` - Data layer refactoring, critical for system stability
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: With Tasks 1,3,4,5
  - **Blocks**: Tasks 6,7,8,10
  - **Blocked By**: None

  **References**:
  - `core/progress_manager.py` - Current progress management
  - `agents/initializer_agent.py:136-141` - Progress file initialization
  - Existing `novels/*/novel-progress.txt` - Current format

  **Acceptance Criteria**:
  - [ ] `chapter-001.yaml` created with proper schema
  - [ ] Migration script runs without errors
  - [ ] Read performance: <50ms per chapter
  - [ ] Old projects continue to work (backward compat)

  **QA Scenarios**:
  ```
  Scenario: Atomic write (happy path)
    Tool: Bash (python)
    Preconditions: Project directory exists
    Steps:
      1. Create ChapterStateStore instance
      2. Write chapter 1 data with status="completed"
      3. Read back and verify
    Expected Result: Data matches, file exists at chapters/chapter-001.yaml
    Evidence: .sisyphus/evidence/task-2-atomic-write.yaml

  Scenario: Migration from JSON (migration path)
    Tool: Bash (python)
    Preconditions: Existing novel-progress.txt with 3 chapters
    Steps:
      1. Run migration script
      2. Verify 3 chapter YAML files created
      3. Verify novel-progress.txt updated to index-only
    Expected Result: All data preserved, new format active
    Evidence: .sisyphus/evidence/task-2-migration/

  Scenario: Concurrent read safety (edge case)
    Tool: Bash (python + multiprocessing)
    Preconditions: Chapter file exists
    Steps:
      1. Start 10 parallel readers
      2. All should complete without errors
    Expected Result: No race conditions
    Evidence: .sisyphus/evidence/task-2-concurrent-read.log
  ```

  **Commit**: YES (Wave 1)
  - Message: `feat(core): implement chapter-level YAML storage`
  - Files: `core/chapter_state_store.py`, `scripts/migrate_progress.py`

- [ ] 3. Soften Rhythm Metrics

  **What to do**:
  - Refactor `agents/senior_editor_agent.py` rhythm checking (around line 280)
  - Replace hard conflict density rules with guidelines
  - Add chapter type detection (action/emotional/setup/transition)
  - Implement emotion curve analysis instead of simple conflict counting
  - Add "suppress-release ratio" tracking (7:3) as soft metric

  **Must NOT do**:
  - ❌ Remove rhythm checking entirely
  - ❌ Add more hard rules
  - ❌ Break existing scoring system

  **Recommended Agent Profile**:
  - **Category**: `quick` - Refactoring existing logic, clear scope
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: With Tasks 1,2,4,5
  - **Blocks**: Tasks 11,12
  - **Blocked By**: None

  **References**:
  - `agents/senior_editor_agent.py:280-310` - Current rhythm metrics
  - `.opencode/skills/web-novel-methodology/SKILL.md` - Web novel methodology

  **Acceptance Criteria**:
  - [ ] Emotional chapters don't fail rhythm check
  - [ ] Setup chapters allowed 0 conflicts
  - [ ] Suppress-release ratio tracked

  **QA Scenarios**:
  ```
  Scenario: Emotional chapter pass (happy path)
    Tool: Bash (python)
    Preconditions: Chapter with sadness/grief content, no conflict
    Steps:
      1. Run rhythm analysis
      2. Verify chapter type detected as "emotional"
      3. Verify no penalty for missing conflict
    Expected Result: Score >= 7.0, no rhythm warnings
    Evidence: .sisyphus/evidence/task-3-emotional-chapter.json
  ```

  **Commit**: YES (Wave 1)
  - Message: `refactor(agents): soften rhythm metrics, add chapter type detection`
  - Files: `agents/senior_editor_agent.py`

- [ ] 4. Scene-based Text Splitter

  **What to do**:
  - Create `core/scene_splitter.py` for intelligent text chunking
  - Implement delimiter detection (###, ---, blank lines, scene transitions)
  - Extract metadata per scene: characters, location, time, key items
  - Support Chinese punctuation for scene boundaries
  - Create reusable TextChunk dataclass

  **Must NOT do**:
  - ❌ Use fixed word count chunks (breaks narrative flow)
  - ❌ Lose metadata during splitting
  - ❌ Require manual scene markers

  **Recommended Agent Profile**:
  - **Category**: `quick` - Clear algorithm, well-defined scope
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: With Tasks 1,2,3,5
  - **Blocks**: Tasks 7,8
  - **Blocked By**: None

  **References**:
  - Chapter files in `novels/*/chapters/chapter-*.md` - Current format
  - `.opencode/skills/web-novel-methodology/SKILL.md` - Scene structure

  **Acceptance Criteria**:
  - [ ] Split 3000-word chapter into 2-5 scenes
  - [ ] Extract correct metadata per scene
  - [ ] Handle Chinese punctuation

  **QA Scenarios**:
  ```
  Scenario: Multi-scene chapter split (happy path)
    Tool: Bash (python)
    Preconditions: Chapter with 3 scenes separated by ###
    Steps:
      1. Run scene splitter
      2. Verify 3 chunks returned
      3. Verify metadata extracted for each
    Expected Result: 3 Scene objects with correct boundaries
    Evidence: .sisyphus/evidence/task-4-scene-split.json
  ```

  **Commit**: YES (Wave 1)
  - Message: `feat(core): add scene-based text splitter for RAG`
  - Files: `core/scene_splitter.py`

- [ ] 5. Local Vector Similarity (SQLite-based)

  **What to do**:
  - Create `core/local_vector_store.py` using SQLite + simple embeddings
  - Implement TF-IDF or BM25 for lightweight semantic similarity
  - Support text chunk storage with metadata
  - Implement similarity search with top-k retrieval
  - Add persistence to SQLite database

  **Must NOT do**:
  - ❌ Use Chroma/Weaviate/Pinecone (external dependency)
  - ❌ Require GPU for embeddings
  - ❌ Store full text in memory

  **Recommended Agent Profile**:
  - **Category**: `deep` - Algorithm implementation, performance critical
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 1)
  - **Parallel Group**: With Tasks 1,2,3,4
  - **Blocks**: Task 7
  - **Blocked By**: None

  **References**:
  - `core/chapter_state_store.py` (Task 2) - Storage patterns
  - Standard libraries: `sqlite3`, `math` for similarity

  **Acceptance Criteria**:
  - [ ] Store and retrieve 1000 chunks
  - [ ] Search latency < 100ms
  - [ ] No external dependencies

  **QA Scenarios**:
  ```
  Scenario: Similarity search (happy path)
    Tool: Bash (python)
    Preconditions: 100 chunks stored
    Steps:
      1. Query: "主角获得法宝"
      2. Retrieve top-5 similar chunks
    Expected Result: Relevant chunks returned, latency < 100ms
    Evidence: .sisyphus/evidence/task-5-similarity-search.json
  ```

  **Commit**: YES (Wave 1)
  - Message: `feat(core): implement local vector store with SQLite`
  - Files: `core/local_vector_store.py`

- [ ] 6. Entity Graph Data Structure

  **What to do**:
  - Create `core/entity_graph.py` with Node and Edge dataclasses
  - Implement entity types: Character, Item, Location, Faction, Ability
  - Support temporal edges (valid_from chapter, valid_until chapter)
  - Implement graph traversal queries (get_all_abilities, get_current_items)
  - Add serialization to JSON for persistence

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Parallelization**: Wave 2, Blocks 9,14, Depends on 2

  **Acceptance Criteria**:
  - [ ] Create entity nodes with temporal validity
  - [ ] Query "主角在第50章拥有的法宝"
  - [ ] Graph traversal < 100ms for 1000 nodes

  **QA Scenarios**:
  ```
  Scenario: Temporal entity query
    Tool: Bash (python)
    Preconditions: Entity graph with protagonist abilities
    Steps:
      1. Add "御剑术" at chapter 10
      2. Query at chapter 50
    Expected Result: Returns "御剑术"
    Evidence: .sisyphus/evidence/task-6-entity-graph.json
  ```

  **Commit**: YES (Wave 2)

- [ ] 7. Time-Aware RAG Retriever

  **What to do**:
  - Create `core/time_aware_rag.py` integrating LocalVectorStore + EntityGraph
  - Implement time-constrained retrieval: `filter={"chapter": {"$lte": current}}`
  - Add multi-path retrieval: semantic + entity + recent summary
  - Implement context assembly with token budget management
  - Support "future content masking" to prevent spoilers

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Parallelization**: Wave 2, Blocks 11,15, Depends on 2,4,5

  **Acceptance Criteria**:
  - [ ] Retrieve only content from chapters <= current
  - [ ] Multi-path retrieval (3 sources combined)
  - [ ] Token budget enforcement

  **QA Scenarios**:
  ```
  Scenario: Time-constrained retrieval
    Tool: Bash (python)
    Preconditions: 100 chapters stored
    Steps:
      1. Query at chapter 50
      2. Verify no content from chapter 51+ returned
    Expected Result: All results chapter <= 50
    Evidence: .sisyphus/evidence/task-7-time-aware.json
  ```

  **Commit**: YES (Wave 2)

- [ ] 8. Hierarchical Summary Indexer (L1-L2)

  **What to do**:
  - Create `core/summary_indexer.py` for 2-level summary hierarchy
  - Implement volume-level summary generation (L1)
  - Implement chapter-level summary generation (L2)
  - Support summary update on chapter completion
  - Add summary-based fast retrieval

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Parallelization**: Wave 2, Blocks 11, Depends on 2,4

  **Commit**: YES (Wave 2)

- [ ] 9. ExpectationTracker Core

  **What to do**:
  - Create `core/expectation_tracker.py` for promise/expectation management
  - Track reader-facing promises ("三年之约",伏笔)
  - Track information gaps (reader knows, protagonist doesn't)
  - Track ability growth expectations (金手指升级节奏)
  - Implement promise fulfillment verification
  - Add overdue promise warnings

  **Recommended Agent Profile**:
  - **Category**: `deep` - Critical feature for web novels
  - **Parallelization**: Wave 2, Blocks 11,14, Depends on 2,6

  **Acceptance Criteria**:
  - [ ] Track promise made in Ch3, due in Ch150
  - [ ] Warn when promise overdue
  - [ ] Verify fulfillment matches setup

  **QA Scenarios**:
  ```
  Scenario: Promise tracking
    Tool: Bash (python)
    Preconditions: Promise "三年之约" made at Ch3
    Steps:
      1. Query at Ch100 - should show pending
      2. Query at Ch200 - should warn overdue
    Expected Result: Correct status tracking
    Evidence: .sisyphus/evidence/task-9-promise-track.json
  ```

  **Commit**: YES (Wave 2)

- [ ] 10. State Snapshot Manager (L4)

  **What to do**:
  - Create `core/state_snapshot.py` for complete world state snapshots
  - Capture full state at chapter boundaries
  - Support "state at chapter X" queries
  - Implement diff between snapshots
  - Add rollback capability for alternate timelines

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Parallelization**: Wave 2, Blocks 11, Depends on 2

  **Commit**: YES (Wave 2)

- [ ] 11. WriterAgent Pipeline Refactor

  **What to do**:
  - Create `agents/writer_agent_v2.py` with Pipeline architecture
  - Implement stages: Outline → Draft → ConsistencyCheck → Polish → Final
  - Integrate TimeAwareRAG for context retrieval
  - Add checkpoint-based writing (every 1000 words)
  - Implement graceful degradation on API failure
  - Replace prompt stacking with priority-based injection

  **Must NOT do**:
  - ❌ Modify existing writer_agent.py (create v2)
  - ❌ Remove human-in-the-loop option

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Parallelization**: Wave 2, Blocks 17, Depends on 1,3,7,8,9,10

  **Commit**: YES (Wave 2)

- [ ] 12. SeniorEditor Semantic Upgrade

  **What to do**:
  - Create `agents/senior_editor_v2.py` with LLM-based semantic analysis
  - Replace keyword matching with literary analysis
  - Add narrative perspective detection
  - Implement emotional engagement scoring
  - Add "Golden Three Chapters" semantic evaluation
  - Support chapter type-aware evaluation

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Parallelization**: Wave 2, Blocks 17, Depends on 3

  **Commit**: YES (Wave 2)

- [ ] 13. MarketAnalyzer (Genre Benchmarking)

  **What to do**:
  - Create `agents/market_analyzer.py` for genre pattern analysis
  - Analyze genre templates (Xianxia, Urban, Fantasy)
  - Extract patterns: golden finger timing, conflict types, chapter length
  - Provide differentiation recommendations
  - Support genre-specific rubrics

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Parallelization**: Wave 3, Blocks 17, No dependencies

  **Commit**: YES (Wave 3)

- [ ] 14. CharacterStateMachine

  **What to do**:
  - Create `core/character_state_machine.py` for precise character tracking
  - Track abilities with acquire/lose timestamps
  - Track relationships with dynamic updates
  - Support ability forgetting (injury, curse)
  - Implement "valid abilities at chapter X" queries

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Parallelization**: Wave 3, Blocks 17, Depends on 6,9

  **Commit**: YES (Wave 3)

- [ ] 15. Consistency Checker 2.0 (RAG-based)

  **What to do**:
  - Refactor `agents/consistency_checker.py` to use RAG retrieval
  - Replace regex-first with semantic-first approach
  - Use EntityGraph for fact verification
  - Implement claim extraction + historical fact comparison
  - Add LLM-based conflict resolution

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Parallelization**: Wave 3, Blocks 17, Depends on 1,6,7

  **Commit**: YES (Wave 3)

- [ ] 16. A/B Testing Framework

  **What to do**:
  - Create `core/ab_testing.py` for opening variant testing
  - Generate multiple opening variations
  - Implement simulated reader scoring
  - Support metrics: hook strength, clarity, engagement
  - Add winner selection based on scores

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Parallelization**: Wave 3, Blocks 17, Depends on 11

  **Commit**: YES (Wave 3)

- [ ] 17. End-to-End Integration & Validation

  **What to do**:
  - Integrate all Wave 1-3 components
  - Create unified NovelGeneratorV2 class
  - Implement graceful fallback to V1
  - Add comprehensive error handling
  - Create demo script showcasing all features

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Parallelization**: Wave 3, Blocks F1-F4, Depends on All 1-16

  **Acceptance Criteria**:
  - [ ] 3-chapter test novel generates
  - [ ] All components integrated
  - [ ] No regressions in V1 functionality

  **Commit**: YES (Wave 3)

---

## Final Verification Wave

- [ ] F1. **Comprehensive Test Suite** - `oracle`
  Run full test suite: pytest with coverage. Verify all 17 tasks have passing tests. Check integration scenarios. Validate no regression in existing functionality.
  Output: Test report with coverage %

- [ ] F2. **Documentation Update** - `writing`
  Update AGENTS.md and README.md with new architecture. Document 4-layer RAG system. Provide usage examples for ExpectationTracker.
  Output: Updated docs

- [ ] F3. **Performance Benchmark** - `unspecified-high`
  Benchmark 200-chapter project: retrieval latency, storage size, initialization time. Compare before/after metrics.
  Output: Benchmark report

- [ ] F4. **Migration Guide** - `writing`
  Create migration guide for existing projects using old JSON progress format. Provide migration script.
  Output: MIGRATION.md + migrate.py

---

## Commit Strategy

- **Wave 1**: `feat(core): Wave 1 - foundation fixes (tasks 1-5)`
- **Wave 2**: `feat(core): Wave 2 - RAG architecture (tasks 6-12)`
- **Wave 3**: `feat(agents): Wave 3 - advanced features (tasks 13-17)`
- **Final**: `docs: complete optimization plan implementation`

---

## Success Criteria

### Verification Commands
```bash
# Test new components
python -c "from core.hybrid_checker import HybridChecker; print('OK')"
python -c "from core.expectation_tracker import ExpectationTracker; print('OK')"
python -c "from core.time_aware_rag import TimeAwareRAG; print('OK')"

# Test full pipeline
python main.py --test-mode --chapters 3

# Performance test
time python -c "from core.time_aware_rag import TimeAwareRAG; rag = TimeAwareRAG('test_project'); rag.retrieve(100, '主角的剑')"
# Expected: < 2 seconds
```

### Final Checklist
- [ ] All Wave 1 tasks complete
- [ ] All Wave 2 tasks complete
- [ ] All Wave 3 tasks complete
- [ ] All Wave F tasks complete
- [ ] 3-chapter test novel generates without errors
- [ ] 200-chapter project retrieval < 2 seconds
- [ ] Documentation updated
- [ ] Migration guide provided
