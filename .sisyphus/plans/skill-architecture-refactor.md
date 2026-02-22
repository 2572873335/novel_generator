# Skills & Agents 架构重构计划

## 执行摘要

**目标**：解决双源维护、触发词冲突、层级扁平化问题，新增开篇诊断和节奏设计功能。

**预计工作量**：8个Phase，约2-3小时执行时间

**风险等级**：中等（需要确保AgentManager正确迁移到单源）

---

## Phase 1: 删除重复源（ agents/*.md ）

**状态**: ⏳ 待执行
**预计时间**: 10分钟
**风险**: 低

### 操作步骤

1. 删除以下文件（保留Python代码文件）:
   - [ ] agents/ChapterArchitect.md
   - [ ] agents/CharacterDesigner.md
   - [ ] agents/Coordinator.md
   - [ ] agents/CultivationDesigner.md
   - [ ] agents/CurrencyExpert.md
   - [ ] agents/Editor.md
   - [ ] agents/GeopoliticsExpert.md
   - [ ] agents/OutlineArchitect.md
   - [ ] agents/PlotArchitect.md
   - [ ] agents/SceneWriter.md
   - [ ] agents/SocietyExpert.md
   - [ ] agents/VolumeArchitect.md
   - [ ] agents/WorldBuilder.md

2. 保留文件:
   - [ ] agents/__init__.py
   - [ ] agents/initializer_agent.py
   - [ ] agents/writer_agent.py
   - [ ] agents/reviewer_agent.py
   - [ ] agents/consistency_checker.py
   - [ ] agents/senior_editor_agent.py

3. 验证命令:
   ```bash
   ls agents/*.md  # 应该为空
   ```

---

## Phase 2: 标准化 SKILL.md 格式

**状态**: ⏳ 待执行
**预计时间**: 30分钟
**风险**: 中（格式必须统一）

### 标准YAML Frontmatter模板

```yaml
---
name: skill-name
version: "1.0"
description: 简短描述
license: MIT
compatibility: opencode
metadata:
  category: novel-writing|novel-review|worldbuilding
  subcategory: plot|writing|editing|character|world
  language: zh-cn
  level: coordinator|architect|expert|auditor
  triggers:
    - 唯一触发词1
    - 唯一触发词2
  parent: parent-skill-name  # 仅子技能填写
  subordinates:  # 仅coordinator填写
    - sub-skill-1
    - sub-skill-2
inputs:
  - name: param1
    type: string|number|object|array
    required: true|false
    description: 参数说明
outputs:
  - path: output/path/file.md
    format: markdown|yaml|json
    description: 输出说明
---
```

### 需要修改的Skill清单

| Skill | 当前格式问题 | 操作 |
|-------|-------------|------|
| worldbuilder-coordinator | 缺level/triggers | 修改 |
| plot-architect-coordinator | 缺level/triggers | 修改 |
| chapter-architect | 有metadata但缺level | 修改 |
| volume-architect | 有metadata但缺level | 修改 |
| outline-architect | 有metadata但缺level | 修改 |
| character-designer | 有metadata但缺level | 修改 |
| scene-writer | 有metadata但缺level | 修改 |
| editor | 有metadata但缺level | 修改 |
| senior-editor | 有metadata但缺level | 修改 |
| cultivation-designer | 有metadata但缺level | 修改 |
| currency-expert | 有metadata但缺level | 修改 |
| geopolitics-expert | 有metadata但缺level | 修改 |
| society-expert | 有metadata但缺level | 修改 |
| novel-coordinator | 有metadata但缺level | 修改 |

---

## Phase 3: 修复触发词冲突

**状态**: ⏳ 待执行
**预计时间**: 20分钟
**风险**: 中（需要唯一性）

### 冲突解决方案

| Skill | 旧触发词 | 新触发词（强制唯一） | 状态 |
|-------|---------|---------------------|------|
| plot-architect-coordinator | 剧情、结构 | **剧情总控**, plot-coord | ⏳ |
| outline-architect | 大纲、主线 | **故事大纲**, outline-design | ⏳ |
| volume-architect | 分卷、卷纲 | **卷纲**, volume-structure | ⏳ |
| chapter-architect | 章纲、节奏 | **章纲**, scene-breakdown | ⏳ |
| scene-writer | 写作、节奏 | **正文**, scene-writing | ⏳ |
| editor | 编辑、润色 | **润色**, line-editing | ⏳ |
| senior-editor | 审稿、编辑 | **审稿**, senior-review | ⏳ |
| novel-coordinator | 协调、管理 | **项目协调**, project-manage | ⏳ |
| character-designer | 人物、角色 | **人物设计**, character-design | ⏳ |
| worldbuilder-coordinator | 世界观 | **世界观总控**, world-coord | ⏳ |
| cultivation-designer | 修炼 | **修炼体系**, cultivation-sys | ⏳ |
| currency-expert | 货币、经济 | **货币体系**, currency-sys | ⏳ |
| geopolitics-expert | 势力、政治 | **地缘政治**, geopolitics | ⏳ |
| society-expert | 社会、文化 | **社会结构**, society-structure | ⏳ |

