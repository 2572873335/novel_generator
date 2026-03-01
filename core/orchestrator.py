"""
Orchestrator - 主循环组装
整合所有组件的主协调器

功能：
1. 协调各组件工作流程
2. 处理异常和熔断
3. 管理检查点恢复
4. 初始化项目（大纲、人物）
5. 保存章节为Markdown
6. 更新Agent状态
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChapterStatus(Enum):
    """章节状态"""
    PENDING = "pending"
    WRITING = "writing"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"


class Orchestrator:
    """
    主协调器

    工作流程：
    1. 初始化组件 (EmotionTracker, WorldBible, PromptAssembler, CreativeDirector, EmotionWriter)
    2. 检查并初始化项目（大纲、人物）
    3. 循环写作各章节
    4. 每次写作后调用CreativeDirector仲裁
    5. 处理熔断和重试
    6. 保存检查点
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_dir = Path(config.get("project_dir", "novels/default"))

        # 组件
        self.llm_client = None
        self.emotion_tracker = None
        self.world_bible = None
        self.prompt_assembler = None
        self.creative_director = None
        self.emotion_writer = None
        self.initializer_agent = None

        # 状态
        self.current_chapter = 1
        self.target_chapters = config.get("target_chapters", 50)
        self.is_running = False
        self.is_suspended = False
        self.pause_event = None  # 由 UI worker 注入的 threading.Event

        # 检查点
        self.checkpoint_interval = config.get("checkpoint_interval", 5)

        # 回调
        self.on_chapter_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_suspended: Optional[Callable] = None
        self.on_agent_status: Optional[Callable] = None
        self.on_emotion_update: Optional[Callable] = None
        self.on_log: Optional[Callable] = None
        self.on_text_stream: Optional[Callable] = None  # 流式文本回调

    def set_ui_callbacks(self,
                         on_log: Optional[Callable] = None,
                         on_agent_status: Optional[Callable] = None,
                         on_emotion_update: Optional[Callable] = None,
                         on_chapter_complete: Optional[Callable] = None,
                         on_error: Optional[Callable] = None,
                         on_suspended: Optional[Callable] = None,
                         on_text_stream: Optional[Callable] = None):
        """
        设置UI回调函数

        Args:
            on_log: 日志回调 (message: str)
            on_agent_status: Agent状态回调 (data: dict)
            on_emotion_update: 情绪更新回调 (data: dict)
            on_chapter_complete: 章节完成回调 (result: dict)
            on_error: 错误回调 (error: dict)
            on_suspended: 暂停回调 (data: dict)
            on_text_stream: 流式文本回调 (chunk: str)
        """
        self.on_log = on_log
        self.on_agent_status = on_agent_status
        self.on_emotion_update = on_emotion_update
        self.on_chapter_complete = on_chapter_complete
        self.on_error = on_error
        self.on_suspended = on_suspended
        self.on_text_stream = on_text_stream

    def _emit_log(self, message: str, level: str = "info"):
        """发送日志回调"""
        if self.on_log:
            self.on_log(message)
        logger.info(message)

    def _emit_agent_status(self, name: str, status: str, chapter: int = 0):
        """发送Agent状态回调"""
        if self.on_agent_status:
            self.on_agent_status({
                "name": name,
                "status": status,
                "chapter": chapter
            })

    def initialize(self):
        """初始化所有组件"""
        logger.info("Initializing Orchestrator...")

        # 创建项目目录和章节目录
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "chapters").mkdir(parents=True, exist_ok=True)

        # 创建LLM客户端
        self._init_llm_client()

        # 延迟导入组件
        from core.emotion_tracker import EmotionTracker
        from core.world_bible import WorldBible
        from core.prompt_assembler import PromptAssembler
        from agents.creative_director import CreativeDirector
        from agents.emotion_writer import EmotionWriter

        # 初始化组件
        self.emotion_tracker = EmotionTracker(str(self.project_dir), self.llm_client)
        self.world_bible = WorldBible(str(self.project_dir))
        self.prompt_assembler = PromptAssembler(str(self.project_dir))
        self.creative_director = CreativeDirector(str(self.project_dir))
        self.emotion_writer = EmotionWriter(self.llm_client, str(self.project_dir))

        # 检查是否已有暂停状态
        if self.creative_director.is_suspended():
            logger.warning("Project is in suspended state!")
            self.is_suspended = True

        logger.info("Orchestrator initialized successfully")

    def _init_llm_client(self):
        """初始化LLM客户端"""
        try:
            from core.model_manager import create_model_manager
            from core.config_manager import load_env_file

            env_config = load_env_file()
            model_id = env_config.get("DEFAULT_MODEL_ID", "deepseek-v3")
            self.llm_client = create_model_manager(model_id)
            logger.info(f"LLM client initialized: {model_id}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise

    def _initialize_project_if_needed(self):
        """
        Issue 3 Fix: 初始化项目（如果需要）
        在开始写作前生成大纲和人物档案
        """
        outline_file = self.project_dir / "outline.md"
        characters_file = self.project_dir / "characters.json"

        # 如果大纲或人物文件不存在，则初始化
        if not outline_file.exists() or not characters_file.exists():
            logger.info("Project not initialized, generating outline and characters...")
            self._emit_log("正在初始化项目：生成大纲和人物档案...")

            # 更新Agent状态 - 使用UI中定义的agent名称
            self._emit_agent_status("PromptAssembler", "working", 0)
            self._emit_agent_status("ElasticArchitect", "thinking", 0)

            try:
                # 调用初始化Agent生成大纲和人物
                self._run_initializer()

                self._emit_log("项目初始化完成")
                logger.info("Project initialization completed")

            except Exception as e:
                logger.error(f"Failed to initialize project: {e}")
                self._emit_agent_status("PromptAssembler", "error", 0)
                raise
            finally:
                # 重置状态
                self._emit_agent_status("PromptAssembler", "idle", 0)
                self._emit_agent_status("ElasticArchitect", "idle", 0)
        else:
            logger.info("Project already initialized, skipping...")

    def _run_initializer(self):
        """运行初始化Agent生成大纲和人物"""
        # 获取项目配置
        title = self.config.get("title", "未命名小说")
        genre = self.config.get("genre", "奇幻")
        description = self.config.get("description", "")
        protagonist = self.config.get("protagonist", "")

        system_prompt = """你是一个专业的小说策划助手，负责生成小说大纲和人物设定。
请根据用户提供的信息，生成完整的：
1. 小说大纲 (outline.md) - 包含故事主线、情节点、章节规划
2. 人物设定 (characters.json) - 包含主角、配角设定

请以JSON格式输出人物设定，大纲使用Markdown格式。"""

        # 构建主角信息
        protagonist_info = ""
        if protagonist:
            protagonist_info = f"\n主角：{protagonist}"

        user_prompt = f"""请为以下小说生成大纲和人物设定：

标题：{title}
类型：{genre}
简介：{description or '无'}{protagonist_info}

目标章节数：{self.target_chapters}章

请严格根据以上信息生成大纲和人物设定，不得擅自更改标题、类型和主角！

请生成：
1. 完整的故事大纲（包括主线剧情、各卷情节安排）
2. 主角和重要配角的详细设定（包括姓名、性格、背景、能力等）

注意：大纲应该有足够的细节，能够支撑{self.target_chapters}章的篇幅。"""

        try:
            response = self.llm_client.generate(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.8
            )

            # 解析输出，分离大纲和人物
            characters_content = ""
            outline_content = ""

            # 方式1: 查找 ```json ... ``` 格式
            json_start = response.find("```json")
            if json_start >= 0:
                json_end = response.find("```", json_start + 7)
                if json_end > json_start:
                    characters_content = response[json_start + 7:json_end].strip()
                    outline_content = response[:json_start].strip()

            # 方式2: 如果没找到JSON，尝试查找 { ... } 格式
            if not characters_content:
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
                if json_match:
                    potential_json = json_match.group(0)
                    try:
                        json.loads(potential_json)
                        characters_content = potential_json
                        outline_content = response[:json_match.start()].strip()
                    except:
                        pass

            # 方式3: 如果完全没有JSON，整个响应作为大纲
            if not characters_content:
                outline_content = response

            # 保存大纲
            outline_file = self.project_dir / "outline.md"
            outline_file.write_text(outline_content, encoding="utf-8")
            logger.info(f"Outline saved to {outline_file}")

            # 保存人物设定
            if characters_content:
                characters_file = self.project_dir / "characters.json"
                # 尝试解析JSON
                try:
                    json_data = json.loads(characters_content)
                    characters_file.write_text(
                        json.dumps(json_data, ensure_ascii=False, indent=2),
                        encoding="utf-8"
                    )
                except json.JSONDecodeError:
                    # 如果解析失败，作为文本保存
                    characters_file.write_text(characters_content, encoding="utf-8")
                logger.info(f"Characters saved to {characters_file}")

            self._emit_log("大纲和人物设定已生成")

        except Exception as e:
            logger.error(f"Failed to run initializer: {e}")
            raise

    def run(self, start_chapter: int = 1):
        """
        运行主循环

        Args:
            start_chapter: 起始章节
        """
        if self.is_suspended:
            logger.error("Cannot run: project is in suspended state")
            return self._handle_suspended()

        self.is_running = True
        self.current_chapter = start_chapter

        logger.info(f"Starting writing loop from chapter {start_chapter}")
        self._emit_log(f"开始生成小说，目标{self.target_chapters}章")

        try:
            # Issue 3 Fix: 初始化项目（如果需要）
            if start_chapter == 1:
                self._initialize_project_if_needed()

            while self.current_chapter <= self.target_chapters and self.is_running:
                # 暂停检查点：如果 UI 触发了暂停，这里会阻塞直到恢复
                if self.pause_event is not None:
                    self.pause_event.wait()
                    if not self.is_running:
                        break

                # 写作章节
                result = self._write_chapter(self.current_chapter)

                if result["status"] == "completed":
                    # 保存章节为Markdown（Issue 1 Fix）
                    self._save_chapter_as_markdown(
                        self.current_chapter,
                        result["content"],
                        result.get("emotion", {})
                    )

                    # 检查是否需要仲裁
                    reports = result.get("reports", [])

                    # Issue 2 Fix: 更新仲裁阶段Agent状态
                    self._emit_agent_status("ConsistencyGuardian", "auditing", self.current_chapter)
                    self._emit_agent_status("PayoffAuditor", "auditing", self.current_chapter)
                    self._emit_agent_status("CreativeDirector", "thinking", self.current_chapter)

                    arbitration = self.creative_director.arbitrate(
                        self.current_chapter,
                        result["content"],
                        reports
                    )

                    # 重置仲裁阶段状态
                    self._emit_agent_status("ConsistencyGuardian", "idle", self.current_chapter)
                    self._emit_agent_status("PayoffAuditor", "idle", self.current_chapter)

                    # 处理仲裁结果
                    self._handle_arbitration(arbitration, result)

                elif result["status"] == "suspended":
                    self.is_running = False
                    self.is_suspended = True
                    if self.on_suspended:
                        self.on_suspended(result)

                elif result["status"] == "failed":
                    if self.on_error:
                        self.on_error(result)

                # 保存检查点
                if self.current_chapter % self.checkpoint_interval == 0:
                    self._save_checkpoint()

                # 下一章
                self.current_chapter += 1

        except Exception as e:
            logger.error(f"Error in writing loop: {e}")
            if self.on_error:
                self.on_error({"error": str(e)})

        finally:
            self.is_running = False
            self._save_checkpoint()

        logger.info("Writing loop completed")
        self._emit_log("小说生成完成！")

    def _save_chapter_as_markdown(self, chapter_num: int, content: str, emotion: Dict):
        """
        Issue 1 Fix: 将章节保存为Markdown格式

        Args:
            chapter_num: 章节编号
            content: 章节内容
            emotion: 情绪数据
        """
        # 确保章节目录存在
        chapters_dir = self.project_dir / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        # 保存为Markdown文件
        md_file = chapters_dir / f"chapter_{chapter_num:03d}.md"
        md_file.write_text(content, encoding="utf-8")
        logger.info(f"Chapter {chapter_num} saved as Markdown: {md_file}")

        # 同时保存元数据JSON（用于情绪追踪）
        meta_file = chapters_dir / f"chapter_{chapter_num:03d}.json"
        meta_data = {
            "chapter": chapter_num,
            "emotion": emotion,
            "saved_at": datetime.now().isoformat()
        }
        meta_file.write_text(
            json.dumps(meta_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _write_chapter(self, chapter_num: int) -> Dict[str, Any]:
        """写作单章 - 支持流式输出"""
        logger.info(f"Writing chapter {chapter_num}/{self.target_chapters}")
        self._emit_log(f"正在写作第{chapter_num}章...")

        # Issue 2 Fix: 更新大纲阶段Agent状态
        self._emit_agent_status("PromptAssembler", "working", chapter_num)
        self._emit_agent_status("ElasticArchitect", "thinking", chapter_num)

        # 获取写作上下文
        context = self.emotion_writer.get_context_for_chapter(
            chapter_num=chapter_num,
            target_chapters=self.target_chapters
        )

        # 重置大纲阶段状态
        self._emit_agent_status("PromptAssembler", "idle", chapter_num)
        self._emit_agent_status("ElasticArchitect", "idle", chapter_num)

        # Issue 2 Fix: 更新写作阶段Agent状态
        self._emit_agent_status("EmotionWriter", "writing", chapter_num)
        self._emit_agent_status("WorldBible", "recording", chapter_num)

        # 获取上一章内容
        previous_chapter = ""
        if chapter_num > 1:
            # 先尝试读取Markdown文件
            prev_md = self.project_dir / "chapters" / f"chapter_{chapter_num - 1:03d}.md"
            if prev_md.exists():
                previous_chapter = prev_md.read_text(encoding="utf-8")
            else:
                # 回退到旧的JSON格式
                prev_file = self.project_dir / "chapters" / f"chapter_{chapter_num - 1}.json"
                if prev_file.exists():
                    try:
                        data = json.loads(prev_file.read_text(encoding="utf-8"))
                        previous_chapter = data.get("content", "")
                    except:
                        pass

        # 使用流式写作
        full_content = ""
        result = None

        try:
            # 获取流式生成器
            stream_gen = self.emotion_writer.write_chapter_stream(context, previous_chapter)

            # 迭代流式响应
            for chunk_text, chunk_result in stream_gen:
                if chunk_result is not None:
                    # 收到最终结果
                    result = chunk_result
                elif chunk_text:
                    # 收到文本块
                    full_content += chunk_text
                    # 触发流式文本回调
                    if self.on_text_stream:
                        self.on_text_stream(chunk_text)

            # 如果没有收到最终结果（兼容模式），构造一个
            if result is None:
                result = {
                    "success": True,
                    "chapter": chapter_num,
                    "content": full_content,
                    "emotion": {},
                    "reports": []
                }

        except Exception as e:
            logger.error(f"Streaming write failed: {e}")
            result = {
                "success": False,
                "chapter": chapter_num,
                "error": str(e),
                "content": full_content
            }

        # 更新情绪追踪状态
        self._emit_agent_status("EmotionTracker", "tracking", chapter_num)

        # 重置写作状态
        self._emit_agent_status("EmotionWriter", "idle", chapter_num)
        self._emit_agent_status("WorldBible", "idle", chapter_num)

        if result.get("success"):
            # 重置情绪追踪状态
            self._emit_agent_status("EmotionTracker", "idle", chapter_num)
            return {
                "status": "completed",
                "chapter": chapter_num,
                "content": result.get("content", full_content),
                "emotion": result.get("emotion", {}),
                "reports": []
            }
        else:
            self._emit_agent_status("EmotionWriter", "error", chapter_num)
            return {
                "status": "failed",
                "chapter": chapter_num,
                "error": result.get("error", "Unknown error")
            }

    def _handle_arbitration(self, arbitration, write_result: Dict):
        """处理仲裁结果"""
        from agents.creative_director import Decision

        if arbitration.decision == Decision.PASS:
            logger.info(f"Chapter {self.current_chapter} passed")
            self._emit_log(f"第{self.current_chapter}章审核通过")
            if self.on_chapter_complete:
                self.on_chapter_complete(write_result)

        elif arbitration.decision == Decision.REWRITE:
            logger.warning(f"Chapter {self.current_chapter} needs rewrite")
            self._emit_log(f"第{self.current_chapter}章需要重写")
            # 触发重写
            self._trigger_rewrite(self.current_chapter, arbitration.actionable_feedback)

        elif arbitration.decision == Decision.ROLLBACK:
            logger.warning(f"Chapter {self.current_chapter} needs rollback")
            self._emit_log(f"第{self.current_chapter}章需要回滚")
            # 触发回滚
            self._trigger_rollback(self.current_chapter, arbitration.actionable_feedback)

        elif arbitration.decision == Decision.SUSPEND:
            logger.critical(f"Chapter {self.current_chapter} triggered suspension!")
            self._emit_log(f"触发熔断：第{self.current_chapter}章")
            self.is_running = False
            self.is_suspended = True
            if self.on_suspended:
                self.on_suspended({
                    "chapter": self.current_chapter,
                    "reason": arbitration.actionable_feedback
                })

    def _trigger_rewrite(self, chapter: int, feedback: str):
        """触发重写 - 支持流式输出"""
        logger.info(f"Rewriting chapter {chapter}")

        # 更新Agent状态
        self._emit_agent_status("EmotionWriter", "writing", chapter)

        # 获取上下文
        context = self.emotion_writer.get_context_for_chapter(
            chapter_num=chapter,
            target_chapters=self.target_chapters
        )

        # 添加反馈到自定义指令
        context.custom_instructions += f"\n\n【重写反馈】\n{feedback}"

        # 使用流式重写
        full_content = ""
        result = None

        try:
            # 获取流式生成器
            stream_gen = self.emotion_writer.write_chapter_stream(context, "")

            # 迭代流式响应
            for chunk_text, chunk_result in stream_gen:
                if chunk_result is not None:
                    # 收到最终结果
                    result = chunk_result
                elif chunk_text:
                    # 收到文本块
                    full_content += chunk_text
                    # 触发流式文本回调
                    if self.on_text_stream:
                        self.on_text_stream(chunk_text)

            # 如果没有收到最终结果（兼容模式），构造一个
            if result is None:
                result = {
                    "success": True,
                    "chapter": chapter,
                    "content": full_content,
                    "emotion": {},
                    "reports": []
                }

        except Exception as e:
            logger.error(f"Streaming rewrite failed: {e}")
            result = {
                "success": False,
                "chapter": chapter,
                "error": str(e),
                "content": full_content
            }

        # 重置状态
        self._emit_agent_status("EmotionWriter", "idle", chapter)

        if result.get("success"):
            # 保存为Markdown
            self._save_chapter_as_markdown(
                chapter,
                result["content"],
                result.get("emotion", {})
            )

            # 再次仲裁
            reports = self.world_bible.check_consistency_violations(
                result["content"], chapter
            )

            # 更新仲裁状态
            self._emit_agent_status("CreativeDirector", "thinking", chapter)

            arbitration = self.creative_director.arbitrate(
                chapter, result["content"], reports
            )

            self._emit_agent_status("CreativeDirector", "idle", chapter)

            self._handle_arbitration(arbitration, result)

    def _trigger_rollback(self, chapter: int, feedback: str):
        """触发回滚"""
        logger.warning(f"Rolling back chapter {chapter}")

        # 更新Agent状态
        self._emit_agent_status("CreativeDirector", "working", chapter)

        # 记录回滚
        self.creative_director.record_rollback(chapter, feedback[:100])

        # 重置状态
        self._emit_agent_status("CreativeDirector", "idle", chapter)

        # 重新写作
        self._trigger_rewrite(chapter, feedback)

    def _handle_suspended(self):
        """处理暂停状态"""
        suspended_file = self.project_dir / ".suspended.json"
        if suspended_file.exists():
            data = json.loads(suspended_file.read_text(encoding="utf-8"))
            logger.critical(f"Suspended at chapter {data.get('suspended_chapter')}")
            logger.critical(f"Reason: {data.get('reason')}")

            if self.on_suspended:
                self.on_suspended(data)

    def _save_checkpoint(self):
        """保存检查点"""
        checkpoint = {
            "current_chapter": self.current_chapter,
            "target_chapters": self.target_chapters,
            "is_suspended": self.is_suspended,
            "timestamp": datetime.now().isoformat(),
            "emotion_state": {
                "net_debt": self.emotion_tracker.ledger.net_debt if self.emotion_tracker else 0
            }
        }

        checkpoint_file = self.project_dir / ".checkpoint.json"
        checkpoint_file.write_text(
            json.dumps(checkpoint, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        logger.info(f"Checkpoint saved: chapter {self.current_chapter}")

    def load_checkpoint(self) -> Optional[int]:
        """加载检查点"""
        checkpoint_file = self.project_dir / ".checkpoint.json"
        if checkpoint_file.exists():
            try:
                data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
                chapter = data.get("current_chapter", 1)
                logger.info(f"Loaded checkpoint: chapter {chapter}")
                return chapter
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return None

    def resume(self):
        """从检查点恢复"""
        chapter = self.load_checkpoint()
        if chapter:
            self.run(start_chapter=chapter)
        else:
            logger.warning("No checkpoint found, starting from beginning")

    def stop(self):
        """停止运行"""
        logger.info("Stopping orchestrator...")
        self._emit_log("正在停止...")
        self.is_running = False

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "is_running": self.is_running,
            "is_suspended": self.is_suspended,
            "current_chapter": self.current_chapter,
            "target_chapters": self.target_chapters,
            "circuit_breaker_status": self.creative_director.get_status() if self.creative_director else {},
            "emotion_state": {
                "net_debt": self.emotion_tracker.ledger.net_debt if self.emotion_tracker else 0
            }
        }


def create_orchestrator(config: Dict[str, Any]) -> Orchestrator:
    """创建并初始化协调器"""
    orchestrator = Orchestrator(config)
    orchestrator.initialize()
    return orchestrator
