"""
一致性检查器模块
用于检查小说的角色行为、情节连贯性、时间线和设定一致性
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConsistencyChecker:
    """一致性检查器，检查小说各章节的一致性"""

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = Path(project_dir)
        self.chapters_dir = self.project_dir / "chapters"
        self.characters_dir = self.project_dir / "characters"
        self.worldbuilding_dir = self.project_dir / "worldbuilding"

        self.name_registry: Dict[str, List[int]] = {}
        self.realm_progression: List[Dict] = []

    def check_chapters(self, chapter_numbers: List[int]) -> Dict[str, Any]:
        """检查指定章节的一致性"""
        chapters_content = self._load_chapters(chapter_numbers)
        if not chapters_content:
            return {"error": "无法加载章节内容", "passed": False}

        character_profiles = self._load_character_profiles()
        world_settings = self._load_world_settings()

        hardcoded_issues = self._hardcoded_consistency_check(
            chapters_content, character_profiles
        )

        results = {
            "checked_chapters": chapter_numbers,
            "character_consistency": self._check_character_consistency(
                chapters_content, character_profiles
            ),
            "plot_consistency": self._check_plot_consistency(chapters_content),
            "timeline_consistency": self._check_timeline_consistency(chapters_content),
            "setting_consistency": self._check_setting_consistency(
                chapters_content, world_settings
            ),
            "hardcoded_issues": hardcoded_issues,
        }

        results["inconsistencies"] = self.find_inconsistencies(chapters_content)
        results["passed"] = len(hardcoded_issues.get("critical", [])) == 0
        results["summary"] = self._generate_summary(results)

        return results

    def _hardcoded_consistency_check(
        self, chapters: Dict[int, str], profiles: Dict[str, Any]
    ) -> Dict[str, List[Dict]]:
        """硬编码一致性检查 - 不依赖LLM"""
        issues = {"critical": [], "warnings": []}

        all_text = "\n".join(chapters.values())

        name_issues = self._check_name_consistency(all_text, profiles)
        issues["critical"].extend(name_issues)

        combat_issues = self._check_combat_consistency(all_text)
        issues["warnings"].extend(combat_issues)

        timeline_issues = self._check_timeline_hardcoded(all_text)
        issues["warnings"].extend(timeline_issues)

        return issues

    def _check_name_consistency(
        self, text: str, profiles: Dict[str, Any]
    ) -> List[Dict]:
        """检查姓名一致性 - 硬编码规则"""
        issues = []

        known_names = {}
        char_file = self.project_dir / "characters.json"
        if char_file.exists():
            try:
                with open(char_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        chars = data.get("characters", [])
                    else:
                        chars = data if isinstance(data, list) else []

                    for char in chars:
                        if isinstance(char, dict):
                            name = char.get("name", "")
                            role = char.get("role", "")
                            if name:
                                known_names[name] = role
            except:
                pass

        for name in known_names:
            surname = name[0] if len(name) >= 1 else ""
            given_name = name[1:] if len(name) > 1 else ""

            pattern = rf"{surname}[\u4e00-\u9fa5]{{1,3}}"
            matches = re.findall(pattern, text)

            variants = [m for m in matches if m != name and len(m) >= 2]

            if variants:
                unique_variants = list(set(variants))[:3]
                for variant in unique_variants:
                    if variant not in known_names:
                        issues.append(
                            {
                                "type": "name_inconsistency",
                                "severity": "critical",
                                "message": f"姓名不一致：'{name}' 在文中出现变体 '{variant}'",
                                "original_name": name,
                                "variant": variant,
                                "suggestion": f"统一使用 '{name}'",
                            }
                        )

        return issues

    def _check_combat_consistency(self, text: str) -> List[Dict]:
        """检查战力一致性 - 硬编码规则"""
        issues = []

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
        realm_order = {realm: i for i, realm in enumerate(realm_keywords)}

        found_realms = {}
        for realm in realm_keywords:
            pattern = rf"{realm}[一二三四五六七八九十\d]*[层期前后巅峰]*"
            matches = re.findall(pattern, text)
            if matches:
                found_realms[realm] = matches

        if len(found_realms) > 1:
            realm_names = list(found_realms.keys())
            for i, r1 in enumerate(realm_names[:-1]):
                for r2 in realm_names[i + 1 :]:
                    diff = abs(realm_order.get(r1, 0) - realm_order.get(r2, 0))
                    if diff > 2:
                        issues.append(
                            {
                                "type": "large_realm_gap",
                                "severity": "warning",
                                "message": f"检测到较大境界跨度：{r1} ↔ {r2}（相差{diff}个大境界）",
                                "realms": [r1, r2],
                                "gap": diff,
                            }
                        )

        battle_patterns = ["击败", "战胜", "击杀", "重创", "打退"]
        for pattern in battle_patterns:
            if pattern in text:
                context_start = max(0, text.find(pattern) - 50)
                context = text[context_start : context_start + 100]

                if "筑基" in context and "炼气" in context:
                    if "代价" not in context and "燃烧" not in context:
                        issues.append(
                            {
                                "type": "unlikely_victory",
                                "severity": "warning",
                                "message": f"可能存在不合理越级战斗（炼气vs筑基），未提及代价",
                            }
                        )
                break

        return issues

    def _check_timeline_hardcoded(self, text: str) -> List[Dict]:
        """检查时间线一致性 - 硬编码规则"""
        issues = []

        year_patterns = [
            (r"(\d+)年前", "years_ago"),
            (r"(\d+)月前", "months_ago"),
            (r"(\d+)日前", "days_ago"),
        ]

        time_refs = {}
        for pattern, ref_type in year_patterns:
            matches = re.findall(pattern, text)
            if matches:
                time_refs[ref_type] = [int(m) for m in matches]

        if "years_ago" in time_refs:
            years = time_refs["years_ago"]
            if len(years) >= 2:
                if max(years) - min(years) > 10:
                    issues.append(
                        {
                            "type": "timeline_discrepancy",
                            "severity": "warning",
                            "message": f"时间参考不一致：{min(years)}年前 vs {max(years)}年前",
                            "values": years,
                        }
                    )

        return issues

    def _load_chapters(self, chapter_numbers: List[int]) -> Dict[int, str]:
        """加载指定章节的内容"""
        chapters = {}
        for num in chapter_numbers:
            chapter_file = self.chapters_dir / f"chapter_{num:03d}.txt"
            if chapter_file.exists():
                chapters[num] = chapter_file.read_text(encoding="utf-8")
        return chapters

    def _load_character_profiles(self) -> Dict[str, Any]:
        """加载角色档案"""
        profiles = {}
        if self.characters_dir.exists():
            for file in self.characters_dir.glob("*.json"):
                try:
                    data = json.loads(file.read_text(encoding="utf-8"))
                    profiles[data.get("name", file.stem)] = data
                except (json.JSONDecodeError, KeyError):
                    continue
        return profiles

    def _load_world_settings(self) -> Dict[str, Any]:
        """加载世界观设定"""
        settings = {}
        if self.worldbuilding_dir.exists():
            for file in self.worldbuilding_dir.glob("*.json"):
                try:
                    settings[file.stem] = json.loads(file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
        return settings

    def _check_character_consistency(
        self, chapters: Dict[int, str], profiles: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查角色行为一致性"""
        prompt = self._build_character_check_prompt(chapters, profiles)
        response = self.llm.chat(prompt)

        return self._parse_llm_response(response, "character")

    def _check_plot_consistency(self, chapters: Dict[int, str]) -> Dict[str, Any]:
        """检查情节连贯性"""
        prompt = self._build_plot_check_prompt(chapters)
        response = self.llm.chat(prompt)

        return self._parse_llm_response(response, "plot")

    def _check_timeline_consistency(self, chapters: Dict[int, str]) -> Dict[str, Any]:
        """检查时间线一致性"""
        prompt = self._build_timeline_check_prompt(chapters)
        response = self.llm.chat(prompt)

        return self._parse_llm_response(response, "timeline")

    def _check_setting_consistency(
        self, chapters: Dict[int, str], settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查设定一致性"""
        prompt = self._build_setting_check_prompt(chapters, settings)
        response = self.llm.chat(prompt)

        return self._parse_llm_response(response, "setting")

    def _build_character_check_prompt(
        self, chapters: Dict[int, str], profiles: Dict[str, Any]
    ) -> str:
        """构建角色一致性检查提示词"""
        chapters_text = "\n\n".join(
            [f"【第{num}章】\n{content[:2000]}" for num, content in chapters.items()]
        )

        profiles_text = "\n".join(
            [
                f"- {name}: 性格={p.get('personality', '未知')}, 特点={p.get('traits', [])}"
                for name, p in profiles.items()
            ]
        )

        return f"""请检查以下章节中角色行为的一致性。

【角色档案】
{profiles_text if profiles_text else "无角色档案"}

【章节内容】
{chapters_text}

请分析：
1. 角色性格是否有突变或不合理的行为
2. 角色之间的关系发展是否自然
3. 角色的能力表现是否前后一致
4. 角色的语言风格是否保持一致

请以JSON格式返回结果：
{{
    "issues": [
        {{
            "character": "角色名",
            "issue_type": "问题类型",
            "description": "问题描述",
            "chapter": 章节号,
            "location": "大致位置描述",
            "severity": "high/medium/low",
            "suggestion": "修改建议"
        }}
    ],
    "overall_score": 1-10分,
    "summary": "总体评价"
}}"""

    def _build_plot_check_prompt(self, chapters: Dict[int, str]) -> str:
        """构建情节连贯性检查提示词"""
        chapters_text = "\n\n".join(
            [f"【第{num}章】\n{content}" for num, content in chapters.items()]
        )

        return f"""请检查以下章节的情节连贯性。

【章节内容】
{chapters_text}

请分析：
1. 前后章节的情节是否有矛盾
2. 伏笔是否有呼应或遗漏
3. 事件的发展逻辑是否合理
4. 是否有未解释的情节跳跃

请以JSON格式返回结果：
{{
    "issues": [
        {{
            "issue_type": "矛盾类型",
            "description": "问题描述",
            "chapters": [涉及章节号],
            "severity": "high/medium/low",
            "suggestion": "修改建议"
        }}
    ],
    "overall_score": 1-10分,
    "summary": "总体评价"
}}"""

    def _build_timeline_check_prompt(self, chapters: Dict[int, str]) -> str:
        """构建时间线一致性检查提示词"""
        chapters_text = "\n\n".join(
            [f"【第{num}章】\n{content[:2000]}" for num, content in chapters.items()]
        )

        return f"""请检查以下章节的时间线一致性。

【章节内容】
{chapters_text}

请分析：
1. 事件的时间顺序是否合理
2. 时间跨度是否有矛盾
3. 季节/天气等时间元素是否一致
4. 角色的年龄/成长是否合理

请以JSON格式返回结果：
{{
    "issues": [
        {{
            "issue_type": "时间线问题类型",
            "description": "问题描述",
            "chapter": 章节号,
            "severity": "high/medium/low",
            "suggestion": "修改建议"
        }}
    ],
    "overall_score": 1-10分,
    "summary": "总体评价"
}}"""

    def _build_setting_check_prompt(
        self, chapters: Dict[int, str], settings: Dict[str, Any]
    ) -> str:
        """构建设定一致性检查提示词"""
        chapters_text = "\n\n".join(
            [f"【第{num}章】\n{content[:2000]}" for num, content in chapters.items()]
        )

        settings_text = json.dumps(settings, ensure_ascii=False, indent=2)

        return f"""请检查以下章节与世界设定的的一致性。

【世界设定】
{settings_text if settings_text else "无设定文件"}

【章节内容】
{chapters_text}

请分析：
1. 世界观元素是否与设定一致
2. 魔法/能力体系是否合理
3. 地理/环境描述是否一致
4. 社会/文化设定是否有矛盾

请以JSON格式返回结果：
{{
    "issues": [
        {{
            "setting_element": "设定元素",
            "issue_type": "问题类型",
            "description": "问题描述",
            "chapter": 章节号,
            "severity": "high/medium/low",
            "suggestion": "修改建议"
        }}
    ],
    "overall_score": 1-10分,
    "summary": "总体评价"
}}"""

    def _parse_llm_response(self, response: str, check_type: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        return {
            "issues": [],
            "overall_score": 0,
            "summary": f"无法解析{check_type}检查结果",
            "raw_response": response,
        }

    def find_inconsistencies(self, chapters: List[str]) -> List[Dict]:
        """找出具体的不一致之处"""
        if isinstance(chapters, dict):
            chapters = list(chapters.values())

        prompt = f"""请详细分析以下章节内容，找出所有不一致之处。

【章节内容】
{chr(10).join([f"第{i + 1}部分: {c[:1500]}" for i, c in enumerate(chapters)])}

请仔细检查并列出所有发现的问题，包括：
1. 数值不一致（如修为等级、人物数量等）
2. 名称不一致（地名、人名、物品名等）
3. 能力不一致（角色能力前后矛盾）
4. 关系不一致（人物关系前后矛盾）
5. 细节不一致（服装、外貌、习惯等）

请以JSON格式返回：
{{
    "inconsistencies": [
        {{
            "type": "不一致类型",
            "location_1": "第一次出现的位置（章节号和描述）",
            "content_1": "第一次出现的内容",
            "location_2": "第二次出现的位置",
            "content_2": "第二次出现的内容",
            "description": "不一致说明",
            "severity": "high/medium/low",
            "suggestion": "修改建议"
        }}
    ]
}}"""

        response = self.llm.chat(prompt)
        result = self._parse_llm_response(response, "inconsistency")
        return result.get("inconsistencies", [])

    def generate_report(self, results: Dict) -> str:
        """生成一致性检查报告"""
        report_lines = [
            "=" * 60,
            "小说一致性检查报告",
            "=" * 60,
            f"检查章节: {results.get('checked_chapters', [])}",
            "",
        ]

        summary = results.get("summary", {})
        report_lines.extend(
            [
                "-" * 40,
                "检查摘要",
                "-" * 40,
                f"总分: {summary.get('overall_score', 'N/A')}/10",
                f"问题总数: {summary.get('total_issues', 'N/A')}",
                "",
            ]
        )

        report_lines.extend(
            self._format_section("角色一致性", results.get("character_consistency", {}))
        )
        report_lines.extend(
            self._format_section("情节连贯性", results.get("plot_consistency", {}))
        )
        report_lines.extend(
            self._format_section(
                "时间线一致性", results.get("timeline_consistency", {})
            )
        )
        report_lines.extend(
            self._format_section("设定一致性", results.get("setting_consistency", {}))
        )

        inconsistencies = results.get("inconsistencies", [])
        if inconsistencies:
            report_lines.extend(
                [
                    "-" * 40,
                    "发现的不一致问题",
                    "-" * 40,
                ]
            )
            for i, issue in enumerate(inconsistencies, 1):
                report_lines.extend(
                    [
                        f"\n问题 {i}:",
                        f"  类型: {issue.get('type', '未知')}",
                        f"  严重程度: {issue.get('severity', '未知')}",
                        f"  描述: {issue.get('description', '无描述')}",
                    ]
                )
                if issue.get("location_1"):
                    report_lines.append(f"  位置1: {issue.get('location_1')}")
                if issue.get("content_1"):
                    report_lines.append(f"  内容1: {issue.get('content_1')}")
                if issue.get("location_2"):
                    report_lines.append(f"  位置2: {issue.get('location_2')}")
                if issue.get("content_2"):
                    report_lines.append(f"  内容2: {issue.get('content_2')}")
                if issue.get("suggestion"):
                    report_lines.append(f"  建议: {issue.get('suggestion')}")

        report_lines.extend(
            [
                "",
                "=" * 60,
                "报告生成完成",
                "=" * 60,
            ]
        )

        return "\n".join(report_lines)

    def _format_section(self, title: str, data: Dict) -> List[str]:
        """格式化检查报告的各个部分"""
        lines = [
            "-" * 40,
            title,
            "-" * 40,
            f"评分: {data.get('overall_score', 'N/A')}/10",
            f"评价: {data.get('summary', '无评价')}",
        ]

        issues = data.get("issues", [])
        if issues:
            lines.append(f"\n发现问题 ({len(issues)}个):")
            for i, issue in enumerate(issues, 1):
                lines.extend(
                    [
                        f"\n  [{i}] {issue.get('issue_type', '未知问题')}",
                        f"      描述: {issue.get('description', '无描述')}",
                    ]
                )
                if issue.get("chapter"):
                    lines.append(f"      章节: 第{issue.get('chapter')}章")
                if issue.get("location"):
                    lines.append(f"      位置: {issue.get('location')}")
                if issue.get("severity"):
                    lines.append(f"      严重程度: {issue.get('severity')}")
                if issue.get("suggestion"):
                    lines.append(f"      建议: {issue.get('suggestion')}")

        return lines

    def _generate_summary(self, results: Dict) -> Dict[str, Any]:
        """生成检查摘要"""
        all_issues = []
        scores = []

        for key in [
            "character_consistency",
            "plot_consistency",
            "timeline_consistency",
            "setting_consistency",
        ]:
            data = results.get(key, {})
            issues = data.get("issues", [])
            all_issues.extend(issues)
            score = data.get("overall_score", 0)
            if isinstance(score, (int, float)):
                scores.append(score)

        inconsistencies = results.get("inconsistencies", [])
        total_issues = len(all_issues) + len(inconsistencies)

        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "overall_score": round(avg_score, 1),
            "total_issues": total_issues,
            "character_issues": len(
                results.get("character_consistency", {}).get("issues", [])
            ),
            "plot_issues": len(results.get("plot_consistency", {}).get("issues", [])),
            "timeline_issues": len(
                results.get("timeline_consistency", {}).get("issues", [])
            ),
            "setting_issues": len(
                results.get("setting_consistency", {}).get("issues", [])
            ),
            "inconsistency_count": len(inconsistencies),
        }

    def check_single_chapter(self, chapter_number: int) -> Dict[str, Any]:
        """检查单个章节的内部一致性"""
        chapters = self._load_chapters([chapter_number])
        if not chapters:
            return {"error": f"无法加载第{chapter_number}章"}

        content = chapters[chapter_number]

        prompt = f"""请检查以下章节的内部一致性。

【章节内容】
{content}

请检查：
1. 人物描写是否前后一致
2. 时间描述是否有矛盾
3. 场景描述是否有矛盾
4. 对话和行为是否合理
5. 数值和设定是否有冲突

请以JSON格式返回结果：
{{
    "issues": [
        {{
            "issue_type": "问题类型",
            "description": "问题描述",
            "location": "问题位置",
            "severity": "high/medium/low",
            "suggestion": "修改建议"
        }}
    ],
    "overall_score": 1-10分,
    "summary": "总体评价"
}}"""

        response = self.llm.chat(prompt)
        result = self._parse_llm_response(response, "single_chapter")
        result["chapter"] = chapter_number
        return result

    def get_character_timeline(
        self, character_name: str, chapters: List[int]
    ) -> Dict[str, Any]:
        """获取角色在指定章节中的时间线"""
        chapters_content = self._load_chapters(chapters)

        prompt = f"""请分析角色"{character_name}"在以下章节中的时间线。

【章节内容】
{chr(10).join([f"第{num}章: {content[:2000]}" for num, content in chapters_content.items()])}

请提取：
1. 角色的主要活动
2. 角色的状态变化
3. 角色的关系变化
4. 时间节点

请以JSON格式返回：
{{
    "character": "{character_name}",
    "timeline": [
        {{
            "chapter": 章节号,
            "events": ["事件1", "事件2"],
            "state": "角色状态",
            "relationships": ["关系变化"]
        }}
    ],
    "consistency_issues": ["一致性问题"]
}}"""

        response = self.llm.chat(prompt)
        return self._parse_llm_response(response, "character_timeline")
