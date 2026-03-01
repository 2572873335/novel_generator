"""
Prompt Assembler - Prompt聚合层
将多个Skill的指令聚合为单次API调用

解决：L1→L2→L3→L4 每层都调API (8-12次调用/章) 的问题
核心：合并L2+L3为单次Prompt组装
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromptComponent:
    """Prompt组件"""
    source: str          # 来源：elastic_architect, rhythm_designer, emotion_continuity, style_skill
    priority: int        # 优先级：1=最高
    content: str         # 内容
    max_tokens: int = 500  # 最大token估算


class PromptAssembler:
    """
    Prompt聚合器

    核心功能：
    1. ElasticArchitect组件：近景清晰，远景模糊
    2. RhythmDesigner组件：情绪债务提醒
    3. EmotionalContinuityGuardian组件：情绪衰减检查
    4. StyleSkill组件：自动匹配文风

    输出：单次超级Prompt
    """

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.outline_file = self.project_dir / "outline.md"
        self.volume_outline_file = self.project_dir / "volume_outline.json"
        self.chapter_outline_file = self.project_dir / "chapters" / "chapter_outlines.json"
        self.style_file = self.project_dir / "style_signature.json"

        # 技能目录
        self.skills_dir = Path(".opencode/skills")
        self.custom_skills_dir = Path("user_data/custom_skills")

        # 状态管理器（延迟初始化）
        self.state_manager = None

    def _get_state_manager(self):
        """获取或初始化状态管理器"""
        if self.state_manager is None:
            try:
                from core.state_snapshot import StateSnapshotManager
                self.state_manager = StateSnapshotManager(str(self.project_dir))
            except Exception as e:
                logger.warning(f"Failed to initialize StateSnapshotManager: {e}")
        return self.state_manager

    def get_state_summary(self, chapter_num: int = None) -> str:
        """
        获取当前世界状态摘要

        从 StateSnapshotManager 获取最新快照的状态信息，用于写入Prompt

        Args:
            chapter_num: 当前章节号，如果为None则获取最新的

        Returns:
            格式化的状态摘要文本
        """
        state_mgr = self._get_state_manager()
        if not state_mgr:
            return ""

        try:
            # 获取指定章节之前的最新快照
            snapshot = state_mgr.get_latest_snapshot_before(chapter_num or 999)
            if not snapshot:
                return "（暂无世界状态记录）"

            # 提取关键状态信息
            state = snapshot.world_state
            summary_parts = ["【当前世界状态】"]

            # 角色状态
            if state.get("characters"):
                chars = list(state["characters"].keys())[:5]  # 最多5个
                summary_parts.append(f"主要角色: {', '.join(chars)}")

            # 地点状态
            if state.get("locations"):
                locs = list(state["locations"].keys())[:3]
                summary_parts.append(f"涉及地点: {', '.join(locs)}")

            # 势力状态
            if state.get("factions"):
                facts = list(state["factions"].keys())[:3]
                summary_parts.append(f"相关势力: {', '.join(facts)}")

            # 物品/道具
            if state.get("items"):
                items = list(state["items"].keys())[:3]
                summary_parts.append(f"关键物品: {', '.join(items)}")

            # 情节点
            if state.get("plot_points"):
                plots = list(state["plot_points"].keys())[:3]
                summary_parts.append(f"进行中情节: {', '.join(plots)}")

            return "\n".join(summary_parts) if len(summary_parts) > 1 else "（世界状态无显著变化）"

        except Exception as e:
            logger.warning(f"Failed to get state summary: {e}")
            return ""

    def load_skill_prompt(self, skill_name: str) -> str:
        """
        加载指定技能的Prompt内容

        搜索顺序：
        1. user_data/custom_skills/{skill_name}/SKILL.md (自定义技能优先)
        2. .opencode/skills/{skill_name}/SKILL.md (内置技能)

        Args:
            skill_name: 技能名称

        Returns:
            技能Prompt内容，如果不存在则返回空字符串
        """
        # 优先从自定义技能目录加载
        custom_path = self.custom_skills_dir / skill_name / "SKILL.md"
        if custom_path.exists():
            content = custom_path.read_text(encoding="utf-8")
            # 跳过 front matter
            return self._strip_front_matter(content)

        # 从内置技能目录加载
        builtin_path = self.skills_dir / skill_name / "SKILL.md"
        if builtin_path.exists():
            content = builtin_path.read_text(encoding="utf-8")
            return self._strip_front_matter(content)

        return ""

    def _strip_front_matter(self, content: str) -> str:
        """移除 Markdown 的 front matter (YAML 头部)"""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content.strip()

    def load_active_skills(self) -> Dict[str, str]:
        """
        加载项目启用的技能

        从项目配置中读取启用的技能列表，然后加载对应的Prompt

        Returns:
            技能名称 -> Prompt内容 的字典
        """
        skills = {}

        # 默认启用的技能（如果项目没有配置）
        default_skills = [
            "chapter-architect",      # 章纲架构
            "rhythm-designer",        # 节奏设计
            "scene-writer",           # 场景写作
            "web-novel-methodology",  # 网文方法论
        ]

        # 尝试从项目配置读取
        config_file = self.project_dir / "project_config.json"
        enabled_skills = default_skills

        if config_file.exists():
            try:
                config = json.loads(config_file.read_text(encoding="utf-8"))
                enabled_skills = config.get("enabled_skills", default_skills)
            except Exception as e:
                logger.warning(f"Failed to load project config for skills: {e}")

        # 加载每个技能
        for skill_name in enabled_skills:
            prompt = self.load_skill_prompt(skill_name)
            if prompt:
                skills[skill_name] = prompt
                logger.debug(f"Loaded skill: {skill_name}")

        return skills

    def get_skill_prompt_section(self, skills: Dict[str, str]) -> str:
        """
        将技能Prompt格式化为章节Prompt的一部分

        Args:
            skills: 技能名称 -> Prompt内容 的字典

        Returns:
            格式化的技能Prompt段落
        """
        if not skills:
            return ""

        sections = ["【技能指导】"]
        for name, content in skills.items():
            # 取内容的前500字符作为关键指导（避免过长）
            key_content = content[:500] if len(content) > 500 else content
            sections.append(f"\n## {name}\n{key_content}")

        return "\n".join(sections)

    def _load_outline(self) -> str:
        """加载主线大纲"""
        if self.outline_file.exists():
            return self.outline_file.read_text(encoding="utf-8")
        return ""

    def _load_volume_outline(self) -> Dict[str, Any]:
        """加载卷纲"""
        if self.volume_outline_file.exists():
            return json.loads(self.volume_outline_file.read_text(encoding="utf-8"))
        return {}

    def _load_chapter_outline(self, chapter_num: int) -> Optional[Dict[str, Any]]:
        """加载指定章节大纲"""
        if self.chapter_outline_file.exists():
            outlines = json.loads(self.chapter_outline_file.read_text(encoding="utf-8"))
            return outlines.get(str(chapter_num)) or outlines.get(f"chapter_{chapter_num}")
        return None

    def _load_style_signature(self) -> Dict[str, Any]:
        """加载文风签名"""
        if self.style_file.exists():
            return json.loads(self.style_file.read_text(encoding="utf-8"))
        return {}

    def _get_elastic_outline(self, chapter_num: int, target_chapters: int) -> str:
        """
        ElasticArchitect组件：近景清晰，远景模糊

        根据章节位置动态调整大纲细节：
        - 前后3章：详细大纲
        - 3-10章：中等细节
        - 10章后：仅主线
        """
        outline = self._load_outline()
        volume_outline = self._load_volume_outline()
        chapter_outline = self._load_chapter_outline(chapter_num)

        # 当前卷信息
        current_volume = volume_outline.get("volumes", [{}])[0]  # 简化处理
        volume_arc = current_volume.get("arc", "")

        # 近景：当前章节详细大纲
        near_outline = ""
        if chapter_outline:
            near_outline = f"""【第{chapter_num}章大纲】
{chapter_outline.get('title', '')}
{chapter_outline.get('summary', '')}
核心场景: {', '.join(chapter_outline.get('scenes', []))}
章末钩子: {chapter_outline.get('cliffhanger', '')}
"""

        # 中景：前后3章概要
        mid_outline = ""
        for i in range(max(1, chapter_num - 2), min(target_chapters + 1, chapter_num + 3)):
            if i != chapter_num:
                ch_out = self._load_chapter_outline(i)
                if ch_out:
                    mid_outline += f"  第{i}章: {ch_out.get('summary', '')[:50]}...\n"

        # 远景：当前卷主线 + 整体主线
        far_outline = f"""
