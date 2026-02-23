"""
Skill上下文总线 (SkillContextBus)

解决17个Skill孤岛问题 - 所有Skill共享上下文

主要功能：
1. 跨Skill状态传递 - scene-writer知道上一章主角境界
2. 上下文存储 - 境界、爽点密度、重要角色、势力等
3. 实时查询 - 支持按Skill类型查询最近上下文
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SkillContext:
    """单个Skill的上下文数据"""
    skill_name: str
    chapter_number: int
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


class SkillContextBus:
    """
    所有Skill共享的上下文总线

    使用方式：
    bus = SkillContextBus('novels/测试')

    # 写入上下文
    bus.update("scene-writer", {
        "realm": "筑基期",
        "location": "青云宗",
        "payoff_density": 0.5
    })

    # 读取完整上下文
    full_context = bus.get_full_context()

    # 跨Skill查询
    recent_realms = bus.get_recent_context(["scene-writer", "cultivation-designer"], last_n=3)
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.context_file = os.path.join(project_dir, "skill_context.json")
        self._contexts: List[SkillContext] = []
        self._load_contexts()

    def _load_contexts(self):
        """从文件加载上下文"""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._contexts = [SkillContext(**ctx) for ctx in data.get("contexts", [])]
            except Exception as e:
                logger.warning(f"Failed to load skill contexts: {e}")
                self._contexts = []

    def _save_contexts(self):
        """保存上下文到文件"""
        try:
            os.makedirs(os.path.dirname(self.context_file), exist_ok=True)
            data = {
                "last_updated": datetime.now().isoformat(),
                "contexts": [ctx.to_dict() for ctx in self._contexts]
            }
            with open(self.context_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save skill contexts: {e}")

    def update(self, skill_name: str, data: Dict[str, Any], chapter_number: int = None):
        """
        更新指定Skill的上下文

        Args:
            skill_name: Skill名称
            data: 要更新的数据
            chapter_number: 当前章节编号（可选，从上下文推断）
        """
        # 查找是否已有该Skill的上下文
        existing_idx = None
        for i, ctx in enumerate(self._contexts):
            if ctx.skill_name == skill_name:
                existing_idx = i
                break

        # 获取章节编号
        if chapter_number is None:
            chapter_number = self._get_latest_chapter_number(skill_name) + 1

        new_context = SkillContext(
            skill_name=skill_name,
            chapter_number=chapter_number,
            timestamp=datetime.now().isoformat(),
            data=data
        )

        if existing_idx is not None:
            self._contexts[existing_idx] = new_context
        else:
            self._contexts.append(new_context)

        # 保持上下文数量限制（每个Skill最多10条）
        self._prune_contexts(skill_name)

        self._save_contexts()
        logger.info(f"Updated skill context: {skill_name} at chapter {chapter_number}")

    def _get_latest_chapter_number(self, skill_name: str) -> int:
        """获取指定Skill的最新章节编号"""
        for ctx in reversed(self._contexts):
            if ctx.skill_name == skill_name:
                return ctx.chapter_number
        return 0

    def _prune_contexts(self, skill_name: str, max_per_skill: int = 10):
        """修剪过期的上下文"""
        skill_contexts = [ctx for ctx in self._contexts if ctx.skill_name == skill_name]
        if len(skill_contexts) > max_per_skill:
            # 保留最新的
            self._contexts = [
                ctx for ctx in self._contexts
                if ctx.skill_name != skill_name
            ] + skill_contexts[-max_per_skill:]

    def get_full_context(self) -> Dict[str, Any]:
        """获取完整上下文"""
        return {
            "last_updated": datetime.now().isoformat(),
            "skills": {
                ctx.skill_name: ctx.data for ctx in self._contexts
            },
            "summary": self._get_context_summary()
        }

    def get_recent_context(self, skills: List[str], last_n: int = 3) -> Dict[str, List[Dict]]:
        """
        跨Skill获取最近上下文

        Args:
            skills: 要查询的Skill列表
            last_n: 每个Skill返回最近N条

        Returns:
            {skill_name: [context_data, ...]}
        """
        result = {}
        for skill_name in skills:
            skill_contexts = [
                {"chapter": ctx.chapter_number, "data": ctx.data}
                for ctx in self._contexts
                if ctx.skill_name == skill_name
            ][-last_n:]
            if skill_contexts:
                result[skill_name] = skill_contexts
        return result

    def get_current_state(self) -> Dict[str, Any]:
        """获取当前项目状态（所有Skill的最新值）"""
        state = {}
        for ctx in self._contexts:
            if ctx.skill_name not in state:
                state[ctx.skill_name] = ctx.data
        return state

    def _get_context_summary(self) -> Dict[str, Any]:
        """获取上下文摘要"""
        skills = list(set(ctx.skill_name for ctx in self._contexts))
        latest_chapters = {}
        for skill_name in skills:
            latest = max(
                [ctx.chapter_number for ctx in self._contexts if ctx.skill_name == skill_name],
                default=0
            )
            latest_chapters[skill_name] = latest

        return {
            "total_contexts": len(self._contexts),
            "skills_tracked": skills,
            "latest_chapters": latest_chapters
        }

    def get_realm_info(self) -> Optional[Dict[str, Any]]:
        """获取当前境界信息"""
        return self._get_latest_by_skill("cultivation-designer")

    def get_faction_info(self) -> Optional[Dict[str, Any]]:
        """获取当前势力信息"""
        return self._get_latest_by_skill("geopolitics-expert")

    def get_character_info(self) -> Optional[Dict[str, Any]]:
        """获取重要角色信息"""
        return self._get_latest_by_skill("character-designer")

    def get_payoff_density_history(self) -> List[Dict]:
        """获取爽点密度历史"""
        return self.get_recent_context(["scene-writer"], last_n=10).get("scene-writer", [])

    def _get_latest_by_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """获取指定Skill的最新数据"""
        for ctx in reversed(self._contexts):
            if ctx.skill_name == skill_name:
                return ctx.data
        return None

    def clear(self):
        """清空所有上下文"""
        self._contexts = []
        self._save_contexts()

    def export_context(self) -> str:
        """导出上下文为JSON字符串"""
        return json.dumps(self.get_full_context(), ensure_ascii=False, indent=2)


class SkillContextBusMiddleware:
    """
    Skill上下文总线中间件

    用于在Skill执行前后自动记录和注入上下文
    """

    def __init__(self, project_dir: str):
        self.bus = SkillContextBus(project_dir)

    def before_skill(self, skill_name: str, prompt: str, chapter_number: int) -> str:
        """
        Skill执行前 - 注入上下文到提示词

        Returns:
            增强后的提示词
        """
        # 获取当前状态
        current_state = self.bus.get_current_state()

        # 根据Skill类型添加相关上下文
        context_injection = ""

        if skill_name == "scene-writer":
            # 注入境界、势力信息
            realm = current_state.get("cultivation-designer", {}).get("current_realm", "")
            faction = current_state.get("geopolitics-expert", {}).get("current_faction", "")
            if realm:
                context_injection += f"\n\n## 当前境界\n{realm}\n"
            if faction:
                context_injection += f"\n\n## 当前势力\n"

        elif skill_name == "cultivation-designer":
            # 注入前文修炼体系
            prev_realms = self.bus.get_recent_context(["cultivation-designer"], last_n=2)
            if prev_realms.get("cultivation-designer"):
                context_injection += f"\n\n## 前文修炼设定\n{prev_realms['cultivation-designer']}\n"

        elif skill_name == "character-designer":
            # 注入已有人物
            chars = current_state.get("character-designer", {}).get("characters", [])
            if chars:
                context_injection += f"\n\n## 已有人物\n{json.dumps(chars, ensure_ascii=False)}\n"

        # 追加到提示词
        if context_injection:
            prompt += f"\n\n---\n{context_injection}\n---"

        return prompt

    def after_skill(self, skill_name: str, result: str, chapter_number: int):
        """
        Skill执行后 - 提取并保存关键信息

        Args:
            skill_name: Skill名称
            result: Skill输出结果
            chapter_number: 当前章节编号
        """
        # 简单的关键信息提取
        import re

        extracted_data = {}

        if skill_name == "cultivation-designer":
            # 提取境界信息
            realm_match = re.search(r'当前境界[：:]\s*([^\n]+)', result)
            if realm_match:
                extracted_data["current_realm"] = realm_match.group(1).strip()

        elif skill_name == "geopolitics-expert":
            # 提取势力信息
            faction_match = re.search(r'当前势力[：:]\s*([^\n]+)', result)
            if faction_match:
                extracted_data["current_faction"] = faction_match.group(1).strip()

        # 保存上下文
        if extracted_data:
            self.bus.update(skill_name, extracted_data, chapter_number)
