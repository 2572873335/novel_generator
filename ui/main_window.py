"""
主窗口 - ProducerDashboard (v5.0 架构优化版)
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
    from ui.views import (
        GlobalStatusBar, MainNavigationBar, PreProductionView,
        ProductionView, ProjectVaultView
    )
except ImportError:
    from views import (
        GlobalStatusBar, MainNavigationBar, PreProductionView,
        ProductionView, ProjectVaultView
    )

# 导入对话框
try:
    from ui.dialogs import (
        ProgressResumeDialog, SettingsDialog, DocumentViewerDialog
    )
except ImportError:
    from dialogs import (
        ProgressResumeDialog, SettingsDialog, DocumentViewerDialog
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
# 主窗口 - v5.0 架构优化版
# ============================================================================
class ProducerDashboard(QMainWindow):
    """
    制片人仪表板主窗口 - v5.0 架构优化版

    架构特点：
    1. 按钮迁移：操作按钮移入对应视图
    2. 信号解耦：视图通过信号与主窗口通信
    3. 数据同步：切换视图时自动重新加载数据
    """

    def __init__(self, project_dir: str = None):
        super().__init__()

        self.project_dir = project_dir or "novels/default"
        self.worker = None
        self.project_config = None
        self.start_chapter = 1

        self.init_ui()

        # 读取项目配置
        self.load_project_config()

        # 显示项目信息
        self.display_project_info()

    def init_ui(self):
        """初始化UI - v5.0 架构优化版"""
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

        # === Page A: 前期筹备 (带操作按钮) ===
        self.view_preprod = PreProductionView()
        self.view_preprod.set_project_dir(self.project_dir)
        self.main_stack.addWidget(self.view_preprod)

        # === Page B: 生产监控 (带操作按钮) ===
        self.view_prod = ProductionView()
        self.view_prod.set_project_dir(self.project_dir)
        self.main_stack.addWidget(self.view_prod)

        # === Page C: 项目仓库 (带数据同步) ===
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

        # ====== 6. 连接视图信号 ======
        self._connect_view_signals()

        # ====== 7. 数据同步：切换视图时重新加载 ======
        self.main_stack.currentChanged.connect(self._on_view_changed)

    def _connect_view_signals(self):
        """连接视图信号 - 实现信号解耦"""

        # === PreProductionView 信号 ===
        self.view_preprod.request_generate.connect(self._on_request_generate)
        self.view_preprod.request_evaluate.connect(self._on_request_evaluate)
        self.view_preprod.request_start.connect(self._on_request_start)
        self.view_preprod.status_changed.connect(self._on_status_changed)

        # === ProductionView 信号 ===
        self.view_prod.request_start.connect(self._on_prod_request_start)
        self.view_prod.request_pause.connect(self._on_prod_request_pause)
        self.view_prod.request_resume.connect(self._on_prod_request_resume)
        self.view_prod.save_config.connect(self._on_save_config)
        self.view_prod.status_changed.connect(self._on_status_changed)

    def _on_view_changed(self, index: int):
        """视图切换时重新加载数据"""
        if index == 0:
            # 切换到前期筹备视图
            self.view_preprod.reload_data()
        elif index == 1:
            # 切换到生产视图
            self.view_prod.reload_data()
        elif index == 2:
            # 切换到项目仓库视图
            self.view_vault.reload_data()

    def _on_status_changed(self, status: str):
        """状态变更处理"""
        self.global_status_bar.update_status(status)

    # === PreProductionView 信号处理 ===
    def _on_request_generate(self):
        """处理生成请求"""
        self.global_status_bar.update_status("生成中...", "info")
        # TODO: 实现实际生成逻辑
        self.global_status_bar.update_status("系统待命", "success")

    def _on_request_evaluate(self):
        """处理评估请求"""
        self.global_status_bar.update_status("评估中...", "warning")
        # TODO: 实现实际评估逻辑
        self.global_status_bar.update_status("系统待命", "success")

    def _on_request_start(self):
        """处理开始写作请求"""
        self.global_status_bar.update_status("准备开始...", "info")
        # 切换到生产视图
        self.main_stack.setCurrentIndex(1)
        # 触发生产视图的开始
        self.view_prod.btn_start.click()

    # === ProductionView 信号处理 ===
    def _on_prod_request_start(self):
        """生产视图请求开始"""
        self.do_start_generation()

    def _on_prod_request_pause(self):
        """生产视图请求暂停"""
        self.on_pause_generation()

    def _on_prod_request_resume(self):
        """生产视图请求恢复"""
        self.on_resume_generation()

    def _on_save_config(self):
        """保存配置"""
        try:
            outline = self.view_prod.outline_edit.toPlainText()
            chars = self.view_prod.chars_edit.toPlainText()
            rules = self.view_prod.rules_edit.toPlainText()

            if self.project_dir:
                project_path = Path(self.project_dir)
                project_path.mkdir(parents=True, exist_ok=True)

                if outline:
                    (project_path / "outline_edit.md").write_text(outline, encoding="utf-8")
                if chars:
                    (project_path / "characters_edit.md").write_text(chars, encoding="utf-8")
                if rules:
                    (project_path / "rules_edit.md").write_text(rules, encoding="utf-8")

                self.view_prod.append_log("设定修改已保存", "success")
        except Exception as e:
            self.view_prod.append_log(f"保存失败: {e}", "error")

    # === 菜单功能 ===
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
        """显示项目信息"""
        if self.project_config:
            title = self.project_config.get("title", "Unknown")
            genre = self.project_config.get("genre", "Unknown")
            chapters = self.project_config.get("target_chapters", 0)

            self.view_prod.append_log(f"=== PROJECT LOADED ===", "system")
            self.view_prod.append_log(f"Title: {title}", "info")
            self.view_prod.append_log(f"Genre: {genre}", "info")
            self.view_prod.append_log(f"Target Chapters: {chapters}", "info")
            self.view_prod.append_log(f"=====================", "system")
        else:
            self.view_prod.append_log("No project config found - starting in demo mode", "warning")

    def on_new_project(self):
        """新建项目"""
        self.project_dir = "novels/default"
        self.project_config = {}
        self.view_prod.append_log("新建项目 - 请在前期筹备室填写项目信息", "info")
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
            "NovelForge v5.0 - AI小说生成系统\n\n"
            "基于Anthropic长运行代理最佳实践的全自动小说创作系统"
        )

    def do_start_generation(self):
        """执行开始生成"""
        if GenerationWorker is None:
            self.view_prod.append_log("ERROR: GenerationWorker not available", "error")
            return

        self.view_prod.append_log("Initializing generation task...", "system")

        config = self.project_config or {}
        target_chapters = config.get("target_chapters", 10)

        self.view_prod.append_log(f"Creating worker for {target_chapters} chapters...", "info")

        worker_config = {
            "target_chapters": target_chapters,
            "checkpoint_interval": 5,
            "start_chapter": self.start_chapter
        }

        self.worker = GenerationWorker(self.project_dir, worker_config)
        self.connect_worker(self.worker)

        # 启动worker
        self.worker.start()

    def on_pause_generation(self):
        """暂停生成"""
        if self.worker:
            self.worker.stop()
        self.view_prod.append_log("Generation paused", "warning")

    def on_resume_generation(self):
        """恢复生成"""
        self.view_prod.append_log("Resuming generation...", "system")

    def connect_worker(self, worker):
        """连接worker信号"""
        self.worker = worker
        worker.log_signal.connect(self.view_prod.append_log)
        worker.text_stream_signal.connect(self.view_prod.append_text)
        worker.emotion_curve_signal.connect(self._on_emotion_curve)

    def _on_emotion_curve(self, data: dict):
        """情绪曲线更新"""
        expected = data.get("expected", [])
        actual = data.get("actual", [])
        chapter = data.get("chapter", 0)
        total = self.worker.config.get("target_chapters", 10) if self.worker else 10

        self.view_prod.update_emotion_curve(expected, actual, chapter, total)


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

    print("[System] 正在点火，启动赛博编辑部中控大屏 v5.0...")

    window = ProducerDashboard(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
