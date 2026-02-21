"""
Writer Agent - 重构版
集成 ConsistencyTracker，解决 Kimi 编辑指出的问题
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WriterAgent:
    """
    写作代理 - 重构版

    集成设定一致性追踪，解决：
    1. 战力体系崩坏 - 追踪敌人威胁，击败需有代价
    2. 能力体系混乱 - 追踪主角能力，上限5个
    3. 逻辑硬伤 - 世界观规则一致性
    4. 时间线混乱 - 事件追踪
    """

    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = project_dir
        self.chapters_dir = os.path.join(project_dir, "chapters")

        # 初始化设定追踪器
        sys_path = os.path.dirname(os.path.dirname(__file__))
        if sys_path not in os.sys.path:
            os.sys.path.insert(0, sys_path)
        from core.consistency_tracker import ConsistencyTracker

        self.tracker = ConsistencyTracker(project_dir)

        os.makedirs(self.chapters_dir, exist_ok=True)

    def write_session(self) -> Dict[str, Any]:
        """执行一次写作会话"""
        print("\n" + "=" * 60)
        print("[Writer] Writer Agent: Starting session")
        print("=" * 60)

        # 1. 加载进度
        print("\n[Step 1] Loading progress...")
        progress = self._load_progress()
        if not progress:
            return {"success": False, "error": "No progress file"}

        print(f"   Novel: {progress['title']}")
        print(
            f"   Progress: {progress['completed_chapters']}/{progress['total_chapters']}"
        )

        if progress["completed_chapters"] >= progress["total_chapters"]:
            return {"success": True, "status": "completed"}

        # 2. 获取下一章节
        print("\n[Step 2] Getting next chapter...")
        chapter_info = self._get_next_chapter(progress)
        if not chapter_info:
            return {"success": False, "error": "No chapter info"}

        chapter_number = chapter_info["chapter_number"]
        print(f"   Chapter {chapter_number}: {chapter_info['title']}")

        # 3. 更新状态
        self._update_chapter_status(chapter_number, "writing")

        # 4. 加载上下文 + 设定追踪
        print("\n[Step 4] Loading context...")
        context = self._load_writing_context(chapter_number)

        # 获取设定一致性约束
        tracker_context = self.tracker.get_context_for_chapter(chapter_number)
        if tracker_context:
            print("   [Tracker] Consistency constraints loaded")
            context["tracker_context"] = tracker_context

        # 5. 写作
        print(f"\n[Step 5] Writing chapter {chapter_number}...")
        chapter_content = self._write_chapter(chapter_number, context)

        # 6. 审查
        print("\n[Step 6] Reviewing...")
        review_result = self._self_review(chapter_number, chapter_content, context)

        if review_result["score"] < 7.0:
            print(f"   Score {review_result['score']:.1f}/10 - needs revision")
            chapter_content = self._revise_chapter(
                chapter_number, chapter_content, review_result, context
            )
        else:
            print(f"   Score {review_result['score']:.1f}/10 - passed")

        # 7. 保存
        chapter_file = os.path.join(
            self.chapters_dir, f"chapter-{chapter_number:03d}.md"
        )
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(chapter_content)
        print(f"\n[Step 7] Saved: chapter-{chapter_number:03d}.md")

        # 8. 更新进度和追踪器
        word_count = len(chapter_content)
        self._update_progress(
            chapter_number, "completed", word_count, review_result["score"]
        )

        # 更新设定追踪器
        self._update_tracker(chapter_number, chapter_content, context)

        # 9. Git commit
        self._git_commit(chapter_number, chapter_info["title"])

        print("\n" + "=" * 60)
        print(f"[Writer] Chapter {chapter_number} completed!")
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
        """加载写作上下文"""
        context = {}

        # 加载完整大纲
        outline_file = os.path.join(self.project_dir, "outline.md")
        if os.path.exists(outline_file):
            with open(outline_file, "r", encoding="utf-8") as f:
                context["outline"] = f.read()
            print(f"   Outline loaded ({len(context['outline'])} chars)")

        # 加载角色设定
        characters_file = os.path.join(self.project_dir, "characters.json")
        if os.path.exists(characters_file):
            with open(characters_file, "r", encoding="utf-8") as f:
                chars_data = json.load(f)
            if isinstance(chars_data, list):
                context["characters"] = {"characters": chars_data}
                char_count = len(chars_data)
            elif isinstance(chars_data, dict):
                context["characters"] = chars_data
                char_count = len(chars_data.get("characters", []))
            else:
                context["characters"] = {"characters": []}
                char_count = 0
            print(f"   Characters loaded ({char_count} chars)")

        # 加载章节列表
        chapter_list_file = os.path.join(self.project_dir, "chapter-list.json")
        if os.path.exists(chapter_list_file):
            with open(chapter_list_file, "r", encoding="utf-8") as f:
                chapters = json.load(f)
                for ch in chapters:
                    if ch["chapter_number"] == chapter_number:
                        context["current_chapter"] = ch
                        break

        # 加载前一章节完整内容
        if chapter_number > 1:
            prev_file = os.path.join(
                self.chapters_dir, f"chapter-{chapter_number - 1:03d}.md"
            )
            if os.path.exists(prev_file):
                with open(prev_file, "r", encoding="utf-8") as f:
                    context["previous_chapter"] = f.read()
                print(
                    f"   Previous chapter loaded ({len(context['previous_chapter'])} chars)"
                )

        # 加载世界观规则
        world_rules_file = os.path.join(self.project_dir, "world-rules.json")
        if os.path.exists(world_rules_file):
            with open(world_rules_file, "r", encoding="utf-8") as f:
                context["world_rules"] = json.load(f)
            print(f"   World rules loaded")

        return context

    def _write_chapter(self, chapter_number: int, context: Dict[str, Any]) -> str:
        """创作章节内容"""
        chapter_info = context.get("current_chapter", {})

        # 构建提示词
        prompt = self._build_chapter_prompt(chapter_number, context)

        try:
            content = self.llm.generate(
                prompt=prompt,
                temperature=0.85,
                system_prompt="你是专业的小说作家。严格按照设定写作，不添加新能力，保持战力体系一致。",
            )

            # 清理输出
            content = content.strip()
            if not content.startswith("#"):
                title = chapter_info.get("title", f"第{chapter_number}章")
                content = f"# {title}\n\n{content}"

            return content

        except Exception as e:
            print(f"   [Error] LLM call failed: {e}")
            return f"# 第{chapter_number}章\n\n[Error: {str(e)}]"

    def _build_chapter_prompt(
        self, chapter_number: int, context: Dict[str, Any]
    ) -> str:
        """构建章节写作提示词"""
        chapter_info = context.get("current_chapter", {})

        prompt = f"""请创作小说的第{chapter_number}章。

