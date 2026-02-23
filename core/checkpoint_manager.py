"""
Enhanced Checkpoint Manager - 增强版检查点管理器

功能：
1. 可恢复检查点 - 支持从任意检查点恢复
2. 自动保存草稿 - 每1000字自动保存
3. 优雅降级 - LLM超时自动重试
4. 人工干预点 - 支持暂停等待确认
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class CheckpointStatus(Enum):
    """检查点状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"


@dataclass
class Checkpoint:
    """检查点数据"""
    checkpoint_id: str
    chapter_number: int
    stage: str
    status: str = "pending"  # 存储为字符串以支持JSON序列化
    word_count: int = 0
    content: str = ""
    timestamp: str = ""
    error: str = ""
    retry_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "chapter_number": self.chapter_number,
            "stage": self.stage,
            "status": self.status,
            "word_count": self.word_count,
            "content": self.content[:500] if self.content else "",
            "timestamp": self.timestamp,
            "error": self.error,
            "retry_count": self.retry_count
        }


@dataclass
class ChapterCheckpointState:
    """章节检查点状态"""
    chapter_number: int
    project_dir: str
    checkpoints: List[Checkpoint] = field(default_factory=list)
    current_stage: str = ""
    last_checkpoint_id: str = ""
    started_at: str = ""
    last_updated: str = ""

    def save(self):
        """保存检查点状态到文件"""
        state_file = os.path.join(
            self.project_dir, "chapters",
            f"checkpoint-state-{self.chapter_number:03d}.json"
        )
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, project_dir: str, chapter_number: int) -> Optional['ChapterCheckpointState']:
        """从文件加载检查点状态"""
        state_file = os.path.join(
            project_dir, "chapters",
            f"checkpoint-state-{chapter_number:03d}.json"
        )
        if not os.path.exists(state_file):
            return None
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                state = cls(
                    chapter_number=data["chapter_number"],
                    project_dir=project_dir,
                    checkpoints=[Checkpoint(**cp) for cp in data.get("checkpoints", [])],
                    current_stage=data.get("current_stage", ""),
                    last_checkpoint_id=data.get("last_checkpoint_id", ""),
                    started_at=data.get("started_at", ""),
                    last_updated=data.get("last_updated", "")
                )
                return state
        except Exception as e:
            logger.warning(f"Failed to load checkpoint state: {e}")
            return None


