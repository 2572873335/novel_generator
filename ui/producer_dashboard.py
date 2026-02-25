"""
Producer Dashboard - 赛博朋克UI重构 (v4.1)
NovelForge v4.0 制片人控制台 - 全面升级版

功能：
1. 左侧：Agent工牌矩阵（带翻转功能）+ 详细信息面板
2. 中间：生产控制 + 实时日志
3. 右侧：pyqtgraph 情绪波浪图（缩小版）
4. 前期筹备Tab：评估后可编辑优化 + 生成过程可视化
5. 进度保存与续写
6. 文档查看器
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
        QLineEdit, QTextBrowser, QMessageBox, QTabWidget, QMenuBar,
        QMenu, QFileDialog, QListWidget, QListWidgetItem, QStackedWidget,
        QGridLayout, QSizePolicy, QDialogButtonBox
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QPropertyAnimation, QEasingCurve, QPoint
    from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor, QAction, QCursor, QPainter, QPicture
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
# Agent 工牌组件（赛博朋克ID卡风格 - 可翻转）
# ============================================================================
class FlipCard(QFrame):
    """可翻转的Agent工牌组件"""

    flipped = pyqtSignal(bool)  # 翻转信号

    def __init__(self, front_widget, back_widget, parent=None):
        super().__init__(parent)
        self.is_flipped = False
        self.front_widget = front_widget
        self.back_widget = back_widget

        self.setMinimumSize(front_widget.sizeHint())
        self.setMaximumSize(400, 200)

        # 使用堆叠窗口
        self.stack = QStackedWidget(self)
        self.stack.addWidget(front_widget)
        self.stack.addWidget(back_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        # 点击事件
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def mousePressEvent(self, event):
        """点击翻转"""
        self.flip()
        super().mousePressEvent(event)

    def flip(self):
        """翻转卡片"""
        self.is_flipped = not self.is_flipped
        self.stack.setCurrentIndex(1 if self.is_flipped else 0)
        self.flipped.emit(self.is_flipped)


class AgentCardBack(QWidget):
    """Agent工牌背面 - 显示详细信息"""

    def __init__(self, agent_info: dict, parent=None):
        super().__init__(parent)
        self.agent_info = agent_info
        self.init_ui()

    def init_ui(self):
        """初始化背面UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #1a1a25;
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # 功能描述
        desc_label = QLabel(f"📋 {self.agent_info.get('description', 'N/A')}")
        desc_label.setFont(QFont("Consolas", 8))
        desc_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 最近活动
        activity_label = QLabel(f"🕐 最近活动: {self.agent_info.get('last_activity', '无')}")
        activity_label.setFont(QFont("Consolas", 7))
        activity_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_DIM};")
        layout.addWidget(activity_label)

        # 统计信息
        stats_label = QLabel(f"📊 处理章节: {self.agent_info.get('chapters_processed', 0)} | 错误: {self.agent_info.get('error_count', 0)}")
        stats_label.setFont(QFont("Consolas", 7))
        stats_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_DIM};")
        layout.addWidget(stats_label)

        layout.addStretch()


class AgentCard(QFrame):
    """Agent 员工工牌 - 赛博朋克ID卡风格（可翻转）"""

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

    card_clicked = pyqtSignal(str)  # 工牌点击信号

    def __init__(self, name: str, role: str, emoji: str = "🤖", agent_info: dict = None, parent=None):
        super().__init__(parent)
        self.agent_name = name
        self.agent_role = role
        self.agent_emoji = emoji
        self.agent_info = agent_info or {
            "description": role,
            "last_activity": "无",
            "chapters_processed": 0,
            "error_count": 0,
            "logs": []
        }
        self.current_task = ""

        self.init_ui()
        self.set_status("idle")

    def init_ui(self):
        """初始化UI - 赛博朋克ID卡风格"""
        self.setFixedSize(170, 75)
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
        content_layout.setContentsMargins(10, 6, 10, 6)
        content_layout.setSpacing(2)

        # 顶部：Emoji + Agent名称
        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)

        self.emoji_label = QLabel(self.agent_emoji)
        self.emoji_label.setStyleSheet("font-size: 14px;")
        top_layout.addWidget(self.emoji_label)

        self.name_label = QLabel(self.agent_name)
        self.name_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.name_label.setStyleSheet("color: #ffffff;")
        self.name_label.setMaximumWidth(120)
        self.name_label.setWordWrap(True)
        top_layout.addWidget(self.name_label)

        top_layout.addStretch()
        content_layout.addLayout(top_layout)

        # 中部：职位角色
        self.role_label = QLabel(self.agent_role)
        self.role_label.setFont(QFont("Consolas", 7))
        self.role_label.setStyleSheet("color: #8888aa;")
        self.role_label.setMaximumWidth(140)
        self.role_label.setWordWrap(True)
        content_layout.addWidget(self.role_label)

        # 底部：状态指示灯 + 状态文字
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

        content_layout.addLayout(bottom_layout)

        layout.addLayout(content_layout, stretch=1)

        # 点击事件
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def mousePressEvent(self, event):
        """点击事件"""
        self.card_clicked.emit(self.agent_name)
        super().mousePressEvent(event)

    def set_status(self, status: str, task: str = ""):
        """设置状态"""
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

    def update_info(self, **kwargs):
        """更新Agent信息"""
        for key, value in kwargs.items():
            if key in self.agent_info:
                self.agent_info[key] = value


