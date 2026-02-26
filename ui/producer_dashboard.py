"""
Producer Dashboard - 赛博朋克UI重构 (v4.2)
NovelForge v4.2 制片人控制台 - 全面升级版

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
        QGridLayout, QSizePolicy, QDialogButtonBox, QGraphicsDropShadowEffect
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect, QSequentialAnimationGroup
    from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor, QAction, QCursor, QPainter, QPicture, QPixmap
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
# 赛博朋克配色方案 v2.0 - 优化对比度和视觉层次
# ============================================================================
class CyberpunkTheme:
    """赛博朋克主题配色 - v2.0"""

    # === 背景层级 (增加深度) ===
    BG_DEEP = "#050508"         # 最深背景 (页面底层)
    BG_DARK = "#0a0a0f"         # 主背景
    BG_MEDIUM = "#12121a"       # 卡片背景
    BG_LIGHT = "#1a1a25"        # 高亮背景
    BG_HOVER = "#252535"        # 悬停背景
    BG_ACTIVE = "#2a2a40"       # 激活背景

    # === 霓虹主色 (增强饱和度) ===
    FG_PRIMARY = "#00f5f5"       # 主色：更亮的青色
    FG_SECONDARY = "#ff00ff"     # 辅色：洋红
    FG_ACCENT = "#b829dd"        # 强调：紫色
    FG_GOLD = "#ffd700"          # 高光：金色

    # === 功能色 (确保对比度 >= 4.5:1) ===
    FG_SUCCESS = "#00e676"       # 成功：翠绿 (对比度 5.8:1)
    FG_WARNING = "#ffb300"       # 警告：琥珀 (对比度 4.7:1)
    FG_DANGER = "#ff1744"        # 错误：鲜红 (对比度 6.2:1)
    FG_INFO = "#00b0ff"          # 信息：天蓝 (对比度 5.1:1)

    # === 文字颜色 (优化可读性) ===
    TEXT_PRIMARY = "#ffffff"      # 主文字：纯白 (对比度 21:1)
    TEXT_SECONDARY = "#b0b0d0"    # 次要：浅灰蓝 (对比度 8.2:1)
    TEXT_TERTIARY = "#8080a0"     # 第三级：中灰 (对比度 4.8:1)
    TEXT_DIM = "#505060"          # 暗淡：深灰

    # === 边框与分隔 ===
    BORDER_COLOR = "#2a2a40"      # 标准边框
    BORDER_HOVER = "#00f5f5"      # 悬停边框
    BORDER_ACTIVE = "#ff00ff"     # 激活边框
    BORDER_DANGER = "#ff1744"     # 错误边框
    BORDER_SUCCESS = "#00e676"    # 成功边框

    # === 阴影与发光效果 ===
    GLOW_PRIMARY = "0 0 20px rgba(0, 245, 245, 0.4)"
    GLOW_SECONDARY = "0 0 20px rgba(255, 0, 255, 0.4)"
    GLOW_SUCCESS = "0 0 15px rgba(0, 230, 118, 0.4)"
    GLOW_DANGER = "0 0 15px rgba(255, 23, 68, 0.4)"
    SHADOW_CARD = "0 4px 20px rgba(0, 0, 0, 0.5)"
    SHADOW_ELEVATED = "0 8px 30px rgba(0, 0, 0, 0.6)"


# ============================================================================
# 字体系统
# ============================================================================
class Typography:
    """字体系统规范"""

    # 字体族 (带备用字体)
    FONT_DISPLAY = "'Segoe UI', 'Microsoft YaHei', sans-serif"    # 显示字体
    FONT_MONO = "'Consolas', 'Monaco', 'JetBrains Mono', monospace"  # 等宽字体
    FONT_BODY = "'Segoe UI', 'Microsoft YaHei', sans-serif"       # 正文字体

    # 字号规范 (px)
    SIZE_H1 = 20           # 页面标题
    SIZE_H2 = 16           # 面板标题
    SIZE_H3 = 14           # 卡片标题
    SIZE_BODY = 12         # 正文
    SIZE_SMALL = 10        # 辅助文字
    SIZE_TINY = 9          # 标签/时间戳

    # 字重
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_BOLD = 700


# ============================================================================
# 间距系统 (基于 4px 网格)
# ============================================================================
class Spacing:
    """间距规范"""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32

    # 组件间距
    PADDING_CARD = 12
    PADDING_INPUT = "8px 12px"
    PADDING_BUTTON = "6px 12px"

    # 圆角
    RADIUS_SM = 4
    RADIUS_MD = 6
    RADIUS_LG = 8
    RADIUS_XL = 12


# ============================================================================
# 布局常量
# ============================================================================
class Layout:
    """布局常量"""

    # 窗口尺寸
    WINDOW_MIN_WIDTH = 1400
    WINDOW_MIN_HEIGHT = 800
    WINDOW_DEFAULT_WIDTH = 1600
    WINDOW_DEFAULT_HEIGHT = 900

    # 面板宽度 (像素)
    PANEL_LEFT_MIN = 300
    PANEL_LEFT_MAX = 400
    PANEL_RIGHT_MIN = 320
    PANEL_RIGHT_MAX = 400
    PANEL_CENTER_MIN = 500

    # Agent 工牌尺寸
    AGENT_CARD_WIDTH = 280
    AGENT_CARD_HEIGHT = 120


# ============================================================================
# 主题管理器 - 支持多主题切换
# ============================================================================
class ThemeManager:
    """主题管理器 - 支持动态切换主题"""

    # 主题定义
    THEMES = {
        "cyberpunk": {
            "name": "赛博朋克",
            "colors": {
                "BG_DEEP": "#050508",
                "BG_DARK": "#0a0a0f",
                "BG_MEDIUM": "#12121a",
                "BG_LIGHT": "#1a1a25",
                "BG_HOVER": "#252535",
                "FG_PRIMARY": "#00f5f5",
                "FG_SECONDARY": "#ff00ff",
                "FG_ACCENT": "#b829dd",
                "FG_GOLD": "#ffd700",
                "FG_SUCCESS": "#00e676",
                "FG_WARNING": "#ffb300",
                "FG_DANGER": "#ff1744",
                "FG_INFO": "#00b0ff",
                "TEXT_PRIMARY": "#ffffff",
                "TEXT_SECONDARY": "#b0b0d0",
                "TEXT_TERTIARY": "#8080a0",
                "BORDER_COLOR": "#2a2a40",
            }
        },
        "neon_blue": {
            "name": "霓虹蓝",
            "colors": {
                "BG_DEEP": "#030712",
                "BG_DARK": "#0f172a",
                "BG_MEDIUM": "#1e293b",
                "BG_LIGHT": "#334155",
                "BG_HOVER": "#475569",
                "FG_PRIMARY": "#38bdf8",
                "FG_SECONDARY": "#818cf8",
                "FG_ACCENT": "#c084fc",
                "FG_GOLD": "#fbbf24",
                "FG_SUCCESS": "#22c55e",
                "FG_WARNING": "#f59e0b",
                "FG_DANGER": "#ef4444",
                "FG_INFO": "#0ea5e9",
                "TEXT_PRIMARY": "#f8fafc",
                "TEXT_SECONDARY": "#cbd5e1",
                "TEXT_TERTIARY": "#94a3b8",
                "BORDER_COLOR": "#334155",
            }
        },
        "sunset": {
            "name": "日落",
            "colors": {
                "BG_DEEP": "#1a0a0a",
                "BG_DARK": "#2d1515",
                "BG_MEDIUM": "#3d2020",
                "BG_LIGHT": "#4d2a2a",
                "BG_HOVER": "#5d3535",
                "FG_PRIMARY": "#fb923c",
                "FG_SECONDARY": "#f472b6",
                "FG_ACCENT": "#a78bfa",
                "FG_GOLD": "#fbbf24",
                "FG_SUCCESS": "#4ade80",
                "FG_WARNING": "#fbbf24",
                "FG_DANGER": "#f87171",
                "FG_INFO": "#38bdf8",
                "TEXT_PRIMARY": "#fef3c7",
                "TEXT_SECONDARY": "#fcd34d",
                "TEXT_TERTIARY": "#d97706",
                "BORDER_COLOR": "#7f1d1d",
            }
        },
        "forest": {
            "name": "森林",
            "colors": {
                "BG_DEEP": "#052e16",
                "BG_DARK": "#064e3b",
                "BG_MEDIUM": "#065f46",
                "BG_LIGHT": "#047857",
                "BG_HOVER": "#059669",
                "FG_PRIMARY": "#34d399",
                "FG_SECONDARY": "#a7f3d0",
                "FG_ACCENT": "#6ee7b7",
                "FG_GOLD": "#fcd34d",
                "FG_SUCCESS": "#10b981",
                "FG_WARNING": "#f59e0b",
                "FG_DANGER": "#ef4444",
                "FG_INFO": "#06b6d4",
                "TEXT_PRIMARY": "#ecfdf5",
                "TEXT_SECONDARY": "#a7f3d0",
                "TEXT_TERTIARY": "#6ee7b7",
                "BORDER_COLOR": "#064e3b",
            }
        },
    }

    current_theme = "cyberpunk"

    @classmethod
    def get_theme(cls, theme_name: str = None) -> dict:
        """获取主题配置"""
        if theme_name is None:
            theme_name = cls.current_theme
        return cls.THEMES.get(theme_name, cls.THEMES["cyberpunk"])

    @classmethod
    def set_theme(cls, theme_name: str):
        """设置当前主题"""
        if theme_name in cls.THEMES:
            cls.current_theme = theme_name

    @classmethod
    def get_theme_names(cls) -> list:
        """获取所有主题名称"""
        return [f"{v['name']} ({k})" for k, v in cls.THEMES.items()]

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """获取当前主题的指定颜色"""
        theme = cls.get_theme()
        return theme["colors"].get(color_name, "#000000")


# ============================================================================
# 主题切换组件
# ============================================================================
class ThemeSelector(QWidget):
    """主题选择器组件"""

    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setFixedHeight(32)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
            }}
            QLabel {{
                background: transparent;
                color: {CyberpunkTheme.TEXT_SECONDARY};
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QComboBox {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 4px 8px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QComboBox:hover {{
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)

        # 标签
        label = QLabel("主题:")
        layout.addWidget(label)

        # 主题选择下拉框
        self.combo = QComboBox()
        for theme_key, theme_data in ThemeManager.THEMES.items():
            self.combo.addItem(theme_data["name"], theme_key)
        self.combo.setCurrentText(ThemeManager.THEMES[ThemeManager.current_theme]["name"])
        self.combo.currentIndexChanged.connect(self._on_theme_changed)
        layout.addWidget(self.combo)

    def _on_theme_changed(self):
        """主题切换事件"""
        theme_key = self.combo.currentData()
        ThemeManager.set_theme(theme_key)
        self.theme_changed.emit(theme_key)


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
    """Agent工牌背面 - 显示详细信息 v2.0"""

    def __init__(self, agent_info: dict, parent=None):
        super().__init__(parent)
        self.agent_info = agent_info
        self.init_ui()

    def init_ui(self):
        """初始化背面UI - v2.0"""
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {CyberpunkTheme.BG_LIGHT},
                    stop:1 {CyberpunkTheme.BG_MEDIUM});
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # 标题：详细信息
        title = QLabel("📋 AGENT INFO")
        title.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY, Typography.WEIGHT_BOLD))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        layout.addWidget(title)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {CyberpunkTheme.BORDER_COLOR};")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # 功能描述
        desc_label = QLabel(self.agent_info.get('description', 'N/A'))
        desc_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        desc_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addSpacing(8)

        # 最近活动
        activity = self.agent_info.get('last_activity', '无')
        activity_label = QLabel(f"🕐 {activity}")
        activity_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))
        activity_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        layout.addWidget(activity_label)

        # 统计信息
        chapters = self.agent_info.get('chapters_processed', 0)
        errors = self.agent_info.get('error_count', 0)
        stats_text = f"📊 章节: {chapters} | 错误: {errors}"
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))

        # 根据错误数决定颜色
        error_color = CyberpunkTheme.FG_DANGER if errors > 0 else CyberpunkTheme.TEXT_TERTIARY
        stats_label.setStyleSheet(f"color: {error_color};")
        layout.addWidget(stats_label)

        layout.addStretch()

        # 点击提示
        hint = QLabel("↩ 点击返回")
        hint.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))
        hint.setStyleSheet(f"color: {CyberpunkTheme.TEXT_DIM};")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)






class MiniAgentBadge(QFrame):
    """侧边栏迷你工牌 - 极致省流"""
    clicked = pyqtSignal(str)
    
    def __init__(self, name: str, emoji: str):
        super().__init__()
        self.agent_name = name
        self.setFixedHeight(40)
        self.setStyleSheet(f"background-color: {CyberpunkTheme.BG_LIGHT}; border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 6px;")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        self.emoji_label = QLabel(emoji)
        self.emoji_label.setFont(QFont("Segoe UI Emoji", 14))
        layout.addWidget(self.emoji_label)
        
        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.name_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY}; border: none; background: transparent;")
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS}; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(self.status_dot)
        
    def mousePressEvent(self, event):
        self.clicked.emit(self.agent_name)
        
    def set_status(self, color_hex: str):
        self.status_dot.setStyleSheet(f"color: {color_hex}; font-size: 14px; border: none; background: transparent;")
        # 工作时给边框发光
        if color_hex != CyberpunkTheme.FG_SUCCESS:
            self.setStyleSheet(f"background-color: {CyberpunkTheme.BG_HOVER}; border: 1px solid {color_hex}; border-radius: 6px;")
        else:
            self.setStyleSheet(f"background-color: {CyberpunkTheme.BG_LIGHT}; border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 6px;")



# ============================================================================
# 极简 3D 翻转实体工牌 - 纯正血统版
# ============================================================================
class MinimalistBadge(QFrame):
    """极简实体工牌组件 - 纵向比例 3:4，带物理挂绳，按压翻面"""
    
    card_clicked = pyqtSignal(str)
    
    def __init__(self, name: str, role: str, description: str, 
                 avatar_path: str = None, emoji: str = "🤖", parent=None):
        super().__init__(parent)
        self.agent_name = name
        self.agent_role = role
        self.agent_desc = description
        self.avatar_path = avatar_path
        self.emoji = emoji
        self.current_status = "idle"
        self.current_task = ""
        self.is_back = False
        
        # 尺寸设定 (纵向ID卡)
        self.BADGE_WIDTH = 220
        self.BADGE_HEIGHT = 300
        self.ROPE_HEIGHT = 50
        
        self.init_ui()
        self.init_animations()
        
    def init_ui(self):
        self.setFixedSize(self.BADGE_WIDTH, self.BADGE_HEIGHT + self.ROPE_HEIGHT)
        self.setStyleSheet("background: transparent; border: none;")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # 核心翻转容器
        self.container = QFrame(self)
        self.container.setGeometry(0, self.ROPE_HEIGHT, self.BADGE_WIDTH, self.BADGE_HEIGHT)
        
        # --- 正面 (Front) ---
        self.front = QFrame(self.container)
        self.front.setGeometry(0, 0, self.BADGE_WIDTH, self.BADGE_HEIGHT)
        self.front_style = f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border-radius: 12px;
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-left: 4px solid {CyberpunkTheme.FG_SUCCESS};
            }}
            QLabel {{ border: none; background: transparent; }}
        """
        self.front.setStyleSheet(self.front_style)
        
        # 阴影
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(self.shadow)
        
        # 挂绳 (Rope)
        self.rope = QFrame(self)
        self.rope.setGeometry(int(self.BADGE_WIDTH/2 - 15), 0, 30, self.ROPE_HEIGHT)
        self.rope.setStyleSheet(f"background-color: {CyberpunkTheme.BG_DEEP}; border-radius: 4px;")
        self.clip = QFrame(self)
        self.clip.setGeometry(int(self.BADGE_WIDTH/2 - 20), self.ROPE_HEIGHT - 5, 40, 12)
        self.clip.setStyleSheet("background-color: #333333; border-radius: 3px; border: 1px solid #555;")
        
        fl = QVBoxLayout(self.front)
        fl.setContentsMargins(15, 15, 15, 15)
        fl.setSpacing(15)
        
        # 顶部标签
        self.name_tag = QLabel(self.agent_name)
        self.name_tag.setFont(QFont(Typography.FONT_MONO, 13, QFont.Weight.Bold))
        self.name_tag.setStyleSheet(f"color: {CyberpunkTheme.BG_DEEP}; background-color: {CyberpunkTheme.TEXT_SECONDARY}; padding: 6px; border-radius: 4px;")
        self.name_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self.name_tag)
        
        # 头像区
        self.avatar_container = QFrame()
        self.avatar_container.setFixedSize(80, 80)
        self.avatar_container.setStyleSheet(f"background-color: {CyberpunkTheme.BG_DARK}; border-radius: 12px; border: 2px solid {CyberpunkTheme.BORDER_COLOR};")
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.avatar_path and os.path.exists(self.avatar_path):
            pixmap = QPixmap(self.avatar_path)
            if not pixmap.isNull():
                self.avatar_label.setPixmap(pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        else:
            self.avatar_label.setText(self.emoji)
            self.avatar_label.setFont(QFont("Segoe UI Emoji", 32))
            
        al = QVBoxLayout(self.avatar_container)
        al.setContentsMargins(0,0,0,0)
        al.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self.avatar_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 职位
        self.role_label = QLabel(self.agent_role)
        self.role_label.setFont(QFont(Typography.FONT_BODY, 11, QFont.Weight.Bold))
        self.role_label.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        self.role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self.role_label)
        
        fl.addStretch()
        
        # 状态区
        bl = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS}; font-size: 14px;")
        self.status_text = QLabel("IDLE")
        self.status_text.setFont(QFont(Typography.FONT_MONO, 10, QFont.Weight.Bold))
        self.status_text.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        bl.addWidget(self.status_dot)
        bl.addWidget(self.status_text)
        bl.addStretch()
        fl.addLayout(bl)
        
        # --- 背面 (Back) ---
        self.back = QFrame(self.container)
        self.back.setGeometry(0, 0, self.BADGE_WIDTH, self.BADGE_HEIGHT)
        self.back.setStyleSheet(f"background-color: {CyberpunkTheme.BG_DEEP}; border-radius: 12px; border: 1px solid {CyberpunkTheme.FG_PRIMARY};")
        self.back.hide()
        
        bkl = QVBoxLayout(self.back)
        bkl.setContentsMargins(15, 15, 15, 15)
        
        hl = QHBoxLayout()
        hl.addWidget(QLabel("←", styleSheet=f"color: {CyberpunkTheme.FG_PRIMARY}; font-size: 16px; font-weight: bold;"))
        hl.addWidget(QLabel("SYS_ARCHIVE", styleSheet=f"color: {CyberpunkTheme.FG_PRIMARY}; font-size: 11px; font-weight: bold;"))
        hl.addStretch()
        bkl.addLayout(hl)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {CyberpunkTheme.BORDER_COLOR};")
        bkl.addWidget(line)
        
        self.desc_label = QLabel(self.agent_desc)
        self.desc_label.setFont(QFont(Typography.FONT_BODY, 9))
        self.desc_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY}; line-height: 1.5;")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        bkl.addWidget(self.desc_label)
        
        self.task_label = QLabel("Task: None")
        self.task_label.setFont(QFont(Typography.FONT_MONO, 9))
        self.task_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY}; font-style: italic;")
        self.task_label.setWordWrap(True)
        bkl.addWidget(self.task_label)
        
        bkl.addStretch()
        barcode = QLabel("||||| || | |||| || |")
        barcode.setFont(QFont("Consolas", 12))
        barcode.setStyleSheet(f"color: {CyberpunkTheme.TEXT_DIM};")
        barcode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bkl.addWidget(barcode)
        
    def init_animations(self):
        self.anim_group = QSequentialAnimationGroup()
        self.press_anim = QPropertyAnimation(self.container, b"geometry")
        self.press_anim.setDuration(120)
        self.release_anim = QPropertyAnimation(self.container, b"geometry")
        self.release_anim.setDuration(300)
        self.release_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim_group.addAnimation(self.press_anim)
        self.anim_group.addAnimation(self.release_anim)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cg = self.container.geometry()
            cx, cy = cg.x() + cg.width()//2, cg.y() + cg.height()//2
            sw, sh = cg.width() - 20, cg.height() - 20
            
            self.press_anim.setStartValue(cg)
            self.press_anim.setEndValue(QRect(cx - sw//2, cy - sh//2, sw, sh))
            self.release_anim.setStartValue(QRect(cx - sw//2, cy - sh//2, sw, sh))
            self.release_anim.setEndValue(cg)
            
            try: self.press_anim.finished.disconnect()
            except: pass
            self.press_anim.finished.connect(self.switch_face)
            self.anim_group.start()
            
            self.card_clicked.emit(self.agent_name)
            
    def switch_face(self):
        self.is_back = not self.is_back
        if self.is_back:
            self.front.hide()
            self.back.show()
            self.shadow.setColor(QColor(0, 0, 0, 30))
        else:
            self.back.hide()
            self.front.show()
            self.shadow.setColor(QColor(0, 0, 0, 100))
            
    def set_status(self, status: str, task: str = ""):
        colors = {
            "idle": CyberpunkTheme.FG_SUCCESS, "thinking": CyberpunkTheme.FG_INFO,
            "writing": CyberpunkTheme.FG_PRIMARY, "auditing": CyberpunkTheme.FG_ACCENT,
            "conflict": CyberpunkTheme.FG_DANGER, "error": CyberpunkTheme.FG_DANGER,
            "suspended": CyberpunkTheme.FG_WARNING
        }
        color = colors.get(status.lower(), CyberpunkTheme.FG_SUCCESS)
        
        # 变色灯条
        self.front.setStyleSheet(self.front_style.replace(CyberpunkTheme.FG_SUCCESS, color))
        self.status_dot.setStyleSheet(f"color: {color}; font-size: 14px;")
        
        dt = status.upper()
        if task: dt += f": {task[:8]}..." if len(task)>8 else f": {task}"
        self.status_text.setText(dt)
        self.status_text.setStyleSheet(f"color: {color if status.lower() != 'idle' else CyberpunkTheme.TEXT_SECONDARY};")
        
        self.task_label.setText(f"Task: {task}" if task else "Task: None")
        self.task_label.setStyleSheet(f"color: {color};" if task else f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        
    def update_info(self, agent_info: dict):
        self.agent_desc = agent_info.get("description", self.agent_desc)
        self.desc_label.setText(self.agent_desc)

# ============================================================================
# Agent 详细信息面板 (原样保留，修复依赖)
# ============================================================================
class AgentDetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_agent = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"QWidget {{ background-color: {CyberpunkTheme.BG_MEDIUM}; border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 4px; }}")
        layout = QVBoxLayout(self)
        title = QLabel("📋 Agent 详细信息")
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY}; font-weight: bold; border:none;")
        layout.addWidget(title)
        
        self.agent_combo = QComboBox()
        layout.addWidget(self.agent_combo)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)
        
        layout.addWidget(QLabel("📝 工作日志", styleSheet="border:none; color:"+CyberpunkTheme.TEXT_SECONDARY))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text, stretch=1)

    def set_agents(self, agents: Dict[str, MinimalistBadge]):
        self.agent_combo.clear()
        self.agent_combo.addItems(agents.keys())
        self.agent_cards = agents
        self.agent_combo.currentTextChanged.connect(self.on_agent_selected)

    def on_agent_selected(self, name: str):
        self.selected_agent = name
        if name in self.agent_cards:
            card = self.agent_cards[name]
            self.info_text.setPlainText(f"【{card.emoji} {name}】\n角色: {card.agent_role}\n状态: {card.current_status}\n当前任务: {card.current_task or '无'}\n\n描述: {card.agent_desc}")

    def add_log(self, agent_name: str, log: str):
        if self.selected_agent == agent_name:
            self.log_text.append(f"{datetime.now().strftime('%H:%M:%S')} - {log}")

# ============================================================================
# Agent 矩阵面板 (核心替换区)
# ============================================================================
class AgentMatrixPanel(QWidget):
    agent_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"QWidget {{ background-color: {CyberpunkTheme.BG_DARK}; border: none; }}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🤖 AGENT MATRIX", styleSheet=f"color: {CyberpunkTheme.FG_PRIMARY}; font-size: 16px; font-weight: bold;"))
        
        self.agent_scroll = QScrollArea()
        self.agent_scroll.setWidgetResizable(True)
        self.agent_container = QWidget()
        self.agent_flow_layout = QGridLayout(self.agent_container)
        self.agent_flow_layout.setSpacing(20)
        self.agent_scroll.setWidget(self.agent_container)
        
        # 自动定位头像路径 (如果代码在 ui/ 下，头像在ui/avatars 下)
        AVATAR_DIR = str(Path(__file__).resolve().parent / "avatars")
        
        self.agents_config = {
            "InitializerAgent": MinimalistBadge("Initializer", "建组设定", "负责项目初始化和基础设定构建", f"{AVATAR_DIR}/avatar_08.png", "🏗️"),
            "PromptAssembler": MinimalistBadge("PromptMixer", "指令聚合", "将多Agent意图聚合为单次Prompt，防止Token爆炸", f"{AVATAR_DIR}/pixel_avatar_01.png", "🎛️"),
            "ElasticArchitect": MinimalistBadge("ElasticArch", "迷雾开图", "动态生成剧情。近景清晰，远景仅保留情绪目标", f"{AVATAR_DIR}/pixel_avatar_02.png", "🗺️"),
            "EmotionWriter": MinimalistBadge("EmotionWriter", "场景生成", "注入情绪张量，依据预期爽点动态调整文字节奏", f"{AVATAR_DIR}/pixel_avatar_03.png", "✍️"),
            "PayoffAuditor": MinimalistBadge("PayoffAuditor", "情绪核算", "精准核算预期张力与实际生成张力的Gap值", f"{AVATAR_DIR}/pixel_avatar_04.png", "🧮"),
            "ConsistencyGuardian": MinimalistBadge("Consistency", "一致性守护", "滑动窗口检测。严防死而复生、时间倒流等毒点", f"{AVATAR_DIR}/pixel_avatar_05.png", "🛡️"),
            "CreativeDirector": MinimalistBadge("CreativeDir", "仲裁回滚", "掌握生杀大权。超阈值强制回滚，触发全局熔断", f"{AVATAR_DIR}/pixel_avatar_07.png", "👑"),
            "StyleAnchor": MinimalistBadge("StyleAnchor", "特征对齐", "提取黄金三章特征向量，确保百万字文风统一", f"{AVATAR_DIR}/pixel_avatar_08.png", "🎨"),
            "WorldBible": MinimalistBadge("WorldBible", "事件溯源", "Event Sourcing状态机。记录实体属性变迁", f"{AVATAR_DIR}/20150225214245_JW4Uh.jpeg", "📚"),
            "EmotionTracker": MinimalistBadge("EmotionTracker", "情绪债务", "使用纯Python逻辑计算情绪债务，拒绝LLM算术灾难", f"{AVATAR_DIR}/20220411174400_1997f.jpg", "📉")
        }

        row, col = 0, 0
        for name, card in self.agents_config.items():
            self.agent_flow_layout.addWidget(card, row, col)
            card.card_clicked.connect(lambda n=name: self.agent_clicked.emit(n))
            self.agent_cards = self.agents_config
            col += 1
            if col >= 3:  # 因为卡片变宽变高了，每行排2个最佳
                col = 0
                row += 1

        layout.addWidget(self.agent_scroll)

    def update_agent_status(self, name: str, status: str, task: str = ""):
        if name in self.agent_cards:
            self.agent_cards[name].set_status(status, task)

