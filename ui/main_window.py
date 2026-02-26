"""
主窗口 - ProducerDashboard
"""

import sys
import json
from pathlib import Path
from datetime import datetime

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
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
    from PyQt6.QtGui import QFont, QColor, QPalette, QTextCursor, QAction, QCursor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available")

# 导入工作线程
try:
    from ui.worker_thread import GenerationWorker
except ImportError:
    GenerationWorker = None

# 导入主题系统
try:
    from ui.themes import CyberpunkTheme, Typography, Spacing, ThemeManager, ThemeSelector
except ImportError:
    from themes import CyberpunkTheme, Typography, Spacing, ThemeManager, ThemeSelector

# 导入视图
try:
    from ui.views import GlobalStatusBar, MainNavigationBar, PreProductionView, ProjectVaultView
except ImportError:
    from views import GlobalStatusBar, MainNavigationBar, PreProductionView, ProjectVaultView

# 导入组件
try:
    from ui.components import (
        FlipCard, AgentCardBack, MiniAgentBadge, MinimalistBadge,
        AgentDetailPanel, AgentMatrixPanel, EmotionWavePanel,
        AutoSaveIndicator, EvaluationCard, LogPanel,
        CircuitBreakerPanel, StatusLightIndicator, RollbackHistoryBars, TopControlPanel
    )
except ImportError:
    from components import (
        FlipCard, AgentCardBack, MiniAgentBadge, MinimalistBadge,
        AgentDetailPanel, AgentMatrixPanel, EmotionWavePanel,
        AutoSaveIndicator, EvaluationCard, LogPanel,
        CircuitBreakerPanel, StatusLightIndicator, RollbackHistoryBars, TopControlPanel
    )

# 导入对话框
try:
    from ui.dialogs import (
        ProgressResumeDialog, PreProductionPanel, ChapterFeedbackDialog,
        SettingsDialog, DocumentViewerDialog
    )
except ImportError:
    from dialogs import (
        ProgressResumeDialog, PreProductionPanel, ChapterFeedbackDialog,
        SettingsDialog, DocumentViewerDialog
    )


# 预生成Worker (简化版)
class PreProdWorker(QThread):
    """预生成工作线程"""
    finished_signal = pyqtSignal(dict)

    def __init__(self, project_dir, action="generate"):
        super().__init__()
        self.project_dir = project_dir
        self.action = action

    def run(self):
        import time
        time.sleep(1)  # 模拟延迟
        self.finished_signal.emit({"outline": "Generated outline...", "characters": "Generated characters..."})


