"""
Constraint Template Manager - 约束模板管理器

管理不同类型的约束模板，为写作提供类型特定的约束

模板类型：
- scifi: 科幻/后室/SCP - 认知阶段、资源消耗、实体威胁
- xianxia: 仙侠/玄幻 - 境界体系、修炼速度、宗门规则
- urban: 都市 - 财富系统、人脉关系、时间线
- suspense: 悬疑 - 线索铺陈、谜题设计、推理逻辑
- game: 游戏/系统 - 任务系统、升级规则、副本设计
- historical: 历史 - 朝堂权谋、经济发展、军事战略
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


# 内置约束模板
TEMPLATES = {
    "scifi": {
        "name": "科幻/后室",
        "description": "科幻、末世、后室、SCP等类型",
        "has_cultivation": False,
        "constraints": {
            "worldview": [
                "无修炼体系，主角是普通人",
                "依靠智慧和道具生存",
                "禁止出现修仙词汇：修炼、灵气、法力、金丹、元婴",
                "禁止出现境界设定",
            ],
            "power_system": {
                "type": "cognitive_stages",
                "stages": ["迷失者", "观察者", "适应者", "探索者", "解析者"],
                "description": "认知深化 = 更多知识/经验，不是修仙升级",
            },
            "entity_rules": {
                "required": True,
                "description": "实体杀人规则是绝对的，不能违反",
                "examples": {
                    "SCP-106": {"ability": "穿墙", "weakness": "高温"},
                    "SCP-939": {"ability": "声波攻击", "weakness": "听力"},
                },
            },
            "resource_tracking": {
                "required": True,
                "items": ["杏仁水", "电池", "食物", "医疗用品"],
                "consumption_rate": "严格",
            },
            "time_tracking": {
                "required": True,
                "format": "Day X",
                "min_days_between_major_events": 1,
            },
        },
    },
    "xianxia": {
        "name": "仙侠/玄幻",
        "description": "仙侠、玄幻、修真等类型",
        "has_cultivation": True,
        "constraints": {
            "worldview": [
                "有完整的修炼体系",
                "灵气、法力、功法、秘境",
                "禁止出现科幻词汇：收容、实体、基金会",
            ],
            "power_system": {
                "type": "realm_hierarchy",
                "stages": ["无剑者", "剑气境", "剑心境", "剑魂境", "剑仙境"],
                "cross_realm_combat": "forbidden",
            },
            "cultivation_speed": {
                "minor_breakthrough_days": 7,
                "major_breakthrough_days": 30,
            },
            "faction_rules": {
                "required": True,
                "max_factions": 5,
                "changes_require_reason": True,
            },
            "constitution_lock": {
                "required": True,
                "allowed_changes": ["觉醒", "返祖", "重塑", "进化"],
            },
        },
    },
    "urban": {
        "name": "都市",
        "description": "都市、重生、总裁等类型",
        "has_cultivation": False,
        "constraints": {
            "worldview": [
                "现代都市背景",
                "禁止出现修仙、灵气等超自然元素",
                "现实合理的社会规则",
            ],
            "wealth_system": {
                "required": True,
                "milestones": ["第一桶金", "公司上市", "商业帝国"],
                "progress_tracking": "每5章记录一次",
            },
            "relationship_tracking": {
                "required": True,
                "max_concurrent": 3,
                "changes_require_arc": True,
            },
            "time_tracking": {
                "required": True,
                "format": "年/月/日",
                "max_jump_days": 30,
            },
        },
    },
    "suspense": {
        "name": "悬疑/推理",
        "description": "悬疑、推理、惊悚等类型",
        "has_cultivation": False,
        "constraints": {
            "worldview": ["现实或近现实背景", "禁止超自然解释除非伏笔充分"],
            "clue_tracking": {
                "required": True,
                "clue_density": "每3000字至少1个关键线索",
                "red_herrings": "不超过关键线索的2倍",
            },
            "mystery_structure": {
                "foreshadowing_required": True,
                "fair_play": True,
                "twist_limit": "每10章不超过1个大反转",
            },
            "time_tracking": {
                "required": True,
                "format": "年/月/日 时:分",
                "exact_timestamps": True,
            },
        },
    },
    "game": {
        "name": "游戏/系统",
        "description": "游戏、副本、系统流等类型",
        "has_cultivation": False,
        "constraints": {
            "worldview": ["游戏世界或现实+系统", "数值化能力体系"],
            "system_rules": {
                "required": True,
                "notification_format": "系统提示：",
                "upgrade_announcement": True,
            },
            "task_tracking": {
                "required": True,
                "task_format": "【主线任务】/【支线任务】/【日常任务】",
                "completion_criteria": "明确",
            },
            "inventory_tracking": {
                "required": True,
                "format": "【背包】物品列表",
                "weight_limit": True,
            },
            "level_system": {"required": True, "exp_curve": "每级所需经验递增"},
        },
    },
    "historical": {
        "name": "历史",
        "description": "历史、穿越、权谋等类型",
        "has_cultivation": False,
        "constraints": {
            "worldview": ["古代历史背景", "符合历史基本逻辑", "禁止现代词汇乱入"],
            "politics_tracking": {
                "required": True,
                "faction_count": "不超过5个主要势力",
                "alliance_changes": "需逻辑支撑",
            },
            "economy_tracking": {
                "required": True,
                "currency": "两/银/铜",
                "inflation_control": True,
            },
            "military_tracking": {
                "required": True,
                "troop_numbers": "符合古代规模",
                "siege_logic": "符合历史常识",
            },
            "time_tracking": {
                "required": True,
                "format": "年号/季节",
                "seasonal_changes": True,
            },
        },
    },
    "general": {
        "name": "通用",
        "description": "默认通用类型",
        "has_cultivation": False,
        "constraints": {
            "worldview": [],
            "basic_rules": {
                "character_names_locked": True,
                "timeline_consistency": True,
            },
        },
    },
}


@dataclass
class ConstraintTemplate:
    """约束模板"""

    name: str
    description: str
    has_cultivation: bool
    constraints: Dict[str, Any]


class ConstraintTemplateManager:
    """
    约束模板管理器

    加载和管理不同类型的约束模板
    """

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = Path(template_dir) if template_dir else None
        self.templates = TEMPLATES.copy()

        if self.template_dir and self.template_dir.exists():
            self._load_custom_templates()

    def _load_custom_templates(self):
        """加载自定义模板"""
        for template_file in self.template_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template_name = template_file.stem
                    self.templates[template_name] = template_data
            except Exception as e:
                print(f"加载模板 {template_file} 失败: {e}")

    def get_template(self, template_name: str) -> Optional[ConstraintTemplate]:
        """
        获取指定模板

        Args:
            template_name: 模板名称 (scifi/xianxia/urban/suspense/game/historical)

        Returns:
            ConstraintTemplate or None
        """
        data = self.templates.get(template_name)
        if not data:
            return None

        return ConstraintTemplate(
            name=data.get("name", template_name),
            description=data.get("description", ""),
            has_cultivation=data.get("has_cultivation", False),
            constraints=data.get("constraints", {}),
        )

    def get_prompt_section(self, template_name: str) -> str:
        """
        获取模板的约束提示词部分

        Args:
            template_name: 模板名称

        Returns:
            str: 格式化的约束提示词
        """
        template = self.get_template(template_name)
        if not template:
            return ""

        prompt = f"""
