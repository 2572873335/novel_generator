# 系统优化方案 V7：通用网文生成系统（编辑终审版）

**版本**: 7.0  
**更新日期**: 2026-02-22  
**基于**: 起点编辑终审意见 + V6修订

---

## 一、终审修订（回应编辑意见）

### 🚨 立即修正

| 问题 | 修正方案 |
|------|----------|
| **样本选择** | 改用"黄金三章"原则（每风格3样本×前3章） |
| **Phase 1过大** | 拆分为 Phase 1A + Phase 1B，分阶段验证 |
| **约束过死** | 增加"风格偏离度"预警机制（warn不断生成） |
| **无验证用例** | 增加AB测试对比设计 |

### ✅ 编辑肯定

1. **元风格分层** - 神来之笔，避免风格爆炸
2. **约束优先级科学化** - temporal_continuity: 100 深得精髓
3. **可量化指标** - 可测试可验收

---

## 二、"黄金三章"样本原则

### 2.1 核心原则

```
原因：
- 网文前3章决定风格基调（节奏、句式、情绪）
- 避免学习中期水字数、后期崩坏
- 减少token消耗
```

### 2.2 样本清单

| 风格 | 样本 | 具体章节 | 关键特征 |
|------|------|----------|----------|
| **blood-punch** | 《斗破苍穹》 | 第1-3章 | "三十年河东"短句、情绪爆发节点 |
| **blood-punch** | 《超神机械师》 | 第1-3章 | 游戏化数值+快节奏冲突 |
| **blood-punch** | 《全职法师》 | 第1-3章 | 都市异能+越级挑战 |
| **cowboy** | 《苟道》 | 第1-3章 | 心理活动70%，动作描写少 |
| **cowboy** | 《我只想安静地玩游戏》 | 第1-3章 | 稳健发育，风险计算 |
| **cowboy** | 《黎明之剑》 | 第1-3章 | 宏观视角+技术细节 |
| **dark** | 《蛊真人》 | 第1-3章 | 残酷觉醒、利益至上 |
| **dark** | 《轮回乐园》 | 第1-3章 | 任务思维、杀伐果断 |
| **dark** | 《熔流》 | 第1-3章 | 末世生存、资源计算 |
| **infinity** | 《惊悚乐园》 | 第1-3章 | 副本任务、智慧解密 |
| **infinity** | 《从姑获鸟开始》 | 第1-3章 | 武侠副本、功法获取 |
| **infinity** | 《我在明日方舟》 | 第1-3章 | 策略布局、多线操作 |
| **building** | 《黎明之剑》 | 第1-3章 | 宏观视角+技术代差 |
| **building** | 《放开那个女巫》 | 第1-3章 | 种田基建、科技发展 |
| **building** | 《异界征服手册》 | 第1-3章 | 领土扩张、外交谋略 |
| **serious** | 《诡秘之主》 | 第1-3章 | 悬疑氛围、克苏鲁元素 |
| **serious** | 《三体》 | 第1-3章 | 硬科幻、宏观视角 |
| **serious** | 《宰执天下》 | 第1-3章 | 权谋政治、历史考据 |
| **sweet** | 《我家老婆来自一千年前》 | 第1-3章 | 甜蜜互动、日常温馨 |
| **sweet** | 《光阴之外》日常篇 | 第1-3章 | 青春校园、纯爱甜宠 |
| **sweet** | 《学渣的心理咨询师》 | 第1-3章 | 轻松甜蜜、互相治愈 |

> **总计**: 7种风格 × 3样本 = 21个"黄金三章"片段

---

## 三、Phase 1 拆分（Phase 1A + 1B）

### Phase 1A: 类型基座 (P0 - 4h)

**目标**: 验证GenreDetector + ConstraintTemplateManager

