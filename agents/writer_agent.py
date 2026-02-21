"""
Writer Agent
基于 Anthropic 文章中的 Coding Agent 模式
负责逐章进行增量式写作
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


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
        print("✍️ [Agent] Writer Agent: 开始写作会话")
        print("=" * 60)
        logger.info("=" * 60)
        logger.info("[WriterAgent] 开始新的写作会话")

        # 1. 阅读进度文件
        print("\n📖 [Step 1] 正在读取进度文件...")
        print(f"   [Tool] _load_progress: 读取 novel-progress.txt")
        progress = self._load_progress()
        if not progress:
            print("❌ 错误: 未找到进度文件，请先运行 Initializer Agent")
            logger.error("[WriterAgent] 未找到进度文件")
            return {"success": False, "error": "No progress file"}

        print(f"   小说: {progress['title']}")
        print(
            f"   进度: {progress['completed_chapters']}/{progress['total_chapters']} 章"
        )
        logger.info(
            f"[WriterAgent] 小说: {progress['title']}, 进度: {progress['completed_chapters']}/{progress['total_chapters']}"
        )

        # 检查是否已完成
        if progress["completed_chapters"] >= progress["total_chapters"]:
            print("\n✅ 小说已完成！")
            logger.info("[WriterAgent] 小说已完成")
            return {"success": True, "status": "completed"}

        # 2. 获取下一个待完成的章节
        print("\n📋 [Step 2] 正在获取章节信息...")
        print(f"   [Tool] _get_next_chapter: 读取 chapter-list.json")
        chapter_info = self._get_next_chapter(progress)
        if not chapter_info:
            print("❌ 错误: 无法获取章节信息")
            logger.error("[WriterAgent] 无法获取章节信息")
            return {"success": False, "error": "No chapter info"}

        chapter_number = chapter_info["chapter_number"]
        print(f"   当前章节: 第{chapter_number}章 - {chapter_info['title']}")
        logger.info(
            f"[WriterAgent] 目标章节: 第{chapter_number}章 - {chapter_info['title']}"
        )

        # 3. 更新章节状态为写作中
        print(f"\n📝 [Step 3] 更新章节状态为 writing")
        print(f"   [Tool] _update_chapter_status: 更新 chapter-list.json")
        self._update_chapter_status(chapter_number, "writing")

        # 4. 加载写作所需的上下文
        print("\n📚 [Step 4] 正在加载写作上下文...")
        context = self._load_writing_context(chapter_number)

        # 5. 创作章节
        print(f"\n✍️ [Step 5] 正在创作第{chapter_number}章...")
        print(f"   [Agent] Chapter Writer: 调用LLM生成章节内容")
        chapter_content = self._write_chapter(chapter_number, context)

        # 6. 自我审查
        print("\n🔍 正在进行自我审查...")
        print(f"   [Agent] Self-Reviewer: 检查章节质量和大纲一致性")
        review_result = self._self_review(chapter_number, chapter_content, context)

        if review_result["score"] < 7.0:
            print(f"   ⚠️ 质量评分 {review_result['score']:.1f}/10，需要修改")
            print(f"   [Agent] Reviser: 正在修改章节...")
            chapter_content = self._revise_chapter(
                chapter_number, chapter_content, review_result, context
            )
        else:
            print(f"   ✓ 质量评分 {review_result['score']:.1f}/10，通过")

        # 7. 保存章节
        print(f"\n💾 [Step 7] 保存章节...")
        print(f"   [Tool] 写入文件: chapter-{chapter_number:03d}.md")
        chapter_file = os.path.join(
            self.chapters_dir, f"chapter-{chapter_number:03d}.md"
        )
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(chapter_content)
        print(f"   ✓ 章节已保存: chapter-{chapter_number:03d}.md")
        logger.info(f"[WriterAgent] 章节已保存: {chapter_file}")

        # 8. 更新进度
        print(f"\n📊 [Step 8] 更新进度文件...")
        print(f"   [Tool] _update_progress: 更新 novel-progress.txt")
        word_count = len(chapter_content)
        self._update_progress(
            chapter_number, "completed", word_count, review_result["score"]
        )
        print(f"   字数: {word_count}")
        print(f"   质量评分: {review_result['score']:.1f}/10")

        # 9. Git提交（模拟）
        print(f"\n📤 [Step 9] Git提交...")
        self._git_commit(chapter_number, chapter_info["title"])

        print("\n" + "=" * 60)
        print(f"✅ [Agent] Writer Agent: 第{chapter_number}章完成！")
        print("=" * 60)
        logger.info(f"[WriterAgent] 写作会话完成，第{chapter_number}章已成功")

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
        logger.info(f"[WriterAgent] 正在加载第{chapter_number}章的写作上下文...")
        print(f"   [Tool] _load_writing_context: 加载完整大纲、角色设定、前章内容")

        context = {}

        # 加载完整大纲
        outline_file = os.path.join(self.project_dir, "outline.md")
        if os.path.exists(outline_file):
            with open(outline_file, "r", encoding="utf-8") as f:
                outline_content = f.read()
                context["outline"] = outline_content
                logger.info(
                    f"[WriterAgent] 已加载完整大纲，共 {len(outline_content)} 字符"
                )
                print(f"   ✓ 完整大纲已加载 ({len(outline_content)} 字符)")
        else:
            logger.warning(f"[WriterAgent] 大纲文件不存在: {outline_file}")
            print(f"   ⚠️ 大纲文件不存在")

        # 加载角色完整设定
        characters_file = os.path.join(self.project_dir, "characters.json")
        if os.path.exists(characters_file):
            with open(characters_file, "r", encoding="utf-8") as f:
                characters_data = json.load(f)
                context["characters"] = characters_data
                # 构建角色详细信息字符串
                char_details = []
                for char in characters_data:
                    detail = f"【{char['name']}】\n"
                    detail += f"  性格: {char.get('personality', '未设定')}\n"
                    detail += f"  背景: {char.get('background', '未设定')}\n"
                    detail += f"  目标: {char.get('goals', '未设定')}\n"
                    detail += f"  特点: {char.get('traits', '未设定')}\n"
                    char_details.append(detail)
                context["characters_detail"] = "\n".join(char_details)
                logger.info(
                    f"[WriterAgent] 已加载 {len(characters_data)} 个角色的完整设定"
                )
                print(f"   ✓ 角色完整设定已加载 ({len(characters_data)} 个角色)")
        else:
            logger.warning(f"[WriterAgent] 角色文件不存在: {characters_file}")

        # 加载章节列表
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")
        if os.path.exists(chapter_list_file):
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)
                context["chapter_list"] = chapters
                for ch in chapters:
                    if ch["chapter_number"] == chapter_number:
                        context["current_chapter"] = ch
                        break

        # 加载风格指南
        style_file = os.path.join(self.project_dir, "style-guide.md")
        if os.path.exists(style_file):
            with open(style_file, "r", encoding="utf-8") as f:
                context["style_guide"] = f.read()
                print(f"   ✓ 风格指南已加载")

        # 加载前一章节的完整内容（不再只加载结尾）
        if chapter_number > 1:
            prev_chapter_file = os.path.join(
                self.chapters_dir, f"chapter-{chapter_number - 1:03d}.md"
            )
            if os.path.exists(prev_chapter_file):
                with open(prev_chapter_file, "r", encoding="utf-8") as f:
                    full_content = f.read()
                    context["previous_chapter_full"] = full_content
                    # 同时保留结尾用于快速参考
                    context["previous_chapter_ending"] = (
                        full_content[-800:] if len(full_content) > 800 else full_content
                    )
                    logger.info(
                        f"[WriterAgent] 已加载前一章完整内容，共 {len(full_content)} 字符"
                    )
                    print(f"   ✓ 前一章完整内容已加载 ({len(full_content)} 字符)")
            else:
                logger.warning(f"[WriterAgent] 前一章文件不存在: {prev_chapter_file}")
                print(f"   ⚠️ 前一章文件不存在")

        logger.info(f"[WriterAgent] 写作上下文加载完成")
        return context

    def _write_chapter(self, chapter_number: int, context: Dict[str, Any]) -> str:
        """创作章节内容"""
        logger.info(f"[WriterAgent] 开始创作第{chapter_number}章...")
        print(f"   [Tool] _write_chapter: 调用LLM生成章节内容")

        chapter_info = context.get("current_chapter", {})

        # 构建写作提示
        prompt = f"""请创作小说的第{chapter_number}章。

