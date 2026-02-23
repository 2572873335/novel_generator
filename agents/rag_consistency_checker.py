"""
RAG-based Consistency Checker (Version 2.0)

This module enhances the original rule-based consistency checker with
Retrieval Augmented Generation (RAG) for more intelligent consistency detection.

Features:
- Build knowledge base from world-building documents, character settings, and chapters
- Use semantic retrieval to get relevant context for consistency checks
- Enhanced plot logic consistency checking using retrieved context
- Hybrid approach: rule-based + RAG-based checks

Usage:
    checker = RAGConsistencyChecker(project_dir)
    checker.build_knowledge_base()  # Build from documents
    result = checker.check_single_chapter(5)  # Check chapter 5
"""

import json
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from core.local_vector_store import LocalVectorStore


@dataclass
class ConsistencyViolation:
    """一致性违规记录"""

    type: str
    severity: str  # critical, warning, info
    message: str
    chapter: int
    details: str
    suggestion: str
    # RAG-specific fields
    retrieved_context: List[str] = field(default_factory=list)  # Retrieved context used
    check_method: str = "rule"  # "rule" or "rag"


@dataclass
class RetrievalContext:
    """检索到的上下文"""

    character_mentions: Dict[str, List[str]] = field(
        default_factory=dict
    )  # character_id -> list of mentions
    faction_mentions: Dict[str, List[str]] = field(default_factory=dict)
    realm_history: List[Dict] = field(
        default_factory=list
    )  # [{chapter, realm, character}]
    ability_history: List[Dict] = field(
        default_factory=list
    )  # [{chapter, ability, character}]
    location_history: List[Dict] = field(
        default_factory=list
    )  # [{chapter, location, character}]
    timeline_events: List[Dict] = field(
        default_factory=list
    )  # [{chapter, event, characters}]