# ============================================================================
# 情绪波浪图面板 v2.0（美化版）
# ============================================================================
class EmotionWavePanel(QWidget):
    """情绪波浪图面板 - 美化版"""

    # 阈值线颜色
    THRESHOLD_DANGER = 70
    THRESHOLD_WARNING = 40

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI - v2.0"""
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {CyberpunkTheme.BG_MEDIUM},
                    stop:1 {CyberpunkTheme.BG_DARK});
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # === 标题栏 ===
        header = QFrame()
        header.setStyleSheet(f"background: transparent; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("📈 EMOTION WAVE")
        title.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # 图例
        legend = QLabel("<span style='color: {0};'>● Expected</span> <span style='color: {1};'>● Actual</span>".format(
            CyberpunkTheme.FG_PRIMARY, CyberpunkTheme.FG_DANGER
        ))
        legend.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))
        header_layout.addWidget(legend)

        layout.addWidget(header)

        # 副标题
        subtitle = QLabel("Expected vs Actual Tension Curve")
        subtitle.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))
        subtitle.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        layout.addWidget(subtitle)

        if PYQTGRAPH_AVAILABLE:
            # 创建图表容器
            chart_frame = QFrame()
            chart_frame.setStyleSheet(f"""
                QFrame {{
                    background: {CyberpunkTheme.BG_DEEP};
                    border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                    border-radius: {Spacing.RADIUS_MD}px;
                }}
            """)
            chart_layout = QVBoxLayout(chart_frame)
            chart_layout.setContentsMargins(4, 4, 4, 4)

            # 创建图表
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground(CyberpunkTheme.BG_DEEP)
            self.plot_widget.setMinimumHeight(180)
            self.plot_widget.setMaximumHeight(250)

            # 配置图表样式
            self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(color=CyberpunkTheme.TEXT_TERTIARY))
            self.plot_widget.getAxis('left').setTextPen(pg.mkPen(color=CyberpunkTheme.TEXT_TERTIARY))
            self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color=CyberpunkTheme.BORDER_COLOR))
            self.plot_widget.getAxis('left').setPen(pg.mkPen(color=CyberpunkTheme.BORDER_COLOR))

            # 配置标签
            self.plot_widget.setLabel('bottom', 'Chapter', color=CyberpunkTheme.TEXT_SECONDARY, size='8pt')
            self.plot_widget.setLabel('left', 'Tension', color=CyberpunkTheme.TEXT_SECONDARY, size='8pt')

            # 网格线 - 虚线样式
            self.plot_widget.showGrid(x=True, y=True, alpha=0.2)

            # 阈值线 - 危险级别
            self.danger_line = pg.InfiniteLine(
                pos=self.THRESHOLD_DANGER, angle=0,
                pen=pg.mkPen(color=CyberpunkTheme.FG_DANGER, width=1, style=Qt.PenStyle.DashLine),
                label='Danger', labelOpts={'color': CyberpunkTheme.FG_DANGER, 'position': 0.95}
            )
            self.plot_widget.addItem(self.danger_line)

            # 阈值线 - 警告级别
            self.warning_line = pg.InfiniteLine(
                pos=self.THRESHOLD_WARNING, angle=0,
                pen=pg.mkPen(color=CyberpunkTheme.FG_WARNING, width=1, style=Qt.PenStyle.DashLine),
                label='Warning', labelOpts={'color': CyberpunkTheme.FG_WARNING, 'position': 0.95}
            )
            self.plot_widget.addItem(self.warning_line)

            # 预期曲线 - 霓虹青色 (发光效果通过更宽的线模拟)
            self.expected_curve = self.plot_widget.plot(
                [], [],
                pen=pg.mkPen(color=CyberpunkTheme.FG_PRIMARY, width=3),
                name='Expected',
                symbol=None
            )
            # 添加发光效果 (较细的高亮线)
            self.expected_glow = self.plot_widget.plot(
                [], [],
                pen=pg.mkPen(color=CyberpunkTheme.FG_PRIMARY, width=1, alpha=0.3),
            )

            # 实际曲线 - 霓虹红色
            self.actual_curve = self.plot_widget.plot(
                [], [],
                pen=pg.mkPen(color=CyberpunkTheme.FG_DANGER, width=3),
                name='Actual',
                symbol='o',
                symbolSize=6,
                symbolBrush=CyberpunkTheme.FG_DANGER,
                symbolPen=None
            )
            # 发光效果
            self.actual_glow = self.plot_widget.plot(
                [], [],
                pen=pg.mkPen(color=CyberpunkTheme.FG_DANGER, width=1, alpha=0.3),
            )

            # 数据点标记 (最新点)
            self.current_point = self.plot_widget.plot(
                [], [],
                symbol='star',
                symbolSize=12,
                symbolBrush=CyberpunkTheme.FG_GOLD,
                symbolPen=pg.mkPen(color=CyberpunkTheme.TEXT_PRIMARY, width=2),
                pen=None
            )

            # 设置Y轴范围 (给标签留出空间)
            self.plot_widget.setYRange(0, 100, padding=0.1)
            self.plot_widget.setXRange(0, 50, padding=0.05)

            chart_layout.addWidget(self.plot_widget)
            layout.addWidget(chart_frame, stretch=1)
        else:
            # 备用显示
            self.fallback_label = QLabel("⚠️ pyqtgraph not available")
            self.fallback_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY))
            self.fallback_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")
            self.fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.fallback_label, stretch=1)

        # === 统计信息栏 ===
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
            }}
            QLabel {{
                padding: 4px 8px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS)
        stats_layout.setSpacing(0)

        # 章节进度
        self.chapter_label = QLabel("📖 Ch: 0/0")
        self.chapter_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.chapter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY};")
        stats_layout.addWidget(self.chapter_label)

        stats_layout.addStretch()

        # 情绪债务 - 带颜色指示
        debt_container = QFrame()
        debt_layout = QHBoxLayout(debt_container)
        debt_layout.setContentsMargins(0, 0, 0, 0)
        debt_layout.setSpacing(4)

        debt_icon = QLabel("⚡")
        debt_icon.setStyleSheet(f"font-size: {Typography.SIZE_SMALL}px;")
        debt_layout.addWidget(debt_icon)

        self.debt_label = QLabel("Debt: 0.0")
        self.debt_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL, Typography.WEIGHT_BOLD))
        self.debt_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        debt_layout.addWidget(self.debt_label)

        stats_layout.addWidget(debt_container)

        # 状态指示
        self.status_label = QLabel("🟢 Normal")
        self.status_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        stats_layout.addWidget(self.status_label)

        layout.addWidget(stats_frame)

    def update_curve(self, expected: List[float], actual: List[float], chapter: int, total: int):
        """更新曲线 - v2.0"""
        if not PYQTGRAPH_AVAILABLE:
            return

        # 更新数据
        x = list(range(1, len(expected) + 1))

        # 主曲线
        self.expected_curve.setData(x, expected)
        self.actual_curve.setData(x, actual)

        # 发光效果 (略微偏移的数据)
        if len(x) > 0:
            self.expected_glow.setData(x, [y + 1 for y in expected])
            self.actual_glow.setData(x, [y + 1 for y in actual])

        # 当前点标记 (最后一个点)
        if actual and len(actual) > 0:
            self.current_point.setData([len(actual)], [actual[-1]])

        # 动态调整X轴范围
        max_x = max(50, len(expected) + 5)
        self.plot_widget.setXRange(0, max_x, padding=0.05)

        # 更新统计
        self.chapter_label.setText(f"📖 Ch: {chapter}/{total}")

        # 计算当前债务
        if actual:
            current_debt = actual[-1]
            self.debt_label.setText(f"Debt: {current_debt:.1f}")

            # 根据债务值改变颜色和状态
            if current_debt > self.THRESHOLD_DANGER:
                color = CyberpunkTheme.FG_DANGER
                status_text = "🔴 CRITICAL"
                status_color = CyberpunkTheme.FG_DANGER
            elif current_debt > self.THRESHOLD_WARNING:
                color = CyberpunkTheme.FG_WARNING
                status_text = "🟡 Warning"
                status_color = CyberpunkTheme.FG_WARNING
            else:
                color = CyberpunkTheme.FG_SUCCESS
                status_text = "🟢 Normal"
                status_color = CyberpunkTheme.FG_SUCCESS

            self.debt_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"color: {status_color};")


# ============================================================================
# 自动保存指示器
# ============================================================================
class AutoSaveIndicator(QWidget):
    """自动保存状态指示器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = "saved"  # saved, saving, unsaved
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(120, 28)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # 状态指示灯
        self.light = QLabel()
        self.light.setFixedSize(8, 8)
        self.light.setStyleSheet(f"""
            background-color: {CyberpunkTheme.FG_SUCCESS};
            border-radius: 4px;
        """)
        layout.addWidget(self.light)

        # 状态文字
        self.text = QLabel("已保存")
        self.text.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.text.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        layout.addWidget(self.text)

    def set_saving(self):
        """设置保存中状态"""
        self.status = "saving"
        self.light.setStyleSheet(f"""
            background-color: {CyberpunkTheme.FG_WARNING};
            border-radius: 4px;
        """)
        self.text.setText("保存中...")
        self.text.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")

    def set_saved(self):
        """设置已保存状态"""
        self.status = "saved"
        self.light.setStyleSheet(f"""
            background-color: {CyberpunkTheme.FG_SUCCESS};
            border-radius: 4px;
        """)
        self.text.setText("已保存")
        self.text.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")

    def set_unsaved(self):
        """设置未保存状态"""
        self.status = "unsaved"
        self.light.setStyleSheet(f"""
            background-color: {CyberpunkTheme.FG_DANGER};
            border-radius: 4px;
        """)
        self.text.setText("未保存")
        self.text.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER};")