# ============================================================================
# 主窗口 - 全面升级版
# ============================================================================
class ProducerDashboard(QMainWindow):
    """
    制片人仪表板主窗口 - v4.2 UI优化版
    """

    start_generation = pyqtSignal(dict)

    def __init__(self, project_dir: str = None):
        super().__init__()

        self.project_dir = project_dir or "novels/default"
        self.worker = None
        self.project_config = None
        self.start_chapter = 1  # 起始章节

        self.init_ui()

        # 读取项目配置
        self.load_project_config()

        # 显示项目信息
        self.display_project_info()

    def init_ui(self):
        """初始化UI - v5.0 终极创作套件"""
        self.setWindowTitle("NovelForge v5.0 - Ultimate Creator Suite")
        self.setMinimumSize(1600, 900)
        self.setStyleSheet(f"QMainWindow {{ background-color: {CyberpunkTheme.BG_DEEP}; }}")

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ====== 1. 全局状态栏 ======
        self.global_status_bar = GlobalStatusBar()
        main_layout.addWidget(self.global_status_bar)

        # ====== 2. 主导航栏 ======
        self.nav_bar = MainNavigationBar()
        main_layout.addWidget(self.nav_bar)

        # ====== 3. 主堆叠窗口 ======
        self.main_stack = QStackedWidget()

        # === Page A: 前期筹备 ===
        self.view_preprod = PreProductionView()
        self.main_stack.addWidget(self.view_preprod)

        # === Page B: 生产监控 (现有的三栏布局) ===
        self.view_prod = QWidget()
        self._setup_production_view(self.view_prod)
        self.main_stack.addWidget(self.view_prod)

        # === Page C: 项目仓库 ===
        self.view_vault = ProjectVaultView(self.project_dir)
        self.main_stack.addWidget(self.view_vault)

        main_layout.addWidget(self.main_stack)
        self.setCentralWidget(central_widget)

        # ====== 4. 菜单栏 ======
        self.setup_menu()

        # ====== 5. 连接导航按钮 ======
        self.nav_bar.btn_preprod.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        self.nav_bar.btn_prod.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))
        self.nav_bar.btn_vault.clicked.connect(lambda: self.main_stack.setCurrentIndex(2))

    def _setup_production_view(self, parent_widget):
        """设置生产监控视图"""
        layout = QVBoxLayout(parent_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # === 顶部控制栏 ===
        self.top_bar = TopControlPanel()
        layout.addWidget(self.top_bar)

        # === 核心 IDE 三栏布局 (Splitter) ===
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {CyberpunkTheme.BORDER_COLOR}; width: 2px; }}")

        # 左侧：微缩工牌 + 情绪图 + 大工牌展示区
        left_panel = QSplitter(Qt.Orientation.Vertical)
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(400)

        # 左上：情绪波浪图
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
            mini_badge = MiniAgentBadge(name, emoji)
            mini_badge.clicked.connect(self.switch_large_badge)
            self.mini_badges[name] = mini_badge
            mini_scroll_layout.addWidget(mini_badge)

            large_badge = MinimalistBadge(name, role, f"Core Logic for {name}", f"{AVATAR_DIR}/{avatar}", emoji)
            large_badge.hide()
            self.large_badges[name] = large_badge

        mini_scroll_layout.addStretch()
        mini_scroll.setWidget(mini_scroll_widget)
        mini_layout.addWidget(mini_scroll)
        left_panel.addWidget(mini_badge_container)

        # 左下：大工牌展示区
        self.large_badge_area = QWidget()
        self.large_badge_layout = QVBoxLayout(self.large_badge_area)
        self.large_badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.large_badge_layout.addWidget(QLabel("Click a mini badge to inspect", styleSheet=f"color: {CyberpunkTheme.TEXT_DIM};"))
        left_panel.addWidget(self.large_badge_area)

        # 中间：沉浸式创作区
        center_panel = QSplitter(Qt.Orientation.Vertical)
        center_panel.setMinimumWidth(600)

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
        editor_layout.addWidget(self.manuscript_viewer)
        center_panel.addWidget(editor_container)

        self.log_panel = LogPanel()
        center_panel.addWidget(self.log_panel)
        center_panel.setStretchFactor(0, 7)
        center_panel.setStretchFactor(1, 3)

        # 右侧：常驻设定参考区
        right_panel = QWidget()
        right_panel.setMinimumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 10, 5)

        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet(f"QTabBar::tab {{ background: {CyberpunkTheme.BG_DARK}; color: white; padding: 8px 12px; }}")

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

        # 组装三栏
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 6)
        main_splitter.setStretchFactor(2, 2)

        layout.addWidget(main_splitter)

        # 绑定按钮事件
        self.top_bar.btn_start.clicked.connect(self.do_start_generation)
        self.top_bar.btn_pause.clicked.connect(self.on_pause_generation)
        self.top_bar.btn_resume.clicked.connect(self.on_resume_generation)
        self.top_bar.btn_save_config.clicked.connect(self.save_right_panel_configs)
        self.top_bar.btn_generate.clicked.connect(self.trigger_generate_settings)
        self.top_bar.btn_evaluate.clicked.connect(self.trigger_evaluate_settings)

    def save_right_panel_configs(self):
        """保存右侧面板配置"""
        try:
            outline = self.outline_edit.toPlainText()
            chars = self.chars_edit.toPlainText()
            rules = self.rules_edit.toPlainText()

            if self.project_dir:
                project_path = Path(self.project_dir)
                project_path.mkdir(parents=True, exist_ok=True)

                if outline:
                    (project_path / "outline_edit.md").write_text(outline, encoding="utf-8")
                if chars:
                    (project_path / "characters_edit.md").write_text(chars, encoding="utf-8")
                if rules:
                    (project_path / "rules_edit.md").write_text(rules, encoding="utf-8")

                self.log_panel.append_log("设定修改已保存", "success")
        except Exception as e:
            self.log_panel.append_log(f"保存失败: {e}", "error")

    def switch_large_badge(self, agent_name: str):
        """点击迷你工牌，在左下方召唤对应的 3D 翻转大卡片"""
        for i in reversed(range(self.large_badge_layout.count())):
            widget = self.large_badge_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if agent_name in self.large_badges:
            card = self.large_badges[agent_name]
            card.show()
            self.large_badge_layout.addWidget(card)

    def on_text_stream(self, text_chunk: str):
        """接收打字机文本流"""
        cursor = self.manuscript_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text_chunk)
        self.manuscript_viewer.setTextCursor(cursor)
        self.manuscript_viewer.ensureCursorVisible()

    def update_agent_status(self, name: str, status: str, task: str = ""):
        """同步更新大卡片和迷你卡片的状态灯"""
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

                config = self.project_config
                if config:
                    self.outline_edit.setPlainText(config.get("outline", ""))
                    self.chars_edit.setPlainText(config.get("characters", ""))
                    self.rules_edit.setPlainText(config.get("rules", config.get("settings", "")))

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

    def on_new_project(self):
        """新建项目"""
        self.project_dir = "novels/default"
        self.project_config = {}
        self.log_panel.append_log("新建项目 - 请在前期筹备室填写项目信息", "info")
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

    def on_theme_changed(self, theme_key: str):
        """主题切换事件"""
        theme = ThemeManager.get_theme(theme_key)
        for color_name, color_value in theme["colors"].items():
            if hasattr(CyberpunkTheme, color_name):
                setattr(CyberpunkTheme, color_name, color_value)
        self.setStyleSheet("")
        self.update()
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
            "基于Anthropic长运行代理最佳实践的全自动小说创作系统"
        )

    def on_start_generation(self):
        """开始生成"""
        self.check_and_prompt_resume()

    def check_and_prompt_resume(self):
        """检查并提示是否续写"""
        progress_file = Path(self.project_dir) / "novel-progress.txt"
        chapters_dir = Path(self.project_dir) / "chapters"

        has_progress = False

        if progress_file.exists():
            try:
                with open(progress_file, 'r', encoding="utf-8") as f:
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
                self.start_chapter = 1

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

        # 更新Agent状态
        self.update_agent_status("EmotionWriter", "thinking")

        # 启动worker
        self.worker.start()

    def on_pause_generation(self):
        """暂停生成"""
        if self.worker:
            self.worker.stop()
        self.log_panel.append_log("Generation paused", "warning")
        self.update_agent_status("EmotionWriter", "idle")

    def on_resume_generation(self):
        """恢复生成"""
        self.log_panel.append_log("Resuming generation...", "system")

    def connect_worker(self, worker):
        self.worker = worker
        worker.log_signal.connect(self.on_log)
        worker.agent_status_signal.connect(lambda d: self.update_agent_status(d["name"], d["status"], d.get("task", "")))
        worker.emotion_curve_signal.connect(self.on_emotion_curve)
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

    def on_emotion_curve(self, data: dict):
        """情绪曲线更新"""
        expected = data.get("expected", [])
        actual = data.get("actual", [])
        chapter = data.get("chapter", 0)

        total = self.worker.config.get("target_chapters", 10) if self.worker else 10

        self.emotion_panel.update_curve(expected, actual, chapter, total)

    def trigger_generate_settings(self):
        """触发生成设定"""
        self.top_bar.btn_generate.setText("生成中...")
        self.top_bar.btn_generate.setEnabled(False)
        self.top_bar.status_indicator.setText("🔵 Agent 生成设定中...")
        self.right_tabs.setCurrentIndex(0)

        self.pre_worker = PreProdWorker(self.project_dir, action="generate")
        self.pre_worker.finished_signal.connect(self.on_preprod_finished)
        self.pre_worker.start()

    def trigger_evaluate_settings(self):
        """触发毒舌诊断"""
        self.top_bar.btn_evaluate.setText("评估中...")
        self.top_bar.btn_evaluate.setEnabled(False)
        self.top_bar.status_indicator.setText("🟣 编辑审查中...")
        self.right_tabs.setCurrentIndex(3)

        self.pre_worker = PreProdWorker(self.project_dir, action="evaluate")
        self.pre_worker.finished_signal.connect(self.on_preprod_finished)
        self.pre_worker.start()

    def on_preprod_finished(self, data: dict):
        """前期筹备完成回调"""
        self.top_bar.btn_generate.setText("1. 🎲 生成基础设定")
        self.top_bar.btn_generate.setEnabled(True)
        self.top_bar.btn_evaluate.setText("2. 🧐 资深编辑诊断")
        self.top_bar.btn_evaluate.setEnabled(True)
        self.top_bar.status_indicator.setText("🟢 系统待命")

        if "outline" in data: self.outline_edit.setText(data["outline"])
        if "characters" in data: self.chars_edit.setText(data["characters"])
        if "rules" in data: self.rules_edit.setText(data["rules"])
        if "evaluation" in data: self.eval_browser.setHtml(data["evaluation"])


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
    app.setQuitOnLastWindowClosed(False)

    if not project_dir:
        project_dir = "novels/default"

    Path(project_dir).mkdir(parents=True, exist_ok=True)
    app.setQuitOnLastWindowClosed(True)

    print("[System] 正在点火，启动赛博编辑部中控大屏 v4.2...")

    window = ProducerDashboard(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
