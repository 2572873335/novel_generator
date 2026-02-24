"""
World Bible - 事件溯源存储
事件驱动状态机，记录所有关键事件用于一致性检查

解决：时间线混乱、战力崩坏、人物状态丢失等问题
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型枚举"""
    # 角色相关
    CHARACTER_DEATH = "CHARACTER_DEATH"
    CHARACTER_REBIRTH = "CHARACTER_REBIRTH"
    CHARACTER_INJURY = "CHARACTER_INJURY"
    CHARACTER_RECOVERY = "CHARACTER_RECOVERY"
    CHARACTER_POWER_CHANGE = "CHARACTER_POWER_CHANGE"
    CHARACTER_RELATIONSHIP = "CHARACTER_RELATIONSHIP"
    CHARACTER_STATUS = "CHARACTER_STATUS"  # 喜怒哀乐等状态

    # 修炼/战力相关
    REALM_UPGRADE = "REALM_UPGRADE"
    REALM_DOWNGRADE = "REALM_DOWNGRADE"
    POWER_BREAKTHROUGH = "POWER_BREAKTHROUGH"
    TECHNIQUE_LEARNED = "TECHNIQUE_LEARNED"
    WEAPON_OBTAINED = "WEAPON_OBTAINED"

    # 势力相关
    FACTION_ESTABLISHED = "FACTION_ESTABLISHED"
    FACTION_DESTROYED = "FACTION_DESTROYED"
    FACTION_ALLIANCE = "FACTION_ALLIANCE"
    FACTION_WAR = "FACTION_WAR"

    # 世界观相关
    WORLD_EVENT = "WORLD_EVENT"
    REVELATION = "REVELATION"  # 重大秘密揭露
    TIMELINE_MARKER = "TIMELINE_MARKER"

    # 物品/资源
    TREASURE_OBTAINED = "TREASURE_OBTAINED"
    TREASURE_LOST = "TREASURE_LOST"
    RESOURCE_CHANGE = "RESOURCE_CHANGE"

    # 情绪/情节
    EMOTION_SHIFT = "EMOTION_SHIFT"
    PLOT_REVERSAL = "PLOT_REVERSAL"
    CLIFFHANGER = "CLIFFHANGER"