# ============================================================================
# Agent 详细信息面板
# ============================================================================
class AgentDetailPanel(QWidget):
    """Agent详细信息面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_agent = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QTextEdit {{
                background-color: {CyberpunkTheme.BG_DARK};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                font-family: Consolas;
                font-size: 9px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 标题
        title = QLabel("📋 Agent 详细信息")
        title.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        layout.addWidget(title)

        # Agent选择
        self.agent_combo = QComboBox()
        self.agent_combo.setFont(QFont("Consolas", 9))
        layout.addWidget(self.agent_combo)

        # 详细信息显示
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)

        # 日志区域
        log_label = QLabel("📝 工作日志")
        log_label.setFont(QFont("Consolas", 10))
        log_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text, stretch=1)

    def set_agents(self, agents: Dict[str, AgentCard]):
        """设置Agent列表"""
        self.agent_combo.clear()
        self.agent_combo.addItems(agents.keys())
        self.agent_cards = agents
        self.agent_combo.currentTextChanged.connect(self.on_agent_selected)

    def on_agent_selected(self, name: str):
        """选择Agent"""
        self.selected_agent = name
        if name in self.agent_cards:
            card = self.agent_cards[name]
            info = card.agent_info

            # 显示详细信息
            detail_text = f"""
【{card.agent_emoji} {name}】

职位: {card.agent_role}
状态: {card.status_label.text()}
当前任务: {card.current_task or '无'}

功能描述: {info.get('description', 'N/A')}

统计信息:
  - 处理章节数: {info.get('', 0)}
chapters_processed  - 错误次数: {info.get('error_count', 0)}
  - 最后活动: {info.get('last_activity', '无')}
"""
            self.info_text.setPlainText(detail_text)

            # 显示日志
            logs = info.get('logs', [])
            if logs:
                log_text = "\n".join([f"• {log}" for log in logs[-10:]])
            else:
                log_text = "暂无日志"
            self.log_text.setPlainText(log_text)

    def add_log(self, agent_name: str, log: str):
        """添加日志"""
        if agent_name in self.agent_cards:
            info = self.agent_cards[agent_name].agent_info
            if 'logs' not in info:
                info['logs'] = []
            info['logs'].append(f"{datetime.now().strftime('%H:%M:%S')} - {log}")

            # 如果当前选中该Agent，刷新显示
            if self.selected_agent == agent_name:
                self.on_agent_selected(agent_name)


# ============================================================================
# Agent 矩阵面板（使用流式布局）
# ============================================================================
class AgentMatrixPanel(QWidget):
    """Agent 员工矩阵 - 使用流式布局避免重叠"""

    agent_clicked = pyqtSignal(str)  # Agent点击信号

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
        layout.setSpacing(8)

        # 标题
        title = QLabel("🤖 AGENT MATRIX")
        title.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Agent Workers Status (点击查看详情)")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Agent 列表 - 使用流式布局
        self.agent_scroll = QScrollArea()
        self.agent_scroll.setWidgetResizable(True)
        self.agent_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {CyberpunkTheme.BG_DARK};
                border: none;
            }}
        """)

        self.agent_container = QWidget()
        self.agent_flow_layout = QGridLayout(self.agent_container)
        self.agent_flow_layout.setSpacing(10)
        self.agent_flow_layout.setContentsMargins(0, 0, 0, 0)

        self.agent_scroll.setWidget(self.agent_container)

        self.agent_cards = {}

        # v4.0 核心Agent（带Emoji）
        self.agents_config = {
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

        # 使用GridLayout排列工牌（每行3个）
        row, col = 0, 0
        for name, card in self.agents_config.items():
            self.agent_flow_layout.addWidget(card, row, col)
            card.card_clicked.connect(lambda n=name: self.agent_clicked.emit(n))
            self.agent_cards[name] = card
            col += 1
            if col >= 3:
                col = 0
                row += 1

        layout.addWidget(self.agent_scroll)

    def update_agent_status(self, name: str, status: str, task: str = ""):
        """更新Agent状态"""
        if name in self.agent_cards:
            self.agent_cards[name].set_status(status, task)

            # 添加到日志
            if hasattr(self, 'detail_panel') and self.detail_panel:
                self.detail_panel.add_log(name, f"状态变更: {status}")


# ============================================================================
# 情绪波浪图面板（缩小版）
# ============================================================================
class EmotionWavePanel(QWidget):
    """情绪波浪图面板 - 缩小版放在右侧"""

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
        layout.setSpacing(5)

        # 标题
        title = QLabel("📈 EMOTION WAVE")
        title.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("Expected vs Actual Tension")
        subtitle.setFont(QFont("Consolas", 8))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(5)

        if PYQTGRAPH_AVAILABLE:
            # 创建图表（缩小尺寸）
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground(CyberpunkTheme.BG_MEDIUM)
            self.plot_widget.setMinimumHeight(150)
            self.plot_widget.setMaximumHeight(200)

            # 配置图表
            self.plot_widget.setLabel('bottom', 'Chapter', color='#8888aa')
            self.plot_widget.setLabel('left', 'Tension', color='#8888aa')
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

        # 统计信息（精简版）
        stats_layout = QHBoxLayout()

        self.chapter_label = QLabel("Ch: 0/0")
        self.chapter_label.setFont(QFont("Consolas", 9))
        self.chapter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY};")
        stats_layout.addWidget(self.chapter_label)

        stats_layout.addStretch()

        self.debt_label = QLabel("Debt: 0.0")
        self.debt_label.setFont(QFont("Consolas", 9))
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
            self.chapter_label.setText(f"Ch: {chapter}/{total}")

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

                self.debt_label.setStyleSheet(f"color: {color}; font-size: 9px;")


