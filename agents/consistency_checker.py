"""
Consistency Checker - 严格一致性检查器
基于起点编辑审稿意见重写，检测6大类致命缺陷

检测类别：
1. 宗门名称一致性（防止精神分裂）
2. 人物姓名一致性（防止姓名混乱）
3. 战力体系一致性（防止战力崩坏）
4. 修为进度一致性（防止坐火箭）
5. 体质设定一致性（防止设定变更）
6. 情节逻辑一致性（防止逻辑硬伤）
"""

import json
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ConsistencyViolation:
    """一致性违规记录"""

    type: str
    severity: str  # critical, warning, info
    message: str
    chapter: int
    details: str
    suggestion: str


class ConsistencyChecker:
    """
    严格一致性检查器

    设计原则：宁可误报，不可漏报
    对于可疑内容一律标记为警告，由人工最终确认
    """

    def __init__(self, project_dir: str, llm_client=None):
        self.project_dir = Path(project_dir)
        self.llm = llm_client  # 保留以兼容旧代码
        self.chapters_dir = self.project_dir / "chapters"
        self.config_file = Path("config/consistency_rules.yaml")

        # 加载配置
        self.config = self._load_config()

        # 加载约束
        self.constraints_file = self.project_dir / "writing_constraints.json"
        self.constraints = self._load_constraints()

        # 加载所有章节索引
        self.chapter_index = self._build_chapter_index()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _load_constraints(self) -> Dict:
        """加载写作约束"""
        if self.constraints_file.exists():
            with open(self.constraints_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _build_chapter_index(self) -> Dict[int, Path]:
        """构建章节索引"""
        index = {}
        if self.chapters_dir.exists():
            for file in self.chapters_dir.glob("chapter-*.md"):
                try:
                    num = int(file.stem.split("-")[1])
                    index[num] = file
                except (IndexError, ValueError):
                    continue
        return index

    def check_all_chapters(self) -> Dict[str, Any]:
        """检查所有章节的一致性"""
        all_violations = []
        chapter_results = {}

        for chapter_num in sorted(self.chapter_index.keys()):
            result = self.check_single_chapter(chapter_num)
            chapter_results[chapter_num] = result
            all_violations.extend(result.get("violations", []))

        # 跨章节检查
        cross_chapter_violations = self._check_cross_chapter_consistency()
        all_violations.extend(cross_chapter_violations)

        return {
            "total_chapters_checked": len(self.chapter_index),
            "violations": all_violations,
            "critical_count": len(
                [v for v in all_violations if v["severity"] == "critical"]
            ),
            "warning_count": len(
                [v for v in all_violations if v["severity"] == "warning"]
            ),
            "chapter_results": chapter_results,
            "passed": len([v for v in all_violations if v["severity"] == "critical"])
            == 0,
        }

    def check_single_chapter(self, chapter_number: int) -> Dict[str, Any]:
        """检查单个章节的严格一致性"""
        violations = []

        # 加载章节内容
        content = self._load_chapter_content(chapter_number)
        if not content:
            return {
                "chapter": chapter_number,
                "violations": [],
                "error": "无法加载章节内容",
            }

        # 1. 宗门名称检查
        faction_violations = self._check_faction_consistency(chapter_number, content)
        violations.extend(faction_violations)

        # 2. 人物姓名检查
        name_violations = self._check_name_consistency(chapter_number, content)
        violations.extend(name_violations)

        # 3. 战力体系检查
        combat_violations = self._check_combat_consistency(chapter_number, content)
        violations.extend(combat_violations)

        # 4. 修为进度检查
        cultivation_violations = self._check_cultivation_consistency(
            chapter_number, content
        )
        violations.extend(cultivation_violations)

        # 5. 体质设定检查
        constitution_violations = self._check_constitution_consistency(
            chapter_number, content
        )
        violations.extend(constitution_violations)

        # 6. 情节逻辑检查
        plot_violations = self._check_plot_logic(chapter_number, content)
        violations.extend(plot_violations)

        # 7. 时间线检查（新增）
        timeline_violations = self._check_timeline_consistency(chapter_number, content)
        violations.extend(timeline_violations)

        # 8. 武器命名检查（新增）
        weapon_violations = self._check_weapon_naming(chapter_number, content)
        violations.extend(weapon_violations)

        return {
            "chapter": chapter_number,
            "violations": violations,
            "violation_count": len(violations),
            "critical_count": len(
                [v for v in violations if v["severity"] == "critical"]
            ),
            "passed": len([v for v in violations if v["severity"] == "critical"]) == 0,
        }

    def _load_chapter_content(self, chapter_number: int) -> str:
        """加载章节内容"""
        file_path = self.chapter_index.get(chapter_number)
        if file_path and file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""

    def _check_faction_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """
        检查宗门名称一致性
        问题：宗门名称精神分裂（天剑宗↔青云剑宗）
        """
        violations = []

        # 从约束中获取白名单
        whitelist = self.constraints.get("faction_whitelist", [])
        if not whitelist:
            return violations

        # 检测所有可能的宗门名称
        faction_pattern = (
            r"[\u4e00-\u9fa5]{2,6}(?:宗|派|阁|门|宫|殿|院|府|山|谷|岛|盟|会)"
        )
        found_factions = set(re.findall(faction_pattern, content))

        for faction in found_factions:
            if faction not in whitelist:
                # 检查是否是相似名称（可能是变体）
                similar = self._find_similar_faction(faction, whitelist)
                if similar:
                    violations.append(
                        {
                            "type": "faction_name_variant",
                            "severity": "critical",
                            "message": f"检测到宗门名称变体：'{faction}'（应为'{similar}'）",
                            "chapter": chapter_number,
                            "details": f"文中使用'{faction}'，但白名单中只有'{similar}'",
                            "suggestion": f"将'{faction}'统一改为'{similar}'",
                        }
                    )
                else:
                    violations.append(
                        {
                            "type": "undefined_faction",
                            "severity": "critical",
                            "message": f"检测到未定义的宗门：'{faction}'",
                            "chapter": chapter_number,
                            "details": f"该宗门不在允许使用的白名单中",
                            "suggestion": f"使用白名单中的宗门：{', '.join(whitelist[:5])}...",
                        }
                    )

        return violations

    def _find_similar_faction(
        self, faction: str, whitelist: List[str]
    ) -> Optional[str]:
        """查找相似的宗门名称"""
        # 简单相似度检查
        for valid_faction in whitelist:
            # 检查是否有共同后缀
            if faction[-1] == valid_faction[-1]:  # 都以"宗"/"派"等结尾
                # 检查前缀相似度
                common_prefix = ""
                for i, (c1, c2) in enumerate(zip(faction, valid_faction)):
                    if c1 == c2:
                        common_prefix += c1
                    else:
                        break
                if len(common_prefix) >= 1:  # 至少有一个共同字
                    return valid_faction
        return None

    def _check_name_consistency(self, chapter_number: int, content: str) -> List[Dict]:
        """
        检查人物姓名一致性
        问题：苏清雪↔叶清雪（姓名变更）
        """
        violations = []

        locked_names = self.constraints.get("locked_names", {})
        if not locked_names:
            return violations

        # 检查每个人物的姓名
        for role, name in locked_names.items():
            if not name or len(name) < 2:
                continue

            # 提取姓氏
            surname = name[0] if len(name) == 2 else name[:2]
            given_name = name[len(surname) :]

            # 检测同姓不同名的变体
            variant_pattern = (
                rf"{re.escape(surname)}[\u4e00-\u9fa5]{{1,{len(given_name) + 1}}}"
            )
            variants = re.findall(variant_pattern, content)

            for variant in set(variants):
                if variant != name and variant not in locked_names.values():
                    # 排除常见词
                    common_words = [
                        "一些",
                        "一样",
                        "一直",
                        "一起",
                        "所谓",
                        "自己",
                        "他人",
                        "此时",
                    ]
                    if variant in common_words:
                        continue

                    # 可能是姓名变体
                    violations.append(
                        {
                            "type": "name_variant",
                            "severity": "warning",
                            "message": f"疑似姓名变体：'{name}' vs '{variant}'",
                            "chapter": chapter_number,
                            "details": f"角色'{role}'设定姓名为'{name}'，但文中出现'{variant}'",
                            "suggestion": f"确认'{variant}'是否为'{name}'的误写，或是否为新角色",
                        }
                    )

        return violations

    def _check_combat_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """
        检查战力体系一致性
        问题：剑气境击败剑心境（跨境界战斗）
        """
        violations = []

        combat_rules = self.config.get("realm_system", {}).get("combat_rules", {})
        realm_hierarchy = self.constraints.get("realm_hierarchy", {})
        current_realm = self.constraints.get("current_realm", "")

        if not realm_hierarchy or combat_rules.get("cross_realm_combat") != "forbidden":
            return violations

        # 检测战斗描述
        battle_keywords = ["击败", "战胜", "击杀", "重创", "打退", "斩杀", "击溃"]
        current_level = realm_hierarchy.get(current_realm, 0)
        max_cross = combat_rules.get("max_cross_within_realm", 2)

        for keyword in battle_keywords:
            # 找到所有战斗描述的位置
            for match in re.finditer(keyword, content):
                context_start = max(0, match.start() - 150)
                context_end = min(len(content), match.end() + 150)
                context = content[context_start:context_end]

                # 检查是否涉及境界描述
                for realm, level in realm_hierarchy.items():
                    if realm in context:
                        level_diff = level - current_level

                        # 检查是否跨大境界
                        if level_diff > max_cross:
                            # 检查是否有代价描述
                            cost_keywords = [
                                "代价",
                                "燃烧",
                                "牺牲",
                                "重伤",
                                "陨落",
                                "自爆",
                                "禁术",
                                "秘法",
                                "底牌",
                            ]
                            has_cost = any(cost in context for cost in cost_keywords)

                            if not has_cost:
                                violations.append(
                                    {
                                        "type": "cross_realm_combat",
                                        "severity": "critical",
                                        "message": f"跨境界战斗未提及代价：{current_realm} vs {realm}",
                                        "chapter": chapter_number,
                                        "details": f"主角{current_realm}（等级{current_level}）击败{realm}（等级{level}），相差{level_diff}级",
                                        "suggestion": "跨境界战斗必须付出沉重代价（燃烧生命、牺牲同伴、使用禁术等）",
                                    }
                                )

        return violations

    def _check_cultivation_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """
        检查修为进度一致性
        问题：4天从废人到剑气境三层（修炼速度过快）
        """
        violations = []

        cultivation_config = self.config.get("cultivation_speed", {})
        minor_config = cultivation_config.get("minor_breakthrough", {})
        major_config = cultivation_config.get("major_breakthrough", {})

        min_minor_days = minor_config.get("min_days", 7)
        min_major_days = major_config.get("min_days", 30)

        # 检测时间描述
        time_patterns = [
            (rf"(\d+)天[后内]?", "day", 1),
            (rf"(\d+)日[后内]?", "day", 1),
            (rf"(\d+)个?月[后内]?", "month", 30),
            (rf"(\d+)年[后内]?", "year", 365),
        ]

        # 检测突破描述
        breakthrough_patterns = ["突破", "晋级", "晋升", "突破到", "晋升到", "达到"]

        for pattern, unit, multiplier in time_patterns:
            for match in re.finditer(pattern, content):
                days = int(match.group(1)) * multiplier

                # 获取上下文
                context_start = max(0, match.start() - 100)
                context_end = min(len(content), match.end() + 100)
                context = content[context_start:context_end]

                # 检查是否有突破描述
                has_breakthrough = any(bp in context for bp in breakthrough_patterns)

                if has_breakthrough:
                    # 检查突破类型
                    realm_change_keywords = ["境", "重天", "阶"]
                    is_major = any(kw in context for kw in realm_change_keywords)

                    if is_major and days < min_major_days:
                        violations.append(
                            {
                                "type": "major_breakthrough_too_fast",
                                "severity": "critical",
                                "message": f"大境界突破速度过快：{match.group(1)}{unit}",
                                "chapter": chapter_number,
                                "details": f"大境界突破至少需要{min_major_days}天，但文中仅用{days}天",
                                "suggestion": f"延长修炼时间至至少{min_major_days}天，或添加详细修炼过程",
                            }
                        )
                    elif not is_major and days < min_minor_days:
                        violations.append(
                            {
                                "type": "minor_breakthrough_too_fast",
                                "severity": "critical",
                                "message": f"小境界突破速度过快：{match.group(1)}{unit}",
                                "chapter": chapter_number,
                                "details": f"小境界突破至少需要{min_minor_days}天，但文中仅用{days}天",
                                "suggestion": f"延长修炼时间至至少{min_minor_days}天",
                            }
                        )

        return violations

    def _check_constitution_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """
        检查体质设定一致性
        问题：九玄剑骨→混沌剑骨（体质无理由变更）
        """
        violations = []

        locked_constitution = self.constraints.get("locked_constitution", "")
        allowed_changes = self.constraints.get("allowed_constitution_changes", [])

        if not locked_constitution:
            return violations

        # 检测体质变更关键词
        change_keywords = [
            "变成",
            "变为",
            "化作",
            "觉醒为",
            "进化为",
            "变异为",
            "转化为",
            "蜕变为",
        ]
        constitution_keywords = ["体质", "剑骨", "灵根", "血脉", "神体", "圣体", "道体"]

        for change_kw in change_keywords:
            if change_kw in content:
                # 获取上下文
                idx = content.find(change_kw)
                context_start = max(0, idx - 100)
                context_end = min(len(content), idx + 100)
                context = content[context_start:context_end]

                # 检查是否涉及体质
                if any(ck in context for ck in constitution_keywords):
                    # 检查是否有允许的变更类型
                    if not any(allowed in context for allowed in allowed_changes):
                        violations.append(
                            {
                                "type": "unauthorized_constitution_change",
                                "severity": "critical",
                                "message": f"检测到未授权的体质变更",
                                "chapter": chapter_number,
                                "details": f"主角体质锁定为'{locked_constitution}'，但文中出现变更描述",
                                "suggestion": f"如需变更体质，必须是以下方式之一：{', '.join(allowed_changes)}，并有充分铺垫",
                            }
                        )

        return violations

    def _check_plot_logic(self, chapter_number: int, content: str) -> List[Dict]:
        """
        检查情节逻辑一致性
        问题：反派降智、未铺垫的禁术、缺失的章节逻辑
        """
        violations = []

        # 1. 检查反派行为动机
        villain_indicators = [
            "反派",
            "敌人",
            "对手",
            "冷笑",
            "阴笑",
            "狞笑",
            "杀意",
            "敌意",
        ]
        motivation_keywords = [
            "因为",
            "为了",
            "由于",
            "想要",
            "计划",
            "目的",
            "意图",
            "图谋",
        ]

        for indicator in villain_indicators:
            if indicator in content:
                # 获取反派相关段落
                idx = content.find(indicator)
                context_start = max(0, idx - 200)
                context_end = min(len(content), idx + 200)
                context = content[context_start:context_end]

                # 检查是否有动机描述
                has_motivation = any(mot in context for mot in motivation_keywords)

                if not has_motivation and len(context) < 300:
                    violations.append(
                        {
                            "type": "villain_no_motivation",
                            "severity": "warning",
                            "message": "反派行为缺乏明确动机",
                            "chapter": chapter_number,
                            "details": f"检测到反派行为（{indicator}），但未说明其行为动机",
                            "suggestion": "为反派添加合理的动机（复仇、野心、嫉妒、理念冲突等），避免'因为是反派所以坏'",
                        }
                    )
                break  # 每个章节只报告一次

        # 2. 检查突然出现的禁术/底牌
        sudden_power_keywords = [
            "禁术",
            "秘法",
            "底牌",
            "绝招",
            "绝学",
            "秘技",
            "杀手锏",
        ]
        foreshadowing_keywords = [
            "曾经",
            "之前",
            "早已",
            "准备",
            "修炼",
            "习得",
            "掌握",
        ]

        for power_kw in sudden_power_keywords:
            if power_kw in content:
                # 获取上下文
                idx = content.find(power_kw)
                context_start = max(0, idx - 150)
                context_end = min(len(content), idx + 50)
                context = content[context_start:context_end]

                # 检查是否有铺垫
                has_foreshadowing = any(fs in context for fs in foreshadowing_keywords)

                if not has_foreshadowing:
                    violations.append(
                        {
                            "type": "sudden_power_no_foreshadowing",
                            "severity": "warning",
                            "message": f"突然出现的{power_kw}缺乏铺垫",
                            "chapter": chapter_number,
                            "details": f"文中突然使用{power_kw}，但之前未提及角色掌握此技能",
                            "suggestion": f"提前在前文铺垫此{power_kw}的存在（修炼过程、偶然获得、师门传承等）",
                        }
                    )

        # 3. 检查禁地/特殊地点的逻辑
        forbidden_keywords = ["禁地", "剑冢", "古地", "秘境", "遗迹", "圣地"]
        access_keywords = [
            "许可",
            "批准",
            "允许",
            "令牌",
            "钥匙",
            "资格",
            "考验",
            "机缘",
        ]

        for forbidden in forbidden_keywords:
            if forbidden in content:
                # 检查进入/出现在禁地
                enter_keywords = ["进入", "来到", "出现在", "抵达", "到达"]
                if any(ek in content for ek in enter_keywords):
                    # 检查是否有进入许可的描述
                    has_access = any(acc in content for acc in access_keywords)

                    if not has_access:
                        violations.append(
                            {
                                "type": "forbidden_area_no_access",
                                "severity": "warning",
                                "message": f"角色进入{forbidden}缺乏合理解释",
                                "chapter": chapter_number,
                                "details": f"角色进入{forbidden}，但未说明如何获得进入许可",
                                "suggestion": f"添加进入{forbidden}的合理解释（持令牌、通过考验、特殊机缘等）",
                            }
                        )

        # 4. 检查突然出现的亲属关系（如第19章突然出现的姐姐）
        if chapter_number > 3:  # 只有在前几章之后才检查
            relation_keywords = [
                "姐姐",
                "妹妹",
                "哥哥",
                "弟弟",
                "父亲",
                "母亲",
                "师父",
                "师兄",
                "师姐",
            ]
            for relation in relation_keywords:
                if relation in content:
                    # 检查是否是第一次出现
                    prev_chapters = [
                        self._load_chapter_content(i) for i in range(1, chapter_number)
                    ]
                    prev_content = "\n".join(prev_chapters)

                    if relation not in prev_content:
                        violations.append(
                            {
                                "type": "sudden_relationship",
                                "severity": "warning",
                                "message": f"突然出现的亲属关系：{relation}",
                                "chapter": chapter_number,
                                "details": f"{relation}在第{chapter_number}章首次出现，但之前未提及",
                                "suggestion": f"提前在前文铺垫{relation}的存在，或说明为何之前未提及",
                            }
                        )

        return violations

    def _check_timeline_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """检查时间线一致性"""
        violations = []

        timeline_config = self.config.get("timeline_validation", {})
        if not timeline_config.get("enforce_timestamp", False):
            return violations

        # 检测"Day X"时间戳
        day_pattern = r"[Dd]ay\s*(\d+)|第(\d+)天"
        matches = re.findall(day_pattern, content)

        if matches:
            days_found = []
            for match in matches:
                day = int(match[0] or match[1])
                days_found.append(day)

            if days_found:
                current_day = max(days_found)
                # 检查时间跳跃
                max_jump = timeline_config.get("max_time_jump", 7)

                # 获取上一章的时间
                prev_day = self._get_previous_chapter_day(chapter_number)
                if prev_day is not None:
                    jump = current_day - prev_day

                    if jump < 0:
                        violations.append(
                            {
                                "type": "time_backwards",
                                "severity": "critical",
                                "message": f"时间倒流：从第{prev_day}天到第{current_day}天",
                                "chapter": chapter_number,
                                "details": "时间不能倒退",
                                "suggestion": "修正时间线",
                            }
                        )
                    elif jump > max_jump:
                        violations.append(
                            {
                                "type": "excessive_time_jump",
                                "severity": "warning",
                                "message": f"时间跳跃过大：从第{prev_day}天到第{current_day}天（跳跃{jump}天）",
                                "chapter": chapter_number,
                                "details": f"最大允许跳跃{max_jump}天",
                                "suggestion": "添加过渡情节或修正时间",
                            }
                        )

        return violations

    def _get_previous_chapter_day(self, chapter_number: int) -> Optional[int]:
        """获取上一章的时间"""
        if chapter_number <= 1:
            return 1

        prev_content = self._load_chapter_content(chapter_number - 1)
        if not prev_content:
            return None

        day_pattern = r"[Dd]ay\s*(\d+)|第(\d+)天"
        matches = re.findall(day_pattern, prev_content)

        if matches:
            return max(int(m[0] or m[1]) for m in matches)
        return None

    def _check_weapon_naming(self, chapter_number: int, content: str) -> List[Dict]:
        """检查武器命名一致性"""
        violations = []

        weapon_config = self.config.get("weapon_naming", {})
        if not weapon_config.get("enforce_unique_names", False):
            return violations

        # 获取锁定的武器名称
        protagonist_weapon = self.constraints.get("protagonist_weapon", "")
        if not protagonist_weapon:
            return violations

        # 允许的状态描述（不算改名）
        allowed_descriptions = weapon_config.get(
            "allowed_descriptions", ["残剑", "断剑", "受损", "修复", "认主", "解封"]
        )

        # 检测所有可能的武器名称
        weapon_mentions = []
        for match in re.finditer(r"[\u4e00-\u9fa5]{1,4}(?:剑|刀|枪|戟|斧)", content):
            weapon_mentions.append(match.group())

        # 检查是否有其他名称
        found_weapons = set(weapon_mentions)

        for weapon in found_weapons:
            if weapon != protagonist_weapon:
                # 检查是否是允许的状态描述
                is_allowed = False
                for allowed in allowed_descriptions:
                    if allowed in weapon:
                        is_allowed = True
                        break

                if not is_allowed and weapon not in ["剑", "武器", "兵器"]:
                    violations.append(
                        {
                            "type": "weapon_name_inconsistency",
                            "severity": "warning",
                            "message": f"武器名称不一致：'{protagonist_weapon}' vs '{weapon}'",
                            "chapter": chapter_number,
                            "details": f"武器应统一使用'{protagonist_weapon}'",
                            "suggestion": f"统一武器名称，或添加'{weapon}'为'{protagonist_weapon}'的描述性称呼",
                        }
                    )

        return violations

    def _check_cross_chapter_consistency(self) -> List[Dict]:
        """检查跨章节的一致性"""
        violations = []

        # 加载所有章节
        all_chapters = {}
        for num in sorted(self.chapter_index.keys()):
            all_chapters[num] = self._load_chapter_content(num)

        # 1. 检查境界变化是否合理
        realm_progression = self._extract_realm_progression(all_chapters)
        for i in range(1, len(realm_progression)):
            prev = realm_progression[i - 1]
            curr = realm_progression[i]

            if curr["chapter"] - prev["chapter"] < 3:  # 3章内连续突破
                violations.append(
                    {
                        "type": "rapid_realm_progression",
                        "severity": "warning",
                        "message": f"境界提升过快：第{prev['chapter']}章到第{curr['chapter']}章",
                        "chapter": curr["chapter"],
                        "details": f"从{prev['realm']}提升到{curr['realm']}仅用了{curr['chapter'] - prev['chapter']}章",
                        "suggestion": "增加修炼过程描写，或延长突破间隔",
                    }
                )

        # 2. 检查地点跳跃是否合理
        location_progression = self._extract_location_progression(all_chapters)
        for i in range(1, len(location_progression)):
            prev = location_progression[i - 1]
            curr = location_progression[i]

            if prev["location"] != curr["location"]:
                # 检查是否有移动过程的描述
                if curr["chapter"] - prev["chapter"] == 1:
                    # 相邻章节突然换地点，需要检查距离
                    violations.append(
                        {
                            "type": "sudden_location_change",
                            "severity": "info",
                            "message": f"地点突然变更：{prev['location']} → {curr['location']}",
                            "chapter": curr["chapter"],
                            "details": f"第{prev['chapter']}章在{prev['location']}，第{curr['chapter']}章突然在{curr['location']}",
                            "suggestion": "添加地点转移的过程描述",
                        }
                    )

        return violations

    def _extract_realm_progression(self, chapters: Dict[int, str]) -> List[Dict]:
        """提取境界变化时间线"""
        progression = []
        realm_hierarchy = self.constraints.get("realm_hierarchy", {})

        for chapter_num, content in sorted(chapters.items()):
            for realm in realm_hierarchy.keys():
                if realm in content:
                    progression.append({"chapter": chapter_num, "realm": realm})
                    break

        return progression

    def _extract_location_progression(self, chapters: Dict[int, str]) -> List[Dict]:
        """提取地点变化时间线"""
        progression = []

        # 常见地点关键词
        location_keywords = [
            "宗门",
            "门派",
            "剑冢",
            "后山",
            "修炼室",
            "大殿",
            "广场",
            "城镇",
            "市集",
            "客栈",
            "山",
            "谷",
            "林",
            "洞府",
        ]

        for chapter_num, content in sorted(chapters.items()):
            for location in location_keywords:
                if location in content:
                    progression.append({"chapter": chapter_num, "location": location})
                    break
            else:
                progression.append({"chapter": chapter_num, "location": "未知"})

        return progression

    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成详细的一致性检查报告"""
        lines = [
            "=" * 80,
            "小说一致性检查报告",
            "=" * 80,
            "",
            f"检查章节数：{results.get('total_chapters_checked', 0)}",
            f"严重错误数：{results.get('critical_count', 0)}",
            f"警告数：{results.get('warning_count', 0)}",
            f"检查结果：{'通过' if results.get('passed') else '未通过'}",
            "",
            "-" * 80,
        ]

        violations = results.get("violations", [])

        if violations:
            # 按严重程度分组
            critical = [v for v in violations if v.get("severity") == "critical"]
            warnings = [v for v in violations if v.get("severity") == "warning"]
            info = [v for v in violations if v.get("severity") == "info"]

            if critical:
                lines.extend(["", "【严重错误】必须修复", "-" * 80])
                for i, v in enumerate(critical, 1):
                    lines.extend(self._format_violation(i, v))

            if warnings:
                lines.extend(["", "【警告】建议修复", "-" * 80])
                for i, v in enumerate(warnings, 1):
                    lines.extend(self._format_violation(i, v))

            if info:
                lines.extend(["", "【提示】仅供参考", "-" * 80])
                for i, v in enumerate(info, 1):
                    lines.extend(self._format_violation(i, v))
        else:
            lines.extend(["", "恭喜！未发现一致性问题。", ""])

        lines.extend(
            [
                "",
                "=" * 80,
                "报告生成完成",
                "=" * 80,
            ]
        )

        return "\n".join(lines)

    def _format_violation(self, index: int, violation: Dict) -> List[str]:
        """格式化单个违规记录"""
        return [
            f"",
            f"[{index}] {violation.get('type', '未知类型')}",
            f"  位置：第{violation.get('chapter', '?')}章",
            f"  问题：{violation.get('message', '')}",
            f"  详情：{violation.get('details', '')}",
            f"  建议：{violation.get('suggestion', '')}",
        ]

    def export_violations_to_json(self, results: Dict[str, Any], output_path: str):
        """导出违规记录到JSON"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


# 便捷函数
def check_novel_consistency(project_dir: str) -> Dict[str, Any]:
    """检查小说一致性的便捷函数"""
    checker = ConsistencyChecker(project_dir)
    return checker.check_all_chapters()


def check_single_chapter(project_dir: str, chapter_number: int) -> Dict[str, Any]:
    """检查单个章节的便捷函数"""
    checker = ConsistencyChecker(project_dir)
    return checker.check_single_chapter(chapter_number)
