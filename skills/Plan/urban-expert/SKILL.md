---
name: 都市重生专家
level: expert
genre: urban
triggers: [都市, 重生, 总裁, 豪门, 创业]
---

## 核心能力
- 都市重生世界观构建
- 财富系统设计
- 人脉关系系统
- 打脸逆袭设计

## 财富系统

### 财富等级
```json
{
  "wealth_levels": [
    {"level": 1, "title": "小康", "range": "100万-1000万"},
    {"level": 2, "title": "中产", "range": "1000万-1亿"},
    {"level": 3, "title": "富裕", "range": "1亿-10亿"},
    {"level": 4, "title": "富豪", "range": "10亿-100亿"},
    {"level": 5, "title": "顶级富豪", "range": "100亿+"}
  ],
  "milestones": [
    {"chapter": 3, "milestone": "第一桶金", "amount": "100万"},
    {"chapter": 8, "milestone": "公司上市", "amount": "1亿"},
    {"chapter": 15, "milestone": "商业帝国", "amount": "10亿+"}
  ]
}
```

### 财富来源
- 股市/期货
- 房地产
- 互联网/科技
- 实业/制造业
- 投资/并购

## 人脉关系系统

### 关系类型
```json
{
  "relationship_types": [
    {"type": "family", "description": "家人"},
    {"type": "friend", "description": "朋友"},
    {"type": "rival", "description": "对手"},
    {"type": "mentor", "description": "导师"},
    {"type": "love_interest", "description": "恋人"},
    {"type": "business", "description": "商业伙伴"}
  ],
  "max_concurrent": 3,
  "changes_require_arc": true
}
```

### 打脸设计
```json
{
  "face_slapping_schedule": [
    {"chapter": 3, "target": "前女友/前男友", "type": "嫌贫爱富"},
    {"chapter": 8, "target": "商业对手", "type": "商业竞争"},
    {"chapter": 15, "target": "仇家", "type": "复仇"}
  ]
}
```

## 重生设定

### 重生优势
- 信息差（未来知识）
- 经验（失败教训）
- 人脉（未来巨头）
- 预知（重大事件）

### 重生代价
- 时间成本（从零开始）
- 心理创伤（前世遗憾）
- 关系重建（失去原有关系）

## 时间线规则
- 格式：年/月/日
- 最大跳跃：30天
- 现实感：符合现代社会发展

## 禁止出现
- 修仙/灵气
- 超自然能力（除非系统/游戏设定）
- 不合理快速暴富

## 输出格式
生成都市重生相关世界观时，必须包含：
1. 财富等级体系
2. 人脉关系设计
3. 打脸逆袭计划
4. 时间线结构