| 任务 | 工作量 | 验收标准 |
|------|--------|----------|
| 1A.1 创建GenreDetector | 2h | 输入"后室+SCP"→识别为scifi |
| 1A.2 创建ConstraintTemplateManager | 2h | 加载scifi模板→约束含"认知阶段" |

**验证用例**:
```
输入: "后室探险，SCP收容失效"
期望: GenreDetector输出 {genre: "scifi", confidence: 0.95}
期望: 模板约束包含 ["认知阶段", "实体威胁", "资源消耗"]
```

---

### Phase 1B: 约束仲裁 (P0 - 4h)

**目标**: 验证ConstraintArbiter + 风格冲突检测

| 任务 | 工作量 | 验收标准 |
|------|--------|----------|
| 1B.1 创建ConstraintArbiter | 2h | 时间线冲突可仲裁 |
| 1B.2 实现StyleConflictDetector | 2h | 检测xianxia+sweet冲突 |

**验证用例**:
```
测试1: genre: xianxia + style: blood-punch
期望: {conflict: false, message: "兼容"}

测试2: genre: xianxia + style: sweet  
期望: {conflict: true, resolution: "建议使用blood-punch", forbidden: true}

测试3: Day 1 → Day 0 (时间倒退)
期望: {conflict: true, priority: 100, message: "时间不可倒退"}
```

---

### Phase 1拆分优势

```
好处：
- 如果1A就错了（GenreDetector识别错误），1B全白做
- 分阶段验证降低返工风险
- 每阶段2小时，可快速迭代
```

---

## 四、风格偏离度预警机制

### 4.1 核心逻辑

```python
class StyleDeviationDetector:
    def __init__(self):
        self.flexibility = 0.3  # 30%浮动
    
    def check_deviation(self, actual: Dict, target: Dict) -> Dict:
        """检测风格偏离度"""
        deviations = []
        
        for metric, target_value in target.items():
            if isinstance(target_value, (int, float)):
                lower_bound = target_value * (1 - self.flexibility)
                actual_value = actual.get(metric, 0)
                
                if actual_value < lower_bound:
                    deviations.append({
                        "metric": metric,
                        "target": target_value,
                        "actual": actual_value,
                        "severity": "warning"  # warn不断生成
                    })
        
        return {
            "deviations": deviations,
            "should_block": False,  # 只警告，不阻断
            "message": "风格偏离度30%，建议调整" if deviations else "风格正常"
        }
```

### 4.2 预警示例

```
场景: blood-punch风格章节
目标: 短句比60%

检测1: 实际短句比45%
→ 触发warning: "当前章节短句过少(45%<60%×0.7=42%)，可能偏离热血升级风格"
→ 不阻断生成，仅提示

检测2: 实际短句比30%  
→ 触发warning: "严重偏离热血升级风格，建议增加战斗描写"
→ 不阻断生成，建议修改

检测3: 连续3章严重偏离
→ 触发warning: "风格持续偏离，建议Reviewer重点关注"
```

### 4.3 浮动参数配置

```json
{
  "style_deviation": {
    "flexibility": 0.3,
    "warning_threshold": 0.3,
    "critical_threshold": 0.5,
    "consecutive_chapters_limit": 3,
    "action": "warn_only"  # 不断生成，只警告
  }
}
```

---

## 五、AB测试对比设计

### 5.1 测试用例

**同一世界观**: 主角被困无限恐怖空间，需通关副本求生

| 组别 | genre | style | 预期特征 |
|------|-------|-------|----------|
| **A组** | game | blood-punch | 每章战斗、升级面板、热斗 |
| **B组** | game | cowboy | 研究规则、稳健发育、风险计算 |
| **C组** | game | dark | 利用队友当炮灰、利益至上 |

### 5.2 验收标准

