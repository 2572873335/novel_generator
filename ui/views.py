"""
视图组件 - 全局状态栏、主导航栏、前期筹备视图、生产视图、项目仓库视图
"""

import sys
import json
from pathlib import Path
from typing import Optional

# PyQt6 导入
try:
    from PyQt6.QtWidgets import (
        QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
        QFrame, QStackedWidget, QGroupBox, QFormLayout, QTextEdit,
        QLineEdit, QComboBox, QSpinBox, QTextBrowser, QListWidget,
        QListWidgetItem, QScrollArea, QSplitter, QTabWidget, QTextBrowser,
        QApplication, QGridLayout, QMessageBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QCursor, QTextCursor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available")


# 导入主题系统
try:
    from ui.themes import CyberpunkTheme, Typography, Spacing, ThemeManager, ThemeStyles
except ImportError:
    from themes import CyberpunkTheme, Typography, Spacing

# 导入领域模型
try:
    from core.project_context import NovelProject
except ImportError:
    from core.project_context import NovelProject
    from themes import CyberpunkTheme, Typography, Spacing


# ============================================================================
# 全局状态栏 (Tier 2) - 仅显示信息，无操作按钮
# ============================================================================
class GlobalStatusBar(QFrame):
    """全局状态栏 - 显示当前项目、进度、模型等信息（无操作按钮）"""

    # 主题切换信号
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_DARK};
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_SECONDARY};
                font-family: {Typography.FONT_PRIMARY};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QComboBox {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 4px 10px;
                font-family: {Typography.FONT_PRIMARY};
                font-size: {Typography.SIZE_SMALL}px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: {CyberpunkTheme.FG_PRIMARY};
                background-color: {CyberpunkTheme.BG_LIGHT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                selection-background-color: {CyberpunkTheme.BG_LIGHT};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(24)

        # 状态指示 - 带脉冲效果
        self.status_label = QLabel("● 系统就绪")
        self.status_label.setStyleSheet(f"""
            color: {CyberpunkTheme.FG_SUCCESS};
            font-weight: {Typography.WEIGHT_MEDIUM};
        """)
        layout.addWidget(self.status_label)

        # 分隔线
        self._add_divider(layout)

        # 当前项目
        self.project_label = QLabel("📁 项目: 未加载")
        layout.addWidget(self.project_label)

        # 分隔线
        self._add_divider(layout)

        # 进度
        self.progress_label = QLabel("📊 进度: -")
        layout.addWidget(self.progress_label)

        # 分隔线
        self._add_divider(layout)

        # 当前模型
        self.model_label = QLabel("🤖 模型: DeepSeek-V3")
        layout.addWidget(self.model_label)

        layout.addStretch()

        # 分隔线
        self._add_divider(layout)

        # 主题切换器
        theme_label = QLabel("🎨 主题:")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Slate Dark", "cyberpunk")
        self.theme_combo.addItem("明日方舟", "arknights")
        self.theme_combo.addItem("日落", "sunset")
        self.theme_combo.addItem("森林", "forest")
        self.theme_combo.addItem("现代浅色", "modern_light")
        self.theme_combo.setCurrentText(ThemeManager.THEMES[ThemeManager.current_theme]["name"])
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)

    def _on_theme_changed(self):
        """主题切换处理"""
        theme_key = self.theme_combo.currentData()
        ThemeManager.set_theme(theme_key)
        self.theme_changed.emit(theme_key)

    def _add_divider(self, layout):
        """添加分隔线"""
        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"background-color: {CyberpunkTheme.BORDER_COLOR};")
        layout.addWidget(divider)

    def update_status(self, status: str, status_type: str = "success"):
        color = CyberpunkTheme.FG_SUCCESS if status_type == "success" else CyberpunkTheme.FG_WARNING if status_type == "warning" else CyberpunkTheme.FG_DANGER
        self.status_label.setText(f"● {status}")
        self.status_label.setStyleSheet(f"color: {color};")

    def update_project(self, project_name: str):
        self.project_label.setText(f"📁 项目: {project_name}")

    def update_progress(self, current: int, total: int):
        self.progress_label.setText(f"📊 进度: {current}/{total}")


# ============================================================================
# 主导航栏 (Tier 3)
# ============================================================================
class MainNavigationBar(QFrame):
    """主导航栏 - 三个主要视图的切换"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_DEEP};
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QPushButton {{
                background-color: transparent;
                color: {CyberpunkTheme.TEXT_SECONDARY};
                border: none;
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 12px 24px;
                font-family: {Typography.FONT_PRIMARY};
                font-size: {Typography.SIZE_BODY}px;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {CyberpunkTheme.BG_LIGHT};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(50, 8, 50, 8)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo / 标题区域
        logo_label = QLabel("⚡ NovelForge")
        logo_label.setStyleSheet(f"""
            font-family: {Typography.FONT_DISPLAY};
            font-size: {Typography.SIZE_H2}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {CyberpunkTheme.FG_PRIMARY};
        """)
        layout.addWidget(logo_label)

        # 分隔线
        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setFixedHeight(32)
        divider.setStyleSheet(f"background-color: {CyberpunkTheme.BORDER_COLOR}; margin: 8px 0;")
        layout.addWidget(divider)

        # 导航按钮
        nav_buttons = [
            ("📝 前期筹备", "btn_preprod"),
            ("🎬 生产监控", "btn_prod"),
            ("📚 项目仓库", "btn_vault"),
            ("🧩 工作流集市", "btn_market"),
        ]

        for text, attr_name in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(attr_name)
            btn.setFixedWidth(160)
            layout.addWidget(btn)
            setattr(self, attr_name, btn)

        # 右侧留白
        layout.addStretch()

        # 存储按钮引用用于设置选中状态
        self.nav_buttons = [self.btn_preprod, self.btn_prod, self.btn_vault, self.btn_market]

    def set_active(self, index: int, styles: dict = None):
        """设置选中状态的导航按钮"""
        # 如果没有传入样式，使用默认的
        if styles is None:
            styles = {
                "navbar_active": f"""
                    QPushButton {{
                        background-color: {CyberpunkTheme.FG_PRIMARY};
                        color: #FFFFFF;
                        border: none;
                        border-radius: {Spacing.RADIUS_MD}px;
                        padding: 12px 24px;
                        font-family: {Typography.FONT_PRIMARY};
                        font-size: {Typography.SIZE_BODY}px;
                        font-weight: {Typography.WEIGHT_BOLD};
                    }}
                """,
                "navbar": f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {CyberpunkTheme.TEXT_SECONDARY};
                        border: none;
                        border-radius: {Spacing.RADIUS_MD}px;
                        padding: 12px 24px;
                        font-family: {Typography.FONT_PRIMARY};
                        font-size: {Typography.SIZE_BODY}px;
                        font-weight: {Typography.WEIGHT_MEDIUM};
                    }}
                    QPushButton:hover {{
                        background-color: {CyberpunkTheme.BG_MEDIUM};
                        color: {CyberpunkTheme.TEXT_PRIMARY};
                    }}
                """
            }

        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet(styles["navbar_active"])
            else:
                btn.setStyleSheet(styles["navbar"])


