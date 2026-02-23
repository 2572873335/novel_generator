"""
状态快照管理器 (L4)
用于捕获小说世界的完整状态快照，支持状态查询、差异比较和回滚功能

核心功能：
1. 在章节边界捕获完整世界状态
2. 支持"第X章状态"查询
3. 实现快照间差异比较
4. 添加时间线回滚能力
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import sqlite3
from pathlib import Path
import hashlib
from enum import Enum


class SnapshotType(Enum):
    """快照类型枚举"""

    CHAPTER_END = "chapter_end"  # 章节结束
    MAJOR_EVENT = "major_event"  # 重大事件
    CHECKPOINT = "checkpoint"  # 检查点
    ROLLBACK_POINT = "rollback_point"  # 回滚点


@dataclass
class WorldState:
    """
    世界状态数据结构

    Attributes:
        chapter: 章节号
        timestamp: 时间戳
        characters: 角色状态字典
        locations: 地点状态字典
        factions: 势力状态字典
        items: 物品状态字典
        plot_points: 情节点状态
        metadata: 额外元数据
    """

    chapter: int
    timestamp: datetime
    characters: Dict[str, Any] = field(default_factory=dict)
    locations: Dict[str, Any] = field(default_factory=dict)
    factions: Dict[str, Any] = field(default_factory=dict)
    items: Dict[str, Any] = field(default_factory=dict)
    plot_points: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldState":
        """从字典创建实例"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def calculate_hash(self) -> str:
        """计算状态哈希值（用于快速比较）"""
        state_str = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.md5(state_str.encode("utf-8")).hexdigest()


@dataclass
class StateSnapshot:
    """
    状态快照实体

    Attributes:
        id: 快照唯一标识符
        snapshot_type: 快照类型
        chapter: 章节号
        description: 快照描述
        world_state: 世界状态
        parent_snapshot_id: 父快照ID（用于构建快照树）
        tags: 标签集合
        metadata: 额外元数据
        created_at: 创建时间戳
    """

    id: str
    snapshot_type: SnapshotType
    chapter: int
    description: str
    world_state: WorldState
    parent_snapshot_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["snapshot_type"] = self.snapshot_type.value
        data["world_state"] = self.world_state.to_dict()
        data["tags"] = list(self.tags)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateSnapshot":
        """从字典创建实例"""
        data["snapshot_type"] = SnapshotType(data["snapshot_type"])
        data["world_state"] = WorldState.from_dict(data["world_state"])
        data["tags"] = set(data.get("tags", []))
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class StateDiff:
    """
    状态差异分析器
    """

    def __init__(self, snapshot_a: StateSnapshot, snapshot_b: StateSnapshot):
        self.snapshot_a = snapshot_a
        self.snapshot_b = snapshot_b
        self.diff_result = self._calculate_diff()

    def _calculate_diff(self) -> Dict[str, Any]:
        """计算两个快照间的差异"""
        state_a = self.snapshot_a.world_state
        state_b = self.snapshot_b.world_state

        diff = {
            "summary": {
                "from_chapter": state_a.chapter,
                "to_chapter": state_b.chapter,
                "chapter_diff": state_b.chapter - state_a.chapter,
                "state_hash_changed": state_a.calculate_hash()
                != state_b.calculate_hash(),
            },
            "characters": self._diff_dicts(
                state_a.characters, state_b.characters, "characters"
            ),
            "locations": self._diff_dicts(
                state_a.locations, state_b.locations, "locations"
            ),
            "factions": self._diff_dicts(
                state_a.factions, state_b.factions, "factions"
            ),
            "items": self._diff_dicts(state_a.items, state_b.items, "items"),
            "plot_points": self._diff_dicts(
                state_a.plot_points, state_b.plot_points, "plot_points"
            ),
        }

        return diff

    def _diff_dicts(
        self, dict_a: Dict[str, Any], dict_b: Dict[str, Any], category: str
    ) -> Dict[str, Any]:
        """比较两个字典的差异"""
        keys_a = set(dict_a.keys())
        keys_b = set(dict_b.keys())

        added = keys_b - keys_a
        removed = keys_a - keys_b
        common = keys_a & keys_b

        changed = {}
        for key in common:
            if dict_a[key] != dict_b[key]:
                changed[key] = {"from": dict_a[key], "to": dict_b[key]}

        return {
            "added": {k: dict_b[k] for k in added},
            "removed": {k: dict_a[k] for k in removed},
            "changed": changed,
            "total_before": len(dict_a),
            "total_after": len(dict_b),
        }

    def get_summary(self) -> str:
        """获取差异摘要"""
        diff = self.diff_result
        summary = []

        if diff["summary"]["state_hash_changed"]:
            summary.append(
                f"状态已改变（第{diff['summary']['from_chapter']}章 → 第{diff['summary']['to_chapter']}章）"
            )

        for category in ["characters", "locations", "factions", "items", "plot_points"]:
            cat_diff = diff[category]
            if cat_diff["added"] or cat_diff["removed"] or cat_diff["changed"]:
                changes = []
                if cat_diff["added"]:
                    changes.append(f"新增{len(cat_diff['added'])}个")
                if cat_diff["removed"]:
                    changes.append(f"移除{len(cat_diff['removed'])}个")
                if cat_diff["changed"]:
                    changes.append(f"变更{len(cat_diff['changed'])}个")

                if changes:
                    summary.append(f"{category}: {', '.join(changes)}")

        return "; ".join(summary) if summary else "无显著变化"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.diff_result