# ⚠️ 重要：必须严格遵循大纲

## 完整大纲（请仔细阅读并严格遵循）
{context.get("outline", "大纲未加载")}

## 当前章节信息
标题: {chapter_info.get("title", f"第{chapter_number}章")}
概要: {chapter_info.get("summary", "")}
字数目标: {chapter_info.get("word_count_target", 3000)}字

## 关键情节点（必须全部包含在章节中）
"""
        for i, point in enumerate(chapter_info.get("key_plot_points", []), 1):
            prompt += f"{i}. {point}\n"

        prompt += f"""
## 本章涉及的角色
{", ".join(chapter_info.get("characters_involved", []))}

## 角色完整设定
{context.get("characters_detail", "角色设定未加载")}

## 风格指南
{context.get("style_guide", "无特殊风格要求")}
"""

        # 添加前一章的完整内容
        if "previous_chapter_full" in context:
            prompt += f"""
## 前一章节完整内容（用于保持情节连贯性，请确保本章与此衔接）
{context["previous_chapter_full"]}
"""

        prompt += f"""
# 写作要求（必须严格遵守）

1. **大纲遵循**：
   - 必须严格按照大纲中的情节线发展
   - 确保本章内容是大纲整体故事的一部分
   - 不要偏离大纲设定的方向