【当前卷主线】{volume_arc}
【整体主线】{outline[:200] if outline else '暂无'}...
"""

        # 根据距离调整权重
        if chapter_num <= 3:
            # 开篇：极详细
            detail_level = "极高"
            outline_text = near_outline + far_outline
        elif chapter_num <= 10:
            # 发展：中等
            detail_level = "中"
            outline_text = near_outline + mid_outline + far_outline
        else:
            # 后期：简略
            detail_level = "低"
            outline_text = f"【第{chapter_num}章】(详细大纲见文件)\n" + far_outline

        return f"""[ElasticArchitect - 弹性大纲]
大纲细节级别: {detail_level}
{outline_text}
"""

    def _get_rhythm_designer(self, emotion_prompt: str, emotional_debt: float) -> str:
        """
        RhythmDesigner组件：情绪债务提醒

        将情绪债务计算结果转化为LLM可理解的指令
        """
        # 根据债务值确定本章节奏要求
        if emotional_debt > 80:
            rhythm_instruction = "⚠️ 必须高强度爽点爆发！安排：逆袭/打脸/突破/揭露"
        elif emotional_debt > 50:
            rhythm_instruction = "⚠️ 需要爽点安排，建议：小高潮/角色成长/敌人受挫"
        elif emotional_debt > 20:
            rhythm_instruction = "ℹ️ 可安排适度爽点，保持节奏"
        elif emotional_debt > -20:
            rhythm_instruction = "✅ 按大纲正常推进"
        elif emotional_debt > -50:
            rhythm_instruction = "✅ 爽点充足，可适度压抑"
        else:
            rhythm_instruction = "🎉 爽点密集，考虑小回落"

        return f"""[RhythmDesigner - 节奏设计]