class StateSnapshotManager:
    """
    状态快照管理器主类
    """

    def __init__(self, project_path: str):
        """
        初始化状态快照管理器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.db_path = self.project_path / "state_snapshots.db"
        self._init_database()

    def _init_database(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建快照表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY,
                    snapshot_type TEXT NOT NULL,
                    chapter INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    world_state TEXT NOT NULL,  -- JSON
                    parent_snapshot_id TEXT,
                    tags TEXT,  -- JSON数组
                    metadata TEXT,  -- JSON对象
                    created_at TEXT NOT NULL
                )
            """)

            # 创建索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_chapter ON snapshots(chapter)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_type ON snapshots(snapshot_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_parent ON snapshots(parent_snapshot_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_created ON snapshots(created_at)"
            )

            conn.commit()

    def create_snapshot(
        self,
        snapshot_type: SnapshotType,
        chapter: int,
        description: str,
        world_state: WorldState,
        parent_snapshot_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        创建状态快照

        Args:
            snapshot_type: 快照类型
            chapter: 章节号
            description: 快照描述
            world_state: 世界状态
            parent_snapshot_id: 父快照ID
            tags: 标签列表
            metadata: 额外元数据

        Returns:
            快照ID
        """
        snapshot_id = f"snapshot_{chapter}_{datetime.now().timestamp()}"

        snapshot = StateSnapshot(
            id=snapshot_id,
            snapshot_type=snapshot_type,
            chapter=chapter,
            description=description,
            world_state=world_state,
            parent_snapshot_id=parent_snapshot_id,
            tags=set(tags or []),
            metadata=metadata or {},
            created_at=datetime.now(),
        )

        self._save_snapshot(snapshot)
        return snapshot_id

    def _save_snapshot(self, snapshot: StateSnapshot) -> None:
        """保存快照到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO snapshots 
                (id, snapshot_type, chapter, description, world_state, 
                 parent_snapshot_id, tags, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot.id,
                    snapshot.snapshot_type.value,
                    snapshot.chapter,
                    snapshot.description,
                    json.dumps(snapshot.world_state.to_dict(), ensure_ascii=False),
                    snapshot.parent_snapshot_id,
                    json.dumps(list(snapshot.tags)),
                    json.dumps(snapshot.metadata),
                    snapshot.created_at.isoformat(),
                ),
            )

            conn.commit()

    def get_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """获取快照"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM snapshots WHERE id = ?", (snapshot_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_snapshot(row)

    def _row_to_snapshot(self, row) -> StateSnapshot:
        """将数据库行转换为StateSnapshot对象"""
        return StateSnapshot(
            id=row[0],
            snapshot_type=SnapshotType(row[1]),
            chapter=row[2],
            description=row[3],
            world_state=WorldState.from_dict(json.loads(row[4])),
            parent_snapshot_id=row[5],
            tags=set(json.loads(row[6]) if row[6] else []),
            metadata=json.loads(row[7]) if row[7] else {},
            created_at=datetime.fromisoformat(row[8]),
        )

    def get_snapshots_by_chapter(self, chapter: int) -> List[StateSnapshot]:
        """获取指定章节的所有快照"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM snapshots 
                WHERE chapter = ? 
                ORDER BY created_at
            """,
                (chapter,),
            )

            rows = cursor.fetchall()
            return [self._row_to_snapshot(row) for row in rows]

    def get_latest_snapshot_before(self, chapter: int) -> Optional[StateSnapshot]:
        """获取指定章节之前的最新快照"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM snapshots 
                WHERE chapter <= ? 
                ORDER BY chapter DESC, created_at DESC 
                LIMIT 1
            """,
                (chapter,),
            )

            row = cursor.fetchone()
            return self._row_to_snapshot(row) if row else None

    def get_snapshots_in_range(
        self, start_chapter: int, end_chapter: int
    ) -> List[StateSnapshot]:
        """获取章节范围内的所有快照"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM snapshots 
                WHERE chapter BETWEEN ? AND ? 
                ORDER BY chapter, created_at
            """,
                (start_chapter, end_chapter),
            )

            rows = cursor.fetchall()
            return [self._row_to_snapshot(row) for row in rows]

    def get_snapshot_timeline(self) -> List[Tuple[int, List[StateSnapshot]]]:
        """获取快照时间线（按章节分组）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT chapter, COUNT(*) as count 
                FROM snapshots 
                GROUP BY chapter 
                ORDER BY chapter
            """)

            timeline = []
            for row in cursor.fetchall():
                chapter = row[0]
                snapshots = self.get_snapshots_by_chapter(chapter)
                timeline.append((chapter, snapshots))

            return timeline

    def compare_snapshots(
        self, snapshot_id_a: str, snapshot_id_b: str
    ) -> Optional[StateDiff]:
        """比较两个快照"""
        snapshot_a = self.get_snapshot(snapshot_id_a)
        snapshot_b = self.get_snapshot(snapshot_id_b)

        if not snapshot_a or not snapshot_b:
            return None

        return StateDiff(snapshot_a, snapshot_b)

    def compare_chapters(self, chapter_a: int, chapter_b: int) -> Optional[StateDiff]:
        """比较两个章节的状态"""
        snapshot_a = self.get_latest_snapshot_before(chapter_a)
        snapshot_b = self.get_latest_snapshot_before(chapter_b)

        if not snapshot_a or not snapshot_b:
            return None

        return StateDiff(snapshot_a, snapshot_b)

    def create_rollback_point(
        self, chapter: int, description: str, world_state: WorldState
    ) -> str:
        """
        创建回滚点

        Args:
            chapter: 章节号
            description: 描述
            world_state: 世界状态

        Returns:
            回滚点ID
        """
        return self.create_snapshot(
            snapshot_type=SnapshotType.ROLLBACK_POINT,
            chapter=chapter,
            description=description,
            world_state=world_state,
            tags=["rollback"],
        )

    def rollback_to_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        回滚到指定快照

        Args:
            snapshot_id: 目标快照ID

        Returns:
            回滚结果
        """
        target_snapshot = self.get_snapshot(snapshot_id)
        if not target_snapshot:
            return {"success": False, "error": "快照不存在"}

        if target_snapshot.snapshot_type != SnapshotType.ROLLBACK_POINT:
            return {"success": False, "error": "只能回滚到回滚点"}

        # 创建当前状态的快照（用于可能的恢复）
        current_snapshot = self.get_latest_snapshot_before(999999)  # 获取最新快照
        if current_snapshot:
            backup_id = self.create_snapshot(
                snapshot_type=SnapshotType.CHECKPOINT,
                chapter=current_snapshot.chapter,
                description=f"回滚前备份: {current_snapshot.description}",
                world_state=current_snapshot.world_state,
                tags=["rollback_backup"],
                metadata={"rollback_from": snapshot_id},
            )
        else:
            backup_id = None

        # 创建回滚后的新快照
        rollback_snapshot_id = self.create_snapshot(
            snapshot_type=SnapshotType.CHECKPOINT,
            chapter=target_snapshot.chapter,
            description=f"回滚到: {target_snapshot.description}",
            world_state=target_snapshot.world_state,
            parent_snapshot_id=snapshot_id,
            tags=["rolled_back"],
            metadata={
                "rollback_source": snapshot_id,
                "backup_snapshot": backup_id,
                "rollback_time": datetime.now().isoformat(),
            },
        )

        return {
            "success": True,
            "rollback_to": snapshot_id,
            "rollback_snapshot": rollback_snapshot_id,
            "backup_snapshot": backup_id,
            "target_chapter": target_snapshot.chapter,
        }

    def export_snapshots(self, filepath: str) -> None:
        """导出所有快照到JSON文件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM snapshots ORDER BY chapter, created_at")
            rows = cursor.fetchall()

            snapshots = [self._row_to_snapshot(row).to_dict() for row in rows]

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(snapshots, f, ensure_ascii=False, indent=2)

    def import_snapshots(self, filepath: str) -> int:
        """从JSON文件导入快照"""
        with open(filepath, "r", encoding="utf-8") as f:
            snapshots_data = json.load(f)

        count = 0
        for snapshot_data in snapshots_data:
            snapshot = StateSnapshot.from_dict(snapshot_data)
            self._save_snapshot(snapshot)
            count += 1

        return count

    def analyze_state_changes(
        self, start_chapter: int, end_chapter: int
    ) -> Dict[str, Any]:
        """
        分析状态变化

        Args:
            start_chapter: 起始章节
            end_chapter: 结束章节

        Returns:
            变化分析结果
        """
        snapshots = self.get_snapshots_in_range(start_chapter, end_chapter)
        if len(snapshots) < 2:
            return {"error": "需要至少两个快照进行分析"}

        # 按章节分组
        chapter_snapshots = {}
        for snapshot in snapshots:
            if snapshot.chapter not in chapter_snapshots:
                chapter_snapshots[snapshot.chapter] = []
            chapter_snapshots[snapshot.chapter].append(snapshot)

        # 计算章节间变化
        chapters = sorted(chapter_snapshots.keys())
        chapter_diffs = []

        for i in range(len(chapters) - 1):
            chapter_a = chapters[i]
            chapter_b = chapters[i + 1]

            # 使用每个章节的最新快照
            snapshot_a = chapter_snapshots[chapter_a][-1]
            snapshot_b = chapter_snapshots[chapter_b][-1]

            diff = StateDiff(snapshot_a, snapshot_b)
            chapter_diffs.append(
                {
                    "from_chapter": chapter_a,
                    "to_chapter": chapter_b,
                    "diff_summary": diff.get_summary(),
                    "has_changes": diff.diff_result["summary"]["state_hash_changed"],
                }
            )

        # 统计变化频率
        total_changes = sum(1 for d in chapter_diffs if d["has_changes"])
        change_frequency = total_changes / len(chapter_diffs) if chapter_diffs else 0

        return {
            "total_snapshots": len(snapshots),
            "chapters_covered": len(chapter_snapshots),
            "chapter_diffs": chapter_diffs,
            "total_changes": total_changes,
            "change_frequency": change_frequency,
            "most_changed_category": self._find_most_changed_category(snapshots),
        }

    def _find_most_changed_category(self, snapshots: List[StateSnapshot]) -> str:
        """找出变化最多的状态类别"""
        if len(snapshots) < 2:
            return "unknown"

        category_changes = {
            "characters": 0,
            "locations": 0,
            "factions": 0,
            "items": 0,
            "plot_points": 0,
        }

        for i in range(len(snapshots) - 1):
            diff = StateDiff(snapshots[i], snapshots[i + 1])
            diff_dict = diff.diff_result

            for category in category_changes.keys():
                cat_diff = diff_dict[category]
                if cat_diff["added"] or cat_diff["removed"] or cat_diff["changed"]:
                    category_changes[category] += 1

        return max(category_changes.items(), key=lambda x: x[1])[0]


# 工具函数
def create_chapter_end_snapshot(
    manager: StateSnapshotManager,
    chapter: int,
    world_state: WorldState,
    description: Optional[str] = None,
) -> str:
    """创建章节结束快照"""
    if description is None:
        description = f"第{chapter}章结束状态"

    return manager.create_snapshot(
        snapshot_type=SnapshotType.CHAPTER_END,
        chapter=chapter,
        description=description,
        world_state=world_state,
        tags=["chapter_end", f"chapter_{chapter}"],
    )


def create_major_event_snapshot(
    manager: StateSnapshotManager,
    chapter: int,
    event_name: str,
    world_state: WorldState,
    event_details: Dict[str, Any],
) -> str:
    """创建重大事件快照"""
    return manager.create_snapshot(
        snapshot_type=SnapshotType.MAJOR_EVENT,
        chapter=chapter,
        description=f"重大事件: {event_name}",
        world_state=world_state,
        tags=["major_event", event_name.lower().replace(" ", "_")],
        metadata={"event_details": event_details},
    )


if __name__ == "__main__":
    # 简单测试
    manager = StateSnapshotManager(".")

    # 创建测试状态
    world_state_1 = WorldState(
        chapter=1,
        timestamp=datetime.now(),
        characters={"主角": {"境界": "炼气期", "位置": "青云宗"}},
        locations={"青云宗": {"类型": "宗门", "状态": "和平"}},
        factions={"青云宗": {"宗主": "青云子", "势力": "正道"}},
    )

    world_state_2 = WorldState(
        chapter=10,
        timestamp=datetime.now(),
        characters={
            "主角": {"境界": "筑基期", "位置": "青云宗"},
            "反派": {"境界": "金丹期", "位置": "魔教"},
        },
        locations={
            "青云宗": {"类型": "宗门", "状态": "和平"},
            "魔教": {"类型": "宗门", "状态": "敌对"},
        },
        factions={
            "青云宗": {"宗主": "青云子", "势力": "正道"},
            "魔教": {"教主": "魔尊", "势力": "魔道"},
        },
    )

    # 创建快照
    snapshot_id_1 = create_chapter_end_snapshot(manager, 1, world_state_1)
    snapshot_id_2 = create_chapter_end_snapshot(manager, 10, world_state_2)

    print(f"创建快照: {snapshot_id_1}, {snapshot_id_2}")

    # 比较快照
    diff = manager.compare_snapshots(snapshot_id_1, snapshot_id_2)
    if diff:
        print(f"状态差异: {diff.get_summary()}")

    # 获取时间线
    timeline = manager.get_snapshot_timeline()
    print(f"时间线章节数: {len(timeline)}")
