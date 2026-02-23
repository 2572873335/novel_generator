"""
A/B Testing Framework for Opening Variants

This module provides functionality to test and analyze different opening variants
for web novels, based on Qidian's "Golden Three Chapters" principles.

Features:
- Generate multiple opening variants
- Score openings based on multiple dimensions
- Compare and rank variants
- Track performance metrics
- Provide improvement suggestions

Usage:
    ab_tester = ABTestingFramework(project_dir)
    variants = ab_tester.generate_variants(chapter_content, num_variants=3)
    results = ab_tester.analyze_variants(variants)
    best = ab_tester.select_best(results)
"""

import json
import re
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class OpeningType(Enum):
    """开篇类型"""

    ACTION = "action"  # 动作开场
    DIALOGUE = "dialogue"  # 对话开场
    SCENE = "scene"  # 场景描写开场
    MONOLOGUE = "monologue"  # 内心独白开场
    INCITING = "inciting"  # 冲突诱发开场
    MYSTERY = "mystery"  # 悬念开场


class HookType(Enum):
    """钩子类型"""

    CLIFFHANGER = "cliffhanger"  # 悬念
    QUESTION = "question"  # 提问
    CONFLICT = "conflict"  # 冲突
    REVEAL = "reveal"  # 揭示
    THREAT = "threat"  # 威胁


