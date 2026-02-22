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


@dataclass
class RealmState:
    """境界状态追踪"""

    current_realm: str
    first_appearance: int
    last_breakthrough_chapter: int
    breakthrough_history: List[Dict] = field(default_factory=list)

    def record_breakthrough(
        self, new_realm: str, chapter: int, days_spent: int, method: str = ""
    ):
        self.breakthrough_history.append(
            {
                "from_realm": self.current_realm,
                "to_realm": new_realm,
                "chapter": chapter,
                "days_spent": days_spent,
                "method": method,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.current_realm = new_realm
        self.last_breakthrough_chapter = chapter

    def to_dict(self) -> Dict:
        return {
            "current_realm": self.current_realm,
            "first_appearance": self.first_appearance,
            "last_breakthrough_chapter": self.last_breakthrough_chapter,
            "breakthrough_history": self.breakthrough_history,
        }


@dataclass
class ConstitutionState:
    """体质状态追踪"""

    current_constitution: str
    original_constitution: str
    changes: List[Dict] = field(default_factory=list)

    def record_change(
        self, new_constitution: str, chapter: int, reason: str, method: str
    ):
        self.changes.append(
            {
                "from": self.current_constitution,
                "to": new_constitution,
                "chapter": chapter,
                "reason": reason,
                "method": method,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.current_constitution = new_constitution

    def to_dict(self) -> Dict:
        return {
            "current_constitution": self.current_constitution,
            "original_constitution": self.original_constitution,
            "changes": self.changes,
        }


@dataclass
class LocationState:
    """地点状态追踪"""

    current_location: str
    location_history: List[Dict] = field(default_factory=list)

    def record_movement(
        self,
        new_location: str,
        chapter: int,
        travel_method: str = "",
        duration: str = "",
    ):
        self.location_history.append(
            {
                "from": self.current_location,
                "to": new_location,
                "chapter": chapter,
                "travel_method": travel_method,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.current_location = new_location

    def to_dict(self) -> Dict:
        return {
            "current_location": self.current_location,
            "location_history": self.location_history,
        }


@dataclass
class FactionState:
    """宗门/势力状态追踪"""

    current_faction: str
    faction_history: List[Dict] = field(default_factory=list)

    def record_faction_change(
        self, new_faction: str, chapter: int, reason: str, method: str = ""
    ):
        self.faction_history.append(
            {
                "from": self.current_faction,
                "to": new_faction,
                "chapter": chapter,
                "reason": reason,
                "method": method,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.current_faction = new_faction

    def to_dict(self) -> Dict:
        return {
            "current_faction": self.current_faction,
            "faction_history": self.faction_history,
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

        # 新增追踪数据（解决编辑指出的问题）
        self.realm_state: Optional[RealmState] = None  # 境界追踪
        self.constitution_state: Optional[ConstitutionState] = None  # 体质追踪
        self.location_state: Optional[LocationState] = None  # 地点追踪
        self.faction_state: Optional[FactionState] = None  # 宗门追踪

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

        if enemy.threat_level >= 6:
            if not casualties or casualties.get("deaths", 0) == 0:
                if not casualties or not any(
                    [
                        casualties.get("injuries"),
                        casualties.get("resource_cost"),
                        casualties.get("technique_sacrifice"),
                        casualties.get("cultivation_drop"),
                    ]
                ):
                    print(
                        f"⚠️ [Tracker严重警告] 敌人 {enemy_name} 威胁等级 {enemy.threat_level}/10"
                    )
                    print(f"   被击败方式: {method}")
                    print(f"   代价: {casualties or '无代价'}")
                    print(f"   ⚠️ 高威胁敌人(>=6)被轻易击败，可能造成战力崩坏！")
                    print(f"   建议：必须付出以下至少一项代价：")
                    print(f"     - 重伤/死亡（deaths/injuries）")
                    print(f"     - 大量资源消耗（resource_cost）")
                    print(f"     - 功法牺牲（technique_sacrifice）")
                    print(f"     - 修为倒退（cultivation_drop）")

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

    # 新增追踪方法（解决编辑指出的问题）

    def init_realm_tracking(self, initial_realm: str, chapter: int = 0):
        """
        初始化境界追踪

        解决问题：修炼速度坐火箭
        - 记录初始境界
        - 追踪每次突破
        """
        self.realm_state = RealmState(
            current_realm=initial_realm,
            first_appearance=chapter,
            last_breakthrough_chapter=chapter,
            breakthrough_history=[],
        )
        self._save()
        print(f"[Tracker] 初始化境界追踪: {initial_realm}")

    def track_realm_breakthrough(
        self,
        new_realm: str,
        chapter: int,
        days_spent: int,
        method: str = "",
    ):
        """
        追踪境界突破

        解决问题：修炼速度不合理
        - 记录突破所用时间
        - 检查是否突破过快
        """
        if not self.realm_state:
            self.init_realm_tracking(new_realm, chapter)
            return

        # 检查突破速度
        min_minor_days = 7
        min_major_days = 30

        if days_spent < min_minor_days:
            print(
                f"⚠️ [Tracker警告] 境界突破过快: {self.realm_state.current_realm} -> {new_realm}"
            )
            print(f"   仅用 {days_spent} 天，建议至少 {min_minor_days} 天")
        elif days_spent < min_major_days and self._is_major_realm_change(
            self.realm_state.current_realm, new_realm
        ):
            print(
                f"⚠️ [Tracker警告] 大境界突破过快: {self.realm_state.current_realm} -> {new_realm}"
            )
            print(f"   仅用 {days_spent} 天，大境界建议至少 {min_major_days} 天")

        self.realm_state.record_breakthrough(new_realm, chapter, days_spent, method)
        self._save()
        print(
            f"[Tracker] 第{chapter}章: {self.realm_state.current_realm} -> {new_realm}"
        )

    def _is_major_realm_change(self, old_realm: str, new_realm: str) -> bool:
        """判断是否为大境界变化"""
        # 简化判断：如果境界名称的"境"前部分不同，则认为是大境界变化
        old_major = old_realm.split("境")[0] if "境" in old_realm else old_realm
        new_major = new_realm.split("境")[0] if "境" in new_realm else new_realm
        return old_major != new_major

    def init_constitution_tracking(self, initial_constitution: str, chapter: int = 0):
        """
        初始化体质追踪

        解决问题：体质无理由变更（九玄剑骨→混沌剑骨）
        - 记录初始体质
        - 追踪体质变化
        """
        self.constitution_state = ConstitutionState(
            current_constitution=initial_constitution,
            original_constitution=initial_constitution,
            changes=[],
        )
        self._save()
        print(f"[Tracker] 初始化体质追踪: {initial_constitution}")

    def track_constitution_change(
        self,
        new_constitution: str,
        chapter: int,
        reason: str,
        method: str,
    ):
        """
        追踪体质变化

        解决问题：体质变更缺乏铺垫
        - 必须提供变更原因
        - 必须提供变更方式
        """
        if not self.constitution_state:
            self.init_constitution_tracking(new_constitution, chapter)
            return

        if not reason:
            print(
                f"⚠️ [Tracker严重警告] 体质变更缺乏原因: {self.constitution_state.current_constitution} -> {new_constitution}"
            )
            print(f"   必须提供体质变更的合理解释！")

        if not method:
            print(
                f"⚠️ [Tracker警告] 体质变更缺乏方式说明: {self.constitution_state.current_constitution} -> {new_constitution}"
            )

        self.constitution_state.record_change(new_constitution, chapter, reason, method)
        self._save()
        print(
            f"[Tracker] 第{chapter}章: 体质变更 {self.constitution_state.current_constitution}"
        )

    def init_location_tracking(self, initial_location: str, chapter: int = 0):
        """
        初始化地点追踪

        解决问题：地点跳跃不合理
        - 记录当前地点
        - 追踪移动过程
        """
        self.location_state = LocationState(
            current_location=initial_location, location_history=[]
        )
        self._save()
        print(f"[Tracker] 初始化地点追踪: {initial_location}")

    def track_location_change(
        self,
        new_location: str,
        chapter: int,
        travel_method: str = "",
        duration: str = "",
    ):
        """
        追踪地点变化

        解决问题：地点突然变更
        - 记录移动方式
        - 记录移动时间
        """
        if not self.location_state:
            self.init_location_tracking(new_location, chapter)
            return

        if self.location_state.current_location == new_location:
            return

        if not travel_method:
            print(
                f"⚠️ [Tracker提示] 地点变更未说明方式: {self.location_state.current_location} -> {new_location}"
            )

        if not duration:
            print(
                f"⚠️ [Tracker提示] 地点变更未说明时间: {self.location_state.current_location} -> {new_location}"
            )

        self.location_state.record_movement(
            new_location, chapter, travel_method, duration
        )
        self._save()
        print(
            f"[Tracker] 第{chapter}章: 地点变更 {self.location_state.current_location}"
        )

    def init_faction_tracking(self, initial_faction: str, chapter: int = 0):
        """
        初始化宗门追踪

        解决问题：宗门名称精神分裂
        - 记录当前宗门
        - 追踪宗门变更
        """
        self.faction_state = FactionState(
            current_faction=initial_faction, faction_history=[]
        )
        self._save()
        print(f"[Tracker] 初始化宗门追踪: {initial_faction}")

    def track_faction_change(
        self, new_faction: str, chapter: int, reason: str, method: str = ""
    ):
        """
        追踪宗门变化

        解决问题：宗门突然变更
        - 必须提供变更原因
        - 必须提供变更方式
        """
        if not self.faction_state:
            self.init_faction_tracking(new_faction, chapter)
            return

        if self.faction_state.current_faction == new_faction:
            return

        if not reason:
            print(
                f"⚠️ [Tracker严重警告] 宗门变更缺乏原因: {self.faction_state.current_faction} -> {new_faction}"
            )
            print(f"   必须提供宗门变更的合理解释！")

        self.faction_state.record_faction_change(new_faction, chapter, reason, method)
        self._save()
        print(f"[Tracker] 第{chapter}章: 宗门变更 {self.faction_state.current_faction}")

    def get_realm_progression_report(self) -> str:
        """生成境界进度报告"""
        if not self.realm_state:
            return "境界追踪未初始化"

        lines = [
            f"当前境界: {self.realm_state.current_realm}",
            f"首次出现: 第{self.realm_state.first_appearance}章",
            f"突破次数: {len(self.realm_state.breakthrough_history)}",
            "\n突破历史:",
        ]

        for record in self.realm_state.breakthrough_history:
            lines.append(
                f"  第{record['chapter']}章: {record['from_realm']} -> {record['to_realm']} "
                f"(用时{record['days_spent']}天)"
            )

        return "\n".join(lines)

    def get_constitution_change_report(self) -> str:
        """生成体质变更报告"""
        if not self.constitution_state:
            return "体质追踪未初始化"

        lines = [
            f"原始体质: {self.constitution_state.original_constitution}",
            f"当前体质: {self.constitution_state.current_constitution}",
            f"变更次数: {len(self.constitution_state.changes)}",
            "\n变更历史:",
        ]

        for change in self.constitution_state.changes:
            lines.append(
                f"  第{change['chapter']}章: {change['from']} -> {change['to']}\n"
                f"    原因: {change['reason']}\n    方式: {change['method']}"
            )

        return "\n".join(lines)

    def get_full_tracking_report(self) -> str:
        """生成完整追踪报告"""
        lines = ["=" * 60, "完整设定追踪报告", "=" * 60]

        # 境界
        if self.realm_state:
            lines.extend(["\n【境界追踪】", self.get_realm_progression_report()])

        # 体质
        if self.constitution_state:
            lines.extend(["\n【体质追踪】", self.get_constitution_change_report()])

        # 地点
        if self.location_state:
            lines.extend(
                [
                    "\n【地点追踪】",
                    f"当前地点: {self.location_state.current_location}",
                    f"移动次数: {len(self.location_state.location_history)}",
                ]
            )

        # 宗门
        if self.faction_state:
            lines.extend(
                [
                    "\n【宗门追踪】",
                    f"当前宗门: {self.faction_state.current_faction}",
                    f"变更次数: {len(self.faction_state.faction_history)}",
                ]
            )

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def check_consistency(self, chapter: int, content: str) -> Dict[str, Any]:
        """
        检查章节内容的一致性

        Returns:
            检查结果，包含问题列表
        """
        issues = []
        warnings = []

        protagonist = self._get_protagonist_name()
        if protagonist in self.characters:
            char = self.characters[protagonist]
            if len(char.abilities) > 4:
                issues.append(
                    {
                        "type": "ability_bloat",
                        "message": f"主角能力过多：{len(char.abilities)} 个（上限4个）: {', '.join(char.abilities)}",
                        "suggestion": "必须合并相似能力或删除冗余能力，主角核心能力不能超过4个",
                    }
                )

        for enemy_name, enemy in self.enemies.items():
            if enemy.threat_level >= 6 and len(enemy.defeats) > 0:
                last_defeat = enemy.defeats[-1]
                casualties = last_defeat.get("casualties", {}) or {}
                has_cost = any(
                    [
                        casualties.get("deaths", 0) > 0,
                        casualties.get("injuries"),
                        casualties.get("resource_cost"),
                        casualties.get("technique_sacrifice"),
                        casualties.get("cultivation_drop"),
                    ]
                )
                if not has_cost:
                    issues.append(
                        {
                            "type": "power_scaling_issue",
                            "message": f"高威胁敌人 {enemy_name} (威胁{enemy.threat_level}/10, >=6为高威胁) 被无代价击败",
                            "suggestion": "必须增加战斗代价或削弱敌人初始设定",
                        }
                    )

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
