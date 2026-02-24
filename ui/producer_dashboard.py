"""
Producer Dashboard - 熔断可视化UI
PyQt6实现的生产者仪表板

功能：
1. 熔断状态实时显示
2. 情绪债务可视化
3. 章节进度追踪
4. 快速操作按钮
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# PyQt6 导入
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QProgressBar, QTextEdit, QFrame,
        QGroupBox, QScrollArea, QSplitter, QStatusBar
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
    from PyQt6.QtGui import QFont, QColor, QPalette
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available, using fallback UI")

from datetime import datetime


class CircuitBreakerMonitor:
    """熔断监控器 - 读取项目状态"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.rollback_log = self.project_dir / "rollback_log.json"
        self.suspended_file = self.project_dir / ".suspended.json"
        self.emotion_ledger = self.project_dir / "emotion_ledger.json"
        self.progress_file = self.project_dir / "novel-progress.txt"

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        status = {
            "is_suspended": self.suspended_file.exists(),
            "circuit_breaker_tripped": False,
            "total_rollbacks": 0,
            "early_rollbacks": 0,
            "emotion_debt": 0.0,
            "emotion_state": "正常",
            "current_chapter": 0,
            "total_chapters": 0,
            "recent_trend": []
        }

        # 读取熔断状态
        if status["is_suspended"]:
            try:
                data = json.loads(self.suspended_file.read_text(encoding="utf-8"))
                status["suspended_info"] = data
                status["circuit_breaker_tripped"] = True
            except:
                pass

        # 读取回滚日志
        if self.rollback_log.exists():
            try:
                data = json.loads(self.rollback_log.read_text(encoding="utf-8"))
                rollbacks = data.get("rollbacks", [])
                status["total_rollbacks"] = len(rollbacks)
                status["early_rollbacks"] = sum(1 for r in rollbacks if r.get("target", 0) <= 3)
            except:
                pass

        # 读取情绪账本
        if self.emotion_ledger.exists():
            try:
                data = json.loads(self.emotion_ledger.read_text(encoding="utf-8"))
                status["emotion_debt"] = data.get("net_debt", 0.0)
                records = data.get("records", [])
                if records:
                    status["recent_trend"] = [r.get("net_debt", 0) for r in records[-5:]]
                    latest_state = records[-1].get("state", "正常")
                    status["emotion_state"] = latest_state
            except:
                pass

        # 读取进度
        if self.progress_file.exists():
            try:
                content = self.progress_file.read_text(encoding="utf-8")
                for line in content.split('\n'):
                    if 'completed_chapters' in line.lower():
                        parts = line.split(':')
                        if len(parts) > 1:
                            status["current_chapter"] = int(parts[1].strip())
            except:
                pass

        return status


class FallbackConsoleUI:
    """控制台回退UI"""

    def __init__(self, project_dir: str):
        self.monitor = CircuitBreakerMonitor(project_dir)

    def refresh(self):
        """刷新显示"""
        status = self.monitor.get_status()

        print("\n" + "=" * 50)
        print("  NovelForge v4.0 Producer Dashboard")
        print("=" * 50)

        # 熔断状态
        if status["circuit_breaker_tripped"]:
            print("⚠️  熔断状态: 已触发！")
            if "suspended_info" in status:
                info = status["suspended_info"]
                print(f"   暂停章节: {info.get('suspended_chapter', 'N/A')}")
                print(f"   原因: {info.get('reason', 'N/A')}")
        else:
            print("✅ 熔断状态: 正常")

        # 回滚统计
        print(f"\n回滚统计:")
        print(f"  总回滚次数: {status['total_rollbacks']}")
        print(f"  前3章回滚: {status['early_rollbacks']}/3")

        # 情绪债务
        print(f"\n情绪状态:")
        print(f"  债务值: {status['emotion_debt']:.1f}")
        print(f"  状态: {status['emotion_state']}")
        if status["recent_trend"]:
            trend_str = " → ".join([f"{v:.0f}" for v in status["recent_trend"]])
            print(f"  趋势: {trend_str}")

        # 进度
        print(f"\n写作进度:")
        print(f"  当前章节: {status['current_chapter']}")
        print("=" * 50 + "\n")