# ============================================================================
# 前期筹备视图 (PreProductionView) - 包含操作按钮和信号
# ============================================================================
class PreProductionView(QWidget):
    """前期筹备视图 - 双轨构思法，带操作按钮和自定义信号"""

    # 信号：视图层发出请求
    request_generate = pyqtSignal()      # 请求生成设置
    request_evaluate = pyqtSignal()     # 请求评估
    request_start = pyqtSignal()         # 请求开始写作
    status_changed = pyqtSignal(str)      # 状态变更信号
    request_ai_chat = pyqtSignal(str)    # AI对话请求（传递用户输入文本）

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_dir = "novels/default"
        self.last_diagnosis = None  # 存储上次诊断结果
        self.init_ui()

    def set_project_dir(self, project_dir: str):
        """设置项目目录"""
        self.project_dir = project_dir
        self.reload_data()

    def reload_data(self):
        """重新加载项目数据"""
        project = NovelProject(self.project_dir)

        # 加载大纲
        outline = project.load_outline()
        if outline:
            self.edit_outline.setText(outline)

        # 加载人物设定
        characters = project.load_characters()
        if characters:
            self.edit_chars.setText(characters)

        # 加载项目配置
        config = project.load_config()
        if config:
            self.edit_title.setText(config.get("title", ""))
            self.edit_protagonist.setText(config.get("protagonist", ""))
            idx = self.edit_genre.findText(config.get("genre", ""))
            if idx >= 0:
                self.edit_genre.setCurrentIndex(idx)
            self.edit_chapters.setValue(config.get("target_chapters", 50))

    def get_project_config(self) -> dict:
        """获取项目配置"""
        return {
            "title": self.edit_title.text().strip() or "未命名项目",
            "genre": self.edit_genre.currentText(),
            "protagonist": self.edit_protagonist.text().strip() or "主角",
            "target_chapters": self.edit_chapters.value(),
            "outline": self.edit_outline.toPlainText(),
            "characters": self.edit_chars.toPlainText()
        }

    def save_project(self):
        """保存项目到磁盘"""
        config = self.get_project_config()
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in config["title"])
        project_dir = f"novels/{safe_name}"

        # 使用 NovelProject 保存
        project = NovelProject(project_dir)
        project.save_config(config)
        project.save_outline(config["outline"])
        project.save_characters(config["characters"])

        self.project_dir = project_dir
        return project_dir

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 内部堆叠窗口
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # ===== Page 0: 选择页 =====
        self.page_selection = self._create_selection_page()
        self.stack.addWidget(self.page_selection)

        # ===== Page 1: 手动填表页 =====
        self.page_manual = self._create_manual_page()
        self.stack.addWidget(self.page_manual)

        # ===== Page 2: AI对话引导页 =====
        self.page_ai_chat = self._create_ai_chat_page()
        self.stack.addWidget(self.page_ai_chat)

        # ===== Page 3: 创作工具箱 =====
        self.page_toolbox = self._create_toolbox_page()
        self.stack.addWidget(self.page_toolbox)

    def _create_selection_page(self):
        """创建选择页 - 现代SaaS风格卡片"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("选择创作模式")
        title.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_H1, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY}; margin-bottom: 30px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        card_layout = QHBoxLayout()
        card_layout.setSpacing(30)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_entry_card(icon_str, title_str, desc_str, target_idx):
            card = QFrame()
            card.setFixedSize(320, 220)
            card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {CyberpunkTheme.BG_MEDIUM};
                    border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    border: 1px solid {CyberpunkTheme.FG_PRIMARY};
                    background-color: {CyberpunkTheme.BG_HOVER};
                }}
            """)
            card.mousePressEvent = lambda e: self.stack.setCurrentIndex(target_idx)

            v = QVBoxLayout(card)
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.setContentsMargins(20, 20, 20, 20)

            icon = QLabel(icon_str)
            icon.setStyleSheet("font-size: 48px; background: transparent; border: none;")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(icon)

            lbl_t = QLabel(title_str)
            lbl_t.setFont(QFont(Typography.FONT_PRIMARY, 16, QFont.Weight.Bold))
            lbl_t.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY}; background: transparent; border: none; margin-top: 10px;")
            lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(lbl_t)

            lbl_d = QLabel(desc_str)
            lbl_d.setFont(QFont(Typography.FONT_PRIMARY, 11))
            lbl_d.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY}; background: transparent; border: none; margin-top: 5px;")
            lbl_d.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_d.setWordWrap(True)
            v.addWidget(lbl_d)

            return card

        card_layout.addWidget(create_entry_card("📝", "手动设定 (Manual)", "传统模式。手动填写书名、大纲与人物设定，精准控制故事走向。", 1))
        card_layout.addWidget(create_entry_card("🤖", "对话生成 (AI Guided)", "向导模式。与资深AI责编对话，通过灵感碰撞自动补全庞大的世界观。", 2))
        card_layout.addWidget(create_entry_card("🧰", "创作工具箱 (Toolbox)", "碎片化创作。单独生成脑洞、书名、金手指或核心反派等设定片段。", 3))

        layout.addLayout(card_layout)

        return page

    def _create_manual_page(self):
        """创建手动填表页 - 带操作按钮"""
        from PyQt6.QtWidgets import QFormLayout
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 左侧表单区
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        # 返回按钮
        btn_back = QPushButton("← 返回")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        form_layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)

        # 表单
        form_group = QGroupBox("📖 基础设定")
        form_inner = QFormLayout(form_group)

        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("输入小说标题...")
        form_inner.addRow("标题:", self.edit_title)

        self.edit_protagonist = QLineEdit()
        self.edit_protagonist.setPlaceholderText("主角姓名...")
        form_inner.addRow("主角:", self.edit_protagonist)

        self.edit_genre = QComboBox()
        self.edit_genre.setEditable(True)
        self.edit_genre.addItems(["玄幻", "仙侠", "科幻", "都市", "历史", "悬疑", "言情", "科幻悬疑", "玄幻都市"])
        form_inner.addRow("题材:", self.edit_genre)

        self.edit_chapters = QSpinBox()
        self.edit_chapters.setRange(10, 1000)
        self.edit_chapters.setValue(50)
        form_inner.addRow("目标章节:", self.edit_chapters)

        form_layout.addWidget(form_group)

        # 大纲编辑区
        outline_group = QGroupBox("🗺️ 故事大纲")
        outline_layout = QVBoxLayout(outline_group)
        self.edit_outline = QTextEdit()
        self.edit_outline.setPlaceholderText("在这里输入详细的故事大纲...")
        outline_layout.addWidget(self.edit_outline)
        form_layout.addWidget(outline_group)

        # 人物设定区
        chars_group = QGroupBox("👤 人物设定")
        chars_layout = QVBoxLayout(chars_group)
        self.edit_chars = QTextEdit()
        self.edit_chars.setPlaceholderText("在这里编辑人物设定...")
        chars_layout.addWidget(self.edit_chars)
        form_layout.addWidget(chars_group)

        # 操作按钮区（生成、评估）
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_generate = QPushButton("🎲 生成设置")
        self.btn_generate.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.btn_generate.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: #000;
                border: 2px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00ccff;
            }}
        """)
        self.btn_generate.clicked.connect(self._on_generate)
        btn_layout.addWidget(self.btn_generate)

        self.btn_evaluate = QPushButton("🧐 资深编辑诊断")
        self.btn_evaluate.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.btn_evaluate.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_WARNING};
                color: #000;
                border: 2px solid {CyberpunkTheme.FG_WARNING};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
        """)
        self.btn_evaluate.clicked.connect(self._on_diagnose)
        btn_layout.addWidget(self.btn_evaluate)

        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)

        layout.addWidget(form_container, stretch=3)

        # 右侧诊断结果区
        result_container = QWidget()
        result_layout = QVBoxLayout(result_container)

        result_label = QLabel("📋 诊断报告")
        result_label.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY}; font-weight: bold;")
        result_layout.addWidget(result_label)

        self.diagnose_result = QTextBrowser()
        self.diagnose_result.setPlaceholderText("诊断结果将在这里显示...")
        result_layout.addWidget(self.diagnose_result)

        # 采纳建议按钮（诊断成功后显示）
        self.btn_apply_advice = QPushButton("💡 采纳建议并修改")
        self.btn_apply_advice.setFont(QFont("Consolas", 10))
        self.btn_apply_advice.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: #000;
                border: 2px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00ccff;
            }}
        """)
        self.btn_apply_advice.clicked.connect(self._on_apply_diagnosis_advice)
        self.btn_apply_advice.setVisible(False)  # 默认隐藏
        result_layout.addWidget(self.btn_apply_advice)

        # 确认并开始写作按钮 - 发出 request_start 信号
        self.btn_start = QPushButton("✅ 确认设定并开始写作")
        self.btn_start.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: #000;
                border: 2px solid {CyberpunkTheme.FG_SUCCESS};
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00cc55;
            }}
        """)
        self.btn_start.clicked.connect(self._on_start)
        result_layout.addWidget(self.btn_start)

        layout.addWidget(result_container, stretch=2)

        return page

    def _on_generate(self):
        """点击生成设置按钮"""
        self.status_changed.emit("生成中...")
        self.request_generate.emit()

    def _on_start(self):
        """点击开始写作按钮"""
        # 先保存项目
        self.save_project()
        self.status_changed.emit("准备开始写作...")
        self.request_start.emit()

    def _create_ai_chat_page(self):
        """创建AI对话引导页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 顶部返回按钮
        btn_back = QPushButton("← 返回")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)

        # 聊天历史区
        self.chat_history = QTextBrowser()
        self.chat_history.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
        """)
        # 添加初始欢迎消息
        welcome_msg = """
        <div style='color: #00f5f5; margin: 10px 0;'>
            <b>🤖 AI 责编:</b> 你好！我是你的专属网文责编。让我们一步步构建你的故事世界。<br><br>
            首先，请告诉我：<b>你想写一个什么类型的小说？</b>（玄幻/仙侠/科幻/都市...）<br>
            或者，你可以简单描述一下你脑海中最强烈的那个画面或灵感。
        </div>
        """
        self.chat_history.setHtml(welcome_msg)
        layout.addWidget(self.chat_history, stretch=1)

        # 输入区
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("输入你的回答...")
        self.chat_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 2px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
        """)
        input_layout.addWidget(self.chat_input)

        btn_send = QPushButton("发送 →")
        btn_send.setFixedWidth(100)
        btn_send.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: #000;
                font-weight: bold;
                border-radius: 8px;
            }}
        """)
        btn_send.clicked.connect(self._on_chat_send)
        input_layout.addWidget(btn_send)

        layout.addLayout(input_layout)

        return page

    def _create_toolbox_page(self):
        """创建创作工具箱页"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 返回按钮
        btn_back = QPushButton("← 返回")
        btn_back.setFixedWidth(100)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignLeft)

        # 标题
        title = QLabel("🧰 创作工具箱")
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_GOLD}; font-size: 22px; font-weight: bold; font-family: Consolas;")
        layout.addWidget(title)

        # 滚动区域 + 网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(20)
        grid.setContentsMargins(10, 10, 10, 10)

        tools = [
            ("💡", "脑洞生成器", "Brainstorm"),
            ("📖", "书名生成器", "Title Generator"),
            ("👆", "金手指生成器", "Cheat Code/Power"),
            ("🌍", "世界观生成器", "Worldview"),
            ("👤", "反派生成器", "Villain Creator"),
            ("⚔️", "核心冲突提炼", "Conflict Extractor"),
        ]

        for i, (emoji, name_cn, name_en) in enumerate(tools):
            card = self._make_tool_card(emoji, name_cn, name_en)
            grid.addWidget(card, i // 3, i % 3)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        return page

    def _make_tool_card(self, emoji: str, name_cn: str, name_en: str) -> QFrame:
        """创建单个工具卡片 - Modern SaaS style"""
        card = QFrame()
        card.setFixedSize(280, 150)
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 10px;
            }}
            QFrame:hover {{
                background-color: {CyberpunkTheme.BG_HOVER};
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 16, 18, 14)
        cl.setSpacing(6)

        lbl_emoji = QLabel(emoji)
        lbl_emoji.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        cl.addWidget(lbl_emoji)

        lbl_name = QLabel(name_cn)
        lbl_name.setFont(QFont(Typography.FONT_PRIMARY, 14, QFont.Weight.Bold))
        lbl_name.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY}; background: transparent; border: none;")
        cl.addWidget(lbl_name)

        lbl_en = QLabel(name_en)
        lbl_en.setFont(QFont(Typography.FONT_PRIMARY, 10))
        lbl_en.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY}; background: transparent; border: none;")
        cl.addWidget(lbl_en)

        cl.addStretch()
        card.mousePressEvent = lambda e, n=name_cn: self._open_tool_dialog(n)
        return card

    def _open_tool_dialog(self, tool_name: str):
        """打开创作工具对话框"""
        from ui.dialogs import ToolGeneratorDialog
        dialog = ToolGeneratorDialog(tool_name, self)
        dialog.applied_signal.connect(self._handle_tool_apply)
        dialog.exec()

    def _handle_tool_apply(self, tool_name: str, result_text: str):
        """将工具生成结果追加到大纲"""
        self.stack.setCurrentIndex(1)
        cursor = self.edit_outline.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(f"\n\n### 【{tool_name}】生成内容\n{result_text}\n")
        self.edit_outline.setTextCursor(cursor)
        self.edit_outline.ensureCursorVisible()
        self.status_changed.emit(f"已将 {tool_name} 结果追加到大纲")

    def _on_diagnose(self):
        """执行资深编辑诊断"""
        title = self.edit_title.text()
        outline = self.edit_outline.toPlainText()
        genre = self.edit_genre.currentText()
        protagonist = self.edit_protagonist.text()
        characters = self.edit_chars.toPlainText()

        if not title or not outline:
            self.diagnose_result.setHtml("<span style='color: #ff1744;'>⚠️ 请先填写标题和大纲！</span>")
            return

        # 显示诊断中状态
        self.diagnose_result.setHtml("<span style='color: #00e676;'>🤔 资深编辑诊断中，请稍候...</span>")
        self.status_changed.emit("诊断中...")

        # 构建诊断提示词
        diagnose_prompt = f"""你是一位拥有8年网文编辑经验的起点金牌编辑。请对以下小说设定进行专业诊断评估：

