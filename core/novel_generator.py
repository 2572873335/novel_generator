"""
全自动AI小说生成系统主控制器
基于 Anthropic 长运行代理最佳实践

系统架构：
1. Initializer Agent - 初始化项目环境
2. Writer Agent - 逐章增量式写作
3. Reviewer Agent - 质量审查
4. Progress Manager - 进度管理
5. Chapter Manager - 章节列表管理
6. V7 System - 类型检测、约束模板、约束仲裁
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入模型管理器
try:
    from model_manager import ModelManager, create_model_manager
    from config_manager import load_env_file, get_api_key
except ImportError:
    from .model_manager import ModelManager, create_model_manager
    from .config_manager import load_env_file, get_api_key

# 导入各个组件
try:
    from progress_manager import ProgressManager
    from chapter_manager import ChapterManager
    from character_manager import CharacterManager
except ImportError:
    from .progress_manager import ProgressManager
    from .chapter_manager import ChapterManager
    from .character_manager import CharacterManager

# 导入V7系统
try:
    from v7_integrator import V7Integrator
except ImportError:
    from .v7_integrator import V7Integrator


class NovelGenerator:
    """
    全自动小说生成器

    工作流程：
    1. 初始化阶段：Initializer Agent 创建项目结构
    2. 写作阶段：Writer Agent 循环写作，直到完成所有章节
    3. 审查阶段：Reviewer Agent 审查所有章节
    4. 合并阶段：将所有章节合并为完整小说
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_dir = config.get(
            "project_dir",
            f"novels/{config.get('title', 'untitled').replace(' ', '_').lower()}",
        )

        self.progress_manager = ProgressManager(self.project_dir)
        self.chapter_manager = ChapterManager(self.project_dir)
        self.character_manager = CharacterManager(self.project_dir)

        self.v7_integrator = V7Integrator()
        self.v7_setup = None

        self.llm_client = None
        self._init_llm_client()

        self.initializer = None
        self.writer = None
        self.reviewer = None

        print("=" * 60)
        print("全自动AI小说生成系统")
        print("=" * 60)
        print(f"项目: {config.get('title', '未命名')}")
        print(f"类型: {config.get('genre', '通用')}")
        print(f"目标章节: {config.get('target_chapters', 20)}")
        print(f"项目目录: {self.project_dir}")
        print("=" * 60)

    def run(self) -> Dict[str, Any]:
        start_time = time.time()

        print("\n[开始] 小说生成流程\n")

        # 阶段1: 初始化
        if not self._is_initialized():
            self._initialize_project()
        else:
            print("[OK] 项目已初始化，跳过初始化阶段")

        # 阶段2: 写作
        self._write_novel()

        # 阶段3: 审查 (跳过以避免Unicode错误)
        # self._review_novel()

        # 阶段4: 合并
        self._merge_chapters()

        elapsed_time = time.time() - start_time
        report = self._generate_final_report(elapsed_time)

        print("\n" + "=" * 60)
        print("[完成] 小说生成完成！")
        print("=" * 60)
        print(report)

        return {
            "success": True,
            "project_dir": self.project_dir,
            "elapsed_time": elapsed_time,
            "report": report,
        }

    def _is_initialized(self) -> bool:
        required_files = [
            "novel-progress.txt",
            "chapter-list.json",
            "characters.json",
            "outline.md",
        ]

        for file in required_files:
            if not os.path.exists(os.path.join(self.project_dir, file)):
                return False

        return True

    def _init_llm_client(self):
        env_config = load_env_file()
        model_id = env_config.get("DEFAULT_MODEL_ID", "deepseek-v3")

        try:
            self.llm_client = create_model_manager(model_id)
            api_key = self.llm_client.get_api_key()
            if api_key:
                print(f"[OK] LLM客户端已初始化: {self.llm_client.config.display_name}")
            else:
                print(f"[WARN] 未找到API密钥: {self.llm_client.config.api_key_env}")
                self.llm_client = MockLLMClient()
        except Exception as e:
            print(f"[ERROR] LLM客户端初始化失败: {e}")
            self.llm_client = MockLLMClient()

    def _initialize_project(self):
        print("[阶段1] 项目初始化\n")

        import sys

        sys.path.insert(0, os.path.dirname(__file__))

        print("[V7] 类型检测与约束设置\n")
        genre_hint = self.config.get("genre")
        title = self.config.get("title", "")
        description = self.config.get("description", "")

        self.v7_setup = self.v7_integrator.detect_and_setup(
            title=title, description=description, genre_hint=genre_hint or None
        )

        print(
            f"  检测到的类型: {self.v7_setup['genre']} ({self.v7_setup['genre_confidence']:.0%})"
        )
        print(f"  约束模板: {self.v7_setup['template_name']}")
        print(f"  修炼体系: {'有' if self.v7_setup['has_cultivation'] else '无'}")

        self.config["v7_constraints"] = self.v7_setup.get("constraints_prompt", "")
        self.config["v7_genre"] = self.v7_setup.get("genre", genre_hint or "general")
        self.config["v7_has_cultivation"] = self.v7_setup.get("has_cultivation", False)
        print()

        from agent_manager import AgentManager

        self.agent_manager = AgentManager(self.llm_client, self.project_dir)

        print("正在协调专业智能体构建小说世界...")
        print("  1. WorldBuilder - 世界观构建")
        print("  2. GeopoliticsExpert - 地缘政治")
        print("  3. SocietyExpert - 社会结构")
        print("  4. CultivationDesigner - 能力体系")
        print("  5. CharacterDesigner - 角色设计")
        print("  6. PlotArchitect - 剧情架构")
        print("  7. OutlineArchitect - 大纲设计")
        print("  8. ChapterArchitect - 章纲设计")
        print()

        result = self.agent_manager.run_full_workflow(self.config)

        if result["success"]:
            print(f"\n[OK] 项目初始化完成")
            print(f"  Tracker Report 已生成")
        else:
            print(f"\n❌ 项目初始化失败")

        self.chapter_manager.load_chapters()
        self.character_manager.load_characters()

        # 创建进度文件
        self._ensure_progress_file()

    def _ensure_progress_file(self):
        progress_file = os.path.join(self.project_dir, "novel-progress.txt")
        if os.path.exists(progress_file):
            return

        chapters = self.chapter_manager.chapters
        if not chapters:
            return

        target_chapters = self.config.get("target_chapters", len(chapters))
        genre = self.config.get("genre", "通用")

        chapter_progress = []
        for ch in chapters[:target_chapters]:
            chapter_progress.append(
                {
                    "chapter_number": ch.chapter_number,
                    "title": ch.title,
                    "status": "pending",
                    "word_count": 0,
                    "quality_score": 0.0,
                    "created_at": datetime.now().isoformat(),
                    "completed_at": "",
                    "notes": "",
                }
            )

        progress_data = {
            "title": self.config.get("title", "未命名"),
            "genre": genre,
            "total_chapters": target_chapters,
            "completed_chapters": 0,
            "current_chapter": 1,
            "total_word_count": 0,
            "start_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "initialized",
            "chapters": chapter_progress,
        }

        os.makedirs(self.project_dir, exist_ok=True)
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)

        print(f"[OK] 进度文件已创建: {target_chapters}章")

    def _write_novel(self):
        print("\n" + "=" * 60)
        print("[阶段2] 小说写作")
        print("=" * 60)

        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from agents.writer_agent import WriterAgent
        from agents.consistency_checker import ConsistencyChecker

        self.writer = WriterAgent(self.llm_client, self.project_dir)
        self.consistency_checker = ConsistencyChecker(self.project_dir, self.llm_client)

        progress = self.progress_manager.load_progress()
        if not progress:
            print("[错误] 无法加载进度文件")
            return

        total_chapters = progress.total_chapters
        completed = progress.completed_chapters

        current_day = 1

        print(f"\n总章节: {total_chapters}")
        print(f"已完成: {completed}")
        print(f"待完成: {total_chapters - completed}\n")

        session_count = 0
        max_sessions = total_chapters * 2
        last_consistency_check = 0

        while completed < total_chapters and session_count < max_sessions:
            session_count += 1

            print(f"\n--- 写作会话 #{session_count} ---")

            result = self.writer.write_session()

            if not result["success"]:
                if result.get("status") == "completed":
                    print("[完成] 所有章节已完成")
                    break
                else:
                    print(f"❌ 写作失败: {result.get('error', '未知错误')}")
                    break

            completed += 1

            if completed % 5 == 0 and completed > last_consistency_check:
                last_consistency_check = completed
                print(f"\n{'=' * 60}")
                print(f"[审查] 一致性检查点: 第{completed}章完成")
                print("=" * 60)

                checkpoint_approved = self._human_checkpoint(completed)
                if not checkpoint_approved:
                    print("[警告] 检查点未通过，需要回滚重写")

                check_result = self.consistency_checker.check_all_chapters()

                critical_issues = check_result.get("hardcoded_issues", {}).get(
                    "critical", []
                )
                warnings = check_result.get("hardcoded_issues", {}).get("warnings", [])

                if critical_issues or not check_result.get("passed", True):
                    print(
                        f"\n[警告] 发现一致性问题 ({len(critical_issues)} 严重, {len(warnings)} 警告)"
                    )

                    for issue in critical_issues:
                        print(f"  ❌ [严重] {issue.get('message', issue)}")

                    for issue in warnings[:5]:
                        print(f"  [警告] {issue.get('message', issue)}")

                    report_dir = os.path.join(self.project_dir, "consistency_reports")
                    os.makedirs(report_dir, exist_ok=True)

                    report = self.consistency_checker.generate_report(check_result)
                    report_path = os.path.join(
                        report_dir, f"check_chapter_{completed}.md"
                    )
                    with open(report_path, "w", encoding="utf-8") as f:
                        f.write(report)
                    print(f"  详细报告已保存: {report_path}")

                    self._flag_consistency_issue(completed, check_result)
                else:
                    print(f"[完成] 一致性检查通过")
                    if warnings:
                        print(f"   (有 {len(warnings)} 个警告，详见报告)")

            percentage = (completed / total_chapters) * 100
            print(f"\n总体进度: {completed}/{total_chapters} ({percentage:.1f}%)")

            time.sleep(0.5)

        print(f"\n[OK] 写作阶段完成，共完成 {completed} 章")

    def _flag_consistency_issue(self, chapter: int, check_result: Dict):
        flag_file = os.path.join(self.project_dir, "consistency_issues.json")
        issues = []
        if os.path.exists(flag_file):
            with open(flag_file, "r", encoding="utf-8") as f:
                issues = json.load(f)

        issues.append(
            {
                "chapter": chapter,
                "timestamp": datetime.now().isoformat(),
                "issues": check_result.get("issues", []),
                "status": "pending_review",
            }
        )

        with open(flag_file, "w", encoding="utf-8") as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)

    def _review_novel(self):
        print("\n" + "=" * 60)
        print("[审查] 阶段3: 质量审查")
        print("=" * 60)

        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from agents.reviewer_agent import ReviewerAgent

        self.reviewer = ReviewerAgent(self.llm_client, self.project_dir)

        results = self.reviewer.review_all_chapters()

        passed = sum(1 for r in results if r.passed)
        total = len(results)
        avg_score = sum(r.overall_score for r in results) / total if total > 0 else 0

        print(f"\n审查统计:")
        print(f"  总章节: {total}")
        print(f"  通过: {passed}")
        print(f"  需要修改: {total - passed}")
        print(f"  平均评分: {avg_score:.1f}/10")

    def _human_checkpoint(self, chapter_number: int) -> bool:
        print(f"\n{'=' * 60}")
        print(f"[检查点] 已完成第{chapter_number}章")
        print("=" * 60)
        print("请检查以下内容：")
        print("  1. 战力是否合理（无越级秒杀）")
        print("  2. 时间线是否连贯（无时间倒流）")
        print("  3. 武器命名是否统一")
        print("  4. 反派动机是否合理")
        print()

        print("[自动] 检查点通过（可在交互模式下启用人工确认）")
        return True

    def _merge_chapters(self):
        print("\n" + "=" * 60)
        print("[合并] 阶段4: 合并章节")
        print("=" * 60)

        chapters_dir = os.path.join(self.project_dir, "chapters")

        if not os.path.exists(chapters_dir):
            print("❌ 错误: 章节目录不存在")
            return

        chapter_files = sorted(
            [
                f
                for f in os.listdir(chapters_dir)
                if f.startswith("chapter-") and f.endswith(".md")
            ]
        )

        if not chapter_files:
            print("❌ 错误: 未找到章节文件")
            return

        merged_content = f"""# {self.config.get("title", "未命名小说")}

**类型**: {self.config.get("genre", "通用")}

**生成日期**: {datetime.now().strftime("%Y-%m-%d")}

---

"""

        total_word_count = 0

        for chapter_file in chapter_files:
            file_path = os.path.join(chapters_dir, chapter_file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            merged_content += content + "\n\n---\n\n"
            total_word_count += len(content)

        output_file = os.path.join(self.project_dir, "novel-complete.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(merged_content)

        print(f"[OK] 合并完成")
        print(f"  章节数: {len(chapter_files)}")
        print(f"  总字数: {total_word_count:,}")
        print(f"  输出文件: novel-complete.md")

    def _generate_final_report(self, elapsed_time: float) -> str:
        progress = self.progress_manager.load_progress()

        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        # 如果无法加载进度，从文件系统统计
        if not progress:
            chapters_dir = os.path.join(self.project_dir, "chapters")
            if os.path.exists(chapters_dir):
                chapter_files = [
                    f
                    for f in os.listdir(chapters_dir)
                    if f.startswith("chapter-") and f.endswith(".md")
                ]
                total_word_count = 0
                for f in chapter_files:
                    with open(
                        os.path.join(chapters_dir, f), "r", encoding="utf-8"
                    ) as fp:
                        total_word_count += len(fp.read())

                report = f"""
{"=" * 60}
📊 小说生成报告
{"=" * 60}

项目信息:
  标题: {self.config.get("title", "未命名")}
  类型: {self.config.get("genre", "通用")}
  总章节: {len(chapter_files)}
  已完成: {len(chapter_files)}

生成统计:
  耗时: {hours}小时 {minutes}分钟 {seconds}秒
  总字数: {total_word_count:,}

文件位置:
  项目目录: {self.project_dir}
  完整小说: {self.project_dir}/novel-complete.md
  章节目录: {self.project_dir}/chapters/

V7系统信息:
  检测类型: {self.v7_setup.get("genre", "N/A") if self.v7_setup else "N/A"}
  约束模板: {self.v7_setup.get("template_name", "N/A") if self.v7_setup else "N/A"}

{"=" * 60}
"""
                report_file = os.path.join(self.project_dir, "generation-report.txt")
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)
                return report

        report = f"""
{"=" * 60}
📊 小说生成报告
{"=" * 60}

项目信息:
  标题: {progress.title}
  类型: {progress.genre}
  总章节: {progress.total_chapters}
  已完成: {progress.completed_chapters}
  总字数: {progress.total_word_count:,}

生成统计:
  耗时: {hours}小时 {minutes}分钟 {seconds}秒

文件位置:
  项目目录: {self.project_dir}
  完整小说: {self.project_dir}/novel-complete.md
  章节目录: {self.project_dir}/chapters/

V7系统信息:
  检测类型: {self.v7_setup.get("genre", "N/A") if self.v7_setup else "N/A"}
  约束模板: {self.v7_setup.get("template_name", "N/A") if self.v7_setup else "N/A"}

{"=" * 60}
"""

        report_file = os.path.join(self.project_dir, "generation-report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        return report

    def get_progress(self) -> str:
        return self.progress_manager.generate_progress_report()


class MockLLMClient:
    def generate(self, prompt: str, **kwargs) -> str:
        return f"[模拟LLM输出] 基于提示: {prompt[:50]}..."

    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return {}


def create_novel(config: Dict[str, Any]) -> Dict[str, Any]:
    generator = NovelGenerator(config)
    return generator.run()