```
验证：三组生成的前3章应有显著差异

A组(热血):
- 短句比 > 50%
- 每章至少1场战斗
- 心理活动: 愤怒→战意→爆发
- 章节钩子: cliffhanger

B组(苟道):
- 短句比 < 40%
- 3章内无战斗，以探索为主
- 心理活动: 观察→计算→谨慎行动
- 章节钩子: information_hook

C组(黑暗):
- 短句比 40-50%
- 涉及资源争夺、道德选择
- 心理活动: 利益计算、风险评估
- 章节钩子: twist
```

### 5.3 测试执行

```
Phase 4集成时执行：
1. 准备统一的世界观输入（无限恐怖空间）
2. 分别调用3种子风格组合
3. 人工验收前3章差异度
4. 差异度 < 30% → 风格系统未生效，需返工
```

---

## 六、完整实施计划 V7

### Phase 0: 基线测试 (P0 - 2h)

| 任务 | 验收 |
|------|------|
| 生成前3章对照 | 记录现有问题 |

---

### Phase 1A: 类型基座 (P0 - 4h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 1A.1 GenreDetector | 2h | scifi识别>90% |
| 1A.2 ConstraintTemplateManager | 2h | 模板加载 |

---

### Phase 1B: 约束仲裁 (P0 - 4h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 1B.1 ConstraintArbiter | 2h | 冲突仲裁 |
| 1B.2 StyleConflictDetector | 2h | 风格冲突检测 |

---

### Phase 2: 风格Skill系统 (P1 - 14h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 2.1 style-blood-punch | 2h | 黄金三章+量化约束 |
| 2.2 style-cowboy | 2h | 同上 |
| 2.3 style-dark | 2h | 同上 |
| 2.4 style-infinity | 2h | 同上 |
| 2.5 style-building | 2h | 同上 |
| 2.6 style-serious | 2h | 同上 |
| 2.7 style-sweet | 2h | 同上 |

---

### Phase 3: 类型打磨 (P1 - 12h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 3.1 scifi-expert | 3h | 科幻世界观 |
| 3.2 suspense-expert | 3h | 悬疑推理 |
| 3.3 urban-expert | 3h | 都市重生 |
| 3.4 时间线追踪增强 | 3h | Day不可倒退 |

---

### Phase 4: 集成与验证 (P1 - 8h)

| 任务 | 工作量 | 验收 |
|------|--------|------|
| 4.1 风格×类型矩阵集成 | 2h | 组合生成 |
| 4.2 AB测试对比 | 2h | 3组差异显著 |
| 4.3 生成20章验证 | 4h | 编辑验收 |

---

**总预计工作量**: ~46小时

---

## 七、立即行动项

- [x] 黄金三章样本清单（21个片段）
- [x] Phase 1拆分为1A+1B
- [x] 风格偏离度预警机制
- [x] AB测试对比设计

---

## 八、验收标准

### Phase 1A 验收
- [ ] GenreDetector识别"后室+SCP"→scifi > 90%
- [ ] 模板约束含"认知阶段"

### Phase 1B 验收
- [ ] xianxia+sweet → 冲突检测通过
- [ ] Day倒退 → 仲裁拦截

### Phase 2 验收
- [ ] 7种风格Skill完整（黄金三章样本）
- [ ] 风格偏离度预警生效

### Phase 3 验收
- [ ] 4种类型Expert（scifi/suspense/urban/xianxia）
- [ ] 时间线Day不可倒退

### Phase 4 验收
- [ ] AB测试3组差异度 > 30%
- [ ] 20章生成通过编辑验收

---

## 九、核心原则

> **分阶段验证，样本黄金三章，偏离预警不断生成**

- ✅ Phase 1拆分为1A+1B（降低返工风险）
- ✅ 样本用"黄金三章"（防崩坏、减token）
- ✅ 偏离度预警（warn不断生成）
- ✅ AB测试验证风格差异

---

## 十、下一步

开始实施 **Phase 1A**:

1. 创建 `core/genre_detector.py`
2. 创建 `core/constraint_template_manager.py`
3. 验证"后室+SCP"→scifi识别

预计2小时完成验证。