# ============================================================================
# 评估卡片组件 - 卡片式展示评估建议
# ============================================================================
class EvaluationCard(QFrame):
    """评估建议卡片组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_DARK};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # 标题栏
        header = QHBoxLayout()

        self.icon_label = QLabel("●")
        self.icon_label.setFont(QFont(Typography.FONT_MONO, 12))
        self.icon_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        header.addWidget(self.icon_label)

        self.title_label = QLabel("评估建议")
        self.title_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
        self.title_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        header.addWidget(self.title_label)

        header.addStretch()

        self.score_label = QLabel("")
        self.score_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_H3, Typography.WEIGHT_BOLD))
        header.addWidget(self.score_label)

        layout.addLayout(header)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {CyberpunkTheme.BORDER_COLOR};")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # 内容区域
        self.content = QTextBrowser()
        self.content.setPlaceholderText("点击「评估设置」按钮获取资深编辑的诊断建议...")
        self.content.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY))
        self.content.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                color: {CyberpunkTheme.TEXT_SECONDARY};
            }}
        """)
        self.content.setMaximumHeight(150)
        layout.addWidget(self.content)

    def set_evaluation(self, text: str, score: int = None):
        """设置评估内容"""
        self.content.setText(text)

        if score is not None:
            self.score_label.setText(f"{score}/100")
            if score >= 80:
                color = CyberpunkTheme.FG_SUCCESS
            elif score >= 60:
                color = CyberpunkTheme.FG_WARNING
            else:
                color = CyberpunkTheme.FG_DANGER
            self.score_label.setStyleSheet(f"color: {color};")
            self.icon_label.setStyleSheet(f"color: {color};")

    def clear(self):
        """清空内容"""
        self.content.clear()
        self.score_label.clear()
        self.icon_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")


