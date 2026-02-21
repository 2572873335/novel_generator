"""
设定一致性追踪器
用于追踪和检查小说中的设定一致性，避免 Kimi 编辑指出的那些问题
"""

import os
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CharacterState:
    """角色状态追踪"""

    name: str
    abilities: List[str] = field(default_factory=list)
    power_level: int = 1  # 1-10
    relationships: Dict[str, str] = field(default_factory=dict)
    first_appearance: int = 0
    last_appearance: int = 0
    key_events: List[str] = field(default_factory=list)

    def add_ability(self, ability: str, chapter: int, reason: str = ""):
        """添加能力，记录来源"""
        if ability not in self.abilities:
            self.abilities.append(ability)
            self.key_events.append(f"Ch{chapter}: 获得能力【{ability}】{reason}")

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "abilities": self.abilities,
            "power_level": self.power_level,
            "relationships": self.relationships,
            "first_appearance": self.first_appearance,
            "last_appearance": self.last_appearance,
            "key_events": self.key_events,
        }


@dataclass
class EnemyState:
    """敌人/威胁状态追踪"""

    name: str
    threat_level: int = 1  # 1-10
    known_weaknesses: List[str] = field(default_factory=list)
    known_abilities: List[str] = field(default_factory=list)
    defeats: List[Dict] = field(default_factory=list)  # 被击败记录

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "threat_level": self.threat_level,
            "known_weaknesses": self.known_weaknesses,
            "known_abilities": self.known_abilities,
            "defeats": self.defeats,
        }


@dataclass
class TimelineEvent:
    """时间线事件"""

    chapter: int
    event_type: str  # "discovery", "battle", "ability_gain", "death", "alliance"
    description: str
    timestamp: str = ""  # 故事内时间
    consequences: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "chapter": self.chapter,
            "event_type": self.event_type,
            "description": self.description,
            "timestamp": self.timestamp,
            "consequences": self.consequences,
        }


