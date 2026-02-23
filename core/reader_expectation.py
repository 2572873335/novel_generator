"""
读者期待感追踪系统
用于追踪读者情感预期，而非仅仅是伏笔

核心概念：
- 期待感 = "主角会怎么解决这个危机？"
- 悬念 = "但主角不知道..."

区别于 ExpectationTracker：
- ExpectationTracker: 追踪"挖坑"（plot-level）
- ReaderExpectation: 追踪"读者情绪"（reader-level）
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import sqlite3
from pathlib import Path


class EmotionType(Enum):
    """情绪类型枚举"""

    # 基础情绪
    NEUTRAL = "neutral"  # 中性
    TENSION = "tension"  # 紧张
    FEAR = "fear"  # 恐惧
    SADNESS = "sadness"  # 悲伤
    ANGER = "anger"  # 愤怒
    JOY = "joy"  # 喜悦
    SURPRISE = "surprise"  # 惊讶

    # 复合情绪（网文特有）
    ANTICIPATION = "anticipation"  # 期待（悬念感）
    ADMIRATION = "admiration"  # 敬佩（装逼成功）
    SCHADENFREUDE = "schadenfreude"  # 快意（打脸）
    TENSION_RELIEF = "tension_relief"  # 释然（突破成功）
    CURIOSITY = "curiosity"  # 好奇（发现秘密）


class QuestionType(Enum):
    """读者问题类型"""

    # 生存类（主角会不会死？）
    SURVIVAL = "survival"  # 生命危险

    # 成长类（主角会变强吗？）
    GROWTH = "growth"  # 实力提升
    BREAKTHROUGH = "breakthrough"  # 境界突破

    # 复仇类（主角会复仇吗？）
    REVENGE = "revenge"  # 复仇

    # 关系类（感情走向）
    RELATIONSHIP = "relationship"  # 人际关系
    ROMANCE = "romance"  # 爱情

    # 秘密类（真相是什么？）
    MYSTERY = "mystery"  # 悬疑
    SECRET = "secret"  # 秘密曝光

    # 成就类（主角会成功吗？）
    ACHIEVEMENT = "achievement"  # 目标达成
    RECOGNITION = "recognition"  # 获得认可


class QuestionUrgency(Enum):
    """问题紧急程度"""

    LOW = 1  # 可以等待（3-5章）
    MEDIUM = 2  # 需要关注（1-3章）
    HIGH = 3  # 即将到期（本章或下章）
    CRITICAL = 4  # 必须解决（本章）


@dataclass
class ReaderQuestion:
    """
    读者问题实体，表示读者在阅读时产生的情感疑问

    核心区别于 Expectation：
    - Expectation: 伏笔/承诺（作者设置的）
    - ReaderQuestion: 读者自然产生的情感疑问（读者感受的）

    示例：
    - "主角被围攻，会不会死？" → SURVIVAL, CRITICAL
    - "三年之约什么时候到期？" → ACHIEVEMENT, MEDIUM
    - "，女主到底喜欢谁？" → ROMANCE, LOW
    """

    id: str
    question_type: QuestionType
    urgency: QuestionUrgency

    # 问题内容
    question_text: str  # 读者心中的问题
    setup_chapter: int  # 问题产生的章节
    due_chapter: Optional[int] = None  # 预期解决章节

    # 情绪价值
    emotion_value: int = 0  # 情绪值 (-50 到 +50)
    emotional_stakes: str = ""  # 情感赌注描述

    # 状态
    is_fulfilled: bool = False  # 是否已解决
    fulfilled_chapter: Optional[int] = None
    fulfillment_method: str = ""  # 解决方式

    # 元数据
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_overdue(self, current_chapter: int) -> bool:
        """检查是否逾期"""
        if self.is_fulfilled:
            return False
        if self.due_chapter is None:
            return False
        return current_chapter >= self.due_chapter

    def get_urgency_score(self, current_chapter: int) -> int:
        """
        计算当前紧急度分数

        Returns:
            0-100 的紧急度分数
        """
        base_score = self.urgency.value * 25

        # 如果有到期日，计算距离
        if self.due_chapter:
            chapters_until_due = self.due_chapter - current_chapter
            if chapters_until_due <= 0:
                return 100  # 已逾期，最高紧急度
            elif chapters_until_due == 1:
                return 80
            elif chapters_until_due <= 3:
                return 60
            else:
                return base_score - (3 - chapters_until_due) * 5
        else:
            return base_score

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["question_type"] = self.question_type.value
        data["urgency"] = self.urgency.value
        data["tags"] = list(self.tags)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReaderQuestion":
        """从字典创建实例"""
        data["question_type"] = QuestionType(data["question_type"])
        data["urgency"] = QuestionUrgency(data["urgency"])
        data["tags"] = set(data.get("tags", []))
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


@dataclass
class EmotionCurvePoint:
    """
    情绪曲线上的一个点
    """

    position: int  # 在章节中的位置（字数）
    emotion_value: int  # 情绪值 (-50 到 +50)
    emotion_type: EmotionType  # 情绪类型
    description: str  # 描述
    is_payoff: bool = False  # 是否是爽点

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "emotion_value": self.emotion_value,
            "emotion_type": self.emotion_type.value,
            "description": self.description,
            "is_payoff": self.is_payoff,
        }


class ReaderExpectation:
    """
    读者期待感追踪器

    与 ExpectationTracker 的区别：
    - ExpectationTracker: 追踪伏笔、承诺（作者视角）
    - ReaderExpectation: 追踪读者情感疑问（读者视角）

    核心功能：
    1. setup_expectation() - 章节结尾设置读者预期
    2. track_emotion() - 追踪读者情绪曲线
    3. verify_fulfillment() - 验证预期是否满足
    4. get_urgent_hooks() - 获取需要立即兑现的钩子
    """

    def __init__(self, project_path: str):
        """
        初始化读者期待追踪器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.db_path = self.project_path / "reader_expectations.db"
        self._init_database()

    def _init_database(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 读者问题表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reader_questions (
                    id TEXT PRIMARY KEY,
                    question_type TEXT NOT NULL,
                    urgency INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    setup_chapter INTEGER NOT NULL,
                    due_chapter INTEGER,
                    emotion_value INTEGER DEFAULT 0,
                    emotional_stakes TEXT,
                    is_fulfilled INTEGER DEFAULT 0,
                    fulfilled_chapter INTEGER,
                    fulfillment_method TEXT,
                    tags TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 情绪曲线表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotion_curves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter INTEGER NOT NULL,
                    position INTEGER NOT NULL,
                    emotion_value INTEGER NOT NULL,
                    emotion_type TEXT NOT NULL,
                    description TEXT,
                    is_payoff INTEGER DEFAULT 0
                )
            """)

            # 创建索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_questions_chapter ON reader_questions(setup_chapter)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_questions_due ON reader_questions(due_chapter)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_curves_chapter ON emotion_curves(chapter)"
            )

            conn.commit()

    # ==================== 读者问题管理 ====================

    def setup_expectation(
        self,
        question_type: QuestionType,
        question_text: str,
        setup_chapter: int,
        urgency: QuestionUrgency = QuestionUrgency.MEDIUM,
        due_chapter: Optional[int] = None,
        emotion_value: int = 0,
        emotional_stakes: str = "",
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        在章节结尾设置读者预期

        这是 ReaderExpectation 的核心方法：
        - 在章节结尾创建读者问题
        - 设置问题的紧急程度
        - 设定预期解决章节

        Args:
            question_type: 问题类型
            question_text: 问题文本（读者心中的疑问）
            setup_chapter: 产生问题的章节
            urgency: 紧急程度
            due_chapter: 预期解决章节
            emotion_value: 情绪值
            emotional_stakes: 情感赌注描述
            tags: 标签

        Returns:
            问题ID
        """
        question_id = (
            f"q_{question_type.value}_{setup_chapter}_{datetime.now().timestamp()}"
        )

        question = ReaderQuestion(
            id=question_id,
            question_type=question_type,
            urgency=urgency,
            question_text=question_text,
            setup_chapter=setup_chapter,
            due_chapter=due_chapter,
            emotion_value=emotion_value,
            emotional_stakes=emotional_stakes,
            tags=set(tags or []),
        )

        self._save_question(question)
        return question_id

    def _save_question(self, question: ReaderQuestion) -> None:
        """保存问题到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO reader_questions 
                (id, question_type, urgency, question_text, setup_chapter, due_chapter,
                 emotion_value, emotional_stakes, is_fulfilled, fulfilled_chapter,
                 fulfillment_method, tags, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    question.id,
                    question.question_type.value,
                    question.urgency.value,
                    question.question_text,
                    question.setup_chapter,
                    question.due_chapter,
                    question.emotion_value,
                    question.emotional_stakes,
                    1 if question.is_fulfilled else 0,
                    question.fulfilled_chapter,
                    question.fulfillment_method,
                    json.dumps(list(question.tags)),
                    json.dumps(question.metadata),
                    question.created_at.isoformat(),
                    question.updated_at.isoformat(),
                ),
            )
            conn.commit()

    def get_question(self, question_id: str) -> Optional[ReaderQuestion]:
        """获取问题"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM reader_questions WHERE id = ?", (question_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_question(row)

    def _row_to_question(self, row) -> ReaderQuestion:
        """数据库行转换为 ReaderQuestion"""
        return ReaderQuestion(
            id=row[0],
            question_type=QuestionType(row[1]),
            urgency=QuestionUrgency(row[2]),
            question_text=row[3],
            setup_chapter=row[4],
            due_chapter=row[5],
            emotion_value=row[6] or 0,
            emotional_stakes=row[7] or "",
            is_fulfilled=bool(row[8]),
            fulfilled_chapter=row[9],
            fulfillment_method=row[10] or "",
            tags=set(json.loads(row[11]) if row[11] else []),
            metadata=json.loads(row[12]) if row[12] else {},
            created_at=datetime.fromisoformat(row[13]),
            updated_at=datetime.fromisoformat(row[14]),
        )

    def verify_fulfillment(
        self,
        question_id: str,
        current_chapter: int,
        fulfillment_method: str = "",
    ) -> bool:
        """
        验证并标记问题已解决

        Args:
            question_id: 问题ID
            current_chapter: 当前章节
            fulfillment_method: 解决方式描述

        Returns:
            是否成功标记
        """
        question = self.get_question(question_id)
        if not question:
            return False

        question.is_fulfilled = True
        question.fulfilled_chapter = current_chapter
        question.fulfillment_method = fulfillment_method
        question.updated_at = datetime.now()

        self._save_question(question)
        return True

    def get_urgent_hooks(self, current_chapter: int) -> List[ReaderQuestion]:
        """
        获取需要立即兑现的钩子

        这是 ReaderExpectation 区别于 ExpectationTracker 的核心方法：
        - ExpectationTracker: 返回所有逾期伏笔
        - ReaderExpectation: 返回需要情感关注的紧急问题

        Args:
            current_chapter: 当前章节

        Returns:
            按紧急度排序的问题列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 获取所有未解决的问题
            cursor.execute(
                """
                SELECT * FROM reader_questions 
                WHERE is_fulfilled = 0
                ORDER BY due_chapter ASC NULLS LAST
            """,
            )

            questions = [self._row_to_question(row) for row in cursor.fetchall()]

            # 计算紧急度并排序
            urgent_questions = []
            for q in questions:
                urgency_score = q.get_urgency_score(current_chapter)
                if urgency_score >= 60:  # 高于60分视为需要关注
                    urgent_questions.append((urgency_score, q))

            # 按紧急度排序
            urgent_questions.sort(key=lambda x: -x[0])

            return [q for _, q in urgent_questions]

    def get_unanswered_questions(
        self,
        question_type: Optional[QuestionType] = None,
        limit: int = 10,
    ) -> List[ReaderQuestion]:
        """
        获取未回答的问题

        Args:
            question_type: 按类型过滤
            limit: 返回数量限制

        Returns:
            问题列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if question_type:
                cursor.execute(
                    """
                    SELECT * FROM reader_questions 
                    WHERE is_fulfilled = 0 AND question_type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (question_type.value, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM reader_questions 
                    WHERE is_fulfilled = 0
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            return [self._row_to_question(row) for row in cursor.fetchall()]

    # ==================== 情绪曲线管理 ====================

    def track_emotion(
        self,
        chapter: int,
        emotion_points: List[EmotionCurvePoint],
    ) -> None:
        """
        追踪章节的情绪曲线

        Args:
            chapter: 章节号
            emotion_points: 情绪曲线点列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 先删除该章节的旧曲线
            cursor.execute("DELETE FROM emotion_curves WHERE chapter = ?", (chapter,))

            # 插入新的情绪曲线点
            for point in emotion_points:
                cursor.execute(
                    """
                    INSERT INTO emotion_curves 
                    (chapter, position, emotion_value, emotion_type, description, is_payoff)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        chapter,
                        point.position,
                        point.emotion_value,
                        point.emotion_type.value,
                        point.description,
                        1 if point.is_payoff else 0,
                    ),
                )

            conn.commit()

    def get_emotion_curve(self, chapter: int) -> List[EmotionCurvePoint]:
        """
        获取章节的情绪曲线

        Args:
            chapter: 章节号

        Returns:
            情绪曲线点列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM emotion_curves 
                WHERE chapter = ?
                ORDER BY position
            """,
                (chapter,),
            )

            points = []
            for row in cursor.fetchall():
                points.append(
                    EmotionCurvePoint(
                        position=row[2],
                        emotion_value=row[3],
                        emotion_type=EmotionType(row[4]),
                        description=row[5] or "",
                        is_payoff=bool(row[6]),
                    )
                )

            return points

    def analyze_emotion_trend(
        self,
        start_chapter: int,
        end_chapter: int,
    ) -> Dict[str, Any]:
        """
        分析章节范围内的情绪趋势

        Args:
            start_chapter: 起始章节
            end_chapter: 结束章节

        Returns:
            情绪分析结果
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 获取所有情绪点
            cursor.execute(
                """
                SELECT chapter, AVG(emotion_value) as avg_emotion, 
                       MAX(emotion_value) as max_emotion,
                       MIN(emotion_value) as min_emotion,
                       SUM(is_payoff) as payoff_count
                FROM emotion_curves
                WHERE chapter BETWEEN ? AND ?
                GROUP BY chapter
                ORDER BY chapter
            """,
                (start_chapter, end_chapter),
            )

            chapter_emotions = []
            for row in cursor.fetchall():
                chapter_emotions.append(
                    {
                        "chapter": row[0],
                        "avg_emotion": row[1] or 0,
                        "max_emotion": row[2] or 0,
                        "min_emotion": row[3] or 0,
                        "payoff_count": row[4] or 0,
                    }
                )

            # 计算整体统计
            if chapter_emotions:
                avg_emotions = [c["avg_emotion"] for c in chapter_emotions]
                overall_avg = sum(avg_emotions) / len(avg_emotions)
                total_payoffs = sum(c["payoff_count"] for c in chapter_emotions)
            else:
                overall_avg = 0
                total_payoffs = 0

            return {
                "chapter_range": (start_chapter, end_chapter),
                "chapters": chapter_emotions,
                "overall_avg_emotion": overall_avg,
                "total_payoffs": total_payoffs,
                "payoff_density": total_payoffs
                / max(1, end_chapter - start_chapter + 1),
            }

    # ==================== 便捷方法 ====================

    def create_survival_hook(
        self,
        chapter: int,
        threat_description: str,
        due_chapter: Optional[int] = None,
    ) -> str:
        """创建生存类钩子（主角生命危险）"""
        return self.setup_expectation(
            question_type=QuestionType.SURVIVAL,
            question_text=f"{threat_description}，主角会不会死？",
            setup_chapter=chapter,
            urgency=QuestionUrgency.CRITICAL
            if due_chapter == chapter
            else QuestionUrgency.HIGH,
            due_chapter=due_chapter,
            emotion_value=-40,
            emotional_stakes="主角生死未卜",
            tags=["生存", "危机"],
        )

    def create_growth_hook(
        self,
        chapter: int,
        obstacle_description: str,
        due_chapter: Optional[int] = None,
    ) -> str:
        """创建成长类钩子（主角实力提升）"""
        return self.setup_expectation(
            question_type=QuestionType.GROWTH,
            question_text=f"{obstacle_description}，主角会如何突破？",
            setup_chapter=chapter,
            urgency=QuestionUrgency.MEDIUM,
            due_chapter=due_chapter,
            emotion_value=20,
            emotional_stakes="实力提升的关键",
            tags=["成长", "突破"],
        )

    def create_mystery_hook(
        self,
        chapter: int,
        mystery_description: str,
        due_chapter: Optional[int] = None,
    ) -> str:
        """创建神秘类钩子（秘密/真相）"""
        return self.setup_expectation(
            question_type=QuestionType.MYSTERY,
            question_text=f"{mystery_description}，真相到底是什么？",
            setup_chapter=chapter,
            urgency=QuestionUrgency.MEDIUM,
            due_chapter=due_chapter,
            emotion_value=15,
            emotional_stakes="隐藏的秘密",
            tags=["悬疑", "秘密"],
        )

    def create_revenge_hook(
        self,
        chapter: int,
        injustice_description: str,
        due_chapter: Optional[int] = None,
    ) -> str:
        """创建复仇类钩子"""
        return self.setup_expectation(
            question_type=QuestionType.REVENGE,
            question_text=f"{injustice_description}，主角会复仇吗？",
            setup_chapter=chapter,
            urgency=QuestionUrgency.MEDIUM,
            due_chapter=due_chapter,
            emotion_value=25,
            emotional_stakes="仇恨与复仇",
            tags=["复仇", "仇恨"],
        )

    # ==================== 统计与分析 ====================

    def get_expectation_summary(self, current_chapter: int) -> Dict[str, Any]:
        """
        获取期待感总结

        Args:
            current_chapter: 当前章节

        Returns:
            总结字典
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 统计各类问题
            cursor.execute(
                """
                SELECT question_type, COUNT(*) as count
                FROM reader_questions
                WHERE is_fulfilled = 0
                GROUP BY question_type
            """
            )
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # 统计紧急问题
            urgent = self.get_urgent_hooks(current_chapter)

            # 统计已解决/未解决
            cursor.execute(
                """
                SELECT 
                    SUM(CASE WHEN is_fulfilled = 1 THEN 1 ELSE 0 END) as fulfilled,
                    SUM(CASE WHEN is_fulfilled = 0 THEN 1 ELSE 0 END) as pending
                FROM reader_questions
            """
            )
            row = cursor.fetchone()
            fulfilled_count = row[0] or 0
            pending_count = row[1] or 0

            return {
                "current_chapter": current_chapter,
                "type_distribution": type_counts,
                "urgent_hooks_count": len(urgent),
                "urgent_hooks": [
                    {
                        "id": q.id,
                        "question": q.question_text,
                        "due_chapter": q.due_chapter,
                        "urgency": q.urgency.name,
                    }
                    for q in urgent[:5]
                ],
                "fulfilled_count": fulfilled_count,
                "pending_count": pending_count,
                "fulfillment_rate": (
                    fulfilled_count / (fulfilled_count + pending_count) * 100
                    if (fulfilled_count + pending_count) > 0
                    else 0
                ),
            }

    def export_to_json(self, filepath: str) -> None:
        """导出所有数据到JSON"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 导出问题
            cursor.execute("SELECT * FROM reader_questions ORDER BY setup_chapter")
            questions = [
                self._row_to_question(row).to_dict() for row in cursor.fetchall()
            ]

            # 导出情绪曲线
            cursor.execute("SELECT * FROM emotion_curves ORDER BY chapter, position")
            curves = []
            for row in cursor.fetchall():
                curves.append(
                    {
                        "chapter": row[1],
                        "position": row[2],
                        "emotion_value": row[3],
                        "emotion_type": row[4],
                        "description": row[5],
                        "is_payoff": bool(row[6]),
                    }
                )

            data = {
                "questions": questions,
                "emotion_curves": curves,
                "exported_at": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)


# ==================== 便捷函数 ====================


def create_survival_question(
    question_text: str,
    setup_chapter: int,
    due_chapter: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ReaderQuestion:
    """创建生存类读者问题"""
    return ReaderQuestion(
        id=f"survival_{setup_chapter}_{datetime.now().timestamp()}",
        question_type=QuestionType.SURVIVAL,
        urgency=QuestionUrgency.CRITICAL,
        question_text=question_text,
        setup_chapter=setup_chapter,
        due_chapter=due_chapter,
        emotion_value=-40,
        emotional_stakes="主角生死",
        tags=set(tags or []),
    )


def create_growth_question(
    question_text: str,
    setup_chapter: int,
    due_chapter: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ReaderQuestion:
    """创建成长类读者问题"""
    return ReaderQuestion(
        id=f"growth_{setup_chapter}_{datetime.now().timestamp()}",
        question_type=QuestionType.GROWTH,
        urgency=QuestionUrgency.MEDIUM,
        question_text=question_text,
        setup_chapter=setup_chapter,
        due_chapter=due_chapter,
        emotion_value=20,
        emotional_stakes="实力成长",
        tags=set(tags or []),
    )


# ==================== 示例模板 ====================

# 网文常见钩子模板
HOOK_TEMPLATES = {
    "危机开场": {
        "question_type": QuestionType.SURVIVAL,
        "urgency": QuestionUrgency.CRITICAL,
        "emotion_value": -40,
        "template": "主角陷入{threat}，会不会死？",
    },
    "秘密暴露": {
        "question_type": QuestionType.MYSTERY,
        "urgency": QuestionUrgency.HIGH,
        "emotion_value": 20,
        "template": "{secret}的真相到底是什么？",
    },
    "不公对待": {
        "question_type": QuestionType.REVENGE,
        "urgency": QuestionUrgency.MEDIUM,
        "emotion_value": 25,
        "template": "主角被{injustice}，会如何复仇？",
    },
    "突破契机": {
        "question_type": QuestionType.BREAKTHROUGH,
        "urgency": QuestionUrgency.MEDIUM,
        "emotion_value": 30,
        "template": "{obstacle}在前，主角能突破吗？",
    },
    "感情纠葛": {
        "question_type": QuestionType.ROMANCE,
        "urgency": QuestionUrgency.LOW,
        "emotion_value": 15,
        "template": "{person}到底喜欢谁？",
    },
}


if __name__ == "__main__":
    # 简单测试
    re = ReaderExpectation(".")

    # 创建生存钩子
    hook_id = re.create_survival_hook(
        chapter=1,
        threat_description="被反派围攻",
        due_chapter=2,
    )
    print(f"创建钩子: {hook_id}")

    # 获取紧急钩子
    urgent = re.get_urgent_hooks(1)
    print(f"第1章紧急钩子: {len(urgent)}个")

    # 添加情绪曲线
    re.track_emotion(
        chapter=1,
        emotion_points=[
            EmotionCurvePoint(0, 0, EmotionType.NEUTRAL, "开篇"),
            EmotionCurvePoint(500, -20, EmotionType.TENSION, "被嘲讽"),
            EmotionCurvePoint(1000, -30, EmotionType.FEAR, "危机出现"),
            EmotionCurvePoint(1500, -10, EmotionType.ANTICIPATION, "转机"),
            EmotionCurvePoint(2000, 25, EmotionType.JOY, "小爽-获得帮助"),
            EmotionCurvePoint(2500, 40, EmotionType.TENSION_RELIEF, "大爽-反击成功"),
            EmotionCurvePoint(3000, 30, EmotionType.SURPRISE, "章末钩子-更强敌人出现"),
        ],
    )

    # 分析情绪趋势
    trend = re.analyze_emotion_trend(1, 1)
    print(f"情绪趋势: {trend}")

    # 获取总结
    summary = re.get_expectation_summary(1)
    print(f"期待总结: {summary}")
