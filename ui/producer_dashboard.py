"""
Producer Dashboard - 赛博朋克UI重构
NovelForge v4.0 制片人控制台

功能：
1. 左侧：Agent 员工矩阵（带状态指示灯）
2. 中间：pyqtgraph 情绪波浪图（蓝线=预期，红线=实际）
3. 右侧：实时裁决日志（HTML彩色格式）
4. 后台：QThread 工作线程，避免UI卡死
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# 导入工作线程
try:
    from ui.worker_thread import GenerationWorker
except ImportError:
    GenerationWorker = None

# PyQt6 导入
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QFrame, QGroupBox,
        QScrollArea, QSplitter, QStatusBar, QSlider, QComboBox,
        QSpinBox, QCheckBox, QProgressBar, QDialog, QFormLayout,
        QLineEdit, QTextBrowser, QMessageBox, QTabWidget
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
    from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available")

# pyqtgraph 导入
try:
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    print("Warning: pyqtgraph not available")

from datetime import datetime


# ============================================================================
# 赛博朋克配色方案
# ============================================================================
class CyberpunkTheme:
    """赛博朋克主题配色"""

    # 背景色
    BG_DARK = "#0a0a0f"
    BG_MEDIUM = "#12121a"
    BG_LIGHT = "#1a1a25"

    # 前景色
    FG_PRIMARY = "#00ffff"      # 青色 (主色)
    FG_SECONDARY = "#ff00ff"    # 洋红 (辅色)
    FG_WARNING = "#ffaa00"      # 橙色 (警告)
    FG_DANGER = "#ff3366"       # 红色 (危险)
    FG_SUCCESS = "#00ff66"      # 绿色 (成功)

    # 文字色
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8888aa"
    TEXT_DIM = "#555566"

    # 边框色
    BORDER_COLOR = "#333355"


# ============================================================================
# 项目初始化对话框
# ============================================================================
class ProjectSetupDialog(QDialog):
    """新建项目档案对话框"""

    # 题材类型与监控指标映射
    GENRE_METRICS = {
        "修仙": ["realm", "spiritual_power", "tribulation_count"],
        "都市": ["reputation", "wealth", "relationship_level"],
        "赛博朋克": ["cyber_psychosis_level", "credits", "augmentation_level"],
        "玄幻": ["realm", "magic_power", "artifact_rank"],
        "科幻": ["tech_level", "resources", "alliance_count"],
        "悬疑": ["clue_count", "danger_level", "truth_revealed"],
        "历史": ["influence", "wealth", "army_size"],
    }

    # 题材类型列表
    GENRE_TYPES = list(GENRE_METRICS.keys()) + ["其他"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_config = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("新建项目档案 - Project Setup")
        self.setFixedSize(500, 480)
        self.setModal(True)

        # 赛博朋克风格
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                padding: 6px;
                font-family: Consolas;
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 4px;
                padding: 10px 20px;
                font-family: Consolas;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        # 标题
        title = QLabel("📁 NEW PROJECT ARCHIVE")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Initialize your novel project")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(15)

        # 表单布局
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 书名
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., 星辰变, 斗破苍穹, 赛博人生...")
        form.addRow("📖 书名:", self.title_edit)

        # 题材类型
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(self.GENRE_TYPES)
        self.genre_combo.currentTextChanged.connect(self.on_genre_changed)
        form.addRow("🎭 题材:", self.genre_combo)

        # 主角名
        self.protagonist_edit = QLineEdit()
        self.protagonist_edit.setPlaceholderText("e.g., 秦羽, 萧炎, 李燃...")
        form.addRow("👤 主角:", self.protagonist_edit)

        # 目标章节数
        self.chapters_spin = QSpinBox()
        self.chapters_spin.setRange(1, 10000)
        self.chapters_spin.setValue(50)
        self.chapters_spin.setToolTip("Recommended: 50-200 for first draft")
        form.addRow("📑 目标章节:", self.chapters_spin)

        layout.addLayout(form)

        # 核心设定（多行文本）
        settings_label = QLabel("⚙️ 核心设定:")
        settings_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(settings_label)

        self.settings_edit = QTextEdit()
        self.settings_edit.setPlaceholderText(
            "描述世界观、主角目标、核心冲突等...\n"
            "例如：灵气复苏时代，主角从废物逆袭成大帝"
        )
        self.settings_edit.setMaximumHeight(80)
        layout.addWidget(self.settings_edit)

        # 监控指标预览
        self.metrics_label = QLabel()
        self.metrics_label.setFont(QFont("Consolas", 8))
        self.metrics_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")
        self.on_genre_changed("修仙")  # 默认显示修仙指标
        layout.addWidget(self.metrics_label)

        layout.addStretch()

        # 按钮区域
        btn_layout = QHBoxLayout()

        # 取消按钮
        cancel_btn = QPushButton("✕ CANCEL")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        # 确认按钮
        self.confirm_btn = QPushButton("▶ INITIALIZE WORLD")
        self.confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)
        self.confirm_btn.clicked.connect(self.on_confirm)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)

    def on_genre_changed(self, genre: str):
        """题材变化时更新监控指标"""
        metrics = self.GENRE_METRICS.get(genre, ["reputation", "wealth", "progress"])
        self.metrics_label.setText(f"监控指标: {', '.join(metrics)}")

    def on_confirm(self):
        """确认创建项目"""
        # 验证输入
        title = self.title_edit.text().strip()
        genre = self.genre_combo.currentText()
        protagonist = self.protagonist_edit.text().strip()
        chapters = self.chapters_spin.value()
        settings = self.settings_edit.toPlainText().strip()

        if not title:
            QMessageBox.warning(
                self, "输入错误",
                "请输入小说书名",
                QMessageBox.StandardButton.Ok
            )
            self.title_edit.setFocus()
            return

        if not protagonist:
            QMessageBox.warning(
                self, "输入错误",
                "请输入主角姓名",
                QMessageBox.StandardButton.Ok
            )
            self.protagonist_edit.setFocus()
            return

        # 生成项目配置
        self.project_config = {
            "title": title,
            "genre": genre,
            "protagonist": protagonist,
            "target_chapters": chapters,
            "settings": settings or f"{genre}类型小说，主角{protagonist}",
            "metrics": self.GENRE_METRICS.get(genre, ["reputation", "wealth", "progress"]),
            "created_at": datetime.now().isoformat(),
            "version": "4.0"
        }

        self.accept()

    def get_project_config(self) -> Optional[Dict[str, Any]]:
        """获取项目配置"""
        return self.project_config


# ============================================================================
# Agent 工牌组件（赛博朋克ID卡风格）
# ============================================================================
class AgentCard(QFrame):
    """Agent 员工工牌 - 赛博朋克ID卡风格"""

    # 状态颜色映射
    STATUS_COLORS = {
        "idle": "#4CAF50",        # 绿色
        "thinking": "#00BCD4",    # 青色
        "writing": "#2196F3",     # 亮蓝色
        "auditing": "#9C27B0",    # 紫色
        "conflict": "#F44336",    # 红色
        "error": "#F44336",       # 红色
        "suspended": "#ff9800",   # 橙色
    }

    def __init__(self, name: str, role: str, emoji: str = "🤖", parent=None):
        super().__init__(parent)
        self.agent_name = name
        self.agent_role = role
        self.agent_emoji = emoji
        self.current_task = ""

        self.init_ui()
        self.set_status("idle")

    def init_ui(self):
        """初始化UI - 赛博朋克ID卡风格"""
        self.setFixedSize(190, 85)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a25;
                border: 1px solid #333355;
                border-radius: 6px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧霓虹边框（4px宽）
        self.left_border = QFrame()
        self.left_border.setFixedWidth(4)
        self.left_border.setStyleSheet(f"""
            QFrame {{
                background-color: {self.STATUS_COLORS["idle"]};
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
            }}
        """)
        layout.addWidget(self.left_border)

        # 右侧内容区
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 8, 10, 8)
        content_layout.setSpacing(2)

        # 顶部：Emoji + Agent名称
        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)

        self.emoji_label = QLabel(self.agent_emoji)
        self.emoji_label.setStyleSheet("font-size: 14px;")
        top_layout.addWidget(self.emoji_label)

        self.name_label = QLabel(self.agent_name)
        self.name_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.name_label.setStyleSheet("color: #ffffff;")
        top_layout.addWidget(self.name_label)

        top_layout.addStretch()
        content_layout.addLayout(top_layout)

        # 中部：职位角色
        self.role_label = QLabel(self.agent_role)
        self.role_label.setFont(QFont("Consolas", 8))
        self.role_label.setStyleSheet("color: #8888aa;")
        content_layout.addWidget(self.role_label)

        # 底部：状态指示灯 + 状态文字 + 任务信息
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(6)

        # 状态指示灯
        self.status_indicator = QLabel("●")
        self.status_indicator.setFixedWidth(16)
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {self.STATUS_COLORS["idle"]};
                font-size: 12px;
            }}
        """)
        bottom_layout.addWidget(self.status_indicator)

        # 状态文字
        self.status_label = QLabel("IDLE")
        self.status_label.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #4CAF50;")
        bottom_layout.addWidget(self.status_label)

        bottom_layout.addStretch()

        # 任务信息（可选，显示具体任务）
        self.task_label = QLabel("")
        self.task_label.setFont(QFont("Consolas", 7))
        self.task_label.setStyleSheet("color: #555566;")
        self.task_label.setMaximumWidth(80)
        self.task_label.setWordWrap(True)
        bottom_layout.addWidget(self.task_label)

        content_layout.addLayout(bottom_layout)

        layout.addLayout(content_layout, stretch=1)

    def set_status(self, status: str, task: str = ""):
        """设置状态

        Args:
            status: 状态字符串 (idle, thinking, writing, auditing, conflict, error, suspended)
            task: 可选的具体任务信息
        """
        status = status.lower()
        self.current_task = task

        # 获取状态颜色
        color = self.STATUS_COLORS.get(status, self.STATUS_COLORS["idle"])

        # 状态文字映射
        status_text_map = {
            "idle": "IDLE",
            "thinking": "THINKING",
            "writing": "WRITING",
            "auditing": "AUDITING",
            "conflict": "CONFLICT",
            "error": "ERROR",
            "suspended": "SUSPENDED",
            "active": "ACTIVE",
        }
        status_text = status_text_map.get(status, "IDLE")

        # 更新霓虹边框颜色
        self.left_border.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
            }}
        """)

        # 更新状态指示灯
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
            }}
        """)

        # 更新状态文字
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 8px;
                font-weight: bold;
            }}
        """)

        # 更新任务信息
        if task:
            # 截断过长的任务描述
            display_task = task[:15] + "..." if len(task) > 15 else task
            self.task_label.setText(display_task)
            self.task_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 7px;
                }}
            """)


