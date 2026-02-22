"""
Writing Constraint Manager
写作约束管理器 - 在写作阶段就施加严格约束

基于起点编辑审稿意见：
1. 宗门名称锁定（防止天剑宗↔青云剑宗）
2. 人物姓名锁定（防止苏清雪↔叶清雪）
3. 战力规则强制（防止剑气境杀剑心境）
4. 修炼速度限制（防止4天到剑气境三层）
5. 体质设定锁定（防止九玄剑骨→混沌剑骨）
"""

import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class WritingConstraints:
    """写作约束集合"""

    # 宗门约束
    faction_whitelist: List[str]  # 允许使用的宗门名称
    current_faction: str  # 主角当前所在宗门

    # 人物约束
    locked_names: Dict[str, str]  # 锁定的人物姓名 {角色: 姓名}
    protagonist_name: str

    # 修为约束
    current_realm: str  # 主角当前境界
    realm_hierarchy: Dict[str, int]  # 境界等级映射
    max_cross_realm: int  # 最大可越级层数

    # 体质约束
    locked_constitution: str  # 锁定的体质类型
    allowed_constitution_changes: List[str]  # 允许的变更方式

    # 战斗约束
    cross_realm_combat: str  # forbidden/allowed_with_cost
    required_costs: List[str]  # 跨境界必须付出的代价

    # 时间约束
    min_minor_breakthrough_days: int  # 小境界突破最少天数
    min_major_breakthrough_days: int  # 大境界突破最少天数
    last_breakthrough_chapter: int  # 上次突破章节

    # 地理约束
    current_location: str  # 当前地点
    location_distances: Dict[str, int]  # 地点间距离

    # 时间线约束
    current_day: int = 1  # 故事内第几天
    max_time_jump: int = 7  # 最大时间跳跃（天）

    # 武器命名约束
    protagonist_weapon: str = "墨渊"  # 主角武器名称（锁定）

    # 战力计算约束
    max_power_gap: float = 1.2  # 最大合理战力差距（120%）


