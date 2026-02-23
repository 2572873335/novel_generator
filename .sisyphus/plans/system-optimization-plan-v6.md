# 系统优化方案 V6：通用网文生成系统（风格Skills版 - 编辑审订版）

**版本**: 6.0  
**更新日期**: 2026-02-22  
**基于**: 起点编辑反馈 V6审订 + 网文类型研究

---

## 一、核心修订（回应编辑意见）

### 🚨 立即修正

| 问题 | 修正方案 |
|------|----------|
| **风格/类型混淆** | 移除`style-mystery`，归入类型`suspense` |
| **样本污染** | 每种风格准备3个**跨类型**样本 |
| **缺失风格** | 新增`style-dark`（黑暗流）、`style-infinity`（无限流）、`style-building`（种田流） |
| **风格冲突** | 增加**类型-风格兼容性矩阵** |
| **粒度不足** | 增加可量化约束指标 |

### ✅ 编辑肯定

1. **类型与风格解耦** - 正确方向
2. **约束仲裁保留** - 关键机制
3. **原子化设计** - 可复用

---

## 二、风格Skill重构

### 2.1 元风格架构（4种）

```
Layer 1: 元风格（Meta-Style）- 4种
├── 快节奏（Fast-paced）- 热血升级、无限流
├── 慢节奏（Slow-paced）- 种田、苟道、日常
├── 情绪外放（Emotive）- 热血、甜宠、黑暗
└── 情绪内敛（Restrained）- 严肃、克苏鲁、悬疑

Layer 2: 具体风格（Concrete Style）- 7种
```

### 2.2 修正后的7种风格

| 风格 | 元风格 | 样本（跨类型） | 反例 |
|------|--------|---------------|------|
| **style-blood-punch** | 快节奏+情绪外放 | 《斗破苍穹》(玄幻)、《全职法师》(都市)、《超神机械师》(科幻) | 主角连续3章被碾压不反击 |
| **style-cowboy** | 慢节奏+情绪内敛 | 《苟道》(仙侠)、《我只想安静地玩游戏》(游戏)、《黎明之剑》(科幻) | 冲动冒险、不做保险 |
| **style-dark** | 情绪外放+快/慢 | 《蛊真人》(仙侠)、《轮回乐园》(无限)、《熔流》(科幻) | 圣母心、伟光正 |
| **style-infinity** | 快节奏+情绪内敛 | 《轮回乐园》(无限)、《惊悚乐园》(游戏)、《从姑获鸟开始》(武侠) | 单一线性剧情 |
| **style-building** | 慢节奏+情绪内敛 | 《黎明之剑》(科幻)、《放开那个女巫》(西幻)、《异界征服手册》(历史) | 快速跳跃发展 |
| **style-serious** | 情绪内敛 | 《诡秘之主》(西幻)、《三体》(科幻)、《宰执天下》(历史) | 过度玩梗、搞笑 |
| **style-sweet** | 情绪外放 | 《我家老婆来自一千年前》(都市)、《光阴之外》(玄幻日常) | 强行虐恋、刀多于糖 |

> **注**: 悬疑推理 → 归入类型 `suspense`，不再作为独立风格

### 2.3 跨类型样本原则（321原则）

每个风格Skill必须包含：

- **3个不同类型的高质量样本**（防止样本污染）
- **2个反例**（明确什么不是该风格）
- **1套可量化约束指标**

---

## 三、类型-风格兼容性矩阵

### 3.1 兼容性规则

