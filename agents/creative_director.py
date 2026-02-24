"""
Creative Director - 熔断机制仲裁者
带全局熔断机制的仲裁者

解决：无限制回滚导致第1章重写100次的问题
核心：第1-3章回滚>3次强制SUSPEND
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Decision(Enum):
    """仲裁决策"""
    PASS = "PASS"          # 通过
    REWRITE = "REWRITE"    # 重写（轻微修改）
    ROLLBACK = "ROLLBACK"  # 回滚（重大问题）
    SUSPEND = "SUSPEND"    # 暂停（触发熔断）


@dataclass
class RollbackRecord:
    """回滚记录"""
    target: int           # 目标章节
    reason: str           # 回滚原因
    timestamp: str        # 时间戳
    attempts: int = 1     # 尝试次数


@dataclass
class ArbitrationResult:
    """仲裁结果"""
    decision: Decision
    target_chapter: int
    actionable_feedback: str
    emotion_gap: float = 0.0
    severity: str = "normal"  # normal, warning, critical
    metadata: Dict[str, Any] = field(default_factory=dict)


class CreativeDirector:
    """
    带全局熔断机制的仲裁者

    核心功能：
    1. 全局回滚计数
    2. 第1-3章熔断阈值：3次
    3. 第4-10章熔断阈值：5次
    4. 10章后熔断阈值：8次

    工作流程：
    1. 收集所有检查报告
    2. 评估问题严重程度
    3. 做出仲裁决策
    4. 如果触发熔断，生成.suspended.json
    """

    # 熔断阈值配置
    CIRCUIT_BREAKER_THRESHOLDS = {
        (1, 3): 3,    # 第1-3章：最多3次回滚
        (4, 10): 5,   # 第4-10章：最多5次回滚
        (11, 100): 8, # 第11-100章：最多8次回滚
    }

    # 严重问题关键词
    CRITICAL_KEYWORDS = {
        "战力崩坏", "角色复活", "战力倒挂", "境界混乱",
        "时间线断裂", "设定吃书", "严重OOC", "逻辑硬伤"
    }

    # 中等问题关键词
    WARNING_KEYWORDS = {
        "节奏拖沓", "情绪断层", "细节不一致", "文风不统一"
    }

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.log_file = self.project_dir / "rollback_log.json"
        self.suspended_file = self.project_dir / ".suspended.json"

        # 全局回滚日志
        self.global_rollback_log: List[RollbackRecord] = []

        # 熔断状态
        self.circuit_breaker_tripped = False
        self.trip_reason = ""

        # 加载已有日志
        self._load_rollback_log()

    def _load_rollback_log(self):
        """加载回滚日志"""
        if self.log_file.exists():
            try:
                data = json.loads(self.log_file.read_text(encoding="utf-8"))
                self.global_rollback_log = [
                    RollbackRecord(**r) for r in data.get("rollbacks", [])
                ]
                logger.info(f"Loaded {len(self.global_rollback_log)} rollback records")
            except Exception as e:
                logger.warning(f"Failed to load rollback log: {e}")

    def _save_rollback_log(self):
        """保存回滚日志"""
        data = {
            "rollbacks": [
                {
                    "target": r.target,
                    "reason": r.reason,
                    "timestamp": r.timestamp,
                    "attempts": r.attempts
                }
                for r in self.global_rollback_log
            ],
            "last_updated": datetime.now().isoformat()
        }
        self.log_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _get_threshold(self, chapter: int) -> int:
        """获取指定章节的回滚阈值"""
        for (start, end), threshold in self.CIRCUIT_BREAKER_THRESHOLDS.items():
            if start <= chapter <= end:
                return threshold
        return 10  # 默认

    def _count_rollbacks_for_chapter(self, target: int) -> int:
        """统计指定章节的回滚次数"""
        return sum(1 for r in self.global_rollback_log if r.target == target)

    def _count_early_rollbacks(self) -> int:
        """统计第1-3章的总回滚次数"""
        return sum(1 for r in self.global_rollback_log if r.target <= 3)

    def _check_circuit_breaker(self, chapter: int) -> Tuple[bool, str]:
        """
        检查是否触发熔断

        Returns:
            (是否熔断, 原因)
        """
        # 统计回滚次数
        if chapter <= 3:
            early_rollbacks = self._count_early_rollbacks()
            threshold = self._get_threshold(chapter)
            if early_rollbacks >= threshold:
                self.circuit_breaker_tripped = True
                reason = f"熔断触发：第1-3章累计回滚{early_rollbacks}次，超过阈值{threshold}"
                logger.critical(reason)
                return True, reason
        else:
            chapter_rollbacks = self._count_rollbacks_for_chapter(chapter)
            threshold = self._get_threshold(chapter)
            if chapter_rollbacks >= threshold:
                self.circuit_breaker_tripped = True
                reason = f"熔断触发：第{chapter}章回滚{chapter_rollbacks}次，超过阈值{threshold}"
                logger.critical(reason)
                return True, reason

        return False, ""

    def _evaluate_severity(self, reports: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """
        评估问题严重程度

        Returns:
            (严重程度, 问题列表)
        """
        issues = []

        for report in reports:
            # 检查关键问题
            content = json.dumps(report, ensure_ascii=False)

            for keyword in self.CRITICAL_KEYWORDS:
                if keyword in content:
                    issues.append(f"[严重] {keyword}: {report.get('message', '')}")

            for keyword in self.WARNING_KEYWORDS:
                if keyword in content:
                    issues.append(f"[警告] {keyword}: {report.get('message', '')}")

        if any("[严重]" in issue for issue in issues):
            return "critical", issues
        elif issues:
            return "warning", issues
        else:
            return "normal", []

    def _generate_feedback(self, reports: List[Dict[str, Any]], severity: str) -> str:
        """生成可操作的反馈"""
        if not reports:
            return "章节质量合格，通过"

        feedback_parts = [f"检测到{len(reports)}个问题："]

        # 按严重程度排序
        critical = [r for r in reports if any(k in json.dumps(r, ensure_ascii=False) for k in self.CRITICAL_KEYWORDS)]
        warning = [r for r in reports if r not in critical]

        if critical:
            feedback_parts.append("\n【严重问题】")
            for r in critical[:3]:  # 最多3个
                feedback_parts.append(f"  - {r.get('message', '严重错误')}")
                if suggestion := r.get('suggestion'):
                    feedback_parts.append(f"    建议: {suggestion}")

        if warning:
            feedback_parts.append("\n【警告问题】")
            for r in warning[:5]:  # 最多5个
                feedback_parts.append(f"  - {r.get('message', '警告')}")

        return "\n".join(feedback_parts)

    def record_rollback(self, target: int, reason: str):
        """记录回滚"""
        record = RollbackRecord(
            target=target,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
        self.global_rollback_log.append(record)
        self._save_rollback_log()
        logger.info(f"Recorded rollback: chapter {target}, reason: {reason[:50]}")

    def create_suspended_state(self, chapter: int, reason: str, reports: List[Dict]) -> Dict[str, Any]:
        """
        创建暂停状态文件

        Returns:
            暂停状态数据
        """
        suspended_data = {
            "status": "SUSPENDED",
            "suspended_chapter": chapter,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "rollback_count": self._count_rollbacks_for_chapter(chapter),
            "reports": reports,
            "required_action": "人工介入处理",
            "can_resume": False
        }

        self.suspended_file.write_text(
            json.dumps(suspended_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        logger.critical(f"Suspended at chapter {chapter}: {reason}")
        return suspended_data

    def arbitrate(
        self,
        chapter: int,
        draft: str,
        reports: List[Dict[str, Any]]
    ) -> ArbitrationResult:
        """
        仲裁决策

        Args:
            chapter: 章节编号
            draft: 草稿内容
            reports: 检查报告列表

        Returns:
            仲裁结果
        """
        # 首先检查熔断
        is_tripped, trip_reason = self._check_circuit_breaker(chapter)
        if is_tripped:
            # 触发熔断
            self.create_suspended_state(chapter, trip_reason, reports)
            return ArbitrationResult(
                decision=Decision.SUSPEND,
                target_chapter=chapter,
                actionable_feedback=trip_reason,
                severity="critical"
            )

        # 评估严重程度
        severity, issues = self._evaluate_severity(reports)

        # 生成反馈
        feedback = self._generate_feedback(reports, severity)

        # 决策
        if severity == "critical":
            # 严重问题：回滚
            self.record_rollback(chapter, feedback[:100])
            return ArbitrationResult(
                decision=Decision.ROLLBACK,
                target_chapter=chapter,
                actionable_feedback=feedback,
                severity="critical"
            )
        elif severity == "warning":
            # 中等问题：重写
            return ArbitrationResult(
                decision=Decision.REWRITE,
                target_chapter=chapter,
                actionable_feedback=feedback,
                severity="warning"
            )
        else:
            # 正常：通过
            return ArbitrationResult(
                decision=Decision.PASS,
                target_chapter=chapter,
                actionable_feedback="章节质量合格",
                severity="normal"
            )

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "circuit_breaker_tripped": self.circuit_breaker_tripped,
            "trip_reason": self.trip_reason,
            "total_rollbacks": len(self.global_rollback_log),
            "early_rollbacks": self._count_early_rollbacks(),
            "thresholds": self.CIRCUIT_BREAKER_THRESHOLDS
        }

    def reset_circuit_breaker(self):
        """重置熔断器（用于恢复后）"""
        self.circuit_breaker_tripped = False
        self.trip_reason = ""
        logger.info("Circuit breaker reset")

    def is_suspended(self) -> bool:
        """检查是否处于暂停状态"""
        return self.suspended_file.exists()

    def clear_suspended(self):
        """清除暂停状态"""
        if self.suspended_file.exists():
            self.suspended_file.unlink()
            logger.info("Suspended state cleared")