# ============================================================================
# Agent 矩阵面板
# ============================================================================
class AgentMatrixPanel(QWidget):
    """Agent 员工矩阵"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("🤖 AGENT MATRIX")
        title.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Agent Workers Status")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Agent 列表
        self.agent_cards = {}

        # v4.0 核心Agent（带Emoji）
        self.agents = {
            "InitializerAgent": AgentCard("InitializerAgent", "初始建组设定", "🏗️"),
            "PromptAssembler": AgentCard("PromptAssembler", "中控(指令聚合)", "🎛️"),
            "ElasticArchitect": AgentCard("ElasticArchitect", "架构(迷雾开图)", "🗺️"),
            "EmotionWriter": AgentCard("EmotionWriter", "写手(场景生成)", "✍️"),
            "PayoffAuditor": AgentCard("PayoffAuditor", "审计(情绪差核算)", "🧮"),
            "ConsistencyGuardian": AgentCard("ConsistencyGuardian", "守护(一致性检测)", "🛡️"),
            "CreativeDirector": AgentCard("CreativeDirector", "总监(仲裁回滚)", "👑"),
            "StyleAnchor": AgentCard("StyleAnchor", "文风(特征对齐)", "🎨"),
            "WorldBible": AgentCard("WorldBible", "圣经(事件溯源)", "📚"),
            "EmotionTracker": AgentCard("EmotionTracker", "债务(Python计算)", "📉"),
        }

        for name, card in self.agents.items():
            self.agent_cards[name] = card
            layout.addWidget(card)

        layout.addStretch()

    def update_agent_status(self, name: str, status: str, task: str = ""):
        """更新Agent状态

        Args:
            name: Agent名称
            status: 状态字符串
            task: 可选的具体任务信息
        """
        if name in self.agent_cards:
            self.agent_cards[name].set_status(status, task)


# ============================================================================
# 情绪波浪图面板
# ============================================================================
class EmotionWavePanel(QWidget):
    """情绪波浪图面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("📈 EMOTION WAVE")
        title.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Expected vs Actual Tension")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        if PYQTGRAPH_AVAILABLE:
            # 创建图表
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground(CyberpunkTheme.BG_MEDIUM)

            # 配置图表
            self.plot_widget.setLabel('bottom', 'Chapter')
            self.plot_widget.setLabel('left', 'Tension')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

            # 预期曲线（蓝色）
            self.expected_curve = self.plot_widget.plot(
                [], [],
                pen=pg.mkPen(color=CyberpunkTheme.FG_PRIMARY, width=2),
                name='Expected'
            )

            # 实际曲线（红色）
            self.actual_curve = self.plot_widget.plot(
                [], [],
                pen=pg.mkPen(color=CyberpunkTheme.FG_DANGER, width=2),
                name='Actual'
            )

            # 图例
            self.plot_widget.addLegend()

            # 设置Y轴范围
            self.plot_widget.setYRange(0, 120)

            layout.addWidget(self.plot_widget)
        else:
            # 备用显示
            self.fallback_label = QLabel("pyqtgraph not available")
            self.fallback_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
            layout.addWidget(self.fallback_label)

        # 统计信息
        stats_layout = QHBoxLayout()

        self.chapter_label = QLabel("Chapter: 0/0")
        self.chapter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY};")
        stats_layout.addWidget(self.chapter_label)

        stats_layout.addStretch()

        self.debt_label = QLabel("Debt: 0.0")
        self.debt_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")
        stats_layout.addWidget(self.debt_label)

        layout.addLayout(stats_layout)

    def update_curve(self, expected: List[float], actual: List[float], chapter: int, total: int):
        """更新曲线"""
        if PYQTGRAPH_AVAILABLE:
            # 更新数据
            x = list(range(1, len(expected) + 1))

            self.expected_curve.setData(x, expected)
            self.actual_curve.setData(x, actual)

            # 更新统计
            self.chapter_label.setText(f"Chapter: {chapter}/{total}")

            # 计算当前债务
            if actual:
                current_debt = actual[-1]
                self.debt_label.setText(f"Debt: {current_debt:.1f}")

                # 根据债务值改变颜色
                if current_debt > 70:
                    color = CyberpunkTheme.FG_DANGER
                elif current_debt > 40:
                    color = CyberpunkTheme.FG_WARNING
                else:
                    color = CyberpunkTheme.FG_SUCCESS

                self.debt_label.setStyleSheet(f"color: {color};")