```python
STYLE_COMPATIBILITY = {
    "xianxia": {  # 仙侠
        "allowed": ["blood-punch", "cowboy", "dark", "serious"],
        "forbidden": ["sweet"],
        "conflict_resolution": {
            "cowboy": "修改为'稳健修仙流'，突破靠水磨工夫而非生死战"
        }
    },
    "scifi": {  # 科幻
        "allowed": ["infinity", "dark", "serious", "building"],
        "forbidden": ["blood-punch", "sweet"],
        "conflict_resolution": {}
    },
    "urban": {  # 都市
        "allowed": ["blood-punch", "sweet", "dark", "building"],
        "forbidden": [],
        "conflict_resolution": {}
    },
    "suspense": {  # 悬疑
        "allowed": ["serious", "dark", "infinity"],
        "forbidden": ["blood-punch", "sweet"],
        "conflict_resolution": {}
    },
    "game": {  # 游戏
        "allowed": ["blood-punch", "infinity", "cowboy", "building"],
        "forbidden": [],
        "conflict_resolution": {}
    },
    "historical": {  # 历史
        "allowed": ["serious", "building", "dark"],
        "forbidden": ["sweet"],  # 古代背景少纯甜宠
        "conflict_resolution": {}
    }
}
```

### 3.2 冲突检测逻辑

```python
class StyleConflictDetector:
    def detect_conflict(self, genre: str, style: str) -> Dict:
        """检测类型-风格冲突"""
        allowed = STYLE_COMPATIBILITY.get(genre, {}).get("allowed", [])
        
        if style not in allowed:
            return {
                "conflict": True,
                "resolution": STYLE_COMPATIBILITY[genre].get("conflict_resolution", {}).get(style),
                "suggestion": f"建议使用 {allowed[0] if allowed else '默认风格'}"
            }
        return {"conflict": False}
```

---

## 四、可量化约束指标

### 4.1 风格约束模板

```json
{
  "style": "blood-punch",
  "quantifiable_constraints": {
    "sentence_structure": {
      "short_sentence_ratio": 0.6,
      "paragraph_max_sentences": 4,
      "dialogue_density": 0.3
    },
    "pacing": {
      "action_scene_frequency": "每章至少1场战斗或冲突",
      "power_display_interval": "每3章必须有一次能力展示/升级",
      "chapter_hook_type": "cliffhanger"
    },
    "emotion": {
      "progression": "压抑→愤怒→爆发→胜利",
      "internal_monologue_required": true,
      "标志性口头禅": ["该死", "给我破", "不可能"]
    }
  },
  "forbidden_patterns": [
    "主角连续3章被碾压不反击",
    "敌人智商全程压制",
    "断更式断章（悬念过度）"
  ]
}
```

### 4.2 各风格约束指标

| 风格 | 短句比 | 冲突频率 | 心理活动 | 章节钩子类型 |
|------|--------|----------|----------|--------------|
| blood-punch | 60% | 每章1场 | 必须 | cliffhanger |
| cowboy | 30% | 每3章1场 | 建议 | mystery |
| dark | 50% | 每2章1场 | 深度 | twist |
| infinity | 70% | 每副本1场 | 可选 | transition |
| building | 20% | 每5章1场 | 丰富 | milestone |
| serious | 40% | 每2章1场 | 深度 | philosophical |
| sweet | 30% | 每4章1场 | 必须 | emotional |

---

## 五、约束仲裁优先级（修订版）

### 5.1 优先级定义

```python
CONSTRAINT_PRIORITY = {
    # ===== 最高：叙事基础（不可违背）=====
    "temporal_continuity": 100,      # 时间连续性
    "character_identity": 95,         # 角色身份
    "genre_worldview": 90,           # 类型世界观（仙侠/科幻等）
    
    # ===== 高：类型核心规则 =====
    "power_system": 80,              # 战力体系
    "realm_boundaries": 75,          # 空间边界
    
    # ===== 中：情节节奏 =====
    "style_pacing": 65,              # 风格节奏
    "plot_escalation": 60,           # 情节升级
    "motivation_tracking": 55,       # 动机追踪
    
    # ===== 低：资源与压力 =====
    "resource_pressure": 40,         # 资源消耗
    "entity_threat": 35,            # 实体威胁
    
    # ===== 最低：风格偏好 =====
    "style_tone": 25,                # 风格调性
    "style_vocabulary": 20,          # 风格词汇
}
```

### 5.2 冲突解决原则

1. **类型世界观 > 风格调性** - 不能让风格违反类型基本规则
2. **硬性约束不可违背** - priority >= 80 的约束不可覆盖
3. **软性约束可协商** - priority < 60 的约束可被情节需要临时放宽
4. **高潮章节特权** - 高潮/转折章节可临时放宽资源限制

