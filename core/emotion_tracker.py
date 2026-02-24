"""
Emotion Tracker - 情绪债务账本
严格Python计算，LLM只接收文本化结果

解决LLM不擅长精确计算的问题，所有计算在Python中完成
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """情绪状态枚举"""
    EXTREMELY_REPRESSED = "极度压抑"  # 情绪债务极高
    REPRESSED = "压抑"                # 情绪债务较高
    CAUTIOUS = "谨慎"                  # 情绪债务中等
    NEUTRAL = "中性"                   # 情绪债务平衡
    OPTIMISTIC = "乐观"                # 有一定爽点
    EXCITED = "兴奋"                   # 爽点较多
    EUPHORIC = "狂喜"                  # 大量爽点爆发


@dataclass
class EmotionalVector:
    """情绪向量"""
    base_tone: str = "中性"           # 基础调性
    tension: float = 50.0              # 紧张度 0-100
    decay_rate: float = 0.3            # 每章衰减率
    triggers: List[str] = field(default_factory=list)  # 触发器
    chapter_history: List[Dict] = field(default_factory=list)  # 历史记录


@dataclass
class EmotionalDebtRecord:
    """情绪债务记录"""
    chapter: int
    accumulated_pressure: float   # 累积压抑值
    accumulated_payoff: float    # 累积爽点值
    net_debt: float              # 净债务
    payoff_density: float        # 爽点密度
    state: EmotionalState        # 情绪状态


class EmotionalDebtLedger:
    """
    情绪债务账本 - 严格Python计算

    核心原则：
    1. 所有数值计算在Python中完成
    2. LLM只接收文本化的情绪指令
    3. 每章自动衰减情绪债务
    """

    # 爽点关键词及权重
    PAYOFF_KEYWORDS = {
        # 核心爽点 (权重高)
        "打脸": 3.0, "逆袭": 3.0, "突破": 2.5, "复仇": 2.5,
        "反转": 2.0, "秒杀": 2.5, "碾压": 2.0, "爆发": 2.0,
        "顿悟": 2.0, "觉醒": 2.0, "揭露": 2.0, "反转": 2.0,
        # 次级爽点
        "胜利": 1.5, "收获": 1.5, "成长": 1.5, "认可": 1.5,
        "惊喜": 1.0, "奇遇": 1.5, "宝物": 1.0, "传承": 1.5,
        # 日常爽点
        "有趣": 0.5, "搞笑": 0.5, "甜蜜": 0.5, "温暖": 0.5,
    }

    # 压抑关键词及权重
    PRESSURE_KEYWORDS = {
        # 核心压抑
        "死亡": 3.0, "失败": 2.5, "失去": 2.5, "背叛": 3.0,
        "危机": 2.0, "困境": 2.0, "强敌": 2.0, "压迫": 2.0,
        # 次级压抑
        "焦虑": 1.5, "担忧": 1.5, "恐惧": 1.5, "悲伤": 2.0,
        "痛苦": 2.0, "绝望": 2.5, "无奈": 1.5, "纠结": 1.0,
    }

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.ledger_file = self.project_dir / "emotion_ledger.json"

        # 核心状态
        self.accumulated_pressure: float = 0.0   # 累积压抑值
        self.accumulated_payoff: float = 0.0    # 累积爽点值
        self.net_debt: float = 0.0              # 净债务
        self.decay_rate: float = 0.3             # 衰减率

        # 情绪向量
        self.emotional_vector = EmotionalVector()

        # 历史记录
        self.records: List[EmotionalDebtRecord] = []

        # 加载已有账本
        self._load_ledger()

    def _load_ledger(self):
        """加载已有账本"""
        if self.ledger_file.exists():
            try:
                data = json.loads(self.ledger_file.read_text(encoding="utf-8"))
                self.accumulated_pressure = data.get("accumulated_pressure", 0.0)
                self.accumulated_payoff = data.get("accumulated_payoff", 0.0)
                self.net_debt = data.get("net_debt", 0.0)
                self.decay_rate = data.get("decay_rate", 0.3)
                self.records = [
                    EmotionalDebtRecord(**r) for r in data.get("records", [])
                ]
                logger.info(f"Loaded emotion ledger: debt={self.net_debt}")
            except Exception as e:
                logger.warning(f"Failed to load ledger: {e}")

    def _save_ledger(self):
        """保存账本"""
        data = {
            "accumulated_pressure": self.accumulated_pressure,
            "accumulated_payoff": self.accumulated_payoff,
            "net_debt": self.net_debt,
            "decay_rate": self.decay_rate,
            "records": [
                {
                    "chapter": r.chapter,
                    "accumulated_pressure": r.accumulated_pressure,
                    "accumulated_payoff": r.accumulated_payoff,
                    "net_debt": r.net_debt,
                    "payoff_density": r.payoff_density,
                    "state": r.state.value
                }
                for r in self.records
            ],
            "last_updated": datetime.now().isoformat()
        }
        self.ledger_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def apply_decay(self):
        """每章自动衰减30%情绪债务"""
        self.accumulated_pressure *= (1 - self.decay_rate)
        self.net_debt = self.accumulated_pressure - self.accumulated_payoff
        logger.debug(f"Decay applied: pressure={self.accumulated_pressure:.1f}, debt={self.net_debt:.1f}")

    def calculate_emotion_from_text(self, text: str, chapter_num: int) -> EmotionalDebtRecord:
        """
        从文本计算情绪值 - Python精确计算

        Args:
            text: 章节文本
            chapter_num: 章节编号

        Returns:
            EmotionalDebtRecord: 情绪债务记录
        """
        # 计算爽点值
        payoff_value = 0.0
        for keyword, weight in self.PAYOFF_KEYWORDS.items():
            if keyword in text:
                payoff_value += weight

        # 计算压抑值
        pressure_value = 0.0
        for keyword, weight in self.PRESSURE_KEYWORDS.items():
            if keyword in text:
                pressure_value += weight

        # 计算爽点密度 (每千字)
        char_count = len(text)
        word_count = char_count / 2  # 估算中文字数
        payoff_density = (payoff_value / word_count * 1000) if word_count > 0 else 0.0

        # 累加到总账本
        self.accumulated_pressure += pressure_value
        self.accumulated_payoff += payoff_value
        self.net_debt = self.accumulated_pressure - self.accumulated_payoff

        # 确定情绪状态
        state = self._determine_emotional_state()

        # 记录
        record = EmotionalDebtRecord(
            chapter=chapter_num,
            accumulated_pressure=self.accumulated_pressure,
            accumulated_payoff=self.accumulated_payoff,
            net_debt=self.net_debt,
            payoff_density=payoff_density,
            state=state
        )
        self.records.append(record)

        # 应用衰减
        self.apply_decay()

        # 保存账本
        self._save_ledger()

        logger.info(f"Chapter {chapter_num}: payoff={payoff_value:.1f}, pressure={pressure_value:.1f}, "
                   f"net_debt={self.net_debt:.1f}, state={state.value}")

        return record

    def _determine_emotional_state(self) -> EmotionalState:
        """根据净债务确定情绪状态"""
        if self.net_debt > 80:
            return EmotionalState.EXTREMELY_REPRESSED
        elif self.net_debt > 50:
            return EmotionalState.REPRESSED
        elif self.net_debt > 20:
            return EmotionalState.CAUTIOUS
        elif self.net_debt > -20:
            return EmotionalState.NEUTRAL
        elif self.net_debt > -50:
            return EmotionalState.OPTIMISTIC
        elif self.net_debt > -80:
            return EmotionalState.EXCITED
        else:
            return EmotionalState.EUPHORIC

    def to_prompt_text(self) -> str:
        """
        将计算结果转化为LLM可理解的文本指令

        这是核心接口 - LLM只看到文本化的情绪指令
        """
        state = self._determine_emotional_state()

        # 根据状态生成不同指令
        if state == EmotionalState.EXTREMELY_REPRESSED:
            instruction = (
                f"⚠️ 极度警告：情绪债务极高({self.net_debt:.1f})！"
                f"本章必须安排高强度爽点爆发！"
                f"建议：逆袭打脸/实力突破/揭露真相/宝物收获"
            )
        elif state == EmotionalState.REPRESSED:
            instruction = (
                f"⚠️ 警告：情绪债务较高({self.net_debt:.1f})。"
                f"本章需要安排爽点，建议："
                f"小高潮/角色成长/敌人受挫/获得认可"
            )
        elif state == EmotionalState.CAUTIOUS:
            instruction = (
                f"ℹ️ 注意：情绪债务中等({self.net_debt:.1f})。"
                f"保持节奏，可以安排小爽点"
            )
        elif state == EmotionalState.NEUTRAL:
            instruction = (
                f"✅ 状态：情绪平衡({self.net_debt:.1f})。"
                f"按大纲正常推进"
            )
        elif state == EmotionalState.OPTIMISTIC:
            instruction = (
                f"✅ 良好：情绪乐观({self.net_debt:.1f})。"
                f"可以安排适度压抑，为后续高潮做准备"
            )
        elif state == EmotionalState.EXCITED:
            instruction = (
                f"🔥 状态：情绪兴奋({self.net_debt:.1f})。"
                f"爽点密集，注意节奏把控"
            )
        else:  # EUPHORIC
            instruction = (
                f"🎉 极好：情绪狂喜({self.net_debt:.1f})。"
                f"爽点大爆发！可考虑安排小回落"
            )

        # 添加情绪向量信息
        vector_info = (
            f"\n\n[情绪向量参考]\n"
            f"- 基础调性: {self.emotional_vector.base_tone}\n"
            f"- 紧张度: {self.emotional_vector.tension}/100\n"
            f"- 触发器: {', '.join(self.emotional_vector.triggers[-3:]) if self.emotional_vector.triggers else '无'}"
        )

        return instruction + vector_info

    def get_recent_debt_trend(self, n: int = 5) -> List[float]:
        """获取最近N章的债务趋势"""
        return [r.net_debt for r in self.records[-n:]]

    def get_payoff_density_trend(self, n: int = 5) -> List[float]:
        """获取最近N章的爽点密度趋势"""
        return [r.payoff_density for r in self.records[-n:]]

    def reset(self):
        """重置账本"""
        self.accumulated_pressure = 0.0
        self.accumulated_payoff = 0.0
        self.net_debt = 0.0
        self.records = []
        self._save_ledger()
        logger.info("Emotion ledger reset")


class EmotionTracker:
    """
    情绪追踪器 - 整合情绪债务账本与世界状态
    """

    def __init__(self, project_dir: str, llm_client=None):
        self.project_dir = Path(project_dir)
        self.llm_client = llm_client
        self.ledger = EmotionalDebtLedger(project_dir)

    def track_chapter_emotion(self, chapter_num: int, text: str) -> Dict[str, Any]:
        """
        追踪章节情绪

        Args:
            chapter_num: 章节编号
            text: 章节文本

        Returns:
            情绪追踪结果
        """
        record = self.ledger.calculate_emotion_from_text(text, chapter_num)

        return {
            "chapter": chapter_num,
            "net_debt": record.net_debt,
            "payoff_density": record.payoff_density,
            "state": record.state.value,
            "prompt_instruction": self.ledger.to_prompt_text(),
            "recent_trend": self.ledger.get_recent_debt_trend(5),
            "requires_payoff": record.net_debt > 50
        }

    def get_emotion_prompt_for_chapter(self, chapter_num: int) -> str:
        """获取章节的情绪Prompt"""
        return self.ledger.to_prompt_text()

    def update_emotional_vector(self, base_tone: str, tension: float, triggers: List[str] = None):
        """更新情绪向量"""
        self.ledger.emotional_vector.base_tone = base_tone
        self.ledger.emotional_vector.tension = tension
        if triggers:
            self.ledger.emotional_vector.triggers.extend(triggers)
