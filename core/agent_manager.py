"""
智能体管理器 - 重构版
真正调用 15 个专业 Skills 和 Agents
集成设定一致性追踪
支持层级架构和触发词冲突检测
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    """Skill 元数据"""

    name: str
    level: str = "expert"  # coordinator, architect, expert, auditor
    triggers: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    parent: Optional[str] = None
    subordinates: List[str] = field(default_factory=list)
    description: str = ""


class AgentManager:
    """
    智能体管理器 - 真正调用所有 Skills 和 Agents

    层级架构：
    - Level 1 (Coordinator): worldbuilder-coordinator, plot-architect-coordinator, novel-coordinator
    - Level 2 (Architect): outline-architect, volume-architect, chapter-architect, character-designer, rhythm-designer
    - Level 3 (Expert): scene-writer, cultivation-designer, currency-expert, geopolitics-expert, society-expert
    - Level 4 (Auditor): opening-diagnostician, senior-editor, editor
    """

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = project_dir

        novel_generator_root = Path(__file__).parent.parent
        self.agents_dir = novel_generator_root / "agents"
        self.skills_dir = novel_generator_root / ".opencode" / "skills"
        Path(self.project_dir).mkdir(parents=True, exist_ok=True)

        # 导入设定追踪器
        try:
            from .consistency_tracker import ConsistencyTracker
        except ImportError:
            from consistency_tracker import ConsistencyTracker

        self.tracker = ConsistencyTracker(project_dir)

        self.active_agents = []
        self.agent_outputs = {}  # 记录每个 agent 的输出
        self.skills_metadata: Dict[str, SkillMetadata] = {}  # Skill 元数据缓存
        self._trigger_index: Dict[str, str] = {}  # 触发词 -> skill 映射

        # 初始化时加载所有 skills 元数据
        self._load_all_skills_metadata()

    def _load_all_skills_metadata(self):
        """加载所有 skills 的元数据"""
        if not self.skills_dir.exists():
            return

        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    metadata = self._parse_skill_metadata(skill_file)
                    if metadata:
                        self.skills_metadata[skill_dir.name] = metadata
                        # 建立触发词索引
                        for trigger in metadata.triggers:
                            self._trigger_index[trigger.lower()] = skill_dir.name

        # 验证触发词冲突
        self._validate_triggers()

    def _parse_skill_metadata(self, skill_file: Path) -> Optional[SkillMetadata]:
        """解析 SKILL.md 的 YAML frontmatter"""
        try:
            content = skill_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            front_matter = yaml.safe_load(parts[1])
            if not front_matter:
                return None

            metadata_dict = front_matter.get("metadata", {})
            return SkillMetadata(
                name=front_matter.get("name", skill_file.parent.name),
                level=metadata_dict.get("level", "expert"),
                triggers=metadata_dict.get("triggers", []),
                category=metadata_dict.get("category", ""),
                subcategory=metadata_dict.get("subcategory", ""),
                parent=metadata_dict.get("parent"),
                subordinates=metadata_dict.get("subordinates", []),
                description=front_matter.get("description", ""),
            )
        except Exception as e:
            print(f"[Warning] 解析 {skill_file} 元数据失败: {e}")
            return None

    def _validate_triggers(self):
        """
        验证触发词是否唯一
        如果有冲突，打印警告但不会抛出异常
        """
        trigger_map: Dict[str, List[str]] = {}
        for skill_name, metadata in self.skills_metadata.items():
            for trigger in metadata.triggers:
                trigger_lower = trigger.lower()
                if trigger_lower not in trigger_map:
                    trigger_map[trigger_lower] = []
                trigger_map[trigger_lower].append(skill_name)

        conflicts = {t: skills for t, skills in trigger_map.items() if len(skills) > 1}
        if conflicts:
            print("\n[Warning] 触发词冲突检测:")
            for trigger, skills in conflicts.items():
                print(f"  - '{trigger}' 被 {skills} 同时使用")
            print("建议修改触发词以确保唯一性\n")

    def get_skill_by_trigger(self, trigger: str) -> Optional[str]:
        """根据触发词查找对应的 skill"""
        return self._trigger_index.get(trigger.lower())

    def get_skills_by_level(self, level: str) -> List[str]:
        """获取指定层级的所有 skills"""
        return [
            name for name, meta in self.skills_metadata.items() if meta.level == level
        ]

    def get_skill_hierarchy(self) -> Dict[str, Any]:
        """获取 skill 层级结构"""
        hierarchy = {"coordinator": [], "architect": [], "expert": [], "auditor": []}
        for name, meta in self.skills_metadata.items():
            level = meta.level
            if level in hierarchy:
                hierarchy[level].append(
                    {
                        "name": name,
                        "triggers": meta.triggers,
                        "subordinates": meta.subordinates,
                        "parent": meta.parent,
                    }
                )
        return hierarchy

    def load_agent_prompt(self, agent_name: str) -> str:
        """加载智能体提示词 - 从 agents/*.md（已弃用，保留兼容）"""
        prompt_file = self.agents_dir / f"{agent_name}.md"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def load_skill_prompt(self, skill_name: str) -> str:
        """加载技能提示词 - 从 .opencode/skills/*/SKILL.md"""
        skill_file = self.skills_dir / skill_name / "SKILL.md"
        if skill_file.exists():
            with open(skill_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def get_available_agents(self) -> List[Dict[str, str]]:
        """获取所有可用的智能体 - 优先从 skills 读取（单源维护）"""
        agents = []

        # 优先从 skills/ 目录读取
        if self.skills_dir.exists():
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        metadata = self.skills_metadata.get(skill_dir.name)
                        agents.append(
                            {
                                "name": skill_dir.name,
                                "file": "SKILL.md",
                                "description": metadata.description if metadata else "",
                                "type": "skill",
                                "level": metadata.level if metadata else "expert",
                                "triggers": metadata.triggers if metadata else [],
                            }
                        )

        return agents

    def _extract_description(self, content: str) -> str:
        """从内容中提取描述"""
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter = parts[1]
                for line in front_matter.split("\n"):
                    if line.startswith("description:"):
                        return line.split(":", 1)[1].strip()
        return ""

    def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行指定智能体 - 真正调用 LLM

        Args:
            agent_name: 智能体名称
            context: 上下文信息，包含 config, previous_results 等

        Returns:
            执行结果
        """
        print(f"  [Agent] {agent_name} 开始执行...")

        # 加载提示词
        prompt = self.load_agent_prompt(agent_name)
        skill_prompt = self.load_skill_prompt(agent_name)

        # 合并提示词（skill 优先）
        base_prompt = skill_prompt if skill_prompt else prompt

        if not base_prompt:
            print(f"  [Warning] 未找到 {agent_name} 的提示词")
            base_prompt = f"你是专业的{agent_name}，请根据上下文完成任务。"

        # 构建完整提示词
        full_prompt = self._build_full_prompt(agent_name, base_prompt, context)

        # 获取设定追踪上下文
        if "current_chapter" in context:
            tracker_context = self.tracker.get_context_for_chapter(
                context["current_chapter"].get("chapter_number", 1)
            )
            if tracker_context:
                full_prompt += f"\n\n【设定一致性约束】\n{tracker_context}"

        try:
            # 调用真实 LLM
            result = self.llm.generate(
                prompt=full_prompt,
                temperature=0.8,
                system_prompt=f"你是专业的{agent_name}。请严格按照设定工作，确保内容一致性。",
            )

            # 保存输出
            self.agent_outputs[agent_name] = result
            self._save_agent_result(agent_name, result, context)

            print(f"  [Agent] {agent_name} 执行完成")

            return {
                "agent": agent_name,
                "success": True,
                "result": result,
                "context": context,
            }
        except Exception as e:
            error_msg = str(e)
            print(f"  [Error] {agent_name} 执行失败: {error_msg}")
            return {
                "agent": agent_name,
                "success": False,
                "error": error_msg,
                "result": "",
            }

    def _build_full_prompt(
        self, agent_name: str, base_prompt: str, context: Dict
    ) -> str:
        """构建完整的智能体提示词"""
        full_prompt = base_prompt + "\n\n"

        # 添加项目配置
        if "config" in context:
            config = context["config"]
            full_prompt += "## 项目配置\n"
            full_prompt += f"- 标题: {config.get('title', '未命名')}\n"
            full_prompt += f"- 类型: {config.get('genre', '通用')}\n"
            full_prompt += f"- 目标章节: {config.get('target_chapters', 10)}\n"
            full_prompt += f"- 每章字数: {config.get('words_per_chapter', 3000)}\n"
            if config.get("description"):
                full_prompt += f"- 故事简介: {config['description']}\n"

        # 添加前序步骤结果
        if "previous_results" in context and context["previous_results"]:
            full_prompt += "\n## 前序步骤结果\n"
            for prev in context["previous_results"][-5:]:  # 最近5个
                agent = prev.get("step", prev.get("agent", "未知"))
                result = prev.get("result", {})
                if isinstance(result, dict):
                    result = result.get("result", str(result))
                full_prompt += f"\n### {agent}\n"
                full_prompt += f"{str(result)[:1000]}\n"  # 限制长度

        # 添加当前章节信息
        if "current_chapter" in context:
            ch = context["current_chapter"]
            full_prompt += "\n## 当前章节\n"
            full_prompt += f"- 章节号: {ch.get('chapter_number', 1)}\n"
            full_prompt += f"- 标题: {ch.get('title', '')}\n"
            full_prompt += f"- 概要: {ch.get('summary', '')}\n"
            if ch.get("key_plot_points"):
                full_prompt += f"- 关键情节: {', '.join(ch['key_plot_points'])}\n"

        # 添加特定智能体的约束
        constraints = self._get_agent_constraints(agent_name)
        if constraints:
            full_prompt += f"\n## 执行约束\n{constraints}\n"

        return full_prompt

    def _get_agent_constraints(self, agent_name: str) -> str:
        """获取特定智能体的约束条件"""
        constraints = {
            "WorldBuilder": """
- 科技水平必须一致，不能随意跳跃
- 政治体系要有内在逻辑
- 社会结构要合理，极端组织不能有正常政治地位
""",
            "CharacterDesigner": """
- 角色能力要有明确边界
- 主角能力不能超过5个核心技能
- 每个角色的动机必须清晰
- 配角也要有独立的人格和目标
""",
            "PlotArchitect": """
- 敌人威胁等级设定后不能随意降低
- 高威胁敌人必须有明显弱点或代价才能击败
- 主角不能是"唯一钥匙"，要给配角发挥作用的空间
- 冲突解决要有代价
""",
            "SceneWriter": """
- 时间线要一致
- 角色能力使用必须在已设定范围内
- 不能突然引入新能力
- 战斗场景要有代价
""",
            "CultivationDesigner": """
- 能力体系要统一
- 不能随意添加新能力类型
- 能力获取必须有明确来源和代价
- 主角不能无限变强
""",
        }
        return constraints.get(agent_name, "")

    def _save_agent_result(self, agent_name: str, result: str, context: Dict):
        """保存智能体执行结果"""
        output_dir = Path(self.project_dir) / "agent_outputs"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{agent_name.lower()}_output.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {agent_name} 输出\n\n")
            f.write(result)

    def run_full_workflow(self, novel_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行完整的智能体工作流

        解决 Kimi 编辑指出的问题：
        1. 战力体系 - PlotArchitect + CultivationDesigner 协作
        2. 能力体系 - CharacterDesigner + CultivationDesigner + 设定追踪
        3. 逻辑硬伤 - WorldBuilder + 专家智能体检查
        4. 时间线 - 追踪器自动管理
        5. 人物工具化 - CharacterDesigner + Editor 确保配角有独立线
        """

        print("\n" + "=" * 60)
        print("[AgentManager] 启动完整智能体工作流")
        print("=" * 60)

        workflow = [
            # Phase 1: 世界构建
            {
                "phase": "world_building",
                "agent": "WorldBuilder",
                "desc": "构建世界观（科技、政治、社会）",
            },
            {
                "phase": "world_building",
                "agent": "GeopoliticsExpert",
                "desc": "设计地缘政治体系",
            },
            {
                "phase": "world_building",
                "agent": "SocietyExpert",
                "desc": "设计社会结构",
            },
            # Phase 2: 能力体系
            {
                "phase": "power_system",
                "agent": "CultivationDesigner",
                "desc": "设计能力/修炼体系（统一、有边界）",
            },
            # Phase 3: 角色设计
            {
                "phase": "character",
                "agent": "CharacterDesigner",
                "desc": "设计角色（主角能力<5，配角独立线）",
            },
            # Phase 4: 剧情架构
            {
                "phase": "plot",
                "agent": "PlotArchitect",
                "desc": "架构剧情（敌人威胁体系、弱点、代价）",
            },
            # Phase 5: 大纲设计
            {"phase": "outline", "agent": "OutlineArchitect", "desc": "设计章节大纲"},
            {
                "phase": "outline",
                "agent": "VolumeArchitect",
                "desc": "分卷规划（长篇）",
            },
            {"phase": "outline", "agent": "ChapterArchitect", "desc": "详细章纲"},
        ]

        results = []
        all_success = True

        for step in workflow:
            print(f"\n[Phase: {step['phase']}] {step['agent']}")
            print(f"  任务: {step['desc']}")

            result = self.execute_agent(
                step["agent"], {"config": novel_config, "previous_results": results}
            )

            results.append(
                {"phase": step["phase"], "agent": step["agent"], "result": result}
            )

            if not result["success"]:
                print(f"  [Error] {step['agent']} 失败")
                all_success = False

        # 生成项目文件
        if all_success:
            self._generate_project_files(novel_config, results)

        return {
            "success": all_success,
            "results": results,
            "tracker_report": self.tracker.generate_report(),
        }

    def _generate_project_files(self, config: Dict[str, Any], results: List[Dict]):
        """根据智能体输出生成项目文件"""
        print("\n[AgentManager] 生成项目文件...")

        os.makedirs(self.project_dir, exist_ok=True)

        # 提取各部分内容
        outline_content = ""
        characters_content = {}
        chapter_list = []
        world_rules = {}

        for result in results:
            agent_name = result["agent"]
            agent_result = result["result"].get("result", "")

            if "Outline" in agent_name or "outline" in agent_name.lower():
                outline_content = agent_result
            elif "Character" in agent_name:
                characters_content = self._parse_characters(agent_result)
            elif "Chapter" in agent_name:
                chapter_list = self._parse_chapters(agent_result, config)
            elif "World" in agent_name:
                world_rules = self._parse_world_rules(agent_result)

        # 保存文件
        # outline.md
        if outline_content:
            with open(
                Path(self.project_dir) / "outline.md", "w", encoding="utf-8"
            ) as f:
                f.write(outline_content)
            print("  [OK] outline.md")

        # characters.json
        with open(
            Path(self.project_dir) / "characters.json", "w", encoding="utf-8"
        ) as f:
            json.dump(
                characters_content if characters_content else {},
                f,
                ensure_ascii=False,
                indent=2,
            )
        print("  [OK] characters.json")

        # chapter-list.json
        if not chapter_list:
            chapter_list = self._create_default_chapters(config)
        with open(
            Path(self.project_dir) / "chapter-list.json", "w", encoding="utf-8"
        ) as f:
            json.dump(chapter_list, f, ensure_ascii=False, indent=2)
        print("  [OK] chapter-list.json")

        # world-rules.json (新增)
        with open(
            Path(self.project_dir) / "world-rules.json", "w", encoding="utf-8"
        ) as f:
            json.dump(world_rules, f, ensure_ascii=False, indent=2)
        print("  [OK] world-rules.json")

        # 更新设定追踪器
        for char_name, char_data in characters_content.items():
            if isinstance(char_data, dict) and char_data.get("role") == "protagonist":
                for ability in char_data.get("abilities", []):
                    self.tracker.track_ability_gain(char_name, ability, 0, "初始设定")

    def _parse_characters(self, content: str) -> Dict:
        """解析角色信息"""
        # 复用 InitializerAgent 的解析逻辑
        try:
            import re

            # 尝试提取 JSON
            json_match = re.search(r"\[[\s\S]*\]", content)
            if json_match:
                return {"characters": json.loads(json_match.group())}
        except:
            pass
        return {"characters": []}

    def _parse_chapters(self, content: str, config: Dict) -> List[Dict]:
        """解析章节列表"""
        # 复用 InitializerAgent 的解析逻辑
        try:
            import re

            json_match = re.search(r"\[[\s\S]*\]", content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return []

    def _parse_world_rules(self, content: str) -> Dict:
        """解析世界观规则 - 增强版，正确提取修炼体系"""
        import re

        rules = {
            "basic_info": {},
            "cultivation_system": {},
            "power_rules": {},
            "geography": [],
            "factions": {},
        }

        lines = content.split("\n")
        current_section = None
        section_content = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("# "):
                if current_section and section_content:
                    self._process_section(rules, current_section, section_content)
                current_section = stripped[2:].lower()
                section_content = []
            elif stripped.startswith("## "):
                current_section = stripped[3:].lower()
                section_content = []
            elif current_section:
                section_content.append(stripped)

            if ":" in stripped and not stripped.startswith("#"):
                parts = stripped.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().replace("**", "")
                    value = parts[1].strip()

                    if "境界" in key or "筑基" in key or "炼气" in key:
                        rules["cultivation_system"][key] = value
                    elif "越级" in key or "战力" in key or "威胁" in key:
                        rules["power_rules"][key] = value
                    elif "世界" in key or "大陆" in key or "区域" in key:
                        rules["basic_info"][key] = value
                    elif "宗门" in key or "皇朝" in key or "势力" in key:
                        rules["factions"][key] = value
                    else:
                        rules["basic_info"][key] = value

        if current_section and section_content:
            self._process_section(rules, current_section, section_content)

        rules["power_rules"]["越级挑战约束"] = (
            "同境界内可越1-2小层，跨大境界必须借助外力或付出代价"
        )
        rules["power_rules"]["能力上限警告"] = "主角核心能力不超过5个"
        rules["power_rules"]["高威胁定义"] = "威胁等级>=6的敌人必须有代价才能击败"

        return rules

    def _process_section(self, rules: Dict, section: str, content: List[str]):
        """处理特定章节内容"""
        section_text = "\n".join(content)

        if "修炼" in section or "境界" in section or "cultivation" in section:
            realms = self._extract_realms(section_text)
            if realms:
                rules["cultivation_system"]["境界列表"] = realms

        elif "战力" in section or "power" in section:
            power_rules = self._extract_power_rules(section_text)
            rules["power_rules"].update(power_rules)

        elif "地理" in section or "区域" in section or "geograph" in section:
            areas = [
                l.strip("- ").strip() for l in content if l.strip().startswith("-")
            ]
            if areas:
                rules["geography"] = areas

    def _extract_realms(self, text: str) -> List[str]:
        """提取修炼境界列表"""
        import re

        realm_patterns = [
            r"炼气[一二三四五六七八九十]+[层期前后巅峰]*",
            r"筑基[一二三四五六七八九十]*[层期前后巅峰]*",
            r"金丹[一二三四五六七八九十]*[层期前后巅峰]*",
            r"元婴[一二三四五六七八九十]*[层期前后巅峰]*",
            r"化神|返虚|合道|渡劫|大乘",
        ]

        realms = []
        for pattern in realm_patterns:
            matches = re.findall(pattern, text)
            realms.extend(matches)

        return list(set(realms))[:15]

    def _extract_power_rules(self, text: str) -> Dict:
        """提取战力规则"""
        rules = {}
        import re

        if "越级" in text:
            rules["允许越级"] = "是，但需代价"

        threat_match = re.search(r"威胁[等级]*[：:]*\s*(\d+)", text)
        if threat_match:
            rules["威胁等级参考"] = threat_match.group(1)

        return rules

    def _create_default_chapters(self, config: Dict[str, Any]) -> List[Dict]:
        """创建默认章节列表"""
        total = config.get("target_chapters", 10)
        return [
            {
                "chapter_number": i + 1,
                "title": f"第{i + 1}章",
                "summary": "",
                "key_plot_points": [],
                "characters_involved": [],
                "word_count_target": config.get("words_per_chapter", 3000),
                "status": "pending",
            }
            for i in range(total)
        ]
