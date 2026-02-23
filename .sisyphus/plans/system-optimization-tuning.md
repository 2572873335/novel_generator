# 系统优化与打磨计划

## 诊断总结

基于起点金牌编辑(8年经验) + 系统架构师的双重诊断，当前系统状态：

| 维度 | 评分 | 问题 |
|------|------|------|
| **架构设计** | A | 分层合理，RAG架构完整 |
| **代码实现** | B+ | 功能全，测试弱 |
| **网文专业度** | B | 规则到位，灵魂不足 |
| **工程成熟度** | B | 可用，但需真实验证 |

### 识别的问题

1. **P0 - Skill Prompt同质化**: 17个skill是否真正差异化？
2. **P0 - jieba依赖缺失**: 运行时错误风险
3. **P1 - Reader Expectation缺失**: 只追踪伏笔，不追踪读者情感预期
4. **P1 - 测试覆盖不足**: 需要>80%覆盖率
5. **P2 - 端到端验证缺失**: 需要真实项目验证

---

## 优化目标

将系统从 **B+ 提升到 A-**，关键指标：
- Skill Prompt差异化审计完成
- jieba依赖修复或fallback
- Reader Expectation模块上线
- 测试覆盖率 >80%
- 至少1个真实项目端到端验证

---

## 执行计划

### Wave 1: 紧急修复 (P0)

#### Task 1: Skill Prompt差异化审计
**目标**: 审计17个skill的prompt，确保真正差异化

**当前问题**:
- scene-writer vs chapter-architect 的prompt差异不明确
- senior-editor vs editor 的prompt几乎相同
- 没有统一的"人格"定义

**执行步骤**:
1. 创建skill_prompt_audit.md
2. 逐个审查17个skill的SKILL.md
3. 提取每个skill的核心差异点
4. 识别同质化skill并重构
5. 添加"人格定义"到每个skill

**验收标准**:
- [ ] 17个skill的差异化矩阵完成
- [ ] 每个skill有明确的"人格定义"
- [ ] 重构后的skill通过集成测试

**参考资料**:
- `.opencode/skills/*/SKILL.md` - 所有skill定义

---

#### Task 2: jieba依赖修复
**目标**: 修复local_vector_store的jieba依赖

**当前问题**:
```
core/local_vector_store.py:16: import jieba
core/local_vector_store.py:135: tokens = list(jieba.cut(text))
```

**执行步骤**:
1. 添加jieba为可选依赖
2. 实现字符n-gram fallback
3. 测试两种分词模式
4. 添加配置选项选择分词模式

**验收标准**:
- [ ] jieba可选，无jieba时使用n-gram fallback
- [ ] 向量搜索功能正常
- [ ] 性能测试: 1000章节检索 <2秒

**参考资料**:
- `core/local_vector_store.py` - 当前实现

---

### Wave 2: 核心增强 (P1)

#### Task 3: Reader Expectation模块开发
**目标**: 追踪读者情感预期，而非只是伏笔

**当前问题**:
- ExpectationTracker只追踪"挖坑"
- 缺失"读者预期管理"

**网文核心**:
```
期待感 = "主角会怎么解决这个危机？"
悬念 = "但主角不知道..."
```

**执行步骤**:
1. 创建core/reader_expectation.py
2. 实现:
   - `setup_expectation()` - 章节结尾设置预期
   - `track_emotion()` - 追踪读者情绪曲线
   - `verify_fulfillment()` - 验证预期是否满足
   - `get_urgent_hooks()` - 获取需要立即兑现的钩子
3. 与expectation_tracker集成
4. 添加情感曲线模板

**验收标准**:
- [ ] ReaderExpectation类实现完成
- [ ] 能追踪"读者问题"和"回答deadline"
- [ ] 与现有ExpectationTracker集成
- [ ] 单元测试通过

**参考资料**:
- `core/expectation_tracker.py` - 现有实现
- `.opencode/skills/rhythm-designer/SKILL.md` - 节奏设计

---

#### Task 4: 测试覆盖补全
**目标**: 测试覆盖率从当前<50%提升到>80%

**当前问题**:
- Wave3 integration tests 6个中2个失败
- 大量核心模块无测试

**执行步骤**:
1. 统计当前测试覆盖率
2. 识别缺失测试的关键模块:
   - core/hybrid_checker.py
   - core/entity_graph.py
   - core/time_aware_rag.py
   - core/scene_splitter.py
3. 编写pytest测试
4. 修复现有失败的测试

**验收标准**:
- [ ] 测试覆盖率 >80%
- [ ] 所有integration tests通过
- [ ] CI/CD测试通过

**测试命令**:
```bash
pytest --cov=. --cov-report=term-missing
```

---

### Wave 3: 验证与打磨 (P2)

#### Task 5: 端到端项目验证
**目标**: 用真实项目验证系统可用性

**执行步骤**:
1. 创建一个完整的测试项目:
   - 世界观设定
   - 3+角色设定
   - 完整大纲
   - 至少10章正文
2. 运行完整流程:
   - 市场分析
   - 角色追踪
   - 一致性检查
   - 开篇测试
3. 记录问题并修复

**验收标准**:
- [ ] 完整项目创建成功
- [ ] 10章生成无一致性报错
- [ ] 所有模块正常工作

---

#### Task 6: Prompt工程优化
**目标**: 基于审计结果重构关键skill prompt

**执行步骤**:
1. 基于Task 1的审计结果
2. 重构以下skill:
   - scene-writer: 强调"画面感"和"情绪"
   - rhythm-designer: 从"数字统计"改为"情绪曲线"
   - senior-editor: 强调"网文节奏感"
3. 测试重构效果

**验收标准**:
- [ ] 重构的skill通过实际写作测试
- [ ] 生成的文本更有"网文感"

---

## 时间估算

| Task | 预计工时 | 优先级 |
|------|---------|--------|
| Task 1: Skill Prompt审计 | 4h | P0 |
| Task 2: jieba依赖修复 | 2h | P0 |
| Task 3: Reader Expectation | 8h | P1 |
| Task 4: 测试补全 | 12h | P1 |
| Task 5: 端到端验证 | 8h | P2 |
| Task 6: Prompt优化 | 6h | P2 |
| **总计** | **40h** | |

---

## 依赖关系

```
Task 1 (独立) ─────────┐
                       ├──> Task 6
Task 2 (独立) ─────────┤
                       │
Task 3 (依赖Task 1) ───┼──> Task 5 (依赖Task 2,3,4)
Task 4 (独立) ─────────┘
```

---

## 验收标准总览

- [ ] **P0**: Skill Prompt差异化审计完成
- [ ] **P0**: jieba依赖修复，fallback正常
- [ ] **P1**: Reader Expectation模块上线
- [ ] **P1**: 测试覆盖率 >80%
- [ ] **P2**: 真实项目端到端验证通过
- [ ] **P2**: Prompt优化完成

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Skill审计发现大量同质化 | 需大量重构 | 分批重构，优先核心skill |
| 测试补全工作量巨大 | 40h+ | 聚焦关键模块，其他保持现状 |
| 端到端验证失败 | 影响上线 | 预留buffer时间修复 |

---

## 下一步行动

1. **立即开始**: Task 1 - Skill Prompt差异化审计
2. **本周完成**: Task 2 - jieba依赖修复
3. **下周完成**: Task 3 - Reader Expectation
4. **两周内**: Task 4 - 测试补全
5. **月底前**: Task 5, 6 - 验证与优化