# ============================================================================
# 实时日志面板
# ============================================================================
class LogPanel(QWidget):
    """实时日志面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QTextEdit {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                font-family: Consolas, monospace;
                font-size: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("📋 ARBITRATION LOG")
        title.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_SECONDARY};")
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Real-time Decision Log")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # 日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def append_log(self, message: str, level: str = "info"):
        """追加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 颜色映射
        colors = {
            "info": CyberpunkTheme.TEXT_PRIMARY,
            "warning": CyberpunkTheme.FG_WARNING,
            "error": CyberpunkTheme.FG_DANGER,
            "success": CyberpunkTheme.FG_SUCCESS,
            "system": CyberpunkTheme.FG_PRIMARY,
        }

        color = colors.get(level, CyberpunkTheme.TEXT_PRIMARY)

        # HTML格式化
        html = f'<span style="color: {CyberpunkTheme.TEXT_DIM};">[{timestamp}]</span> '
        html += f'<span style="color: {color};">{message}</span><br>'

        self.log_text.append(html)

        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def clear(self):
        """清空日志"""
        self.log_text.clear()


# ============================================================================
# 前期筹备面板 (Pre-Production)
# ============================================================================
class PreProductionPanel(QWidget):
    """
    前期筹备面板

    功能：
    1. 大纲编辑区域 (outline.md)
    2. 人物设定编辑区域 (characters.json)
    3. 资深编辑诊断结果
    4. 生成设置、评估、开始写作按钮
    """

    # 信号定义
    generate_settings = pyqtSignal()  # 触发初始化
    evaluate_settings = pyqtSignal()  # 触发评估
    approve_and_start = pyqtSignal()  # 批准并开始写作
    evaluation_complete = pyqtSignal(str)  # 评估完成信号

    def __init__(self, project_dir: str = None, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir or "novels/default"
        self.init_ui()
        self.load_existing_files()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QTextEdit, QTextBrowser {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                font-family: Consolas;
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 4px;
                padding: 12px 24px;
                font-family: Consolas;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
            }}
            QPushButton:pressed {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("📝 前期筹备室 (Pre-Production)")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY}; padding: 10px;")
        layout.addWidget(title)

        # 大纲和人物设定区域（上下布局）
        content_splitter = QSplitter(Qt.Orientation.Vertical)

        # 大纲编辑区
        outline_group = QGroupBox("📖 故事大纲 (outline.md)")
        outline_layout = QVBoxLayout()
        self.outline_text = QTextEdit()
        self.outline_text.setPlaceholderText("在这里编辑故事大纲...\n\n包括：\n- 故事主线\n- 情节点\n- 章节规划")
        self.outline_text.setMinimumHeight(200)
        outline_layout.addWidget(self.outline_text)
        outline_group.setLayout(outline_layout)
        content_splitter.addWidget(outline_group)

        # 人物设定区
        chars_group = QGroupBox("👤 人物设定 (characters.json)")
        chars_layout = QVBoxLayout()
        self.chars_text = QTextEdit()
        self.chars_text.setPlaceholderText("在这里编辑人物设定...\n\n主角信息：\n- 姓名、年龄\n- 性格特点\n- 背景故事\n- 能力设定")
        self.chars_text.setMinimumHeight(150)
        chars_layout.addWidget(self.chars_text)
        chars_group.setLayout(chars_layout)
        content_splitter.addWidget(chars_group)

        # 资深编辑诊断区
        eval_group = QGroupBox("📋 资深编辑诊断 (Senior Editor Evaluation)")
        eval_layout = QVBoxLayout()
        self.eval_text = QTextBrowser()
        self.eval_text.setPlaceholderText("点击「评估设置」按钮获取资深编辑的诊断建议...")
        self.eval_text.setMinimumHeight(100)
        eval_layout.addWidget(self.eval_text)
        eval_group.setLayout(eval_layout)
        content_splitter.addWidget(eval_group)

        layout.addWidget(content_splitter, stretch=1)

        # 按钮区
        button_layout = QHBoxLayout()

        self.gen_btn = QPushButton("1️⃣ 生成设置")
        self.gen_btn.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.gen_btn.clicked.connect(self.on_generate_settings)
        button_layout.addWidget(self.gen_btn)

        self.eval_btn = QPushButton("2️⃣ 评估设置")
        self.eval_btn.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.eval_btn.clicked.connect(self.on_evaluate_settings)
        button_layout.addWidget(self.eval_btn)

        self.start_btn = QPushButton("3️⃣ ✅ 批准并开始写作")
        self.start_btn.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: {CyberpunkTheme.BG_DARK};
                border: 2px solid {CyberpunkTheme.FG_SUCCESS};
            }}
            QPushButton:hover {{
                background-color: #00cc55;
            }}
        """)
        self.start_btn.clicked.connect(self.on_approve_and_start)
        button_layout.addWidget(self.start_btn)

        layout.addLayout(button_layout)

    def load_existing_files(self):
        """加载已存在的大纲和人物文件"""
        project_path = Path(self.project_dir)

        # 加载大纲
        outline_file = project_path / "outline.md"
        if outline_file.exists():
            try:
                self.outline_text.setText(outline_file.read_text(encoding="utf-8"))
            except:
                pass

        # 加载人物
        chars_file = project_path / "characters.json"
        if chars_file.exists():
            try:
                self.chars_text.setText(chars_file.read_text(encoding="utf-8"))
            except:
                pass

    def save_to_disk(self):
        """保存编辑内容到磁盘"""
        project_path = Path(self.project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        # 保存大纲
        outline_file = project_path / "outline.md"
        outline_file.write_text(self.outline_text.toPlainText(), encoding="utf-8")

        # 保存人物
        chars_file = project_path / "characters.json"
        chars_file.write_text(self.chars_text.toPlainText(), encoding="utf-8")

    def on_generate_settings(self):
        """生成设置按钮点击"""
        self.gen_btn.setEnabled(False)
        self.gen_btn.setText("生成中...")
        self.generate_settings.emit()

    def on_evaluate_settings(self):
        """评估设置按钮点击"""
        self.eval_btn.setEnabled(False)
        self.eval_btn.setText("评估中...")
        self.evaluate_settings.emit()

    def on_approve_and_start(self):
        """批准并开始写作"""
        # 先保存编辑的内容
        self.save_to_disk()
        self.approve_and_start.emit()

    def set_generation_complete(self):
        """设置生成完成状态"""
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("1️⃣ 生成设置")

    def set_evaluation_result(self, result: str):
        """显示评估结果"""
        self.eval_btn.setEnabled(True)
        self.eval_btn.setText("2️⃣ 评估设置")
        self.eval_text.setHtml(f"<pre style='color: {CyberpunkTheme.TEXT_PRIMARY};'>{result}</pre>")

    def set_error(self, message: str):
        """显示错误"""
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("1️⃣ 生成设置")
        self.eval_text.setHtml(f"<span style='color: {CyberpunkTheme.FG_DANGER};'>{message}</span>")


# ============================================================================
# 熔断状态面板
# ============================================================================
class CircuitBreakerPanel(QWidget):
    """熔断状态面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # 状态图标
        self.status_icon = QLabel("🛡️")
        self.status_icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.status_icon)

        # 状态文字
        self.status_label = QLabel("CIRCUIT BREAKER")
        self.status_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # 计数器
        self.counter_label = QLabel("Rollbacks: 0")
        self.counter_label.setFont(QFont("Consolas", 9))
        self.counter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(self.counter_label)

    def set_tripped(self, chapter: int, reason: str, rollbacks: int):
        """设置熔断触发"""
        self.status_icon.setText("⚠️")
        self.status_label.setText(f"TRIGGERED @ CH.{chapter}")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER};")
        self.counter_label.setText(f"Rollbacks: {rollbacks}")

    def set_normal(self, rollbacks: int):
        """设置正常状态"""
        self.status_icon.setText("🛡️")
        self.status_label.setText("CIRCUIT BREAKER")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        self.counter_label.setText(f"Rollbacks: {rollbacks}")