class WritingConstraintManager:
    """
    写作约束管理器

    在写作阶段就将约束注入到LLM提示词中，防止生成不符合设定的内容
    """

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.config_file = Path("config/consistency_rules.yaml")
        self.constraints_file = self.project_dir / "writing_constraints.json"
        self.config = self._load_config()
        self.constraints = self._load_or_create_constraints()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _load_or_create_constraints(self) -> WritingConstraints:
        """加载或创建约束"""
        if self.constraints_file.exists():
            with open(self.constraints_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return WritingConstraints(**data)

        # 从项目文件中提取初始约束
        constraints = self._extract_initial_constraints()
        self._save_constraints(constraints)
        return constraints

    def _extract_initial_constraints(self) -> WritingConstraints:
        """从项目文件中提取初始约束"""
        # 加载角色信息
        characters = self._load_characters()
        world_rules = self._load_world_rules()

        # 提取主角信息
        protagonist_name = ""
        protagonist_constitution = ""
        for char in characters:
            if char.get("role") == "protagonist":
                protagonist_name = char.get("name", "")
                # 尝试从abilities或background中提取体质
                abilities = char.get("abilities", [])
                for ability in abilities:
                    if "骨" in ability or "体" in ability:
                        protagonist_constitution = ability
                        break

        # 提取宗门信息
        factions = world_rules.get("factions", {})
        faction_names = list(factions.keys())
        current_faction = faction_names[0] if faction_names else ""

        # 提取境界体系
        cultivation_system = world_rules.get("cultivation_system", {})
        realm_list = cultivation_system.get("境界列表", [])
        realm_hierarchy = {realm: i for i, realm in enumerate(realm_list)}

        # 提取当前境界（从第一章或设定中）
        current_realm = self._detect_initial_realm(characters)

        # 加载配置中的规则
        realm_config = self.config.get("realm_system", {})
        combat_rules = realm_config.get("combat_rules", {})
        cultivation_config = self.config.get("cultivation_speed", {})

        return WritingConstraints(
            faction_whitelist=faction_names,
            current_faction=current_faction,
            locked_names={
                char.get("role", f"char_{i}"): char.get("name", "")
                for i, char in enumerate(characters)
                if char.get("name")
            },
            protagonist_name=protagonist_name,
            current_realm=current_realm,
            realm_hierarchy=realm_hierarchy,
            max_cross_realm=combat_rules.get("max_cross_within_realm", 2),
            locked_constitution=protagonist_constitution,
            allowed_constitution_changes=self.config.get("constitution_lock", {}).get(
                "allowed_transformation", []
            ),
            cross_realm_combat=combat_rules.get("cross_realm_combat", "forbidden"),
            required_costs=combat_rules.get("required_costs", []),
            min_minor_breakthrough_days=cultivation_config.get(
                "minor_breakthrough", {}
            ).get("min_days", 7),
            min_major_breakthrough_days=cultivation_config.get(
                "major_breakthrough", {}
            ).get("min_days", 30),
            last_breakthrough_chapter=0,
            current_location="",
            location_distances={},
        )

    def _load_characters(self) -> List[Dict]:
        """加载角色信息"""
        char_file = self.project_dir / "characters.json"
        if char_file.exists():
            with open(char_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("characters", [])
        return []

    def _load_world_rules(self) -> Dict:
        """加载世界观规则"""
        rules_file = self.project_dir / "world-rules.json"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _detect_initial_realm(self, characters: List[Dict]) -> str:
        """检测主角初始境界"""
        for char in characters:
            if char.get("role") == "protagonist":
                # 从background或notes中提取初始境界
                background = char.get("background", "")
                if "废" in background or "无剑" in background:
                    return "无剑者"
                # 尝试从abilities中推断
                abilities = char.get("abilities", [])
                for ability in abilities:
                    if "剑气" in ability:
                        return ability.replace("剑气", "剑气境")
        return "无剑者"

    def _save_constraints(self, constraints: WritingConstraints):
        """保存约束到文件"""
        with open(self.constraints_file, "w", encoding="utf-8") as f:
            json.dump(asdict(constraints), f, ensure_ascii=False, indent=2)

    def get_constraint_prompt(self, chapter_number: int) -> str:
        """
        获取写作约束提示词

        这个提示词会被添加到writer_agent的提示词中，强制LLM遵守约束
        """
        c = self.constraints

        prompt = f"""
## 【强制写作约束】违反以下约束将导致设定崩坏，必须严格遵守：

### 1. 宗门名称锁定（防止精神分裂）
- 允许使用的宗门名称：{", ".join(c.faction_whitelist)}
- 主角当前所在宗门：{c.current_faction}
- ⚠️ 严禁使用白名单外的宗门名称！
- ⚠️ 如需转场到另一个宗门，必须明确写出"离开{c.current_faction}，前往XXX"

### 2. 人物姓名锁定（防止姓名混乱）
- 主角姓名：{c.protagonist_name}（绝对禁止变更）
- 重要配角姓名：
"""
        for role, name in c.locked_names.items():
            if role != "protagonist":
                prompt += f"  - {role}：{name}\n"

        prompt += f"""
- ⚠️ 严禁改变任何人物姓名！
- ⚠️ 新人物出场必须有明确铺垫，禁止突然冒出（如第19章才出现的"姐姐"）

### 3. 修为境界规则（防止战力崩坏）
- 主角当前境界：{c.current_realm}
- 可挑战上限：同境界内可越{c.max_cross_realm}个小层
- 跨大境界战斗：{c.cross_realm_combat}
"""

        if c.cross_realm_combat == "forbidden":
            prompt += "- ⚠️ 严禁跨大境界战斗！剑气境绝对无法击败剑心境！\n"
        else:
            prompt += f"- ⚠️ 如必须跨境界战斗，必须付出以下代价之一：{', '.join(c.required_costs)}\n"

        prompt += f"""
### 4. 体质设定锁定（防止设定变更）
- 主角当前体质：{c.locked_constitution}
- 允许变更方式：{", ".join(c.allowed_constitution_changes)}
- ⚠️ 严禁无理由变更体质类型！
- ⚠️ 如必须变更（如觉醒、重塑），必须有明确剧情铺垫和说明

### 5. 修炼速度限制（防止坐火箭）
- 小境界突破（如一层→二层）：至少{c.min_minor_breakthrough_days}天
- 大境界突破（如剑气境→剑心境）：至少{c.min_major_breakthrough_days}天
- 上次突破章节：第{c.last_breakthrough_chapter}章
- ⚠️ 严禁在短时间内连续突破！

### 6. 战斗逻辑约束（防止反派降智）
- 反派行为必须有合理动机（禁止"因为是反派所以坏"）
- 禁术使用必须有铺垫（禁止突然用出未提及的禁术）
- 底牌使用必须提前说明
- 高境界反派追杀低境界主角，失败必须有合理解释（如主角逃跑、有帮手、利用地形）

### 7. 地理逻辑约束
- 主角当前位置：{c.current_location if c.current_location else "（请在写作中明确）"}
- 地点间移动需要合理时间
- 禁地（如剑冢、古地）进出必须有明确许可或解释

### 8. 时间线约束（防止时间混乱）
- 故事当前时间：第{c.current_day}天
- 本章必须标注"Day X"时间戳
- 章节间时间跳跃不能超过7天
- 严禁时间倒流（不能今天变成昨天）
- 严禁时间循环（不能"七天后"连续出现两次）

### 9. 武器命名锁定（防止精神分裂）
- 主角武器名称：{c.protagonist_weapon if hasattr(c, "protagonist_weapon") else "墨渊"}（锁定，禁止改名）
- 第一次提及后必须统一使用此名称
- 允许的状态描述：残剑、断剑、受损、修复、认主、解封（不算改名）
- 严禁使用别名

### 10. 战力计算约束（防止越级秒杀）
- 战力差距超过120%视为不合理
- 同境界越级：最多越2层（如二层打四层）
- 越级战斗必须有合理代价
- 主角越级获胜必须满足：对手轻敌/有帮手/利用环境/付出代价

---

**违规示例（严禁出现）：**
❌ "林尘来到青云剑宗"（青云剑宗不在白名单中）
❌ "苏清雪改名为叶清雪"（人物姓名锁定）
❌ "剑气境三层击败剑心境"（跨大境界战斗）
❌ "三天后突破到剑气境五层"（修炼速度过快）
❌ "九玄剑骨变成了混沌剑骨"（体质无理由变更）
❌ "赵锋在剑冢深处伏击"（未说明如何进入禁地）

**请严格检查写作内容，确保不违反以上任何约束！**
"""
        return prompt

    def update_constraints_after_chapter(
        self,
        chapter_number: int,
        chapter_content: str,
        detected_realm: Optional[str] = None,
        detected_location: Optional[str] = None,
        detected_faction: Optional[str] = None,
    ):
        """
        章节写作完成后，更新约束

        Args:
            chapter_number: 章节号
            chapter_content: 章节内容
            detected_realm: 检测到的境界变化
            detected_location: 检测到的位置变化
            detected_faction: 检测到的宗门变化
        """
        updated = False

        # 更新境界
        if detected_realm and detected_realm != self.constraints.current_realm:
            self.constraints.current_realm = detected_realm
            self.constraints.last_breakthrough_chapter = chapter_number
            updated = True

        # 更新位置
        if detected_location and detected_location != self.constraints.current_location:
            self.constraints.current_location = detected_location
            updated = True

        # 更新宗门
        if detected_faction and detected_faction in self.constraints.faction_whitelist:
            if detected_faction != self.constraints.current_faction:
                self.constraints.current_faction = detected_faction
                updated = True

        if updated:
            self._save_constraints(self.constraints)

    def validate_chapter(
        self, chapter_number: int, chapter_content: str
    ) -> List[Dict[str, Any]]:
        """
        验证章节是否违反约束 - 严格检测逻辑

        Returns:
            违规列表，每项包含type、message、severity
        """
        import re

        violations = []
        c = self.constraints

        # 1. 检查宗门名称 - 严格白名单制度
        # 提取所有可能的宗门名称（XXX宗、XXX派、XXX阁等）
        faction_pattern = r"[\u4e00-\u9fa5]{2,4}(?:宗|派|阁|门|宫|殿|院|府)"
        found_factions = set(re.findall(faction_pattern, chapter_content))

        for faction in found_factions:
            if faction not in c.faction_whitelist:
                violations.append(
                    {
                        "type": "faction_violation",
                        "message": f"检测到未定义的宗门名称：'{faction}'",
                        "severity": "critical",
                        "details": f"允许使用的宗门：{', '.join(c.faction_whitelist)}",
                        "suggestion": f"将'{faction}'改为白名单中的宗门，或在设定中添加该宗门",
                    }
                )

        # 2. 检查人物姓名变更 - 检测疑似变体
        for role, name in c.locked_names.items():
            # 如果原姓名在文中出现，检查是否有变体
            if name in chapter_content and len(name) >= 2:
                surname = name[0] if len(name) == 2 else name[:2]
                # 检测同姓不同名的变体
                variant_pattern = rf"{re.escape(surname)}[\u4e00-\u9fa5]{{1,2}}"
                variants = re.findall(variant_pattern, chapter_content)

                for variant in set(variants):
                    if variant != name and variant not in c.locked_names.values():
                        # 可能是姓名变体，需要警告
                        violations.append(
                            {
                                "type": "name_variant_warning",
                                "message": f"检测到疑似姓名变体：'{name}' vs '{variant}'",
                                "severity": "warning",
                                "details": f"角色'{role}'的姓名为'{name}'，但文中出现'{variant}'",
                                "suggestion": f"确认'{variant}'是否为'{name}'的误写",
                            }
                        )

        # 3. 检查跨境界战斗 - 严格禁止
        if c.cross_realm_combat == "forbidden":
            # 检测战斗描述
            battle_keywords = ["击败", "战胜", "击杀", "重创", "打退", "斩杀"]
            current_level = c.realm_hierarchy.get(c.current_realm, 0)

            for keyword in battle_keywords:
                if keyword in chapter_content:
                    # 检查是否涉及高境界
                    for realm, level in c.realm_hierarchy.items():
                        if level > current_level + c.max_cross_realm:
                            if realm in chapter_content:
                                # 可能是跨境界战斗
                                context_start = max(
                                    0, chapter_content.find(keyword) - 100
                                )
                                context_end = min(
                                    len(chapter_content),
                                    chapter_content.find(keyword) + 100,
                                )
                                context = chapter_content[context_start:context_end]

                                # 检查是否有代价描述
                                cost_keywords = [
                                    "代价",
                                    "燃烧",
                                    "牺牲",
                                    "重伤",
                                    "陨落",
                                    "自爆",
                                    "禁术",
                                ]
                                has_cost = any(
                                    cost in context for cost in cost_keywords
                                )

                                if not has_cost:
                                    violations.append(
                                        {
                                            "type": "cross_realm_combat",
                                            "message": f"检测到可能的跨境界战斗：{c.current_realm} vs {realm}",
                                            "severity": "critical",
                                            "details": f"主角当前境界'{c.current_realm}'尝试{keyword}高境界'{realm}'，未提及代价",
                                            "suggestion": "跨境界战斗必须付出沉重代价（重伤、牺牲、禁术等），或改为同境界战斗",
                                        }
                                    )

        # 4. 检查体质变更
        if c.locked_constitution:
            # 检测体质相关词汇
            constitution_keywords = ["体质", "剑骨", "灵根", "血脉", "神体"]
            for keyword in constitution_keywords:
                if keyword in chapter_content:
                    # 检查是否有体质变更描述
                    change_keywords = [
                        "变成",
                        "变为",
                        "化作",
                        "觉醒为",
                        "进化为",
                        "变异为",
                    ]
                    for change in change_keywords:
                        if change in chapter_content:
                            violations.append(
                                {
                                    "type": "constitution_change",
                                    "message": f"检测到可能的体质变更",
                                    "severity": "warning",
                                    "details": f"主角体质锁定为'{c.locked_constitution}'，但文中出现变更描述",
                                    "suggestion": f"如需变更体质，必须从{c.allowed_constitution_changes}中选择，并有充分铺垫",
                                }
                            )
                            break

        # 5. 检查修炼速度
        time_patterns = [
            (r"(\d+)天后", "day"),
            (r"(\d+)日后", "day"),
            (r"(\d+)个月后", "month"),
            (r"(\d+)月后", "month"),
        ]

        for pattern, unit in time_patterns:
            matches = re.findall(pattern, chapter_content)
            for match in matches:
                days = int(match)
                if unit == "month":
                    days *= 30

                # 检测是否有突破描述
                breakthrough_keywords = ["突破", "晋级", "晋升", "提升"]
                realm_keywords = ["层", "境", "阶", "级"]

                if any(kw in chapter_content for kw in breakthrough_keywords):
                    if any(kw in chapter_content for kw in realm_keywords):
                        # 可能是境界突破
                        if days < c.min_minor_breakthrough_days:
                            violations.append(
                                {
                                    "type": "cultivation_speed",
                                    "message": f"修炼速度过快：{match}{'天' if unit == 'day' else '月'}内突破",
                                    "severity": "critical",
                                    "details": f"小境界突破至少需要{c.min_minor_breakthrough_days}天",
                                    "suggestion": f"延长修炼时间至至少{c.min_minor_breakthrough_days}天，或增加详细修炼过程描写",
                                }
                            )

        # 6. 检查反派行为逻辑
        villain_keywords = ["反派", "敌人", "对手", "宿敌", "大敌"]
        for keyword in villain_keywords:
            if keyword in chapter_content:
                # 检查是否有动机描述
                motivation_keywords = ["因为", "为了", "由于", "想要", "计划", "目的"]
                has_motivation = any(
                    mot in chapter_content for mot in motivation_keywords
                )

                if not has_motivation:
                    # 获取反派相关上下文
                    idx = chapter_content.find(keyword)
                    if idx != -1:
                        context = chapter_content[
                            max(0, idx - 50) : min(len(chapter_content), idx + 100)
                        ]
                        if len(context) < 150:  # 上下文较短，可能没有足够描述
                            violations.append(
                                {
                                    "type": "villain_motivation",
                                    "message": f"反派行为缺乏动机",
                                    "severity": "warning",
                                    "details": f"检测到反派行为，但未说明其行为动机",
                                    "suggestion": "为反派添加合理的动机（复仇、野心、嫉妒、理念冲突等）",
                                }
                            )

        return violations

    def get_setting_manual(self) -> str:
        """
        生成设定说明书（对应编辑说的"用Excel拉设定表"）
        """
        c = self.constraints

        manual = f"""# 《设定说明书》

## 一、主角设定
- **姓名**：{c.protagonist_name}（锁定，禁止变更）
- **初始体质**：{c.locked_constitution}（锁定，变更需说明）
- **初始境界**：{c.current_realm}
- **所属宗门**：{c.current_faction}

## 二、宗门势力表
| 宗门名称 | 类型 | 与主角关系 |
|---------|------|-----------|
"""
        for faction in c.faction_whitelist:
            manual += f"| {faction} | | |\n"

        manual += f"""
## 三、人物档案表
| 角色定位 | 姓名 | 身份 | 备注 |
|---------|------|------|------|
"""
        for role, name in c.locked_names.items():
            manual += f"| {role} | {name} | | 姓名锁定 |\n"

        manual += f"""
## 四、境界体系表
| 境界 | 等级值 | 描述 |
|------|--------|------|
"""
        for realm, level in sorted(c.realm_hierarchy.items(), key=lambda x: x[1]):
            manual += f"| {realm} | {level} | |\n"

        manual += f"""
## 五、战力规则
- **同境界内**：可越{c.max_cross_realm}个小层
- **跨大境界**：{c.cross_realm_combat}
- **跨境界战斗必须付出的代价**：{", ".join(c.required_costs)}

## 六、修炼速度限制
- **小境界突破**（如剑气境一层→二层）：至少{c.min_minor_breakthrough_days}天
- **大境界突破**（如剑气境→剑心境）：至少{c.min_major_breakthrough_days}天

## 七、修为进度追踪表
| 章节 | 境界 | 突破方式 | 用时 | 备注 |
|------|------|---------|------|------|
| 初始 | {c.current_realm} | - | - | 初始状态 |

*请在每次突破后更新此表*
"""
        return manual