### 类型特定约束 ({template.name})
"""

        constraints = template.constraints

        # 世界观约束
        if "worldview" in constraints:
            prompt += f"""
**世界观规则：**
"""
            for rule in constraints["worldview"]:
                prompt += f"- {rule}\n"

        # 战力体系
        if "power_system" in constraints:
            ps = constraints["power_system"]
            prompt += f"""
**战力体系：**
"""
            if ps.get("type") == "cognitive_stages":
                stages = ps.get("stages", [])
                prompt += f"- 认知阶段体系：{', '.join(stages)}\n"
                prompt += f"- {ps.get('description', '')}\n"
            elif ps.get("type") == "realm_hierarchy":
                stages = ps.get("stages", [])
                prompt += f"- 境界体系：{', '.join(stages)}\n"
                prompt += f"- 跨境界战斗：{ps.get('cross_realm_combat', 'forbidden')}\n"

        # 实体规则（后室/SCP）
        if "entity_rules" in constraints:
            er = constraints["entity_rules"]
            if er.get("required"):
                prompt += f"""
**实体规则（必须遵守）：**
- {er.get("description", "实体规则是绝对的")}
"""
                examples = er.get("examples", {})
                for entity, info in examples.items():
                    prompt += f"- {entity}: 能力={info.get('ability', '未知')}, 弱点={info.get('weakness', '未知')}\n"

        # 资源追踪
        if "resource_tracking" in constraints:
            rt = constraints["resource_tracking"]
            if rt.get("required"):
                items = rt.get("items", [])
                prompt += f"""
**资源追踪：**
- 关键物品：{", ".join(items)}
- 消耗规则：{rt.get("consumption_rate", "正常")}
"""

        # 时间追踪
        if "time_tracking" in constraints:
            tt = constraints["time_tracking"]
            if tt.get("required"):
                prompt += f"""
**时间线规则：**
- 时间格式：{tt.get("format", "Day X")}
"""
                if tt.get("min_days_between_major_events"):
                    prompt += f"- 重大事件间隔：至少{tt.get('min_days_between_major_events')}天\n"

        # 修炼速度（仙侠）
        if "cultivation_speed" in constraints:
            cs = constraints["cultivation_speed"]
            prompt += f"""
**修炼速度限制：**
- 小境界突破：至少{cs.get("minor_breakthrough_days", 7)}天
- 大境界突破：至少{cs.get("major_breakthrough_days", 30)}天
"""

        return prompt

    def get_all_template_names(self) -> List[str]:
        """获取所有可用模板名称"""
        return list(self.templates.keys())

    def list_templates(self) -> Dict[str, str]:
        """列出所有模板"""
        return {
            name: data.get("description", "") for name, data in self.templates.items()
        }


# 便捷函数
def get_template_manager(
    template_dir: Optional[str] = None,
) -> ConstraintTemplateManager:
    """快速获取模板管理器"""
    return ConstraintTemplateManager(template_dir)


if __name__ == "__main__":
    manager = ConstraintTemplateManager()

    print("=" * 60)
    print("ConstraintTemplateManager 测试")
    print("=" * 60)

    # 测试各类型模板
    test_templates = ["scifi", "xianxia", "urban", "suspense", "game", "historical"]

    for template_name in test_templates:
        template = manager.get_template(template_name)
        print(f"\n【{template.name}】")
        print(f"描述: {template.description}")
        print(f"有修炼体系: {template.has_cultivation}")
        print(f"约束键: {list(template.constraints.keys())}")

    # 测试提示词生成
    print("\n" + "=" * 60)
    print("scifi 模板提示词")
    print("=" * 60)
    print(manager.get_prompt_section("scifi"))
