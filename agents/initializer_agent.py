"""
Initializer Agent
基于 Anthropic 文章中的初始化代理模式
负责首次运行时设置完整的小说项目环境
"""

import json
import os
import re
from typing import Dict, List, Any, Optional


class InitializerAgent:
    """
    初始化代理

    职责：
    1. 分析用户需求，创建详细的小说大纲
    2. 设计完整的角色设定
    3. 规划章节结构，创建章节列表（feature list）
    4. 设定世界观和背景
    5. 创建写作风格指南
    6. 初始化进度文件
    7. 设置Git仓库
    """

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = project_dir

    def _extract_json(self, text: str) -> Any:
        """从文本中提取JSON，支持多种格式"""
        if not isinstance(text, str):
            return text

        text = text.strip()

        # 尝试直接解析
        try:
            return json.loads(text)
        except:
            pass

        # 尝试提取代码块中的JSON
        patterns = [
            r"```json\s*([\s\S]*?)\s*```",
            r"```\s*([\s\S]*?)\s*```",
            r"\[[\s\S]*\]",
            r"\{[\s\S]*\}",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue

        # 尝试找到第一个 [ 或 { 开始的内容
        for start_char, end_char in [("[", "]"), ("{", "}")]:
            start_idx = text.find(start_char)
            if start_idx != -1:
                # 找到匹配的结束位置
                depth = 0
                for i, char in enumerate(text[start_idx:], start_idx):
                    if char == start_char:
                        depth += 1
                    elif char == end_char:
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[start_idx : i + 1])
                            except:
                                break

        raise ValueError("无法从响应中提取有效的JSON")

    def initialize_project(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        初始化小说项目

        Args:
            config: 包含title, genre, target_chapters, description等

        Returns:
            初始化结果，包含创建的所有文件路径
        """
        print("🚀 Initializer Agent: 开始初始化小说项目...")
        print(f"   标题: {config.get('title')}")
        print(f"   类型: {config.get('genre')}")

        # 创建项目目录
        os.makedirs(self.project_dir, exist_ok=True)

        results = {"project_dir": self.project_dir, "files_created": []}

        # 1. 创建小说大纲
        print("\n📋 正在生成小说大纲...")
        outline = self._generate_outline(config)
        outline_path = os.path.join(self.project_dir, "outline.md")
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write(outline)
        results["files_created"].append("outline.md")
        print(f"   ✓ 大纲已保存: outline.md")

        # 2. 创建角色设定
        print("\n👥 正在设计角色...")
        characters = self._generate_characters(config, outline)
        characters_path = os.path.join(self.project_dir, "characters.json")
        with open(characters_path, "w", encoding="utf-8") as f:
            json.dump(characters, f, ensure_ascii=False, indent=2)
        results["files_created"].append("characters.json")
        print(f"   ✓ 角色设定已保存: characters.json ({len(characters)}个角色)")

        # 3. 创建章节列表（feature list）
        print("\n📑 正在规划章节结构...")
        chapters = self._generate_chapter_list(config, outline, characters)
        chapters_path = os.path.join(self.project_dir, "chapter-list.json")
        with open(chapters_path, "w", encoding="utf-8") as f:
            json.dump(chapters, f, ensure_ascii=False, indent=2)
        results["files_created"].append("chapter-list.json")
        print(f"   ✓ 章节列表已保存: chapter-list.json ({len(chapters)}个章节)")

        # 4. 创建写作风格指南
        print("\n✍️ 正在创建写作风格指南...")
        style_guide = self._generate_style_guide(config)
        style_path = os.path.join(self.project_dir, "style-guide.md")
        with open(style_path, "w", encoding="utf-8") as f:
            f.write(style_guide)
        results["files_created"].append("style-guide.md")
        print(f"   ✓ 风格指南已保存: style-guide.md")

        # 5. 初始化进度文件
        print("\n📊 正在初始化进度文件...")
        progress = self._initialize_progress(config, chapters)
        progress_path = os.path.join(self.project_dir, "novel-progress.txt")
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        results["files_created"].append("novel-progress.txt")
        print(f"   ✓ 进度文件已初始化: novel-progress.txt")

        # 6. 创建chapters目录
        chapters_dir = os.path.join(self.project_dir, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)

        # 7. 创建world-rules.json（关键：必须先于章节生成）
        print("\n🌍 正在生成世界观规则...")
        world_rules = self._generate_world_rules(config, outline, characters)
        world_rules_path = os.path.join(self.project_dir, "world-rules.json")
        with open(world_rules_path, "w", encoding="utf-8") as f:
            json.dump(world_rules, f, ensure_ascii=False, indent=2)
        results["files_created"].append("world-rules.json")
        print(f"   ✓ 世界观规则已保存: world-rules.json")

        # 8. 创建README
        readme = self._generate_readme(config, len(chapters))
        readme_path = os.path.join(self.project_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)
        results["files_created"].append("README.md")

        print("\n" + "=" * 60)
        print("✅ 项目初始化完成！")
        print("=" * 60)
        print(f"\n项目位置: {self.project_dir}")
        print(f"创建文件: {', '.join(results['files_created'])}")
        print("\n接下来可以使用 Writer Agent 开始写作。")

        return results

    def _generate_outline(self, config: Dict[str, Any]) -> str:
        """生成小说大纲"""
        prompt = f"""请为以下小说创建详细的大纲：

标题: {config.get("title")}
类型: {config.get("genre")}
目标章节数: {config.get("target_chapters", 20)}
每章字数: {config.get("words_per_chapter", 3000)}

用户描述:
{config.get("description", "请发挥创意")}

请创建包含以下内容的详细大纲：
1. 故事梗概（500字左右）
2. 主题和核心冲突
3. 世界观设定
4. 主要情节线
5. 章节规划（每个章节包含标题和简要概要）
6. 高潮和结局设计

使用Markdown格式输出。"""

        # 这里调用LLM生成大纲
        try:
            outline = self.llm.generate(
                prompt=prompt,
                temperature=0.8,
                system_prompt="你是一位专业的小说策划师，擅长构建引人入胜的故事大纲。",
            )
        except Exception as e:
            print(f"   ❌ 大纲生成失败: {e}")
            outline = f"# {config.get('title', '未命名')} 大纲\n\n## 故事梗概\n\n等待AI生成...\n\n## 章节规划\n\n1. 第一章\n2. 第二章\n"
        return outline

    def _load_character_designer_skill(self) -> str:
        """动态加载 character-designer 技能 (基于内容识别)"""
        from pathlib import Path

        # 搜索 skills 目录及其所有子目录
        skills_dir = Path("skills")
        if skills_dir.exists():
            for skill_file in skills_dir.rglob("*.md"):
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    # 检查元数据是否匹配 (name: character-designer)
                    if "name: character-designer" in content[:1000]:
                        print(f"   ✓ 找到 character-designer skill: {skill_file}")
                        # 移除 front matter
                        if content.startswith("---"):
                            parts = content.split("---", 2)
                            if len(parts) >= 3:
                                return parts[2].strip()
                        return content.strip()
                except Exception as e:
                    continue

        print("   ⚠ character-designer 技能未找到")
        return ""

    def _generate_characters(
        self, config: Dict[str, Any], outline: str
    ) -> List[Dict[str, Any]]:
        """生成角色设定 - 使用 character-designer 技能"""
        # 动态加载 character-designer 技能
        skill_content = self._load_character_designer_skill()

        # 构建用户上下文
        title = config.get("title", "未命名")
        genre = config.get("genre", "未知")

        if skill_content:
            # 使用技能构建 prompt
            prompt = f"""请根据以下小说背景和专家指令，设计符合要求的角色设定：

【书名】: {title}
【题材】: {genre}
【故事大纲】:
{outline}

请严格遵循以下专家指令和JSON格式要求进行输出：

{skill_content}

请直接以JSON数组格式输出，不要添加任何其他文字说明。"""
            system_msg = "你是商业网文人物架构师，擅长创造极致执念与金手指高度适配的角色。请严格按照JSON格式输出。"
        else:
            # 回退到新格式（商业网文格式）
            print("   ⚠ character-designer 技能未找到，使用新商业格式")
            prompt = f"""请根据以下小说背景，设计符合要求的角色设定：

【书名】: {title}
【题材】: {genre}
【故事大纲】:
{outline}

请创建5-8个角色，包括：
- 1-2个主角
- 1个反派或对立角色
- 3-5个配角

请严格按照以下JSON格式输出（禁止使用旧格式如 appearance, personality, background）：

```json
[
  {{
    "name": "角色姓名",
    "age": "年龄",
    "gender": "性别",
    "role": "主角/主要配角/核心反派",
    "commercial_tags": ["商业标签1", "商业标签2"],
    "core_obsession": "极度渴望的具体目标",
    "reverse_scale": "绝对不可触碰的底线/逆鳞",
    "golden_finger_synergy": "（仅主角）性格如何将金手指发挥到最大化？",
    "external_persona": "对外展现的伪装/人设",
    "internal_logic": "真实的内心算计与行为逻辑（反派需体现不降智的逻辑闭环）",
    "growth_path": "从【初始状态】到【终极状态】的权力/力量跃迁",
    "classic_dialogue": "最能代表其性格的一句极具网文张力的台词",
    "voice_tag": {{
      "tone": "慵懒/清冷/癫狂/温柔/铁血等",
      "speech_pattern": "短句/长句/反问/沉默/习惯性语气词",
      "signature_phrase": "标志性口头禅"
    }}
  }}
]
```

请直接以JSON数组格式输出，不要添加任何其他文字说明。"""
            system_msg = "你是商业网文人物架构师，擅长创造极致执念与金手指高度适配的角色。请严格按照新的JSON格式输出，不要使用旧格式。"

        # 调用LLM生成角色
        try:
            characters_str = self.llm.generate(
                prompt=prompt,
                temperature=0.8,
                system_prompt=system_msg,
            )
            # 使用改进的JSON提取
            characters = self._extract_json(characters_str)
            if not isinstance(characters, list):
                characters = (
                    [characters]
                    if isinstance(characters, dict)
                    else self._get_default_characters()
                )
        except Exception as e:
            print(f"   ❌ 角色生成失败: {e}")
            characters = self._get_default_characters()

        return characters

    def _generate_chapter_list(
        self, config: Dict[str, Any], outline: str, characters: List[Dict]
    ) -> List[Dict[str, Any]]:
        """生成章节列表（feature list）"""
        character_names = [ch["name"] for ch in characters]

        prompt = f"""基于以下信息，创建详细的章节列表：

标题: {config.get("title")}
类型: {config.get("genre")}
目标章节数: {config.get("target_chapters", 20)}
每章字数: {config.get("words_per_chapter", 3000)}

大纲摘要:
{outline[:1500]}...

可用角色: {", ".join(character_names)}

为每个章节创建以下信息：
{{
    "chapter_number": 章节编号,
    "title": "章节标题",
    "summary": "章节概要（100-150字）",
    "key_plot_points": ["关键情节点1", "关键情节点2", "关键情节点3"],
    "characters_involved": ["涉及的角色名"],
    "word_count_target": 字数目标,
    "status": "pending",
    "notes": ""
}}

确保：
1. 章节之间有逻辑连贯性
2. 每个章节都有明确的情节点
3. 角色出场分布合理
4. 情节逐步推进，有起伏

请以JSON数组格式输出。"""

        # 调用LLM生成章节列表
        try:
            chapters_str = self.llm.generate(
                prompt=prompt,
                temperature=0.8,
                system_prompt="你是一位专业的剧情策划师，擅长设计引人入胜的章节结构。请直接以JSON数组格式输出，不要添加任何其他文字。",
            )
            # 使用改进的JSON提取
            chapters = self._extract_json(chapters_str)
            if not isinstance(chapters, list):
                chapters = self._get_default_chapters(config.get("target_chapters", 20))
        except Exception as e:
            print(f"   ❌ 章节列表生成失败: {e}")
            chapters = self._get_default_chapters(config.get("target_chapters", 20))

        return chapters

    def _generate_style_guide(self, config: Dict[str, Any]) -> str:
        """生成写作风格指南"""
        genre = config.get("genre", "general")
        writing_style = config.get("writing_style", "descriptive")

        style_guides = {
            "科幻": """## 科幻小说写作指南

### 世界观构建
- 科学设定要自洽，设定规则后要严格遵守
- 技术描写要有一定科学依据，避免明显的科学错误
- 展现未来社会的文化、政治、生活方式

### 叙事特点
- 可以多用概念解释，但要自然融入叙事
- 探索科技对人类社会和个体的影响
- 平衡硬科幻的技术细节和故事性
""",
            "奇幻": """## 奇幻小说写作指南

### 世界观构建
- 魔法系统要有规则和限制
- 创造独特的种族和文化
- 历史背景要丰富且有深度

### 叙事特点
- 注重氛围营造，创造神秘感
- 可以包含史诗般的旅程和冒险
- 探索命运、预言等主题
""",
            "悬疑": """## 悬疑小说写作指南

### 叙事结构
- 设置悬念，逐步揭示真相
- 线索要公平地呈现给读者
- 结局要有合理的解释

### 写作技巧
- 控制信息释放的节奏
- 营造紧张和不安的氛围
- 误导和反转要巧妙
""",
            "general": """## 通用小说写作指南

### 叙事基础
- 展示而非讲述（Show, don't tell）
- 保持视角一致
- 对话要自然，符合角色性格

### 场景描写
- 调动五感，创造沉浸感
- 细节要服务于故事和氛围
- 节奏要有变化，张弛有度
""",
        }

        guide = f"""# {config.get("title")} - 写作风格指南

## 基本信息
- **类型**: {genre}
- **写作风格**: {writing_style}
- **基调**: {config.get("tone", "neutral")}

{style_guides.get(genre, style_guides["general"])}

## 通用写作原则

### 1. 角色塑造
- 每个角色都要有独特的声音
- 通过行动和对话展现性格，而非直接描述
- 角色要有缺点和成长空间

### 2. 对话写作
- 对话要推动情节或揭示角色
- 避免过度解释性的对话
- 使用对话标签要适度

### 3. 场景描写
- 开场要吸引人
- 场景转换要流畅
- 结尾要留有余味或悬念

### 4. 节奏控制
- 动作场景要快速、简洁
- 情感场景要深入、细腻
- 过渡场景要简洁明了

### 5. 一致性检查
- [ ] 角色行为是否符合设定？
- [ ] 时间线是否连贯？
- [ ] 场景描述是否前后一致？
- [ ] 角色知识范围是否合理？

## 质量控制标准
- 每章字数控制在目标范围内（±20%）
- 所有关键情节点必须展开
- 避免明显的逻辑漏洞
- 语言流畅，无明显语病
"""

        return guide

    def _initialize_progress(
        self, config: Dict[str, Any], chapters: List[Dict]
    ) -> Dict[str, Any]:
        """初始化进度文件"""
        from datetime import datetime

        progress = {
            "title": config.get("title"),
            "genre": config.get("genre"),
            "total_chapters": len(chapters),
            "completed_chapters": 0,
            "current_chapter": 1,
            "total_word_count": 0,
            "start_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "initialized",
            "chapters": [
                {
                    "chapter_number": ch["chapter_number"],
                    "title": ch["title"],
                    "status": "pending",
                    "word_count": 0,
                    "quality_score": 0.0,
                    "created_at": datetime.now().isoformat(),
                    "completed_at": "",
                    "notes": "",
                }
                for ch in chapters
            ],
        }

        return progress

    def _generate_world_rules(self, config: Dict[str, Any], outline: str, characters: List[Dict]) -> Dict[str, Any]:
        """生成世界观规则文件（关键修复：确保生成完整的world-rules.json）"""
        genre = config.get("genre", "xianxia")

        # 默认修仙世界观
        world_rules = {
            "world_type": genre,
            "has_cultivation": True,
            "cultivation_system": {
                "境界列表": ["无剑者", "炼气期", "剑气境", "剑心境", "剑意境"],
                "境界层级": {
                    "无剑者": 0,
                    "炼气期": 1,
                    "剑气境": 2,
                    "剑心境": 3,
                    "剑意境": 4
                }
            },
            "factions": {},
            "realm_hierarchy": {
                "无剑者": 0,
                "炼气期": 1,
                "剑气境": 2,
                "剑心境": 3,
                "剑意境": 4
            },
            "cross_realm_combat": "forbidden",
            "max_cross_realm": 0
        }

        # 从大纲中提取宗门信息
        faction_keywords = ["宗", "门", "派", "阁", "宫", "府", "殿", "院"]
        found_factions = set()
        for line in outline.split("\n"):
            for keyword in faction_keywords:
                if keyword in line:
                    # 提取2-4个字的宗门名
                    import re
                    matches = re.findall(rf"[\u4e00-\u9fa5]{{2,4}}{keyword}", line)
                    found_factions.update(matches)

        # 添加找到的宗门
        for faction in list(found_factions)[:10]:  # 最多10个
            world_rules["factions"][faction] = {"type": "sect"}

        # 如果没有找到宗门，添加默认值
        if not world_rules["factions"]:
            if genre == "xianxia":
                world_rules["factions"] = {"天剑宗": {"type": "sect"}}
            elif genre == "fantasy":
                world_rules["factions"] = {"王国A": {"type": "kingdom"}, "王国B": {"type": "kingdom"}}

        # 从角色中提取主角名
        protagonist_name = None
        for char in characters:
            if char.get("role") == "protagonist":
                protagonist_name = char.get("name")
                break

        if protagonist_name:
            world_rules["protagonist_name"] = protagonist_name
            world_rules["locked_names"] = {"主角": protagonist_name}

        return world_rules

    def _generate_readme(self, config: Dict[str, Any], total_chapters: int) -> str:
        """生成项目README"""
        return f"""# {config.get("title")}

## 项目信息
- **类型**: {config.get("genre")}
- **目标章节**: {total_chapters}
- **每章字数**: {config.get("words_per_chapter", 3000)}

## 项目结构
```
{self.project_dir}/
├── README.md              # 本文件
├── outline.md             # 小说大纲
├── characters.json        # 角色设定
├── chapter-list.json      # 章节列表
├── style-guide.md         # 写作风格指南
├── novel-progress.txt     # 进度跟踪
└── chapters/              # 章节内容
    ├── chapter-001.md
    ├── chapter-002.md
    └── ...
```

## 写作进度
查看 `novel-progress.txt` 了解当前进度。

## 使用说明
1. 使用 Initializer Agent 初始化项目（已完成）
2. 使用 Writer Agent 逐章写作
3. 使用 Reviewer Agent 审查质量
4. 完成后合并所有章节

## 创作日期
{__import__("datetime").datetime.now().strftime("%Y-%m-%d")}
"""

    def _mock_llm_call(self, prompt: str, task_type: str) -> Any:
        """
        模拟LLM调用
        实际实现中应该调用真实的LLM API
        """
        # 从prompt中提取目标章节数
        target_chapters = 20  # 默认值
        for line in prompt.split("\n"):
            if "目标章节数" in line or "target_chapters" in line.lower():
                try:
                    # 尝试从行中提取数字
                    import re

                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        target_chapters = int(numbers[0])
                        break
                except:
                    pass

        # 这里返回模拟数据
        if task_type == "outline":
            return self._get_default_outline(target_chapters)
        elif task_type == "characters":
            return self._get_default_characters()
        elif task_type == "chapters":
            return self._get_default_chapters(target_chapters)
        return ""

    def _get_default_outline(self, count: int = 10) -> str:
        """默认大纲模板"""
        # 根据章节数生成不同的大纲结构
        if count <= 5:
            structure = """## 章节规划
1. 开端：引入主角和冲突
2. 发展：挑战与成长
3. 高潮：最终对决
4. 结局：问题解决，新的开始"""
        elif count <= 10:
            structure = """## 章节规划
1-2. 开端：引入主角和冲突
3-6. 发展：挑战与成长
7-8. 高潮：最终对决
9-10. 结局：问题解决，新的开始"""
        else:
            structure = f"""## 章节规划
1-3. 开端：引入主角和冲突
4-{count - 4}. 发展：挑战与成长
{count - 3}-{count - 2}. 高潮：最终对决
{count - 1}-{count}. 结局：问题解决，新的开始"""

        return f"""# 小说大纲

## 故事梗概
这是一个关于成长与冒险的故事...

## 主题
探索、勇气、自我发现

## 世界观
现代都市背景，带有神秘元素...

{structure}
"""

    def _get_default_characters(self) -> List[Dict[str, Any]]:
        """默认角色设定"""
        return [
            {
                "name": "主角",
                "role": "protagonist",
                "age": 25,
                "appearance": "普通但有个性的外表",
                "personality": "勇敢、好奇、有些固执",
                "background": "平凡的成长背景",
                "motivation": "寻找真相，保护重要的人",
                "character_arc": "从普通人成长为英雄",
                "relationships": {},
                "distinctive_features": ["特殊的眼神", "独特的习惯"],
                "speech_patterns": "直接、真诚",
            }
        ]

    def _get_default_chapters(self, count: int) -> List[Dict[str, Any]]:
        """默认章节列表"""
        chapters = []
        for i in range(1, count + 1):
            chapters.append(
                {
                    "chapter_number": i,
                    "title": f"第{i}章",
                    "summary": f"这是第{i}章的概要...",
                    "key_plot_points": ["情节点1", "情节点2"],
                    "characters_involved": ["主角"],
                    "word_count_target": 3000,
                    "status": "pending",
                    "notes": "",
                }
            )
        return chapters
