# 系统优化方案 V5：通用网文生成系统（风格Skills版）

**版本**: 5.0  
**更新日期**: 2026-02-22  
**基于**: 起点编辑反馈 + 网文类型研究 + 写作风格Skills

---

## 一、架构升级：从"修车"到"造车"

### 核心突破

1. **类型感知引擎（GenreDetector）** - 解决"仙侠/科幻混杂"的根本方案
2. **约束模板化（Template System）** - 同一引擎，不同内容
3. **专家Skill专业化** - 让专业的人做专业的事

---

## 二、风险规避（V3盲区修复）

### 🚨 风险1：工作量低估
**原问题**: 6个Expert只需14小时  
**修复**: 采用MVP策略，分阶段实施

### 🚨 风险2：约束冲突（⭐⭐⭐⭐⭐ 新增）
**问题**: 时间线约束 vs 情节升级冲突时，系统听谁的？  
**修复**: 增加`ConstraintArbiter`约束仲裁机制
```python
class ConstraintArbiter:
    def resolve_conflict(self, constraints: List[Constraint]) -> Constraint:
        """约束优先级仲裁"""
        priority = {
            "temporal_continuity": 100,  # 时间连续性最高
            "character_motivation": 90,
            "power_system": 80,
            "genre_style": 70,
            "plot_escalation": 60,
            "resource_pressure": 50
        }
        # 返回最高优先级约束
```

### 🚨 风险3：风格同质化（⭐⭐⭐⭐ 新增）
**问题**: 所有科幻都变成"标准SCP风"  
**修复**: 增加Style Template
```json
{
  "genre": "scifi",
  "style": "clinical_horror",  // SCP风格
  // 或 "poetic_post_apocalyptic" // 《小蘑菇》风格
  // 或 "cyberpunk_noir" // 赛博朋克风格
}
```

---

## 三、类型研究（保持）

| 类型 | 核心爽点 | 需要的专业Skill |
|------|---------|----------------|
| **玄幻/仙侠** | 升级突破→打脸反派 | cultivation-designer |
| **都市** | 重生逆袭→打脸前任 | urban-expert |
| **科幻/悬疑** | 生存挑战→解密 | scifi-expert |
| **游戏** | 升级装备→副本挑战 | game-expert |
| **言情** | 相遇误会→HE结局 | romance-expert |
| **历史** | 穿越→权谋→争霸 | historical-expert |

---

## 四、写作风格Skills（新增）

基于网文研究，创建8种写作风格Skills：

### 3.1 风格分类

| 风格 | 核心特点 | 代表作 | Skill名称 |
|------|---------|--------|----------|
| **热血升级流** | 升级战斗、激情澎湃、越级挑战 | 《斗破苍穹》《全职高手》 | `style-blood-punch` |
| **轻松搞笑流** | 幽默吐槽、反转打脸、轻松氛围 | 《大王饶仁》《我师兄太稳健了》 | `style-comedy` |
| **严肃正剧流** | 深度思考、现实映射、人物复杂 | 《诡秘之主》《宰执天下》 | `style-serious` |
| **悬疑推理流** | 谜题线索、烧脑反转、紧张气氛 | 《十日终焉》《盗墓笔记》 | `style-mystery` |
| **情感细腻流** | 心理描写、情感递进、细节丰富 | 《何以笙箫默》《我不配》 | `style-romance` |
| **脑洞创意流** | 独特设定、世界观创新、出乎意料 | 《的一路向北》《道诡异仙》 | `style-brainhole` |
| **苟道发育流** | 谨慎稳健、延迟满足、积累实力 | 《苟道》《我只想安静地玩游戏》 | `style-cowboy` |
| **软饭甜宠流** | 轻松甜蜜、依赖对象、甜蜜互动 | 《软饭》《吃软饭》 | `style-sweet` |

### 3.2 风格Skill结构

每个风格Skill包含：

```yaml
# .opencode/skills/style-blood-punch/SKILL.md

---
name: 热血升级流
level: style
genre: universal
triggers: [热血, 升级, 战斗]
---

## 风格特点
- 节奏紧凑，每章必有战斗或升级
- 越级挑战体现主角成长
- 情绪递进：压抑→爆发→高潮
- 金手指明确且逐步增强

## 爽点设计
```
开篇: 退婚/羞辱/困境
前期: 小boss胜利建立信心
中期: 越级挑战成功，打脸反派
后期: 越阶战斗，震撼全场
高潮: 越级击败强敌，收获至宝
```

## 句式特征
- 短句为主，节奏快
- 心理活动丰富，内心独白多
- 战斗描写详细，动作感强
- 情绪递进：愤怒→战意→爆发

## 示例（来自《斗破苍穹》）
```
"萧炎，再不使用斗技的话，你就要死了！"
萧炎冷笑一声，手掌猛然握拢：
"既然如此，那便让你看看吧"
"焰分噬浪尺！"
天空上，巨大的尺影划破长空，带着刺耳的音啸声，
对着黑袍人暴射而下...
```

## 叙事节拍
- Chapter 1: 困境/金手指亮相
- Chapter 2-3: 小试牛刀，崭露头角
- Chapter 4-6: 建立信心，收获追随者
- Chapter 7-10: 越级挑战，打脸反派
- Chapter 11+: 越阶战斗，震撼世界

## 禁止出现
- 主角长时间压抑不反击
- 连续失败超过2次
- 敌人智商全程在线
- 断更式断章（悬念过度）
```

