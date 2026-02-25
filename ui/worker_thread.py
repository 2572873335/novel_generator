"""
Worker Thread - 后台工作线程
用于在后台运行小说生成任务，避免UI卡死
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal


class GenerationWorker(QThread):
    """
    小说生成工作线程

    使用PyQt6 Signal进行线程安全通信：
    - log_signal: 实时日志
    - agent_status_signal: Agent状态更新
    - emotion_curve_signal: 情绪曲线数据
    - circuit_breaker_signal: 熔断状态
    - chapter_complete_signal: 章节完成
    - error_signal: 错误信息
    """

    # 信号定义
    log_signal = pyqtSignal(str)  # 日志消息
    agent_status_signal = pyqtSignal(dict)  # Agent状态 {"name": str, "status": str, "chapter": int}
    emotion_curve_signal = pyqtSignal(dict)  # 情绪曲线 {"expected": list, "actual": list, "chapter": int}
    circuit_breaker_signal = pyqtSignal(dict)  # 熔断状态 {"tripped": bool, "chapter": int, "reason": str}
    chapter_complete_signal = pyqtSignal(dict)  # 章节完成 {"chapter": int, "word_count": int, "emotion_debt": float}
    error_signal = pyqtSignal(str)  # 错误信息
    progress_signal = pyqtSignal(int, int)  # 进度 (current, total)

    def __init__(self, project_dir: str, config: Dict[str, Any]):
        super().__init__()
        self.project_dir = project_dir
        self.config = config
        self.orchestrator = None
        self.is_running = False

    def run(self):
        """执行生成任务"""
        self.is_running = True

        try:
            self._initialize_orchestrator()
            self._run_generation()
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")
        finally:
            self.is_running = False

    def _initialize_orchestrator(self):
        """初始化协调器"""
        from core.orchestrator import create_orchestrator

        self.log_signal.emit("Initializing orchestrator...")

        # 读取项目配置文件
        project_config = {}
        config_path = Path(self.project_dir) / "project_config.json"
        if config_path.exists():
            try:
                import json
                project_config = json.loads(config_path.read_text(encoding="utf-8"))
            except:
                pass

        # 创建配置 - 合并项目配置
        orch_config = {
            "project_dir": self.project_dir,
            "target_chapters": self.config.get("target_chapters", 10),
            "checkpoint_interval": self.config.get("checkpoint_interval", 5),
            # 从项目配置中读取
            "title": project_config.get("title", "未命名小说"),
            "genre": project_config.get("genre", "奇幻"),
            "description": project_config.get("settings", ""),
            "protagonist": project_config.get("protagonist", ""),
        }

        self.log_signal.emit(f"Project: {orch_config['title']} ({orch_config['genre']})")

        # 创建并初始化协调器
        self.orchestrator = create_orchestrator(orch_config)

        # 设置回调
        self.orchestrator.on_chapter_complete = self._on_chapter_complete
        self.orchestrator.on_error = self._on_error
        self.orchestrator.on_suspended = self._on_suspended

        self.log_signal.emit("Orchestrator initialized successfully")

    def _run_generation(self):
        """运行生成循环"""
        self.log_signal.emit(f"Starting generation: {self.config.get('target_chapters', 10)} chapters")

        # 加载检查点
        start_chapter = self.orchestrator.load_checkpoint() or 1

        if start_chapter > 1:
            self.log_signal.emit(f"Resuming from checkpoint: Chapter {start_chapter}")

        # 运行
        self.orchestrator.run(start_chapter=start_chapter)

    def _on_chapter_complete(self, result: Dict[str, Any]):
        """章节完成回调"""
        chapter = result.get("chapter", 0)
        content = result.get("content", "")
        emotion = result.get("emotion", {})

        word_count = len(content)
        emotion_debt = emotion.get("net_debt", 0)

        # 发送信号
        self.chapter_complete_signal.emit({
            "chapter": chapter,
            "word_count": word_count,
            "emotion_debt": emotion_debt
        })

        # 更新进度
        self.progress_signal.emit(chapter, self.orchestrator.target_chapters)

        # 更新情绪曲线
        self._emit_emotion_curve(chapter)

        # 更新Agent状态
        self.agent_status_signal.emit({
            "name": "EmotionWriter",
            "status": "idle",
            "chapter": chapter
        })

        self.log_signal.emit(f"Chapter {chapter} completed ({word_count} words)")

    def _on_error(self, error: Dict[str, Any]):
        """错误回调"""
        error_msg = error.get("error", "Unknown error")
        self.error_signal.emit(error_msg)
        self.log_signal.emit(f"ERROR: {error_msg}")

        # 更新Agent状态
        self.agent_status_signal.emit({
            "name": "EmotionWriter",
            "status": "error",
            "chapter": self.orchestrator.current_chapter
        })

    def _on_suspended(self, data: Dict[str, Any]):
        """暂停回调（熔断触发）"""
        chapter = data.get("chapter", 0)
        reason = data.get("reason", "Unknown")

        self.circuit_breaker_signal.emit({
            "tripped": True,
            "chapter": chapter,
            "reason": reason
        })

        self.log_signal.emit(f"CIRCUIT BREAKER TRIGGERED at Chapter {chapter}: {reason}")

        # 更新Agent状态
        self.agent_status_signal.emit({
            "name": "CreativeDirector",
            "status": "suspended",
            "chapter": chapter
        })

    def _emit_emotion_curve(self, chapter: int):
        """发送情绪曲线数据"""
        if not self.orchestrator:
            return

        # 获取预期情绪曲线
        expected = []
        actual = []

        # 从emotion_ledger读取实际数据
        emotion_file = Path(self.project_dir) / "emotion_ledger.json"
        if emotion_file.exists():
            try:
                data = json.loads(emotion_file.read_text(encoding="utf-8"))
                records = data.get("records", [])
                for r in records:
                    actual.append(r.get("net_debt", 0))
            except:
                pass

        # 生成预期曲线（基于章节进度的正弦波）
        import math
        for i in range(1, chapter + 1):
            # 预期的情绪张力曲线
            expected_val = 50 + 30 * math.sin(i / 3)
            expected.append(expected_val)

        self.emotion_curve_signal.emit({
            "expected": expected,
            "actual": actual,
            "chapter": chapter
        })

    def stop(self):
        """停止工作线程"""
        if self.orchestrator:
            self.orchestrator.stop()
        self.is_running = False