class ProducerDashboard:
    """
    生产者仪表板

    如果PyQt6可用，显示图形界面
    否则显示控制台界面
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir

        if PYQT_AVAILABLE:
            self.ui = PyQtDashboard(project_dir)
        else:
            self.ui = FallbackConsoleUI(project_dir)

    def show(self):
        """显示仪表板"""
        if PYQT_AVAILABLE:
            self.ui.show()
        else:
            self.ui.refresh()

    def get_monitor(self):
        """获取监控器"""
        return self.ui.monitor if hasattr(self.ui, 'monitor') else None


if PYQT_AVAILABLE:
    class PyQtDashboard(QMainWindow):
        """PyQt6 仪表板"""

        def __init__(self, project_dir: str):
            super().__init__()
            self.project_dir = project_dir
            self.monitor = CircuitBreakerMonitor(project_dir)

            self.init_ui()
            self.setup_timer()

        def init_ui(self):
            """初始化UI"""
            self.setWindowTitle("NovelForge v4.0 - Producer Dashboard")
            self.setGeometry(100, 100, 800, 600)

            # 中心部件
            central = QWidget()
            self.setCentralWidget(central)

            layout = QVBoxLayout(central)

            # 标题
            title = QLabel("NovelForge v4.0 生产者仪表板")
            title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)

            # 熔断状态组
            circuit_group = self.create_circuit_breaker_group()
            layout.addWidget(circuit_group)

            # 情绪债务组
            emotion_group = self.create_emotion_group()
            layout.addWidget(emotion_group)

            # 进度组
            progress_group = self.create_progress_group()
            layout.addWidget(progress_group)

            # 操作按钮
            button_layout = QHBoxLayout()

            refresh_btn = QPushButton("刷新")
            refresh_btn.clicked.connect(self.refresh_status)
            button_layout.addWidget(refresh_btn)

            resume_btn = QPushButton("恢复写作")
            resume_btn.clicked.connect(self.resume_writing)
            button_layout.addWidget(resume_btn)

            clear_btn = QPushButton("清除暂停")
            clear_btn.clicked.connect(self.clear_suspension)
            button_layout.addWidget(clear_btn)

            layout.addLayout(button_layout)

            # 状态栏
            self.statusBar().showMessage("就绪")

        def create_circuit_breaker_group(self) -> QGroupBox:
            """创建熔断状态组"""
            group = QGroupBox("熔断状态")
            layout = QVBoxLayout()

            self.circuit_status_label = QLabel("✅ 正常")
            self.circuit_status_label.setFont(QFont("Microsoft YaHei", 12))
            layout.addWidget(self.circuit_status_label)

            self.rollback_label = QLabel("总回滚: 0 | 前3章回滚: 0/3")
            layout.addWidget(self.rollback_label)

            group.setLayout(layout)
            return group

        def create_emotion_group(self) -> QGroupBox:
            """创建情绪债务组"""
            group = QGroupBox("情绪债务")
            layout = QVBoxLayout()

            self.emotion_debt_label = QLabel("债务值: 0.0")
            self.emotion_debt_label.setFont(QFont("Microsoft YaHei", 12))
            layout.addWidget(self.emotion_debt_label)

            self.emotion_state_label = QLabel("状态: 正常")
            layout.addWidget(self.emotion_state_label)

            self.emotion_trend_label = QLabel("趋势: -")
            layout.addWidget(self.emotion_trend_label)

            self.emotion_progress = QProgressBar()
            self.emotion_progress.setRange(0, 100)
            self.emotion_progress.setValue(50)
            layout.addWidget(self.emotion_progress)

            group.setLayout(layout)
            return group

        def create_progress_group(self) -> QGroupBox:
            """创建进度组"""
            group = QGroupBox("写作进度")
            layout = QVBoxLayout()

            self.progress_label = QLabel("当前章节: 0")
            layout.addWidget(self.progress_label)

            self.chapter_progress = QProgressBar()
            self.chapter_progress.setRange(0, 100)
            self.chapter_progress.setValue(0)
            layout.addWidget(self.chapter_progress)

            group.setLayout(layout)
            return group

        def setup_timer(self):
            """设置定时刷新"""
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_status)
            self.timer.start(5000)  # 5秒刷新

        def refresh_status(self):
            """刷新状态"""
            status = self.monitor.get_status()

            # 熔断状态
            if status["circuit_breaker_tripped"]:
                self.circuit_status_label.setText("⚠️ 熔断已触发！")
                self.circuit_status_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.circuit_status_label.setText("✅ 正常")
                self.circuit_status_label.setStyleSheet("color: green;")

            self.rollback_label.setText(
                f"总回滚: {status['total_rollbacks']} | 前3章回滚: {status['early_rollbacks']}/3"
            )

            # 情绪状态
            debt = status["emotion_debt"]
            self.emotion_debt_label.setText(f"债务值: {debt:.1f}")
            self.emotion_state_label.setText(f"状态: {status['emotion_state']}")

            # 情绪趋势
            trend = status["recent_trend"]
            if trend:
                trend_str = " → ".join([f"{v:.0f}" for v in trend])
                self.emotion_trend_label.setText(f"趋势: {trend_str}")

            # 情绪进度条
            # 0-100 映射情绪状态
            progress_value = int(50 + debt / 2)  # 0 debt = 50, 100 debt = 100
            progress_value = max(0, min(100, progress_value))
            self.emotion_progress.setValue(progress_value)

            # 进度
            current = status["current_chapter"]
            self.progress_label.setText(f"当前章节: {current}")

            self.statusBar().showMessage(f"最后更新: {datetime.now().strftime('%H:%M:%S')}")

        def resume_writing(self):
            """恢复写作"""
            print("恢复写作功能待实现")

        def clear_suspension(self):
            """清除暂停状态"""
            suspended_file = Path(self.project_dir) / ".suspended.json"
            if suspended_file.exists():
                suspended_file.unlink()
                self.refresh_status()
                self.statusBar().showMessage("暂停状态已清除")


def run_dashboard(project_dir: str):
    """运行仪表板"""
    if PYQT_AVAILABLE:
        app = QApplication(sys.argv)
        window = PyQtDashboard(project_dir)
        window.show()
        sys.exit(app.exec())
    else:
        # 控制台模式
        ui = FallbackConsoleUI(project_dir)
        ui.refresh()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        project_dir = "novels/test"

    run_dashboard(project_dir)
