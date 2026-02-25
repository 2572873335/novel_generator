"""
Quality Gate - 适配 4 级 Skills 架构的统一质量检查
Level 3 (Expert): 实时硬约束检查（scene-writer 阶段）
Level 4 (Auditor): 深度语义检查（senior-editor 阶段）

包含 Skill Context Bus 状态传递，防止"失忆"问题
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


class ViolationLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class QualityViolationException(Exception):
    """
    质量违规异常 - 携带 Skill Context 状态防止失忆
    反馈将定向路由给对应的 Level 3 Expert Skill
    """
    def __init__(self, violations: List[Dict], chapter: int, checker: str, skill_context: Optional[Dict] = None):
        self.violations = violations
        self.chapter_number = chapter
        self.checker_name = checker
        self.skill_context = skill_context or {}
        self.critical_count = len([v for v in violations if v.get("severity") == "critical"])
        self.warning_count = len([v for v in violations if v.get("severity") == "warning"])

        message = f"第{chapter}章触发{checker}拦截，{self.critical_count}个严重问题"
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter": self.chapter_number,
            "checker": self.checker_name,
            "violations": self.violations,
            "rewrite_instructions": self._generate_rewrite_instructions(),
            "skill_context_snapshot": self.skill_context
        }

    def _generate_rewrite_instructions(self) -> str:
        """生成给 scene-writer 的具体修改指令"""
        instructions = []
        for v in self.violations:
            if v.get("severity") == "critical":
                vtype = v.get("type", "")
                if "realm" in vtype or "cultivation" in vtype:
                    instructions.append(f"[战力体系/修炼] {v.get('message')} - 请检查 cultivation-designer skill 的设定")
                elif "faction" in vtype:
                    instructions.append(f"[宗门设定] {v.get('message')} - 请检查 geopolitics-expert skill 的势力表")
                elif "name" in vtype:
                    instructions.append(f"[角色姓名] {v.get('message')} - 请检查 character-designer skill 的设定")
                elif "timeline" in vtype:
                    instructions.append(f"[时间线] {v.get('message')} - 请检查节奏连续性")
                else:
                    instructions.append(f"[严重] {v.get('message')}: {v.get('suggestion', '需修改')}")
        return "\n".join(instructions) if instructions else "请全面检查并优化章节质量"


class QualityGate:
    """
    统一质量检查入口 - 适配 4 级 Skills 架构

    工作原理：
    1. Level 3 Expert 阶段：validate_for_expert_stage - scene-writer 写作时，轻量级检查
    2. Level 4 Auditor 阶段：validate_for_auditor_stage - senior-editor 审核前，重量级检查
    3. Skill Context Bus 状态传递，防止"失忆"
    """

    def __init__(self, project_dir: str, llm_client=None, skill_context_bus=None):
        self.project_dir = Path(project_dir)
        self.llm_client = llm_client
        self.skill_context_bus = skill_context_bus

        # 延迟导入避免循环依赖
        from core.writing_constraint_manager import WritingConstraintManager
        from core.hybrid_checker import HybridChecker

        self.constraint_mgr = WritingConstraintManager(project_dir)
        self.hybrid_checker = HybridChecker([], llm_client)

        # 设置白名单
        constraints = self.constraint_mgr.constraints
        if hasattr(constraints, 'faction_whitelist') and constraints.faction_whitelist:
            self.hybrid_checker.whitelist = set(constraints.faction_whitelist)

    def validate_for_expert_stage(self, chapter_number: int, content: str, current_context: Optional[Dict] = None):
        """
        Level 3 Expert 阶段检查（scene-writer 写作时）
        轻量级，不调用 LLM，确保写作流畅性

        Args:
            chapter_number: 章节编号
            content: 章节内容
            current_context: 当前 Skill Context（从 WriterAgentV2 传入）
        """
        # 获取 Skill Context（防止失忆）
        skill_ctx = current_context or {}
        if self.skill_context_bus:
            skill_ctx = self.skill_context_bus.get_full_context()

        # L1: 硬约束检查（宗门、境界、姓名锁定）
        hard_violations = self.constraint_mgr.validate_chapter(chapter_number, content)
        critical_hard = [v for v in hard_violations if v.get("severity") == "critical"]

        if critical_hard:
            raise QualityViolationException(
                violations=critical_hard,
                chapter=chapter_number,
                checker="WritingConstraintManager",
                skill_context=skill_ctx
            )

        # L2: 实体一致性（HybridChecker 快速模式）
        context = {
            "locked_names": getattr(self.constraint_mgr.constraints, 'locked_names', {}),
            "realm_hierarchy": getattr(self.constraint_mgr.constraints, 'realm_hierarchy', {}),
            "current_realm": getattr(self.constraint_mgr.constraints, 'current_realm', ''),
            "cross_realm_combat": getattr(self.constraint_mgr.constraints, 'cross_realm_combat', 'forbidden'),
        }
        hybrid_result = self.hybrid_checker.check_chapter(chapter_number, content, context)
        if not hybrid_result.get("passed", True):
            issues = hybrid_result.get("issues", [])
            critical_issues = [i for i in issues if i.get("severity") == "critical"]
            if critical_issues:
                raise QualityViolationException(
                    violations=critical_issues,
                    chapter=chapter_number,
                    checker="HybridChecker",
                    skill_context=skill_ctx
                )

        return True

    def validate_for_auditor_stage(self, chapter_number: int, content: str, recent_skeletons: Optional[List] = None):
        """
        Level 4 Auditor 阶段检查（senior-editor 审核前）
        重量级，允许调用 LLM 进行语义分析
        滑动窗口：只检查最近 5 章

        Args:
            chapter_number: 章节编号
            content: 章节内容
            recent_skeletons: 最近章节的骨架（可选，提高效率）
        """
        from agents.consistency_checker import ConsistencyChecker

        checker = ConsistencyChecker(str(self.project_dir), self.llm_client)

        try:
            result = checker.check_recent_n_chapters(
                n=5,
                before_chapter=chapter_number,
                skeletons=recent_skeletons
            )
            if not result.get("passed", True):
                raise QualityViolationException(
                    violations=[{
                        "type": "consistency",
                        "severity": "critical",
                        "message": "跨章节逻辑一致性断裂",
                        "suggestion": "请回顾 outline-architect 的大纲和前文 scene-writer 的设定"
                    }],
                    chapter=chapter_number,
                    checker="ConsistencyChecker"
                )
        except QualityViolationException:
            raise
        except Exception as e:
            print(f"  [Auditor 阶段警告] 深度检查跳过: {e}")

        return True

    def validate_or_raise(self, chapter_number: int, content: str) -> Dict[str, Any]:
        """
        统一验证接口（兼容旧代码）
        默认执行 Level 3 Expert 阶段检查
        """
        try:
            self.validate_for_expert_stage(chapter_number, content)
            return {
                "chapter": chapter_number,
                "passed": True,
                "stage": "expert"
            }
        except QualityViolationException as e:
            raise

    def validate_with_sliding_window(
        self,
        chapter_number: int,
        content: str,
        window_size: int = 5
    ) -> Dict[str, Any]:
        """
        带滑动窗口的验证（每5章调用一次）
        执行 Level 3 + Level 4 双重检查
        """
        # 先进行 Expert 阶段检查
        self.validate_for_expert_stage(chapter_number, content)

        # 每5章进行 Auditor 阶段检查
        if chapter_number % window_size == 0 or chapter_number == 1:
            self.validate_for_auditor_stage(chapter_number, content)

        return {
            "chapter": chapter_number,
            "passed": True,
            "stage": "expert+auditor" if chapter_number % window_size == 0 else "expert"
        }

    def check_for_suspension(self, chapter_number: int, content: str, retry_count: int = 0) -> Dict[str, Any]:
        """检查是否需要挂起"""
        max_retries = 3

        try:
            result = self.validate_or_raise(chapter_number, content)
            result["suspended"] = False
            return result
        except QualityViolationException as e:
            if retry_count >= max_retries - 1:
                return {
                    "suspended": True,
                    "chapter": chapter_number,
                    "violations": e.violations,
                    "critical_count": e.critical_count,
                    "message": str(e),
                    "feedback": e.to_dict()["rewrite_instructions"]
                }
            else:
                raise


def create_quality_gate(project_dir: str, llm_client=None, skill_context_bus=None) -> QualityGate:
    """创建质量门的便捷函数"""
    return QualityGate(project_dir, llm_client, skill_context_bus)