@dataclass
class OpeningVariant:
    """开篇变体"""

    variant_id: str
    content: str
    opening_type: OpeningType
    hooks: List[HookType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OpeningScore:
    """开篇评分"""

    variant_id: str

    # 黄金三章维度
    three_second_rule: float = 0.0  # 三秒定律（主角名出现）
    hook_density: float = 0.0  # 钩子密度
    conflict_early: float = 0.0  # 冲突提前
    info_density: float = 0.0  # 信息密度
    golden_finger: float = 0.0  # 金手指亮相

    # 附加维度
    readability: float = 0.0  # 可读性
    engagement: float = 0.0  # 吸引力
    originality: float = 0.0  # 新颖度

    total_score: float = 0.0

    # 详细分析
    analysis: Dict[str, Any] = field(default_factory=dict)

    def calculate_total(self):
        """计算总分"""
        weights = {
            "three_second_rule": 0.15,
            "hook_density": 0.20,
            "conflict_early": 0.15,
            "info_density": 0.10,
            "golden_finger": 0.15,
            "readability": 0.10,
            "engagement": 0.10,
            "originality": 0.05,
        }

        self.total_score = sum(
            getattr(self, key) * weight for key, weight in weights.items()
        )


@dataclass
class ABTestResult:
    """A/B测试结果"""

    variant_id: str
    scores: OpeningScore
    rank: int
    is_recommended: bool
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class ABTestingFramework:
    """
    A/B测试框架

    用于生成、测试和优化小说开篇
    """

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.results_file = self.project_dir / "ab_test_results.json"

        # 加载历史结果
        self.historical_results = self._load_results()

        # 开篇模式库
        self.opening_patterns = self._init_patterns()

    def _load_results(self) -> List[Dict]:
        """加载历史测试结果"""
        if self.results_file.exists():
            with open(self.results_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_results(self):
        """保存测试结果"""
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(self.historical_results, f, ensure_ascii=False, indent=2)

    def _init_patterns(self) -> Dict[str, Any]:
        """初始化开篇模式库"""
        return {
            "action_opening": {
                "type": OpeningType.ACTION,
                "patterns": [
                    r"(\w+)突然(?:\s*)(?:冲|杀|闯|奔)",
                    r"(\w+)手持(?:.*?)冲入",
                    r"一道(?:.*?)光芒",
                    r"(?:突然|猛然|骤然)发生变化",
                ],
                "description": "以激烈动作开场，快速抓住读者注意力",
            },
            "dialogue_opening": {
                "type": OpeningType.DIALOGUE,
                "patterns": [
                    r'"([^"]+)"',
                    r"「([^」]+)」",
                    r"(\w+)说道：[「\"]",
                    r"(\w+)问道：[「\"]",
                ],
                "description": "以对话开场，快速建立人物和冲突",
            },
            "scene_opening": {
                "type": OpeningType.SCENE,
                "patterns": [
                    r"(?:天空|大地|山岳|河流|森林)(?:之中|之上|之间)",
                    r"(?:清晨|黄昏|夜晚|黎明|正午)",
                    r"(?:远处|面前|身后|头顶|脚下)",
                ],
                "description": "以场景描写建立世界观",
            },
            "monologue_opening": {
                "type": OpeningType.MONOLOGUE,
                "patterns": [
                    r"(?:心想|暗道|思虑|想到)",
                    r"(?:难道|难道说|难不成)",
                    r"(?:必须|一定要|一定要)",
                ],
                "description": "以内心独白展示主角心理",
            },
            "inciting_opening": {
                "type": OpeningType.INCITING,
                "patterns": [
                    r"((?:挑战|考核|测试|大选|比试|比武))",
                    r"((?:危险|危机|灾难|变故|突变))",
                    r"((?:仇敌|敌人|对手| rival))出现",
                ],
                "description": "以冲突事件诱发故事",
            },
            "mystery_opening": {
                "type": OpeningType.MYSTERY,
                "patterns": [
                    r"(?:奇怪|怪异|异常|可疑)",
                    r"(?:秘密|谜团|真相|隐藏)",
                    r"(?:为何|为什么|怎么回事)",
                ],
                "description": "以悬念引导读者继续阅读",
            },
        }

    def generate_variants(
        self, original_content: str, num_variants: int = 3, preserve_style: bool = True
    ) -> List[OpeningVariant]:
        """生成开篇变体

        Args:
            original_content: 原始开篇内容
            num_variants: 生成变体数量
            preserve_style: 是否保留原文风格

        Returns:
            变体列表
        """
        variants = []

        # 分析原文
        original_type = self._detect_opening_type(original_content)

        # 生成不同类型的变体
        target_types = self._select_target_types(original_type, num_variants)

        for i, target_type in enumerate(target_types):
            variant = self._generate_variant(
                original_content, target_type, variant_num=i + 1
            )
            variants.append(variant)

        return variants

    def _detect_opening_type(self, content: str) -> OpeningType:
        """检测开篇类型"""
        scores = {}

        for pattern_name, pattern_data in self.opening_patterns.items():
            pattern_type = pattern_data["type"]
            score = 0

            for pattern in pattern_data["patterns"]:
                matches = re.findall(pattern, content)
                score += len(matches)

            scores[pattern_type] = score

        # 返回得分最高的类型
        if scores:
            return max(scores, key=scores.get)
        return OpeningType.SCENE

    def _select_target_types(
        self, original_type: OpeningType, num_variants: int
    ) -> List[OpeningType]:
        """选择目标开篇类型"""
        all_types = list(OpeningType)

        # 移除原始类型
        if original_type in all_types:
            all_types.remove(original_type)

        # 选择不同类型
        selected = [original_type]  # 保留原版
        remaining = all_types

        while len(selected) < num_variants and remaining:
            # 优先选择与原文差异大的类型
            selected.append(remaining.pop(0))

        return selected[:num_variants]

    def _generate_variant(
        self, content: str, target_type: OpeningType, variant_num: int
    ) -> OpeningVariant:
        """生成单个变体"""
        # 生成唯一ID
        variant_id = hashlib.md5(
            f"{content[:50]}_{target_type.value}_{variant_num}".encode()
        ).hexdigest()[:8]

        # 检测钩子
        hooks = self._detect_hooks(content)

        # 元数据
        metadata = {
            "target_type": target_type.value,
            "original_type": self._detect_opening_type(content).value,
            "word_count": len(content),
            "variant_num": variant_num,
        }

        return OpeningVariant(
            variant_id=variant_id,
            content=content,  # 实际应用中这里会使用LLM重写
            opening_type=target_type,
            hooks=hooks,
            metadata=metadata,
        )

    def _detect_hooks(self, content: str) -> List[HookType]:
        """检测内容中的钩子"""
        hooks = []

        hook_patterns = {
            HookType.CLIFFHANGER: [
                r"(?:然而|但是|就在这时|突然|紧接着)",
                r"(?:到底|究竟|会发生|如何)",
                r"(?:危险|危机|威胁)即将?降临",
            ],
            HookType.QUESTION: [
                r"(\w+)到底",
                r"这(?:是|究竟|到底)是",
                r"为什么会",
                r"怎(?:么|样)才能",
            ],
            HookType.CONFLICT: [
                r"(?:战斗|冲突|对抗|争夺|竞争)",
                r"(?:敌人|对手|仇人|威胁)",
                r"(?:挑战|考核|危机)",
            ],
            HookType.REVEAL: [
                r"(?:原来|竟然|居然|竟然)是",
                r"(?:秘密|真相|秘密)被",
                r"(?:发现|揭示|暴露)",
            ],
            HookType.THREAT: [
                r"(?:威胁|危险|危机|灾难)即将?降临",
                r"(?:死亡|毁灭|灭亡|消亡)",
                r"(?:必须|一定要|不得不)",
            ],
        }

        for hook_type, patterns in hook_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    hooks.append(hook_type)
                    break

        return hooks

    def analyze_variant(self, variant: OpeningVariant) -> OpeningScore:
        """分析单个变体"""
        content = variant.content

        score = OpeningScore(variant_id=variant.variant_id)

        # 1. 三秒定律：前500字出现主角名
        first_500 = content[:500]
        score.three_second_rule = self._check_three_second_rule(first_500)

        # 2. 钩子密度：每300字至少一个钩子
        score.hook_density = self._check_hook_density(content)

        # 3. 冲突提前：3000字内核心冲突
        score.conflict_early = self._check_conflict_timing(content)

        # 4. 信息密度：禁止大段说明文
        score.info_density = self._check_info_density(content)

        # 5. 金手指亮相：第1章展示核心优势
        score.golden_finger = self._check_golden_finger(content)

        # 6. 可读性
        score.readability = self._check_readability(content)

        # 7. 吸引力
        score.engagement = self._check_engagement(content, variant)

        # 8. 新颖度
        score.originality = self._check_originality(content, variant)

        # 计算总分
        score.calculate_total()

        # 详细分析
        score.analysis = {
            "word_count": len(content),
            "sentence_count": len(re.split(r"[。！？]", content)),
            "paragraph_count": len(content.split("\n\n")),
            "opening_type": variant.opening_type.value,
            "hooks_detected": [h.value for h in variant.hooks],
        }

        return score

    def analyze_variants(self, variants: List[OpeningVariant]) -> List[ABTestResult]:
        """分析所有变体"""
        results = []

        # 分析每个变体
        scores = []
        for variant in variants:
            score = self.analyze_variant(variant)
            scores.append((variant.variant_id, score))

        # 按总分排序
        scores.sort(key=lambda x: x[1].total_score, reverse=True)

        # 生成结果
        for rank, (variant_id, score) in enumerate(scores, 1):
            variant = next(v for v in variants if v.variant_id == variant_id)

            result = ABTestResult(
                variant_id=variant_id,
                scores=score,
                rank=rank,
                is_recommended=(rank == 1),
                strengths=self._extract_strengths(score),
                weaknesses=self._extract_weaknesses(score),
                suggestions=self._generate_suggestions(score, variant),
            )
            results.append(result)

        # 保存结果
        self._save_test_results(variants, results)

        return results

    def _check_three_second_rule(self, text: str) -> float:
        """检查三秒定律"""
        # 检测是否提到"我"、"他"、"主角名"等
        pronouns = ["我", "他", "她", "它", "此人", "此人"]

        # 检查是否有人名模式
        name_pattern = r"[\u4e00-\u9fa5]{2,4}(?:道|说|想|问|喊|叫)"

        if re.search(name_pattern, text):
            return 1.0

        for pronoun in pronouns:
            if pronoun in text:
                return 0.8

        return 0.3

    def _check_hook_density(self, text: str) -> float:
        """检查钩子密度"""
        # 每300字一个钩子为满分
        hook_indicators = [
            "然而",
            "但是",
            "就在这时",
            "突然",
            "紧接着",
            "到底",
            "究竟",
            "如何",
            "为什么",
            "危机",
            "危险",
            "威胁",
            "挑战",
        ]

        hook_count = sum(1 for indicator in hook_indicators if indicator in text)

        expected_hooks = len(text) / 300

        if expected_hooks == 0:
            return 1.0 if hook_count > 0 else 0.5

        ratio = min(hook_count / expected_hooks, 1.5) / 1.5

        return ratio

    def _check_conflict_timing(self, text: str) -> float:
        """检查冲突时机"""
        conflict_keywords = [
            "战斗",
            "冲突",
            "比试",
            "挑战",
            "考核",
            "危险",
            "危机",
            "敌人",
            "对手",
            "争夺",
            "比武",
            "大选",
            "测试",
        ]

        # 查找关键词首次出现位置
        first_conflict = len(text)
        for keyword in conflict_keywords:
            pos = text.find(keyword)
            if pos != -1 and pos < first_conflict:
                first_conflict = pos

        # 3000字内出现为满分
        if first_conflict > len(text):
            return 0.0

        if first_conflict < 500:
            return 1.0
        elif first_conflict < 1000:
            return 0.9
        elif first_conflict < 2000:
            return 0.7
        elif first_conflict < 3000:
            return 0.5
        else:
            return 0.3

    def _check_info_density(self, text: str) -> float:
        """检查信息密度"""
        # 连续无剧情推进的段落
        info_paragraphs = 0
        paragraphs = text.split("\n\n")

        for para in paragraphs:
            # 纯描写性段落（无人物、无动作）
            if len(para) > 200:
                has_action = any(
                    kw in para
                    for kw in ["说", "道", "想", "做", "走", "跑", "看", "听"]
                )
                has_character = any(
                    kw in para for kw in ["他", "她", "我", "人", "弟子", "长老"]
                )

                if not has_action and not has_character:
                    info_paragraphs += 1

        if not paragraphs:
            return 0.5

        bad_ratio = info_paragraphs / len(paragraphs)

        return max(0, 1.0 - bad_ratio * 3)

    def _check_golden_finger(self, text: str) -> float:
        """检查金手指"""
        golden_finger_indicators = [
            "系统",
            "系统提示",
            "觉醒",
            "传承",
            "秘密",
            "特殊",
            "天赋",
            "能力",
            "功法",
            "秘籍",
            "法宝",
            "灵宝",
            "仙器",
            "血脉",
            "体质",
        ]

        # 查找金手指关键词
        found_count = sum(
            1 for indicator in golden_finger_indicators if indicator in text
        )

        if found_count == 0:
            return 0.3
        elif found_count == 1:
            return 0.7
        else:
            return 1.0

    def _check_readability(self, text: str) -> float:
        """检查可读性"""
        # 简单指标：句子长度、段落长度
        sentences = re.split(r"[。！？]", text)
        avg_sentence_len = sum(len(s) for s in sentences) / max(len(sentences), 1)

        # 最佳句子长度 20-40 字
        if 15 <= avg_sentence_len <= 50:
            return 1.0
        elif 10 <= avg_sentence_len <= 60:
            return 0.8
        else:
            return 0.5

    def _check_engagement(self, content: str, variant: OpeningVariant) -> float:
        """检查吸引力"""
        score = 0.5

        # 开头有冲突加分
        if variant.hooks:
            score += 0.2

        # 开头有悬念加分
        if HookType.CLIFFHANGER in variant.hooks or HookType.QUESTION in variant.hooks:
            score += 0.2

        # 开头有动作加分
        if variant.opening_type == OpeningType.ACTION:
            score += 0.1

        return min(score, 1.0)

    def _check_originality(self, content: str, variant: OpeningVariant) -> float:
        """检查新颖度"""
        # 与常见模式对比
        common_opening_words = [
            "清晨",
            "黄昏",
            "夜晚",
            "天空",
            "大陆",
            "世界",
            "传说",
            "很久以前",
            "在一个",
            "这是",
        ]

        matches = sum(1 for word in common_opening_words if content.startswith(word))

        if matches == 0:
            return 1.0
        elif matches <= 1:
            return 0.7
        else:
            return 0.5

    def _extract_strengths(self, score: OpeningScore) -> List[str]:
        """提取优势"""
        strengths = []

        if score.three_second_rule >= 0.8:
            strengths.append("✓ 快速引入主角")
        if score.hook_density >= 0.7:
            strengths.append("✓ 钩子设置密集")
        if score.conflict_early >= 0.7:
            strengths.append("✓ 冲突出现及时")
        if score.golden_finger >= 0.7:
            strengths.append("✓ 金手指明确")
        if score.readability >= 0.8:
            strengths.append("✓ 文字流畅易读")

        return strengths

    def _extract_weaknesses(self, score: OpeningScore) -> List[str]:
        """提取劣势"""
        weaknesses = []

        if score.three_second_rule < 0.5:
            weaknesses.append("✗ 主角出场不够快")
        if score.hook_density < 0.4:
            weaknesses.append("✗ 钩子不足")
        if score.conflict_early < 0.5:
            weaknesses.append("✗ 冲突出现太晚")
        if score.info_density < 0.5:
            weaknesses.append("✗ 说明文过多")
        if score.golden_finger < 0.5:
            weaknesses.append("✗ 金手指不明确")

        return weaknesses

    def _generate_suggestions(
        self, score: OpeningScore, variant: OpeningVariant
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if score.three_second_rule < 0.8:
            suggestions.append("建议：在前500字内明确出现主角姓名")
        if score.hook_density < 0.6:
            suggestions.append("建议：增加悬念设置，每300字一个钩子")
        if score.conflict_early < 0.6:
            suggestions.append("建议：将核心冲突提前到3000字内")
        if score.info_density < 0.6:
            suggestions.append("建议：减少纯描写段落，增加剧情推进")
        if score.golden_finger < 0.7:
            suggestions.append("建议：在第一章明确展示主角的金手指/优势")

        # 针对开篇类型的建议
        if variant.opening_type == OpeningType.SCENE:
            suggestions.append("场景描写过多，建议增加人物互动")
        elif variant.opening_type == OpeningType.MONOLOGUE:
            suggestions.append("内心独白过多，建议增加外在冲突")

        return suggestions

    def _save_test_results(
        self, variants: List[OpeningVariant], results: List[ABTestResult]
    ):
        """保存测试结果"""
        test_result = {
            "timestamp": datetime.now().isoformat(),
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "content": v.content[:200] + "...",
                    "type": v.opening_type.value,
                    "hooks": [h.value for h in v.hooks],
                }
                for v in variants
            ],
            "results": [
                {
                    "variant_id": r.variant_id,
                    "rank": r.rank,
                    "is_recommended": r.is_recommended,
                    "scores": {
                        "three_second_rule": r.scores.three_second_rule,
                        "hook_density": r.scores.hook_density,
                        "conflict_early": r.scores.conflict_early,
                        "info_density": r.scores.info_density,
                        "golden_finger": r.scores.golden_finger,
                        "total": r.scores.total_score,
                    },
                    "strengths": r.strengths,
                    "weaknesses": r.weaknesses,
                    "suggestions": r.suggestions,
                }
                for r in results
            ],
        }

        self.historical_results.append(test_result)
        self._save_results()

    def select_best(self, results: List[ABTestResult]) -> Optional[ABTestResult]:
        """选择最佳变体"""
        if not results:
            return None

        # 返回排名第一的
        return next((r for r in results if r.rank == 1), None)

    def get_historical_analysis(self) -> Dict[str, Any]:
        """获取历史分析"""
        if not self.historical_results:
            return {"message": "暂无历史数据"}

        # 汇总统计
        total_tests = len(self.historical_results)
        recommended_types = {}

        for result in self.historical_results:
            for variant_result in result["results"]:
                if variant_result["is_recommended"]:
                    # 获取推荐的变体类型
                    variant = next(
                        v
                        for v in result["variants"]
                        if v["variant_id"] == variant_result["variant_id"]
                    )
                    vtype = variant["type"]
                    recommended_types[vtype] = recommended_types.get(vtype, 0) + 1

        return {
            "total_tests": total_tests,
            "recommended_types": recommended_types,
            "success_rate": sum(
                1
                for r in self.historical_results
                if any(vr["is_recommended"] for vr in r["results"])
            )
            / max(total_tests, 1),
        }


# ============================================================================
# 便捷函数
# ============================================================================


def quick_analyze(content: str) -> OpeningScore:
    """快速分析开篇质量"""
    framework = ABTestingFramework(".")

    # 创建临时变体
    variant = OpeningVariant(
        variant_id="temp",
        content=content,
        opening_type=framework._detect_opening_type(content),
        hooks=framework._detect_hooks(content),
    )

    return framework.analyze_variant(variant)


def compare_openings(
    contents: List[str], names: Optional[List[str]] = None
) -> List[ABTestResult]:
    """比较多个开篇

    Args:
        contents: 开篇内容列表
        names: 可选的名称列表

    Returns:
        排序后的测试结果
    """
    framework = ABTestingFramework(".")

    if names is None:
        names = [f"开篇{i + 1}" for i in range(len(contents))]

    variants = []
    for i, content in enumerate(contents):
        variant = OpeningVariant(
            variant_id=f"variant_{i}",
            content=content,
            opening_type=framework._detect_opening_type(content),
            hooks=framework._detect_hooks(content),
            metadata={"name": names[i]},
        )
        variants.append(variant)

    return framework.analyze_variants(variants)
