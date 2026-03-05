"""
Story State Manager - 全局故事状态管理
用于解决"上下文失忆症"问题

功能：
1. 追踪当前地点、主角名、战力等级、进行中的剧情线
2. 在Prompt中注入硬约束，防止连续性错误
3. 验证章节内容，检测模板开头、战力通胀等

核心：维护一个全局 story_state.json，每次写作后更新
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class StoryStateManager:
    """
    故事状态管理器

    管理全局故事状态，确保章节之间的连续性
    """

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.state_file = self.project_dir / "story_state.json"

        # 模板开头检测（常见网文模板）
        self.template_openings = [
            "激光擦肩而过",
            "一道闪电划过",
            "突然的爆炸",
            "就在这时",
            "突然之间",
            "一道光芒",
            "只见",
            "突然",
            "猛然",
            "骤然",
        ]

        # 禁止出现的模式（战力通胀）
        self.power_inflation_patterns = [
            (r"抹杀.*半径", "无代价大范围秒杀"),
            (r"秒杀.*全场", "无代价秒杀"),
            (r"瞬间.*死亡", "无代价瞬杀"),
        ]

    def load_state(self) -> Dict[str, Any]:
        """
        加载现有状态或返回默认状态

        Returns:
            故事状态字典
        """
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding="utf-8"))
                logger.info(f"Loaded story state from {self.state_file}")
                return state
            except Exception as e:
                logger.warning(f"Failed to load story state: {e}")

        # 返回默认状态
        return self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """获取默认状态"""
        return {
            "current_location": "未知",
            "female_lead_name": "",
            "male_lead_name": "",
            "power_level": "未知",
            "power_level_cap": "根据当前境界确定",
            "active_plot_threads": [],
            "last_chapter_ending": "",
            "forbidden_patterns": [],
            "character_whitelist": [],  # 允许使用的角色名
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def save_state(self, state: Dict[str, Any]):
        """保存状态到JSON文件"""
        state["updated_at"] = datetime.now().isoformat()

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"Story state saved to {self.state_file}")

    def update_location(self, new_location: str):
        """更新当前地点"""
        state = self.load_state()
        state["current_location"] = new_location
        self.save_state(state)
        logger.info(f"Location updated to: {new_location}")

    def update_power_level(self, level: str, cap: str):
        """更新战力等级和上限"""
        state = self.load_state()
        state["power_level"] = level
        state["power_level_cap"] = cap
        self.save_state(state)
        logger.info(f"Power level updated to: {level} (cap: {cap})")

    def add_plot_thread(self, thread: str, chapter: int):
        """添加进行中的剧情线"""
        state = self.load_state()

        # 检查是否已存在
        for existing in state["active_plot_threads"]:
            if existing["thread"] == thread:
                existing["chapter"] = chapter
                existing["status"] = "进行中"
                break
        else:
            state["active_plot_threads"].append({
                "thread": thread,
                "chapter": chapter,
                "status": "进行中"
            })

        self.save_state(state)
        logger.info(f"Plot thread added: {thread}")

    def complete_plot_thread(self, thread: str):
        """标记剧情线完成"""
        state = self.load_state()

        for existing in state["active_plot_threads"]:
            if existing["thread"] == thread:
                existing["status"] = "已完成"

        self.save_state(state)

    def get_story_state_constraints(self) -> str:
        """
        获取故事状态约束，格式化为Prompt注入

        Returns:
            格式化的约束文本
        """
        state = self.load_state()

        constraints = ["【系统强制约束 - 严禁违背】"]

        # 1. 地点约束
        location = state.get("current_location", "未知")
        constraints.append(f"\n1. 地点：{location}")
        constraints.append("   - 禁止随意更换地点，必须有合理过渡")
        constraints.append("   - 如需更换地点，必须在上一章结尾明确说明")

        # 2. 角色约束
        constraints.append("\n2. 主要角色（禁止引入新角色）：")
        if state.get("male_lead_name"):
            constraints.append(f"   - 男主：{state['male_lead_name']}")
        if state.get("female_lead_name"):
            constraints.append(f"   - 女主：{state['female_lead_name']}")

        if state.get("character_whitelist"):
            whitelist = state["character_whitelist"]
            constraints.append(f"   - 已登场角色：{', '.join(whitelist[:10])}")
            constraints.append("   - 严禁使用上述以外的新角色名")

        # 3. 战力约束
        power_level = state.get("power_level", "未知")
        power_cap = state.get("power_level_cap", "根据境界确定")
        constraints.append(f"\n3. 战力锁定：")
        constraints.append(f"   - 当前等级：{power_level}")
        constraints.append(f"   - 战力上限：{power_cap}")
        constraints.append("   - 使用大招后必须进入虚弱期")
        constraints.append("   - 越级战斗必须有合理代价")

        # 4. 剧情线约束
        active_threads = state.get("active_plot_threads", [])
        if active_threads:
            constraints.append("\n4. 进行中的剧情（必须承接，禁止重启）：")
            for thread in active_threads[:5]:  # 最多显示5条
                if thread.get("status") == "进行中":
                    constraints.append(f"   - {thread['thread']}（第{thread['chapter']}章）")

        # 5. 上一章结尾约束
        last_ending = state.get("last_chapter_ending", "")
        if last_ending:
            constraints.append(f"\n5. 上一章结尾（必须自然承接）：")
            constraints.append(f"   {last_ending[-500:]}")  # 取最后500字

        return "\n".join(constraints)

    def update_from_chapter(self, chapter_num: int, content: str):
        """
        从章节内容更新故事状态

        Args:
            chapter_num: 章节编号
            content: 章节内容
        """
        state = self.load_state()

        # 1. 提取并更新地点
        new_location = self._extract_location(content)
        if new_location and new_location != state.get("current_location"):
            state["current_location"] = new_location
            logger.info(f"Extracted location: {new_location}")

        # 2. 提取并更新战力变化
        power_change = self._detect_power_change(content)
        if power_change:
            state["power_level"] = power_change.get("new_level", state.get("power_level"))
            state["power_level_cap"] = power_change.get("cap", state.get("power_level_cap"))
            logger.info(f"Power change: {power_change}")

        # 3. 提取并更新角色（如果发现新角色）
        new_characters = self._extract_characters(content)
        existing_whitelist = set(state.get("character_whitelist", []))
        new_chars = [c for c in new_characters if c not in existing_whitelist]
        if new_chars:
            state["character_whitelist"] = list(existing_whitelist | set(new_chars))
            logger.info(f"New characters added: {new_chars}")

        # 4. 更新上一章结尾
        state["last_chapter_ending"] = content[-1000:] if len(content) > 1000 else content

        # 5. 提取剧情线变化
        plot_changes = self._extract_plot_changes(content, chapter_num)
        for change in plot_changes:
            if change["type"] == "new":
                self.add_plot_thread(change["thread"], chapter_num)
            elif change["type"] == "complete":
                self.complete_plot_thread(change["thread"])

        self.save_state(state)

    def _extract_location(self, text: str) -> Optional[str]:
        """从文本中提取地点"""
        # 常见地点关键词 - 简化版
        location_keywords = [
            "星尘学院", "暮霭镇", "议会", "训练场", "城市", "基地", "总部",
            "神殿", "学院", "城堡", "山脉", "森林", "沙漠", "海岸"
        ]

        for keyword in location_keywords:
            if keyword in text[:2000]:
                return keyword

        return None

    def _detect_power_change(self, text: str) -> Optional[Dict[str, str]]:
        """检测战力变化"""
        # 境界升级关键词
        upgrade_patterns = [
            (r"突破到(\w+)境", "new_level"),
            (r"晋升为(\w+)", "new_level"),
            (r"踏入(\w+)境", "new_level"),
            (r"升级到(\w+)", "new_level"),
        ]

        for pattern, key in upgrade_patterns:
            match = re.search(pattern, text)
            if match:
                new_level = match.group(1)
                return {
                    "new_level": new_level,
                    "cap": f"{new_level}境上限，使用越级技能需付出代价"
                }

        return None

    def _extract_characters(self, text: str) -> List[str]:
        """提取文本中的角色名"""
        # 这是一个简化实现，实际可以使用NER
        # 这里检查常见的女性名字模式
        potential_names = []

        # 简单模式：引号中的对话
        matches = re.findall(r"“([^”]{2,6})”", text[:5000])
        potential_names.extend(matches)

        return list(set(potential_names))

    def _extract_plot_changes(self, text: str, chapter: int) -> List[Dict[str, str]]:
        """提取剧情线变化"""
        changes = []

        # 新剧情线开始
        new_plot_keywords = ["准备", "计划", "即将", "开始行动"]
        for keyword in new_plot_keywords:
            if keyword in text[:1000]:
                # 简化：取关键词后的一句话
                idx = text.find(keyword)
                context = text[idx:idx+50]
                changes.append({
                    "type": "new",
                    "thread": context.strip()
                })
                break

        # 剧情线完成
        complete_keywords = ["成功", "完成", "终于", "彻底"]
        for keyword in complete_keywords:
            if keyword in text[-1000:]:
                idx = text.rfind(keyword)
                context = text[max(0, idx-30):idx+20]
                changes.append({
                    "type": "complete",
                    "thread": context.strip()
                })
                break

        return changes

    def validate_chapter(self, chapter_text: str) -> Tuple[bool, List[str]]:
        """
        验证章节内容，检测连续性错误

        Args:
            chapter_text: 章节文本

        Returns:
            (是否通过, 错误列表)
        """
        errors = []
        state = self.load_state()

        # 1. 检查模板开头
        first_200 = chapter_text[:200]
        for template in self.template_openings:
            if template in first_200:
                errors.append(f"使用了通用模板开头: {template}")

        # 2. 检查角色名一致性
        female_lead = state.get("female_lead_name", "")
        male_lead = state.get("male_lead_name", "")

        # 如果有主角名，检查是否一致（简化检查）
        # 实际应该更复杂地检查
        if female_lead and male_lead:
            # 检查是否提到了"新"女性角色
            possible_new_names = ['林雨桐', '林诗雅', '苏晴', '白浅', '慕容', '上官']
            for name in possible_new_names:
                if name in chapter_text and name != female_lead:
                    # 排除"林晚晴的妹妹"这类合法引用
                    if f"{female_lead}的" not in chapter_text and name != female_lead:
                        pass  # 暂时不报错，因为可能是配角

        # 3. 检查战力通胀
        for pattern, desc in self.power_inflation_patterns:
            if re.search(pattern, chapter_text):
                # 检查是否有代价描述
                has_cost = any(cost_word in chapter_text for cost_word in ["代价", "虚弱", "昏迷", "消耗", "反噬"])
                if not has_cost:
                    errors.append(f"战力通胀：{desc}，但没有描写代价")

        # 4. 检查地点变化是否有过渡
        current_location = state.get("current_location", "")
        if current_location and current_location != "未知":
            # 检查本章是否暗示了地点变化
            location_change_keywords = ["来到", "前往", "抵达", "回到", "进入"]
            has_location_change = any(kw in chapter_text[:1000] for kw in location_change_keywords)

            # 如果没有明确地点变化关键词，检查是否在同一地点
            if not has_location_change:
                # 检查本章提到的地点是否与当前一致
                extracted_loc = self._extract_location(chapter_text)
                if extracted_loc and extracted_loc != current_location:
                    # 可能有问题，但不确定，警告而非错误
                    logger.warning(f"Location may have changed from {current_location} to {extracted_loc}")

        return len(errors) == 0, errors

    def initialize_from_characters(self):
        """从 characters.json 初始化故事状态"""
        characters_file = self.project_dir / "characters.json"
        if not characters_file.exists():
            logger.warning("characters.json not found, cannot initialize story state")
            return

        try:
            data = json.loads(characters_file.read_text(encoding="utf-8"))

            # 处理两种格式：{"characters": [...]} 或 [...]
            if isinstance(data, dict) and "characters" in data:
                characters = data["characters"]
            elif isinstance(data, list):
                characters = data
            else:
                logger.warning(f"Unknown characters.json format")
                return

            state = self.load_state()

            # 提取主角名
            for char in characters:
                role = char.get("role", "")
                name = char.get("name", "")

                if not name:
                    continue

                if "主角" in role or "男主" in role:
                    if not state.get("male_lead_name"):
                        state["male_lead_name"] = name

                if "女主" in role:
                    if not state.get("female_lead_name"):
                        state["female_lead_name"] = name

                # 添加所有角色到白名单
                if name and name not in state["character_whitelist"]:
                    state["character_whitelist"].append(name)

            self.save_state(state)
            logger.info(f"Story state initialized from characters.json")

        except Exception as e:
            logger.error(f"Failed to initialize from characters.json: {e}")


def create_story_state_manager(project_dir: str) -> StoryStateManager:
    """创建并初始化故事状态管理器"""
    manager = StoryStateManager(project_dir)

    # 尝试从characters.json初始化
    manager.initialize_from_characters()

    return manager