---

## Phase 4: 建立层级架构

**状态**: ⏳ 待执行
**预计时间**: 15分钟
**风险**: 低

### 三级架构定义

```
Level 1: Coordinator (协调员)
├── worldbuilder-coordinator
│   └── subordinates: [currency-expert, geopolitics-expert, society-expert, cultivation-designer]
├── plot-architect-coordinator
│   └── subordinates: [outline-architect, volume-architect, chapter-architect]
└── novel-coordinator
    └── subordinates: [所有其他skills]

Level 2: Architect (架构师)
├── outline-architect
├── volume-architect
├── chapter-architect
└── character-designer

Level 3: Expert (专家)
├── cultivation-designer
├── currency-expert
├── geopolitics-expert
├── society-expert
└── scene-writer

Level 4: Auditor (审计)
├── opening-diagnostician (新增)
├── senior-editor
└── editor
```

### metadata配置示例

```yaml
# worldbuilder-coordinator
metadata:
  level: coordinator
  triggers: [世界观总控, world-coord]
  subordinates:
    - currency-expert
    - geopolitics-expert
    - society-expert
    - cultivation-designer

# cultivation-designer
metadata:
  level: expert
  triggers: [修炼体系, cultivation-sys]
  parent: worldbuilder-coordinator
```

---

## Phase 5: 创建 opening-diagnostician Skill

**状态**: ⏳ 待执行
**预计时间**: 20分钟
**风险**: 中（新增功能）

### 文件路径
`.opencode/skills/opening-diagnostician/SKILL.md`

### 内容要点
- **level**: auditor
- **triggers**: [开篇诊断, gold-chapter, opening-check]
- **输入**: chapter_1_content, chapter_2_content, chapter_3_content
- **输出**: reports/opening_audit.md

### 检测清单
- [ ] 3秒定律：前500字出现主角名
- [ ] 钩子密度：每300字一个悬念点
- [ ] 毒点扫描：无绿帽/圣母/虐主过度
- [ ] 金手指亮相：第1章必须展示核心金手指
- [ ] 冲突爆发：3000字内首场核心冲突
- [ ] 信息密度：禁止大段世界观说明文

### 评级标准
- S级：符合所有标准
- A级：minor issues
- F级：fatal flaws（必须重写）

---

## Phase 6: 创建 rhythm-designer Skill

**状态**: ⏳ 待执行
**预计时间**: 20分钟
**风险**: 中（新增功能）

### 文件路径
`.opencode/skills/rhythm-designer/SKILL.md`

### 内容要点
- **level**: architect
- **triggers**: [节奏设计, pacing-chart, rhythm-design]
- **输入**: chapter_outline, target_word_count, genre
- **输出**: plot/rhythm/chapter_XXX_rhythm.yaml

### 强制规则
1. 每3000字必须1个小爽点
2. 压抑:释放 = 7:3
3. 章末最后200字必须是cliffhanger
4. 禁止连续2章无爽点
5. 情绪曲线必须波浪形

### 爽点类型矩阵
| 类型 | 触发时机 | 情绪值 |
|------|----------|--------|
| 装逼 | 压抑后 | +30 |
| 打脸 | 被辱后 | +40 |
| 收获 | 探索后 | +20 |
| 突破 | 积累后 | +35 |
| 震惊 | 揭秘时 | +25 |

---

## Phase 7: 更新 AgentManager

**状态**: ⏳ 待执行
**预计时间**: 30分钟
**风险**: 高（核心代码修改）

### 修改要点

