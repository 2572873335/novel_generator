"""
SeniorEditorAgent - 起点金牌资深编辑
对小说进行多维度锐评，提供签约建议和修改方向
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ReviewDimension:
    """评审维度"""

    name: str
    score: float
    weight: float
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


@dataclass
class SeniorEditorReport:
    """资深编辑审稿报告"""

    novel_title: str
    overall_score: float
    verdict: str
    contract_grade: str
    dimensions: List[ReviewDimension]
    fatal_flaws: List[Dict[str, Any]]
    strengths: List[str]
    improvement_plan: List[Dict[str, Any]]
    editor_note: str


class SeniorEditorAgent:
    """
    起点金牌资深编辑

    评审维度：
    1. 战力体系（25%）- 境界、越级、升级节奏
    2. 时间线一致性（20%）- 年龄、事件顺序、设定一致
    3. 反派塑造（15%）- 动机、智商、失败原因
    4. 主角人设（15%）- 性格一致、行为逻辑、双标
    5. 情节节奏（15%）- 开篇、爽点、注水、套路
    6. 市场潜力（10%）- 题材、差异化、读者群
    """

    DIMENSION_WEIGHTS = {
        "战力体系": 0.25,
        "时间线一致性": 0.20,
        "反派塑造": 0.15,
        "主角人设": 0.15,
        "情节节奏": 0.15,
        "市场潜力": 0.10,
    }

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = Path(project_dir)
        self.chapters_dir = self.project_dir / "chapters"

    def review_novel(self, chapter_range: tuple = None) -> SeniorEditorReport:
        """
        对小说进行全面审稿

        Args:
            chapter_range: 审稿章节范围，如(1, 20)

        Returns:
            SeniorEditorReport: 完整审稿报告
        """
        print(f"\n{'=' * 60}")
        print("📋 起点金牌资深编辑审稿中...")
        print("=" * 60)

        chapters_content = self._load_chapters(chapter_range)
        characters = self._load_characters()
        world_rules = self._load_world_rules()

        dimensions = []

        print("\n[1/6] 评估战力体系...")
        combat_dim = self._evaluate_combat_system(chapters_content, world_rules)
        dimensions.append(combat_dim)

        print("[2/6] 评估时间线一致性...")
        timeline_dim = self._evaluate_timeline(chapters_content, characters)
        dimensions.append(timeline_dim)

        print("[3/6] 评估反派塑造...")
        villain_dim = self._evaluate_villain(chapters_content, characters)
        dimensions.append(villain_dim)

        print("[4/6] 评估主角人设...")
        protagonist_dim = self._evaluate_protagonist(chapters_content, characters)
        dimensions.append(protagonist_dim)

        print("[5/6] 评估情节节奏...")
        plot_dim = self._evaluate_plot_rhythm(chapters_content)
        dimensions.append(plot_dim)

        print("[6/6] 评估市场潜力...")
        market_dim = self._evaluate_market_potential(chapters_content, world_rules)
        dimensions.append(market_dim)

        overall_score = self._calculate_weighted_score(dimensions)
        contract_grade = self._determine_contract_grade(overall_score, dimensions)
        verdict = self._generate_verdict(overall_score, dimensions)
        fatal_flaws = self._identify_fatal_flaws(dimensions)
        strengths = self._extract_strengths(dimensions)
        improvement_plan = self._create_improvement_plan(dimensions)
        editor_note = self._write_editor_note(overall_score, contract_grade)

        report = SeniorEditorReport(
            novel_title=self._get_novel_title(),
            overall_score=overall_score,
            verdict=verdict,
            contract_grade=contract_grade,
            dimensions=dimensions,
            fatal_flaws=fatal_flaws,
            strengths=strengths,
            improvement_plan=improvement_plan,
            editor_note=editor_note,
        )

        self._save_report(report)
        self._print_summary(report)

        return report

    def _load_chapters(self, chapter_range: tuple = None) -> Dict[int, str]:
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
                chapters[num] = file.read_text(encoding="utf-8")

        return chapters

    def _load_characters(self) -> Dict[str, Any]:
        """加载角色设定"""
        char_file = self.project_dir / "characters.json"
        if char_file.exists():
            with open(char_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_world_rules(self) -> Dict[str, Any]:
        """加载世界观规则"""
        rules_file = self.project_dir / "world-rules.json"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _get_novel_title(self) -> str:
        """获取小说标题"""
        progress_file = self.project_dir / "novel-progress.txt"
        if progress_file.exists():
            with open(progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("title", "未知")
        return "未知"

    def _evaluate_combat_system(
        self, chapters: Dict[int, str], world_rules: Dict
    ) -> ReviewDimension:
        """评估战力体系"""
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
        realm_mentions = {}
        for realm in realm_keywords:
            count = len(
                re.findall(
                    rf"{realm}[一二三四五六七八九十\d]*[层期前后巅峰]*", all_text
                )
            )
            if count > 0:
                realm_mentions[realm] = count

        cross_level_patterns = [
            (r"炼气[一二三四五六七八九十\d]*[层].*击败.*筑基", "炼气击败筑基"),
            (r"筑基[一二三四五六七八九十\d]*[层].*击败.*金丹", "筑基击败金丹"),
            (r"金丹[一二三四五六七八九十\d]*[层].*击败.*元婴", "金丹击败元婴"),
        ]

        for pattern, desc in cross_level_patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                for match in matches:
                    context = self._get_context(all_text, match, 200)
                    cost_keywords = [
                        "代价",
                        "燃烧",
                        "消耗",
                        "损伤",
                        "根基",
                        "寿元",
                        "底牌",
                    ]
                    if not any(kw in context for kw in cost_keywords):
                        issues.append(f"越级战斗缺乏代价描述：{desc}")
                        score -= 0.5

        upgrade_pattern = r"突破至?[炼筑金元化返合道][气基丹婴神虚道]"
        upgrades = re.findall(upgrade_pattern, all_text)
        if len(upgrades) > 3:
            issues.append(f"升级频率过高：检测到{len(upgrades)}次突破")
            score -= 0.5

        if len(realm_mentions) >= 5:
            strengths.append(f"境界体系完整：涉及{len(realm_mentions)}个大境界")

        if not issues:
            strengths.append("战力体系基本合理")

        return ReviewDimension(
            name="战力体系",
            score=max(1.0, min(10.0, score)),
            weight=self.DIMENSION_WEIGHTS["战力体系"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_timeline(
        self, chapters: Dict[int, str], characters: Dict
    ) -> ReviewDimension:
        """评估时间线一致性"""
        issues = []
        strengths = []
        score = 8.0

        all_text = "\n".join(chapters.values())

        year_refs = re.findall(r"(\d+)年前", all_text)
        if year_refs:
            years = [int(y) for y in year_refs]
            if max(years) - min(years) > 10:
                issues.append(f"时间参考不一致：{min(years)}年前 vs {max(years)}年前")
                score -= 1.0

        age_refs = re.findall(r"(\d+)岁", all_text)
        if age_refs:
            ages = [int(a) for a in age_refs]
            if max(ages) - min(ages) > 30:
                issues.append(f"年龄跨度异常：{min(ages)}岁到{max(ages)}岁")
                score -= 0.5

        if not issues:
            strengths.append("时间线基本连贯")

        return ReviewDimension(
            name="时间线一致性",
            score=max(1.0, min(10.0, score)),
            weight=self.DIMENSION_WEIGHTS["时间线一致性"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_villain(
        self, chapters: Dict[int, str], characters: Dict
    ) -> ReviewDimension:
        """评估反派塑造"""
        issues = []
        strengths = []
        score = 8.0

        all_text = "\n".join(chapters.values())

        villain_keywords = ["魔宗", "反派", "敌人", "追杀", "杀意"]
        villain_presence = sum(1 for kw in villain_keywords if kw in all_text)

        if villain_presence > 5:
            strengths.append("反派存在感充足")

        failure_count = len(re.findall(r"败退|退却|撤离|遁走", all_text))
        if failure_count > 3:
            issues.append(f"反派失败次数过多({failure_count}次)，可能存在降智")
            score -= 0.5

        return ReviewDimension(
            name="反派塑造",
            score=max(1.0, min(10.0, score)),
            weight=self.DIMENSION_WEIGHTS["反派塑造"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_protagonist(
        self, chapters: Dict[int, str], characters: Dict
    ) -> ReviewDimension:
        """评估主角人设"""
        issues = []
        strengths = []
        score = 8.0

        all_text = "\n".join(chapters.values())

        protagonist = None
        if isinstance(characters, list):
            for char in characters:
                if char.get("role") == "protagonist":
                    protagonist = char
                    break
        elif isinstance(characters, dict):
            char_list = characters.get("characters", [])
            for char in char_list:
                if isinstance(char, dict) and char.get("role") == "protagonist":
                    protagonist = char
                    break

        if protagonist:
            if protagonist.get("personality"):
                strengths.append(
                    f"主角人设有明确设定：{protagonist.get('personality', '')[:30]}"
                )

            name = protagonist.get("name", "")
            if name:
                name_count = all_text.count(name)
                if name_count < len(chapters) * 5:
                    issues.append(f"主角出场率偏低：'{name}'仅出现{name_count}次")
                    score -= 0.5

        return ReviewDimension(
            name="主角人设",
            score=max(1.0, min(10.0, score)),
            weight=self.DIMENSION_WEIGHTS["主角人设"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_plot_rhythm(self, chapters: Dict[int, str]) -> ReviewDimension:
        """评估情节节奏"""
        issues = []
        strengths = []
        score = 8.0

        if not chapters:
            return ReviewDimension(
                name="情节节奏",
                score=5.0,
                weight=self.DIMENSION_WEIGHTS["情节节奏"],
                issues=["无法加载章节内容"],
                strengths=[],
            )

        all_text = "\n".join(chapters.values())

        conflict_keywords = ["冲突", "战斗", "危机", "困境", "矛盾"]
        conflict_count = sum(all_text.count(kw) for kw in conflict_keywords)

        if conflict_count > len(chapters) * 3:
            strengths.append(f"冲突密度充足：检测到{conflict_count}处冲突相关词")
        elif conflict_count < len(chapters):
            issues.append(f"冲突密度不足：仅{conflict_count}处冲突相关词")
            score -= 1.0

        hook_keywords = ["?", "？", "...", "悬念", "究竟", "到底"]
        hooks = sum(all_text.count(kw) for kw in hook_keywords)
        if hooks > len(chapters) * 5:
            strengths.append("悬念设置密集")

        return ReviewDimension(
            name="情节节奏",
            score=max(1.0, min(10.0, score)),
            weight=self.DIMENSION_WEIGHTS["情节节奏"],
            issues=issues,
            strengths=strengths,
        )

    def _evaluate_market_potential(
        self, chapters: Dict[int, str], world_rules: Dict
    ) -> ReviewDimension:
        """评估市场潜力"""
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

        return ReviewDimension(
            name="市场潜力",
            score=max(1.0, min(10.0, score)),
            weight=self.DIMENSION_WEIGHTS["市场潜力"],
            issues=issues,
            strengths=strengths,
        )

    def _get_context(self, text: str, match: str, length: int) -> str:
        """获取匹配文本的上下文"""
        idx = text.find(match)
        if idx == -1:
            return ""
        start = max(0, idx - length // 2)
        end = min(len(text), idx + len(match) + length // 2)
        return text[start:end]

    def _calculate_weighted_score(self, dimensions: List[ReviewDimension]) -> float:
        """计算加权总分"""
        total = 0.0
        for dim in dimensions:
            total += dim.score * dim.weight
        return round(total, 1)

    def _determine_contract_grade(
        self, score: float, dimensions: List[ReviewDimension]
    ) -> str:
        """确定签约等级"""
        fatal_count = sum(1 for dim in dimensions if dim.score < 5)

        if score >= 8.0 and fatal_count == 0:
            return "S级"
        elif score >= 7.0 and fatal_count <= 1:
            return "A级"
        elif score >= 6.0:
            return "B级"
        elif score >= 5.0:
            return "C级"
        else:
            return "D级"

    def _generate_verdict(self, score: float, dimensions: List[ReviewDimension]) -> str:
        """生成一句话verdict"""
        low_dims = [dim.name for dim in dimensions if dim.score < 6]

        if score >= 8.0:
            return "优秀作品，具备签约潜力"
        elif score >= 7.0:
            return "良好作品，小幅修改后可签约"
        elif score >= 6.0:
            return f"有潜力但存在问题，{','.join(low_dims)}需要优化"
        else:
            return f"存在严重问题，{','.join(low_dims)}必须大修"

    def _identify_fatal_flaws(
        self, dimensions: List[ReviewDimension]
    ) -> List[Dict[str, Any]]:
        """识别致命伤"""
        fatal_flaws = []
        for dim in dimensions:
            if dim.score < 5:
                for issue in dim.issues:
                    fatal_flaws.append(
                        {
                            "dimension": dim.name,
                            "issue": issue,
                            "severity": "致命" if dim.score < 4 else "严重",
                            "suggestion": f"建议重新审视{dim.name}相关设定",
                        }
                    )
        return fatal_flaws

    def _extract_strengths(self, dimensions: List[ReviewDimension]) -> List[str]:
        """提取优点"""
        strengths = []
        for dim in dimensions:
            strengths.extend(dim.strengths)
        return strengths[:5]

    def _create_improvement_plan(
        self, dimensions: List[ReviewDimension]
    ) -> List[Dict[str, Any]]:
        """创建改进计划"""
        plan = []
        priority = 1
        for dim in sorted(dimensions, key=lambda x: x.score):
            if dim.score < 7 and dim.issues:
                plan.append(
                    {
                        "priority": priority,
                        "dimension": dim.name,
                        "issues": dim.issues[:3],
                        "actions": [f"修改{issue}" for issue in dim.issues[:3]],
                    }
                )
                priority += 1
        return plan[:5]

    def _write_editor_note(self, score: float, grade: str) -> str:
        """撰写编辑寄语"""
        if score >= 8.0:
            return "这部作品展现出良好的创作功底，继续保持！"
        elif score >= 7.0:
            return "作品有一定潜力，按建议修改后有望签约。"
        elif score >= 6.0:
            return "建议作者仔细审视指出的问题，3周内完成修改后重新投稿。"
        else:
            return "作品存在较多硬伤，建议大修后再考虑投稿。"

    def _save_report(self, report: SeniorEditorReport):
        """保存审稿报告"""
        reports_dir = self.project_dir / "senior_editor_reports"
        reports_dir.mkdir(exist_ok=True)

        report_file = reports_dir / f"review_{report.novel_title}.md"

        content = f"""# 起点金牌资深编辑审稿报告

