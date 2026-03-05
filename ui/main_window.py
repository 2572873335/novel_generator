"""
主窗口 - ProducerDashboard (v5.0 架构优化版)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from ui.ui_controller import UIDriver, UIRemoteServer

# Agent 导入
try:
    from agents.initializer_agent import InitializerAgent
except ImportError:
    InitializerAgent = None

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
    from ui.worker_thread import GenerationWorker, AgenticChatWorker
except ImportError:
    GenerationWorker = None
    AgenticChatWorker = None

# 导入主题系统
try:
    from ui.themes import CyberpunkTheme, Typography, Spacing, ThemeManager, ThemeSelector, ThemeStyles
except ImportError:
    from themes import CyberpunkTheme, Typography, Spacing, ThemeManager, ThemeSelector

# 导入视图
try:
    from ui.views import (
        GlobalStatusBar, MainNavigationBar, PreProductionView,
        ProductionView, ProjectVaultView, SkillMarketView
    )
except ImportError:
    from views import (
        GlobalStatusBar, MainNavigationBar, PreProductionView,
        ProductionView, ProjectVaultView, SkillMarketView
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
        self.chat_history = []  # AI 对话历史（多轮记忆）

        self.init_ui()

        # UIDriver - AI 控制 UI 的桥梁
        self.ui_driver = UIDriver(self)

        # IPC 远程控制服务
        self.remote_server = UIRemoteServer(parent=self)
        self.remote_server.command_received.connect(self.ui_driver.execute_commands)
        self.remote_server.start()

        # 读取项目配置
        self.load_project_config()

        # 显示项目信息
        self.display_project_info()

    def init_ui(self):
        """初始化UI - v5.0 架构优化版"""
        self.setWindowTitle("NovelForge v5.1 - Ultimate Creator Suite")
        self.setMinimumSize(1600, 900)

        # 现代化主窗口样式 - 添加渐变背景
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {CyberpunkTheme.BG_DEEP};
            }}
            QMenuBar {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_PRIMARY};
                border-bottom: 1px solid {CyberpunkTheme.BORDER_COLOR};
                padding: 4px;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {CyberpunkTheme.BG_HOVER};
            }}
            QMenu {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                color: #FFFFFF;
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {CyberpunkTheme.BG_LIGHT};
            }}
            QStatusBar {{
                background-color: {CyberpunkTheme.BG_MEDIUM};
                color: {CyberpunkTheme.TEXT_SECONDARY};
                border-top: 1px solid {CyberpunkTheme.BORDER_COLOR};
            }}
        """)

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

        # === Page D: 工作流集市 ===
        self.view_market = SkillMarketView()
        self.main_stack.addWidget(self.view_market)

        main_layout.addWidget(self.main_stack)
        self.setCentralWidget(central_widget)

        # ====== 4. 菜单栏 ======
        self.setup_menu()

        # ====== 5. 连接导航按钮 ======
        self.nav_bar.btn_preprod.clicked.connect(lambda: (self.main_stack.setCurrentIndex(0), self.nav_bar.set_active(0)))
        self.nav_bar.btn_prod.clicked.connect(lambda: (self.main_stack.setCurrentIndex(1), self.nav_bar.set_active(1)))
        self.nav_bar.btn_vault.clicked.connect(lambda: (self.main_stack.setCurrentIndex(2), self.nav_bar.set_active(2)))
        self.nav_bar.btn_market.clicked.connect(lambda: (self.main_stack.setCurrentIndex(3), self.nav_bar.set_active(3)))

        # 初始化导航栏选中状态
        self.nav_bar.set_active(0)

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
        self.view_preprod.request_ai_chat.connect(self._handle_ai_chat)

        # === ProductionView 信号 ===
        self.view_prod.request_start.connect(self._on_prod_request_start)
        self.view_prod.request_pause.connect(self._on_prod_request_pause)
        self.view_prod.request_resume.connect(self._on_prod_request_resume)
        self.view_prod.save_config.connect(self._on_save_config)
        self.view_prod.status_changed.connect(self._on_status_changed)

        # === 全局状态栏信号 ===
        self.global_status_bar.theme_changed.connect(self._on_theme_changed)

    def _on_view_changed(self, index: int):
        """视图切换时重新加载数据"""
        # 更新导航栏选中状态
        self.nav_bar.set_active(index)

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

    def _on_theme_changed(self, theme_key: str):
        """主题切换处理 - 应用主题特定的UI布局风格"""
        # 获取主题样式配置
        styles = ThemeStyles.get_theme_styles(theme_key)

        # 设置主窗口样式
        self.setStyleSheet(f"""
            {styles['main_window']}
            {styles['menubar']}
            QStatusBar {{
                background-color: {ThemeManager.get_color('BG_MEDIUM')};
                color: {ThemeManager.get_color('TEXT_SECONDARY')};
                border-top: 1px solid {ThemeManager.get_color('BORDER_COLOR')};
            }}
        """)

        # 重新加载各组件样式
        self._reload_component_styles(theme_key, styles)

    def _reload_component_styles(self, theme_key: str, styles: dict = None):
        """重新加载各组件样式"""
        if styles is None:
            styles = ThemeStyles.get_theme_styles(theme_key)

        # 重新设置全局状态栏样式
        self.global_status_bar.setStyleSheet(f"""
            {styles['statusbar']}
            QLabel {{
                {styles['label']}
                font-family: {styles['font_family']};
                font-size: {Typography.SIZE_BODY}px;
            }}
            {styles['combobox']}
        """)

        # 重新加载导航栏样式
        self.nav_bar.setStyleSheet(styles['navbar'])

        # 刷新导航按钮选中状态
        current_index = self.main_stack.currentIndex()
        self.nav_bar.set_active(current_index, styles)

    # === PreProductionView 信号处理 ===
    def _on_request_generate(self):
        """处理生成请求 - 使用 InitializerAgent 生成设定"""
        if InitializerAgent is None:
            print("❌ InitializerAgent 不可用")
            return

        # 获取用户输入的配置
        config = self.view_preprod.get_project_config()
        title = config.get("title", "未命名")
        genre = config.get("genre", "玄幻")
        outline = config.get("outline", "")

        print("📝 正在生成角色设定...")
        self.global_status_bar.update_status("生成中...", "info")

        try:
            # 创建 LLM 客户端
            from core.model_manager import create_model_manager
            llm_client = create_model_manager()

            if llm_client is None:
                print("❌ 无法创建 LLM 客户端")
                self.global_status_bar.update_status("生成失败", "error")
                return

            # 创建 InitializerAgent
            project_dir = self.project_dir or "novels/default"
            agent = InitializerAgent(llm_client, project_dir)

            # 生成角色设定（传入完整大纲）
            characters = agent._generate_characters(config, outline)

            # 保存到项目
            characters_path = Path(project_dir) / "characters.json"
            with open(characters_path, "w", encoding="utf-8") as f:
                json.dump(characters, f, ensure_ascii=False, indent=2)

            print(f"✅ 角色设定已生成: {len(characters)} 个角色")
            self.view_preprod.edit_chars.setPlainText(json.dumps(characters, ensure_ascii=False, indent=2))
            self.global_status_bar.update_status("生成完成", "success")

        except Exception as e:
            print(f"❌ 生成失败: {e}")
            self.global_status_bar.update_status("生成失败", "error")
            import traceback
            traceback.print_exc()

    def _on_request_evaluate(self):
        """处理评估请求"""
        self.global_status_bar.update_status("评估中...", "warning")
        # TODO: 实现实际评估逻辑
        self.global_status_bar.update_status("系统待命", "success")

    def _on_request_start(self):
        """处理开始写作请求"""
        self.global_status_bar.update_status("准备开始...", "info")

        # 1. 先保存前期筹备的数据
        project_dir = self.view_preprod.save_project()
        if project_dir:
            self.project_dir = project_dir

        # 1.5 重新加载项目配置（关键：save_project 创建了新目录，必须刷新 config）
        self.load_project_config()

        # 2. 更新生产视图的项目目录（确保加载最新数据）
        self.view_prod.set_project_dir(self.project_dir)

        # 3. 切换到生产视图
        self.main_stack.setCurrentIndex(1)

        # 4. 触发生产视图重新加载数据（确保大纲、人物等最新）
        self.view_prod.reload_data()

        # 5. 触发生产视图的开始
        self.view_prod.btn_start.click()

    # === AI 对话处理 ===
    def _handle_ai_chat(self, user_text: str):
        """启动 AgenticChatWorker 处理用户的 AI 对话"""
        if AgenticChatWorker is None:
            self.view_preprod.append_ai_reply(
                "<span style='color:red;'>AgenticChatWorker 不可用</span>"
            )
            return
        self.chat_worker = AgenticChatWorker(user_text, self.chat_history)
        self.chat_worker.chat_reply_signal.connect(self._on_chat_reply)
        self.chat_worker.ui_command_signal.connect(self.ui_driver.execute_commands)
        self.chat_worker.start()

    def _on_chat_reply(self, reply_text: str):
        """收到 AI 回复后，更新聊天界面和历史记录"""
        self.view_preprod.append_ai_reply(reply_text)
        # 追溯保存用户输入到历史
        user_text = self.chat_worker.user_text
        self.chat_history.append({"role": "user", "content": user_text})
        self.chat_history.append({"role": "assistant", "content": reply_text})

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
            "NovelForge v5.1 - AI小说生成系统\n\n"
            "✨ 基于Anthropic长运行代理最佳实践的全自动小说创作系统\n\n"
            "🎨 现代化UI设计 | 🚀 高效批处理 | 🛡️ 熔断机制"
        )

    def closeEvent(self, event):
        """关闭窗口时停止远程服务器"""
        if hasattr(self, 'remote_server'):
            self.remote_server.stop()
        super().closeEvent(event)

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

        # 启用暂停按钮，禁用开始按钮
        self.view_prod.btn_start.setEnabled(False)
        self.view_prod.btn_pause.setEnabled(True)
        self.view_prod.btn_resume.setEnabled(False)

    def on_pause_generation(self):
        """暂停生成"""
        if self.worker:
            self.worker.pause()
        self.view_prod.append_log("Generation paused", "warning")
        self.view_prod.btn_pause.setEnabled(False)
        self.view_prod.btn_resume.setEnabled(True)

    def on_resume_generation(self):
        """恢复生成"""
        if self.worker:
            self.worker.resume()
        self.view_prod.append_log("Generation resumed", "system")
        self.view_prod.btn_pause.setEnabled(True)
        self.view_prod.btn_resume.setEnabled(False)

    def connect_worker(self, worker):
        """连接worker信号"""
        self.worker = worker
        worker.log_signal.connect(self.view_prod.append_log)
        worker.text_stream_signal.connect(self.view_prod.append_text)
        worker.emotion_curve_signal.connect(self._on_emotion_curve)
        # 连接 Agent 状态信号
        worker.agent_status_signal.connect(self._on_agent_status)

    def _on_agent_status(self, data: dict):
        """Agent 状态更新"""
        name = data.get("name", "")
        status = data.get("status", "idle")
        task = data.get("task", "")
        self.view_prod.update_agent_status(name, status, task)

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

    print("[System] 正在点火，启动 NovelForge v5.1 创意工坊...")

    window = ProducerDashboard(project_dir)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
