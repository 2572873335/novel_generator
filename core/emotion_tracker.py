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

    # 爽点关键词及权重（包含章节大纲标记）
    PAYOFF_KEYWORDS = {
        # 章节大纲标记（最高优先级）
        "(+)": 10.0, "爽点": 8.0, "高潮": 8.0, "大高潮": 10.0,
        "情绪净值(+)": 10.0, "情绪净值: (+)": 10.0,
        # 核心爽点 (权重高)
        "打脸": 3.0, "逆袭": 3.0, "突破": 2.5, "复仇": 2.5,
        "反转": 2.0, "秒杀": 2.5, "碾压": 2.0, "爆发": 2.0,
        "顿悟": 2.0, "觉醒": 2.0, "揭露": 2.0,
        # 次级爽点
        "胜利": 1.5, "收获": 1.5, "成长": 1.5, "认可": 1.5,
        "惊喜": 1.0, "奇遇": 1.5, "宝物": 1.0, "传承": 1.5,
        # 日常爽点
        "有趣": 0.5, "搞笑": 0.5, "甜蜜": 0.5, "温暖": 0.5,
    }

    # 压抑关键词及权重（包含章节大纲标记）
    PRESSURE_KEYWORDS = {
        # 章节大纲标记（最高优先级）
        "(-)": 10.0, "压抑": 8.0, "低谷": 6.0,
        "情绪净值(-)": 10.0, "情绪净值: (-)": 10.0,
        # 核心压抑
        "死亡": 3.0, "失败": 2.5, "失去": 2.5, "背叛": 3.0,
        "危机": 2.0, "困境": 2.0, "强敌": 2.0, "压迫": 2.0,
        # 次级压抑
        "焦虑": 1.5, "担忧": 1.5, "恐惧": 1.5, "悲伤": 2.0,
        "痛苦": 2.0, "绝望": 2.5, "无奈": 1.5, "纠结": 1.0,
    }

    # 过渡关键词（保持平稳）
    NEUTRAL_KEYWORDS = {
        "(0)": 5.0, "过渡": 3.0, "铺垫": 2.0, "日常": 1.0,
        "情绪净值(0)": 5.0, "情绪净值: (0)": 5.0,
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
                    EmotionalDebtRecord(
                        **{**r, "state": EmotionalState(r["state"]) if isinstance(r.get("state"), str) else r.get("state", EmotionalState.NEUTRAL)}
                    ) for r in data.get("records", [])
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
                    "state": r.state.value if isinstance(r.state, EmotionalState) else str(r.state)
                }
                for r in self.records
            ],
            "last_updated": datetime.now().isoformat()
        }
        self.ledger_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def apply_decay(self):
        """每章自动衰减30%情绪债务（对称应用到压力和爽点）"""
        self.accumulated_pressure *= (1 - self.decay_rate)
        self.accumulated_payoff *= (1 - self.decay_rate)
        self.net_debt = self.accumulated_pressure - self.accumulated_payoff
        logger.debug(f"Decay applied: pressure={self.accumulated_pressure:.1f}, payoff={self.accumulated_payoff:.1f}, debt={self.net_debt:.1f}")

    def extract_emotion_from_outline(self, outline_text: str, chapter_num: int = 0) -> float:
        """
        从章节大纲中提取情绪净值标记，如果没有大纲则使用正弦震荡模式

        支持的格式:
        - 情绪净值：(-)
        - 情绪净值：(+)
        - 情绪净值：(0)
        - (-)：压抑
        - (+)：爽点
        - (0)：过渡

        Args:
            outline_text: 章节大纲文本
            chapter_num: 章节编号（用于生成正弦震荡）

        Returns:
            float: 情绪偏移值 (+15表示爽点, -15表示压抑, 0表示过渡)
        """
        if not outline_text:
            # 如果没有大纲，使用正弦震荡模式生成情绪波动
            # 这确保即使没有大纲，情绪曲线也会呈现震荡
            return self._generate_sinusoidal_emotion(chapter_num)

        # 检查高级优先级标记 (情绪净值)
        if "情绪净值：(+)" in outline_text or "情绪净值(+)：" in outline_text:
            return 15.0  # 强爽点
        if "情绪净值：(-)" in outline_text or "情绪净值(-)" in outline_text:
            return -15.0  # 强压抑
        if "情绪净值：(0)" in outline_text or "情绪净值(0)" in outline_text:
            return 0.0  # 过渡

        # 检查简短标记 (+)/(-)achi
        if "(+)" in outline_text[:500]:  # 只检查大纲开头
            return 10.0  # 爽点
        if "(-)" in outline_text[:500]:  # 只检查大纲开头
            return -10.0  # 压抑
        if "(0)" in outline_text[:500]:
            return 0.0  # 过渡

        # 检查文字描述
        if "爽点" in outline_text or "高潮" in outline_text or "大高潮" in outline_text:
            return 8.0
        if "压抑" in outline_text or "低谷" in outline_text or "危机" in outline_text:
            return -8.0
        if "过渡" in outline_text or "铺垫" in outline_text:
            return 0.0

        # 如果大纲存在但没有情绪标记，使用正弦震荡
        return self._generate_sinusoidal_emotion(chapter_num)

    def _generate_sinusoidal_emotion(self, chapter_num: int) -> float:
        """
        生成基于章节号的正弦震荡情绪值

        这模拟了典型的网文情绪曲线：
        - 前10章压抑积累 (-)
        - 第10章小高潮 (+)
        - 11-20章继续积累 (-)
        - 第20章中高潮 (+)
        - 依此类推...

        Args:
            chapter_num: 章节编号

        Returns:
            float: 情绪偏移值
        """
        if chapter_num <= 0:
            return 0.0

        # 每10章一个周期，前半部分压抑，后半部分爽点
        # 使用正弦函数产生平滑的震荡曲线
        import math

        # 周期为20章：-10到+10的震荡
        # chapter 1-10: 负值（压抑）
        # chapter 11-20: 正值（爽点）
        # chapter 21-30: 负值（压抑）
        # 以此类推

        phase = (chapter_num - 1) / 10.0 * math.pi  # 每10章一个π相位
        emotion = math.sin(phase) * 12.0  # 振幅12

        # 确保前几章是压抑的（符合网文规律）
        if chapter_num <= 3:
            return -8.0 + chapter_num * 2  # -8, -6, -4
        elif chapter_num <= 10:
            return emotion * 0.5  # 缓和的压抑
        else:
            return emotion

    def calculate_emotion_from_text(self, text: str, chapter_num: int, outline_text: str = "") -> EmotionalDebtRecord:
        """
        从章节大纲和文本计算情绪值 - Python精确计算

        核心逻辑：情绪曲线应该反映章节的情绪方向，而不是累加值。
        使用正弦震荡模式确保曲线呈现波浪状起伏。

        Args:
            text: 章节文本
            chapter_num: 章节编号
            outline_text: 章节大纲文本（可选，用于提取情绪净值标记）

        Returns:
            EmotionalDebtRecord: 情绪债务记录
        """
        # 优先从大纲提取情绪偏移，如果没有大纲则使用正弦震荡模式
        outline_emotion = self.extract_emotion_from_outline(outline_text, chapter_num)

        # 如果大纲/正弦模式有明确情绪，使用它来主导 net_debt
        # 这是关键修改：直接使用情绪方向，而不是累加
        if outline_emotion != 0.0:
            # 使用大纲/正弦的情绪值作为基础
            # 让 net_debt 跟随情绪方向震荡
            base_emotion = outline_emotion

            # 叠加文本中检测到的关键词（作为微调）
            payoff_value = 0.0
            for keyword, weight in self.PAYOFF_KEYWORDS.items():
                if keyword in text:
                    payoff_value += weight

            pressure_value = 0.0
            for keyword, weight in self.PRESSURE_KEYWORDS.items():
                if keyword in text:
                    pressure_value += weight

            # 文本检测值作为微调（权重较低）
            text_emotion = payoff_value - pressure_value
            self.net_debt = base_emotion * 0.7 + text_emotion * 0.3
        else:
            # 没有情绪方向，使用纯文本检测（后备方案）
            payoff_value = 0.0
            for keyword, weight in self.PAYOFF_KEYWORDS.items():
                if keyword in text:
                    payoff_value += weight

            pressure_value = 0.0
            for keyword, weight in self.PRESSURE_KEYWORDS.items():
                if keyword in text:
                    pressure_value += weight

            # 累加到总账本（原有逻辑）
            self.accumulated_pressure += pressure_value
            self.accumulated_payoff += payoff_value
            self.net_debt = self.accumulated_pressure - self.accumulated_payoff

            # 应用衰减
            self.apply_decay()

        # 计算爽点密度 (每千字)
        char_count = len(text)
        word_count = char_count / 2  # 估算中文字数
        payoff_density = (payoff_value / word_count * 1000) if word_count > 0 else 0.0

        # 确定情绪状态
        state = self._determine_emotional_state()

        # 记录（保存当前的压力/爽点值供下次参考）
        record = EmotionalDebtRecord(
            chapter=chapter_num,
            accumulated_pressure=self.accumulated_pressure,
            accumulated_payoff=self.accumulated_payoff,
            net_debt=self.net_debt,
            payoff_density=payoff_density,
            state=state
        )
        self.records.append(record)

        # 保存账本
        self._save_ledger()

        logger.info(f"Chapter {chapter_num}: outline_emotion={outline_emotion:.1f}, "
                   f"net_debt={self.net_debt:.1f}, state={state.value if isinstance(state, EmotionalState) else state}")

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

    def track_chapter_emotion(self, chapter_num: int, text: str, outline_text: str = "") -> Dict[str, Any]:
        """
        追踪章节情绪

        Args:
            chapter_num: 章节编号
            text: 章节文本
            outline_text: 章节大纲文本（可选，用于提取情绪净值标记）

        Returns:
            情绪追踪结果
        """
        record = self.ledger.calculate_emotion_from_text(text, chapter_num, outline_text)

        return {
            "chapter": chapter_num,
            "net_debt": record.net_debt,
            "payoff_density": record.payoff_density,
            "state": record.state.value if isinstance(record.state, EmotionalState) else str(record.state),
            "prompt_instruction": self.ledger.to_prompt_text(),
            "recent_trend": self.ledger.get_recent_debt_trend(5),
            "requires_payoff": record.net_debt > 50,
            "outline_emotion": self.ledger.extract_emotion_from_outline(outline_text, chapter_num)
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