2. **情节点覆盖**：
   - 所有列出的关键情节点必须在章节中出现
   - 每个情节点都要有足够的展开和描写
   - 不要遗漏任何关键事件

3. **角色一致性**：
   - 角色行为必须符合其性格设定
   - 对话风格要符合角色特点
   - 角色之间的关系要符合设定

4. **与上一章衔接**：
   - 情节要从上一章的结尾自然过渡
   - 保持时间线的连贯性
   - 角色状态要与上一章结尾一致

5. **格式要求**：
   - 以章节标题开始（使用#标记）
   - 达到字数目标（{chapter_info.get("word_count_target", 3000)}字）
   - 在结尾处为下一章留下适当的过渡

请直接输出章节内容，不要添加任何额外说明或注释。"""

        logger.info(f"[WriterAgent] 已构建写作提示词，准备调用LLM")
        print(f"   [Tool] LLM.generate: 正在生成章节内容...")

        # 调用LLM生成内容
        try:
            content = self.llm.generate(
                prompt=prompt,
                temperature=0.85,
                system_prompt="你是一位专业的小说作家，擅长创作情节紧凑、人物立体、文字生动的小说。你的作品注重细节描写，对话自然，能够吸引读者持续阅读。请严格遵循提供的大纲和设定进行创作。",
            )
            logger.info(f"[WriterAgent] LLM生成完成，内容长度: {len(content)} 字符")
            print(f"   ✓ LLM生成完成 ({len(content)} 字符)")
        except Exception as e:
            logger.error(f"[WriterAgent] LLM调用失败: {e}")
            print(f"   ❌ LLM调用失败: {e}")
            content = f"# 第{chapter_number}章\n\n[错误: AI生成失败 - {str(e)}]"

        return content

    def _self_review(
        self, chapter_number: int, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """自我审查 - 检查章节内容是否与大纲一致"""
        logger.info(f"[WriterAgent] 开始自我审查第{chapter_number}章...")
        print(f"   [Tool] _self_review: 检查大纲一致性、情节点覆盖、角色一致性")

        chapter_info = context.get("current_chapter", {})
        outline = context.get("outline", "")

        # 基础检查
        word_count = len(content)
        target = chapter_info.get("word_count_target", 3000)

        # 计算基础分数
        score = 8.0  # 基础分
        issues = []
        missing_points = []

        # 1. 字数检查
        if word_count < target * 0.8:
            score -= 1.5
            issues.append(f"字数不足: {word_count}/{target} (低于80%)")
        elif word_count > target * 1.3:
            score -= 0.5
            issues.append(f"字数超出: {word_count}/{target} (超过130%)")
        else:
            print(f"   ✓ 字数检查通过: {word_count}/{target}")

        # 2. 检查关键情节点覆盖
        key_points = chapter_info.get("key_plot_points", [])
        for point in key_points:
            # 提取关键词进行匹配
            keywords = [kw for kw in point.split() if len(kw) > 2][:3]
            found = False
            for kw in keywords:
                if kw in content:
                    found = True
                    break
            if not found:
                missing_points.append(point)
                score -= 0.5

        if missing_points:
            issues.append(f"缺少关键情节点: {', '.join(missing_points[:3])}")
            print(f"   ⚠️ 缺少 {len(missing_points)} 个关键情节点")
        else:
            print(f"   ✓ 所有关键情节点已覆盖")

        # 3. 检查角色出现
        characters_involved = chapter_info.get("characters_involved", [])
        missing_chars = []
        for char in characters_involved:
            if char not in content:
                missing_chars.append(char)
                score -= 0.3

        if missing_chars:
            issues.append(f"缺少角色: {', '.join(missing_chars)}")
            print(f"   ⚠️ 缺少角色: {', '.join(missing_chars)}")
        else:
            print(f"   ✓ 所有涉及角色已出现")

        # 4. 使用LLM进行大纲一致性检查
        print(f"   [Tool] LLM.generate: 正在进行语义一致性检查...")
        consistency_score = self._check_outline_consistency(
            content, outline, chapter_info
        )
        if consistency_score < 7.0:
            score -= (7.0 - consistency_score) * 0.3
            issues.append(f"大纲一致性评分较低: {consistency_score:.1f}/10")
            print(f"   ⚠️ 大纲一致性评分: {consistency_score:.1f}/10")
        else:
            print(f"   ✓ 大纲一致性评分: {consistency_score:.1f}/10")

        # 5. 检查与前一章节的衔接
        if "previous_chapter_ending" in context:
            prev_ending = context["previous_chapter_ending"]
            # 简单检查：查找前一章节末尾提到的元素
            transition_score = self._check_chapter_transition(content, prev_ending)
            if transition_score < 0.5:
                score -= 0.5
                issues.append("与前一章节衔接不够自然")
                print(f"   ⚠️ 章节衔接评分较低")
            else:
                print(f"   ✓ 章节衔接良好")

        # 确保分数在合理范围
        score = max(1.0, min(10.0, score))

        logger.info(f"[WriterAgent] 自我审查完成，评分: {score:.1f}/10")

        return {
            "score": score,
            "word_count": word_count,
            "missing_plot_points": missing_points,
            "issues": issues,
            "consistency_score": consistency_score,
        }

    def _check_outline_consistency(
        self, content: str, outline: str, chapter_info: Dict[str, Any]
    ) -> float:
        """使用LLM检查章节内容与大纲的一致性"""
        logger.info(f"[WriterAgent] 正在进行大纲一致性语义检查...")

        prompt = f"""请评估以下章节内容与大纲的一致性。