# ============================================================================
# 主窗口
# ============================================================================
class ProducerDashboard(QMainWindow):
    """
    制片人仪表板主窗口

    三栏布局：
    - 左侧：Agent工牌矩阵
    - 中间：情绪波浪图
    - 右侧：实时日志
    """

    # 信号定义（供外部调用）
    start_generation = pyqtSignal(dict)  # 开始生成信号

    def __init__(self, project_dir: str = None):
        super().__init__()

        self.project_dir = project_dir or "novels/default"
        self.worker = None
        self.project_config = None

        # 读取项目配置
        self.load_project_config()

        self.init_ui()

        # 显示项目信息
        self.display_project_info()

    def init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("NovelForge v4.0 - Producer Dashboard")
        self.setGeometry(100, 100, 1400, 800)

        # 设置深色主题
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 4px;
                padding: 8px 16px;
                font-family: Consolas;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
            }}
            QPushButton:pressed {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
            QTabWidget::pane {{
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QTabBar::tab {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                padding: 8px 16px;
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QTabBar::tab:selected {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)

        # 中心部件 - 使用TabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab 1: 前期筹备
        self.preproduction_panel = PreProductionPanel(self.project_dir)
        self.preproduction_panel.generate_settings.connect(self.on_generate_settings)
        self.preproduction_panel.evaluate_settings.connect(self.on_evaluate_settings)
        self.preproduction_panel.approve_and_start.connect(self.on_approve_and_start)
        self.tabs.addTab(self.preproduction_panel, "📝 前期筹备 (Pre-Production)")

        # Tab 2: 生产监控 (现有的UI)
        production_widget = QWidget()
        production_layout = QHBoxLayout(production_widget)
        production_layout.setContentsMargins(5, 5, 5, 5)

        # 创建三个面板
        self.agent_panel = AgentMatrixPanel()
        self.emotion_panel = EmotionWavePanel()
        self.log_panel = LogPanel()

        # 左侧面板容器
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.agent_panel)

        # 添加控制按钮
        self.setup_control_buttons(left_layout)

        # 中间+右侧布局
        center_layout = QVBoxLayout()

        # 熔断状态栏
        self.circuit_breaker = CircuitBreakerPanel()
        center_layout.addWidget(self.circuit_breaker)

        # 情绪波浪图
        center_layout.addWidget(self.emotion_panel, stretch=3)

        # 右侧日志（通过splitter）
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.log_panel)

        # 使用splitter分割中间和右侧
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(self.emotion_panel)
        splitter.addWidget(right_container)

        splitter.setStretchFactor(0, 1)  # 左侧
        splitter.setStretchFactor(1, 2)  # 中间
        splitter.setStretchFactor(2, 1)  # 右侧

        production_layout.addWidget(splitter)

        # 添加到TabWidget
        self.tabs.addTab(production_widget, "🎬 生产监控 (Production Dashboard)")

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Click 'Start Generation' to begin")

    def load_project_config(self):
        """加载项目配置"""
        config_path = Path(self.project_dir) / "project_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.project_config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load project config: {e}")
                self.project_config = None
        else:
            self.project_config = None

    def display_project_info(self):
        """显示项目信息到日志"""
        if self.project_config:
            title = self.project_config.get("title", "Unknown")
            genre = self.project_config.get("genre", "Unknown")
            protagonist = self.project_config.get("protagonist", "Unknown")
            chapters = self.project_config.get("target_chapters", 0)

            self.log_panel.append_log(f"=== PROJECT LOADED ===", "system")
            self.log_panel.append_log(f"Title: {title}", "info")
            self.log_panel.append_log(f"Genre: {genre}", "info")
            self.log_panel.append_log(f"Protagonist: {protagonist}", "info")
            self.log_panel.append_log(f"Target Chapters: {chapters}", "info")

            metrics = self.project_config.get("metrics", [])
            if metrics:
                self.log_panel.append_log(f"Metrics: {', '.join(metrics)}", "info")
            self.log_panel.append_log(f"=====================", "system")
        else:
            self.log_panel.append_log("No project config found - starting in demo mode", "warning")

    def setup_control_buttons(self, layout):
        """设置控制按钮"""
        layout.addSpacing(20)

        # 开始按钮
        self.start_btn = QPushButton("▶ START")
        self.start_btn.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.start_btn.clicked.connect(self.on_start_generation)
        layout.addWidget(self.start_btn)

        # 暂停按钮
        self.pause_btn = QPushButton("⏸ PAUSE")
        self.pause_btn.setFont(QFont("Consolas", 10))
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.on_pause_generation)
        layout.addWidget(self.pause_btn)

        # 恢复按钮
        self.resume_btn = QPushButton("⏩ RESUME")
        self.resume_btn.setFont(QFont("Consolas", 10))
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self.on_resume_generation)
        layout.addWidget(self.resume_btn)

        # 清空日志
        self.clear_btn = QPushButton("🗑 CLEAR LOG")
        self.clear_btn.setFont(QFont("Consolas", 9))
        self.clear_btn.clicked.connect(self.log_panel.clear)
        layout.addWidget(self.clear_btn)

        layout.addStretch()

    def on_start_generation(self):
        """开始生成"""
        if GenerationWorker is None:
            self.log_panel.append_log("ERROR: GenerationWorker not available", "error")
            return

        self.log_panel.append_log("Initializing generation task...", "system")

        # 获取项目配置
        config = self.project_config or {}
        target_chapters = config.get("target_chapters", 10)

        # 创建工作线程
        self.log_panel.append_log(f"Creating worker for {target_chapters} chapters...", "info")
        self.worker = GenerationWorker(self.project_dir, {
            "target_chapters": target_chapters,
            "checkpoint_interval": 5
        })

        # 连接信号
        self.connect_worker(self.worker)

        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

        # 更新Agent状态
        self.agent_panel.update_agent_status("EmotionWriter", "thinking")

        # 启动worker
        self.worker.start()

        self.status_bar.showMessage("Generating...")

    def on_generate_settings(self):
        """从前期筹备面板触发生成设置"""
        self.log_panel.append_log("Generating project settings (outline & characters)...", "system")

        # 切换到生产监控标签页
        self.tabs.setCurrentIndex(1)

        # 调用on_start_generation来初始化项目
        self.on_start_generation()

    def on_evaluate_settings(self):
        """从前期筹备面板触发评估"""
        self.log_panel.append_log("Running senior editor evaluation...", "system")

        # 禁用按钮
        self.preproduction_panel.eval_btn.setEnabled(False)
        self.preproduction_panel.eval_btn.setText("评估中...")

        # 连接评估完成信号
        self.preproduction_panel.evaluation_complete.connect(self._on_evaluation_complete)

        # 在后台线程运行评估
        import threading
        eval_thread = threading.Thread(target=self._run_evaluation)
        eval_thread.start()

    def _run_evaluation(self):
        """运行评估（后台线程）"""
        try:
            # 获取大纲和人物设定
            outline = self.preproduction_panel.outline_text.toPlainText()
            characters = self.preproduction_panel.chars_text.toPlainText()

            if not outline and not characters:
                self.preproduction_panel.evaluation_complete.emit("Error: 请先生成或填写大纲和人物设定！")
                return

            # 构建评估Prompt
            system_prompt = """你是一位拥有8年从业经验的起点金牌资深编辑「锐评官」。你的职责是对网文进行多维度锐评，包含开篇诊断、节奏把控、人设审计、战力审计、商业性评估。

请以专业编辑的视角，对作者提供的大纲和人物设定进行严格评估。
输出要求：
1. 使用中文
2. 评分要客观、严格
3. 必须给出具体的改进建议
4. 发现问题时用【问题】标注
5. 给出总分（满分100分）"""

            user_prompt = f"""请评估以下小说项目：

【故事大纲】
{outline if outline else '未提供大纲'}

【人物设定】
{characters if characters else '未提供人物设定'}

请从以下维度进行评估：
1. 开篇吸引力（20分）：故事是否能快速抓住读者？
2. 人物设定（20分）：人物是否立体、有记忆点？
3. 世界观（20分）：设定是否新颖、有吸引力？
4. 剧情结构（20分）：主线是否清晰、节奏是否合理？
5. 商业性（20分）：是否有市场潜力？

请给出：
- 每个维度的评分和评语
- 发现的问题
- 改进建议
- 最终总分"""

            # 调用LLM
            from core.model_manager import create_model_manager
            from core.config_manager import load_env_file

            env_config = load_env_file()
            model_id = env_config.get("DEFAULT_MODEL_ID", "deepseek-v3")
            llm = create_model_manager(model_id)

            self.log_panel.append_log("Editor is evaluating...", "info")
            result = llm.generate(user_prompt, system_prompt=system_prompt, temperature=0.7)

            # 发送评估完成信号
            self.preproduction_panel.evaluation_complete.emit(result)
            self.log_panel.append_log("Evaluation completed!", "system")

        except Exception as e:
            error_msg = f"评估失败：{str(e)}"
            self.preproduction_panel.evaluation_complete.emit(f"Error: {error_msg}")
            self.log_panel.append_log(f"Evaluation error: {str(e)}", "error")

    def _on_evaluation_complete(self, result: str):
        """评估完成回调（在主线程执行）"""
        if result.startswith("Error:"):
            self.preproduction_panel.set_error(result.replace("Error:", ""))
        else:
            self.preproduction_panel.set_evaluation_result(result)
        self.preproduction_panel.eval_btn.setEnabled(True)
        self.preproduction_panel.eval_btn.setText("2️⃣ 评估设置")

    def on_approve_and_start(self):
        """从前期筹备面板批准并开始写作"""
        self.log_panel.append_log("Settings approved. Starting generation...", "system")

        # 切换到生产监控标签页
        self.tabs.setCurrentIndex(1)

        # 开始生成
        self.on_start_generation()

    def on_pause_generation(self):
        """暂停生成"""
        if self.worker:
            self.worker.stop()

        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(True)

        self.log_panel.append_log("Generation paused", "warning")
        self.agent_panel.update_agent_status("EmotionWriter", "idle")
        self.status_bar.showMessage("Paused")

    def on_resume_generation(self):
        """恢复生成"""
        self.log_panel.append_log("Resuming generation...", "system")
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)
        self.status_bar.showMessage("Generating...")

    def connect_worker(self, worker):
        """连接工作线程"""
        self.worker = worker

        # 连接信号
        worker.log_signal.connect(self.on_log)
        worker.agent_status_signal.connect(self.on_agent_status)
        worker.emotion_curve_signal.connect(self.on_emotion_curve)
        worker.circuit_breaker_signal.connect(self.on_circuit_breaker)
        worker.chapter_complete_signal.connect(self.on_chapter_complete)
        worker.error_signal.connect(self.on_error)
        worker.progress_signal.connect(self.on_progress)

    def on_log(self, message: str):
        """日志信号处理"""
        # 判断日志级别
        if "ERROR" in message.upper():
            level = "error"
        elif "WARNING" in message.upper():
            level = "warning"
        elif "completed" in message.lower():
            level = "success"
        else:
            level = "info"

        self.log_panel.append_log(message, level)

    def on_agent_status(self, data: dict):
        """Agent状态更新"""
        name = data.get("name", "")
        status = data.get("status", "idle")
        self.agent_panel.update_agent_status(name, status)

    def on_emotion_curve(self, data: dict):
        """情绪曲线更新"""
        expected = data.get("expected", [])
        actual = data.get("actual", [])
        chapter = data.get("chapter", 0)

        total = self.worker.config.get("target_chapters", 10) if self.worker else 10

        self.emotion_panel.update_curve(expected, actual, chapter, total)

    def on_circuit_breaker(self, data: dict):
        """熔断信号处理"""
        if data.get("tripped"):
            chapter = data.get("chapter", 0)
            reason = data.get("reason", "Unknown")

            # 读取回滚次数
            rollbacks = 0
            rollback_file = Path(self.project_dir) / "rollback_log.json"
            if rollback_file.exists():
                try:
                    data = json.loads(rollback_file.read_text(encoding="utf-8"))
                    rollbacks = len(data.get("rollbacks", []))
                except:
                    pass

            self.circuit_breaker.set_tripped(chapter, reason, rollbacks)
            self.log_panel.append_log(f"CIRCUIT BREAKER TRIGGERED at Chapter {chapter}: {reason}", "error")

            # 更新按钮状态
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
        else:
            self.circuit_breaker.set_normal(0)

    def on_chapter_complete(self, data: dict):
        """章节完成"""
        chapter = data.get("chapter", 0)
        word_count = data.get("word_count", 0)

        self.status_bar.showMessage(f"Chapter {chapter} completed - {word_count} words")

    def on_error(self, error: str):
        """错误处理"""
        self.log_panel.append_log(f"ERROR: {error}", "error")
        self.agent_panel.update_agent_status("EmotionWriter", "error")

    def on_progress(self, current: int, total: int):
        """进度更新"""
        self.status_bar.showMessage(f"Progress: {current}/{total} chapters")