情绪债务值: {emotional_debt:.1f}
本章节奏要求: {rhythm_instruction}
情绪指令: {emotion_prompt}
"""

    def _get_emotional_continuity_check(self, chapter_num: int, recent_debts: List[float]) -> str:
        """
        EmotionalContinuityGuardian组件：情绪衰减检查

        检查最近章节的情绪趋势，防止情绪断层
        """
        if len(recent_debts) < 2:
            return "[EmotionalContinuity] 暂无历史数据，跳过检查"

        # 计算趋势
        diff = recent_debts[-1] - recent_debts[-2]
        trend = "上升" if diff > 10 else ("下降" if diff < -10 else "平稳")

        # 检查是否需要调整
        warning = ""
        if trend == "上升" and diff > 30:
            warning = "⚠️ 情绪突然大幅上升，需要平滑过渡，避免突兀"
        elif trend == "下降" and diff < -30:
            warning = "⚠️ 情绪突然大幅下降，需检查是否有逻辑断层"

        return f"""[EmotionalContinuity - 情绪连续性]
最近趋势: {trend} (变化{diff:.1f})
{warning}
"""

    def _get_style_signature(self, emotional_vector: Dict = None) -> str:
        """
        StyleSkill组件：自动匹配文风

        根据情绪向量和已有风格调整写作
        """
        style = self._load_style_signature()

        if not style:
            return "[Style] 使用默认网文风格"

        # 提取风格特征
        tone = style.get("tone", "中性的")
        pacing = style.get("pacing", "中等")
        dialogue_ratio = style.get("dialogue_ratio", "20%")
        description_style = style.get("description_style", "白描")

        # 根据情绪向量调整
        adjust = ""
        if emotional_vector:
            base_tone = emotional_vector.get("base_tone", "")
            if "压抑" in base_tone:
                adjust = "（情绪压抑，减少轻松幽默描写）"
            elif "狂喜" in base_tone:
                adjust = "（情绪高涨，可增加夸张描写）"

        return f"""[StyleSkill - 文风锁定]
