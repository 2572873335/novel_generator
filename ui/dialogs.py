"""
对话框 - 进度恢复、章节反馈、设置、文档查看等
"""

import os
import json
from pathlib import Path
from typing import List

# PyQt6 导入
try:
    from PyQt6.QtWidgets import (
        QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
        QFrame, QDialog, QFormLayout, QTextEdit, QLineEdit,
        QComboBox, QSpinBox, QProgressBar, QGroupBox, QTextBrowser,
        QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QInputDialog
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available")

# 导入主题系统
try:
    from ui.themes import CyberpunkTheme, Typography, Spacing
except ImportError:
    from themes import CyberpunkTheme, Typography, Spacing

# 导入组件
try:
    from ui.components import AutoSaveIndicator, EvaluationCard
except ImportError:
    from components import AutoSaveIndicator, EvaluationCard


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
                with open(progress_file, 'r', encoding="utf-8") as f:
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
                        with open(config_file, 'r', encoding="utf-8") as f:
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

    # 题材类型和监控指标映射
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

        # ========== 三栏内容区域 ==========
        from PyQt6.QtWidgets import QSplitter
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

        # 保存项目按钮
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
        """获取项目配置"""
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

        # 使用书名作为项目目录名
        if config["title"] and config["title"] != "未命名项目":
            safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in config["title"])
            self.project_dir = f"novels/{safe_name}"

        project_path = Path(self.project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        # 保存项目配置
        config_path = project_path / "project_config.json"
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
        """显示评估结果"""
        self.current_evaluation = result

        self.eval_btn.setEnabled(True)
        self.eval_btn.setText("2. 评估设置")

        # 使用评估卡片组件
        self.eval_card.set_evaluation(result, score)

        # 启用操作按钮
        self.apply_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.re_eval_btn.setEnabled(True)

    def set_error(self, message: str):
        """显示错误"""
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

    # 可用模型
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
        try:
            from core.config_manager import check_api_key, get_api_key
            from core.model_manager import create_model_manager
            from core.config_manager import load_env_file

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

            env_config = load_env_file()
            model_id = env_config.get("DEFAULT_MODEL_ID", "deepseek-chat")
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
            result = llm.generate("Say 'OK' if you receive this message.", temperature=0)

            QMessageBox.information(
                self, "测试连接",
                f"✅ 连接成功！\n\n模型: {model_id}\nAPI Key: {key_name[:10]}...\n响应: {result[:50]}...",
                QMessageBox.StandardButton.Ok
            )

        except Exception as e:
            error_msg = str(e)
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
            from core.config_manager import save_api_key

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


class ToolGeneratorDialog(QDialog):
    """创作工具箱 - 单工具生成对话框"""
    applied_signal = pyqtSignal(str, str)  # tool_name, result_text

    def __init__(self, tool_name: str, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.worker = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle(f"🧰 {self.tool_name}")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CyberpunkTheme.BG_DARK}; }}
            QLabel {{ color: {CyberpunkTheme.TEXT_PRIMARY}; font-family: Consolas; font-weight: bold; }}
            QTextEdit, QTextBrowser {{ background-color: {CyberpunkTheme.BG_MEDIUM}; color: {CyberpunkTheme.TEXT_PRIMARY}; border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 6px; padding: 10px; font-family: 'Microsoft YaHei', Consolas; font-size: 14px; }}
            QTextEdit:focus {{ border-color: {CyberpunkTheme.FG_PRIMARY}; }}
            QPushButton {{ background-color: {CyberpunkTheme.BG_LIGHT}; color: {CyberpunkTheme.FG_PRIMARY}; border: 1px solid {CyberpunkTheme.FG_PRIMARY}; border-radius: 6px; padding: 10px; font-family: Consolas; font-weight: bold; }}
            QPushButton:hover {{ background-color: {CyberpunkTheme.FG_PRIMARY}; color: #000; }}
        """)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("🔑 输入灵感关键词 (如：赛博朋克, 修仙, 诡异):"))
        self.input_edit = QTextEdit()
        self.input_edit.setMaximumHeight(80)
        self.input_edit.setPlaceholderText("在此输入你的零碎想法...")
        layout.addWidget(self.input_edit)

        self.btn_generate = QPushButton("✨ 开始生成 (Generate)")
        self.btn_generate.clicked.connect(self._on_generate)
        layout.addWidget(self.btn_generate)

        layout.addWidget(QLabel("📝 生成结果:"))
        self.result_browser = QTextBrowser()
        layout.addWidget(self.result_browser)

        btn_layout = QHBoxLayout()
        self.btn_copy = QPushButton("📋 复制结果")
        self.btn_copy.clicked.connect(self._on_copy)
        btn_layout.addWidget(self.btn_copy)

        self.btn_append = QPushButton("📥 追加到大纲 (Append to Outline)")
        self.btn_append.setStyleSheet(f"background-color: {CyberpunkTheme.FG_SUCCESS}; color: #000; border-color: {CyberpunkTheme.FG_SUCCESS};")
        self.btn_append.clicked.connect(self._on_append)
        btn_layout.addWidget(self.btn_append)

        layout.addLayout(btn_layout)

    def _on_generate(self):
        keywords = self.input_edit.toPlainText().strip()
        if not keywords:
            return
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("🧠 思考中...")
        self.result_browser.setHtml(f"<span style='color:{CyberpunkTheme.FG_INFO};'>正在连接灵感网络...</span>")

        from ui.worker_thread import ToolWorker
        self.worker = ToolWorker(self.tool_name, keywords)
        self.worker.result_signal.connect(self._on_result)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_result(self, text: str):
        self.result_browser.setMarkdown(text)
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("✨ 重新生成 (Regenerate)")

    def _on_error(self, err: str):
        self.result_browser.setHtml(f"<span style='color:{CyberpunkTheme.FG_DANGER};'>{err}</span>")
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("✨ 开始生成 (Generate)")

    def _on_copy(self):
        QApplication.clipboard().setText(self.result_browser.toPlainText())
        self.btn_copy.setText("✅ 已复制!")
        QTimer.singleShot(2000, lambda: self.btn_copy.setText("📋 复制结果"))

    def _on_append(self):
        self.applied_signal.emit(self.tool_name, self.result_browser.toPlainText())
        self.accept()


class SkillEditorDialog(QDialog):
    """技能编辑器 - 内置只读/克隆，自定义可编辑/删除"""
    skill_changed = pyqtSignal()  # 通知外部刷新列表

    def __init__(self, skill_name: str, skill_path: str, is_custom: bool = False, parent=None):
        super().__init__(parent)
        self.skill_name = skill_name
        self.skill_path = Path(skill_path)
        self.is_custom = is_custom
        self._init_ui()
        self._load_content()

    def _init_ui(self):
        self.setWindowTitle(f"{'⚙️ 编辑' if self.is_custom else '👁️ 查看'} {self.skill_name}")
        self.setMinimumSize(700, 550)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CyberpunkTheme.BG_DARK}; }}
            QLabel {{ color: {CyberpunkTheme.TEXT_PRIMARY}; font-family: Consolas; }}
            QTextEdit {{ background-color: {CyberpunkTheme.BG_MEDIUM}; color: {CyberpunkTheme.TEXT_PRIMARY};
                border: 1px solid {CyberpunkTheme.BORDER_COLOR}; border-radius: 6px; padding: 10px;
                font-family: Consolas; font-size: 13px; }}
            QPushButton {{ background-color: {CyberpunkTheme.BG_LIGHT}; color: {CyberpunkTheme.FG_PRIMARY};
                border: 1px solid {CyberpunkTheme.FG_PRIMARY}; border-radius: 6px; padding: 8px 16px;
                font-family: Consolas; font-weight: bold; }}
            QPushButton:hover {{ background-color: {CyberpunkTheme.FG_PRIMARY}; color: #000; }}
        """)

        layout = QVBoxLayout(self)

        # 标题
        mode = "🟢 自定义技能 (可编辑)" if self.is_custom else "🔒 内置技能 (只读)"
        lbl = QLabel(f"{mode}  —  {self.skill_name}")
        lbl.setStyleSheet(f"font-weight: bold; font-size: 14px;")
        layout.addWidget(lbl)

        # 编辑器
        self.editor = QTextEdit()
        self.editor.setReadOnly(not self.is_custom)
        layout.addWidget(self.editor)

        # 按钮栏
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if self.is_custom:
            btn_del = QPushButton("🗑️ 删除 (Delete)")
            btn_del.setStyleSheet(f"background-color: {CyberpunkTheme.FG_DANGER}; color: #fff; border-color: {CyberpunkTheme.FG_DANGER};")
            btn_del.clicked.connect(self._on_delete)
            btn_row.addWidget(btn_del)

            btn_cancel = QPushButton("取消")
            btn_cancel.clicked.connect(self.reject)
            btn_row.addWidget(btn_cancel)

            btn_save = QPushButton("💾 保存修改 (Save)")
            btn_save.setStyleSheet(f"background-color: {CyberpunkTheme.FG_SUCCESS}; color: #000; border-color: {CyberpunkTheme.FG_SUCCESS};")
            btn_save.clicked.connect(self._on_save)
            btn_row.addWidget(btn_save)
        else:
            btn_cancel = QPushButton("取消")
            btn_cancel.clicked.connect(self.reject)
            btn_row.addWidget(btn_cancel)

            btn_clone = QPushButton("📋 克隆为自定义 (Clone)")
            btn_clone.setStyleSheet(f"background-color: {CyberpunkTheme.FG_GOLD}; color: #000; border-color: {CyberpunkTheme.FG_GOLD};")
            btn_clone.clicked.connect(self._on_clone)
            btn_row.addWidget(btn_clone)

        layout.addLayout(btn_row)

    def _load_content(self):
        """加载技能文件内容"""
        # 尝试多种常见文件名
        for fname in ("SKILL.md", "prompt.yaml", "prompt.md", "README.md"):
            f = self.skill_path / fname
            if f.exists():
                self.editor.setPlainText(f.read_text(encoding="utf-8"))
                self._content_file = f
                return
        # 如果没有找到，列出目录内容
        files = [p.name for p in self.skill_path.iterdir()] if self.skill_path.exists() else []
        self.editor.setPlainText(f"# 未找到标准技能文件\n# 目录内容: {files}")
        self._content_file = self.skill_path / "prompt.yaml"

    def _on_clone(self):
        name, ok = QInputDialog.getText(self, "克隆技能", "请输入自定义技能名称:")
        if not ok or not name.strip():
            return
        safe = name.strip().replace(" ", "-").lower()
        dest = Path("user_data/custom_skills") / safe
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "prompt.yaml").write_text(self.editor.toPlainText(), encoding="utf-8")
        self.skill_changed.emit()
        QMessageBox.information(self, "克隆成功", f"已克隆到 user_data/custom_skills/{safe}/")
        self.accept()

    def _on_save(self):
        self._content_file.parent.mkdir(parents=True, exist_ok=True)
        self._content_file.write_text(self.editor.toPlainText(), encoding="utf-8")
        self.skill_changed.emit()
        self.accept()

    def _on_delete(self):
        ret = QMessageBox.question(self, "确认删除", f"确定要删除自定义技能 [{self.skill_name}] 吗？")
        if ret != QMessageBox.StandardButton.Yes:
            return
        import shutil
        shutil.rmtree(self.skill_path, ignore_errors=True)
        self.skill_changed.emit()
        self.accept()
