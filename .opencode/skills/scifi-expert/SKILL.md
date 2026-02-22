---
name: 科幻/后室专家
level: expert
genre: scifi
triggers: [科幻, 后室, SCP, 末世, 废土]
---

## 核心能力
- 科幻/后室/SCP世界观构建
- 认知阶段体系设计
- 实体威胁规则设计
- 资源消耗系统

## 战力体系

### 认知深化系统
```json
{
  "type": "cognitive_stages",
  "stages": [
    {"name": "迷失者", "ability": "基本生存", "description": "刚进入后室，无法理解规则"},
    {"name": "观察者", "ability": "规则辨识", "description": "能识别危险实体和生存规则"},
    {"name": "适应者", "ability": "环境利用", "description": "能利用后室资源生存"},
    {"name": "探索者", "ability": "地图绘制", "description": "能探索新区域并记录"},
    {"name": "解析者", "ability": "实体研究", "description": "能研究实体弱点并利用"}
  ],
  "progression": "每个阶段需要明确的触发条件（如：发现X个实体弱点）"
}
```

## 实体威胁设计

### SCP实体模板
```json
{
  "entity_id": "SCP-XXX",
  "name": "实体名称",
  "class": "Safe/Euclid/Keter",
  "threat_level": 1-5,
  "abilities": ["能力描述"],
  "weakness": ["弱点"],
  "containment_method": "收容方法",
  "kill_rules": "杀人规则（绝对）"
}
```

### 常见实体示例
| 实体 | 威胁等级 | 能力 | 弱点 | 杀人规则 |
|------|----------|------|------|----------|
| SCP-106 | 5 | 穿墙 | 高温 | 接触即死 |
| SCP-939 | 4 | 声波攻击 | 听力 | 听到声音被同化 |
| 笑魇 | 5 | 极速 | 强光 | 黑暗中直视3秒即死 |
| 派对客 | 4 | 诱惑 | 拒绝 | 接受邀请即被同化 |

## 资源系统

### 关键资源
```json
{
  "resources": [
    {"name": "杏仁水", "usage": "恢复SAN值/治愈", "rarity": "常见"},
    {"name": "电池", "usage": "照明/设备", "rarity": "中等"},
    {"name": "食物", "usage": "充饥", "rarity": "稀少"},
    {"name": "医疗用品", "usage": "治疗", "rarity": "稀少"}
  ],
  "consumption_rate": "严格（饥饿/疲惫会影响行动）"
}
```

## 时间线规则
- 格式：Day X
- 重大事件间隔：至少1天
- 时间跳跃限制：最大7天

## 禁止出现
- 修仙词汇：修炼、灵气、法力、金丹、元婴
- 境界设定
- 科幻装备出现（需铺垫）

## 输出格式
生成后室/SCP相关世界观时，必须包含：
1. 认知阶段体系定义
2. 至少3个实体威胁设计
3. 资源系统设计
4. 时间线规则
