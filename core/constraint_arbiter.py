"""
Constraint Arbiter - 约束仲裁器

约束优先级仲裁和风格冲突检测

功能：
1. 约束优先级仲裁 - 解决约束冲突
2. 风格冲突检测 - 类型×风格兼容性
3. 时间线冲突检测 - 防止时间倒流
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConstraintPriority(Enum):
    """约束优先级枚举"""

    TEMPORAL_CONTINUITY = 100
    CHARACTER_IDENTITY = 95
    GENRE_WORLDVIEW = 90
    POWER_SYSTEM = 80
    REALM_BOUNDARIES = 75
    STYLE_PACING = 65
    PLOT_ESCALATION = 60
    MOTIVATION_TRACKING = 55
    RESOURCE_PRESSURE = 40
    ENTITY_THREAT = 35
    STYLE_TONE = 25
    STYLE_VOCABULARY = 20


CONSTRAINT_PRIORITY = {
    "temporal_continuity": 100,
    "character_identity": 95,
    "genre_worldview": 90,
    "power_system": 80,
    "realm_boundaries": 75,
    "style_pacing": 65,
    "plot_escalation": 60,
    "motivation_tracking": 55,
    "resource_pressure": 40,
    "entity_threat": 35,
    "style_tone": 25,
    "style_vocabulary": 20,
}


STYLE_COMPATIBILITY = {
    "xianxia": {
        "allowed": ["blood-punch", "cowboy", "dark", "serious"],
        "forbidden": ["sweet"],
        "conflict_resolution": {
            "cowboy": "修改为'稳健修仙流'，突破靠水磨工夫而非生死战"
        },
    },
    "scifi": {
        "allowed": ["infinity", "dark", "serious", "building"],
        "forbidden": ["blood-punch", "sweet"],
        "conflict_resolution": {},
    },
    "urban": {
        "allowed": ["blood-punch", "sweet", "dark", "building"],
        "forbidden": [],
        "conflict_resolution": {},
    },
    "suspense": {
        "allowed": ["serious", "dark", "infinity"],
        "forbidden": ["blood-punch", "sweet"],
        "conflict_resolution": {},
    },
    "game": {
        "allowed": ["blood-punch", "infinity", "cowboy", "building"],
        "forbidden": [],
        "conflict_resolution": {},
    },
    "historical": {
        "allowed": ["serious", "building", "dark"],
        "forbidden": ["sweet"],
        "conflict_resolution": {},
    },
}


@dataclass
class ConflictResult:
    """冲突检测结果"""

    has_conflict: bool
    constraint_name: str = ""
    priority: int = 0
    message: str = ""
    resolution: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class StyleConflictResult:
    """风格冲突结果"""

    conflict: bool
    genre: str
    style: str
    forbidden: bool = False
    resolution: Optional[str] = None
    suggestion: Optional[str] = None


class StyleConflictDetector:
    """风格冲突检测器"""

    def __init__(self):
        self.compatibility = STYLE_COMPATIBILITY

    def detect_conflict(self, genre: str, style: str) -> StyleConflictResult:
        """检测类型-风格冲突"""
        genre_config = self.compatibility.get(genre, {})
        allowed = genre_config.get("allowed", [])

        if style in allowed:
            return StyleConflictResult(conflict=False, genre=genre, style=style)

        forbidden = genre_config.get("forbidden", [])
        is_forbidden = style in forbidden
        resolution = genre_config.get("conflict_resolution", {}).get(style)
        suggestion = allowed[0] if allowed else "默认风格"

        return StyleConflictResult(
            conflict=True,
            genre=genre,
            style=style,
            forbidden=is_forbidden,
            resolution=resolution,
            suggestion=f"建议使用 {suggestion}",
        )

    def get_allowed_styles(self, genre: str) -> List[str]:
        """获取类型允许的风格"""
        return self.compatibility.get(genre, {}).get("allowed", [])


class ConstraintArbiter:
    """
    约束仲裁器

    解决约束冲突，确定优先级
    """

    def __init__(self):
        self.priority = CONSTRAINT_PRIORITY
        self.style_detector = StyleConflictDetector()

    def resolve_conflict(
        self,
        constraint_a: str,
        constraint_b: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConflictResult:
        """
        解决两个约束之间的冲突

        Args:
            constraint_a: 约束A的名称
            constraint_b: 约束B的名称
            context: 额外上下文信息

        Returns:
            ConflictResult: 冲突解决结果
        """
        priority_a = self.priority.get(constraint_a, 0)
        priority_b = self.priority.get(constraint_b, 0)

        if priority_a >= priority_b:
            winner = constraint_a
            winner_priority = priority_a
            loser = constraint_b
        else:
            winner = constraint_b
            winner_priority = priority_b
            loser = constraint_a

        return ConflictResult(
            has_conflict=True,
            constraint_name=winner,
            priority=winner_priority,
            message=f"约束冲突：{constraint_a}({priority_a}) vs {constraint_b}({priority_b})，优先保留 {winner}",
            resolution=f"保留 {winner}，{loser} 被覆盖",
        )

    def check_temporal_conflict(self, current_day: int, new_day: int) -> ConflictResult:
        """
        检查时间线冲突（时间倒流）

        Args:
            current_day: 当前天数
            new_day: 新的天数

        Returns:
            ConflictResult: 冲突检测结果
        """
        if new_day < current_day:
            return ConflictResult(
                has_conflict=True,
                constraint_name="temporal_continuity",
                priority=100,
                message=f"时间倒流：Day {current_day} → Day {new_day}",
                resolution="时间不可倒退",
                suggestion="保持时间连续性，或使用时间循环设定",
            )

        return ConflictResult(
            has_conflict=False,
            constraint_name="temporal_continuity",
            priority=100,
            message="时间线正常",
        )

    def check_style_conflict(self, genre: str, style: str) -> StyleConflictResult:
        """
        检查类型-风格冲突

        Args:
            genre: 类型
            style: 风格

        Returns:
            StyleConflictResult: 风格冲突结果
        """
        return self.style_detector.detect_conflict(genre, style)

    def get_constraint_priority(self, constraint_name: str) -> int:
        """获取约束优先级"""
        return self.priority.get(constraint_name, 0)

    def validate_constraint_chain(self, constraints: List[str]) -> List[ConflictResult]:
        """
        验证约束链的一致性

        Args:
            constraints: 约束列表

        Returns:
            List[ConflictResult]: 冲突列表
        """
        results = []
        seen = set()

        for constraint in constraints:
            if constraint in seen:
                results.append(
                    ConflictResult(
                        has_conflict=False,
                        constraint_name=constraint,
                        message=f"约束 '{constraint}' 已存在",
                    )
                )
            else:
                seen.add(constraint)

        return results


def create_arbiter() -> ConstraintArbiter:
    """创建约束仲裁器"""
    return ConstraintArbiter()


if __name__ == "__main__":
    arbiter = ConstraintArbiter()

    print("=" * 60)
    print("ConstraintArbiter 测试")
    print("=" * 60)

    print("\n【测试1: 时间线冲突】")
    result = arbiter.check_temporal_conflict(3, 1)
    print(f"Day 3 → Day 1: {result.message}")
    print(f"冲突: {result.has_conflict}, 优先级: {result.priority}")
    print(f"解决方案: {result.resolution}")

    result = arbiter.check_temporal_conflict(1, 3)
    print(f"\nDay 1 → Day 3: {result.message}")
    print(f"冲突: {result.has_conflict}")

    print("\n【测试2: 风格冲突】")
    result = arbiter.check_style_conflict("xianxia", "sweet")
    print(f"仙侠 + 甜宠: 冲突={result.conflict}, 禁止={result.forbidden}")
    print(f"建议: {result.suggestion}")

    result = arbiter.check_style_conflict("xianxia", "blood-punch")
    print(f"\n仙侠 + 热血: 冲突={result.conflict}")

    result = arbiter.check_style_conflict("scifi", "blood-punch")
    print(f"\n科幻 + 热血: 冲突={result.conflict}, 禁止={result.forbidden}")
    print(f"建议: {result.suggestion}")

    print("\n【测试3: 约束优先级仲裁】")
    result = arbiter.resolve_conflict("temporal_continuity", "style_pacing")
    print(f"时间连续性 vs 风格节奏: {result.message}")
    print(f"保留: {result.constraint_name} (优先级 {result.priority})")
