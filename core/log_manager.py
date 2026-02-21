"""
日志管理器
记录所有操作日志到文件
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys


class LogManager:
    """日志管理器 - 统一管理应用日志"""

    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        初始化日志管理器

        Args:
            log_dir: 日志文件存放目录
            log_level: 日志级别
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 创建日志文件路径
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"novel_generator_{current_date}.log"

        # 配置日志记录器
        self.logger = logging.getLogger("NovelGenerator")
        self.logger.setLevel(log_level)

        # 清除现有处理器（避免重复）
        self.logger.handlers = []

        # 文件处理器
        file_handler = logging.FileHandler(
            self.log_file,
            encoding="utf-8",
            mode="a",  # 追加模式
        )
        file_handler.setLevel(log_level)

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # 格式化器
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 记录初始化信息
        self.info("=" * 60)
        self.info("日志系统初始化完成")
        self.info(f"日志文件: {self.log_file}")
        self.info("=" * 60)

    def _get_caller_info(self) -> str:
        """获取调用者信息"""
        import inspect

        frame = inspect.currentframe()
        # 回溯到调用者的调用者（跳过 _get_caller_info 和日志方法本身）
        try:
            for _ in range(3):
                frame = frame.f_back
            if frame:
                filename = Path(frame.f_code.co_filename).name
                lineno = frame.f_lineno
                func_name = frame.f_code.co_name
                return f"[{filename}:{lineno}:{func_name}]"
        finally:
            del frame
        return ""

    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(f"{self._get_caller_info()} {message}")

    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(f"{self._get_caller_info()} {message}")

    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(f"{self._get_caller_info()} {message}")

    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(f"{self._get_caller_info()} {message}")

    def critical(self, message: str):
        """记录严重错误日志"""
        self.logger.critical(f"{self._get_caller_info()} {message}")

    def log_operation(
        self,
        operation: str,
        details: Optional[str] = None,
        user: str = "system",
        success: bool = True,
    ):
        """
        记录操作日志

        Args:
            operation: 操作名称
            details: 操作详情
            user: 操作用户
            success: 是否成功
        """
        status = "[OK] 成功" if success else "[FAIL] 失败"
        message = f"[操作] {operation} | {status} | 用户: {user}"
        if details:
            message += f" | 详情: {details}"
        self.info(message)

    def log_model_selection(
        self, model_id: str, provider: str, temperature: float, max_tokens: int
    ):
        """记录模型选择"""
        self.info(
            f"[模型选择] 模型: {model_id} | 提供商: {provider} | "
            f"Temperature: {temperature} | Max Tokens: {max_tokens}"
        )

    def log_api_key_save(self, key_name: str, success: bool):
        """记录API密钥保存"""
        status = "成功" if success else "失败"
        self.info(f"[API密钥] 保存 {key_name}: {status}")

    def log_project_creation(self, project_name: str, config: dict):
        """记录项目创建"""
        self.info(
            f"[项目创建] 名称: {project_name} | "
            f"类型: {config.get('genre', '未知')} | "
            f"章节数: {config.get('target_chapters', 0)}"
        )

    def log_chapter_generation(
        self, project_name: str, chapter_num: int, word_count: int, success: bool
    ):
        """记录章节生成"""
        status = "成功" if success else "失败"
        self.info(
            f"[章节生成] 项目: {project_name} | "
            f"章节: {chapter_num} | 字数: {word_count} | {status}"
        )

    def log_agent_execution(
        self, agent_name: str, task: str, duration: float, success: bool
    ):
        """记录智能体执行"""
        status = "成功" if success else "失败"
        self.info(
            f"[智能体] {agent_name} | 任务: {task} | 耗时: {duration:.2f}s | {status}"
        )

    def log_error_with_traceback(self, error: Exception, context: str = ""):
        """记录错误和堆栈跟踪"""
        import traceback

        self.error(f"[错误] {context}: {str(error)}")
        self.error(f"堆栈跟踪:\n{traceback.format_exc()}")

    def get_recent_logs(self, lines: int = 100) -> str:
        """获取最近的日志内容"""
        if not self.log_file.exists():
            return "暂无日志"

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except Exception as e:
            return f"读取日志失败: {e}"

    def get_log_files(self) -> list:
        """获取所有日志文件列表"""
        if not self.log_dir.exists():
            return []

        log_files = sorted(
            [f for f in self.log_dir.glob("*.log")],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        return log_files


# 全局日志管理器实例
_log_manager: Optional[LogManager] = None


def get_logger() -> LogManager:
    """获取日志管理器实例（单例模式）"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def init_logger(log_dir: str = "logs") -> LogManager:
    """初始化日志管理器"""
    global _log_manager
    _log_manager = LogManager(log_dir)
    return _log_manager