## 大纲内容
{outline[:2000]}

## 当前章节概要
{chapter_info.get("summary", "")}

## 关键情节点
{json.dumps(chapter_info.get("key_plot_points", []), ensure_ascii=False)}

## 章节内容
{content[:3000]}

请从以下方面评估一致性（每项1-10分）：
1. 情节走向是否与大纲一致
2. 关键事件是否都有体现
3. 角色行为是否符合设定
4. 整体故事节奏是否合理

请只返回一个JSON格式的评分：
{{"score": 分数, "reason": "简短原因"}}
"""

        try:
            result = self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                system_prompt="你是一位专业的小说编辑，擅长评估故事的一致性和连贯性。请只返回JSON格式的评分结果。",
            )
            # 尝试解析JSON
            import re

            json_match = re.search(r"\{[^}]+\}", result)
            if json_match:
                score_data = json.loads(json_match.group())
                return float(score_data.get("score", 7.0))
        except Exception as e:
            logger.warning(f"[WriterAgent] 一致性检查LLM调用失败: {e}")
            print(f"   ⚠️ 一致性检查失败，使用默认分数")

        return 7.0  # 默认分数

    def _check_chapter_transition(self, content: str, prev_ending: str) -> float:
        """检查章节间的衔接"""
        # 提取前一章节末尾的关键词
        import re

        # 简单的关键词提取
        prev_words = set(re.findall(r"[\u4e00-\u9fff]{2,}", prev_ending[-300:]))
        content_start = set(re.findall(r"[\u4e00-\u9fff]{2,}", content[:500]))

        # 计算重叠度
        if not prev_words:
            return 0.5

        overlap = len(prev_words & content_start) / min(len(prev_words), 5)
        return min(1.0, overlap)

    def _revise_chapter(
        self,
        chapter_number: int,
        content: str,
        review_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """修改章节 - 确保内容与大纲一致"""
        logger.info(f"[WriterAgent] 开始修改第{chapter_number}章...")
        print(f"   [Tool] _revise_chapter: 根据审查结果修改章节")
        print(f"   问题列表: {review_result.get('issues', [])}")

        chapter_info = context.get("current_chapter", {})
        outline = context.get("outline", "")

        # 构建修改提示
        prompt = f"""请修改以下章节内容，解决存在的问题。