class ConsistencyTracker:
    """
    设定一致性追踪器

    解决 Kimi 编辑指出的问题：
    1. 战力体系崩坏 - 追踪敌我双方战力变化
    2. 能力体系混乱 - 记录主角能力获取过程
    3. 逻辑硬伤 - 检测设定矛盾
    4. 时间线混乱 - 统一时间管理
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.tracker_file = os.path.join(project_dir, "consistency_tracker.json")

        # 追踪数据
        self.characters: Dict[str, CharacterState] = {}
        self.enemies: Dict[str, EnemyState] = {}
        self.timeline: List[TimelineEvent] = []
        self.world_rules: Dict[str, Any] = {}  # 世界观规则
        self.protagonist_abilities: List[Dict] = []  # 主角能力日志

        # 加载已有数据
        self._load()

    def _load(self):
        """加载追踪数据"""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 重建对象
                for name, char_data in data.get("characters", {}).items():
                    self.characters[name] = CharacterState(
                        name=char_data["name"],
                        abilities=char_data.get("abilities", []),
                        power_level=char_data.get("power_level", 1),
                        relationships=char_data.get("relationships", {}),
                        first_appearance=char_data.get("first_appearance", 0),
                        last_appearance=char_data.get("last_appearance", 0),
                        key_events=char_data.get("key_events", []),
                    )

                for name, enemy_data in data.get("enemies", {}).items():
                    self.enemies[name] = EnemyState(
                        name=enemy_data["name"],
                        threat_level=enemy_data.get("threat_level", 1),
                        known_weaknesses=enemy_data.get("known_weaknesses", []),
                        known_abilities=enemy_data.get("known_abilities", []),
                        defeats=enemy_data.get("defeats", []),
                    )

                for event_data in data.get("timeline", []):
                    self.timeline.append(
                        TimelineEvent(
                            chapter=event_data["chapter"],
                            event_type=event_data["event_type"],
                            description=event_data["description"],
                            timestamp=event_data.get("timestamp", ""),
                            consequences=event_data.get("consequences", []),
                        )
                    )

                self.world_rules = data.get("world_rules", {})
                self.protagonist_abilities = data.get("protagonist_abilities", [])

            except Exception as e:
                print(f"[Tracker] 加载失败: {e}")

    def _save(self):
        """保存追踪数据"""
        data = {
            "characters": {
                name: char.to_dict() for name, char in self.characters.items()
            },
            "enemies": {name: enemy.to_dict() for name, enemy in self.enemies.items()},
            "timeline": [event.to_dict() for event in self.timeline],
            "world_rules": self.world_rules,
            "protagonist_abilities": self.protagonist_abilities,
            "last_updated": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)
        with open(self.tracker_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def track_character_appearance(self, name: str, chapter: int):
        """追踪角色出现"""
        if name not in self.characters:
            self.characters[name] = CharacterState(name=name, first_appearance=chapter)
        self.characters[name].last_appearance = chapter
        self._save()

    def track_ability_gain(
        self,
        character: str,
        ability: str,
        chapter: int,
        source: str = "",
        reason: str = "",
    ):
        """
        追踪能力获取

        解决问题：能力体系混乱
        - 每个能力必须有明确来源
        - 记录获取原因
        """
        if character not in self.characters:
            self.characters[character] = CharacterState(name=character)

        char = self.characters[character]

        # 检查能力是否已存在
        if ability in char.abilities:
            return False, f"角色 {character} 已有能力【{ability}】"

        # 添加能力
        char.add_ability(ability, chapter, f"来源:{source} {reason}")

        # 如果是主角，记录到主角能力日志
        if character == self._get_protagonist_name():
            self.protagonist_abilities.append(
                {
                    "ability": ability,
                    "chapter": chapter,
                    "source": source,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        self._save()
        return True, f"角色 {character} 在第{chapter}章获得能力【{ability}】"

    def track_enemy_threat(
        self,
        enemy_name: str,
        threat_level: int,
        chapter: int,
        abilities: List[str] = None,
    ):
        """
        追踪敌人威胁等级

        解决问题：战力体系崩坏
        - 追踪敌人初始威胁
        - 记录已知能力
        """
        if enemy_name not in self.enemies:
            self.enemies[enemy_name] = EnemyState(name=enemy_name)

        enemy = self.enemies[enemy_name]

        # 警告：威胁等级不能随意下降
        if threat_level < enemy.threat_level:
            print(
                f"⚠️ [Tracker警告] 敌人 {enemy_name} 威胁等级从 {enemy.threat_level} 降至 {threat_level}"
            )
            print(f"   请确保有合理的剧情解释！")

        enemy.threat_level = max(enemy.threat_level, threat_level)
        if abilities:
            for ability in abilities:
                if ability not in enemy.known_abilities:
                    enemy.known_abilities.append(ability)

        self._save()

    def track_enemy_defeat(
        self, enemy_name: str, chapter: int, method: str, casualties: Dict = None
    ):
        """
        追踪敌人被击败

        解决问题：战力体系崩坏
        - 记录击败方式
        - 检查合理性
        """
        if enemy_name not in self.enemies:
            print(f"⚠️ [Tracker警告] 未知敌人 {enemy_name} 被击败")
            return False

        enemy = self.enemies[enemy_name]

        # 检查击败方式是否合理
        if enemy.threat_level >= 9:  # 高威胁敌人
            if not casualties or casualties.get("deaths", 0) == 0:
                print(
                    f"⚠️ [Tracker严重警告] 敌人 {enemy_name} 威胁等级 {enemy.threat_level}/10"
                )
                print(f"   被击败方式: {method}")
                print(f"   代价: {casualties or '无代价'}")
                print(f"   ⚠️ 高威胁敌人被轻易击败，可能造成战力崩坏！")
                print(f"   建议：增加代价或削弱敌人初始设定")

        enemy.defeats.append(
            {
                "chapter": chapter,
                "method": method,
                "casualties": casualties or {},
                "enemy_threat_at_defeat": enemy.threat_level,
            }
        )

        # 降低威胁等级
        enemy.threat_level = max(1, enemy.threat_level - 5)

        self._save()
        return True

    def track_timeline_event(
        self, chapter: int, event_type: str, description: str, timestamp: str = ""
    ):
        """
        追踪时间线事件

        解决问题：时间线混乱
        """
        event = TimelineEvent(
            chapter=chapter,
            event_type=event_type,
            description=description,
            timestamp=timestamp,
        )
        self.timeline.append(event)
        self._save()

    def set_world_rule(self, rule_name: str, rule_value: Any, chapter: int):
        """
        设置世界观规则

        解决问题：设定矛盾
        - 规则一旦设定不能轻易改变
        """
        if rule_name in self.world_rules:
            old_value = self.world_rules[rule_name]["value"]
            if old_value != rule_value:
                print(f"⚠️ [Tracker警告] 世界观规则【{rule_name}】被修改")
                print(f"   旧值: {old_value}")
                print(f"   新值: {rule_value}")
                print(f"   请确保有合理的剧情解释！")

        self.world_rules[rule_name] = {
            "value": rule_value,
            "set_at_chapter": chapter,
            "set_at_time": datetime.now().isoformat(),
        }
        self._save()

    def check_consistency(self, chapter: int, content: str) -> Dict[str, Any]:
        """
        检查章节内容的一致性

        Returns:
            检查结果，包含问题列表
        """
        issues = []
        warnings = []

        # 1. 检查能力滥用
        protagonist = self._get_protagonist_name()
        if protagonist in self.characters:
            char = self.characters[protagonist]
            if len(char.abilities) > 5:
                warnings.append(
                    {
                        "type": "ability_bloat",
                        "message": f"主角已有 {len(char.abilities)} 个能力: {', '.join(char.abilities)}",
                        "suggestion": "考虑合并相似能力或删除冗余能力",
                    }
                )

        # 2. 检查敌人威胁变化
        for enemy_name, enemy in self.enemies.items():
            if enemy.threat_level >= 8 and len(enemy.defeats) > 0:
                last_defeat = enemy.defeats[-1]
                if last_defeat.get("casualties", {}).get("deaths", 0) == 0:
                    issues.append(
                        {
                            "type": "power_scaling_issue",
                            "message": f"高威胁敌人 {enemy_name} (威胁{enemy.threat_level}/10) 被无代价击败",
                            "suggestion": "增加战斗代价或削弱敌人初始设定",
                        }
                    )

        # 3. 检查未使用角色
        for name, char in self.characters.items():
            if char.last_appearance > 0 and chapter - char.last_appearance > 5:
                warnings.append(
                    {
                        "type": "forgotten_character",
                        "message": f"角色 {name} 已 {chapter - char.last_appearance} 章未出现",
                        "suggestion": "考虑是否需要让该角色重新登场或交代去向",
                    }
                )

        return {
            "chapter": chapter,
            "issues": issues,
            "warnings": warnings,
            "passed": len(issues) == 0,
        }

    def generate_report(self) -> str:
        """生成一致性追踪报告"""
        report = []
        report.append("=" * 60)
        report.append("设定一致性追踪报告")
        report.append("=" * 60)

        # 主角能力
        protagonist = self._get_protagonist_name()
        if protagonist in self.characters:
            char = self.characters[protagonist]
            report.append(f"\n【主角能力】({len(char.abilities)}个)")
            for ability in char.abilities:
                report.append(f"  - {ability}")

            # 能力获取历史
            report.append(f"\n【能力获取历史】")
            for event in char.key_events:
                report.append(f"  {event}")

        # 敌人威胁
        if self.enemies:
            report.append(f"\n【敌人威胁等级】")
            for name, enemy in self.enemies.items():
                report.append(f"  {name}: {enemy.threat_level}/10")
                if enemy.known_weaknesses:
                    report.append(f"    已知弱点: {', '.join(enemy.known_weaknesses)}")
                if enemy.defeats:
                    report.append(f"    被击败次数: {len(enemy.defeats)}")

        # 时间线
        if self.timeline:
            report.append(f"\n【关键事件时间线】")
            for event in self.timeline[-10:]:  # 最近10个事件
                report.append(
                    f"  Ch{event.chapter}: [{event.event_type}] {event.description}"
                )

        # 世界观规则
        if self.world_rules:
            report.append(f"\n【世界观规则】")
            for rule_name, rule_data in self.world_rules.items():
                report.append(
                    f"  {rule_name}: {rule_data['value']} (第{rule_data['set_at_chapter']}章设定)"
                )

        return "\n".join(report)

    def _get_protagonist_name(self) -> str:
        """获取主角名称"""
        # 从 characters.json 加载
        char_file = os.path.join(self.project_dir, "characters.json")
        if os.path.exists(char_file):
            try:
                with open(char_file, "r", encoding="utf-8") as f:
                    characters = json.load(f)
                    for char in characters:
                        if char.get("role") == "protagonist":
                            return char.get("name", "主角")
            except:
                pass
        return "主角"

    def get_context_for_chapter(self, chapter: int) -> str:
        """
        为章节生成上下文提示

        用于在生成章节时提供一致性约束
        """
        context_parts = []

        # 主角能力约束
        protagonist = self._get_protagonist_name()
        if protagonist in self.characters:
            char = self.characters[protagonist]
            if char.abilities:
                context_parts.append(f"【主角当前能力】{', '.join(char.abilities)}")
                context_parts.append(
                    f"注意：主角不能突然获得新能力，除非有明确剧情原因"
                )

        # 敌人威胁约束
        for enemy_name, enemy in self.enemies.items():
            if enemy.threat_level >= 7:
                context_parts.append(
                    f"【高威胁敌人】{enemy_name} 威胁等级 {enemy.threat_level}/10"
                )
                if enemy.known_weaknesses:
                    context_parts.append(
                        f"已知弱点: {', '.join(enemy.known_weaknesses)}"
                    )
                context_parts.append(f"注意：击败此敌人必须有重大代价，不能轻易取胜")

        # 最近事件
        recent_events = [e for e in self.timeline if e.chapter >= chapter - 3]
        if recent_events:
            context_parts.append("【最近事件】")
            for event in recent_events:
                context_parts.append(f"  第{event.chapter}章: {event.description}")

        return "\n".join(context_parts)
