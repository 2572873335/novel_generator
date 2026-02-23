"""
期待感追踪系统
用于追踪小说中的承诺、伏笔、信息差和能力成长预期

核心功能：
1. 追踪读者面向承诺（"三年之约"、伏笔）
2. 追踪信息差（读者知道但主角不知道）
3. 追踪能力成长预期（金手指升级节奏）
4. 验证承诺兑现情况
5. 发出逾期承诺警告
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import sqlite3
from pathlib import Path


class ExpectationType(Enum):
    """期待类型枚举"""

    PROMISE = "promise"  # 明确承诺（"三年之约"）
    FORESHADOWING = "foreshadowing"  # 伏笔暗示
    INFORMATION_GAP = "information_gap"  # 信息差（读者知道主角不知道）
    ABILITY_GROWTH = "ability_growth"  # 能力成长预期
    PLOT_HOOK = "plot_hook"  # 情节钩子


class ExpectationStatus(Enum):
    """期待状态枚举"""

    PENDING = "pending"  # 待兑现
    FULFILLED = "fulfilled"  # 已兑现
    OVERDUE = "overdue"  # 逾期未兑现
    CANCELLED = "cancelled"  # 已取消（情节变化导致无效）


@dataclass
class Expectation:
    """
    期待感实体，表示一个需要追踪的承诺或预期

    Attributes:
        id: 期待唯一标识符
        expectation_type: 期待类型
        title: 期待标题（简短描述）
        description: 详细描述
        setup_chapter: 设置章节（承诺/伏笔出现的章节）
        due_chapter: 预期兑现章节（None表示无明确期限）
        fulfilled_chapter: 实际兑现章节（None表示未兑现）
        status: 当前状态
        tags: 标签集合（用于分类和检索）
        metadata: 额外元数据
        created_at: 创建时间戳
        updated_at: 最后更新时间戳
    """

    id: str
    expectation_type: ExpectationType
    title: str
    description: str
    setup_chapter: int
    due_chapter: Optional[int] = None
    fulfilled_chapter: Optional[int] = None
    status: ExpectationStatus = ExpectationStatus.PENDING
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_overdue(self, current_chapter: int) -> bool:
        """检查期待是否逾期"""
        if self.status == ExpectationStatus.FULFILLED:
            return False
        if self.due_chapter is None:
            return False
        return current_chapter > self.due_chapter

    def update_status(self, current_chapter: int) -> None:
        """根据当前章节更新状态"""
        if self.status == ExpectationStatus.FULFILLED:
            return

        if self.is_overdue(current_chapter):
            self.status = ExpectationStatus.OVERDUE
        else:
            self.status = ExpectationStatus.PENDING

        self.updated_at = datetime.now()

    def mark_fulfilled(self, chapter: int, notes: str = "") -> None:
        """标记为已兑现"""
        self.status = ExpectationStatus.FULFILLED
        self.fulfilled_chapter = chapter
        self.metadata["fulfillment_notes"] = notes
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换特殊类型
        data["expectation_type"] = self.expectation_type.value
        data["status"] = self.status.value
        data["tags"] = list(self.tags)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expectation":
        """从字典创建实例"""
        # 转换特殊类型
        data["expectation_type"] = ExpectationType(data["expectation_type"])
        data["status"] = ExpectationStatus(data["status"])
        data["tags"] = set(data.get("tags", []))
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class ExpectationTracker:
    """
    期待感追踪器主类

    提供期待感的增删改查、状态更新、逾期检测等功能
    """

    def __init__(self, project_path: str):
        """
        初始化期待感追踪器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.db_path = self.project_path / "expectations.db"
        self._init_database()

    def _init_database(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建期待表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expectations (
                    id TEXT PRIMARY KEY,
                    expectation_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    setup_chapter INTEGER NOT NULL,
                    due_chapter INTEGER,
                    fulfilled_chapter INTEGER,
                    status TEXT NOT NULL,
                    tags TEXT,  -- JSON数组
                    metadata TEXT,  -- JSON对象
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 创建索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_status ON expectations(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_setup_chapter ON expectations(setup_chapter)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_due_chapter ON expectations(due_chapter)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_type ON expectations(expectation_type)"
            )

            conn.commit()

    def add_expectation(self, expectation: Expectation) -> str:
        """
        添加期待

        Args:
            expectation: 期待对象

        Returns:
            期待ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO expectations 
                (id, expectation_type, title, description, setup_chapter, due_chapter, 
                 fulfilled_chapter, status, tags, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    expectation.id,
                    expectation.expectation_type.value,
                    expectation.title,
                    expectation.description,
                    expectation.setup_chapter,
                    expectation.due_chapter,
                    expectation.fulfilled_chapter,
                    expectation.status.value,
                    json.dumps(list(expectation.tags)),
                    json.dumps(expectation.metadata),
                    expectation.created_at.isoformat(),
                    expectation.updated_at.isoformat(),
                ),
            )

            conn.commit()

        return expectation.id

    def get_expectation(self, expectation_id: str) -> Optional[Expectation]:
        """获取期待"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM expectations WHERE id = ?", (expectation_id,))
            row = cursor.fetchone()

            if not row:
                return None

            # 解析数据库行
            return self._row_to_expectation(row)

    def _row_to_expectation(self, row) -> Expectation:
        """将数据库行转换为Expectation对象"""
        return Expectation(
            id=row[0],
            expectation_type=ExpectationType(row[1]),
            title=row[2],
            description=row[3],
            setup_chapter=row[4],
            due_chapter=row[5],
            fulfilled_chapter=row[6],
            status=ExpectationStatus(row[7]),
            tags=set(json.loads(row[8]) if row[8] else []),
            metadata=json.loads(row[9]) if row[9] else {},
            created_at=datetime.fromisoformat(row[10]),
            updated_at=datetime.fromisoformat(row[11]),
        )

    def update_expectation(self, expectation: Expectation) -> bool:
        """更新期待"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE expectations SET
                    expectation_type = ?,
                    title = ?,
                    description = ?,
                    setup_chapter = ?,
                    due_chapter = ?,
                    fulfilled_chapter = ?,
                    status = ?,
                    tags = ?,
                    metadata = ?,
                    updated_at = ?
                WHERE id = ?
            """,
                (
                    expectation.expectation_type.value,
                    expectation.title,
                    expectation.description,
                    expectation.setup_chapter,
                    expectation.due_chapter,
                    expectation.fulfilled_chapter,
                    expectation.status.value,
                    json.dumps(list(expectation.tags)),
                    json.dumps(expectation.metadata),
                    expectation.updated_at.isoformat(),
                    expectation.id,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0

    def delete_expectation(self, expectation_id: str) -> bool:
        """删除期待"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM expectations WHERE id = ?", (expectation_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_expectations_by_status(
        self, status: ExpectationStatus
    ) -> List[Expectation]:
        """根据状态获取期待列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM expectations WHERE status = ? ORDER BY setup_chapter",
                (status.value,),
            )
            rows = cursor.fetchall()

            return [self._row_to_expectation(row) for row in rows]

    def get_overdue_expectations(self, current_chapter: int) -> List[Expectation]:
        """
        获取逾期期待列表

        Args:
            current_chapter: 当前章节

        Returns:
            逾期期待列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 查询所有待处理且有到期章节的期待
            cursor.execute(
                """
                SELECT * FROM expectations 
                WHERE status = ? AND due_chapter IS NOT NULL AND due_chapter < ?
                ORDER BY due_chapter
            """,
                (ExpectationStatus.PENDING.value, current_chapter),
            )

            rows = cursor.fetchall()
            expectations = [self._row_to_expectation(row) for row in rows]

            # 更新状态为逾期
            for exp in expectations:
                exp.status = ExpectationStatus.OVERDUE
                exp.updated_at = datetime.now()
                self.update_expectation(exp)

            return expectations

    def get_expectations_at_chapter(self, chapter: int) -> List[Expectation]:
        """
        获取在指定章节相关的期待

        Args:
            chapter: 章节号

        Returns:
            相关期待列表（包括在该章节设置、到期或兑现的期待）
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM expectations 
                WHERE setup_chapter = ? OR due_chapter = ? OR fulfilled_chapter = ?
                ORDER BY setup_chapter
            """,
                (chapter, chapter, chapter),
            )

            rows = cursor.fetchall()
            return [self._row_to_expectation(row) for row in rows]

    def get_active_expectations(self, current_chapter: int) -> List[Expectation]:
        """
        获取当前活跃的期待（已设置但未兑现）

        Args:
            current_chapter: 当前章节

        Returns:
            活跃期待列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM expectations 
                WHERE status IN (?, ?) AND setup_chapter <= ?
                ORDER BY due_chapter ASC NULLS LAST
            """,
                (
                    ExpectationStatus.PENDING.value,
                    ExpectationStatus.OVERDUE.value,
                    current_chapter,
                ),
            )

            rows = cursor.fetchall()
            expectations = [self._row_to_expectation(row) for row in rows]

            # 更新状态（检查是否逾期）
            for exp in expectations:
                exp.update_status(current_chapter)
                if exp.status == ExpectationStatus.OVERDUE:
                    self.update_expectation(exp)

            return expectations

    def analyze_expectation_density(
        self, start_chapter: int, end_chapter: int
    ) -> Dict[str, Any]:
        """
        分析期待密度

        Args:
            start_chapter: 起始章节
            end_chapter: 结束章节

        Returns:
            密度分析结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 统计各类型期待数量
            cursor.execute(
                """
                SELECT expectation_type, COUNT(*) as count 
                FROM expectations 
                WHERE setup_chapter BETWEEN ? AND ?
                GROUP BY expectation_type
            """,
                (start_chapter, end_chapter),
            )

            type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # 统计状态分布
            cursor.execute(
                """
                SELECT status, COUNT(*) as count 
                FROM expectations 
                WHERE setup_chapter BETWEEN ? AND ?
                GROUP BY status
            """,
                (start_chapter, end_chapter),
            )

            status_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # 计算平均兑现时间
            cursor.execute(
                """
                SELECT AVG(fulfilled_chapter - setup_chapter) as avg_fulfillment_time
                FROM expectations 
                WHERE status = ? AND fulfilled_chapter IS NOT NULL
                  AND setup_chapter BETWEEN ? AND ?
            """,
                (ExpectationStatus.FULFILLED.value, start_chapter, end_chapter),
            )

            avg_fulfillment_time = cursor.fetchone()[0] or 0

            return {
                "type_distribution": type_counts,
                "status_distribution": status_counts,
                "avg_fulfillment_time": avg_fulfillment_time,
                "total_expectations": sum(type_counts.values()),
                "fulfillment_rate": (
                    status_counts.get(ExpectationStatus.FULFILLED.value, 0)
                    / sum(status_counts.values())
                    * 100
                    if sum(status_counts.values()) > 0
                    else 0
                ),
            }

    def export_to_json(self, filepath: str) -> None:
        """导出所有期待到JSON文件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM expectations ORDER BY setup_chapter")
            rows = cursor.fetchall()

            expectations = [self._row_to_expectation(row).to_dict() for row in rows]

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(expectations, f, ensure_ascii=False, indent=2)

    def import_from_json(self, filepath: str) -> int:
        """从JSON文件导入期待"""
        with open(filepath, "r", encoding="utf-8") as f:
            expectations_data = json.load(f)

        count = 0
        for exp_data in expectations_data:
            expectation = Expectation.from_dict(exp_data)
            self.add_expectation(expectation)
            count += 1

        return count


# 工具函数
def create_promise_expectation(
    title: str,
    description: str,
    setup_chapter: int,
    due_chapter: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Expectation:
    """创建承诺期待"""
    return Expectation(
        id=f"promise_{setup_chapter}_{datetime.now().timestamp()}",
        expectation_type=ExpectationType.PROMISE,
        title=title,
        description=description,
        setup_chapter=setup_chapter,
        due_chapter=due_chapter,
        tags=set(tags or []),
    )


def create_foreshadowing_expectation(
    title: str, description: str, setup_chapter: int, tags: Optional[List[str]] = None
) -> Expectation:
    """创建伏笔期待"""
    return Expectation(
        id=f"foreshadowing_{setup_chapter}_{datetime.now().timestamp()}",
        expectation_type=ExpectationType.FORESHADOWING,
        title=title,
        description=description,
        setup_chapter=setup_chapter,
        tags=set(tags or []),
    )


def create_information_gap_expectation(
    title: str, description: str, setup_chapter: int, tags: Optional[List[str]] = None
) -> Expectation:
    """创建信息差期待"""
    return Expectation(
        id=f"info_gap_{setup_chapter}_{datetime.now().timestamp()}",
        expectation_type=ExpectationType.INFORMATION_GAP,
        title=title,
        description=description,
        setup_chapter=setup_chapter,
        tags=set(tags or []),
    )


if __name__ == "__main__":
    # 简单测试
    tracker = ExpectationTracker(".")

    # 添加测试期待
    promise = create_promise_expectation(
        title="三年之约",
        description="主角与反派约定三年后决斗",
        setup_chapter=3,
        due_chapter=150,
    )
    tracker.add_expectation(promise)

    print(f"添加期待: {promise.title}")

    # 获取活跃期待
    active = tracker.get_active_expectations(100)
    print(f"第100章活跃期待: {len(active)}个")

    # 检查逾期
    overdue = tracker.get_overdue_expectations(200)
    print(f"第200章逾期期待: {len(overdue)}个")