## 基本信息
- 标题: {title}
- 题材: {genre}
- 主角: {protagonist or "未设定"}

## 故事大纲
{outline}

## 人物设定
{characters or "未设定"}

请从以下6个维度进行评估并给出分数(0-100)和修改建议：

1. **开篇吸引力**: 前三章是否能抓住读者？金手指是否够早出现？
2. **题材契合度**: 设定与{genre}题材的契合程度
3. **人设讨喜度**: 主角人设是否讨喜？是否有记忆点？
4. **升级体系**: 力量体系/剧情升级设计是否合理有盼头？
5. **商业化潜力**: 是否有热门元素？爽点密度如何？
6. **节奏把控**: 整体节奏设计是否合理？是否有注水风险？

请以JSON格式返回诊断结果：
{{
    "开篇吸引力": {{"分数": XX, "评价": "..."}},
    "题材契合度": {{"分数": XX, "评价": "..."}},
    "人设讨喜度": {{"分数": XX, "评价": "..."}},
    "升级体系": {{"分数": XX, "评价": "..."}},
    "商业化潜力": {{"分数": XX, "评价": "..."}},
    "节奏把控": {{"分数": XX, "评价": "..."}},
    "综合评级": "S/A/B/C/D",
    "修改建议": ["建议1", "建议2", "建议3"]
}}"""

        # 调用 LLM 进行诊断
        try:
            from core.model_manager import ModelManager

            # 使用默认模型
            mm = ModelManager()

            # 调用 API
            result = mm.generate(
                prompt=diagnose_prompt,
                temperature=0.7,
                system_prompt="你是一位资深网文编辑，擅长评估和指导网文创作。请用专业但易懂的语言给出诊断结果。"
            )

            # 解析结果
            if result.startswith("[错误]"):
                # API 调用失败，显示友好错误
                self.diagnose_result.setHtml(f"""
                <h3 style='color: #ff1744;'>⚠️ 诊断服务暂不可用</h3>
                <p>{result}</p>
                <p style='color: #888;'>请检查 API Key 配置后重试</p>
                """)
                return

            # 尝试解析 JSON
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    import json
                    diagnosis = json.loads(json_match.group())

                    # 构建 HTML 报告
                    def get_color(score):
                        if score >= 80: return "#00e676"
                        if score >= 60: return "#ffb300"
                        return "#ff1744"

                    html = f"""
                    <h3 style='color: #00e676;'>✅ 诊断完成 - {diagnosis.get('综合评级', 'B')}</h3>
                    <p><b>标题:</b> {title}</p>
                    <p><b>题材:</b> {genre}</p>
                    <hr>
                    """

                    for dim, data in [
                        ("开篇吸引力", diagnosis.get("开篇吸引力", {})),
                        ("题材契合度", diagnosis.get("题材契合度", {})),
                        ("人设讨喜度", diagnosis.get("人设讨喜度", {})),
                        ("升级体系", diagnosis.get("升级体系", {})),
                        ("商业化潜力", diagnosis.get("商业化潜力", {})),
                        ("节奏把控", diagnosis.get("节奏把控", {}))
                    ]:
                        score = data.get("分数", 0)
                        eval_text = data.get("评价", "")
                        color = get_color(score)
                        html += f'<p><b>{dim}:</b> <span style="color: {color}; font-weight: bold;">{score}分</span> - {eval_text}</p>'

                    suggestions = diagnosis.get("修改建议", [])
                    if suggestions:
                        html += '<hr><p><b>📝 修改建议:</b></p><ul>'
                        for s in suggestions:
                            html += f'<li>{s}</li>'
                        html += '</ul>'

                    self.diagnose_result.setHtml(html)

                    # 存储诊断结果并显示采纳按钮
                    self.last_diagnosis = diagnosis
                    self.btn_apply_advice.setVisible(True)
                else:
                    # 无法解析 JSON，直接显示原始结果
                    self.diagnose_result.setPlainText(result)
            except json.JSONDecodeError:
                # JSON 解析失败，显示原始结果
                self.diagnose_result.setPlainText(result)

        except Exception as e:
            self.diagnose_result.setHtml(f"""
            <h3 style='color: #ff1744;'>⚠️ 诊断失败</h3>
            <p>{str(e)}</p>
            """)
        finally:
            self.status_changed.emit("系统待命")

    def _on_apply_diagnosis_advice(self):
        """采纳诊断建议并修改大纲和人物设定"""
        if not self.last_diagnosis:
            return

        suggestions = self.last_diagnosis.get("修改建议", [])
        if not suggestions:
            QMessageBox.information(self, "提示", "没有可采纳的建议")
            return

        # 构建修改后的大纲（追加建议）
        current_outline = self.edit_outline.toPlainText()
        new_outline = current_outline

        # 获取各项评价，生成改进建议文本
        improvements = []
        for dim, data in self.last_diagnosis.items():
            if dim == "综合评级" or dim == "修改建议":
                continue
            score = data.get("分数", 0)
            eval_text = data.get("评价", "")
            if score < 70:  # 只采纳低分项的建议
                improvements.append(f"【{dim}】{eval_text}")

        if improvements:
            new_outline += "\n\n" + "="*40 + "\n【根据诊断建议的改进】\n"
            for imp in improvements:
                new_outline += f"- {imp}\n"

        # 获取人物设定的改进建议
        chars = self.edit_chars.toPlainText()
        # 如果有人物相关的低分建议，追加到人物设定
        for dim, data in self.last_diagnosis.items():
            if "人设" in dim:
                score = data.get("分数", 0)
                if score < 70:
                    chars += f"\n\n【根据诊断建议改进】{data.get('评价', '')}"

        # 更新文本框
        self.edit_outline.setText(new_outline)
        if chars != self.edit_chars.toPlainText():
            self.edit_chars.setText(chars)

        # 隐藏按钮
        self.btn_apply_advice.setVisible(False)

        QMessageBox.information(
            self, "采纳成功",
            "已根据诊断建议更新大纲和人物设定！\n请检查并确认修改内容。"
        )

    def _on_chat_send(self):
        """发送聊天消息 - 通过信号委托给主窗口处理"""
        text = self.chat_input.text().strip()
        if not text:
            return
        user_html = f"<div style='color: #ffffff; margin: 10px 0; text-align: right;'><b>👤 作者:</b> {text}</div>"
        self.chat_history.append(user_html)
        self.chat_input.clear()

        # 发射信号，由主窗口启动 AgenticChatWorker
        self.request_ai_chat.emit(text)

    def append_ai_reply(self, html_text: str):
        """接收 AI 回复并追加到聊天历史"""
        response = f"<div style='color: #00f5f5; margin: 10px 0;'><b>🤖 AI 责编:</b> {html_text}</div>"
        self.chat_history.append(response)


# ============================================================================
# 生产视图 (ProductionView) - 包含操作按钮和信号
# ============================================================================
class ProductionView(QWidget):
    """生产视图 - 带操作按钮和自定义信号"""

    # 信号：视图层发出请求
    request_start = pyqtSignal()      # 请求开始写作
    request_pause = pyqtSignal()     # 请求暂停
    request_resume = pyqtSignal()    # 请求恢复
    status_changed = pyqtSignal(str)  # 状态变更信号
    save_config = pyqtSignal()       # 保存配置信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_dir = "novels/default"
        self.init_ui()

    def set_project_dir(self, project_dir: str):
        """设置项目目录"""
        self.project_dir = project_dir

    def reload_data(self):
        """重新加载项目数据"""
        project = NovelProject(self.project_dir)

        # 加载大纲
        outline = project.load_outline()
        if outline:
            self.outline_edit.setPlainText(outline)

        # 加载人物
        characters = project.load_characters()
        if characters:
            self.chars_edit.setPlainText(characters)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 生产控制栏 =====
        control_bar = QFrame()
        control_bar.setFixedHeight(50)
        control_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px 16px;
                font-family: Consolas;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_HOVER};
                border-color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(20, 0, 20, 0)

        # 状态标签
        self.status_label = QLabel("🟢 等待开始")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS}; font-weight: bold;")
        control_layout.addWidget(self.status_label)

        control_layout.addStretch()

        # 保存按钮
        self.btn_save = QPushButton("💾 保存设定")
        self.btn_save.clicked.connect(self._on_save)
        control_layout.addWidget(self.btn_save)

        # 开始/暂停按钮
        self.btn_start = QPushButton("▶ 确认开机 (START)")
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: #000;
                font-weight: bold;
            }}
        """)
        self.btn_start.clicked.connect(self._on_start)
        control_layout.addWidget(self.btn_start)

        self.btn_pause = QPushButton("⏸ 暂停 (PAUSE)")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self._on_pause)
        control_layout.addWidget(self.btn_pause)

        self.btn_resume = QPushButton("⏩ 恢复 (RESUME)")
        self.btn_resume.setEnabled(False)
        self.btn_resume.clicked.connect(self._on_resume)
        control_layout.addWidget(self.btn_resume)

        # 黄金三章评估按钮
        self.btn_golden_check = QPushButton("🏆 黄金三章评估")
        self.btn_golden_check.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_WARNING};
                color: #000;
                border: 2px solid {CyberpunkTheme.FG_WARNING};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #ffca28;
            }}
            QPushButton:disabled {{
                background-color: #475569;
                border-color: #475569;
                color: #94a3b8;
            }}
        """)
        self.btn_golden_check.clicked.connect(self._on_golden_check)
        control_layout.addWidget(self.btn_golden_check)

        layout.addWidget(control_bar)

        # ===== 核心三栏布局 =====
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：情绪图+工牌
        left_panel = QSplitter(Qt.Orientation.Vertical)

        # 情绪波浪图
        try:
            from ui.components import EmotionWavePanel
            self.emotion_panel = EmotionWavePanel()
        except ImportError:
            from components import EmotionWavePanel
            self.emotion_panel = EmotionWavePanel()
        left_panel.addWidget(self.emotion_panel)

        # Agent 列表
        agent_container = QWidget()
        agent_layout = QVBoxLayout(agent_container)
        agent_layout.setContentsMargins(5, 5, 5, 5)
        agent_label = QLabel("👥 AGENT CLUSTER")
        agent_label.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY}; font-weight: bold; font-family: Consolas;")
        agent_layout.addWidget(agent_label)

        # Agent 定义
        AVATAR_DIR = str(Path(__file__).resolve().parent.parent / "avatars")
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

        # 迷你工牌滚动区域
        mini_scroll = QScrollArea()
        mini_scroll.setWidgetResizable(True)
        mini_scroll.setStyleSheet("border: none; background: transparent;")
        mini_scroll_widget = QWidget()
        mini_scroll_layout = QVBoxLayout(mini_scroll_widget)

        # 导入并创建工牌
        try:
            from ui.components import MiniAgentBadge, MinimalistBadge
        except ImportError:
            from components import MiniAgentBadge, MinimalistBadge

        self.mini_badges = {}
        self.large_badges = {}

        for name, role, emoji, avatar in agent_defs:
            mini_badge = MiniAgentBadge(name, emoji)
            mini_badge.clicked.connect(lambda n=name: self._on_agent_badge_clicked(n))
            self.mini_badges[name] = mini_badge
            mini_scroll_layout.addWidget(mini_badge)

            large_badge = MinimalistBadge(name, role, f"Core Logic for {name}", f"{AVATAR_DIR}/{avatar}", emoji)
            large_badge.hide()
            self.large_badges[name] = large_badge

        mini_scroll_layout.addStretch()
        mini_scroll.setWidget(mini_scroll_widget)
        agent_layout.addWidget(mini_scroll)

        # 大工牌展示区
        self.large_badge_area = QWidget()
        self.large_badge_layout = QVBoxLayout(self.large_badge_area)
        self.large_badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.large_badge_layout.addWidget(QLabel("Click a mini badge to inspect", styleSheet=f"color: {CyberpunkTheme.TEXT_DIM};"))
        agent_layout.addWidget(self.large_badge_area)

        left_panel.addWidget(agent_container)

        left_panel.setStretchFactor(0, 2)
        left_panel.setStretchFactor(1, 1)
        main_splitter.addWidget(left_panel)

        # 中间：文稿区+日志
        center_panel = QSplitter(Qt.Orientation.Vertical)

        # 文稿查看器
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(10, 10, 10, 0)

        self.manuscript_viewer = QTextBrowser()
        self.manuscript_viewer.setStyleSheet(f"""
            background-color: #1e1e1e; color: #d4d4d4;
            font-family: 'Microsoft YaHei', Consolas; font-size: 15px;
            line-height: 1.8; padding: 20px; border-radius: 8px; border: 1px solid #333;
        """)
        self.manuscript_viewer.setPlaceholderText(">> AI 实时生成正文将在这里显示...")
        # 性能优化
        self.manuscript_viewer.setUndoRedoEnabled(False)
        self.manuscript_viewer.document().setMaximumBlockCount(1000)
        editor_layout.addWidget(self.manuscript_viewer)
        center_panel.addWidget(editor_container)

        # 日志面板
        try:
            from ui.components import LogPanel
            self.log_panel = LogPanel()
        except ImportError:
            from components import LogPanel
            self.log_panel = LogPanel()
        center_panel.addWidget(self.log_panel)
        center_panel.setStretchFactor(0, 7)
        center_panel.setStretchFactor(1, 3)

        main_splitter.addWidget(center_panel)

        # 右侧：设定参考区
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 10, 5)

        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet(f"""
            QTabBar::tab {{ background: {CyberpunkTheme.BG_DARK}; color: white; padding: 8px 12px; }}
        """)

        self.outline_edit = QTextEdit()
        self.chars_edit = QTextEdit()
        self.rules_edit = QTextEdit()
        self.eval_browser = QTextBrowser()

        for widget in [self.outline_edit, self.chars_edit, self.rules_edit]:
            widget.setStyleSheet(f"background-color: {CyberpunkTheme.BG_MEDIUM}; color: {CyberpunkTheme.TEXT_PRIMARY}; font-size: 13px; font-family: Consolas;")

        self.right_tabs.addTab(self.outline_edit, "📖 剧情大纲")
        self.right_tabs.addTab(self.chars_edit, "👤 角色档案")
        self.right_tabs.addTab(self.rules_edit, "⚙️ 世界法则")
        self.right_tabs.addTab(self.eval_browser, "🧐 诊断报告")

        right_layout.addWidget(self.right_tabs)
        right_panel.setMinimumWidth(300)

        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 6)
        main_splitter.setStretchFactor(2, 2)

        layout.addWidget(main_splitter)

    def _on_start(self):
        """开始写作"""
        self.status_changed.emit("写作中...")
        self.request_start.emit()

    def _on_pause(self):
        """暂停"""
        self.status_changed.emit("已暂停")
        self.request_pause.emit()

    def _on_resume(self):
        """恢复"""
        self.status_changed.emit("写作中...")
        self.request_resume.emit()

    def _on_golden_check(self):
        """黄金三章评估"""
        from pathlib import Path

        chapters_dir = Path(self.project_dir) / "chapters"

        # 检查前三章是否存在
        missing_chapters = []
        for i in range(1, 4):
            ch_file = chapters_dir / f"chapter_{i:03d}.md"
            if not ch_file.exists():
                missing_chapters.append(f"chapter_{i:03d}.md")

        if missing_chapters:
            QMessageBox.warning(
                self,
                "无法评估",
                f"需生成完前三章才能评估！\n\n缺少: {', '.join(missing_chapters)}"
            )
            return

        # 禁用按钮，显示评估中
        self.btn_golden_check.setEnabled(False)
        self.btn_golden_check.setText("评估中...")
        self.append_log("正在启动黄金三章评估...", "system")

        # 启动评估Worker
        try:
            from ui.worker_thread import GoldenThreeWorker
            self.golden_worker = GoldenThreeWorker(self.project_dir)
            self.golden_worker.result_signal.connect(self._on_golden_result)
            self.golden_worker.error_signal.connect(self._on_golden_error)
            self.golden_worker.start()
        except Exception as e:
            self.append_log(f"评估启动失败: {e}", "error")
            self.btn_golden_check.setEnabled(True)
            self.btn_golden_check.setText("🏆 黄金三章评估")

    def _on_golden_result(self, report_html: str):
        """评估完成，显示报告"""
        self.btn_golden_check.setEnabled(True)
        self.btn_golden_check.setText("🏆 黄金三章评估")
        self.append_log("黄金三章评估完成", "success")

        # 显示报告对话框
        try:
            from ui.dialogs import GoldenReportDialog
            dialog = GoldenReportDialog(report_html, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "显示报告失败", str(e))

    def _on_golden_error(self, error_msg: str):
        """评估出错"""
        self.btn_golden_check.setEnabled(True)
        self.btn_golden_check.setText("🏆 黄金三章评估")
        self.append_log(f"评估失败: {error_msg}", "error")
        QMessageBox.warning(self, "评估失败", error_msg)

    def _on_agent_badge_clicked(self, agent_name: str):
        """点击迷你工牌，显示大工牌"""
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

    def update_agent_status(self, name: str, status: str, task: str = ""):
        """更新 Agent 状态"""
        colors = {"idle": CyberpunkTheme.FG_SUCCESS, "thinking": CyberpunkTheme.FG_INFO,
                  "writing": CyberpunkTheme.FG_PRIMARY, "auditing": CyberpunkTheme.FG_ACCENT,
                  "conflict": CyberpunkTheme.FG_DANGER}
        color_hex = colors.get(status.lower(), CyberpunkTheme.FG_SUCCESS)

        if name in self.large_badges:
            self.large_badges[name].set_status(status, task)
        if name in self.mini_badges:
            self.mini_badges[name].set_status(color_hex)

    def _on_save(self):
        """保存配置"""
        self.save_config.emit()

    def append_log(self, message: str, level: str = "info", agent: str = None):
        """添加日志"""
        self.log_panel.append_log(message, level, agent)

    def append_text(self, text: str):
        """追加文本到文稿区"""
        cursor = self.manuscript_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.manuscript_viewer.setTextCursor(cursor)
        self.manuscript_viewer.ensureCursorVisible()

    def clear_text(self):
        """清空文稿区"""
        self.manuscript_viewer.clear()

    def update_emotion_curve(self, expected: list, actual: list, chapter: int, total: int):
        """更新情绪曲线"""
        self.emotion_panel.update_curve(expected, actual, chapter, total)


# ============================================================================
# 项目仓库视图 (ProjectVaultView)
# ============================================================================
class ProjectVaultView(QWidget):
    """项目仓库视图 - 左侧书籍列表，右侧阅读/资料"""

    def __init__(self, project_dir: str, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir
        self.init_ui()
        self.load_projects()

    def reload_data(self):
        """重新加载数据"""
        self.load_projects()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ===== 左侧：书籍列表 =====
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("📚 我的作品")
        title.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY}; font-weight: bold; font-size: 16px;")
        left_layout.addWidget(title)

        self.book_list = QListWidget()
        self.book_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)
        self.book_list.itemClicked.connect(self._on_book_selected)
        left_layout.addWidget(self.book_list)

        # 刷新按钮
        btn_refresh = QPushButton("🔄 刷新列表")
        btn_refresh.clicked.connect(self.load_projects)
        left_layout.addWidget(btn_refresh)

        splitter.addWidget(left_panel)

        # ===== 右侧：阅读/资料标签页 =====
        right_tabs = QTabWidget()
        right_tabs.setStyleSheet(f"""
            QTabBar::tab {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_SECONDARY};
                padding: 10px 20px;
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QTabBar::tab:selected {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                color: {CyberpunkTheme.FG_PRIMARY};
            }}
        """)

        # 阅读正文标签
        self.read_tab = QTextBrowser()
        self.read_tab.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {CyberpunkTheme.BG_DARK};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                padding: 20px;
                font-family: 'Microsoft YaHei';
                font-size: 15px;
                line-height: 1.8;
            }}
        """)
        self.read_tab.setPlaceholderText("选择左侧作品开始阅读...")
        right_tabs.addTab(self.read_tab, "📖 阅读正文")

        # 资料库标签
        self.material_tab = QWidget()
        material_layout = QVBoxLayout(self.material_tab)

        material_info = QLabel("📁 项目资料库")
        material_info.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY};")
        material_layout.addWidget(material_info)

        self.material_list = QListWidget()
        material_layout.addWidget(self.material_list)

        right_tabs.addTab(self.material_tab, "📂 资料库")

        splitter.addWidget(right_tabs)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

    def load_projects(self):
        """加载所有项目"""
        self.book_list.clear()
        novels_dir = Path("novels")

        if not novels_dir.exists():
            novels_dir.mkdir(parents=True)

        for project in novels_dir.iterdir():
            if project.is_dir():
                # 尝试读取项目配置
                config_file = project / "project_config.json"
                if config_file.exists():
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        title = config.get("title", project.name)
                        genre = config.get("genre", "未知")
                        item_text = f"{title}\n[{genre}]"
                    except:
                        item_text = project.name
                else:
                    item_text = project.name

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, str(project))
                self.book_list.addItem(item)

        if self.book_list.count() == 0:
            self.book_list.addItem("暂无项目，去前期筹备创建吧！")

    def _on_book_selected(self, item):
        """选择书籍"""
        project_path = item.data(Qt.ItemDataRole.UserRole)
        if not project_path:
            return

        # 加载章节列表
        self.material_list.clear()
        chapters_dir = Path(project_path) / "chapters"

        if chapters_dir.exists():
            chapters = sorted(chapters_dir.glob("chapter_*.md"))
            full_text = ""
            for ch in chapters:
                try:
                    content = ch.read_text(encoding="utf-8")
                    full_text += f"\n\n{'='*50}\n{ch.stem}\n{'='*50}\n\n{content}"
                    self.material_list.addItem(ch.name)
                except:
                    pass

            self.read_tab.setPlainText(full_text if full_text else "暂无内容")


