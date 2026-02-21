"""
SeniorEditorAgent - 起点金牌资深编辑「锐评官」
对小说进行多维度锐评，提供签约建议和修改方向
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class ReviewDimension:
    """评审维度"""

    name: str
    score: float
    weight: float
    issues: List[Dict[str, Any]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


@dataclass
class ChapterAnalysis:
    """章节分析"""

    chapter_number: int
    word_count: int
    hook_present: bool
    conflict_present: bool
    emotion_score: float
    pacing: str


@dataclass
class SeniorEditorReport:
    """资深编辑审稿报告"""

    novel_title: str
    overall_score: float
    verdict: str
    contract_grade: str
    predicted_retention: float
    dimensions: List[ReviewDimension]
    fatal_flaws: List[Dict[str, Any]]
    strengths: List[str]
    improvement_plan: List[Dict[str, Any]]
    chapter_analyses: List[ChapterAnalysis]
    editor_note: str
    recommendations: Dict[str, Any]


class SeniorEditorAgent:
    """
    起点金牌资深编辑「锐评官」

    8年+从业经验，经手作品总收藏破千万
    擅长玄幻/仙侠/都市品类

    评审维度（百分制）：
    1. 开篇抓人（25%）- 黄金三章、3秒定律
    2. 逻辑自洽（20%）- 战力、时间线、设定
    3. 爽感设计（20%）- 期待感、爽点密度
    4. 人设鲜活（15%）- 人格一致性、反派塑造
    5. 更新潜力（10%）- 世界观延展
    6. 商业适配（10%）- 品类契合度
    """

    DIMENSION_WEIGHTS = {
        "开篇抓人": 0.25,
        "逻辑自洽": 0.20,
        "爽感设计": 0.20,
        "人设鲜活": 0.15,
        "更新潜力": 0.10,
        "商业适配": 0.10,
    }

    TOXIC_PATTERNS = [
        (r"绿帽|戴帽|被.{0,3}睡|被.{0,3}上|被.{0,3}玩", "绿帽流毒点"),
        (r"圣母.{0,5}心|以德报怨|原谅.{0,3}杀|放过.{0,3}仇", "圣母婊毒点"),
        (r"系统.{0,10}话痨|系统.{0,10}啰嗦|系统.{0,5}废话", "系统话痨毒点"),
        (r"虐主.{0,5}过度|主角.{0,5}惨.{0,5}无.{0,5}爽", "虐主过度毒点"),
        (r"双标|主角.{0,5}杀人.{0,5}有理|配角.{0,5}该死", "双标毒点"),
    ]

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = Path(project_dir)
        self.chapters_dir = self.project_dir / "chapters"
        self._load_project_info()

    def _load_project_info(self):
        """加载项目信息"""
        self.novel_info = {}
        progress_file = self.project_dir / "novel-progress.txt"
        if progress_file.exists():
            with open(progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.novel_info = {
                    "title": data.get("title", "未知"),
                    "genre": data.get("genre", "未知"),
                    "total_chapters": data.get("total_chapters", 0),
                    "completed_chapters": data.get("completed_chapters", 0),
                }

    def review_novel(self, chapter_range: Tuple[int, int] = None) -> SeniorEditorReport:
        """
        对小说进行全面审稿

        Args:
            chapter_range: 审稿章节范围，如(1, 20)

        Returns:
            SeniorEditorReport: 完整审稿报告
        """
        print(f"\n{'=' * 70}")
        print("📋 起点金牌资深编辑「锐评官」审稿中...")
        print("=" * 70)
        print(f"作品: {self.novel_info.get('title', '未知')}")
        print(f"类型: {self.novel_info.get('genre', '未知')}")
        print("=" * 70)

        chapters_content = self._load_chapters(chapter_range)
        if not chapters_content:
            print("❌ 无法加载章节内容")
            return self._create_empty_report()

        characters = self._load_characters()
        world_rules = self._load_world_rules()

        dimensions = []

        print("\n[1/6] 📝 评估开篇抓人度...")
        opening_dim = self._evaluate_opening(chapters_content)
        dimensions.append(opening_dim)

        print("[2/6] 🔍 评估逻辑自洽性...")
        logic_dim = self._evaluate_logic(chapters_content, world_rules)
        dimensions.append(logic_dim)

        print("[3/6] ⚡ 评估爽感设计...")
        satisfaction_dim = self._evaluate_satisfaction(chapters_content)
        dimensions.append(satisfaction_dim)

        print("[4/6] 👤 评估人设鲜活度...")
        character_dim = self._evaluate_characters(chapters_content, characters)
        dimensions.append(character_dim)

        print("[5/6] 🌍 评估更新潜力...")
        potential_dim = self._evaluate_potential(world_rules)
        dimensions.append(potential_dim)

        print("[6/6] 💰 评估商业适配度...")
        commercial_dim = self._evaluate_commercial(chapters_content, characters)
        dimensions.append(commercial_dim)

        chapter_analyses = self._analyze_chapters(chapters_content)
        overall_score = self._calculate_weighted_score(dimensions)
        predicted_retention = self._predict_retention(chapter_analyses, dimensions)
        contract_grade = self._determine_contract_grade(overall_score, dimensions)
        verdict = self._generate_verdict(overall_score, contract_grade, dimensions)
        fatal_flaws = self._identify_fatal_flaws(dimensions)
        strengths = self._extract_strengths(dimensions)
        improvement_plan = self._create_improvement_plan(dimensions)
        recommendations = self._generate_recommendations(dimensions, chapter_analyses)
        editor_note = self._write_editor_note(overall_score, contract_grade, dimensions)

        report = SeniorEditorReport(
            novel_title=self.novel_info.get("title", "未知"),
            overall_score=overall_score,
            verdict=verdict,
            contract_grade=contract_grade,
            predicted_retention=predicted_retention,
            dimensions=dimensions,
            fatal_flaws=fatal_flaws,
            strengths=strengths,
            improvement_plan=improvement_plan,
            chapter_analyses=chapter_analyses,
            editor_note=editor_note,
            recommendations=recommendations,
        )

        self._save_report(report)
        self._print_summary(report)

        return report

    def _load_chapters(self, chapter_range: Tuple[int, int] = None) -> Dict[int, str]:
        """加载章节内容"""
        chapters = {}
        if not self.chapters_dir.exists():
            return chapters

        for file in sorted(self.chapters_dir.glob("chapter-*.md")):
            match = re.search(r"chapter-(\d+)", file.name)
            if match:
                num = int(match.group(1))
                if chapter_range:
                    if num < chapter_range[0] or num > chapter_range[1]:
                        continue
                try:
                    chapters[num] = file.read_text(encoding="utf-8")
                except:
                    pass

        return chapters

    def _load_characters(self) -> Dict[str, Any]:
        """加载角色设定"""
        char_file = self.project_dir / "characters.json"
        if char_file.exists():
            try:
                with open(char_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _load_world_rules(self) -> Dict[str, Any]:
        """加载世界观规则"""
        rules_file = self.project_dir / "world-rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _evaluate_opening(self, chapters: Dict[int, str]) -> ReviewDimension:
        """评估开篇抓人度"""
        issues = []
        strengths = []
        score = 8.0

        if not chapters:
            return ReviewDimension(
                "开篇抓人",
                5.0,
                self.DIMENSION_WEIGHTS["开篇抓人"],
                [{"type": "fatal", "message": "无法加载章节内容"}],
                [],
            )

        ch1 = chapters.get(1, "")
        ch2 = chapters.get(2, "")
        ch3 = chapters.get(3, "")

        protagonist_keywords = ["主角", "他", "她", "少年", "青年"]
        if len(ch1) > 500:
            first_500 = ch1[:500]
            if not any(kw in first_500 for kw in protagonist_keywords):
                issues.append(
                    {
                        "type": "fatal",
                        "message": "第1章前500字未出现主角，违反'3秒定律'",
                    }
                )
                score -= 3.0

        conflict_keywords = ["冲突", "战斗", "危机", "困境", "敌人", "杀", "死", "危机"]
        if ch1 and not any(kw in ch1[:3000] for kw in conflict_keywords):
            issues.append(
                {"type": "warning", "message": "第1章3000字内未出现首场冲突，节奏过慢"}
            )
            score -= 1.5

        golden_finger_keywords = [
            "系统",
            "金手指",
            "功法",
            "传承",
            "觉醒",
            "突破",
            "能力",
        ]
        combined_3_chapters = ch1 + ch2 + ch3
        if combined_3_chapters and not any(
            kw in combined_3_chapters for kw in golden_finger_keywords
        ):
            issues.append(
                {"type": "warning", "message": "前3章未展示金手指，建议提前亮相"}
            )
            score -= 1.0

        hook_indicators = ["?", "？", "...", "悬念", "究竟", "难道", "竟然"]
        chapter1_hooks = sum(ch1.count(ind) for ind in hook_indicators) if ch1 else 0
        if chapter1_hooks < 2:
            issues.append({"type": "minor", "message": "第1章悬念钩子不足，建议增加"})
            score -= 0.5

        for pattern, desc in self.TOXIC_PATTERNS:
            if re.search(pattern, combined_3_chapters):
                issues.append(
                    {"type": "fatal", "message": f"检测到{desc}，可能劝退读者"}
                )
                score -= 2.0

        if len(ch1) > 2000:
            strengths.append("第1章篇幅充足，信息量够")
        if chapter1_hooks >= 3:
            strengths.append("悬念设置密集，有翻页动力")

        return ReviewDimension(
            name="开篇抓人",
            score=max(0, min(10, score)),
            weight=self.DIMENSION_WEIGHTS["开篇抓人"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_logic(
        self, chapters: Dict[int, str], world_rules: Dict
    ) -> ReviewDimension:
        """评估逻辑自洽性"""
        issues = []
        strengths = []
        score = 8.0

        all_text = "\n".join(chapters.values())

        realm_keywords = [
            "炼气",
            "筑基",
            "金丹",
            "元婴",
            "化神",
            "返虚",
            "合道",
            "渡劫",
        ]
        realms_found = {}
        for realm in realm_keywords:
            count = len(
                re.findall(
                    rf"{realm}[一二三四五六七八九十\d]*[层期前后巅峰]*", all_text
                )
            )
            if count > 0:
                realms_found[realm] = count

        if len(realms_found) > 2:
            strengths.append(f"境界体系完整，涉及{len(realms_found)}个境界")

        cross_level_patterns = [
            (r"炼气.*击败.*筑基", "炼气击败筑基"),
            (r"筑基.*击败.*金丹", "筑基击败金丹"),
            (r"金丹.*击败.*元婴", "金丹击败元婴"),
        ]
        for pattern, desc in cross_level_patterns:
            if re.search(pattern, all_text):
                cost_keywords = [
                    "代价",
                    "燃烧",
                    "消耗",
                    "损伤",
                    "根基",
                    "寿元",
                    "底牌",
                    "重伤",
                ]
                if not any(kw in all_text for kw in cost_keywords):
                    issues.append(
                        {
                            "type": "fatal",
                            "message": f"{desc}但缺乏代价描述，战力崩坏风险",
                        }
                    )
                    score -= 2.0

        year_refs = re.findall(r"(\d+)年前", all_text)
        if year_refs:
            years = [int(y) for y in year_refs]
            if max(years) - min(years) > 10:
                issues.append(
                    {
                        "type": "warning",
                        "message": f"时间参考矛盾：{min(years)}年前 vs {max(years)}年前",
                    }
                )
                score -= 1.0

        return ReviewDimension(
            name="逻辑自洽",
            score=max(0, min(10, score)),
            weight=self.DIMENSION_WEIGHTS["逻辑自洽"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_satisfaction(self, chapters: Dict[int, str]) -> ReviewDimension:
        """评估爽感设计"""
        issues = []
        strengths = []
        score = 8.0

        all_text = "\n".join(chapters.values())
        total_words = len(all_text)

        conflict_keywords = ["冲突", "战斗", "危机", "困境", "击败", "胜利", "突破"]
        conflict_count = sum(all_text.count(kw) for kw in conflict_keywords)

        expected_conflicts = total_words / 3000
        if conflict_count < expected_conflicts:
            issues.append(
                {"type": "warning", "message": f"爽点密度不足，每3000字应有一个小爽点"}
            )
            score -= 1.0
        else:
            strengths.append(f"冲突/爽点密度充足")

        satisfaction_keywords = [
            "爽",
            "痛快",
            "扬眉吐气",
            "打脸",
            "装逼",
            "震撼",
            "惊艳",
        ]
        satisfaction_count = sum(all_text.count(kw) for kw in satisfaction_keywords)
        if satisfaction_count < len(chapters):
            issues.append({"type": "minor", "message": "情绪宣泄不足，读者缺乏快感"})
            score -= 0.5

        return ReviewDimension(
            name="爽感设计",
            score=max(0, min(10, score)),
            weight=self.DIMENSION_WEIGHTS["爽感设计"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_characters(
        self, chapters: Dict[int, str], characters: Dict
    ) -> ReviewDimension:
        """评估人设鲜活度"""
        issues = []
        strengths = []
        score = 8.0

        all_text = "\n".join(chapters.values())

        protagonist = None
        char_list = []
        if isinstance(characters, list):
            char_list = characters
        elif isinstance(characters, dict):
            char_list = characters.get("characters", [])

        for char in char_list:
            if isinstance(char, dict) and char.get("role") == "protagonist":
                protagonist = char
                break

        if protagonist:
            name = protagonist.get("name", "")
            personality = protagonist.get("personality", "")

            if personality:
                strengths.append(f"主角人设明确：{personality[:30]}...")

            if name and name in all_text:
                name_count = all_text.count(name)
                if name_count < len(chapters) * 3:
                    issues.append({"type": "minor", "message": f"主角{name}出场率偏低"})
                    score -= 0.5

        villain_keywords = ["反派", "敌人", "魔宗", "宗主", "少主", "追杀"]
        villain_count = sum(all_text.count(kw) for kw in villain_keywords)
        if villain_count > 5:
            strengths.append("反派存在感充足")

        return ReviewDimension(
            name="人设鲜活",
            score=max(0, min(10, score)),
            weight=self.DIMENSION_WEIGHTS["人设鲜活"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_potential(self, world_rules: Dict) -> ReviewDimension:
        """评估更新潜力"""
        issues = []
        strengths = []
        score = 7.0

        if world_rules:
            if world_rules.get("cultivation_system"):
                strengths.append("修炼体系完整")
                score += 0.5
            if world_rules.get("factions"):
                strengths.append("势力设定丰富")
                score += 0.5
            if world_rules.get("geography"):
                strengths.append("世界观地图完整")
                score += 0.5

        return ReviewDimension(
            name="更新潜力",
            score=max(0, min(10, score)),
            weight=self.DIMENSION_WEIGHTS["更新潜力"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_commercial(
        self, chapters: Dict[int, str], characters: Dict
    ) -> ReviewDimension:
        """评估商业适配度"""
        issues = []
        strengths = []
        score = 7.0

        all_text = "\n".join(chapters.values())

        trendy_keywords = ["稳健", "苟道", "模拟器", "克系", "诡异", "飞升", "系统"]
        trendy_count = sum(1 for kw in trendy_keywords if kw in all_text)
        if trendy_count > 0:
            strengths.append(f"融入当前流行元素({trendy_count}个)")
            score += 0.5

        genre = self.novel_info.get("genre", "")
        if "修仙" in genre or "玄幻" in genre:
            strengths.append("品类市场大，受众明确")
            score += 0.5

        return ReviewDimension(
            name="商业适配",
            score=max(0, min(10, score)),
            weight=self.DIMENSION_WEIGHTS["商业适配"],
            issues=issues,
            strengths=strengths,
        )

    def _analyze_chapters(self, chapters: Dict[int, str]) -> List[ChapterAnalysis]:
        """逐章分析"""
        analyses = []

        for num, content in sorted(chapters.items()):
            word_count = len(content)

            hook_keywords = [
                "?",
                "？",
                "...",
                "悬念",
                "究竟",
                "难道",
                "竟然",
                "出乎意料",
            ]
            hook_present = any(kw in content[-500:] for kw in hook_keywords)

            conflict_keywords = ["冲突", "战斗", "危机", "困境", "敌人"]
            conflict_present = any(kw in content for kw in conflict_keywords)

            emotion_keywords = ["愤怒", "悲伤", "喜悦", "兴奋", "震撼", "感动"]
            emotion_score = min(10, sum(content.count(kw) for kw in emotion_keywords))

            if word_count < 1500:
                pacing = "过短"
            elif word_count > 4000:
                pacing = "过长"
            else:
                pacing = "适中"

            analyses.append(
                ChapterAnalysis(
                    chapter_number=num,
                    word_count=word_count,
                    hook_present=hook_present,
                    conflict_present=conflict_present,
                    emotion_score=emotion_score,
                    pacing=pacing,
                )
            )

        return analyses

    def _calculate_weighted_score(self, dimensions: List[ReviewDimension]) -> float:
        """计算加权总分（转换为百分制）"""
        total = 0.0
        for dim in dimensions:
            total += dim.score * dim.weight
        # 转换为百分制
        return round(total * 10, 1)

    def _predict_retention(
        self, analyses: List[ChapterAnalysis], dimensions: List[ReviewDimension]
    ) -> float:
        """预测追读率"""
        base_retention = 50.0

        opening_score = next((d.score for d in dimensions if d.name == "开篇抓人"), 5)
        base_retention += (opening_score - 5) * 2

        if analyses:
            hook_rate = sum(1 for a in analyses if a.hook_present) / len(analyses)
            base_retention += hook_rate * 10

        return min(95, max(5, base_retention))

    def _determine_contract_grade(
        self, score: float, dimensions: List[ReviewDimension]
    ) -> str:
        """确定签约等级"""
        fatal_count = sum(
            1 for d in dimensions for i in d.issues if i.get("type") == "fatal"
        )

        if score >= 90 and fatal_count == 0:
            return "S级"
        elif score >= 80 and fatal_count <= 1:
            return "A级"
        elif score >= 70:
            return "B级"
        elif score >= 60:
            return "C级"
        else:
            return "D级"

    def _generate_verdict(
        self, score: float, grade: str, dimensions: List[ReviewDimension]
    ) -> str:
        """生成一句话verdict"""
        fatal_dims = [
            d.name
            for d in dimensions
            if any(i.get("type") == "fatal" for i in d.issues)
        ]

        if score >= 90:
            return "优秀作品，具备爆款潜质"
        elif score >= 80:
            return "良好作品，小幅修改后可签约"
        elif score >= 70:
            if fatal_dims:
                return f"有潜力但存在致命伤，{','.join(fatal_dims[:2])}需重点优化"
            return "中规中矩，有亮点但需打磨"
        elif score >= 60:
            return f"硬伤明显，{','.join(fatal_dims[:2] if fatal_dims else ['多处'])}必须大修"
        else:
            return "不建议签约，建议重新构思"

    def _identify_fatal_flaws(
        self, dimensions: List[ReviewDimension]
    ) -> List[Dict[str, Any]]:
        """识别致命伤"""
        flaws = []
        for dim in dimensions:
            for issue in dim.issues:
                if issue.get("type") in ["fatal", "critical"]:
                    flaws.append(
                        {
                            "dimension": dim.name,
                            "type": issue.get("type"),
                            "message": issue.get("message", ""),
                            "suggestion": f"建议重新审视{dim.name}相关设定",
                        }
                    )
        return flaws[:5]

    def _extract_strengths(self, dimensions: List[ReviewDimension]) -> List[str]:
        """提取优点"""
        strengths = []
        for dim in dimensions:
            strengths.extend(dim.strengths)
        return strengths[:8]

    def _create_improvement_plan(
        self, dimensions: List[ReviewDimension]
    ) -> List[Dict[str, Any]]:
        """创建改进计划"""
        plan = []
        priority = 1

        sorted_dims = sorted(dimensions, key=lambda x: x.score)
        for dim in sorted_dims:
            if dim.score < 7 and dim.issues:
                plan.append(
                    {
                        "priority": f"P{priority}",
                        "dimension": dim.name,
                        "current_score": f"{dim.score}/10",
                        "target_score": "8/10",
                        "issues": [i.get("message", "") for i in dim.issues[:3]],
                        "actions": self._generate_actions(dim.name, dim.issues[:3]),
                    }
                )
                priority += 1
                if priority > 5:
                    break

        return plan

    def _generate_actions(self, dimension: str, issues: List[Dict]) -> List[str]:
        """生成改进行动"""
        actions = []

        if dimension == "开篇抓人":
            actions = [
                "第1章前500字必须出现主角",
                "3000字内引爆首场冲突",
                "提前展示金手指",
            ]
        elif dimension == "逻辑自洽":
            actions = ["建立战力对照表", "制作详细时间轴", "统一设定前后一致"]
        elif dimension == "爽感设计":
            actions = ["每3000字设置一个小爽点", "增加情绪宣泄场景", "优化卡点设计"]
        elif dimension == "人设鲜活":
            actions = ["明确主角底层行为逻辑", "给反派合理动机", "配角避免功能化"]
        else:
            actions = [f"优化{dimension}相关设定"]

        return actions

    def _generate_recommendations(
        self, dimensions: List[ReviewDimension], analyses: List[ChapterAnalysis]
    ) -> Dict[str, Any]:
        """生成建议"""
        recs = {
            "vip_chapter": 15,
            "daily_word_count": 6000,
            "chapters_per_day": 3,
            "key_milestones": [],
            "avoid_pitfalls": [],
        }

        fatal_issues = []
        for dim in dimensions:
            for issue in dim.issues:
                if issue.get("type") == "fatal":
                    fatal_issues.append(issue.get("message", ""))

        if fatal_issues:
            recs["avoid_pitfalls"] = fatal_issues[:5]

        if analyses:
            avg_words = sum(a.word_count for a in analyses) / len(analyses)
            if avg_words < 2500:
                recs["daily_word_count"] = 6000
            elif avg_words > 3500:
                recs["chapters_per_day"] = 2

        return recs

    def _write_editor_note(
        self, score: float, grade: str, dimensions: List[ReviewDimension]
    ) -> str:
        """撰写编辑寄语"""
        if score >= 90:
            return "这是一部有爆款潜质的优秀作品，继续保持！建议重点打磨开篇，争取冲击三江阁推荐。"
        elif score >= 80:
            return "作品整体质量不错，按建议完成修改后有望顺利签约。注意控制战力体系，避免后期崩坏。"
        elif score >= 70:
            return "作品有亮点但也有明显问题，建议3周内完成重点修改后重新投稿。重点关注致命伤的修复。"
        elif score >= 60:
            return "作品硬伤较多，建议大修核心设定。如果时间允许，建议重新构思开篇或考虑换题材。"
        else:
            return "当前版本不建议投稿。建议系统学习网文写作方法论，或尝试更适合自己的题材方向。"

    def _save_report(self, report: SeniorEditorReport):
        """保存审稿报告"""
        reports_dir = self.project_dir / "senior_editor_reports"
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        report_file = reports_dir / f"review_{report.novel_title}_{timestamp}.md"

        content = f"""# 【起点金牌编辑审稿报告】{report.novel_title}