# ============================================================================
# 实时日志面板（带筛选）
# ============================================================================
class LogPanel(QWidget):
    """实时日志面板 - 带Agent筛选"""

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
            QComboBox {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                font-family: Consolas;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 标题行
        title_layout = QHBoxLayout()

        title = QLabel("📋 ARBITRATION LOG")
        title.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_SECONDARY};")
        title_layout.addWidget(title)

        title_layout.addStretch()

        # Agent筛选下拉框
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "EmotionWriter", "CreativeDirector", "EmotionTracker",
                                     "ConsistencyGuardian", "StyleAnchor", "WorldBible", "InitializerAgent"])
        self.filter_combo.setFont(QFont("Consolas", 8))
        self.filter_combo.setFixedWidth(150)
        title_layout.addWidget(self.filter_combo)

        layout.addLayout(title_layout)

        # 副标题
        subtitle = QLabel("Real-time Decision Log")
        subtitle.setFont(QFont("Consolas", 8))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(5)

        # 日志区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text, stretch=1)

        # 导出按钮
        export_btn = QPushButton("📥 导出日志")
        export_btn.setFont(QFont("Consolas", 9))
        export_btn.clicked.connect(self.export_log)
        layout.addWidget(export_btn)

    def append_log(self, message: str, level: str = "info", agent: str = None):
        """追加日志"""
        # 检查筛选
        current_filter = self.filter_combo.currentText()
        if current_filter != "全部" and agent and agent != current_filter:
            return

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

        # Agent标签
        agent_tag = f"[{agent}] " if agent else ""

        # HTML格式化
        html = f'<span style="color: {CyberpunkTheme.TEXT_DIM};">[{timestamp}]</span> '
        html += f'<span style="color: {color};">{agent_tag}{message}</span><br>'

        self.log_text.append(html)

        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def clear(self):
        """清空日志"""
        self.log_text.clear()

    def export_log(self):
        """导出日志到文件"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出日志", f"novel_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            "Log Files (*.log);;Text Files (*.txt)"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())


# ============================================================================
# 项目初始化对话框
# ============================================================================
class ProjectSetupDialog(QDialog):
    """新建项目档案对话框"""

    GENRE_METRICS = {
        "修仙": ["realm", "spiritual_power", "tribulation_count"],
        "都市": ["reputation", "wealth", "relationship_level"],
        "赛博朋克": ["cyber_psychosis_level", "credits", "augmentation_level"],
        "玄幻": ["realm", "magic_power", "artifact_rank"],
        "科幻": ["tech_level", "resources", "alliance_count"],
        "悬疑": ["clue_count", "danger_level", "truth_revealed"],
        "历史": ["influence", "wealth", "army_size"],
    }

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
        self.on_genre_changed("修仙")
        layout.addWidget(self.metrics_label)

        layout.addStretch()

        # 按钮区域
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("✕ CANCEL")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

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
        title = self.title_edit.text().strip()
        genre = self.genre_combo.currentText()
        protagonist = self.protagonist_edit.text().strip()
        chapters = self.chapters_spin.value()
        settings = self.settings_edit.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "输入错误", "请输入小说书名", QMessageBox.StandardButton.Ok)
            self.title_edit.setFocus()
            return

        if not protagonist:
            QMessageBox.warning(self, "输入错误", "请输入主角姓名", QMessageBox.StandardButton.Ok)
            self.protagonist_edit.setFocus()
            return

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
# 进度检测与恢复对话框
# ============================================================================
class ProgressResumeDialog(QDialog):
    """进度恢复对话框"""

    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.completed_chapters = 0
        self.total_chapters = 0
        self.init_ui()
        self.check_progress()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("检测到历史进度")
        self.setFixedSize(450, 250)
        self.setModal(True)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 4px;
                padding: 12px 24px;
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
        layout.setSpacing(15)

        # 图标
        icon = QLabel("📂")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # 标题
        title = QLabel("检测到历史进度")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 进度信息
        self.info_label = QLabel("正在检查...")
        self.info_label.setFont(QFont("Consolas", 10))
        self.info_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                text-align: center;
                color: {CyberpunkTheme.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()

        self.restart_btn = QPushButton("🔄 重新开始")
        self.restart_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.restart_btn)

        self.continue_btn = QPushButton("▶ 继续写作")
        self.continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: {CyberpunkTheme.BG_DARK};
                border: 2px solid {CyberpunkTheme.FG_SUCCESS};
            }}
        """)
        self.continue_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.continue_btn)

        layout.addLayout(btn_layout)

    def check_progress(self):
        """检查进度"""
        progress_file = Path(self.project_dir) / "novel-progress.txt"

        if progress_file.exists():
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.completed_chapters = data.get('completed_chapters', 0)
                self.total_chapters = data.get('total_chapters', 0)

                percentage = (self.completed_chapters / self.total_chapters * 100) if self.total_chapters > 0 else 0

                self.info_label.setText(
                    f"项目: {data.get('title', 'Unknown')}\n"
                    f"已完成: {self.completed_chapters}/{self.total_chapters} 章 ({percentage:.1f}%)"
                )
                self.progress_bar.setValue(int(percentage))
            except Exception as e:
                self.info_label.setText(f"无法读取进度: {str(e)}")
                self.progress_bar.setValue(0)
        else:
            # 检查chapters目录
            chapters_dir = Path(self.project_dir) / "chapters"
            if chapters_dir.exists():
                chapter_files = list(chapters_dir.glob("chapter-*.md"))
                self.completed_chapters = len(chapter_files)

                # 尝试获取总章节数
                config_file = Path(self.project_dir) / "project_config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        self.total_chapters = config.get('target_chapters', 0)
                    except:
                        self.total_chapters = self.completed_chapters
                else:
                    self.total_chapters = self.completed_chapters

                percentage = (self.completed_chapters / self.total_chapters * 100) if self.total_chapters > 0 else 0
                self.info_label.setText(
                    f"检测到 {self.completed_chapters} 个已完成的章节\n"
                    f"总目标章节数: {self.total_chapters}"
                )
                self.progress_bar.setValue(int(percentage))
            else:
                self.info_label.setText("未检测到历史进度")
                self.progress_bar.setValue(0)

    def get_start_chapter(self) -> int:
        """获取起始章节"""
        return self.completed_chapters + 1