## 章节信息
- 标题: {chapter_info.get("title", f"第{chapter_number}章")}
- 概要: {chapter_info.get("summary", "")}
- 字数目标: {chapter_info.get("word_count_target", 3000)}字

## 关键情节点（必须包含）
"""
        for point in chapter_info.get("key_plot_points", []):
            prompt += f"- {point}\n"

        # 涉及角色
        involved = chapter_info.get("characters_involved", [])
        if involved:
            prompt += f"\n## 涉及角色\n{', '.join(involved)}\n"

        # 角色设定
        characters = context.get("characters", {}).get("characters", [])
        if characters:
            prompt += "\n## 角色设定\n"
            for char in characters:
                name = char.get("name", "")
                if not involved or name in involved:
                    prompt += f"\n### {name}\n"
                    if char.get("personality"):
                        prompt += f"性格: {char['personality'][:200]}\n"
                    if char.get("background"):
                        prompt += f"背景: {char['background'][:200]}\n"
                    if char.get("abilities"):
                        prompt += f"能力: {', '.join(char['abilities'][:5])}\n"

        # 前一章节
        if "previous_chapter" in context:
            prompt += f"""
## 前一章结尾
{context["previous_chapter"][-1000:]}
"""

        # 完整大纲
        if "outline" in context:
            prompt += f"""
## 小说大纲
{context["outline"][:3000]}
"""

        # 世界观规则
        if "world_rules" in context:
            wr = context["world_rules"]
            prompt += "\n## 世界观规则（必须遵守）\n"

            if isinstance(wr, dict):
                if "cultivation_system" in wr:
                    cs = wr["cultivation_system"]
                    prompt += "\n### 修炼体系\n"
                    if isinstance(cs, dict):
                        for key, value in cs.items():
                            if isinstance(value, list):
                                prompt += f"- {key}: {', '.join(str(v) for v in value[:10])}\n"
                            else:
                                prompt += f"- {key}: {value}\n"
                    else:
                        prompt += f"{cs}\n"

                if "power_rules" in wr:
                    pr = wr["power_rules"]
                    prompt += "\n### 战力规则（重要！）\n"
                    if isinstance(pr, dict):
                        for key, value in pr.items():
                            prompt += f"- {key}: {value}\n"
                    else:
                        prompt += f"{pr}\n"

                if "basic_info" in wr:
                    bi = wr["basic_info"]
                    prompt += "\n### 基础设定\n"
                    if isinstance(bi, dict):
                        for key, value in list(bi.items())[:5]:
                            prompt += f"- {key}: {value}\n"

                if "factions" in wr:
                    fa = wr["factions"]
                    prompt += "\n### 势力设定\n"
                    if isinstance(fa, dict):
                        for key, value in list(fa.items())[:5]:
                            prompt += f"- {key}: {value}\n"
            else:
                prompt += f"{wr}\n"

        # 设定追踪约束
        if "tracker_context" in context:
            prompt += f"""
