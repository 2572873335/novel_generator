"""
Orchestrator - 主循环组装
整合所有组件的主协调器

功能：
1. 协调各组件工作流程
2. 处理异常和熔断
3. 管理检查点恢复
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
    2. 循环写作各章节
    3. 每次写作后调用CreativeDirector仲裁
    4. 处理熔断和重试
    5. 保存检查点
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

        # 状态
        self.current_chapter = 1
        self.target_chapters = config.get("target_chapters", 50)
        self.is_running = False
        self.is_suspended = False

        # 检查点
        self.checkpoint_interval = config.get("checkpoint_interval", 5)

        # 回调
        self.on_chapter_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_suspended: Optional[Callable] = None

    def initialize(self):
        """初始化所有组件"""
        logger.info("Initializing Orchestrator...")

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

        try:
            while self.current_chapter <= self.target_chapters and self.is_running:
                # 写作章节
                result = self._write_chapter(self.current_chapter)

                if result["status"] == "completed":
                    # 检查是否需要仲裁
                    reports = result.get("reports", [])
                    arbitration = self.creative_director.arbitrate(
                        self.current_chapter,
                        result["content"],
                        reports
                    )

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

    def _write_chapter(self, chapter_num: int) -> Dict[str, Any]:
        """写作单章"""
        logger.info(f"Writing chapter {chapter_num}/{self.target_chapters}")

        # 获取写作上下文
        context = self.emotion_writer.get_context_for_chapter(
            chapter_num=chapter_num,
            target_chapters=self.target_chapters
        )

        # 获取上一章内容
        previous_chapter = ""
        if chapter_num > 1:
            prev_file = self.project_dir / "chapters" / f"chapter_{chapter_num - 1}.json"
            if prev_file.exists():
                try:
                    data = json.loads(prev_file.read_text(encoding="utf-8"))
                    previous_chapter = data.get("content", "")
                except:
                    pass

        # 写作
        result = self.emotion_writer.write_chapter(context, previous_chapter)

        if result["success"]:
            return {
                "status": "completed",
                "chapter": chapter_num,
                "content": result["content"],
                "emotion": result.get("emotion", {}),
                "reports": []
            }
        else:
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
            if self.on_chapter_complete:
                self.on_chapter_complete(write_result)

        elif arbitration.decision == Decision.REWRITE:
            logger.warning(f"Chapter {self.current_chapter} needs rewrite")
            # 触发重写
            self._trigger_rewrite(self.current_chapter, arbitration.actionable_feedback)

        elif arbitration.decision == Decision.ROLLBACK:
            logger.warning(f"Chapter {self.current_chapter} needs rollback")
            # 触发回滚
            self._trigger_rollback(self.current_chapter, arbitration.actionable_feedback)

        elif arbitration.decision == Decision.SUSPEND:
            logger.critical(f"Chapter {self.current_chapter} triggered suspension!")
            self.is_running = False
            self.is_suspended = True
            if self.on_suspended:
                self.on_suspended({
                    "chapter": self.current_chapter,
                    "reason": arbitration.actionable_feedback
                })

    def _trigger_rewrite(self, chapter: int, feedback: str):
        """触发重写"""
        logger.info(f"Rewriting chapter {chapter}")

        # 获取上下文
        context = self.emotion_writer.get_context_for_chapter(
            chapter_num=chapter,
            target_chapters=self.target_chapters
        )

        # 添加反馈到自定义指令
        context.custom_instructions += f"\n\n【重写反馈】\n{feedback}"

        # 重写
        result = self.emotion_writer.write_chapter(context)

        if result["success"]:
            # 再次仲裁
            reports = self.world_bible.check_consistency_violations(
                result["content"], chapter
            )
            arbitration = self.creative_director.arbitrate(
                chapter, result["content"], reports
            )
            self._handle_arbitration(arbitration, result)

    def _trigger_rollback(self, chapter: int, feedback: str):
        """触发回滚"""
        logger.warning(f"Rolling back chapter {chapter}")

        # 记录回滚
        self.creative_director.record_rollback(chapter, feedback[:100])

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