# ============================================================================
# 独立运行入口
# ============================================================================
def run_dashboard(project_dir: str = None):
    """运行仪表板"""
    if not PYQT_AVAILABLE:
        print("Error: PyQt6 is required")
        return

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 🔥【核心修复】：关闭"最后一个窗口退出即结束程序"的默认设定
    # 否则弹窗关闭时程序会误以为要退出
    app.setQuitOnLastWindowClosed(False)

    # 检查是否需要弹出项目设置对话框
    need_setup = False

    if project_dir:
        # 检查项目目录是否存在有效配置
        config_path = Path(project_dir) / "project_config.json"
        if not config_path.exists():
            need_setup = True
    else:
        need_setup = True

    # 如果需要设置，弹出对话框
    if need_setup:
        # 创建对话框
        dialog = ProjectSetupDialog()

        if dialog.exec() != QDialog.DialogCode.Accepted:
            print("Project setup cancelled by user.")
            sys.exit(0)

        # 获取配置
        config = dialog.get_project_config()
        if not config:
            print("Failed to get project config")
            sys.exit(1)

        # 创建项目目录
        title = config["title"]
        # 生成安全的目录名（处理中文和特殊字符）
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title)
        project_dir = f"novels/{safe_name}"

        Path(project_dir).mkdir(parents=True, exist_ok=True)

        # 保存配置到文件
        config_path = Path(project_dir) / "project_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"Project created: {project_dir}")
        print(f"Config saved to: {config_path}")

    # 🔥【核心修复】：主窗口准备就绪，恢复自动退出机制
    app.setQuitOnLastWindowClosed(True)

    print("[System] 正在点火，启动赛博编辑部中控大屏...")

    # 创建并显示主窗口
    window = ProducerDashboard(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # 传递命令行参数作为预选项目路径
    # 如果该路径没有有效配置，会弹出设置对话框
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