## 设定一致性约束（重要！）
{context["tracker_context"]}
"""

        prompt += """
## 写作要求（强制遵守）

1. 严格遵循大纲和设定
2. 【禁止】突然添加新能力或设定 - 能力必须有明确来源
3. 【禁止】无代价越级战斗 - 同境界最多越1-2小层，跨大境界必须借助外力/付出代价
4. 【禁止】角色姓名变化 - 姓名必须全文一致
5. 时间线要一致 - 年份、年龄、事件顺序不能矛盾
6. 角色行为符合已建立的性格
7. 主角核心能力不超过5个
8. 章节衔接自然

直接输出章节内容。
"""

        return prompt

    def _self_review(
        self, chapter_number: int, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """自我审查"""
        chapter_info = context.get("current_chapter", {})

        score = 8.0
        issues = []

        # 字数检查
        word_count = len(content)
        target = chapter_info.get("word_count_target", 3000)
        if word_count < target * 0.5:
            score -= 2.0
            issues.append(f"字数严重不足: {word_count}/{target}")
        elif word_count < target * 0.8:
            score -= 1.0
            issues.append(f"字数不足: {word_count}/{target}")

        # 情节点检查
        missing_points = []
        for point in chapter_info.get("key_plot_points", []):
            keywords = [w for w in point.split() if len(w) > 2]
            if keywords and not any(kw in content for kw in keywords[:2]):
                missing_points.append(point)
                score -= 0.5

        # 角色检查
        for char in chapter_info.get("characters_involved", []):
            if char not in content:
                score -= 0.3
                issues.append(f"角色 {char} 未出现")

        # 设定一致性检查
        consistency = self.tracker.check_consistency(chapter_number, content)
        if not consistency.get("passed", True):
            for issue in consistency.get("issues", []):
                issues.append(issue.get("message", ""))
                score -= 1.0

        score = max(1.0, min(10.0, score))

        return {
            "score": score,
            "word_count": word_count,
            "missing_plot_points": missing_points,
            "issues": issues,
        }

    def _revise_chapter(
        self,
        chapter_number: int,
        content: str,
        review_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """修改章节"""
        print("   [Reviser] Calling LLM for revision...")

        issues = review_result.get("issues", [])

        prompt = f"""请修改以下章节，解决这些问题：

## 原始内容
{content}

## 需要解决的问题
"""
        for issue in issues:
            prompt += f"- {issue}\n"

        if review_result.get("missing_plot_points"):
            prompt += f"\n## 必须包含的情节点\n"
            for point in review_result["missing_plot_points"]:
                prompt += f"- {point}\n"

        prompt += """
## 修改要求
1. 保持原有故事主线
2. 解决所有问题
3. 确保设定一致性
4. 直接输出修改后的完整章节
"""

        try:
            revised = self.llm.generate(
                prompt=prompt,
                temperature=0.8,
                system_prompt="你是专业编辑，擅长修改小说，确保设定一致性。",
            )
            return revised.strip()
        except:
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
            for ch in progress.get("chapters", []):
                if ch.get("chapter_number") == chapter_number:
                    ch["status"] = status
                    ch["word_count"] = word_count
                    ch["quality_score"] = quality_score
                    ch["completed_at"] = datetime.now().isoformat()
                    break

            # 更新整体进度
            completed = sum(
                1
                for ch in progress.get("chapters", [])
                if ch.get("status") == "completed"
            )
            progress["completed_chapters"] = completed
            progress["total_word_count"] = sum(
                ch.get("word_count", 0) for ch in progress.get("chapters", [])
            )
            progress["last_updated"] = datetime.now().isoformat()

            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"   [Warning] Failed to update progress: {e}")

    def _update_tracker(
        self, chapter_number: int, content: str, context: Dict[str, Any]
    ):
        """更新设定追踪器"""
        # 追踪角色出现
        chapter_info = context.get("current_chapter", {})
        for char_name in chapter_info.get("characters_involved", []):
            self.tracker.track_character_appearance(char_name, chapter_number)

        # 追踪时间线事件
        self.tracker.track_timeline_event(
            chapter_number,
            "chapter_written",
            f"第{chapter_number}章: {chapter_info.get('title', '')} ({len(content)}字)",
        )

    def _git_commit(self, chapter_number: int, chapter_title: str):
        """Git 提交"""
        print(f"   [Git] Committed: Chapter {chapter_number} - {chapter_title}")