1. **移除agents/*.md加载逻辑**
   - [ ] 修改 `get_available_agents()` 仅读取 `.opencode/skills/`
   - [ ] 修改 `load_agent_prompt()` 重定向到 `load_skill_prompt()`
   - [ ] 添加弃用警告

2. **添加层级解析功能**
   - [ ] 新增 `_parse_skill_hierarchy()` 方法
   - [ ] 新增 `_validate_triggers()` 冲突检测
   - [ ] 新增 `get_skill_by_trigger()` 触发词查找

3. **集成开篇诊断到流程**
   - [ ] 在 `run_full_workflow()` 中，写作前3章时自动调用 opening-diagnostician
   - [ ] 如果评级为F，拒绝生成并提示修改

4. **集成节奏设计到流程**
   - [ ] chapter-architect 完成后自动调用 rhythm-designer
   - [ ] scene-writer 必须按照节奏地图写作

### 关键代码修改

```python
def _validate_triggers(self):
    """触发词冲突检测"""
    all_triggers = {}
    for skill_name, skill in self.skills.items():
        for trigger in skill.metadata.triggers:
            if trigger in all_triggers:
                raise ValueError(
                    f"触发词冲突: '{trigger}' 被 {skill_name} 和 {all_triggers[trigger]} 同时占用"
                )
            all_triggers[trigger] = skill_name

def run_full_workflow(self):
    """新的层级化流程"""
    # 先执行coordinators
    coordinators = [s for s in self.skills if s.metadata.level == "coordinator"]
    for coord in coordinators:
        result = self.execute_agent(coord.name)
        # 调度下属experts
        for sub in coord.metadata.get("subordinates", []):
            self.execute_agent(sub, parent_context=result)
    
    # 前3章强制诊断
    if chapter_number <= 3:
        audit = self.execute_agent("opening-diagnostician", content)
        if audit.get("rating") == "F":
            raise FatalOpeningError("开篇不合格，拒绝生成")
```

---

## Phase 8: 测试与验证

**状态**: ⏳ 待执行
**预计时间**: 20分钟
**风险**: 低

### 验证清单

- [ ] `ls agents/*.md` 为空
- [ ] 所有SKILL.md都有metadata.level
- [ ] 所有triggers都是唯一的
- [ ] AgentManager能正确加载所有skills
- [ ] 触发词冲突检测正常运行
- [ ] opening-diagnostician skill可用
- [ ] rhythm-designer skill可用
- [ ] 完整流程测试通过

### 测试命令

```bash
# 1. 检查agents目录
ls agents/*.md
# Expected: No such file or directory

# 2. 检查skills格式
python -c "
import yaml
from pathlib import Path
skills_dir = Path('.opencode/skills')
for skill_dir in skills_dir.iterdir():
    if skill_dir.is_dir():
        skill_file = skill_dir / 'SKILL.md'
        if skill_file.exists():
            content = skill_file.read_text()
            # 解析YAML frontmatter
            if content.startswith('---'):
                yaml_content = content[3:content.find('---', 3)]
                data = yaml.safe_load(yaml_content)
                print(f'{skill_dir.name}: level={data.get(\"metadata\", {}).get(\"level\", \"MISSING\")}')
"

# 3. 触发词冲突检测
python -c "
from core.agent_manager import AgentManager
manager = AgentManager(None, '.')
manager._validate_triggers()
print('✓ No trigger conflicts')
"

# 4. 完整流程测试
python main.py --config test_config.json
```

---

## 批次执行详情（方案B - 保守式）

### ✅ 批次1完成：Phase 1（已提交 `12ff0ad`）
- 删除13个agents/*.md文件
- 验证AgentManager从.opencode/skills/加载
- 系统运行正常

---

### 批次2：Phase 2-4（准备执行）

#### 步骤2.1：更新Coordinator级别Skills

**文件1**: `.opencode/skills/worldbuilder-coordinator/SKILL.md`
```yaml
---
name: worldbuilder-coordinator
version: "1.0"
description: 统筹小说世界观构建全流程，根据小说类型调度各专业子专家
license: MIT
compatibility: opencode
metadata:
  category: novel-writing
  subcategory: worldbuilding
  language: zh-cn
  level: coordinator
  triggers:
    - 世界观总控
    - world-coord
    - worldbuilding
  subordinates:
    - currency-expert
    - geopolitics-expert
    - society-expert
    - cultivation-designer
---
```

**文件2**: `.opencode/skills/plot-architect-coordinator/SKILL.md`
```yaml
---
name: plot-architect-coordinator
version: "1.0"
description: 统筹剧情架构全流程，协调大纲/卷纲/章纲三层架构师
license: MIT
compatibility: opencode
metadata:
  category: novel-writing
  subcategory: plot
  language: zh-cn
  level: coordinator
  triggers:
    - 剧情总控
    - plot-coord
    - story-structure
  subordinates:
    - outline-architect
    - volume-architect
    - chapter-architect
---
```

**文件3**: `.opencode/skills/novel-coordinator/SKILL.md`
```yaml
---
name: novel-coordinator
version: "1.0"
description: 统筹小说创作全流程，管理项目进度和智能体调度
license: MIT
compatibility: opencode
metadata:
  category: novel-writing
  subcategory: coordination
  language: zh-cn
  level: coordinator
  triggers:
    - 项目协调
    - project-manage
    - workflow
---
```

#### 步骤2.2：更新Architect级别Skills

**文件4**: `.opencode/skills/outline-architect/SKILL.md`
- level: architect
- triggers: [故事大纲, outline-design, plot-skeleton]

**文件5**: `.opencode/skills/volume-architect/SKILL.md`
- level: architect
- triggers: [卷纲, volume-structure, book-division]

**文件6**: `.opencode/skills/chapter-architect/SKILL.md`
- level: architect
- triggers: [章纲, scene-breakdown, chapter-outline]

**文件7**: `.opencode/skills/character-designer/SKILL.md`
- level: architect
- triggers: [人物设计, character-design, cast-design]

**文件8**: `.opencode/skills/rhythm-designer/SKILL.md` (新增)
- level: architect
- triggers: [节奏设计, pacing-chart, rhythm-design]

#### 步骤2.3：更新Expert级别Skills

**文件9**: `.opencode/skills/scene-writer/SKILL.md`
- level: expert
- triggers: [正文, scene-writing, draft-chapter]

**文件10**: `.opencode/skills/cultivation-designer/SKILL.md`
- level: expert
- parent: worldbuilder-coordinator
- triggers: [修炼体系, cultivation-sys, power-system]

**文件11**: `.opencode/skills/currency-expert/SKILL.md`
- level: expert
- parent: worldbuilder-coordinator
- triggers: [货币体系, currency-sys, economy-design]

**文件12**: `.opencode/skills/geopolitics-expert/SKILL.md`
- level: expert
- parent: worldbuilder-coordinator
- triggers: [地缘政治, geopolitics, faction-design]

**文件13**: `.opencode/skills/society-expert/SKILL.md`
- level: expert
- parent: worldbuilder-coordinator
- triggers: [社会结构, society-structure, culture-design]

#### 步骤2.4：更新Auditor级别Skills

**文件14**: `.opencode/skills/editor/SKILL.md`
- level: auditor
- triggers: [润色, line-editing, polish-text]

**文件15**: `.opencode/skills/senior-editor/SKILL.md`
- level: auditor
- triggers: [审稿, senior-review, sharp-eval]

**文件16**: `.opencode/skills/opening-diagnostician/SKILL.md` (新增)
- level: auditor
- triggers: [开篇诊断, gold-chapter, opening-check]

---

## 执行顺序建议

### 方案A：激进式（一次性完成）
适合：有完整测试环境，可以rollback
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8

### 方案B：保守式（分批次）✅ 当前方案
适合：生产环境，需要逐步验证
1. ✅ **批次1**: Phase 1 + Phase 8（验证删除agents后系统正常）- 已完成
2. ⏳ **批次2**: Phase 2 + Phase 3 + Phase 4 + Phase 8（验证格式统一）- 准备中
3. ⏳ **批次3**: Phase 5 + Phase 6 + Phase 8（验证新增skill）- 待执行
4. ⏳ **批次4**: Phase 7 + Phase 8（验证AgentManager更新）- 待执行

### 方案C：迭代式（推荐）
1. **Sprint 1**: Phase 1（清理重复源）
2. **Sprint 2**: Phase 2-4（标准化格式和层级）
3. **Sprint 3**: Phase 5-6（新增功能）
4. **Sprint 4**: Phase 7-8（集成与测试）

---

## 风险缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| AgentManager迁移后无法加载skills | 中 | 高 | 保留agents/目录备份，快速回滚 |
| 触发词修改后现有工作流失效 | 低 | 中 | 提供新旧触发词映射表 |
| 新增skill与现有逻辑不兼容 | 中 | 中 | 先独立测试，再集成 |
| YAML格式错误导致解析失败 | 中 | 低 | 使用schema验证工具 |

---

## 成功标准

✅ **Phase 1**: `ls agents/*.md` 返回空
✅ **Phase 2-4**: 所有SKILL.md都有标准YAML frontmatter + level + triggers
✅ **Phase 5-6**: `opening-diagnostician` 和 `rhythm-designer` 可用
✅ **Phase 7**: AgentManager仅从.skills/加载，支持层级调度
✅ **Phase 8**: 完整流程测试通过，触发词无冲突

---

## 编辑寄语

> 这个重构计划解决的是**架构级癌症**（双源维护）和**慢性病**（触发词撞车、层级混乱）。
>
> **立即执行Phase 1**（删除重复源）是**救命手术**，不要犹豫。
>
> **Phase 5-6**（新增开篇诊断和节奏设计）是**给系统装上心脏起搏器**——没有黄金三章检查的小说生成系统，就像没有刹车的跑车。
>
> **不要追求完美，先完成再优化**。这个计划已经足够让你的系统从"能用"变成"好用"。

**请确认执行方案（A/B/C）后开始实施。**