@dataclass
class Event:
    """事件结构"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: str = ""
    chapter: int = 0

    # 涉及实体
    entity_id: str = ""  # 角色/势力ID
    entity_name: str = ""  # 实体名称（冗余存储便于调试）

    # 事件详情
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    # 情绪向量（用于情绪追踪）
    emotional_impact: float = 0.0  # 正数=爽点，负数=压抑

    # 时间戳
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 溯源信息
    source_chapter: int = 0  # 事件首次出现的章节
    is_reversed: bool = False  # 是否被反转（如复活）
    reversal_event_id: str = ""  # 反转事件ID

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "chapter": self.chapter,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "description": self.description,
            "details": self.details,
            "emotional_impact": self.emotional_impact,
            "timestamp": self.timestamp,
            "source_chapter": self.source_chapter,
            "is_reversed": self.is_reversed,
            "reversal_event_id": self.reversal_event_id
        }


class WorldBible:
    """
    世界圣经 - 事件溯源存储

    核心功能：
    1. 记录所有关键事件
    2. 事件溯源查询
    3. 时间线一致性检查
    4. 战力/状态追踪

    设计原则：
    - 只记录关键事件，不过度详细
    - 支持事件反转（如角色复活）
    - 轻量级查询，不加载全部历史
    """

    # 关键事件类型 - 只有这些类型的事件会被记录
    KEY_EVENT_TYPES = {
        EventType.CHARACTER_DEATH,
        EventType.CHARACTER_REBIRTH,
        EventType.REALM_UPGRADE,
        EventType.REALM_DOWNGRADE,
        EventType.POWER_BREAKTHROUGH,
        EventType.FACTION_DESTROYED,
        EventType.FACTION_WAR,
        EventType.REVELATION,
        EventType.PLOT_REVERSAL,
    }

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.bible_file = self.project_dir / "world_bible.json"

        # 事件索引
        self.events: List[Event] = []

        # 实体索引: entity_id -> [event_ids]
        self.entity_index: Dict[str, List[str]] = {}

        # 类型索引: event_type -> [event_ids]
        self.type_index: Dict[str, List[str]] = {}

        # 加载已有圣经
        self._load_bible()

    def _load_bible(self):
        """加载已有圣经"""
        if self.bible_file.exists():
            try:
                data = json.loads(self.bible_file.read_text(encoding="utf-8"))
                self.events = [Event(**e) for e in data.get("events", [])]
                self._rebuild_indexes()
                logger.info(f"Loaded world bible with {len(self.events)} events")
            except Exception as e:
                logger.warning(f"Failed to load world bible: {e}")

    def _save_bible(self):
        """保存圣经"""
        data = {
            "events": [e.to_dict() for e in self.events],
            "entity_index": self.entity_index,
            "type_index": self.type_index,
            "last_updated": datetime.now().isoformat()
        }
        self.bible_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _rebuild_indexes(self):
        """重建索引"""
        self.entity_index = {}
        self.type_index = {}

        for event in self.events:
            # 实体索引
            if event.entity_id:
                if event.entity_id not in self.entity_index:
                    self.entity_index[event.entity_id] = []
                self.entity_index[event.entity_id].append(event.event_id)

            # 类型索引
            if event.event_type not in self.type_index:
                self.type_index[event.event_type] = []
            self.type_index[event.event_type].append(event.event_id)

    def record_event(self, event: Event) -> str:
        """
        记录事件

        Args:
            event: 事件对象

        Returns:
            event_id: 事件ID
        """
        # 检查是否需要记录（非关键事件可能跳过）
        try:
            event_type_enum = EventType(event.event_type)
            if event_type_enum not in self.KEY_EVENT_TYPES:
                logger.debug(f"Skipping non-key event: {event.event_type}")
        except ValueError:
            pass  # 自定义事件类型

        # 设置源章节（如果是首次记录）
        if event.source_chapter == 0:
            event.source_chapter = event.chapter

        # 添加到事件列表
        self.events.append(event)

        # 更新索引
        if event.entity_id:
            if event.entity_id not in self.entity_index:
                self.entity_index[event.entity_id] = []
            self.entity_index[event.entity_id].append(event.event_id)

        if event.event_type not in self.type_index:
            self.type_index[event.event_type] = []
        self.type_index[event.event_type].append(event.event_id)

        # 保存
        self._save_bible()

        logger.info(f"Recorded event: {event.event_type} - {event.description[:50]}")

        return event.event_id

    def get_entity_events(self, entity_id: str, limit: int = 20) -> List[Event]:
        """获取实体的所有事件（按时间倒序）"""
        event_ids = self.entity_index.get(entity_id, [])
        events = [e for e in self.events if e.event_id in event_ids]
        return events[-limit:][::-1]  # 倒序

    def get_entity_latest_state(self, entity_id: str) -> Optional[Event]:
        """获取实体最新状态"""
        events = self.get_entity_events(entity_id, limit=1)
        return events[0] if events else None

    def get_events_by_type(self, event_type: str, limit: int = 20) -> List[Event]:
        """获取指定类型的事件"""
        event_ids = self.type_index.get(event_type, [])
        events = [e for e in self.events if e.event_id in event_ids]
        return events[-limit:][::-1]

    def get_chapter_events(self, chapter: int) -> List[Event]:
        """获取指定章节的事件"""
        return [e for e in self.events if e.chapter == chapter]

    def check_consistency_violations(self, new_text: str, chapter: int) -> List[Dict[str, Any]]:
        """
        检查一致性违规

        Args:
            new_text: 新章节文本
            chapter: 章节编号

        Returns:
            违规列表
        """
        violations = []

        # 检查角色死亡/复活一致性
        death_events = self.get_events_by_type(EventType.CHARACTER_DEATH.value)
        for death_event in death_events:
            # 检查该角色是否有复活事件
            entity_events = self.get_entity_events(death_event.entity_id)
            has_rebirth = any(
                e.event_type == EventType.CHARACTER_REBIRTH.value and
                e.source_chapter > death_event.source_chapter
                for e in entity_events
            )

            # 如果有复活，说明角色还活着
            if has_rebirth:
                # 检查新文本是否提到角色已死（复活后不应再死）
                if death_event.entity_name in new_text:
                    # 简单检查：如果提到角色死亡相关描述
                    death_mentions = ["已死", "死了", "死亡", "去世", "陨落"]
                    if any(m in new_text for m in death_mentions):
                        violations.append({
                            "type": "character_resurrection_inconsistency",
                            "severity": "critical",
                            "entity": death_event.entity_name,
                            "message": "角色已复活，不应在文本中再次出现死亡描述",
                            "death_chapter": death_event.chapter,
                            "suggestion": "删除角色死亡相关描述"
                        })

        # 检查战力升级一致性
        upgrade_events = self.get_events_by_type(EventType.REALM_UPGRADE.value)
        for upgrade_event in upgrade_events:
            if upgrade_event.chapter >= chapter - 1:  # 刚升级就降级
                downgrade_events = self.get_entity_events(upgrade_event.entity_id)
                for down in downgrade_events:
                    if down.event_type == EventType.REALM_DOWNGRADE.value:
                        if down.chapter > upgrade_event.chapter and down.chapter < chapter:
                            violations.append({
                                "type": "realm_downgrade_inconsistency",
                                "severity": "warning",
                                "entity": upgrade_event.entity_name,
                                "message": "境界刚升级就降级",
                                "suggestion": "确认境界变化符合逻辑"
                            })

        return violations

    def get_timeline_summary(self, entity_id: str = None) -> str:
        """
        获取时间线摘要（用于Prompt）

        Args:
            entity_id: 可选，指定实体

        Returns:
            格式化的文本摘要
        """
        if entity_id:
            events = self.get_entity_events(entity_id)
            entity_name = events[0].entity_name if events else entity_id
            title = f"【{entity_name}】时间线"
        else:
            events = self.events[-50:]  # 最近50个事件
            title = "【世界】时间线"

        if not events:
            return f"{title}\n暂无记录"

        lines = [title]
        for e in events:
            reversal_mark = " [已反转]" if e.is_reversed else ""
            lines.append(f"  第{e.chapter}章: {e.event_type} - {e.description[:30]}{reversal_mark}")

        return "\n".join(lines)

    def create_event(
        self,
        event_type: str,
        chapter: int,
        entity_id: str,
        entity_name: str,
        description: str,
        details: Dict[str, Any] = None,
        emotional_impact: float = 0.0
    ) -> Event:
        """创建并记录事件"""
        event = Event(
            event_type=event_type,
            chapter=chapter,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            details=details or {},
            emotional_impact=emotional_impact
        )
        return self.record_event(event)

    def reverse_event(self, event_id: str, reversal_event_id: str):
        """反转事件（如角色复活）"""
        for event in self.events:
            if event.event_id == event_id:
                event.is_reversed = True
                event.reversal_event_id = reversal_event_id
                break
        self._save_bible()

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_events": len(self.events),
            "entity_count": len(self.entity_index),
            "type_distribution": {
                et: len(eids) for et, eids in self.type_index.items()
            },
            "latest_chapter": max((e.chapter for e in self.events), default=0)
        }
