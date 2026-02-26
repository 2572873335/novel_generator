"""
Worker Thread - 后台工作线程 v5.0 (支持流式文本输出)
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal

class GenerationWorker(QThread):
    # --- 核心信号定义 ---
    log_signal = pyqtSignal(str)  
    agent_status_signal = pyqtSignal(dict)  
    emotion_curve_signal = pyqtSignal(dict)  
    circuit_breaker_signal = pyqtSignal(dict)  
    chapter_complete_signal = pyqtSignal(dict)  
    error_signal = pyqtSignal(str)  
    progress_signal = pyqtSignal(int, int)  
    
    # 🔥 新增：流式文本输出信号（用于中间大屏的打字机效果）
    text_stream_signal = pyqtSignal(str)

    def __init__(self, project_dir: str, config: Dict[str, Any]):
        super().__init__()
        self.project_dir = project_dir
        self.config = config
        self.orchestrator = None
        self.is_running = False

    def run(self):
        self.is_running = True
        try:
            self._initialize_orchestrator()
            self._run_generation()
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")
        finally:
            self.is_running = False

    def _initialize_orchestrator(self):
        from core.orchestrator import create_orchestrator
        self.log_signal.emit("<span style='color: #00f5f5;'>[System] 初始化 IDE 调度总线...</span>")
        
        project_config = {}
        config_path = Path(self.project_dir) / "project_config.json"
        if config_path.exists():
            try: project_config = json.loads(config_path.read_text(encoding="utf-8"))
            except: pass

        orch_config = {
            "project_dir": self.project_dir,
            "target_chapters": self.config.get("target_chapters", 50),
            "checkpoint_interval": self.config.get("checkpoint_interval", 5),
            "title": project_config.get("title", "未命名小说"),
            "genre": project_config.get("genre", "通用"),
            "protagonist": project_config.get("protagonist", ""),
        }

        self.orchestrator = create_orchestrator(orch_config)
        self.orchestrator.on_chapter_complete = self._on_chapter_complete
        self.orchestrator.on_error = self._on_error
        self.orchestrator.on_suspended = self._on_suspended
        
        # 🔥 将打字机信号注入给后端
        self.orchestrator.on_text_stream = lambda text: self.text_stream_signal.emit(text)
        self.orchestrator.on_agent_status = lambda name, status, task="": self.agent_status_signal.emit({"name": name, "status": status, "task": task})

    def _run_generation(self):
        start_chapter = self.config.get("start_chapter", 1)
        self.orchestrator.run(start_chapter=start_chapter)

    def _on_chapter_complete(self, result: Dict[str, Any]):
        chapter = result.get("chapter", 0)
        word_count = len(result.get("content", ""))
        self.chapter_complete_signal.emit({"chapter": chapter, "word_count": word_count})
        self.progress_signal.emit(chapter, self.orchestrator.target_chapters)
        self._emit_emotion_curve(chapter)
        self.log_signal.emit(f"<span style='color: #00e676;'>[Success] 第 {chapter} 章生成完毕 ({word_count} 字)</span>")

    def _on_error(self, error: Dict[str, Any]):
        self.error_signal.emit(error.get("error", "Unknown error"))

    def _on_suspended(self, data: Dict[str, Any]):
        self.circuit_breaker_signal.emit({"tripped": True, "chapter": data.get("chapter", 0), "reason": data.get("reason", "Unknown")})

    def _emit_emotion_curve(self, chapter: int):
        expected, actual = [], []
        emotion_file = Path(self.project_dir) / "emotion_ledger.json"
        if emotion_file.exists():
            try:
                records = json.loads(emotion_file.read_text(encoding="utf-8")).get("records", [])
                actual = [r.get("net_debt", 0) for r in records]
            except: pass
        import math
        expected = [50 + 30 * math.sin(i / 3) for i in range(1, chapter + 1)]
        self.emotion_curve_signal.emit({"expected": expected, "actual": actual, "chapter": chapter})

    def stop(self):
        if self.orchestrator: self.orchestrator.stop()
        self.is_running = False