### 3.3 风格组合矩阵

| Genre \ Style | 热血升级 | 轻松搞笑 | 严肃正剧 | 悬疑推理 |
|---------------|----------|----------|----------|----------|
| **仙侠** | ✅ 经典《斗破》 | ✅ 《我师兄太稳健了》 | ✅ 《凡人修仙传》 | ❌ |
| **都市** | ✅ 《重生之都市修仙》 | ✅ 《大王饶命》 | ✅ 《重生之财源滚滚》 | ❌ |
| **科幻** | ✅ 《星河战队》 | ❌ | ✅ 《三体》 | ✅ 《深海之下》 |
| **悬疑** | ❌ | ❌ | ✅ 《盗墓笔记》 | ✅ 《十日终焉》 |

---

## 四、优化计划 V5（分阶段MVP）

### Phase 0: 基线测试 (P0)
**目标**: 验证现有系统问题，生成对照组

**任务**:
1. 用现有系统生成前3章
2. 记录问题（时间线、类型混杂等）
3. 作为优化后的对比基线

---

### Phase 1: MVP核心逻辑 (P0 - 8小时)

**目标**: 验证"类型感知+约束切换"的核心逻辑

#### Task 1.1: 创建GenreDetector
```python
GENRE_SIGNATURES = {
    "xianxia": {"keywords": ["修仙", "境界", "宗门"], "template": "xianxia"},
    "scifi": {"keywords": ["末世", "科幻", "后室"], "template": "scifi"},
    "urban": {"keywords": ["都市", "重生", "总裁"], "template": "urban"}
}
```

#### Task 1.2: 创建ConstraintTemplateManager
- 支持3种基础模板: xianxia, scifi, urban
- 模板存储在 `config/constraints/`

#### Task 1.3: 重构WritingConstraintManager
- 根据genre加载对应模板
- 生成类型特定约束

#### Task 1.4: 创建ConstraintArbiter（新增）
- 定义约束优先级
- 解决冲突

#### Task 1.5: MVP验证
- 用同一世界观（后室+SCP），分别加载scifi和xianxia模板生成第1章
- 验证:
  - [xianxia模板] 不出现"认知阶段"、"实体威胁"
  - [scifi模板] 出现"认知阶段"约束
  - 时间线约束生效

---

### Phase 2: 单类型打磨 (P1 - 12小时)

**目标**: 把科幻悬疑类型做到极致

#### Task 2.1: 创建scifi-expert Skill
**输出格式**:
```json
{
  "power_system": {
    "type": "cognitive_stages",
    "stages": ["迷失者", "观察者", "适应者", "探索者", "解析者"]
  },
  "entity_threats": {
    "SCP-106": {"threat": 5, "ability": "穿墙", "weakness": "高温"},
    "SCP-939": {"threat": 4, "ability": "声波攻击", "weakness": "听力"}
  },
  "resource_tracking": {
    "items": ["杏仁水", "电池", "食物"],
    "consumption_rate": "严格"
  }
}
```

#### Task 2.2: 增强时间线追踪
- 严格Day追踪
- 不允许倒退（除非重生设定）
- 最大跳跃限制

#### Task 2.3: 认知阶段系统
- 每阶段能力边界
- 阶段晋升触发条件
- 软性约束设计（flexibility: 0.3）

#### Task 2.4: 实体威胁验证（Warning Mode）
- 检测实体能力是否被削弱
- 警告而非阻断

#### Task 2.5: 生成完整20章
- 用优化后的系统生成后室项目20章
- 用起点编辑标准验收

---

### Phase 3: 多类型扩展 (P1 - 18小时)

#### Task 3.1: urban-expert Skill
```json
{
  "wealth_system": {
    "milestones": ["第一桶金", "公司上市", "商业帝国"]
  },
  "face_slapping_schedule": [
    {"chapter": 3, "target": "前女友"},
    {"chapter": 8, "target": "商业对手"}
  ]
}
```

#### Task 3.2: xianxia-expert（复用现有cultivation-designer）
- 确保仙侠模板完整