class RAGConsistencyChecker:
    """
    RAG增强的一致性检查器

    设计原则：
    1. 保留原有的规则检查作为基础
    2. 使用RAG检索增强上下文感知
    3. 对于可疑内容使用RAG进行二次验证
    """

    def __init__(self, project_dir: str, llm_client=None):
        self.project_dir = Path(project_dir)
        self.llm = llm_client
        self.chapters_dir = self.project_dir / "chapters"

        # 知识库
        self.vector_store: Optional[LocalVectorStore] = None
        self.knowledge_base_built = False

        # 检索到的上下文缓存
        self.context_cache: Dict[int, RetrievalContext] = {}

        # 加载配置
        self.config = self._load_config()

        # 加载约束
        self.constraints_file = self.project_dir / "writing_constraints.json"
        self.constraints = self._load_constraints()

        # 加载世界设定
        self.world_rules = self._load_world_rules()

        # 角色设定
        self.character_profiles = self._load_character_profiles()

        # 章节索引
        self.chapter_index = self._build_chapter_index()

        # 初始化向量存储
        self._init_vector_store()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_file = Path("config/consistency_rules.yaml")
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _load_constraints(self) -> Dict:
        """加载写作约束"""
        if self.constraints_file.exists():
            with open(self.constraints_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_world_rules(self) -> Dict:
        """加载世界规则"""
        world_rules_file = self.project_dir / "world-rules.json"
        if world_rules_file.exists():
            with open(world_rules_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_character_profiles(self) -> Dict:
        """加载角色设定"""
        chars_file = self.project_dir / "characters.json"
        if chars_file.exists():
            with open(chars_file, "r", encoding="utf-8") as f:
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

    def _init_vector_store(self):
        """初始化向量存储"""
        db_path = self.project_dir / "rag_consistency.db"
        self.vector_store = LocalVectorStore(str(db_path))

    def build_knowledge_base(self):
        """构建知识库 - 从所有相关文档中索引内容"""
        documents = []

        # 1. 添加世界规则
        if self.world_rules:
            world_text = json.dumps(self.world_rules, ensure_ascii=False)
            documents.append({"text": world_text, "metadata": {"type": "world_rules"}})

        # 2. 添加角色设定
        if self.character_profiles:
            chars_text = json.dumps(self.character_profiles, ensure_ascii=False)
            documents.append(
                {"text": chars_text, "metadata": {"type": "character_profiles"}}
            )

        # 3. 添加约束
        if self.constraints:
            constraints_text = json.dumps(self.constraints, ensure_ascii=False)
            documents.append(
                {"text": constraints_text, "metadata": {"type": "constraints"}}
            )

        # 4. 添加所有已完成的章节
        for chapter_num, file_path in sorted(self.chapter_index.items()):
            content = file_path.read_text(encoding="utf-8")
            documents.append(
                {
                    "text": content,
                    "metadata": {"type": "chapter", "chapter": chapter_num},
                }
            )

        # 5. 添加大纲
        outline_file = self.project_dir / "outline.md"
        if outline_file.exists():
            outline_text = outline_file.read_text(encoding="utf-8")
            documents.append({"text": outline_text, "metadata": {"type": "outline"}})

        # 添加到向量存储
        for doc in documents:
            self.vector_store.add(text=doc["text"], metadata=doc["metadata"])

        self.knowledge_base_built = True

    def retrieve_context(self, query: str, top_k: int = 5) -> List[str]:
        """检索相关上下文"""
        if not self.knowledge_base_built:
            self.build_knowledge_base()

        results = self.vector_store.search(query)
        # Apply top_k limit after getting results
        return [r.text for r in results[:top_k]]

    def get_chapter_context(
        self, chapter_number: int, max_chapters: int = 3
    ) -> RetrievalContext:
        """获取指定章节的上下文（包括前文回顾）"""
        if chapter_number in self.context_cache:
            return self.context_cache[chapter_number]

        context = RetrievalContext()

        # 收集前文章节内容
        relevant_chapters = range(
            max(1, chapter_number - max_chapters), chapter_number + 1
        )

        all_text = ""
        for ch in relevant_chapters:
            if ch in self.chapter_index:
                content = self._load_chapter_content(ch)
                all_text += f"\n\n=== Chapter {ch} ===\n{content}"

        # 提取角色提及
        context = self._extract_context_info(all_text, chapter_number)

        # 缓存
        self.context_cache[chapter_number] = context
        return context

    def _extract_context_info(
        self, text: str, current_chapter: int
    ) -> RetrievalContext:
        """从文本中提取上下文信息"""
        context = RetrievalContext()

        # 提取角色提及
        for char_id, char_data in self.character_profiles.items():
            name = char_data.get("name", char_id)
            # 简单的名称匹配
            if name in text:
                mentions = re.findall(rf".{{0,50}}{name}.{{0,50}}", text)
                context.character_mentions[char_id] = mentions

        # 提取境界信息
        realm_patterns = [
            r"(\w+)突破到?了?(\w+)境",
            r"(\w+)达到(\w+)境",
            r"(\w+)晋升(\w+)境",
            r"进入了(\w+)境",
        ]

        for pattern in realm_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2:
                    char_name = match[0]
                    realm = match[1]
                    context.realm_history.append(
                        {
                            "chapter": current_chapter,
                            "character": char_name,
                            "realm": realm,
                        }
                    )

        # 提取地点信息
        location_pattern = r"在([^，。]{2,10})(?:城|省|州|山|谷|岛|府|宗|派|阁)"
        locations = re.findall(location_pattern, text)
        for loc in set(locations):
            context.location_history.append(
                {"chapter": current_chapter, "location": loc}
            )

        return context

    def check_all_chapters(self) -> Dict[str, Any]:
        """检查所有章节的一致性"""
        if not self.knowledge_base_built:
            self.build_knowledge_base()

        all_violations = []
        chapter_results = {}

        for chapter_num in sorted(self.chapter_index.keys()):
            result = self.check_single_chapter(chapter_num)
            chapter_results[chapter_num] = result
            all_violations.extend(result.get("violations", []))

        # 跨章节检查（使用RAG）
        cross_chapter_violations = self._check_cross_chapter_consistency_rag()
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
            "rag_checks_performed": True,
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

        # 获取上下文
        context = self.get_chapter_context(chapter_number)

        # 1. 宗门名称检查（规则基础）
        faction_violations = self._check_faction_consistency(chapter_number, content)
        violations.extend(faction_violations)

        # 2. 人物姓名检查（规则基础 + RAG增强）
        name_violations = self._check_name_consistency_rag(
            chapter_number, content, context
        )
        violations.extend(name_violations)

        # 3. 战力体系检查（RAG增强）
        combat_violations = self._check_combat_consistency_rag(
            chapter_number, content, context
        )
        violations.extend(combat_violations)

        # 4. 修为进度检查（RAG增强）
        cultivation_violations = self._check_cultivation_consistency_rag(
            chapter_number, content, context
        )
        violations.extend(cultivation_violations)

        # 5. 体质设定检查（规则基础）
        constitution_violations = self._check_constitution_consistency(
            chapter_number, content
        )
        violations.extend(constitution_violations)

        # 6. 情节逻辑检查（RAG增强）
        plot_violations = self._check_plot_logic_rag(chapter_number, content, context)
        violations.extend(plot_violations)

        # 7. 时间线检查
        timeline_violations = self._check_timeline_consistency(chapter_number, content)
        violations.extend(timeline_violations)

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

    # =========================================================================
    # Rule-based checks (保留原有逻辑)
    # =========================================================================

    def _check_faction_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """检查宗门名称一致性"""
        violations = []

        whitelist = self.constraints.get("faction_whitelist", [])
        if not whitelist:
            return violations

        faction_pattern = (
            r"[\u4e00-\u9fa5]{2,6}(?:宗|派|阁|门|宫|殿|院|府|山|谷|岛|盟|会)"
        )
        found_factions = set(re.findall(faction_pattern, content))

        for faction in found_factions:
            if faction not in whitelist:
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
                            "check_method": "rule",
                        }
                    )
                else:
                    violations.append(
                        {
                            "type": "undefined_faction",
                            "severity": "critical",
                            "message": f"检测到未定义的宗门：'{faction}'",
                            "chapter": chapter_number,
                            "details": "该宗门不在允许使用的白名单中",
                            "suggestion": f"使用白名单中的宗门：{', '.join(whitelist[:5])}...",
                            "check_method": "rule",
                        }
                    )

        return violations

    def _find_similar_faction(
        self, faction: str, whitelist: List[str]
    ) -> Optional[str]:
        """查找相似的宗门名称"""
        for valid_faction in whitelist:
            if faction[-1] == valid_faction[-1]:
                common_prefix = ""
                for i, (c1, c2) in enumerate(zip(faction, valid_faction)):
                    if c1 == c2:
                        common_prefix += c1
                    else:
                        break
                if len(common_prefix) >= 1:
                    return valid_faction
        return None

    def _check_constitution_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """检查体质设定一致性"""
        violations = []

        # 从角色设定中获取体质
        constitutions = set()
        for char_id, char_data in self.character_profiles.items():
            if "constitution" in char_data:
                constitutions.add(char_data["constitution"])

        # 检查是否有冲突的体质描述
        for char_id, char_data in self.character_profiles.items():
            name = char_data.get("name", char_id)
            constitution = char_data.get("constitution", "")

            # 检索相关内容
            context = self.retrieve_context(f"{name} {constitution}", top_k=3)
            context_text = " ".join(context)

            # 检查是否提到了其他体质
            mentioned_constitutions = re.findall(r"(\w+体质|特殊体质|\s体质)", content)

            for mc in mentioned_constitutions:
                if mc != constitution and mc not in constitutions:
                    violations.append(
                        {
                            "type": "constitution_conflict",
                            "severity": "warning",
                            "message": f"可能存在体质设定冲突：'{mc}'",
                            "chapter": chapter_number,
                            "details": f"角色{name}的体质是'{constitution}'，但文中提到'{mc}'",
                            "suggestion": "确认体质设定是否一致",
                            "check_method": "rag",
                        }
                    )

        return violations

    # =========================================================================
    # RAG-enhanced checks
    # =========================================================================

    def _check_name_consistency_rag(
        self, chapter_number: int, content: str, context: RetrievalContext
    ) -> List[Dict]:
        """RAG增强的姓名一致性检查"""
        violations = []

        # 获取该章节前所有章节提到的角色名
        all_previous_names = set()
        for char_id, char_data in self.character_profiles.items():
            all_previous_names.add(char_data.get("name", char_id))

        # 检查本章提到的角色名是否一致
        for char_id, char_data in self.character_profiles.items():
            name = char_data.get("name", char_id)
            aliases = char_data.get("aliases", [])

            # 从RAG检索获取历史提及
            query = f"{name}角色"
            retrieved = self.retrieve_context(query, top_k=5)
            retrieved_text = " ".join(retrieved)

            # 检查是否有其他名字指代同一人
            for alias in aliases:
                if alias in content and alias not in [name]:
                    # 确认是否真的是别名
                    if alias not in retrieved_text:
                        violations.append(
                            {
                                "type": "name_consistency",
                                "severity": "warning",
                                "message": f"检测到可能的姓名不一致：'{alias}'",
                                "chapter": chapter_number,
                                "details": f"'{alias}'可能是'{name}'的别名，请确认",
                                "suggestion": "统一使用角色姓名",
                                "retrieved_context": retrieved[:2],
                                "check_method": "rag",
                            }
                        )

        return violations

    def _check_combat_consistency_rag(
        self, chapter_number: int, content: str, context: RetrievalContext
    ) -> List[Dict]:
        """RAG增强的战力体系一致性检查"""
        violations = []

        # 检索历史战斗记录
        combat_query = "战斗 越级挑战 战力"
        retrieved = self.retrieve_context(combat_query, top_k=5)

        # 查找越级战斗的描述
        level_up_patterns = [
            r"(\w+)越(\d+)级挑战",
            r"(\w+)击败了(\w+)境",
            r"(\w+)跨境界",
        ]

        for pattern in level_up_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # 检查是否符合规则
                if len(match) >= 2:
                    attacker = match[0]
                    # 从检索内容中查找被挑战者的境界
                    for ret in retrieved:
                        if attacker in ret:
                            # 检查是否有合理的越级理由
                            if "越级挑战" not in ret and "跨境" not in ret:
                                violations.append(
                                    {
                                        "type": "combat_power",
                                        "severity": "warning",
                                        "message": f"可能存在战力崩坏：{attacker}的越级战斗",
                                        "chapter": chapter_number,
                                        "details": "需要确认是否有足够的越级理由",
                                        "suggestion": "添加越级战斗的合理理由",
                                        "retrieved_context": retrieved[:2],
                                        "check_method": "rag",
                                    }
                                )

        return violations

    def _check_cultivation_consistency_rag(
        self, chapter_number: int, content: str, context: RetrievalContext
    ) -> List[Dict]:
        """RAG增强的修为进度一致性检查"""
        violations = []

        # 获取修炼速度限制
        speed_limit = self.constraints.get("cultivation_speed_limit", {})
        small_realm_days = speed_limit.get("small_realm", 7)
        large_realm_days = speed_limit.get("large_realm", 30)

        # 检索历史修炼记录
        cultivation_query = "突破 晋升 境界"
        retrieved = self.retrieve_context(cultivation_query, top_k=10)

        # 查找突破描述
        breakthrough_patterns = [
            r"(\w+)突破到?了?(\w+)境",
            r"(\w+)达到(\w+)境",
            r"(\w+)晋升为?(\w+)境",
        ]

        breakthroughs = []
        for pattern in breakthrough_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) >= 2:
                    breakthroughs.append({"character": match[0], "realm": match[1]})

        # 检查修炼速度
        for bt in breakthroughs:
            char_name = bt["character"]
            realm = bt["realm"]

            # 从检索内容中查找历史境界
            for ret in retrieved:
                if char_name in ret:
                    # 检查境界变化是否合理
                    if "突破" in ret or "晋升" in ret:
                        # 可能修炼过快
                        violations.append(
                            {
                                "type": "cultivation_speed",
                                "severity": "warning",
                                "message": f"检测到{char_name}境界变化：{realm}",
                                "chapter": chapter_number,
                                "details": "请确认修炼速度是否符合设定",
                                "suggestion": f"小境界至少{speed_limit}天",
                                "retrieved_context": [ret],
                                "check_method": "rag",
                            }
                        )

        return violations

    def _check_plot_logic_rag(
        self, chapter_number: int, content: str, context: RetrievalContext
    ) -> List[Dict]:
        """RAG增强的情节逻辑一致性检查"""
        violations = []

        # 检索相关历史情节
        plot_query = f"Chapter {chapter_number - 1} 情节"
        retrieved = self.retrieve_context(plot_query, top_k=5)

        # 查找本章开头与上章结尾的承接
        # 检查关键情节转折
        key_events = ["死亡", "离别", "背叛", "中毒", "重伤", "闭关"]

        for event in key_events:
            if event in content:
                # 检索是否有过渡
                query = f"{event} 前后 过渡"
                event_retrieved = self.retrieve_context(query, top_k=3)

                if not event_retrieved:
                    violations.append(
                        {
                            "type": "plot_transition",
                            "severity": "info",
                            "message": f"检测到关键情节：'{event}'",
                            "chapter": chapter_number,
                            "details": "建议添加情节过渡",
                            "suggestion": "添加适当的铺垫和过渡",
                            "retrieved_context": event_retrieved,
                            "check_method": "rag",
                        }
                    )

        # 检查角色行为一致性
        for char_id, char_data in self.character_profiles.items():
            name = char_data.get("name", char_id)
            personality = char_data.get("personality", "")

            if name in content and personality:
                # 检索角色行为历史
                query = f"{name} {personality} 行为"
                retrieved = self.retrieve_context(query, top_k=3)

                # 简单检查：如果是反派性格但做了好事
                if "阴险" in personality or "狡诈" in personality:
                    if "帮助" in content or "拯救" in content:
                        # 检查是否有合理动机
                        if not any("阴谋" in r or "利用" in r for r in retrieved):
                            violations.append(
                                {
                                    "type": "character_behavior",
                                    "severity": "warning",
                                    "message": f"角色{name}的行为可能与其性格不符",
                                    "chapter": chapter_number,
                                    "details": f"角色性格是'{personality}'，但行为似乎不符",
                                    "suggestion": "添加合理的动机解释",
                                    "retrieved_context": retrieved[:2],
                                    "check_method": "rag",
                                }
                            )

        return violations

    def _check_cross_chapter_consistency_rag(self) -> List[Dict]:
        """跨章节一致性检查（使用RAG）"""
        violations = []

        if not self.chapter_index:
            return violations

        # 检查章节间的战力平衡
        combat_query = "战斗 越级 击杀"
        all_combat = self.retrieve_context(combat_query, top_k=20)

        # 检查是否有不合理的越级击杀
        for i, ret in enumerate(all_combat):
            if "越级击杀" in ret or "跨境击杀" in ret:
                # 检查后续是否有交代
                violations.append(
                    {
                        "type": "cross_chapter_power",
                        "severity": "info",
                        "message": "检测到越级击杀",
                        "chapter": 0,
                        "details": "检查后续章节是否合理交代",
                        "suggestion": "确保战力体系不崩坏",
                        "retrieved_context": [ret],
                        "check_method": "rag",
                    }
                )

        return violations

    def _check_timeline_consistency(
        self, chapter_number: int, content: str
    ) -> List[Dict]:
        """检查时间线一致性"""
        violations = []

        # 简单的季节/时间检查
        seasons = ["春天", "夏天", "秋天", "冬天"]
        month_pattern = r"(\d+)月"

        found_seasons = [s for s in seasons if s in content]
        found_months = re.findall(month_pattern, content)

        # 检查是否有明显的时间矛盾
        # 这里可以添加更复杂的逻辑

        return violations

    def _check_weapon_naming(self, chapter_number: int, content: str) -> List[Dict]:
        """检查武器命名一致性"""
        violations = []

        # 加载角色武器设定
        weapons = {}
        for char_id, char_data in self.character_profiles.items():
            if "weapons" in char_data:
                weapons[char_id] = char_data["weapons"]

        # 检查武器名称是否一致
        # (简化实现)

        return violations


# ============================================================================
# 兼容性包装器
# ============================================================================


class ConsistencyChecker(RAGConsistencyChecker):
    """
    兼容性包装器

    保持与原 ConsistencyChecker 的接口兼容
    """

    def __init__(self, project_dir: str, llm_client=None):
        super().__init__(project_dir, llm_client)

        # 确保知识库已构建
        if not self.knowledge_base_built:
            self.build_knowledge_base()

    def check_single_chapter(self, chapter_number: int) -> Dict[str, Any]:
        """检查单个章节（返回原始格式）"""
        result = super().check_single_chapter(chapter_number)

        # 转换格式以兼容原版
        violations = []
        for v in result.get("violations", []):
            violations.append(
                {
                    "type": v.get("type", ""),
                    "severity": v.get("severity", ""),
                    "message": v.get("message", ""),
                    "chapter": v.get("chapter", 0),
                    "details": v.get("details", ""),
                    "suggestion": v.get("suggestion", ""),
                }
            )

        result["violations"] = violations
        return result