# ============================================================================
# 实时日志面板（带筛选和语法高亮）
# ============================================================================
class LogPanel(QWidget):
    """实时日志面板 - 带Agent筛选和语法高亮 v2.0"""

    # 日志级别图标映射
    LEVEL_ICONS = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
        "system": "⚡",
    }

    # 关键字高亮颜色
    KEYWORD_COLORS = {
        "PASS": CyberpunkTheme.FG_SUCCESS,
        "FAIL": CyberpunkTheme.FG_DANGER,
        "REWRITE": CyberpunkTheme.FG_WARNING,
        "ROLLBACK": CyberpunkTheme.FG_DANGER,
        "SUSPEND": CyberpunkTheme.FG_DANGER,
        "Chapter": CyberpunkTheme.FG_PRIMARY,
        "Emotion": CyberpunkTheme.FG_ACCENT,
        "ERROR": CyberpunkTheme.FG_DANGER,
        "completed": CyberpunkTheme.FG_SUCCESS,
        "generating": CyberpunkTheme.FG_INFO,
        "auditing": CyberpunkTheme.FG_ACCENT,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_count = 0
        self.max_logs = 1000  # 最大日志条数，防止内存溢出
        self.all_logs = []  # 存储所有日志，用于过滤
        self.init_ui()

    def init_ui(self):
        """初始化UI - v2.0"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QFrame {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
            QComboBox {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 4px 8px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QComboBox:hover {{
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
            QPushButton {{
                background: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 6px 12px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QPushButton:hover {{
                background: {CyberpunkTheme.BG_HOVER};
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # === 标题栏 ===
        header = QFrame()
        header.setFixedHeight(40)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(Spacing.MD, 0, Spacing.MD, 0)
        header_layout.setSpacing(Spacing.SM)

        # 标题
        title = QLabel("📋 ARBITRATION LOG")
        title.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_SECONDARY};")
        header_layout.addWidget(title)

        # 日志计数
        self.count_label = QLabel("0 entries")
        self.count_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_TINY))
        self.count_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        header_layout.addWidget(self.count_label)

        header_layout.addStretch()

        # Agent筛选
        filter_label = QLabel("Filter:")
        filter_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        filter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        header_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "EmotionWriter", "CreativeDirector", "EmotionTracker",
                                     "ConsistencyGuardian", "StyleAnchor", "WorldBible", "InitializerAgent"])
        self.filter_combo.setFixedWidth(140)
        self.filter_combo.currentTextChanged.connect(self._apply_filters)
        header_layout.addWidget(self.filter_combo)

        # 搜索框
        search_label = QLabel("搜索:")
        search_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        search_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        header_layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("关键词...")
        self.search_box.setFixedWidth(120)
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 4px 8px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QLineEdit:focus {{
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)
        self.search_box.textChanged.connect(self._apply_filters)
        header_layout.addWidget(self.search_box)

        # 清空按钮
        clear_btn = QPushButton("清空")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(clear_btn)

        layout.addWidget(header)

        # === 日志区域 ===
        self.log_frame = QFrame()
        self.log_frame.setStyleSheet(f"""
            QFrame {{
                background: {CyberpunkTheme.BG_DEEP};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
        """)
        log_layout = QVBoxLayout(self.log_frame)
        log_layout.setContentsMargins(0, 0, 0, 0)

        self.log_text = QTextBrowser()
        self.log_text.setReadOnly(True)
        self.log_text.setOpenExternalLinks(False)
        self.log_text.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {CyberpunkTheme.BG_DEEP};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: none;
                border-radius: {Spacing.RADIUS_MD}px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
                line-height: 1.5;
                padding: 8px;
            }}
            QTextBrowser::viewport {{
                background-color: {CyberpunkTheme.BG_DEEP};
            }}
        """)
        log_layout.addWidget(self.log_text, stretch=1)

        layout.addWidget(self.log_frame, stretch=1)

        # === 底部工具栏 ===
        toolbar = QHBoxLayout()
        toolbar.setSpacing(Spacing.SM)

        # 级别筛选按钮
        self.level_filter = "all"
        self.level_buttons = {}
        for level, icon in [("all", "全部"), ("info", "ℹ️"), ("warning", "⚠️"), ("error", "❌"), ("success", "✅")]:
            btn = QPushButton(icon)
            btn.setFixedSize(32, 28)
            btn.setCheckable(True)
            btn.setChecked(level == "all")
            btn.clicked.connect(lambda checked, l=level: self.set_level_filter(l))
            self.level_buttons[level] = btn
            toolbar.addWidget(btn)

        toolbar.addStretch()

        # 导出按钮
        export_btn = QPushButton("📥 导出")
        export_btn.setFixedWidth(70)
        export_btn.clicked.connect(self.export_log)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

    def set_level_filter(self, level: str):
        """设置日志级别筛选"""
        self.level_filter = level
        for lvl, btn in self.level_buttons.items():
            btn.setChecked(lvl == level)

    def highlight_keywords(self, message: str) -> str:
        """高亮关键字"""
        result = message
        for keyword, color in self.KEYWORD_COLORS.items():
            # 使用正则表达式替换，保留原文本
            if keyword in result:
                result = result.replace(
                    keyword,
                    f'<span style="color: {color}; font-weight: bold;">{keyword}</span>'
                )
        return result

    def append_log(self, message: str, level: str = "info", agent: str = None):
        """追加日志 - v2.0 增强版（支持搜索过滤）"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # 存储到内部列表（用于过滤）
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "level": level,
            "agent": agent,
        }
        self.all_logs.append(log_entry)

        # 限制日志数量
        if len(self.all_logs) > self.max_logs:
            self.all_logs = self.all_logs[-self.max_logs:]

        # 应用过滤并显示
        self._apply_filters()

        # 更新计数
        self.count_label.setText(f"{len(self.all_logs)} entries")

    def _apply_filters(self):
        """应用过滤条件"""
        # 获取过滤条件
        current_filter = self.filter_combo.currentText()
        search_text = self.search_box.text().lower() if hasattr(self, 'search_box') else ""

        # 清空当前显示
        self.log_text.clear()
        self.log_count = 0

        # 级别颜色映射
        colors = {
            "info": CyberpunkTheme.TEXT_SECONDARY,
            "warning": CyberpunkTheme.FG_WARNING,
            "error": CyberpunkTheme.FG_DANGER,
            "success": CyberpunkTheme.FG_SUCCESS,
            "system": CyberpunkTheme.FG_PRIMARY,
        }

        # 过滤并显示
        for log in self.all_logs:
            # Agent过滤
            if current_filter != "全部" and log["agent"] and log["agent"] != current_filter:
                continue

            # 级别过滤
            if self.level_filter != "all" and log["level"] != self.level_filter:
                continue

            # 搜索过滤
            if search_text and search_text.lower() not in log["message"].lower():
                continue

            self.log_count += 1

            # 构建HTML
            level = log["level"]
            icon = self.LEVEL_ICONS.get(level, "•")
            color = colors.get(level, CyberpunkTheme.TEXT_SECONDARY)

            agent_html = ""
            if log["agent"]:
                agent_html = f'<span style="color: {CyberpunkTheme.FG_ACCENT}; font-weight: bold;">[{log["agent"]}]</span> '

            highlighted_message = self.highlight_keywords(log["message"])

            html = f'<div style="margin: 2px 0;">'
            html += f'<span style="color: {CyberpunkTheme.TEXT_DIM};">{icon} [{log["timestamp"]}]</span> '
            if agent_html:
                html += agent_html
            html += f'<span style="color: {color};">{highlighted_message}</span>'
            html += '</div>'

            self.log_text.append(html)

        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _trim_logs(self):
        """修剪日志数量"""
        document = self.log_text.document()
        block = document.begin()

        # 删除前 100 条
        for _ in range(100):
            if block.isValid():
                cursor = QTextCursor(block)
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                block = document.begin()

        self.log_count -= 100

    def clear(self):
        """清空日志"""
        self.log_text.clear()
        self.log_count = 0
        self.all_logs = []
        self.count_label.setText("0 entries")

    def export_log(self):
        """导出日志到文件"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出日志", f"novel_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML Files (*.html);;Log Files (*.log);;Text Files (*.txt)"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                if filename.endswith('.html'):
                    # 导出带样式的HTML
                    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NovelForge Log</title>
    <style>
        body {{
            background: {CyberpunkTheme.BG_DARK};
            color: {CyberpunkTheme.TEXT_PRIMARY};
            font-family: Consolas, monospace;
            font-size: 12px;
            padding: 20px;
        }}
    </style>
</head>
<body>
{self.log_text.toHtml()}
</body>
</html>""")
                else:
                    # 导出纯文本
                    f.write(self.log_text.toPlainText())


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

    # 题材类型和监控指标映射（从ProjectSetupDialog移过来）
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

    def init_ui(self):
        """初始化UI - v2.0 优化版"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_DARK};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                font-family: {Typography.FONT_MONO};
                background: transparent;
                border: none;
            }}
            QTextEdit, QTextBrowser {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_BODY}px;
                padding: {Spacing.XS}px;
            }}
            QTextEdit:focus, QTextBrowser:focus {{
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: {Spacing.SM}px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                width: 16px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {CyberpunkTheme.BG_HOVER};
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: {Spacing.SM}px {Spacing.LG}px;
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_HOVER};
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
            QPushButton:disabled {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_DIM};
                border-color: {CyberpunkTheme.BORDER_COLOR};
            }}
            QGroupBox {{
                color: {CyberpunkTheme.TEXT_PRIMARY};
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
                font-family: {Typography.FONT_MONO};
                font-weight: bold;
                font-size: {Typography.SIZE_BODY}px;
                margin-top: {Spacing.MD}px;
                padding-top: {Spacing.MD}px;
                padding: {Spacing.MD}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.SM}px;
                padding: 0 {Spacing.XS}px;
                color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # ========== 标题栏 + 自动保存指示器 ==========
        header_layout = QHBoxLayout()

        # 标题
        title = QLabel("前期筹备室 (Pre-Production)")
        title.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_H2, Typography.WEIGHT_BOLD))
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY};")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # 自动保存指示器
        self.save_indicator = AutoSaveIndicator()
        header_layout.addWidget(self.save_indicator)

        layout.addLayout(header_layout)

        # ========== 项目基础信息区域（可折叠）==========
        info_group = QGroupBox("项目基础信息")
        info_group.setCheckable(True)
        info_group.setChecked(True)
        info_layout = QFormLayout()
        info_layout.setSpacing(Spacing.SM)
        info_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # 书名
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入小说书名...")
        self.title_edit.textChanged.connect(self._on_content_changed)
        info_layout.addRow("书名:", self.title_edit)

        # 题材类型
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(self.GENRE_TYPES)
        self.genre_combo.currentTextChanged.connect(self.on_genre_changed)
        info_layout.addRow("题材:", self.genre_combo)

        # 主角名
        self.protagonist_edit = QLineEdit()
        self.protagonist_edit.setPlaceholderText("输入主角姓名...")
        self.protagonist_edit.textChanged.connect(self._on_content_changed)
        info_layout.addRow("主角:", self.protagonist_edit)

        # 目标章节数
        self.chapters_spin = QSpinBox()
        self.chapters_spin.setRange(1, 10000)
        self.chapters_spin.setValue(50)
        self.chapters_spin.setToolTip("建议: 第一版50-200章")
        info_layout.addRow("目标章节:", self.chapters_spin)

        # 监控指标预览
        self.metrics_label = QLabel()
        self.metrics_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.metrics_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")
        info_layout.addRow("监控指标:", self.metrics_label)
        self.on_genre_changed("修仙")  # 默认显示修仙指标

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # ========== 三栏内容区域（可拖拽调整）==========
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        content_splitter.setHandleWidth(8)
        content_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)

        # 大纲编辑区
        outline_group = QGroupBox("故事大纲 (outline.md)")
        outline_layout = QVBoxLayout()
        outline_layout.setContentsMargins(4, 12, 4, 4)
        self.outline_text = QTextEdit()
        self.outline_text.setPlaceholderText("在这里编辑故事大纲...\n\n包括：\n- 故事主线\n- 情节点\n- 章节规划")
        self.outline_text.setMinimumHeight(150)
        self.outline_text.textChanged.connect(self._on_content_changed)
        outline_layout.addWidget(self.outline_text)
        outline_group.setLayout(outline_layout)
        content_splitter.addWidget(outline_group)

        # 人物设定区
        chars_group = QGroupBox("人物设定 (characters.json)")
        chars_layout = QVBoxLayout()
        chars_layout.setContentsMargins(4, 12, 4, 4)
        self.chars_text = QTextEdit()
        self.chars_text.setPlaceholderText("在这里编辑人物设定...\n\n主角信息：\n- 姓名、年龄\n- 性格特点\n- 背景故事\n- 能力设定")
        self.chars_text.setMinimumHeight(100)
        self.chars_text.textChanged.connect(self._on_content_changed)
        chars_layout.addWidget(self.chars_text)
        chars_group.setLayout(chars_layout)
        content_splitter.addWidget(chars_group)

        # 资深编辑诊断区 - 卡片式展示
        eval_group = QGroupBox("资深编辑诊断")
        eval_layout = QVBoxLayout()
        eval_layout.setContentsMargins(4, 12, 4, 4)
        eval_layout.setSpacing(Spacing.SM)

        # 评估内容卡片
        self.eval_card = EvaluationCard()
        eval_layout.addWidget(self.eval_card)

        # 评估操作按钮
        eval_btn_layout = QHBoxLayout()
        eval_btn_layout.setSpacing(Spacing.SM)

        self.apply_btn = QPushButton("采纳建议")
        self.apply_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY))
        self.apply_btn.setEnabled(False)
        self.apply_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogApplyButton))
        self.apply_btn.clicked.connect(self.on_apply_suggestions)
        eval_btn_layout.addWidget(self.apply_btn)

        self.edit_btn = QPushButton("手动修改")
        self.edit_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY))
        self.edit_btn.setEnabled(False)
        self.edit_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogContentsView))
        self.edit_btn.clicked.connect(lambda: self.focus_edit.emit("outline"))
        eval_btn_layout.addWidget(self.edit_btn)

        self.re_eval_btn = QPushButton("重新评估")
        self.re_eval_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY))
        self.re_eval_btn.setEnabled(False)
        self.re_eval_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_BrowserReload))
        self.re_eval_btn.clicked.connect(self.on_evaluate_settings)
        eval_btn_layout.addWidget(self.re_eval_btn)

        eval_btn_layout.addStretch()
        eval_layout.addLayout(eval_btn_layout)

        eval_group.setLayout(eval_layout)
        content_splitter.addWidget(eval_group)

        # 设置分割比例
        content_splitter.setSizes([300, 200, 200])
        layout.addWidget(content_splitter, stretch=1)

        # 自动保存定时器
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._auto_save)
        self.pending_save = False

        # 按钮区
        button_layout = QHBoxLayout()

        # 保存项目按钮（替代原来的弹窗确认）
        self.save_btn = QPushButton("保存项目")
        self.save_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
                border: 2px solid {CyberpunkTheme.FG_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: #00ccff;
            }}
        """)
        self.save_btn.clicked.connect(self.on_save_project)
        button_layout.addWidget(self.save_btn)

        button_layout.addSpacing(20)

        self.gen_btn = QPushButton("1. 生成设置")
        self.gen_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
        self.gen_btn.clicked.connect(self.on_generate_settings)
        button_layout.addWidget(self.gen_btn)

        self.eval_btn = QPushButton("2. 评估设置")
        self.eval_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
        self.eval_btn.clicked.connect(self.on_evaluate_settings)
        button_layout.addWidget(self.eval_btn)

        self.start_btn = QPushButton("3. 批准并开始写作")
        self.start_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_BODY, Typography.WEIGHT_BOLD))
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

    def on_genre_changed(self, genre: str):
        """题材变化时更新监控指标"""
        metrics = self.GENRE_METRICS.get(genre, ["reputation", "wealth", "progress"])
        self.metrics_label.setText(f"{', '.join(metrics)}")

    def get_project_config(self) -> dict:
        """获取项目配置（用于保存项目信息）"""
        title = self.title_edit.text().strip()
        genre = self.genre_combo.currentText()
        protagonist = self.protagonist_edit.text().strip()
        chapters = self.chapters_spin.value()

        return {
            "title": title or "未命名项目",
            "genre": genre,
            "protagonist": protagonist or "主角",
            "target_chapters": chapters,
            "settings": f"{genre}类型小说，主角{protagonist or '主角'}",
            "metrics": self.GENRE_METRICS.get(genre, ["reputation", "wealth", "progress"]),
        }

    def save_to_disk(self):
        """保存编辑内容到磁盘"""
        # 获取项目配置
        config = self.get_project_config()

        # 使用书名作为项目目录名（如果没有书名则使用默认）
        if config["title"] and config["title"] != "未命名项目":
            safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in config["title"])
            self.project_dir = f"novels/{safe_name}"

        project_path = Path(self.project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        # 保存项目配置
        config_path = project_path / "project_config.json"
        import json
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

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

    def _on_content_changed(self):
        """内容变化时触发自动保存"""
        self.pending_save = True
        self.save_indicator.set_unsaved()
        # 延迟2秒后自动保存
        self.save_timer.start(2000)

    def _auto_save(self):
        """自动保存内容"""
        if not self.pending_save:
            return

        self.save_indicator.set_saving()

        try:
            self.save_to_disk()
            self.pending_save = False
            self.save_indicator.set_saved()
        except Exception as e:
            print(f"[WARN] 自动保存失败: {e}")
            self.save_indicator.set_unsaved()

    def on_save_project(self):
        """保存项目按钮点击"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(
                self, "保存失败",
                "请输入书名后再保存项目",
                QMessageBox.StandardButton.Ok
            )
            self.title_edit.setFocus()
            return

        self.save_to_disk()
        QMessageBox.information(
            self, "保存成功",
            f"项目「{title}」已保存到 {self.project_dir}",
            QMessageBox.StandardButton.Ok
        )

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
        self.gen_btn.setText("1. 生成设置")

    def set_evaluation_result(self, result: str, score: int = None):
        """显示评估结果 - v2.0 使用卡片式展示"""
        self.current_evaluation = result

        self.eval_btn.setEnabled(True)
        self.eval_btn.setText("2. 评估设置")

        # 使用新的评估卡片组件
        self.eval_card.set_evaluation(result, score)

        # 启用操作按钮
        self.apply_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.re_eval_btn.setEnabled(True)

    def set_error(self, message: str):
        """显示错误 - v2.0"""
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("1. 生成设置")
        self.eval_card.set_evaluation(f"[错误] {message}")
        self.eval_card.icon_label.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER};")
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
        "ANTHROPIC_AUTH_TOKEN": ("MiniMax/Kimi Auth Token", "MiniMax & Kimi 编程版"),
        "KIMI_FOR_CODING_API_KEY": ("Kimi for Coding API Key (备用)", "Kimi 编程版"),
    }

    # 可用模型（与 model_manager.py 中的 AVAILABLE_MODELS 保持一致）
    MODELS = [
        "deepseek-chat (DeepSeek V3.2)",
        "deepseek-reasoner (DeepSeek V3.2 思考模式)",
        "claude-3-5-sonnet (Anthropic)",
        "gpt-4o (OpenAI)",
        "moonshot-v1-8k (Moonshot)",
        "minimax-m2.5 (MiniMax)",
        "kimi-for-coding (Kimi 编程版)",
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
                "minimax": "ANTHROPIC_AUTH_TOKEN",
                "kimi-for-coding": "KIMI_FOR_CODING_API_KEY",
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
    """熔断状态面板 - v2.0 增强版

    特性：
    - 红色警报脉冲动画（触发时）
    - 回滚历史条形图
    - 重置按钮
    - 状态图标+颜色指示器
    """

    reset_requested = pyqtSignal()  # 重置请求信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_tripped = False
        self.rollbacks_history = []  # 回滚历史记录
        self.max_rollbacks = 10  # 最大显示的回滚次数
        self.pulse_alpha = 0.0
        self.pulse_increasing = True

        # 脉冲动画定时器
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._update_pulse)
        self.pulse_timer.setInterval(50)  # 50ms 更新一次

        self.init_ui()

    def init_ui(self):
        """初始化UI - v2.0"""
        self.setFixedHeight(140)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # === 顶部：状态指示器 ===
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)

        # 状态指示灯（自定义绘制）
        self.status_light = StatusLightIndicator()
        self.status_light.setFixedSize(16, 16)
        status_layout.addWidget(self.status_light)

        # 状态文字
        self.status_label = QLabel("CIRCUIT BREAKER")
        self.status_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_H3, Typography.WEIGHT_BOLD))
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        # 重置按钮（默认隐藏）
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.TEXT_SECONDARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.FG_DANGER};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border-color: {CyberpunkTheme.FG_DANGER};
            }}
        """)
        self.reset_btn.clicked.connect(self._on_reset)
        self.reset_btn.setVisible(False)
        status_layout.addWidget(self.reset_btn)

        main_layout.addLayout(status_layout)

        # === 中间：回滚历史条形图 ===
        self.history_bars = RollbackHistoryBars()
        self.history_bars.setFixedHeight(40)
        main_layout.addWidget(self.history_bars)

        # === 底部：统计信息 ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        # 回滚计数
        self.counter_label = QLabel("回滚: 0")
        self.counter_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.counter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.counter_label)

        # 阈值显示
        self.threshold_label = QLabel("阈值: 3/5/8")
        self.threshold_label.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.threshold_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        stats_layout.addWidget(self.threshold_label)

        # 章节信息
        self.chapter_info = QLabel("")
        self.chapter_info.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_SMALL))
        self.chapter_info.setStyleSheet(f"color: {CyberpunkTheme.TEXT_TERTIARY};")
        self.chapter_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        stats_layout.addWidget(self.chapter_info, stretch=1)

        main_layout.addLayout(stats_layout)

    def _update_pulse(self):
        """更新脉冲动画"""
        if self.pulse_increasing:
            self.pulse_alpha += 0.1
            if self.pulse_alpha >= 1.0:
                self.pulse_alpha = 1.0
                self.pulse_increasing = False
        else:
            self.pulse_alpha -= 0.1
            if self.pulse_alpha <= 0.3:
                self.pulse_alpha = 0.3
                self.pulse_increasing = True

        # 应用脉冲效果到边框
        alpha_hex = int(self.pulse_alpha * 255)
        danger_color = f"rgba(255, 23, 68, {self.pulse_alpha:.1f})"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 2px solid {danger_color};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

    def _on_reset(self):
        """重置按钮点击"""
        self.reset_requested.emit()
        self.set_normal(0)

    def add_rollback(self, chapter: int):
        """添加回滚记录"""
        self.rollbacks_history.append({
            "chapter": chapter,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        if len(self.rollbacks_history) > self.max_rollbacks:
            self.rollbacks_history.pop(0)
        self.history_bars.update_data(self.rollbacks_history)

    def set_tripped(self, chapter: int, reason: str, rollbacks: int):
        """设置熔断触发状态"""
        self.is_tripped = True

        # 启动脉冲动画
        self.pulse_timer.start()

        # 更新状态灯
        self.status_light.set_status("danger")

        # 更新文字
        self.status_label.setText("⚠ 熔断触发")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER};")

        # 更新计数
        self.counter_label.setText(f"回滚: {rollbacks}")
        self.counter_label.setStyleSheet(f"color: {CyberpunkTheme.FG_DANGER}; font-weight: bold;")

        # 更新章节信息
        self.chapter_info.setText(f"第 {chapter} 章 | {reason[:15]}...")

        # 显示重置按钮
        self.reset_btn.setVisible(True)

        # 添加回滚记录
        self.add_rollback(chapter)

    def set_normal(self, rollbacks: int):
        """设置正常状态"""
        self.is_tripped = False

        # 停止脉冲动画
        self.pulse_timer.stop()

        # 恢复样式
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        # 更新状态灯
        self.status_light.set_status("normal")

        # 更新文字
        self.status_label.setText("● 系统正常")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")

        # 更新计数
        self.counter_label.setText(f"回滚: {rollbacks}")
        self.counter_label.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")

        # 清空章节信息
        self.chapter_info.setText("")

        # 隐藏重置按钮
        self.reset_btn.setVisible(False)

    def set_warning(self, rollbacks: int, threshold: int):
        """设置警告状态（接近阈值）"""
        if self.is_tripped:
            return  # 如果已熔断，保持熔断状态

        # 更新状态灯
        self.status_light.set_status("warning")

        # 更新文字
        self.status_label.set_text("▲ 接近阈值")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")

        # 更新计数
        self.counter_label.set_text(f"回滚: {rollbacks}/{threshold}")
        self.counter_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")


class StatusLightIndicator(QWidget):
    """状态指示灯组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = "normal"  # normal, warning, danger
        self.pulse_opacity = 1.0

        # 脉冲动画
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._pulse)
        self.pulse_timer.start(100)

    def set_status(self, status: str):
        """设置状态"""
        self.status = status
        self.update()

    def _pulse(self):
        """脉冲效果"""
        import math
        import time
        self.pulse_opacity = 0.5 + 0.5 * math.sin(time.time() * 5)
        self.update()

    def paintEvent(self, event):
        """绘制指示灯"""
        from PyQt6.QtGui import QPainter, QBrush, QColor, QRadialGradient

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            # 根据状态选择颜色
            if self.status == "normal":
                color = QColor(CyberpunkTheme.FG_SUCCESS)
            elif self.status == "warning":
                color = QColor(CyberpunkTheme.FG_WARNING)
            else:  # danger
                color = QColor(CyberpunkTheme.FG_DANGER)

            # 创建径向渐变 - 使用QPointF
            center = QtCore.QPointF(self.rect().center())
            gradient = QRadialGradient(center, self.width() / 2)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, color.darker(150))

            # 绘制发光效果
            painter.setOpacity(self.pulse_opacity if self.status != "normal" else 1.0)

            # 外发光圈
            outer_color = QColor(color)
            outer_color.setAlpha(50)
            painter.setBrush(QBrush(outer_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(self.rect().adjusted(-2, -2, 2, 2))

            # 内部实心圆
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(self.rect().adjusted(2, 2, -2, -2))
        finally:
            painter.end()


class RollbackHistoryBars(QWidget):
    """回滚历史条形图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # 回滚历史数据
        self.max_bars = 10
        self.bar_spacing = 4

    def update_data(self, history: List[Dict]):
        """更新数据"""
        self.data = history[-self.max_bars:]  # 只显示最近的数据
        self.update()

    def paintEvent(self, event):
        """绘制条形图"""
        from PyQt6.QtGui import QPainter, QBrush, QColor, QLinearGradient

        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # 计算每个条形的宽度
        bar_width = (width - (len(self.data) - 1) * self.bar_spacing) / len(self.data)

        for i, item in enumerate(self.data):
            x = i * (bar_width + self.bar_spacing)

            # 计算条形高度（根据章节号）
            chapter = item.get("chapter", 1)
            max_chapter = max(d.get("chapter", 1) for d in self.data) if self.data else 1
            bar_height = int((chapter / max(max_chapter, 10)) * height * 0.8)
            bar_height = max(bar_height, 8)  # 最小高度

            y = height - bar_height

            # 创建渐变
            gradient = QLinearGradient(x, y + bar_height, x, y)
            gradient.setColorAt(0, QColor(CyberpunkTheme.FG_DANGER))
            gradient.setColorAt(1, QColor(CyberpunkTheme.FG_WARNING))

            # 绘制条形
            painter.fillRect(int(x), y, int(bar_width), bar_height, gradient)

            # 绘制边框
            painter.setPen(QColor(CyberpunkTheme.BORDER_COLOR))
            painter.drawRect(int(x), y, int(bar_width), bar_height)


# ============================================================================
# 顶部状态栏 - 全局信息显示
# ============================================================================
class TopStatusBar(QWidget):
    """顶部状态栏 - 显示系统状态、进度、当前模型等信息"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化顶部状态栏"""
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {CyberpunkTheme.BG_MEDIUM},
                    stop:1 {CyberpunkTheme.BG_DARK});
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_SECONDARY};
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
                padding: 0 8px;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                color: {CyberpunkTheme.TEXT_SECONDARY};
                font-size: {Typography.SIZE_SMALL}px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                color: {CyberpunkTheme.FG_PRIMARY};
                background: {CyberpunkTheme.BG_LIGHT};
                border-radius: {Spacing.RADIUS_SM}px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        # 左侧: 系统状态
        self.status_indicator = QLabel("🟢 系统正常")
        self.status_indicator.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        layout.addWidget(self.status_indicator)

        # 分隔线
        separator1 = QLabel("|")
        separator1.setStyleSheet(f"color: {CyberpunkTheme.BORDER_COLOR};")
        layout.addWidget(separator1)

        # 当前项目
        self.project_label = QLabel("📁 项目: 未命名")
        layout.addWidget(self.project_label)

        # 分隔线
        separator2 = QLabel("|")
        separator2.setStyleSheet(f"color: {CyberpunkTheme.BORDER_COLOR};")
        layout.addWidget(separator2)

        # 进度显示
        self.progress_label = QLabel("📊 进度: 0/0 章")
        layout.addWidget(self.progress_label)

        # 分隔线
        separator3 = QLabel("|")
        separator3.setStyleSheet(f"color: {CyberpunkTheme.BORDER_COLOR};")
        layout.addWidget(separator3)

        # 当前模型
        self.model_label = QLabel("⚡ 模型: 未配置")
        layout.addWidget(self.model_label)

        # 弹性空间
        layout.addStretch()

        # 主题选择器
        self.theme_selector = ThemeSelector()
        layout.addWidget(self.theme_selector)

        # 分隔线
        separator4 = QLabel("|")
        separator4.setStyleSheet(f"color: {CyberpunkTheme.BORDER_COLOR};")
        layout.addWidget(separator4)

        # 右侧: 快捷按钮
        self.settings_btn = QPushButton("设置")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.settings_btn)

    def update_status(self, status: str, is_error: bool = False):
        """更新系统状态"""
        icon = "🔴" if is_error else "🟢"
        color = CyberpunkTheme.FG_DANGER if is_error else CyberpunkTheme.FG_SUCCESS
        self.status_indicator.setText(f"{icon} {status}")
        self.status_indicator.setStyleSheet(f"color: {color};")

    def update_project(self, project_name: str):
        """更新项目名称"""
        self.project_label.setText(f"📁 项目: {project_name}")

    def update_progress(self, current: int, total: int):
        """更新进度"""
        self.progress_label.setText(f"📊 进度: {current}/{total} 章")

    def update_model(self, model_name: str):
        """更新当前模型"""
        self.model_label.setText(f"⚡ 模型: {model_name}")