## 📊 综合评级：{report.contract_grade}（{report.overall_score}/100）
**一句话verdict**：{report.verdict}

**预测追读率**：{report.predicted_retention:.1f}%（{"优秀" if report.predicted_retention > 60 else "及格" if report.predicted_retention > 40 else "危险"}）

---

## 🚦 红绿灯评估

| 维度 | 得分 | 状态 | 说明 |
|------|------|------|------|
"""

        for dim in report.dimensions:
            status = "🟢" if dim.score >= 8 else "🟡" if dim.score >= 6 else "🔴"
            content += f"| {dim.name} | {dim.score}/10 | {status} | {dim.strengths[0] if dim.strengths else '需改进'} |\n"

        content += f"""
---

## 🔴 致命伤（必须修改）

"""
        if report.fatal_flaws:
            for i, flaw in enumerate(report.fatal_flaws, 1):
                content += f"{i}. **[{flaw['dimension']}]** {flaw['message']}\n"
                content += f"   - 建议：{flaw['suggestion']}\n\n"
        else:
            content += "✅ 未发现致命伤\n\n"

        content += f"""---

## 🟢 亮点保持

"""
        for strength in report.strengths:
            content += f"- {strength}\n"

        content += f"""
---

## 📋 改进计划（按优先级排序）