---

## 六、实施计划 V6

### Phase 0: 基线测试 (P0 - 2h)

| 任务 | 验收 |
|------|------|
| 生成前3章对照 | 记录现有问题 |

---

### Phase 1: MVP核心逻辑 (P0 - 10h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 1.1 创建GenreDetector | 2h | 类型识别>90% |
| 1.2 创建ConstraintTemplateManager | 2h | 3种模板加载 |
| 1.3 重构WritingConstraintManager | 2h | 约束生效 |
| 1.4 创建ConstraintArbiter + 冲突检测 | 2h | 冲突解决 |
| 1.5 MVP验证 | 2h | 模板切换对比 |

---

### Phase 2: 风格Skill系统 (P1 - 14h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 2.1 创建style-blood-punch | 2h | 3跨类型样本+量化约束 |
| 2.2 创建style-cowboy | 2h | 同上 |
| 2.3 创建style-dark | 2h | 新增黑暗流 |
| 2.4 创建style-infinity | 2h | 新增无限流 |
| 2.5 创建style-building | 2h | 新增种田流 |
| 2.6 创建style-serious | 2h | 严肃正剧 |
| 2.7 创建style-sweet | 2h | 甜宠流 |

> **注**: 先实现Layer 1的4种元风格，再细化为7种具体风格

---

### Phase 3: 类型打磨 (P1 - 12h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 3.1 创建scifi-expert | 3h | 科幻世界观 |
| 3.2 创建suspense-expert | 3h | 悬疑推理 |
| 3.3 创建urban-expert | 3h | 都市重生 |
| 3.4 增强时间线追踪 | 3h | Day不可倒退 |

---

### Phase 4: 集成与验证 (P1 - 8h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 4.1 集成风格×类型矩阵 | 3h | 组合生成 |
| 4.2 生成20章验证 | 5h | 编辑验收 |

---

**总预计工作量**: ~46小时

---

## 七、立即行动项（V6发布后）

- [x] 移除`style-mystery`（归入类型suspense）
- [x] 新增`style-dark`、`style-infinity`、`style-building`
- [x] 每种风格准备3个跨类型样本
- [x] 增加"类型-风格冲突检测"逻辑
- [x] 增加可量化约束指标
- [x] 简化到4种元风格验证可行性

---

## 八、验收标准

### MVP验收（Phase 1完成）
- [ ] GenreDetector识别准确率 > 90%
- [ ] 切换模板后约束内容变化
- [ ] 时间线约束生效（Day不可倒退）
- [ ] 约束冲突有仲裁机制
- [ ] 类型-风格兼容性检测生效

### 风格验收（Phase 2完成）
- [ ] 7种风格Skill完整
- [ ] 每种风格有3个跨类型样本
- [ ] 可量化约束指标生效
- [ ] 风格冲突检测通过

### 多类型验收（Phase 3完成）
- [ ] 支持4种以上类型（scifi/suspense/urban/xianxia）
- [ ] 每种类型有专业Expert
- [ ] 模板可热切换

### 集成验收（Phase 4完成）
- [ ] 类型×风格组合生成正常
- [ ] 20章完整生成通过编辑验收

---

## 九、核心原则

> **类型基座稳固，风格叠加验证，冲突仲裁兜底**

- ✅ 先类型Expert后风格Skill（基座优先）
- ✅ 321样本原则（防止污染）
- ✅ 兼容性矩阵（防止冲突）
- ✅ 可量化约束（避免模糊）
- ✅ MVP验证先行（分阶段验证）

---

## 十、下一步

开始实施 **Phase 1**：

1. 创建 `core/genre_detector.py`
2. 创建 `core/constraint_template_manager.py`
3. 重构 `core/writing_constraint_manager.py`
4. 实现 `core/constraint_arbiter.py`（含风格冲突检测）

用MVP验证"类型感知+约束切换+风格检测"核心逻辑。