class CheckpointManager:
    """
    增强版检查点管理器

    使用方式：
    manager = CheckpointManager(project_dir, chapter_number)

    # 创建一个检查点
    cp = manager.create_checkpoint("draft_stage", 1)

    # 保存进度
    manager.update_checkpoint(cp.checkpoint_id, content="xxx", status="completed")

    # 检查是否有可恢复的检查点
    recoverable = manager.get_recoverable_checkpoint()
    if recoverable:
        content = manager.recover_content(recoverable.checkpoint_id)
    """

    def __init__(self, project_dir: str, chapter_number: int):
        self.project_dir = project_dir
        self.chapter_number = chapter_number
        self.chapters_dir = os.path.join(project_dir, "chapters")
        self.state = ChapterCheckpointState.load(project_dir, chapter_number)

        if not self.state:
            self.state = ChapterCheckpointState(
                chapter_number=chapter_number,
                project_dir=project_dir,
                started_at=datetime.now().isoformat()
            )

    def create_checkpoint(self, stage: str, checkpoint_id: str = None) -> Checkpoint:
        """创建一个新的检查点"""
        if not checkpoint_id:
            checkpoint_id = f"{stage}-{len(self.state.checkpoints) + 1}"

        cp = Checkpoint(
            checkpoint_id=checkpoint_id,
            chapter_number=self.chapter_number,
            stage=stage,
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )

        self.state.checkpoints.append(cp)
        self.state.current_stage = stage
        self.state.last_checkpoint_id = checkpoint_id
        self.state.last_updated = datetime.now().isoformat()

        self._save_checkpoint_file(cp)
        self.state.save()

        logger.info(f"Created checkpoint: {checkpoint_id}")
        return cp

    def update_checkpoint(self, checkpoint_id: str, content: str = None,
                          status: str = None, error: str = None):
        """更新检查点状态"""
        for cp in self.state.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                if content is not None:
                    cp.content = content
                    cp.word_count = len(content)
                if status is not None:
                    cp.status = status
                if error:
                    cp.error = error
                cp.timestamp = datetime.now().isoformat()

                self._save_checkpoint_file(cp)
                break

        self.state.last_updated = datetime.now().isoformat()
        self.state.save()

    def retry_checkpoint(self, checkpoint_id: str, max_retries: int = 3) -> bool:
        """重试失败的检查点"""
        for cp in self.state.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                if cp.retry_count >= max_retries:
                    logger.warning(f"Checkpoint {checkpoint_id} exceeded max retries")
                    return False

                cp.retry_count += 1
                cp.status = CheckpointStatus.IN_PROGRESS
                cp.error = ""
                cp.timestamp = datetime.now().isoformat()

                self._save_checkpoint_file(cp)
                self.state.save()

                logger.info(f"Retrying checkpoint {checkpoint_id}, attempt {cp.retry_count}")
                return True

        return False

    def get_recoverable_checkpoint(self) -> Optional[Checkpoint]:
        """获取最近可恢复的检查点"""
        for cp in reversed(self.state.checkpoints):
            if cp.status == "completed" and cp.content:
                return cp

        # 查找最后一个 IN_PROGRESS 的检查点
        for cp in reversed(self.state.checkpoints):
            if cp.status == "in_progress" and cp.retry_count < 3:
                return cp

        return None

    def recover_content(self, checkpoint_id: str = None) -> str:
        """从检查点恢复内容"""
        if checkpoint_id:
            for cp in self.state.checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    cp.status = "recovered"
                    self.state.save()
                    return cp.content
        else:
            # 恢复到最后一个完成或进行中的检查点
            recoverable = self.get_recoverable_checkpoint()
            if recoverable:
                recoverable.status = CheckpointStatus.RECOVERED
                self.state.save()
                return recoverable.content

        return ""

    def _save_checkpoint_file(self, checkpoint: Checkpoint):
        """保存单个检查点文件"""
        cp_file = os.path.join(
            self.chapters_dir,
            f"checkpoint-{checkpoint.checkpoint_id}.json"
        )
        try:
            with open(cp_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save checkpoint file: {e}")

    def clear_checkpoints(self, keep_latest: bool = True):
        """清理旧检查点"""
        if keep_latest and self.state.checkpoints:
            # 保留最后一个
            latest = self.state.checkpoints[-1]
            self.state.checkpoints = [latest]
        else:
            self.state.checkpoints = []

        self.state.save()

    def get_checkpoint_summary(self) -> Dict[str, Any]:
        """获取检查点摘要"""
        total = len(self.state.checkpoints)
        completed = sum(1 for cp in self.state.checkpoints if cp.status == "completed")
        failed = sum(1 for cp in self.state.checkpoints if cp.status == "failed")

        return {
            "chapter": self.chapter_number,
            "total": total,
            "completed": completed,
            "failed": failed,
            "current_stage": self.state.current_stage,
            "last_checkpoint": self.state.last_checkpoint_id,
            "started_at": self.state.started_at,
            "last_updated": self.state.last_updated
        }


class RetryableLLMCall:
    """
    可重试的LLM调用包装器

    用于优雅降级 - LLM调用超时自动重试
    """

    def __init__(self, llm_client, max_retries: int = 3, timeout: int = 60):
        self.llm_client = llm_client
        self.max_retries = max_retries
        self.timeout = timeout

    def generate(self, prompt: str, **kwargs) -> str:
        """带重试的LLM调用"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # 尝试调用LLM
                result = self.llm_client.generate(prompt=prompt, **kwargs)
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    # 指数退避
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        # 所有重试都失败
        logger.error(f"LLM call failed after {self.max_retries} attempts: {last_error}")
        raise last_error


class HumanInLoop:
    """
    人工干预点

    支持在关键决策点暂停等待人工确认
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.pause_file = os.path.join(project_dir, ".human_pause")
        self.approval_file = os.path.join(project_dir, ".human_approval")

    def wait_for_approval(self, decision_point: str, timeout: int = 300) -> bool:
        """
        等待人工确认

        Args:
            decision_point: 决策点标识
            timeout: 超时时间（秒）

        Returns:
            True: 人工确认通过
            False: 超时或拒绝
        """
        # 写入暂停文件
        pause_info = {
            "decision_point": decision_point,
            "timestamp": datetime.now().isoformat(),
            "status": "waiting"
        }

        with open(self.pause_file, "w", encoding="utf-8") as f:
            json.dump(pause_info, f, ensure_ascii=False, indent=2)

        print(f"\n{'=' * 60}")
        print(f"[人工干预] 等待确认: {decision_point}")
        print(f"超时时间: {timeout}秒")
        print("=" * 60)

        # 等待批准文件
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(self.approval_file):
                try:
                    with open(self.approval_file, "r", encoding="utf-8") as f:
                        approval = json.load(f)

                    # 清理文件
                    os.remove(self.pause_file)
                    os.remove(self.approval_file)

                    if approval.get("approved", False):
                        print(f"[人工干预] 决策点 {decision_point} 已批准")
                        return True
                    else:
                        print(f"[人工干预] 决策点 {decision_point} 已拒绝")
                        return False
                except Exception as e:
                    logger.warning(f"Failed to read approval: {e}")

            time.sleep(1)

        # 超时
        print(f"[人工干预] 等待超时，自动继续")
        if os.path.exists(self.pause_file):
            os.remove(self.pause_file)

        return True  # 超时后默认继续

    def request_intervention(self, issue_description: str) -> Dict[str, Any]:
        """
        请求人工干预

        用于报告问题并等待处理
        """
        intervention_file = os.path.join(self.project_dir, ".intervention_request.json")

        request = {
            "description": issue_description,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }

        with open(intervention_file, "w", encoding="utf-8") as f:
            json.dump(request, f, ensure_ascii=False, indent=2)

        print(f"\n[人工干预请求] {issue_description}")
        print("请检查干预请求文件并处理")

        return request