# ============================================================================
# 工作流集市视图 (SkillMarketView)
# ============================================================================
class SkillMarketView(QWidget):
    """工作流/技能集市视图 - 内置(只读) + 自定义(可编辑)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("🧩 提示词与工作流集市 (Skill Market)")
        header.setFont(QFont(Typography.FONT_MONO, Typography.SIZE_H1, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {CyberpunkTheme.FG_PRIMARY}; margin: 20px 0;")
        layout.addWidget(header)

        # ===== CLI 控制区域 =====
        cli_group = QGroupBox("⚡ CLI 控制 (快速创建)")
        cli_layout = QFormLayout(cli_group)

        self.edit_skill_name = QLineEdit()
        self.edit_skill_name.setPlaceholderText("输入技能名称...")
        cli_layout.addRow("技能名称:", self.edit_skill_name)

        self.edit_skill_content = QTextEdit()
        self.edit_skill_content.setPlaceholderText("输入技能内容 (Markdown格式)...")
        self.edit_skill_content.setMaximumHeight(150)
        cli_layout.addRow("技能内容:", self.edit_skill_content)

        self.btn_create_skill = QPushButton("➕ 创建技能")
        self.btn_create_skill.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: #000;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #00cc55; }}
        """)
        self.btn_create_skill.clicked.connect(self._on_create_skill_from_input)
        cli_layout.addRow("", self.btn_create_skill)

        layout.addWidget(cli_group)

        # ===== 原有的新建按钮 =====
        btn_create = QPushButton("➕ 新建自定义工作流 (Create Custom Skill)")
        btn_create.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.BG_MEDIUM}; color: {CyberpunkTheme.FG_GOLD};
                border: 2px dashed {CyberpunkTheme.FG_GOLD}; border-radius: 8px;
                padding: 12px; font-family: Consolas; font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {CyberpunkTheme.BG_HOVER}; }}
        """)
        btn_create.clicked.connect(self._on_create_custom)
        layout.addWidget(btn_create)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(20)
        self._load_all_skills()
        scroll.setWidget(self._container)
        layout.addWidget(scroll)

    def _on_create_skill_from_input(self):
        """从输入框创建技能 (支持 CLI)"""
        name = self.edit_skill_name.text().strip()
        content = self.edit_skill_content.toPlainText().strip()

        if not name:
            # 使用状态栏消息替代弹窗，避免无头环境阻塞
            self._show_status_message("请输入技能名称！", is_error=True)
            return

        if not content:
            content = f"# {name}\n\n在此编写你的自定义提示词/工作流规则"

        # 保存技能
        safe = name.replace(" ", "-").lower()
        dest = Path("user_data/custom_skills") / safe
        dest.mkdir(parents=True, exist_ok=True)

        # 保存为 SKILL.md
        skill_file = dest / "SKILL.md"
        skill_file.write_text(content, encoding="utf-8")

        # 清空输入框
        self.edit_skill_name.clear()
        self.edit_skill_content.clear()

        # 刷新列表
        self._load_all_skills()

        # 使用状态栏消息替代弹窗
        self._show_status_message(f"✅ 技能 [{name}] 已创建！")

    def _show_status_message(self, message: str, is_error: bool = False):
        """显示状态栏消息（CLI友好）"""
        # 尝试通过dashboard的状态栏显示
        try:
            if hasattr(self, 'window') and hasattr(self.window(), 'global_status_bar'):
                self.window().global_status_bar.update_status(message)
                return
        except RuntimeError:
            pass

        # 如果无法访问状态栏，使用print输出（CLI模式）
        prefix = "❌" if is_error else "✅"
        print(f"{prefix} {message}")

    def _load_all_skills(self):
        """加载内置 + 自定义技能"""
        # 清空网格
        while self._grid.count():
            w = self._grid.takeAt(0).widget()
            if w:
                w.deleteLater()

        row, col = 0, 0

        # --- 内置技能 ---
        builtin_dir = Path("skills")
        if builtin_dir.exists():
            lbl = QLabel("🔒 内置系统技能 (Built-in)")
            lbl.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY}; font-weight: bold; font-size: 13px; font-family: Consolas;")
            self._grid.addWidget(lbl, row, 0, 1, 3)
            row += 1
            for sp in sorted(builtin_dir.iterdir()):
                if sp.is_dir():
                    self._grid.addWidget(self._create_skill_card(sp.name, str(sp), False), row, col)
                    col += 1
                    if col >= 3:
                        col = 0
                        row += 1
            if col != 0:
                col = 0
                row += 1

        # --- 自定义技能 ---
        custom_dir = Path("user_data/custom_skills")
        custom_dir.mkdir(parents=True, exist_ok=True)
        lbl2 = QLabel("🟢 我的自定义技能 (Custom)")
        lbl2.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS}; font-weight: bold; font-size: 13px; font-family: Consolas;")
        self._grid.addWidget(lbl2, row, 0, 1, 3)
        row += 1
        has_custom = False
        for sp in sorted(custom_dir.iterdir()):
            if sp.is_dir():
                has_custom = True
                self._grid.addWidget(self._create_skill_card(sp.name, str(sp), True), row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
        if not has_custom:
            hint = QLabel("暂无自定义技能，点击上方按钮创建")
            hint.setStyleSheet(f"color: {CyberpunkTheme.TEXT_DIM}; font-style: italic;")
            self._grid.addWidget(hint, row, 0, 1, 3)

    def _create_skill_card(self, skill_name: str, skill_path: str, is_custom: bool) -> QFrame:
        card = QFrame()
        card.setFixedSize(350, 140)
        card.setStyleSheet(f"""
            QFrame {{ background-color: {CyberpunkTheme.BG_MEDIUM}; border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 10px; }}
            QFrame:hover {{ border-color: {CyberpunkTheme.FG_PRIMARY}; background-color: {CyberpunkTheme.BG_HOVER}; }}
        """)
        lo = QVBoxLayout(card)
        lo.setContentsMargins(16, 14, 16, 12)
        lo.setSpacing(6)

        title_row = QHBoxLayout()
        icon = QLabel("🟢" if is_custom else "📜")
        icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        title = QLabel(skill_name.replace("-", " ").title())
        title.setFont(QFont(Typography.FONT_PRIMARY, 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CyberpunkTheme.TEXT_PRIMARY}; background: transparent; border: none;")
        title_row.addWidget(icon)
        title_row.addWidget(title)
        title_row.addStretch()
        lo.addLayout(title_row)

        tag = "Custom" if is_custom else "Built-in"
        desc = QLabel(f"{tag} · {skill_name}")
        desc.setFont(QFont(Typography.FONT_PRIMARY, 10))
        desc.setStyleSheet(f"color: {CyberpunkTheme.TEXT_SECONDARY}; background: transparent; border: none;")
        desc.setWordWrap(True)
        lo.addWidget(desc)
        lo.addStretch()

        bot = QHBoxLayout()
        bot.addStretch()
        btn_text = "编辑" if is_custom else "查看"
        btn = QPushButton(btn_text)
        btn.setFixedHeight(28)
        btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 4px; padding: 2px 14px; font-size: 11px; }}
            QPushButton:hover {{ border-color: {CyberpunkTheme.FG_PRIMARY}; background-color: {CyberpunkTheme.BG_LIGHT}; }}
        """)
        btn.clicked.connect(lambda _, n=skill_name, p=skill_path, c=is_custom: self._open_skill_editor(n, p, c))
        bot.addWidget(btn)
        lo.addLayout(bot)
        return card

    def _open_skill_editor(self, name: str, path: str, is_custom: bool):
        from ui.dialogs import SkillEditorDialog
        dlg = SkillEditorDialog(name, path, is_custom, self)
        dlg.skill_changed.connect(self._load_all_skills)
        dlg.exec()

    def _on_create_custom(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建自定义工作流", "请输入技能名称:")
        if not ok or not name.strip():
            return
        safe = name.strip().replace(" ", "-").lower()
        dest = Path("user_data/custom_skills") / safe
        dest.mkdir(parents=True, exist_ok=True)
        prompt_file = dest / "prompt.yaml"
        if not prompt_file.exists():
            prompt_file.write_text(f"# {name}\n# 在此编写你的自定义提示词/工作流规则\n", encoding="utf-8")
        self._open_skill_editor(safe, str(dest), True)