"""
        for item in report.improvement_plan:
            content += f"### {item['priority']}: {item['dimension']}（{item['current_score']} → {item['target_score']}）\n\n"
            content += f"**问题**：\n"
            for issue in item["issues"]:
                content += f"- {issue}\n"
            content += f"\n**改进行动**：\n"
            for action in item["actions"]:
                content += f"1. {action}\n"
            content += "\n"

        content += f"""---

## 📈 上架建议

- **VIP切入点**：第{report.recommendations["vip_chapter"]}章左右
- **爆更计划**：每天{report.recommendations["daily_word_count"]}字，分{report.recommendations["chapters_per_day"]}章发布
- **推荐期节奏**：早8午12晚6发布，保持固定时间

### ⚠️ 避雷指南

"""
        for pitfall in report.recommendations["avoid_pitfalls"]:
            content += f"- {pitfall}\n"

        content += f"""
---

## 💬 编辑寄语

> {report.editor_note}

---

*审稿时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M")}*
*审稿人：起点金牌资深编辑「锐评官」*
*经验：8年+审稿，经手作品总收藏破千万*
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n📄 审稿报告已保存: {report_file}")

    def _print_summary(self, report: SeniorEditorReport):
        """打印审稿摘要"""
        print(f"\n{'=' * 70}")
        print("📋 审稿完成")
        print("=" * 70)
        print(f"\n🎯 总评：{report.verdict}")
        print(f"📊 总分：{report.overall_score}/100")
        print(f"📈 签约建议：{report.contract_grade}")
        print(f"📉 预测追读率：{report.predicted_retention:.1f}%")

        print("\n📋 维度评分：")
        for dim in report.dimensions:
            status = "✅" if dim.score >= 8 else "⚠️" if dim.score >= 6 else "❌"
            print(f"  {status} {dim.name}: {dim.score}/10")

        if report.fatal_flaws:
            print(f"\n🔴 致命伤：{len(report.fatal_flaws)}个")
            for flaw in report.fatal_flaws[:3]:
                print(f"  - [{flaw['dimension']}] {flaw['message']}")

        print(f"\n💬 编辑寄语：{report.editor_note}")
        print("=" * 70)

    def _create_empty_report(self) -> SeniorEditorReport:
        """创建空报告"""
        return SeniorEditorReport(
            novel_title=self.novel_info.get("title", "未知"),
            overall_score=0,
            verdict="无法加载章节内容",
            contract_grade="D级",
            predicted_retention=0,
            dimensions=[],
            fatal_flaws=[{"message": "无法加载章节内容"}],
            strengths=[],
            improvement_plan=[],
            chapter_analyses=[],
            editor_note="无法完成审稿，请检查章节文件是否存在。",
            recommendations={},
        )