## 基本信息

- **小说标题**: {report.novel_title}
- **总分**: {report.overall_score}/10
- **评级**: {report.contract_grade}
- **Verdict**: {report.verdict}

---

## 维度评分

| 维度 | 分数 | 权重 | 加权分 |
|------|------|------|--------|
"""
        for dim in report.dimensions:
            content += f"| {dim.name} | {dim.score}/10 | {dim.weight * 100:.0f}% | {dim.score * dim.weight:.2f} |\n"

        content += f"""

---

## 优点

"""
        for s in report.strengths:
            content += f"- {s}\n"

        content += f"""

---

## 致命伤（必须修改）

"""
        for flaw in report.fatal_flaws:
            content += (
                f"- **[{flaw['severity']}]** {flaw['dimension']}: {flaw['issue']}\n"
            )
            content += f"  - {flaw['suggestion']}\n"

        content += f"""

---

## 改进计划

"""
        for item in report.improvement_plan:
            content += f"### 优先级 {item['priority']}: {item['dimension']}\n\n"
            for issue in item["issues"]:
                content += f"- {issue}\n"
            content += "\n"

        content += f"""
---

## 编辑寄语

> {report.editor_note}

---

*审稿日期: {self._get_current_time()}*
*审稿人: 起点金牌资深编辑*
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n📄 审稿报告已保存: {report_file}")

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _print_summary(self, report: SeniorEditorReport):
        """打印审稿摘要"""
        print(f"\n{'=' * 60}")
        print("📋 审稿完成")
        print("=" * 60)
        print(f"\n总评: {report.verdict}")
        print(f"总分: {report.overall_score}/10")
        print(f"签约建议: {report.contract_grade}")

        print("\n维度评分:")
        for dim in report.dimensions:
            status = "✅" if dim.score >= 7 else "⚠️" if dim.score >= 5 else "❌"
            print(f"  {status} {dim.name}: {dim.score}/10")

        if report.fatal_flaws:
            print(f"\n致命伤: {len(report.fatal_flaws)}个")
            for flaw in report.fatal_flaws[:3]:
                print(f"  - {flaw['dimension']}: {flaw['issue']}")

        print(f"\n编辑寄语: {report.editor_note}")
        print("=" * 60)
