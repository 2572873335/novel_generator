"""
Emotion Writer - 单次API调用场景写作
整合PromptAssembler和EmotionTracker，实现单次API调用完成场景写作

解决：L2→L3 多层调用的问题
核心：一次Prompt聚合 + 一次API调用
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class WritingContext:
    """写作上下文"""
    chapter_num: int
    target_chapters: int
    project_dir: str

    # 情绪相关
    emotional_debt: float = 0.0
    emotion_prompt: str = ""
    recent_debts: List[float] = None
    emotional_vector: Dict = None

    # 世界观相关
    world_state: Dict = None

    # 额外约束
    custom_instructions: str = ""

    def __post_init__(self):
        if self.recent_debts is None:
            self.recent_debts = []
        if self.world_state is None:
            self.world_state = {}


class EmotionWriter:
    """
    单次API调用场景写作器

    核心优势：
    1. PromptAssembler: 聚合多个Skill指令为单次Prompt
    2. 单次API调用: 减少Token消耗和延迟
    3. 整合情绪追踪: 实时计算情绪债务

    工作流程：
    1. 组装Prompt (PromptAssembler)
    2. 调用LLM (单次)
    3. 计算情绪值 (EmotionTracker)
    4. 记录事件 (WorldBible)
    """

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = Path(project_dir)

        # 延迟导入，避免循环依赖
        from core.prompt_assembler import PromptAssembler
        from core.emotion_tracker import EmotionTracker
        from core.world_bible import WorldBible

        self.prompt_assembler = PromptAssembler(project_dir)
        self.emotion_tracker = EmotionTracker(project_dir, llm_client)
        self.world_bible = WorldBible(project_dir)

        # 输出目录
        self.chapters_dir = self.project_dir / "chapters"
        self.chapters_dir.mkdir(exist_ok=True)

    def write_chapter(
        self,
        context: WritingContext,
        previous_chapter: str = ""
    ) -> Dict[str, Any]:
        """
        写作单章 - 单次API调用

        Args:
            context: 写作上下文
            previous_chapter: 上一章内容（用于连续性）

        Returns:
            写作结果
        """
        chapter_num = context.chapter_num

        logger.info(f"Starting chapter {chapter_num} - single API call mode")

        # Step 1: 组装Prompt
        prompt = self.prompt_assembler.assemble_chapter_prompt(
            chapter_num=chapter_num,
            context={
                "target_chapters": context.target_chapters,
                "emotional_debt": context.emotional_debt,
                "emotion_prompt": context.emotion_prompt,
                "recent_debts": context.recent_debts,
                "emotional_vector": context.emotional_vector,
                "custom_instructions": context.custom_instructions,
            }
        )

        # 添加上一章摘要（如果有）
        if previous_chapter:
            # 提取摘要
            summary = self._extract_summary(previous_chapter)
            prompt += f"\n\n【前情提要】\n{summary}"

        # Step 2: 单次API调用
        try:
            logger.debug(f"Calling LLM for chapter {chapter_num}")
            # 使用更大的max_tokens确保完整输出
            response = self.llm.generate(prompt, max_tokens=8192)

            # 解析响应
            if hasattr(response, 'content'):
                chapter_content = response.content
            elif isinstance(response, dict):
                chapter_content = response.get('content', response.get('text', ''))
            else:
                chapter_content = str(response)

            # Step 2.5: 后处理 - 清理不完整的句子
            chapter_content = self._clean_incomplete_sentences(chapter_content)

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "chapter": chapter_num
            }

        # Step 3: 计算情绪值
        emotion_result = self.emotion_tracker.track_chapter_emotion(
            chapter_num=chapter_num,
            text=chapter_content
        )

        # Step 4: 提取并记录关键事件
        events = self._extract_events(chapter_content, chapter_num)
        for event in events:
            self.world_bible.record_event(event)

        # Step 5: 保存章节
        chapter_file = self.chapters_dir / f"chapter_{chapter_num}.json"
        chapter_data = {
            "chapter": chapter_num,
            "content": chapter_content,
            "emotion": {
                "net_debt": emotion_result["net_debt"],
                "payoff_density": emotion_result["payoff_density"],
                "state": emotion_result["state"]
            },
            "events": [e.to_dict() for e in events],
            "created_at": datetime.now().isoformat()
        }

        chapter_file.write_text(
            json.dumps(chapter_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        logger.info(f"Chapter {chapter_num} completed: {len(chapter_content)} chars, "
                   f"emotion state: {emotion_result['state']}")

        return {
            "success": True,
            "chapter": chapter_num,
            "content": chapter_content,
            "emotion": emotion_result,
            "events_count": len(events),
            "word_count": len(chapter_content)
        }

    def write_chapter_with_retry(
        self,
        context: WritingContext,
        max_retries: int = 3,
        feedback: str = ""
    ) -> Dict[str, Any]:
        """
        带重试的写作

        Args:
            context: 写作上下文
            max_retries: 最大重试次数
            feedback: 上次失败的反馈

        Returns:
            写作结果
        """
        for attempt in range(max_retries):
            try:
                # 如果有反馈，添加到上下文
                if feedback and attempt > 0:
                    context.custom_instructions += f"\n\n【重试{attempt}】请特别注意以下问题：\n{feedback}"

                result = self.write_chapter(context)

                if result["success"]:
                    return result

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                feedback = str(e)

        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts",
            "chapter": context.chapter_num
        }

    def _clean_incomplete_sentences(self, text: str) -> str:
        """清理不完整的句子，防止章节被截断"""
        if not text:
            return text

        # 移除可能的截断标记
        text = text.strip()

        # 检查是否被截断（没有以完整标点结尾）
        last_char = text[-1] if text else ""
        if last_char not in "。！？.":
            # 尝试找到最后一个完整句子
            # 查找最后一个句号、问号、感叹号
            last_period = max(
                text.rfind('。'),
                text.rfind('！'),
                text.rfind('？'),
                text.rfind('."'),
                text.rfind('!'),
                text.rfind('?')
            )

            if last_period > len(text) * 0.5:  # 确保不是太短
                text = text[:last_period + 1]

        # 移除可能被切断的对话（如 "他说--" 或 "她说"""）
        import re
        # 移除不完整的对话（以引号开头但没有正确结尾）
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 检查是否有未闭合的引号
            open_quotes = line.count('"') + line.count('"') + line.count('"')
            if open_quotes % 2 != 0:
                # 找到最后一个引号位置，截断
                last_quote = max(line.rfind('"'), line.rfind('"'), line.rfind('"'))
                if last_quote > 0:
                    line = line[:last_quote + 1]
            cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)

        # 最终确保以完整标点结尾
        text = text.strip()
        if text and text[-1] not in "。！？.!??"" ":
            # 找到最后一个完整句子
            last_punct = max(
                text.rfind('。'),
                text.rfind('！'),
                text.rfind('？'),
                text.rfind('."'),
                text.rfind('!"'),
                text.rfind('?"')
            )
            if last_punct > 0:
                text = text[:last_punct + 1]

        return text

    def _extract_summary(self, text: str, max_length: int = 300) -> str:
        """提取章节摘要"""
        # 简单实现：取前200字 + 后100字
        if len(text) <= max_length:
            return text

        # 尝试在句号处截断
        first_part = text[:150]
        last_part = text[-100:]

        # 找到最近的句号
        last_period = first_part.rfind('。')
        if last_period > 100:
            first_part = first_part[:last_period + 1]

        return first_part + "..." + last_part

    def _extract_events(self, text: str, chapter: int) -> List:
        """从文本中提取关键事件"""
        from core.world_bible import Event, EventType

        events = []

        # 简单的基于关键词的事件提取
        # 实际项目中可以使用更复杂的NLP

        # 境界升级
        upgrade_keywords = ["突破到", "晋升", "升级到", "进阶", "踏入"]
        for keyword in upgrade_keywords:
            if keyword in text:
                # 简单提取
                idx = text.find(keyword)
                context = text[max(0, idx-20):idx+30]
                events.append(Event(
                    event_type=EventType.REALM_UPGRADE.value,
                    chapter=chapter,
                    entity_id="protagonist",  # 简化
                    entity_name="主角",
                    description=f"境界突破: {context}",
                    emotional_impact=2.0
                ))
                break

        # 角色死亡
        death_keywords = ["死了", "陨落", "身亡", "死亡"]
        for keyword in death_keywords:
            if keyword in text:
                idx = text.find(keyword)
                context = text[max(0, idx-20):idx+20]
                events.append(Event(
                    event_type=EventType.CHARACTER_DEATH.value,
                    chapter=chapter,
                    entity_id="unknown",
                    entity_name=context[:10],
                    description=f"角色死亡: {context}",
                    emotional_impact=-2.0
                ))
                break

        # 获得宝物
        treasure_keywords = ["获得了", "得到", "收获", "获得"]
        for keyword in treasure_keywords:
            if keyword in text and any(t in text for t in ["宝物", "功法", "灵宝", "神器"]):
                events.append(Event(
                    event_type=EventType.TREASURE_OBTAINED.value,
                    chapter=chapter,
                    entity_id="protagonist",
                    entity_name="主角",
                    description="获得宝物/功法",
                    emotional_impact=1.5
                ))
                break

        return events

    def get_context_for_chapter(
        self,
        chapter_num: int,
        target_chapters: int
    ) -> WritingContext:
        """
        获取章节写作上下文

        Args:
            chapter_num: 章节编号
            target_chapters: 目标章节数

        Returns:
            WritingContext
        """
        # 获取情绪上下文
        emotion_prompt = self.emotion_tracker.get_emotion_prompt_for_chapter(chapter_num)
        recent_debts = self.emotion_tracker.ledger.get_recent_debt_trend(5)

        # 获取情绪向量
        emotional_vector = {
            "base_tone": self.emotion_tracker.ledger.emotional_vector.base_tone,
            "tension": self.emotion_tracker.ledger.emotional_vector.tension,
            "triggers": self.emotion_tracker.ledger.emotional_vector.triggers
        }

        return WritingContext(
            chapter_num=chapter_num,
            target_chapters=target_chapters,
            project_dir=str(self.project_dir),
            emotional_debt=self.emotion_tracker.ledger.net_debt,
            emotion_prompt=emotion_prompt,
            recent_debts=recent_debts,
            emotional_vector=emotional_vector
        )