# ============================================================================
# 前期筹备面板 (Pre-Production) - 增强版
# ============================================================================
class PreProductionPanel(QWidget):
    """前期筹备面板 - 增强版支持评估优化和生成可视化"""

    generate_settings = pyqtSignal()
    evaluate_settings = pyqtSignal()
    approve_and_start = pyqtSignal()
    evaluation_complete = pyqtSignal(str)

    # 信号：采纳建议
    apply_suggestions = pyqtSignal(str)  # 评估建议
    focus_edit = pyqtSignal(str)  # 聚焦编辑区域

    def __init__(self, project_dir: str = None, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir or "novels/default"
        self.current_evaluation = ""
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
            QGroupBox {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: Consolas;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
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
        self.outline_text.setMinimumHeight(180)
        outline_layout.addWidget(self.outline_text)
        outline_group.setLayout(outline_layout)
        content_splitter.addWidget(outline_group)

        # 人物设定区
        chars_group = QGroupBox("👤 人物设定 (characters.json)")
        chars_layout = QVBoxLayout()
        self.chars_text = QTextEdit()
        self.chars_text.setPlaceholderText("在这里编辑人物设定...\n\n主角信息：\n- 姓名、年龄\n- 性格特点\n- 背景故事\n- 能力设定")
        self.chars_text.setMinimumHeight(120)
        chars_layout.addWidget(self.chars_text)
        chars_group.setLayout(chars_layout)
        content_splitter.addWidget(chars_group)

        # 资深编辑诊断区 - 增强版
        eval_group = QGroupBox("📋 资深编辑诊断 (Senior Editor Evaluation)")
        eval_layout = QVBoxLayout()

        self.eval_text = QTextBrowser()
        self.eval_text.setPlaceholderText("点击「评估设置」按钮获取资深编辑的诊断建议...")
        self.eval_text.setMinimumHeight(100)
        eval_layout.addWidget(self.eval_text)

        # 评估操作按钮
        eval_btn_layout = QHBoxLayout()

        self.apply_btn = QPushButton("✅ 采纳建议并修改")
        self.apply_btn.setFont(QFont("Consolas", 10))
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.on_apply_suggestions)
        eval_btn_layout.addWidget(self.apply_btn)

        self.edit_btn = QPushButton("✏️ 手动修改")
        self.edit_btn.setFont(QFont("Consolas", 10))
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(lambda: self.focus_edit.emit("outline"))
        eval_btn_layout.addWidget(self.edit_btn)

        self.re_eval_btn = QPushButton("🔄 重新评估")
        self.re_eval_btn.setFont(QFont("Consolas", 10))
        self.re_eval_btn.setEnabled(False)
        self.re_eval_btn.clicked.connect(self.on_evaluate_settings)
        eval_btn_layout.addWidget(self.re_eval_btn)

        eval_btn_layout.addStretch()
        eval_layout.addLayout(eval_btn_layout)

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
        self.save_to_disk()
        self.approve_and_start.emit()

    def on_apply_suggestions(self):
        """采纳建议并修改"""
        if self.current_evaluation:
            # 从评估结果中提取改进建议并应用到大纲
            # 这里可以解析评估结果中的建议
            self.apply_suggestions.emit(self.current_evaluation)
            QMessageBox.information(
                self, "已采纳",
                "建议已应用到大纲，请查看并根据需要手动调整",
                QMessageBox.StandardButton.Ok
            )

    def set_generation_complete(self):
        """设置生成完成状态"""
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("1️⃣ 生成设置")

    def set_evaluation_result(self, result: str):
        """显示评估结果"""
        self.current_evaluation = result

        self.eval_btn.setEnabled(True)
        self.eval_btn.setText("2️⃣ 评估设置")
        self.eval_text.setHtml(f"<pre style='color: {CyberpunkTheme.TEXT_PRIMARY};'>{result}</pre>")

        # 启用操作按钮
        self.apply_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.re_eval_btn.setEnabled(True)

    def set_error(self, message: str):
        """显示错误"""
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("1️⃣ 生成设置")
        self.eval_text.setHtml(f"<span style='color: {CyberpunkTheme.FG_DANGER};'>{message}</span>")
        self.apply_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.re_eval_btn.setEnabled(False)


# ============================================================================
# 章节完成后反馈对话框
# ============================================================================
class ChapterFeedbackDialog(QDialog):
    """章节完成后反馈对话框"""

    def __init__(self, chapter: int, summary: str, quality_score: float, logs: List[str], parent=None):
        super().__init__(parent)
        self.chapter = chapter
        self.summary = summary
        self.quality_score = quality_score
        self.logs = logs
        self.result = "continue"  # 默认继续
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"第{self.chapter}章完成")
        self.setMinimumSize(500, 400)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QTextEdit {{
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title = QLabel(f"✅ 第{self.chapter}章已完成")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 质量分数
        score_text = f"质量分数: {self.quality_score:.1f}/10"
        score_label = QLabel(score_text)
        score_label.setFont(QFont("Consolas", 11))
        score_label.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(score_label)

        # 章节摘要
        summary_label = QLabel("章节摘要:")
        summary_label.setFont(QFont("Consolas", 11))
        layout.addWidget(summary_label)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setText(self.summary or "无")
        self.summary_text.setMaximumHeight(80)
        layout.addWidget(self.summary_text)

        # Agent日志
        log_label = QLabel("Agent工作日志:")
        log_label.setFont(QFont("Consolas", 11))
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_content = "\n".join([f"• {log}" for log in self.logs]) if self.logs else "无日志"
        self.log_text.setText(log_content)
        layout.addWidget(self.log_text, stretch=1)

        # 按钮
        btn_layout = QHBoxLayout()

        rewrite_btn = QPushButton("🔄 需要重写")
        rewrite_btn.clicked.connect(lambda: self.set_result("rewrite"))
        btn_layout.addWidget(rewrite_btn)

        edit_btn = QPushButton("✏️ 手动修改")
        edit_btn.clicked.connect(lambda: self.set_result("edit"))
        btn_layout.addWidget(edit_btn)

        continue_btn = QPushButton("▶ 继续下一章")
        continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)
        continue_btn.clicked.connect(lambda: self.set_result("continue"))
        btn_layout.addWidget(continue_btn)

        layout.addLayout(btn_layout)

    def set_result(self, result: str):
        """设置结果"""
        self.result = result
        self.accept()

    def get_result(self) -> str:
        """获取结果"""
        return self.result


# ============================================================================
# API Key 设置对话框
# ============================================================================
class SettingsDialog(QDialog):
    """API Key设置对话框"""

    # API Key配置
    API_KEYS = {
        "DEEPSEEK_API_KEY": ("DeepSeek API Key", "DeepSeek 模型"),
        "ANTHROPIC_API_KEY": ("Anthropic API Key", "Claude 模型"),
        "OPENAI_API_KEY": ("OpenAI API Key", "GPT 模型"),
        "MOONSHOT_API_KEY": ("Moonshot API Key", "Kimi 模型"),
    }

    # 可用模型（与 model_manager.py 中的 AVAILABLE_MODELS 保持一致）
    MODELS = [
        "deepseek-chat (DeepSeek V3.2)",
        "deepseek-reasoner (DeepSeek V3.2 思考模式)",
        "claude-3-5-sonnet (Anthropic)",
        "gpt-4o (OpenAI)",
        "moonshot-v1-8k (Moonshot)",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("API Key 设置")
        self.setMinimumSize(550, 500)
        self.setModal(True)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QLineEdit {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas;
            }}
            QComboBox {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px;
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
            QGroupBox {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                font-family: Consolas;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title = QLabel("⚙️ API Key 设置")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 当前模型状态
        model_group = QGroupBox("当前模型")
        model_layout = QFormLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems(self.MODELS)
        model_layout.addRow("选择模型:", self.model_combo)

        self.model_status_label = QLabel("未设置")
        self.model_status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")
        model_layout.addRow("状态:", self.model_status_label)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # API Key输入区
        keys_group = QGroupBox("API Keys")
        keys_layout = QFormLayout()
        keys_layout.setSpacing(10)

        self.key_inputs = {}
        for key_name, (label, desc) in self.API_KEYS.items():
            row_layout = QHBoxLayout()

            input_field = QLineEdit()
            input_field.setPlaceholderText(f"请输入 {desc}...")
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
            input_field.setMinimumWidth(300)

            # 状态指示
            status_label = QLabel("❌ 未配置")
            status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER};")
            status_label.setFixedWidth(100)

            row_layout.addWidget(input_field)
            row_layout.addWidget(status_label)

            self.key_inputs[key_name] = {"input": input_field, "status": status_label}
            keys_layout.addRow(f"{label}:", row_layout)

        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)

        # 提示信息
        tip_label = QLabel("💡 提示：API Key 仅保存在本地 .env 文件中，不会提交到 Git")
        tip_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY}; font-size: 9px;")
        layout.addWidget(tip_label)

        layout.addStretch()

        # 按钮区域
        btn_layout = QHBoxLayout()

        test_btn = QPushButton("🔗 测试连接")
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("✕ 取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 保存设置")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def load_current_settings(self):
        """加载当前设置"""
        try:
            from core.config_manager import get_api_key, check_api_key, load_env_file

            # 加载环境变量
            env_config = load_env_file()

            # 加载当前模型
            default_model = env_config.get("DEFAULT_MODEL_ID", "")
            if default_model:
                for i, model in enumerate(self.MODELS):
                    if default_model in model.lower():
                        self.model_combo.setCurrentIndex(i)
                        break
                self.model_status_label.setText("✅ 已配置")
                self.model_status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
            else:
                self.model_status_label.setText("⚠️ 默认")
                self.model_status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")

            # 加载API Key状态
            for key_name in self.API_KEYS.keys():
                is_configured = check_api_key(key_name)
                if key_name in self.key_inputs:
                    status_label = self.key_inputs[key_name]["status"]
                    if is_configured:
                        status_label.setText("✅ 已配置")
                        status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
                        # 不显示实际Key，只显示已配置
                        self.key_inputs[key_name]["input"].setText("••••••••••••••••")
                    else:
                        status_label.setText("❌ 未配置")
                        status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER};")

        except Exception as e:
            print(f"Error loading settings: {e}")

    def test_connection(self):
        """测试API连接"""
        # 检查是否有可用的API Key
        from core.config_manager import check_api_key, get_api_key

        available_keys = []
        for key_name in self.API_KEYS.keys():
            if check_api_key(key_name):
                available_keys.append(key_name)

        if not available_keys:
            QMessageBox.warning(
                self, "测试连接",
                "请至少配置一个API Key后再测试连接",
                QMessageBox.StandardButton.Ok
            )
            return

        # 尝试使用配置的Key进行简单测试
        try:
            from core.model_manager import create_model_manager
            from core.config_manager import load_env_file, get_api_key

            env_config = load_env_file()
            model_id = env_config.get("DEFAULT_MODEL_ID", "deepseek-chat")

            # 确定需要检查的API Key
            key_name = env_config.get("DEFAULT_MODEL_API_KEY", "DEEPSEEK_API_KEY")
            api_key = get_api_key(key_name)

            if not api_key or api_key.strip() == "":
                QMessageBox.warning(
                    self, "测试连接",
                    f"❌ API Key未配置\n\n模型: {model_id}\n需要配置: {key_name}",
                    QMessageBox.StandardButton.Ok
                )
                return

            llm = create_model_manager(model_id)

            # 简单测试
            result = llm.generate("Say 'OK' if you receive this message.", temperature=0)

            QMessageBox.information(
                self, "测试连接",
                f"✅ 连接成功！\n\n模型: {model_id}\nAPI Key: {key_name[:10]}...\n响应: {result[:50]}...",
                QMessageBox.StandardButton.Ok
            )

        except Exception as e:
            error_msg = str(e)
            # 提供更友好的错误信息
            if "Client.__init__()" in error_msg or "api key" in error_msg.lower():
                error_msg = f"API Key可能无效或未正确配置\n\n详情: {error_msg}"
            QMessageBox.critical(
                self, "测试连接",
                f"❌ 连接失败\n\n模型: {model_id}\n错误信息: {error_msg}",
                QMessageBox.StandardButton.Ok
            )

    def save_settings(self):
        """保存设置"""
        try:
            from core.config_manager import save_api_key, load_env_file

            # 获取.env文件路径
            current_dir = Path(__file__).parent.parent
            env_path = current_dir / ".env"

            # 保存模型设置
            selected_model = self.model_combo.currentText()
            model_id = selected_model.split(" ")[0]  # 提取模型ID

            # 映射模型到API Key
            model_key_map = {
                "deepseek": "DEEPSEEK_API_KEY",
                "claude": "ANTHROPIC_API_KEY",
                "gpt": "OPENAI_API_KEY",
                "moonshot": "MOONSHOT_API_KEY",
            }

            # 保存选中的模型
            for key, name in model_key_map.items():
                if key in model_id.lower():
                    save_api_key("DEFAULT_MODEL_ID", model_id, str(env_path))
                    save_api_key("DEFAULT_MODEL_API_KEY", name, str(env_path))
                    break

            # 保存API Keys
            saved_count = 0
            for key_name in self.API_KEYS.keys():
                input_field = self.key_inputs[key_name]["input"]
                key_value = input_field.text().strip()

                # 跳过默认的掩码字符
                if key_value and key_value != "••••••••••••••••":
                    save_api_key(key_name, key_value, str(env_path))
                    saved_count += 1

            if saved_count > 0:
                QMessageBox.information(
                    self, "保存成功",
                    "✅ API Key设置已保存！\n\n请重启应用程序以使更改生效。",
                    QMessageBox.StandardButton.Ok
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self, "未更改",
                    "未能保存设置，请重试",
                    QMessageBox.StandardButton.Ok
                )

        except Exception as e:
            QMessageBox.critical(
                self, "保存失败",
                f"❌ 保存设置时出错:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )


# ============================================================================
# 文档查看对话框
# ============================================================================
class DocumentViewerDialog(QDialog):
    """文档查看对话框"""

    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("查看文档")
        self.setMinimumSize(700, 500)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: Consolas;
            }}
            QListWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                font-family: Consolas;
            }}
            QTextEdit {{
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
                padding: 8px 16px;
                font-family: Consolas;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 左侧文件列表
        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(200)
        self.populate_file_list()
        self.file_list.currentRowChanged.connect(self.on_file_selected)
        layout.addWidget(self.file_list)

        # 右侧内容区
        content_layout = QVBoxLayout()

        # 内容显示
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        content_layout.addWidget(self.content_text, stretch=1)

        # 按钮
        btn_layout = QHBoxLayout()

        open_external_btn = QPushButton("📂 用系统编辑器打开")
        open_external_btn.clicked.connect(self.open_external)
        btn_layout.addWidget(open_external_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        content_layout.addLayout(btn_layout)

        layout.addLayout(content_layout, stretch=1)

    def populate_file_list(self):
        """填充文件列表"""
        project_path = Path(self.project_dir)

        # 添加大纲
        outline_file = project_path / "outline.md"
        if outline_file.exists():
            self.file_list.addItem("📖 大纲 (outline.md)")

        # 添加人物
        chars_file = project_path / "characters.json"
        if chars_file.exists():
            self.file_list.addItem("👤 人物设定 (characters.json)")

        # 添加章节
        chapters_dir = project_path / "chapters"
        if chapters_dir.exists():
            chapter_files = sorted(chapters_dir.glob("chapter-*.md"))
            for cf in chapter_files:
                chapter_num = cf.stem.replace("chapter-", "")
                self.file_list.addItem(f"📄 第{chapter_num}章")

    def on_file_selected(self, row: int):
        """选择文件"""
        if row < 0:
            return

        item_text = self.file_list.item(row).text()
        project_path = Path(self.project_dir)

        if "大纲" in item_text:
            file_path = project_path / "outline.md"
        elif "人物" in item_text:
            file_path = project_path / "characters.json"
        elif "第" in item_text and "章" in item_text:
            chapter_num = item_text.replace("📄 第", "").replace("章", "")
            file_path = project_path / "chapters" / f"chapter-{chapter_num}.md"
        else:
            return

        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                self.content_text.setText(content)
                self.current_file = file_path
            except Exception as e:
                self.content_text.setText(f"读取失败: {str(e)}")
        else:
            self.content_text.setText("文件不存在")

    def open_external(self):
        """用系统编辑器打开"""
        if hasattr(self, 'current_file') and self.current_file.exists():
            import subprocess
            try:
                # Windows系统
                subprocess.Popen(['notepad.exe', str(self.current_file)])
            except:
                # 尝试其他方式
                os.startfile(str(self.current_file))


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
# 主窗口 - 全面升级版
# ============================================================================
class ProducerDashboard(QMainWindow):
    """
    制片人仪表板主窗口 - v4.1 全面升级

    三栏布局（重新设计）:
    - 左侧：Agent工牌矩阵（可翻转）+ Agent详细信息面板
    - 中间：生产控制 + 实时日志
    - 右侧：情绪波浪图（缩小版）
    """

    start_generation = pyqtSignal(dict)

    def __init__(self, project_dir: str = None):
        super().__init__()

        self.project_dir = project_dir or "novels/default"
        self.worker = None
        self.project_config = None
        self.start_chapter = 1  # 起始章节（用于续写）

        # 读取项目配置
        self.load_project_config()

        self.init_ui()

        # 显示项目信息
        self.display_project_info()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("NovelForge v4.1 - Producer Dashboard")
        self.setGeometry(100, 100, 1500, 850)

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
            QMenuBar {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
            }}
            QMenuBar::item:selected {{
                background-color: {CyberpunkTheme.BG_LIGHT};
            }}
            QMenu {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QMenu::item:selected {{
                background-color: {CyberpunkTheme.BG_LIGHT};
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

        # Tab 2: 生产监控 (重新设计的三栏布局)
        production_widget = QWidget()
        production_layout = QHBoxLayout(production_widget)
        production_layout.setContentsMargins(5, 5, 5, 5)
        production_layout.setSpacing(5)

        # === 左侧：Agent面板 ===
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        # Agent矩阵
        self.agent_panel = AgentMatrixPanel()
        self.agent_panel.agent_clicked.connect(self.on_agent_clicked)
        left_layout.addWidget(self.agent_panel, stretch=2)

        # Agent详细信息面板
        self.detail_panel = AgentDetailPanel()
        self.detail_panel.set_agents(self.agent_panel.agent_cards)
        left_layout.addWidget(self.detail_panel, stretch=1)

        # 控制按钮
        self.setup_control_buttons(left_layout)

        # === 中间：日志面板 ===
        self.log_panel = LogPanel()

        # === 右侧：情绪曲线 + 熔断状态 ===
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        # 熔断状态栏
        self.circuit_breaker = CircuitBreakerPanel()
        right_layout.addWidget(self.circuit_breaker)

        # 情绪波浪图（缩小版）
        self.emotion_panel = EmotionWavePanel()
        right_layout.addWidget(self.emotion_panel, stretch=1)

        # 使用splitter分割
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_container)
        splitter.addWidget(self.log_panel)
        splitter.addWidget(right_container)

        # 重新设计比例：左侧2:中间2:右侧1
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)

        # 设置最小宽度
        left_container.setMinimumWidth(350)
        self.log_panel.setMinimumWidth(300)
        right_container.setMinimumWidth(280)

        production_layout.addWidget(splitter)

        self.tabs.addTab(production_widget, "🎬 生产监控 (Production Dashboard)")

        # 设置菜单栏（在log_panel创建后）
        self.setup_menu()

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Click 'Start Generation' to begin")

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")

        new_action = QAction("新建项目", self)
        new_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("打开项目", self)
        open_action.triggered.connect(self.on_open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        settings_menu = menubar.addMenu("⚙️ 设置")

        api_key_action = QAction("API Key设置", self)
        api_key_action.triggered.connect(self.on_api_key_settings)
        settings_menu.addAction(api_key_action)

        # 查看菜单
        view_menu = menubar.addMenu("👁️ 查看")

        docs_action = QAction("查看文档", self)
        docs_action.triggered.connect(self.on_view_documents)
        view_menu.addAction(docs_action)

        view_menu.addSeparator()

        log_action = QAction("清空日志", self)
        log_action.triggered.connect(self.log_panel.clear)
        view_menu.addAction(log_action)

        # 帮助菜单
        help_menu = menubar.addMenu("❓ 帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

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
        layout.addSpacing(10)

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

        layout.addStretch()

    def on_agent_clicked(self, agent_name: str):
        """Agent工牌点击事件"""
        self.detail_panel.on_agent_selected(agent_name)
        self.log_panel.append_log(f"Selected agent: {agent_name}", "info", agent_name)

    def on_new_project(self):
        """新建项目"""
        dialog = ProjectSetupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_project_config()
            if config:
                title = config["title"]
                safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title)
                self.project_dir = f"novels/{safe_name}"

                Path(self.project_dir).mkdir(parents=True, exist_ok=True)

                config_path = Path(self.project_dir) / "project_config.json"
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                self.project_config = config
                self.log_panel.append_log(f"New project created: {title}", "success")
                self.display_project_info()

    def on_open_project(self):
        """打开项目"""
        directory = QFileDialog.getExistingDirectory(self, "选择项目目录", "novels")
        if directory:
            self.project_dir = directory
            self.load_project_config()
            self.display_project_info()

    def on_view_documents(self):
        """查看文档"""
        dialog = DocumentViewerDialog(self.project_dir, self)
        dialog.exec()

    def on_api_key_settings(self):
        """API Key设置"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def on_about(self):
        """关于"""
        QMessageBox.about(
            self, "关于 NovelForge",
            "NovelForge v4.1 - AI小说生成系统\n\n"
            "基于Anthropic长运行代理最佳实践的全自动小说创作系统\n\n"
            "功能：\n"
            "• 前期筹备与评估优化\n"
            "• 生产过程可视化\n"
            "• 断点续写\n"
            "• Agent工牌翻转详情\n"
            "• 情绪曲线监控"
        )

    def on_start_generation(self):
        """开始生成"""
        # 检查是否有历史进度
        self.check_and_prompt_resume()

    def check_and_prompt_resume(self):
        """检查并提示是否续写"""
        progress_file = Path(self.project_dir) / "novel-progress.txt"
        chapters_dir = Path(self.project_dir) / "chapters"

        has_progress = False

        if progress_file.exists():
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('completed_chapters', 0) > 0:
                    has_progress = True
            except:
                pass

        if chapters_dir.exists():
            chapter_files = list(chapters_dir.glob("chapter-*.md"))
            if len(chapter_files) > 0:
                has_progress = True

        if has_progress:
            dialog = ProgressResumeDialog(self.project_dir, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.start_chapter = dialog.get_start_chapter()
                self.log_panel.append_log(f"Continuing from chapter {self.start_chapter}", "info")
            else:
                # 用户选择重新开始
                self.start_chapter = 1

        # 继续开始生成
        self.do_start_generation()

    def do_start_generation(self):
        """执行开始生成"""
        if GenerationWorker is None:
            self.log_panel.append_log("ERROR: GenerationWorker not available", "error")
            return

        self.log_panel.append_log("Initializing generation task...", "system")

        config = self.project_config or {}
        target_chapters = config.get("target_chapters", 10)

        self.log_panel.append_log(f"Creating worker for {target_chapters} chapters starting from {self.start_chapter}...", "info")

        worker_config = {
            "target_chapters": target_chapters,
            "checkpoint_interval": 5,
            "start_chapter": self.start_chapter
        }

        self.worker = GenerationWorker(self.project_dir, worker_config)
        self.connect_worker(self.worker)

        # 更新按钮状态
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(target_chapters)
        self.progress_bar.setValue(self.start_chapter - 1)

        # 更新Agent状态
        self.agent_panel.update_agent_status("EmotionWriter", "thinking")

        # 启动worker
        self.worker.start()

        self.status_bar.showMessage("Generating...")

    def on_generate_settings(self):
        """从前期筹备面板触发生成设置"""
        self.log_panel.append_log("Generating project settings (outline & characters)...", "system")
        self.tabs.setCurrentIndex(1)
        self.on_start_generation()

    def on_evaluate_settings(self):
        """从前期筹备面板触发评估"""
        self.log_panel.append_log("Running senior editor evaluation...", "system")

        self.preproduction_panel.eval_btn.setEnabled(False)
        self.preproduction_panel.eval_btn.setText("评估中...")

        self.preproduction_panel.evaluation_complete.connect(self._on_evaluation_complete)

        import threading
        eval_thread = threading.Thread(target=self._run_evaluation)
        eval_thread.start()

    def _run_evaluation(self):
        """运行评估（后台线程）"""
        try:
            outline = self.preproduction_panel.outline_text.toPlainText()
            characters = self.preproduction_panel.chars_text.toPlainText()

            if not outline and not characters:
                self.preproduction_panel.evaluation_complete.emit("Error: 请先生成或填写大纲和人物设定！")
                return

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

            from core.model_manager import create_model_manager
            from core.config_manager import load_env_file

            env_config = load_env_file()
            model_id = env_config.get("DEFAULT_MODEL_ID", "deepseek-chat")
            llm = create_model_manager(model_id)

            self.log_panel.append_log("Editor is evaluating...", "info", "SeniorEditor")
            result = llm.generate(user_prompt, system_prompt=system_prompt, temperature=0.7)

            self.preproduction_panel.evaluation_complete.emit(result)
            self.log_panel.append_log("Evaluation completed!", "success", "SeniorEditor")

        except Exception as e:
            error_msg = f"评估失败：{str(e)}"
            self.preproduction_panel.evaluation_complete.emit(f"Error: {error_msg}")
            self.log_panel.append_log(f"Evaluation error: {str(e)}", "error")

    def _on_evaluation_complete(self, result: str):
        """评估完成回调"""
        if result.startswith("Error:"):
            self.preproduction_panel.set_error(result.replace("Error:", ""))
        else:
            self.preproduction_panel.set_evaluation_result(result)
        self.preproduction_panel.eval_btn.setEnabled(True)
        self.preproduction_panel.eval_btn.setText("2️⃣ 评估设置")

    def on_approve_and_start(self):
        """从前期筹备面板批准并开始写作"""
        self.log_panel.append_log("Settings approved. Starting generation...", "system")
        self.tabs.setCurrentIndex(1)
        self.check_and_prompt_resume()

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

        worker.log_signal.connect(self.on_log)
        worker.agent_status_signal.connect(self.on_agent_status)
        worker.emotion_curve_signal.connect(self.on_emotion_curve)
        worker.circuit_breaker_signal.connect(self.on_circuit_breaker)
        worker.chapter_complete_signal.connect(self.on_chapter_complete)
        worker.error_signal.connect(self.on_error)
        worker.progress_signal.connect(self.on_progress)

    def on_log(self, message: str, agent: str = None):
        """日志信号处理"""
        if "ERROR" in message.upper():
            level = "error"
        elif "WARNING" in message.upper():
            level = "warning"
        elif "completed" in message.lower():
            level = "success"
        else:
            level = "info"

        self.log_panel.append_log(message, level, agent)

    def on_agent_status(self, data: dict):
        """Agent状态更新"""
        name = data.get("name", "")
        status = data.get("status", "idle")
        self.agent_panel.update_agent_status(name, status)

        # 添加到详情面板日志
        self.detail_panel.add_log(name, f"状态变更: {status}")

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

            rollbacks = 0
            rollback_file = Path(self.project_dir) / "rollback_log.json"
            if rollback_file.exists():
                try:
                    rollback_data = json.loads(rollback_file.read_text(encoding="utf-8"))
                    rollbacks = len(rollback_data.get("rollbacks", []))
                except:
                    pass

            self.circuit_breaker.set_tripped(chapter, reason, rollbacks)
            self.log_panel.append_log(f"CIRCUIT BREAKER TRIGGERED at Chapter {chapter}: {reason}", "error", "CreativeDirector")

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

        # 更新进度条
        if self.progress_bar.isVisible():
            self.progress_bar.setValue(chapter)

        # 显示反馈对话框
        summary = data.get("summary", "")
        quality_score = data.get("quality_score", 0.0)
        logs = data.get("logs", [])

        dialog = ChapterFeedbackDialog(chapter, summary, quality_score, logs, self)
        result = dialog.get_result()

        if result == "rewrite":
            self.log_panel.append_log(f"Chapter {chapter} marked for rewrite", "warning")
        elif result == "edit":
            self.log_panel.append_log(f"Chapter {chapter} opened for manual edit", "info")
        else:
            self.log_panel.append_log(f"Continuing to next chapter", "success")

    def on_error(self, error: str):
        """错误处理"""
        self.log_panel.append_log(f"ERROR: {error}", "error")
        self.agent_panel.update_agent_status("EmotionWriter", "error")

    def on_progress(self, current: int, total: int):
        """进度更新"""
        percentage = int(current / total * 100) if total > 0 else 0
        self.status_bar.showMessage(f"Progress: {current}/{total} chapters ({percentage}%)")

        if self.progress_bar.isVisible():
            self.progress_bar.setValue(current)


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

    # 🔥 关闭"最后一个窗口退出即结束程序"的默认设定
    app.setQuitOnLastWindowClosed(False)

    # 检查是否需要弹出项目设置对话框
    need_setup = False

    if project_dir:
        config_path = Path(project_dir) / "project_config.json"
        if not config_path.exists():
            need_setup = True
    else:
        need_setup = True

    if need_setup:
        dialog = ProjectSetupDialog()

        if dialog.exec() != QDialog.DialogCode.Accepted:
            print("Project setup cancelled by user.")
            sys.exit(0)

        config = dialog.get_project_config()
        if not config:
            print("Failed to get project config")
            sys.exit(1)

        title = config["title"]
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title)
        project_dir = f"novels/{safe_name}"

        Path(project_dir).mkdir(parents=True, exist_ok=True)

        config_path = Path(project_dir) / "project_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"Project created: {project_dir}")
        print(f"Config saved to: {config_path}")

    app.setQuitOnLastWindowClosed(True)

    print("[System] 正在点火，启动赛博编辑部中控大屏 v4.1...")

    window = ProducerDashboard(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
