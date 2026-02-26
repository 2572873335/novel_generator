"""
视图组件 - 全局状态栏、主导航栏、前期筹备视图、项目仓库视图
"""

import sys
import json
from pathlib import Path

# PyQt6 导入
try:
    from PyQt6.QtWidgets import (
        QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
        QFrame, QStackedWidget, QGroupBox, QFormLayout, QTextEdit,
        QLineEdit, QComboBox, QSpinBox, QTextBrowser, QListWidget,
        QListWidgetItem, QScrollArea, QSplitter, QTabWidget, QTextBrowser
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont, QCursor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available")


# 导入主题系统
try:
    from ui.themes import CyberpunkTheme, Typography, Spacing
except ImportError:
    from themes import CyberpunkTheme, Typography, Spacing


# ============================================================================
# 全局状态栏 (Tier 2)
# ============================================================================
class GlobalStatusBar(QFrame):
    """全局状态栏 - 显示当前项目、进度、模型等信息"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QLabel {{
                color: {CyberpunkTheme.TEXT_SECONDARY};
                font-family: Consolas;
                font-size: 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(30)

        # 状态指示
        self.status_label = QLabel("● 系统就绪")
        self.status_label.setStyleSheet(f"color: {CyberpunkTheme.FG_SUCCESS};")
        layout.addWidget(self.status_label)

        # 当前项目
        self.project_label = QLabel("📁 项目: 未加载")
        layout.addWidget(self.project_label)

        # 进度
        self.progress_label = QLabel("📊 进度: -")
        layout.addWidget(self.progress_label)

        # 当前模型
        self.model_label = QLabel("🤖 模型: DeepSeek-V3")
        layout.addWidget(self.model_label)

        layout.addStretch()

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
        self.setFixedHeight(60)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkTheme.BG_DEEP};
                border-bottom: 2px solid {CyberpunkTheme.BORDER_COLOR};
            }}
            QPushButton {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_SECONDARY};
                border: 2px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 8px;
                padding: 10px 30px;
                font-family: Consolas;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                border-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.FG_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {CyberpunkTheme.FG_PRIMARY};
                color: {CyberpunkTheme.BG_DARK};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(50, 5, 50, 5)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 前期筹备按钮
        self.btn_preprod = QPushButton("📝 前期筹备")
        self.btn_preprod.setFixedWidth(200)
        layout.addWidget(self.btn_preprod)

        # 生产监控按钮
        self.btn_prod = QPushButton("🎬 生产监控")
        self.btn_prod.setFixedWidth(200)
        layout.addWidget(self.btn_prod)

        # 项目仓库按钮
        self.btn_vault = QPushButton("📚 项目仓库")
        self.btn_vault.setFixedWidth(200)
        layout.addWidget(self.btn_vault)


# ============================================================================
# 前期筹备视图 (PreProductionView)
# ============================================================================
class PreProductionView(QWidget):
    """前期筹备视图 - 双轨构思法"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

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

    def _create_selection_page(self):
        """创建选择页 - 左右两个巨大按钮"""
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(100, 50, 100, 50)
        layout.setSpacing(50)

        # 左侧：已有设定按钮
        btn_manual = QPushButton("📝\n\n已有设定\n\n(Manual Settings)")
        btn_manual.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 3px solid {CyberpunkTheme.FG_PRIMARY};
                border-radius: 20px;
                padding: 40px;
                font-family: Consolas;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                border-color: {CyberpunkTheme.FG_GOLD};
            }}
        """)
        btn_manual.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(btn_manual)

        # 右侧：AI对话引导按钮
        btn_ai = QPushButton("🤖\n\n对话生成\n\n(AI Guided)")
        btn_ai.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 3px solid {CyberpunkTheme.FG_SECONDARY};
                border-radius: 20px;
                padding: 40px;
                font-family: Consolas;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CyberpunkTheme.BG_LIGHT};
                border-color: {CyberpunkTheme.FG_GOLD};
            }}
        """)
        btn_ai.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        layout.addWidget(btn_ai)

        return page

    def _create_manual_page(self):
        """创建手动填表页"""
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
        self.edit_genre.addItems(["玄幻", "仙侠", "科幻", "都市", "历史", "悬疑", "言情"])
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

        # 诊断按钮
        btn_diagnose = QPushButton("🔍 资深编辑诊断")
        btn_diagnose.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_WARNING};
                color: #000;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }}
        """)
        btn_diagnose.clicked.connect(self._on_diagnose)
        form_layout.addWidget(btn_diagnose)

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

        # 确认并开始按钮
        btn_confirm = QPushButton("✅ 确认设定并开机")
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkTheme.FG_SUCCESS};
                color: #000;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }}
        """)
        result_layout.addWidget(btn_confirm)

        layout.addWidget(result_container, stretch=2)

        return page

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

    def _on_diagnose(self):
        """执行资深编辑诊断"""
        title = self.edit_title.text()
        outline = self.edit_outline.toPlainText()

        if not title or not outline:
            self.diagnose_result.setHtml("<span style='color: #ff1744;'>⚠️ 请先填写标题和大纲！</span>")
            return

        # 模拟诊断结果
        result = f"""
        <h3 style='color: #00e676;'>✅ 诊断完成</h3>
        <p><b>标题:</b> {title}</p>
        <p><b>题材契合度:</b> <span style='color: #00e676;'>85%</span></p>
        <p><b>开篇吸引力:</b> <span style='color: #ffb300;'>中等</span> - 建议前三章加入更强的冲突</p>
        <p><b>节奏评估:</b> 整体节奏把控良好，但中期可能存在"升级倦怠期"</p>
        <p><b>商业化潜力:</b> <span style='color: #00e676;'>A级</span> - 题材热门，人设讨喜</p>
        <hr>
        <p><b>📝 修改建议:</b></p>
        <ul>
            <li>主角金手指建议在前500字内出现</li>
            <li>反派塑造需要加强动机合理性</li>
            <li>世界观设定建议在第一章通过"事件"自然带出，而非旁白</li>
        </ul>
        """
        self.diagnose_result.setHtml(result)

    def _on_chat_send(self):
        """发送聊天消息"""
        text = self.chat_input.text().strip()
        if not text:
            return

        # 添加用户消息
        user_html = f"""
        <div style='color: #ffffff; margin: 10px 0; text-align: right;'>
            <b>👤 作者:</b> {text}
        </div>
        """
        self.chat_history.append(user_html)
        self.chat_input.clear()

        # 模拟AI回复
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, lambda: self._add_ai_response(text))

    def _add_ai_response(self, user_text):
        """添加AI回复"""
        response = """
        <div style='color: #00f5f5; margin: 10px 0;'>
            <b>🤖 AI 责编:</b> 了解了！这个设定很有趣。<br><br>
            接下来我想了解：<b>你的主角叫什么名字？他/她最渴望得到/改变的是什么？</b><br>
            （这是构建人物弧光的核心）
        </div>
        """
        self.chat_history.append(response)


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
