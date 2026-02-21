"""
Writer Agent
基于 Anthropic 文章中的 Coding Agent 模式
负责逐章进行增量式写作
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class WriterAgent:
    """
    写作代理

    工作流程（基于 Anthropic 文章）：
    1. 阅读进度文件，了解已完成内容
    2. 查看章节列表，选择下一个待完成的章节
    3. 阅读相关角色设定和世界背景
    4. 创作该章节内容
    5. 进行自我审查
    6. 更新进度文件
    7. Git提交

    原则：
    - 每次只专注于一个章节
    - 保持角色一致性
    - 遵循已建立的世界观
    - 推进情节发展
    """

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = project_dir
        self.chapters_dir = os.path.join(project_dir, "chapters")

        # 确保章节目录存在
        os.makedirs(self.chapters_dir, exist_ok=True)

    def write_session(self) -> Dict[str, Any]:
        """
        执行一次写作会话

        Returns:
            会话结果，包含写作的章节信息
        """
        print("\n" + "=" * 60)
        print("✍️ Writer Agent: 开始写作会话")
        print("=" * 60)

        # 1. 阅读进度文件
        print("\n📖 正在读取进度文件...")
        progress = self._load_progress()
        if not progress:
            print("❌ 错误: 未找到进度文件，请先运行 Initializer Agent")
            return {"success": False, "error": "No progress file"}

        print(f"   小说: {progress['title']}")
        print(
            f"   进度: {progress['completed_chapters']}/{progress['total_chapters']} 章"
        )

        # 检查是否已完成
        if progress["completed_chapters"] >= progress["total_chapters"]:
            print("\n✅ 小说已完成！")
            return {"success": True, "status": "completed"}

        # 2. 获取下一个待完成的章节
        print("\n📋 正在获取章节信息...")
        chapter_info = self._get_next_chapter(progress)
        if not chapter_info:
            print("❌ 错误: 无法获取章节信息")
            return {"success": False, "error": "No chapter info"}

        chapter_number = chapter_info["chapter_number"]
        print(f"   当前章节: 第{chapter_number}章 - {chapter_info['title']}")

        # 3. 更新章节状态为写作中
        self._update_chapter_status(chapter_number, "writing")

        # 4. 加载写作所需的上下文
        print("\n📚 正在加载写作上下文...")
        context = self._load_writing_context(chapter_number)
        print(f"   ✓ 大纲已加载")
        print(f"   ✓ 角色设定已加载 ({len(context.get('characters', []))}个角色)")
        print(f"   ✓ 章节指导已加载")

        # 5. 创作章节
        print(f"\n📝 正在创作第{chapter_number}章...")
        chapter_content = self._write_chapter(chapter_number, context)

        # 6. 自我审查
        print("\n🔍 正在进行自我审查...")
        review_result = self._self_review(chapter_number, chapter_content, context)

        if review_result["score"] < 7.0:
            print(f"   ⚠️ 质量评分 {review_result['score']:.1f}/10，需要修改")
            chapter_content = self._revise_chapter(
                chapter_number, chapter_content, review_result
            )
        else:
            print(f"   ✓ 质量评分 {review_result['score']:.1f}/10，通过")

        # 7. 保存章节
        chapter_file = os.path.join(
            self.chapters_dir, f"chapter-{chapter_number:03d}.md"
        )
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(chapter_content)
        print(f"\n💾 章节已保存: chapter-{chapter_number:03d}.md")

        # 8. 更新进度
        word_count = len(chapter_content)
        self._update_progress(
            chapter_number, "completed", word_count, review_result["score"]
        )
        print(f"   字数: {word_count}")
        print(f"   质量评分: {review_result['score']:.1f}/10")

        # 9. Git提交（模拟）
        self._git_commit(chapter_number, chapter_info["title"])

        print("\n" + "=" * 60)
        print(f"✅ 第{chapter_number}章完成！")
        print("=" * 60)

        return {
            "success": True,
            "chapter_number": chapter_number,
            "title": chapter_info["title"],
            "word_count": word_count,
            "quality_score": review_result["score"],
        }

    def _load_progress(self) -> Optional[Dict[str, Any]]:
        """加载进度文件"""
        progress_file = os.path.join(self.project_dir, "novel-progress.txt")
        if not os.path.exists(progress_file):
            return None

        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

    def _get_next_chapter(self, progress: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取下一个待完成的章节"""
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")

        if not os.path.exists(chapter_list_file):
            return None

        try:
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)

            # 找到第一个pending状态的章节
            for ch in chapters:
                if ch["status"] == "pending":
                    return ch

            return None
        except:
            return None

    def _update_chapter_status(self, chapter_number: int, status: str):
        """更新章节状态"""
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")

        try:
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)

            for ch in chapters:
                if ch["chapter_number"] == chapter_number:
                    ch["status"] = status
                    break

            with open(chapter_list_file, "w", encoding="utf-8") as f:
                json.dump(chapters, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _load_writing_context(self, chapter_number: int) -> Dict[str, Any]:
        """加载写作所需的上下文"""
        context = {}

        # 加载大纲
        outline_file = os.path.join(self.project_dir, "outline.md")
        if os.path.exists(outline_file):
            with open(outline_file, "r", encoding="utf-8") as f:
                context["outline"] = f.read()

        # 加载角色设定
        characters_file = os.path.join(self.project_dir, "characters.json")
        if os.path.exists(characters_file):
            with open(characters_file, "r", encoding="utf-8") as f:
                context["characters"] = json.load(f)

        # 加载章节列表
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")
        if os.path.exists(chapter_list_file):
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)
                for ch in chapters:
                    if ch["chapter_number"] == chapter_number:
                        context["current_chapter"] = ch
                        break

        # 加载风格指南
        style_file = os.path.join(self.project_dir, "style-guide.md")
        if os.path.exists(style_file):
            with open(style_file, "r", encoding="utf-8") as f:
                context["style_guide"] = f.read()

        # 加载前一章节内容（用于连贯性）
        if chapter_number > 1:
            prev_chapter_file = os.path.join(
                self.chapters_dir, f"chapter-{chapter_number - 1:03d}.md"
            )
            if os.path.exists(prev_chapter_file):
                with open(prev_chapter_file, "r", encoding="utf-8") as f:
                    # 只加载最后500字作为上下文
                    content = f.read()
                    context["previous_chapter_ending"] = (
                        content[-500:] if len(content) > 500 else content
                    )

        return context

    def _write_chapter(self, chapter_number: int, context: Dict[str, Any]) -> str:
        """创作章节内容"""
        chapter_info = context.get("current_chapter", {})

        # 构建写作提示
        prompt = f"""请创作小说的第{chapter_number}章。

## 章节信息
标题: {chapter_info.get("title", f"第{chapter_number}章")}
概要: {chapter_info.get("summary", "")}
字数目标: {chapter_info.get("word_count_target", 3000)}字

## 关键情节点（必须包含）
"""
        for point in chapter_info.get("key_plot_points", []):
            prompt += f"- {point}\n"

        prompt += f"""
## 涉及角色
{", ".join(chapter_info.get("characters_involved", []))}

## 角色设定摘要
"""
        for char in context.get("characters", []):
            if char["name"] in chapter_info.get("characters_involved", []):
                prompt += f"- {char['name']}: {char['personality'][:100]}...\n"

        if "previous_chapter_ending" in context:
            prompt += f"""
## 前一章节结尾（用于保持连贯性）
{context["previous_chapter_ending"]}
"""

        prompt += """
## 写作要求
1. 以章节标题开始（使用#标记）
2. 确保所有关键情节点都得到展开
3. 保持角色行为和对话符合其性格设定
4. 注重场景描写，创造沉浸感
5. 对话要自然，推动情节发展
6. 在结尾处制造适当的过渡
7. 达到字数目标

请直接输出章节内容，不要添加额外说明。"""

        # 调用LLM生成内容
        try:
            content = self.llm.generate(
                prompt=prompt,
                temperature=0.85,
                system_prompt="你是一位专业的小说作家，擅长创作情节紧凑、人物立体、文字生动的小说。你的作品注重细节描写，对话自然，能够吸引读者持续阅读。",
            )
        except Exception as e:
            print(f"   ❌ LLM调用失败: {e}")
            content = f"# 第{chapter_number}章\n\n[错误: AI生成失败 - {str(e)}]"

        return content

    def _self_review(
        self, chapter_number: int, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """自我审查"""
        chapter_info = context.get("current_chapter", {})

        # 基础检查
        word_count = len(content)
        target = chapter_info.get("word_count_target", 3000)

        # 计算基础分数
        score = 8.0  # 基础分

        # 字数检查
        if word_count < target * 0.8:
            score -= 1.5
        elif word_count > target * 1.3:
            score -= 0.5

        # 检查关键情节点
        missing_points = []
        for point in chapter_info.get("key_plot_points", []):
            keywords = point.split()[:2]
            if not any(kw in content for kw in keywords if len(kw) > 2):
                missing_points.append(point)
                score -= 0.5

        # 检查角色出现
        characters_involved = chapter_info.get("characters_involved", [])
        for char in characters_involved:
            if char not in content:
                score -= 0.3

        # 确保分数在合理范围
        score = max(1.0, min(10.0, score))

        return {
            "score": score,
            "word_count": word_count,
            "missing_plot_points": missing_points,
            "issues": [],
        }

    def _revise_chapter(
        self, chapter_number: int, content: str, review_result: Dict[str, Any]
    ) -> str:
        """修改章节"""
        print(f"   正在修改章节...")

        # 简单的修改逻辑：添加缺失的情节点
        if review_result.get("missing_plot_points"):
            content += "\n\n"
            for point in review_result["missing_plot_points"]:
                content += f"【补充】{point}\n"

        return content

    def _update_progress(
        self, chapter_number: int, status: str, word_count: int, quality_score: float
    ):
        """更新进度文件"""
        progress_file = os.path.join(self.project_dir, "novel-progress.txt")

        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress = json.load(f)

            # 更新章节信息
            for ch in progress["chapters"]:
                if ch["chapter_number"] == chapter_number:
                    ch["status"] = status
                    ch["word_count"] = word_count
                    ch["quality_score"] = quality_score
                    ch["completed_at"] = datetime.now().isoformat()
                    break

            # 更新整体进度
            completed = sum(
                1 for ch in progress["chapters"] if ch["status"] == "completed"
            )
            progress["completed_chapters"] = completed
            progress["total_word_count"] = sum(
                ch.get("word_count", 0) for ch in progress["chapters"]
            )
            progress["last_updated"] = datetime.now().isoformat()

            # 找到下一个待完成的章节
            for ch in progress["chapters"]:
                if ch["status"] == "pending":
                    progress["current_chapter"] = ch["chapter_number"]
                    break

            # 更新整体状态
            if completed >= progress["total_chapters"]:
                progress["status"] = "completed"
            elif completed > 0:
                progress["status"] = "writing"

            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"   警告: 更新进度文件失败 - {e}")

    def _git_commit(self, chapter_number: int, chapter_title: str):
        """模拟Git提交"""
        # 实际实现中应该调用git命令
        print(f"   [Git] 已提交: 完成第{chapter_number}章 - {chapter_title}")

    def _mock_llm_write(self, prompt: str, chapter_info: Dict) -> str:
        """
        模拟LLM写作
        实际实现中应该调用真实的LLM API
        """
        chapter_num = chapter_info.get("chapter_number", 1)
        title = chapter_info.get("title", f"第{chapter_num}章")

        # 根据章节号生成不同的模拟内容
        scenarios = [
            "清晨的阳光洒进房间",
            "午后的街道热闹非凡",
            "黄昏时分的天空绚烂",
            "深夜的寂静中只有虫鸣",
            "雨后的空气格外清新",
        ]

        challenges = [
            "遇到了一个神秘的陌生人",
            "发现了一封改变命运的信件",
            "意外获得了某种特殊能力",
            "被迫做出艰难的选择",
            "卷入了一场意想不到的事件",
        ]

        resolutions = [
            "最终找到了问题的答案",
            "学会了接受自己的不完美",
            "意识到真正的力量来自内心",
            "决定踏上新的旅程",
            "明白了什么是真正重要的",
        ]

        # 根据章节号循环选择不同的场景
        scenario_idx = (chapter_num - 1) % len(scenarios)
        challenge_idx = (chapter_num - 1) % len(challenges)
        resolution_idx = (chapter_num - 1) % len(resolutions)

        content = f"""# {title}

这是{title}的内容。本章将推进故事情节，展现角色的成长与变化。

## 场景一：开端

{scenarios[scenario_idx]}，主角开始了新的一天。但今天的氛围有些不同，空气中似乎弥漫着某种紧张的气息。

他整理了一下思绪，回想着前几章发生的事情。那些经历已经让他改变了许多。

## 场景二：冲突

就在这个时刻，{challenges[challenge_idx]}。这个意外打乱了他原本的计划，迫使他必须立即做出反应。

"这不可能..."他喃喃自语，但眼前的现实不容否认。

周围的空气仿佛凝固了，时间在这一刻变得格外缓慢。他深吸一口气，强迫自己冷静下来。

## 场景三：转折

经过一番思考和努力，{resolutions[resolution_idx]}。虽然过程艰难，但这段经历让他获得了宝贵的经验。

他望向远方，知道这只是旅程的一部分。前方还有更多的挑战等待着他，但他已经准备好了。

夕阳西下，新的一章结束了，但故事才刚刚开始。

---

*（这是第{chapter_num}章的模拟内容，实际应由LLM根据提示生成独特的章节内容）*
"""

        return content