#### Task 3.3: game-expert Skill
#### Task 3.4: romance-expert Skill

---

### Phase 4: 风格系统 (P2 - 6小时)

#### Task 4.1: 创建Style Template系统
```json
{
  "styles": {
    "clinical_horror": {
        "tone": "客观、编号化",
        "vocabulary": ["实体", "收容", "异常"]
    },
    "poetic_apocalyptic": {
        "tone": "诗意、抒情",
        "vocabulary": ["废墟", "幸存", "希望"]
    },
    "cyberpunk_noir": {
        "tone": "冷硬、黑色电影",
        "vocabulary": ["义体", "赛博", "霓虹"]
    }
  }
}
```

#### Task 4.2: 集成到WritingConstraintManager

---

## 五、实施优先级 V4

| 阶段 | 任务 | 工作量 | 优先级 | 验收 |
|------|------|--------|--------|------|
| **Phase 0** | 基线测试 | 2h | P0 | 生成前3章 |
| **Phase 1** | 1.1 GenreDetector | 2h | P0 | 类型识别>90% |
| **Phase 1** | 1.2 模板管理器 | 2h | P0 | 3种模板加载 |
| **Phase 1** | 1.3 重构约束 | 2h | P0 | 约束生效 |
| **Phase 1** | 1.4 ConstraintArbiter | 2h | P0 | 冲突解决 |
| **Phase 1** | 1.5 MVP验证 | 2h | P0 | 模板切换对比 |
| **Phase 2** | 2.1 scifi-expert | 3h | P1 | 完整输出 |
| **Phase 2** | 2.2-2.4 追踪系统 | 5h | P1 | 时间线正确 |
| **Phase 2** | 2.5 20章生成 | 4h | P1 | 编辑验收 |
| **Phase 3** | 3.1-3.4 多类型 | 12h | P1 | 3+类型支持 |
| **Phase 4** | 4.1-4.2 风格 | 6h | P2 | 风格切换 |

**总预计工作量**: ~42小时

---

## 六、验收标准

### MVP验收（Phase 1完成）
- [ ] GenreDetector识别准确率 > 90%
- [ ] 切换模板后约束内容变化
- [ ] 时间线约束生效（Day不可倒退）
- [ ] 约束冲突有仲裁机制

### 类型验收（Phase 2完成）
- [ ] 科幻类型20章完整生成
- [ ] 认知阶段渐进式体现
- [ ] 实体威胁合理
- [ ] 资源消耗有压力

### 多类型验收（Phase 3完成）
- [ ] 支持3种以上类型
- [ ] 每种类型有专业Expert
- [ ] 模板可热切换

### 风格验收（Phase 4完成）
- [ ] 支持Style Template
- [ ] 同一类型不同风格

---

## 七、约束仲裁优先级

```python
CONSTRAINT_PRIORITY = {
    # 最高：叙事基础（不可违背）
    "temporal_continuity": 100,      # 时间连续性
    "character_identity": 95,          # 角色身份
    
    # 高：核心类型规则
    "power_system": 80,                # 战力体系（境界/认知阶段）
    "realm_boundaries": 75,            # 空间边界
    
    # 中：情节节奏
    "plot_escalation": 60,            # 情节升级
    "motivation_tracking": 55,         # 动机追踪
    
    # 低：资源压力
    "resource_pressure": 40,           # 资源消耗
    "entity_threat": 35,              # 实体威胁
    
    # 最低：风格偏好
    "genre_style": 20,                 # 类型风格
}
```

**冲突解决原则**:
1. 高优先级约束不可违背
2. 低优先级可被覆盖（通过hook机制）
3. 高潮/转折章节可临时放宽资源限制

---

## 八、风格模板示例

### clinical_horror（SCP风格）
```
✅ 允许: "实体表现出攻击性"
❌ 禁止: "怪物张牙舞爪地扑来"
```

### poetic_apocalyptic（《小蘑菇》风格）
```
✅ 允许: "废墟上开出一朵小花"
❌ 禁止: "杏仁水恢复剂 -50ml"
```

### cyberpunk_noir（赛博朋克风格）
```
✅ 允许: "义体闪烁红光"
❌ 禁止: "修仙功法"
```

---

## 九、核心原则

> **MVP验证先行，约束仲裁兜底，风格差异化**

- ✅ 分阶段验证，不做一次性大规模重构
- ✅ 约束冲突有仲裁机制
- ✅ 风格模板避免同质化
- ⚠️ 软性约束保留AI创造性
- 🎯 叙事张力优先于技术完美

---

## 十、下一步

开始实施 **Phase 0 + Phase 1.1-1.3**：
1. 基线测试（生成前3章）
2. GenreDetector实现
3. 模板管理器实现
4. 约束重构

用MVP验证"类型感知+约束切换"核心逻辑是否正确。
