"""
组件库 - Agent卡片、面板、情绪波浪图、日志面板等
"""

import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# PyQt6 导入
try:
    from PyQt6.QtWidgets import (
        QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
        QFrame, QScrollArea, QGridLayout, QTextEdit, QComboBox,
        QTextBrowser, QGraphicsDropShadowEffect, QApplication,
        QFileDialog, QLineEdit
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QRect, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
    from PyQt6.QtGui import QFont, QColor, QCursor, QPixmap, QPainter, QBrush, QLinearGradient, QRadialGradient
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

# 导入主题系统
try:
    from ui.themes import CyberpunkTheme, Typography, Spacing
except ImportError:
    from themes import CyberpunkTheme, Typography, Spacing


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
# Agent 详细信息面板
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
# Agent 矩阵面板
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

        # Expected 曲线（独立 X 轴）
        if expected:
            x_exp = list(range(1, len(expected) + 1))
            self.expected_curve.setData(x_exp, expected)
            self.expected_glow.setData(x_exp, [y + 1 for y in expected])

        # Actual 曲线（独立 X 轴，防止 shape mismatch）
        if actual:
            x_act = list(range(1, len(actual) + 1))
            self.actual_curve.setData(x_act, actual)
            self.actual_glow.setData(x_act, [y + 1 for y in actual])

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
# 熔断状态面板
# ============================================================================
class CircuitBreakerPanel(QWidget):
    """熔断状态面板 - v2.0 增强版"""

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
        self.status_label.setText("▲ 接近阈值")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_WARNING};")

        # 更新计数
        self.counter_label.setText(f"回滚: {rollbacks}/{threshold}")
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
# 顶部双行控制台 - 赛博编辑部中控 (V5.0)
# ============================================================================
class TopControlPanel(QFrame):
    """顶部双行控制台：行1显示状态与项目，行2是全生命周期操作按钮"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{ background-color: {CyberpunkTheme.BG_MEDIUM}; border-bottom: 2px solid {CyberpunkTheme.BORDER_COLOR}; }}
            QLabel {{ color: {CyberpunkTheme.TEXT_SECONDARY}; font-family: {Typography.FONT_MONO}; font-size: 13px; font-weight: bold; background: transparent; border: none; }}
            QPushButton {{ background-color: {CyberpunkTheme.BG_LIGHT}; color: {CyberpunkTheme.TEXT_PRIMARY}; border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 4px; padding: 6px 14px; font-family: 'Microsoft YaHei', Consolas; font-weight: bold; }}
            QPushButton:hover {{ background-color: {CyberpunkTheme.BG_HOVER}; border-color: {CyberpunkTheme.FG_PRIMARY}; color: {CyberpunkTheme.FG_PRIMARY}; }}
            QPushButton:disabled {{ background-color: {CyberpunkTheme.BG_DEEP}; color: {CyberpunkTheme.TEXT_DIM}; border-color: {CyberpunkTheme.BG_DARK}; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # === 第一行：状态信息与全局设置 ===
        row1 = QHBoxLayout()
        self.status_indicator = QLabel("🟢 系统待命")
        self.status_indicator.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        self.project_label = QLabel("📁 项目: 未命名")
        self.progress_label = QLabel("📊 进度: 0/0 章")
        self.model_label = QLabel("⚡ 模型: 自动")

        row1.addWidget(self.status_indicator)
        row1.addWidget(self._vline())
        row1.addWidget(self.project_label)
        row1.addWidget(self._vline())
        row1.addWidget(self.progress_label)
        row1.addWidget(self._vline())
        row1.addWidget(self.model_label)
        row1.addStretch()

        # 导入并添加主题选择器
        try:
            from ui.themes import ThemeSelector
            self.theme_selector = ThemeSelector()
        except ImportError:
            self.theme_selector = QLabel("主题")
        row1.addWidget(self.theme_selector)

        self.settings_btn = QPushButton("⚙️ 系统设置")
        row1.addWidget(self.settings_btn)

        # === 第二行：全局操作按钮（前期筹备 + 生产控制） ===
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        # 筹备区
        row2.addWidget(QLabel("【前期筹备】", styleSheet=f"color: {CyberpunkTheme.FG_SECONDARY};"))
        self.btn_generate = QPushButton("1. 🎲 生成基础设定")
        self.btn_evaluate = QPushButton("2. 🧐 资深编辑诊断")
        self.btn_save_config = QPushButton("💾 保存右侧设定")

        row2.addWidget(self.btn_generate)
        row2.addWidget(self.btn_evaluate)
        row2.addWidget(self.btn_save_config)

        row2.addSpacing(20)
        row2.addWidget(self._vline())
        row2.addSpacing(20)

        # 生产区
        row2.addWidget(QLabel("【生产控制】", styleSheet=f"color: {CyberpunkTheme.FG_PRIMARY};"))
        self.btn_start = QPushButton("▶ 确认开机 (START)")
        self.btn_start.setStyleSheet(f"background-color: {CyberpunkTheme.FG_SUCCESS}; color: #000; font-size: 14px;")
        self.btn_pause = QPushButton("⏸ 暂停 (PAUSE)")
        self.btn_pause.setEnabled(False)
        self.btn_resume = QPushButton("⏩ 恢复 (RESUME)")
        self.btn_resume.setEnabled(False)
        self.btn_override = QPushButton("✏️ 人工接管")

        row2.addWidget(self.btn_start)
        row2.addWidget(self.btn_pause)
        row2.addWidget(self.btn_resume)
        row2.addWidget(self.btn_override)
        row2.addStretch()

        layout.addLayout(row1)
        layout.addLayout(row2)

    def _vline(self):
        l = QLabel("|")
        l.setStyleSheet(f"color: {CyberpunkTheme.BORDER_COLOR}; margin: 0 8px;")
        return l