文风基调: {tone}
节奏: {pacing}
对话比例: {dialogue_ratio}
描写风格: {description_style}{adjust}
"""

    def assemble_emotion_writer_prompt(
        self,
        chapter_num: int,
        target_chapters: int,
        emotional_debt: float,
        emotion_prompt: str,
        recent_debts: List[float],
        emotional_vector: Dict = None,
        custom_instructions: str = ""
    ) -> str:
        """
        聚合为超级Prompt - 单次API调用

        Args:
            chapter_num: 章节编号
            target_chapters: 目标章节数
            emotional_debt: 情绪债务值
            emotion_prompt: 情绪指令文本
            recent_debts: 最近债务趋势
            emotional_vector: 情绪向量
            custom_instructions: 自定义指令

        Returns:
            聚合后的完整Prompt
        """
        components = []

        # 1. ElasticArchitect组件
        elastic = self._get_elastic_outline(chapter_num, target_chapters)
        components.append(PromptComponent("elastic_architect", 1, elastic))

        # 2. RhythmDesigner组件
        rhythm = self._get_rhythm_designer(emotion_prompt, emotional_debt)
        components.append(PromptComponent("rhythm_designer", 2, rhythm))

        # 3. EmotionalContinuityGuardian组件
        continuity = self._get_emotional_continuity_check(chapter_num, recent_debts)
        components.append(PromptComponent("emotion_continuity", 3, continuity))

        # 4. StyleSkill组件
        style = self._get_style_signature(emotional_vector)
        components.append(PromptComponent("style_skill", 4, style))

        # 5. 自定义指令
        if custom_instructions:
            components.append(PromptComponent("custom", 5, custom_instructions))

        # 5.5. 技能Prompt (从 .opencode/skills/ 加载)
        try:
            active_skills = self.load_active_skills()
            if active_skills:
                skill_section = self.get_skill_prompt_section(active_skills)
                components.append(PromptComponent("skills", 5, skill_section))
                logger.info(f"Loaded {len(active_skills)} skills for chapter {chapter_num}")
        except Exception as e:
            logger.warning(f"Failed to load skills: {e}")

        # 6. 世界状态摘要（从 StateSnapshotManager 加载）
        try:
            state_summary = self.get_state_summary(chapter_num)
            if state_summary:
                components.append(PromptComponent("world_state", 4, state_summary))
        except Exception as e:
            logger.warning(f"Failed to load state summary: {e}")

        # 7. 防截断规则（最高优先级）
        anti_truncation_rule = """<rule>你必须完整地结束本章，严禁在句子中间或对话中间截断！如果接近字数上限，请立刻收尾并输出完整的句号。最后一段必须逻辑完整。绝对禁止输出被切断的句子！</rule>"""
        components.append(PromptComponent("anti_truncation", 0, anti_truncation_rule))

        # 按优先级排序
        components.sort(key=lambda x: x.priority)

        # 组装最终Prompt
        header = f"""你是一位专业的网络小说作家。请根据以下信息创作第{chapter_num}章。

【创作要求】
- 字数：3000-6000字
- 语言：简体中文
- 风格：网文风格，节奏明快

"""

        body = "\n".join(c.content for c in components)

        footer = """
【输出格式】
请直接输出章节内容，无需额外说明。
重要提醒：在输出任何内容之前，请确保你已经完整地构思了这一章的全部内容。
"""

        final_prompt = header + body + footer

        logger.info(f"Assembled prompt for chapter {chapter_num}: ~{len(final_prompt)} chars, "
                   f"{len(final_prompt)//4} estimated tokens")

        return final_prompt

    def assemble_chapter_prompt(
        self,
        chapter_num: int,
        context: Dict[str, Any]
    ) -> str:
        """
        便捷接口：组装章节Prompt

        Args:
            chapter_num: 章节编号
            context: 上下文字典，包含：
                - target_chapters: 目标章节数
                - emotional_debt: 情绪债务
                - emotion_prompt: 情绪指令
                - recent_debts: 最近债务列表
                - emotional_vector: 情绪向量
                - custom_instructions: 自定义指令

        Returns:
            聚合后的Prompt
        """
        return self.assemble_emotion_writer_prompt(
            chapter_num=chapter_num,
            target_chapters=context.get("target_chapters", 50),
            emotional_debt=context.get("emotional_debt", 0.0),
            emotion_prompt=context.get("emotion_prompt", ""),
            recent_debts=context.get("recent_debts", []),
            emotional_vector=context.get("emotional_vector"),
            custom_instructions=context.get("custom_instructions", "")
        )

    def estimate_tokens(self, text: str) -> int:
        """估算token数量（中文字约等于1.5个token）"""
        # 简单估算：中文1字≈1.5token，英文1词≈1.3token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 1.5 + other_chars * 1.3)