## 原始章节内容
{content}

## 存在的问题
{json.dumps(review_result.get("issues", []), ensure_ascii=False, indent=2)}

## 缺少的关键情节点
{json.dumps(review_result.get("missing_plot_points", []), ensure_ascii=False, indent=2)}

## 大纲（必须严格遵循）
{outline[:2000]}

## 章节信息
标题: {chapter_info.get("title", "")}
概要: {chapter_info.get("summary", "")}

## 修改要求
1. 必须包含所有缺少的关键情节点
2. 确保情节走向与大纲一致
3. 保持与前后章节的连贯性
4. 保持原有的写作风格
5. 不要删减已有的好内容，只添加缺失的部分

请输出修改后的完整章节内容："""

        print(f"   [Tool] LLM.generate: 正在重新生成章节...")
        try:
            revised_content = self.llm.generate(
                prompt=prompt,
                temperature=0.7,
                system_prompt="你是一位专业的小说编辑，擅长修改和完善小说章节。请确保修改后的内容严格遵循大纲。",
            )
            logger.info(
                f"[WriterAgent] 章节修改完成，新内容长度: {len(revised_content)}"
            )
            print(f"   ✓ 章节修改完成 ({len(revised_content)} 字符)")
            return revised_content
        except Exception as e:
            logger.error(f"[WriterAgent] 修改失败: {e}")
            print(f"   ❌ 修改失败，返回原内容: {e}")
            # 如果修改失败，简单地在末尾添加缺失的情节点
            if review_result.get("missing_plot_points"):
                content += "\n\n"
                for point in review_result["missing_plot_points"]:
                    content += f"【补充情节】{point}\n"
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