# ============================================================================
# 主窗口 - 全面升级版
# ============================================================================
class ProducerDashboard(QMainWindow):
    """
    制片人仪表板主窗口 - v4.2 UI优化版

    三栏布局（v4.2 优化）:
    - 左侧：实时日志面板（带筛选和语法高亮）
    - 中间：Agent工牌矩阵（可翻转）+ Agent详细信息面板 + 生产控制
    - 右侧：情绪波浪图 + 熔断状态面板
    """

    start_generation = pyqtSignal(dict)

    def __init__(self, project_dir: str = None):
        super().__init__()

        self.project_dir = project_dir or "novels/default"
        self.worker = None
        self.project_config = None
        self.start_chapter = 1  # 起始章节（用于续写）

        self.init_ui()

        # 读取项目配置（在UI初始化后）
        self.load_project_config()

        # 显示项目信息
        self.display_project_info()

    def init_ui(self):
        self.setWindowTitle("NovelForge v5.0 - AI IDE 工作台")
        self.setMinimumSize(1600, 900)
        self.setStyleSheet(f"QMainWindow {{ background-color: {CyberpunkTheme.BG_DEEP}; }}")

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 顶部状态与控制栏 (两行控制台)
        self.top_bar = TopStatusBar()
        central_layout.addWidget(self.top_bar)
        
        # === 核心 IDE 三栏布局 (Splitter) ===
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {CyberpunkTheme.BORDER_COLOR}; width: 2px; }}")

        # ==========================================
        # 左侧：微缩工牌 + 情绪图 + 大工牌展示区
        # ==========================================
        left_panel = QSplitter(Qt.Orientation.Vertical)
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(400)
        
        # 左上：情绪波浪图 (紧凑版)
        self.emotion_panel = EmotionWavePanel()
        left_panel.addWidget(self.emotion_panel)
        
        # 左中：迷你工牌列表
        mini_badge_container = QWidget()
        mini_layout = QVBoxLayout(mini_badge_container)
        mini_layout.setContentsMargins(5, 5, 5, 5)
        mini_layout.addWidget(QLabel("👥 AGENT CLUSTER", styleSheet=f"color: {CyberpunkTheme.FG_PRIMARY}; font-weight: bold; font-family: Consolas;"))
        
        self.mini_badges = {}
        self.large_badges = {}
        AVATAR_DIR = str(Path(__file__).resolve().parent.parent / "avatars")
        
        # 定义核心Agent
        agent_defs = [
            ("InitializerAgent", "建组设定", "🏗️", "avatar_08.png"),
            ("PromptAssembler", "指令聚合", "🎛️", "pixel_avatar_01.png"),
            ("ElasticArchitect", "迷雾开图", "🗺️", "pixel_avatar_02.png"),
            ("EmotionWriter", "场景生成", "✍️", "pixel_avatar_03.png"),
            ("PayoffAuditor", "情绪核算", "🧮", "pixel_avatar_04.png"),
            ("ConsistencyGuardian", "一致性守护", "🛡️", "pixel_avatar_05.png"),
            ("CreativeDirector", "仲裁回滚", "👑", "pixel_avatar_07.png"),
            ("StyleAnchor", "特征对齐", "🎨", "pixel_avatar_08.png")
        ]
        
        mini_scroll = QScrollArea()
        mini_scroll.setWidgetResizable(True)
        mini_scroll.setStyleSheet("border: none; background: transparent;")
        mini_scroll_widget = QWidget()
        mini_scroll_layout = QVBoxLayout(mini_scroll_widget)
        
        for name, role, emoji, avatar in agent_defs:
            # 迷你工牌
            mini_badge = MiniAgentBadge(name, emoji)
            mini_badge.clicked.connect(self.switch_large_badge)
            self.mini_badges[name] = mini_badge
            mini_scroll_layout.addWidget(mini_badge)
            
            # 隐藏的大工牌 (真正的 MinimalistBadge)
            large_badge = MinimalistBadge(name, role, f"Core Logic for {name}", f"{AVATAR_DIR}/{avatar}", emoji)
            large_badge.hide()
            self.large_badges[name] = large_badge
            
        mini_scroll_layout.addStretch()
        mini_scroll.setWidget(mini_scroll_widget)
        mini_layout.addWidget(mini_scroll)
        left_panel.addWidget(mini_badge_container)
        
        # 左下：选中的大工牌展示区 (高地)
        self.large_badge_area = QWidget()
        self.large_badge_layout = QVBoxLayout(self.large_badge_area)
        self.large_badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.large_badge_layout.addWidget(QLabel("Click a mini badge to inspect", styleSheet=f"color: {CyberpunkTheme.TEXT_DIM};"))
        left_panel.addWidget(self.large_badge_area)
        
        # ==========================================
        # 中间：沉浸式创作区 (正文流式输出 + 日志)
        # ==========================================
        center_panel = QSplitter(Qt.Orientation.Vertical)
        center_panel.setMinimumWidth(600)
        
        # 中上：控制台与打字机视图
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(10, 10, 10, 0)
        
        # 控制按钮组
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ 开启/恢复生成 (START)")
        self.btn_start.setStyleSheet(f"background-color: {CyberpunkTheme.FG_SUCCESS}; color: #000; font-weight: bold;")
        self.btn_pause = QPushButton("⏸ 紧急暂停 (PAUSE)")
        self.btn_override = QPushButton("✏️ 人工接管 (OVERRIDE)")
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_override)
        editor_layout.addLayout(btn_layout)
        
        # 实时正文查看器 (The Typewriter)
        self.manuscript_viewer = QTextBrowser()
        self.manuscript_viewer.setStyleSheet(f"""
            background-color: #1e1e1e; color: #d4d4d4; 
            font-family: 'Microsoft YaHei', Consolas; font-size: 15px; 
            line-height: 1.8; padding: 20px; border-radius: 8px; border: 1px solid #333;
        """)
        self.manuscript_viewer.setPlaceholderText(">> AI 实时生成正文将在这里显示，如打字机般倾泻而出...")
        editor_layout.addWidget(self.manuscript_viewer)
        center_panel.addWidget(editor_container)
        
        # 中下：日志与仲裁
        self.log_panel = LogPanel()
        center_panel.addWidget(self.log_panel)
        
        # 设置中间上下比例 (正文占 70%，日志占 30%)
        center_panel.setStretchFactor(0, 7)
        center_panel.setStretchFactor(1, 3)

        # ==========================================
        # 右侧：常驻设定参考区 (Outline/Chars/Rules)
        # ==========================================
        right_panel = QWidget()
        right_panel.setMinimumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 10, 5)
        
        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet(f"QTabBar::tab {{ background: {CyberpunkTheme.BG_DARK}; color: white; padding: 8px 12px; }}")
        
        self.outline_edit = QTextEdit()
        self.chars_edit = QTextEdit()
        self.rules_edit = QTextEdit()
        
        for widget in [self.outline_edit, self.chars_edit, self.rules_edit]:
            widget.setStyleSheet(f"background-color: {CyberpunkTheme.BG_MEDIUM}; color: {CyberpunkTheme.TEXT_PRIMARY}; font-size: 13px; font-family: Consolas;")
            
        self.right_tabs.addTab(self.outline_edit, "📖 剧情大纲")
        self.right_tabs.addTab(self.chars_edit, "👤 角色档案")
        self.right_tabs.addTab(self.rules_edit, "⚙️ 世界法则")
        
        right_layout.addWidget(self.right_tabs)
        
        btn_save_config = QPushButton("💾 实时保存设定修改")
        btn_save_config.setStyleSheet(f"border: 1px solid {CyberpunkTheme.FG_PRIMARY}; color: {CyberpunkTheme.FG_PRIMARY};")
        right_layout.addWidget(btn_save_config)

        # === 组装三栏 ===
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 6)
        main_splitter.setStretchFactor(2, 2)
        
        central_layout.addWidget(main_splitter)
        self.setCentralWidget(central_widget)

        # 绑定按钮事件
        self.btn_start.clicked.connect(self.do_start_generation)
        btn_save_config.clicked.connect(self.save_right_panel_configs)

    def switch_large_badge(self, agent_name: str):
        """点击迷你工牌，在左下方召唤对应的 3D 翻转大卡片"""
        # 清除布局中旧的卡片
        for i in reversed(range(self.large_badge_layout.count())): 
            widget = self.large_badge_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        # 添加新的卡片
        if agent_name in self.large_badges:
            card = self.large_badges[agent_name]
            card.show()
            self.large_badge_layout.addWidget(card)

    def on_text_stream(self, text_chunk: str):
        """接收打字机文本流，追加到中间正文区"""
        # 移动光标到末尾并插入文本
        cursor = self.manuscript_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text_chunk)
        self.manuscript_viewer.setTextCursor(cursor)
        self.manuscript_viewer.ensureCursorVisible()

    def update_agent_status(self, name: str, status: str, task: str = ""):
        """同步更新大卡片和迷你卡片的状态灯"""
        # 获取颜色
        colors = {"idle": CyberpunkTheme.FG_SUCCESS, "thinking": CyberpunkTheme.FG_INFO, "writing": CyberpunkTheme.FG_PRIMARY, "auditing": CyberpunkTheme.FG_ACCENT, "conflict": CyberpunkTheme.FG_DANGER}
        color_hex = colors.get(status.lower(), CyberpunkTheme.FG_SUCCESS)
        
        if name in self.large_badges:
            self.large_badges[name].set_status(status, task)
        if name in self.mini_badges:
            self.mini_badges[name].set_status(color_hex)

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

                # 加载配置到前期筹备面板的表单
                config = self.project_config
                if config:
                    self.preproduction_panel.title_edit.setText(config.get("title", ""))
                    self.preproduction_panel.protagonist_edit.setText(config.get("protagonist", ""))
                    self.preproduction_panel.chapters_spin.setValue(config.get("target_chapters", 50))

                    # 设置题材
                    genre = config.get("genre", "修仙")
                    index = self.preproduction_panel.genre_combo.findText(genre)
                    if index >= 0:
                        self.preproduction_panel.genre_combo.setCurrentIndex(index)

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
        """新建项目 - 直接切换到前期筹备标签页"""
        # 清空当前项目
        self.project_dir = "novels/default"
        self.project_config = {}

        # 清空前期筹备面板
        self.preproduction_panel.title_edit.clear()
        self.preproduction_panel.protagonist_edit.clear()
        self.preproduction_panel.chapters_spin.setValue(50)
        self.preproduction_panel.genre_combo.setCurrentIndex(0)
        self.preproduction_panel.outline_text.clear()
        self.preproduction_panel.chars_text.clear()
        self.preproduction_panel.eval_text.clear()

        # 切换到前期筹备标签页
        self.tabs.setCurrentIndex(0)

        self.log_panel.append_log("新建项目 - 请在前期筹备室填写项目信息", "info")
        self.display_project_info()

    def on_open_project(self):
        """打开项目"""
        directory = QFileDialog.getExistingDirectory(self, "选择项目目录", "novels")
        if directory:
            self.project_dir = directory
            self.load_project_config()
            self.display_project_info()

            # 加载大纲和人物文件到前期筹备面板
            project_path = Path(self.project_dir)

            # 加载大纲
            outline_file = project_path / "outline.md"
            if outline_file.exists():
                try:
                    self.preproduction_panel.outline_text.setText(
                        outline_file.read_text(encoding="utf-8")
                    )
                except Exception as e:
                    print(f"Warning: Failed to load outline: {e}")

            # 加载人物设定
            chars_file = project_path / "characters.json"
            if chars_file.exists():
                try:
                    self.preproduction_panel.chars_text.setText(
                        chars_file.read_text(encoding="utf-8")
                    )
                except Exception as e:
                    print(f"Warning: Failed to load characters: {e}")

            # 更新前期筹备面板的项目目录
            self.preproduction_panel.project_dir = self.project_dir

    def on_view_documents(self):
        """查看文档"""
        dialog = DocumentViewerDialog(self.project_dir, self)
        dialog.exec()

    def on_api_key_settings(self):
        """API Key设置"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def on_theme_changed(self, theme_key: str):
        """主题切换事件"""
        # Get new theme colors
        theme = ThemeManager.get_theme(theme_key)

        # 更新CyberpunkTheme类的颜色值
        for color_name, color_value in theme["colors"].items():
            if hasattr(CyberpunkTheme, color_name):
                setattr(CyberpunkTheme, color_name, color_value)

        # 重新应用样式表（触发全局刷新）
        self.setStyleSheet("")  # 先清空
        # 重新设置init_ui中的样式表 - 这里通过重新调用来刷新
        # 由于样式已经应用，直接刷新当前窗口
        self.update()

        # 显示切换成功提示
        QMessageBox.information(
            self, "主题切换",
            f"已切换到「{theme['name']}」主题",
            QMessageBox.StandardButton.Ok
        )

    def on_about(self):
        """关于"""
        QMessageBox.about(
            self, "关于 NovelForge",
            "NovelForge v4.2 - AI小说生成系统\n\n"
            "基于Anthropic长运行代理最佳实践的全自动小说创作系统\n\n"
            "功能：\n"
            "• 前期筹备与评估优化\n"
            "• 生产过程可视化\n"
            "• 断点续写\n"
            "• Agent工牌翻转详情\n"
            "• 情绪曲线监控\n"
            "• 4套主题切换\n"
            "• 日志搜索过滤"
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
        self.preproduction_panel.eval_btn.setText("2. 评估设置")

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
        self.worker = worker
        worker.log_signal.connect(self.on_log)
        worker.agent_status_signal.connect(lambda d: self.update_agent_status(d["name"], d["status"], d.get("task", "")))
        worker.emotion_curve_signal.connect(self.on_emotion_curve)
        # 🔥 绑定流式输出信号
        worker.text_stream_signal.connect(self.on_text_stream)

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

    # 如果没有指定项目目录，使用默认目录
    if not project_dir:
        project_dir = "novels/default"

    # 确保项目目录存在
    Path(project_dir).mkdir(parents=True, exist_ok=True)

    app.setQuitOnLastWindowClosed(True)

    print("[System] 正在点火，启动赛博编辑部中控大屏 v4.2...")

    window = ProducerDashboard(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
