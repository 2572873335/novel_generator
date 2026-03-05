"""
主题系统 - 赛博朋克配色、字体、间距和布局规范
"""

# PyQt6 导入
try:
    from PyQt6.QtWidgets import QWidget, QLabel, QComboBox
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not available")


# ============================================================================
# 赛博朋克配色方案 v2.0 - 优化对比度和视觉层次
# ============================================================================
class CyberpunkTheme:
    """Modern Professional SaaS Dark Theme - Slate Dark"""

    # === 背景层级 (Slate Dark) ===
    BG_DEEP = "#0B1120"         # 最深背景 (页面底层)
    BG_DARK = "#0F172A"         # 主背景 (Deep Slate)
    BG_MEDIUM = "#1E293B"       # 卡片背景 (Lighter Slate)
    BG_LIGHT = "#334155"        # 高亮背景 (Hover/Active)
    BG_HOVER = "#233145"        # 悬停背景
    BG_ACTIVE = "#3B4D66"       # 激活背景

    # === 主色调 ===
    FG_PRIMARY = "#38BDF8"       # 主色：Sky Blue
    FG_SECONDARY = "#818CF8"     # 辅色：Indigo
    FG_ACCENT = "#C084FC"        # 强调：Purple
    FG_GOLD = "#FBBF24"          # 高光：Amber

    # === 功能色 ===
    FG_SUCCESS = "#10B981"       # 成功：Emerald
    FG_WARNING = "#F59E0B"       # 警告：Amber
    FG_DANGER = "#EF4444"        # 错误：Rose Red
    FG_INFO = "#8B5CF6"          # 信息：Violet

    # === 文字颜色 ===
    TEXT_PRIMARY = "#F8FAFC"      # 主文字：Crisp White
    TEXT_SECONDARY = "#94A3B8"    # 次要：Muted Gray
    TEXT_TERTIARY = "#64748B"     # 第三级：Slate Gray
    TEXT_DIM = "#475569"          # 暗淡：Dark Slate

    # === 边框与分隔 ===
    BORDER_COLOR = "#334155"      # 标准边框
    BORDER_HOVER = "#38BDF8"      # 悬停边框
    BORDER_ACTIVE = "#818CF8"     # 激活边框
    BORDER_DANGER = "#EF4444"     # 错误边框
    BORDER_SUCCESS = "#10B981"    # 成功边框

    # === 渐变定义 ===
    GRADIENT_PRIMARY = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38BDF8, stop:1 #818CF8)"
    GRADIENT_ACCENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C084FC, stop:1 #818CF8)"
    GRADIENT_GOLD = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FBBF24, stop:1 #F59E0B)"
    GRADIENT_SUCCESS = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #34D399)"
    GRADIENT_DARK = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1E293B, stop:1 #0F172A)"
    GRADIENT_CARD = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #334155, stop:1 #1E293B)"

    # === 阴影效果 ===
    GLOW_PRIMARY = "0 0 12px rgba(56, 189, 248, 0.25)"
    GLOW_SECONDARY = "0 0 12px rgba(129, 140, 248, 0.25)"
    GLOW_SUCCESS = "0 0 10px rgba(16, 185, 129, 0.25)"
    GLOW_DANGER = "0 0 10px rgba(239, 68, 68, 0.25)"
    GLOW_GOLD = "0 0 15px rgba(251, 191, 36, 0.3)"
    GLOW_ACCENT = "0 0 15px rgba(192, 132, 252, 0.3)"
    SHADOW_CARD = "0 4px 16px rgba(0, 0, 0, 0.3)"
    SHADOW_ELEVATED = "0 8px 24px rgba(0, 0, 0, 0.4)"
    SHADOW_INSET = "inset 0 2px 4px rgba(0, 0, 0, 0.2)"
    SHADOW_BUTTON = "0 2px 8px rgba(0, 0, 0, 0.3), 0 0 1px rgba(56, 189, 248, 0.3)"

    # === 玻璃拟态 ===
    GLASS_BACKGROUND = "rgba(30, 41, 59, 0.7)"
    GLASS_BORDER = "rgba(148, 163, 184, 0.1)"
    GLASS_BLUR = "backdrop-filter: blur(10px);"

    # === 动画时长 (ms) ===
    ANIM_FAST = 150
    ANIM_NORMAL = 250
    ANIM_SLOW = 400


# ============================================================================
# 字体系统 - 专业设计字体组合
# ============================================================================
class Typography:
    """字体系统规范 - 现代化专业字体"""

    # 字体族 (带备用字体) - 升级为更具设计感的字体
    FONT_PRIMARY = "'Nunito Sans', 'Segoe UI', 'Microsoft YaHei', sans-serif"    # 主字体 - 圆润现代
    FONT_DISPLAY = "'Outfit', 'Segoe UI', 'Microsoft YaHei', sans-serif"    # 显示字体 - 几何现代
    FONT_MONO = "'JetBrains Mono', 'Consolas', 'Monaco', monospace"  # 等宽字体 - 编程风格
    FONT_BODY = "'Source Sans 3', 'Segoe UI', 'Microsoft YaHei', sans-serif"       # 正文字体 - 清晰易读

    # 字号规范 (px) - 优化层级
    SIZE_H1 = 22           # 页面标题
    SIZE_H2 = 18           # 面板标题
    SIZE_H3 = 15           # 卡片标题
    SIZE_BODY = 13         # 正文
    SIZE_SMALL = 11        # 辅助文字
    SIZE_TINY = 10          # 标签/时间戳

    # 字重
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_BOLD = 700
    WEIGHT_EXTRABOLD = 800


# ============================================================================
# 间距系统 (基于 4px 网格)
# ============================================================================
class Spacing:
    """间距规范 - 现代化间距系统"""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48

    # 组件间距
    PADDING_CARD = 16
    PADDING_CARD_LG = 24
    PADDING_INPUT = "10px 14px"
    PADDING_BUTTON = "10px 20px"
    PADDING_BUTTON_SM = "8px 16px"

    # 圆角 - 更现代的圆角设计
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 9999  # 完全圆角（药丸形状）

    # 间距倍数
    UNIT = 4


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
# 动画系统 - PyQt 动画样式
# ============================================================================
class Animations:
    """动画系统 - 用于创建流畅的UI过渡效果"""

    # 缓动曲线
    EASE_OUT = "easeOut"
    EASE_IN_OUT = "easeInOut"
    EASE_IN = "easeIn"
    LINEAR = "linear"

    # 预设动画样式
    @staticmethod
    def button_hover(theme=CyberpunkTheme) -> str:
        """按钮悬停动画"""
        return f"""
            QPushButton:hover {{
                background-color: {theme.BG_HOVER};
                border-color: {theme.FG_PRIMARY};
                transform: translateY(-1px);
                box-shadow: none;
            }}
        """

    @staticmethod
    def card_hover(theme=CyberpunkTheme) -> str:
        """卡片悬停效果"""
        return f"""
            QFrame:hover {{
                background-color: {theme.BG_HOVER};
                border-color: {theme.BORDER_HOVER};
            }}
        """

    @staticmethod
    def pulse_animation(color: str = CyberpunkTheme.FG_PRIMARY) -> str:
        """脉冲动画关键帧"""
        return f"""
            QFrame#pulse {{
                animation: pulse 2s infinite;
            }}
        """

    @staticmethod
    def fade_in(duration: int = 250) -> str:
        """淡入动画"""
        return f"""
            QPropertyAnimation#fade {{
                duration: {duration}ms;
                easingCurve: Type.InOut;
            }}
        """


# ============================================================================
# 主题管理器 - 支持多主题切换
# ============================================================================
class ThemeManager:
    """主题管理器 - 支持动态切换主题"""

    # 主题定义 - 包含渐变和特殊效果
    THEMES = {
        "cyberpunk": {
            "name": "Slate Dark",
            "description": "现代深色主题，专业而优雅",
            "colors": {
                "BG_DEEP": "#0B1120",
                "BG_DARK": "#0F172A",
                "BG_MEDIUM": "#1E293B",
                "BG_LIGHT": "#334155",
                "BG_HOVER": "#233145",
                "FG_PRIMARY": "#38BDF8",
                "FG_SECONDARY": "#818CF8",
                "FG_ACCENT": "#C084FC",
                "FG_GOLD": "#FBBF24",
                "FG_SUCCESS": "#10B981",
                "FG_WARNING": "#F59E0B",
                "FG_DANGER": "#EF4444",
                "FG_INFO": "#8B5CF6",
                "TEXT_PRIMARY": "#F8FAFC",
                "TEXT_SECONDARY": "#94A3B8",
                "TEXT_TERTIARY": "#64748B",
                "BORDER_COLOR": "#334155",
            },
            "gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F172A, stop:1 #0B1120)",
        },
        "neon_blue": {
            "name": "霓虹蓝",
            "description": "赛博朋克霓虹风格",
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
            },
            "gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f172a, stop:1 #030712)",
        },
        "sunset": {
            "name": "日落",
            "description": "温暖的日落色调",
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
            },
            "gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d1515, stop:1 #1a0a0a)",
        },
        "forest": {
            "name": "森林",
            "description": "自然清新的森林色调",
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
            },
            "gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #064e3b, stop:1 #052e16)",
        },
        # 现代浅色风格 - Modern Light
        "modern_light": {
            "name": "现代浅色",
            "description": "简洁现代 - 黑白配色",
            "colors": {
                "BG_DEEP": "#FFFFFF",
                "BG_DARK": "#FAFAFA",
                "BG_MEDIUM": "#F9FAFB",
                "BG_LIGHT": "#F3F4F6",
                "BG_HOVER": "#E5E7EB",
                "FG_PRIMARY": "#1F2937",
                "FG_SECONDARY": "#4B5563",
                "FG_ACCENT": "#6B7280",
                "FG_GOLD": "#F59E0B",
                "FG_SUCCESS": "#10B981",
                "FG_WARNING": "#F59E0B",
                "FG_DANGER": "#EF4444",
                "FG_INFO": "#3B82F6",
                "TEXT_PRIMARY": "#1F2937",
                "TEXT_SECONDARY": "#6B7280",
                "TEXT_TERTIARY": "#9CA3AF",
                "BORDER_COLOR": "#E5E7EB",
            },
            "gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F9FAFB)",
        },
        # 明日方舟风格 - Arknights
        "arknights": {
            "name": "明日方舟",
            "description": "罗德岛风格 - 暖棕深色调",
            "colors": {
                "BG_DEEP": "#1A1714",
                "BG_DARK": "#231F1C",
                "BG_MEDIUM": "#2D2824",
                "BG_LIGHT": "#3A3530",
                "BG_HOVER": "#4A4540",
                "FG_PRIMARY": "#E86E3D",       # 罗德岛红橙色
                "FG_SECONDARY": "#D4A857",      # 暗金色
                "FG_ACCENT": "#8B4513",         # 棕色点缀
                "FG_GOLD": "#C9A227",           # 金色高光
                "FG_SUCCESS": "#6B8E23",        # 橄榄绿
                "FG_WARNING": "#D4A857",        # 金色警告
                "FG_DANGER": "#B22222",         # 深红
                "FG_INFO": "#708090",           # 灰蓝色
                "TEXT_PRIMARY": "#E8E0D5",      # 暖白
                "TEXT_SECONDARY": "#A09080",   # 暖灰
                "TEXT_TERTIARY": "#706050",    # 深暖灰
                "BORDER_COLOR": "#3A3530",
            },
            "gradient": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #231F1C, stop:1 #1A1714)",
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
if PYQT_AVAILABLE:
    class ThemeSelector(QWidget):
        """主题选择器组件"""

        theme_changed = pyqtSignal(str)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.init_ui()

        def init_ui(self):
            """初始化UI"""
            self.setFixedHeight(36)
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {CyberpunkTheme.GLASS_BACKGROUND};
                    border: 1px solid {CyberpunkTheme.GLASS_BORDER};
                    border-radius: {Spacing.RADIUS_MD}px;
                }}
                QLabel {{
                    background: transparent;
                    color: {CyberpunkTheme.TEXT_SECONDARY};
                    font-family: {Typography.FONT_PRIMARY};
                    font-size: {Typography.SIZE_SMALL}px;
                }}
                QComboBox {{
                    background-color: {CyberpunkTheme.BG_LIGHT};
                    color: {CyberpunkTheme.TEXT_PRIMARY};
                    border: 1px solid {CyberpunkTheme.BORDER_COLOR};
                    border-radius: {Spacing.RADIUS_MD}px;
                    padding: 6px 12px;
                    font-family: {Typography.FONT_PRIMARY};
                    font-size: {Typography.SIZE_SMALL}px;
                }}
                QComboBox:hover {{
                    border-color: {CyberpunkTheme.FG_PRIMARY};
                    background-color: {CyberpunkTheme.BG_HOVER};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 24px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid {CyberpunkTheme.TEXT_SECONDARY};
                    margin-right: 8px;
                }}
            """)

            layout = QLabel(self)
            from PyQt6.QtWidgets import QHBoxLayout
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
# 样式生成器 - 用于创建现代化的 UI 组件样式
# ============================================================================
class StyleSheet:
    """样式生成器 - 快速生成现代化组件样式"""

    @staticmethod
    def button_primary(theme=CyberpunkTheme, hover=True) -> str:
        """主按钮样式 - 带渐变和发光效果"""
        base = f"""
            QPushButton {{
                background-color: {theme.BG_LIGHT};
                color: {theme.FG_PRIMARY};
                border: 1px solid {theme.FG_PRIMARY};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: {Spacing.PADDING_BUTTON};
                font-family: {Typography.FONT_PRIMARY};
                font-weight: {Typography.WEIGHT_MEDIUM};
                font-size: {Typography.SIZE_BODY}px;
                min-width: 80px;
            }}
        """
        if hover:
            base += f"""
            QPushButton:hover {{
                background-color: {theme.FG_PRIMARY};
                color: {theme.BG_DARK};
                border-color: {theme.FG_PRIMARY};
                box-shadow: none;
            }}
            QPushButton:pressed {{
                background-color: {theme.FG_SECONDARY};
                transform: translateY(1px);
            }}
        """
        return base

    @staticmethod
    def button_success(theme=CyberpunkTheme) -> str:
        """成功按钮样式"""
        return f"""
            QPushButton {{
                background-color: {theme.FG_SUCCESS};
                color: {theme.BG_DARK};
                border: 2px solid {theme.FG_SUCCESS};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: {Spacing.PADDING_BUTTON};
                font-family: {Typography.FONT_PRIMARY};
                font-weight: {Typography.WEIGHT_BOLD};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_LIGHT};
                color: {theme.FG_SUCCESS};
                box-shadow: none;
            }}
        """

    @staticmethod
    def button_danger(theme=CyberpunkTheme) -> str:
        """危险按钮样式"""
        return f"""
            QPushButton {{
                background-color: {theme.FG_DANGER};
                color: {theme.TEXT_PRIMARY};
                border: 2px solid {theme.FG_DANGER};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: {Spacing.PADDING_BUTTON};
                font-family: {Typography.FONT_PRIMARY};
                font-weight: {Typography.WEIGHT_BOLD};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QPushButton:hover {{
                box-shadow: none;
            }}
        """

    @staticmethod
    def card(theme=CyberpunkTheme, border_color=None) -> str:
        """卡片样式 - 现代化玻璃拟态"""
        bc = border_color or theme.BORDER_COLOR
        return f"""
            QFrame {{
                background-color: {theme.BG_MEDIUM};
                border: 1px solid {bc};
                border-radius: {Spacing.RADIUS_LG}px;
                padding: {Spacing.PADDING_CARD}px;
            }}
            QFrame:hover {{
                background-color: {theme.BG_LIGHT};
                border-color: {theme.BORDER_HOVER};
            }}
        """

    @staticmethod
    def input_field(theme=CyberpunkTheme) -> str:
        """输入框样式"""
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {theme.BG_DARK};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 10px 14px;
                font-family: {Typography.FONT_BODY};
                font-size: {Typography.SIZE_BODY}px;
                selection-background-color: {theme.FG_PRIMARY};
                selection-color: {theme.BG_DARK};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {theme.FG_PRIMARY};
                box-shadow: none;
            }}
            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: {theme.TEXT_TERTIARY};
            }}
        """

    @staticmethod
    def panel(theme=CyberpunkTheme) -> str:
        """面板样式"""
        return f"""
            QGroupBox {{
                background-color: {theme.BG_MEDIUM};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_LG}px;
                margin-top: 16px;
                padding-top: 16px;
                font-family: {Typography.FONT_DISPLAY};
                font-weight: {Typography.WEIGHT_BOLD};
                color: {theme.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 4px 8px;
                color: {theme.FG_PRIMARY};
            }}
        """

    @staticmethod
    def progress_bar(theme=CyberpunkTheme) -> str:
        """进度条样式"""
        return f"""
            QProgressBar {{
                background-color: {theme.BG_DARK};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_SM}px;
                text-align: center;
                color: {theme.TEXT_PRIMARY};
                font-family: {Typography.FONT_MONO};
                font-size: {Typography.SIZE_SMALL}px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {theme.FG_PRIMARY};
                border-radius: {Spacing.RADIUS_SM}px;
            }}
        """

    @staticmethod
    def scrollbar(theme=CyberpunkTheme) -> str:
        """滚动条样式"""
        return f"""
            QScrollBar:vertical {{
                background-color: {theme.BG_DARK};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme.BG_LIGHT};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme.FG_PRIMARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {theme.BG_DARK};
                height: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {theme.BG_LIGHT};
                border-radius: 5px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme.FG_PRIMARY};
            }}
        """

    @staticmethod
    def tab_widget(theme=CyberpunkTheme) -> str:
        """标签页样式"""
        return f"""
            QTabWidget::pane {{
                background-color: {theme.BG_MEDIUM};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
            QTabBar::tab {{
                background-color: {theme.BG_DARK};
                color: {theme.TEXT_SECONDARY};
                padding: 10px 20px;
                border: 1px solid {theme.BORDER_COLOR};
                border-bottom: none;
                border-top-left-radius: {Spacing.RADIUS_MD}px;
                border-top-right-radius: {Spacing.RADIUS_MD}px;
                font-family: {Typography.FONT_PRIMARY};
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
            QTabBar::tab:selected {{
                background-color: {theme.BG_MEDIUM};
                color: {theme.FG_PRIMARY};
                border-color: {theme.BORDER_COLOR};
            }}
            QTabBar::tab:hover:selected {{
                background-color: {theme.BG_LIGHT};
            }}
        """

    @staticmethod
    def list_widget(theme=CyberpunkTheme) -> str:
        """列表组件样式"""
        return f"""
            QListWidget {{
                background-color: {theme.BG_DARK};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_COLOR};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 4px;
                font-family: {Typography.FONT_BODY};
                font-size: {Typography.SIZE_BODY}px;
            }}
            QListWidget::item {{
                background-color: transparent;
                padding: 8px 12px;
                border-radius: {Spacing.RADIUS_SM}px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {theme.FG_PRIMARY};
                color: {theme.BG_DARK};
            }}
            QListWidget::item:hover {{
                background-color: {theme.BG_LIGHT};
            }}
        """


# ============================================================================
# 主题样式配置 - 不同主题的独特UI布局风格
# ============================================================================
class ThemeStyles:
    """主题样式配置 - 为每个主题定义独特的UI风格"""

    @staticmethod
    def get_theme_styles(theme_key: str) -> dict:
        """获取主题的完整样式配置"""
        styles = {
            "cyberpunk": ThemeStyles._cyberpunk_styles(),
            "arknights": ThemeStyles._arknights_styles(),
            "sunset": ThemeStyles._sunset_styles(),
            "forest": ThemeStyles._forest_styles(),
            "modern_light": ThemeStyles._modern_light_styles(),
        }
        return styles.get(theme_key, styles["cyberpunk"])

    @staticmethod
    def _cyberpunk_styles() -> dict:
        """Slate Dark 风格 - 现代SaaS深色"""
        return {
            "name": "Slate Dark",
            "font_family": "'Nunito Sans', 'Segoe UI', sans-serif",
            "font_display": "'Outfit', 'Segoe UI', sans-serif",
            "font_mono": "'JetBrains Mono', 'Consolas', monospace",

            # 主窗口
            "main_window": """
                QMainWindow { background-color: #0B1120; }
            """,

            # 菜单栏
            "menubar": f"""
                QMenuBar {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                    border-bottom: 1px solid #334155;
                    padding: 4px;
                }}
                QMenuBar::item {{
                    background: transparent;
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                QMenuBar::item:selected {{ background-color: #233145; }}
                QMenu {{
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 4px;
                }}
                QMenu::item {{
                    color: #FFFFFF;
                    padding: 8px 24px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{ background-color: #334155; }}
            """,

            # 状态栏
            "statusbar": f"""
                QFrame {{
                    background-color: #0F172A;
                    border-bottom: 1px solid #334155;
                }}
            """,

            # 导航栏
            "navbar": f"""
                QFrame {{
                    background-color: #0B1120;
                    border-bottom: 1px solid #334155;
                }}
                QPushButton {{
                    background-color: transparent;
                    color: #94A3B8;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                }}
            """,

            # 导航按钮 - 选中状态
            "navbar_active": f"""
                QPushButton {{
                    background-color: #38BDF8;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 700;
                }}
            """,

            # 按钮样式
            "button": f"""
                QPushButton {{
                    background-color: #334155;
                    color: #38BDF8;
                    border: 1px solid #38BDF8;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #38BDF8;
                    color: #0B1120;
                    box-shadow: none;
                }}
            """,

            # 按钮 - 主要
            "button_primary": f"""
                QPushButton {{
                    background-color: #38BDF8;
                    color: #0B1120;
                    border: 2px solid #38BDF8;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: #0B1120;
                    color: #38BDF8;
                    box-shadow: none;
                }}
            """,

            # 按钮 - 成功
            "button_success": f"""
                QPushButton {{
                    background-color: #10B981;
                    color: #0B1120;
                    border: 2px solid #10B981;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    box-shadow: none;
                }}
            """,

            # 输入框
            "input": f"""
                QLineEdit, QTextEdit {{
                    background-color: #0F172A;
                    color: #F8FAFC;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
                    font-size: 13px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: #38BDF8;
                    box-shadow: none;
                }}
            """,

            # 卡片
            "card": f"""
                QFrame {{
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 12px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    background-color: #334155;
                    border-color: #38BDF8;
                }}
            """,

            # 面板
            "panel": f"""
                QGroupBox {{
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 12px;
                    margin-top: 16px;
                    padding-top: 16px;
                    font-family: 'Outfit', 'Segoe UI', sans-serif;
                    font-weight: 700;
                    color: #F8FAFC;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 12px;
                    padding: 4px 8px;
                    color: #38BDF8;
                }}
            """,

            # 进度条
            "progress": f"""
                QProgressBar {{
                    background-color: #0F172A;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    text-align: center;
                    color: #F8FAFC;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 11px;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: #38BDF8;
                    border-radius: 4px;
                }}
            """,

            # 标签页
            "tabs": f"""
                QTabWidget::pane {{
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 8px;
                }}
                QTabBar::tab {{
                    background-color: #0F172A;
                    color: #94A3B8;
                    padding: 10px 20px;
                    border: 1px solid #334155;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QTabBar::tab:selected {{
                    background-color: #1E293B;
                    color: #38BDF8;
                }}
            """,

            # 下拉框
            "combobox": f"""
                QComboBox {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-family: 'Nunito Sans', 'Segoe UI', sans-serif;
                    font-size: 12px;
                }}
                QComboBox:hover {{
                    border-color: #38BDF8;
                    background-color: #334155;
                }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                    selection-background-color: #334155;
                    border: 1px solid #334155;
                }}
            """,

            # 滚动条
            "scrollbar": f"""
                QScrollBar:vertical {{
                    background-color: #0F172A;
                    width: 10px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #334155;
                    border-radius: 5px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{ background-color: #38BDF8; }}
            """,

            # 标签文字颜色
            "label": "color: #94A3B8;",
            "label_primary": "color: #F8FAFC;",
            "label_accent": "color: #38BDF8;",
            "label_success": "color: #10B981;",
            "label_warning": "color: #F59E0B;",
            "label_danger": "color: #EF4444;",

            # Logo 样式
            "logo": f"""
                font-family: 'Outfit', 'Segoe UI', sans-serif;
                font-size: 18px;
                font-weight: 700;
                color: #38BDF8;
            """,
        }

    @staticmethod
    def _arknights_styles() -> dict:
        """明日方舟风格 - 硬朗线条、暖棕色调"""
        return {
            "name": "明日方舟",
            "font_family": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
            "font_display": "'Noto Sans SC', 'Microsoft YaHei', sans-serif",
            "font_mono": "'Consolas', 'Source Code Pro', monospace",

            # 主窗口
            "main_window": """
                QMainWindow { background-color: #1A1714; }
            """,

            # 菜单栏
            "menubar": f"""
                QMenuBar {{
                    background-color: #2D2824;
                    color: #E8E0D5;
                    border-bottom: 2px solid #3A3530;
                    padding: 6px;
                }}
                QMenuBar::item {{
                    background: transparent;
                    padding: 8px 16px;
                    border-radius: 2px;
                    border: 1px solid transparent;
                }}
                QMenuBar::item:selected {{
                    background-color: #3A3530;
                    border-color: #E86E3D;
                }}
                QMenu {{
                    background-color: #2D2824;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    padding: 0px;
                }}
                QMenu::item {{
                    color: #E8E0D5;
                    padding: 10px 30px;
                    border-left: 3px solid transparent;
                }}
                QMenu::item:selected {{
                    background-color: #3A3530;
                    border-left-color: #E86E3D;
                }}
            """,

            # 状态栏
            "statusbar": f"""
                QFrame {{
                    background-color: #231F1C;
                    border-bottom: 2px solid #3A3530;
                }}
            """,

            # 导航栏
            "navbar": f"""
                QFrame {{
                    background-color: #1A1714;
                    border-bottom: 2px solid #3A3530;
                }}
                QPushButton {{
                    background-color: transparent;
                    color: #A09080;
                    border: none;
                    border-left: 3px solid transparent;
                    padding: 14px 28px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background-color: #2D2824;
                    color: #E8E0D5;
                }}
            """,

            # 导航按钮 - 选中状态
            "navbar_active": f"""
                QPushButton {{
                    background-color: #2D2824;
                    color: #E86E3D;
                    border: none;
                    border-left: 3px solid #E86E3D;
                    padding: 14px 28px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-size: 14px;
                    font-weight: 700;
                    letter-spacing: 1px;
                }}
            """,

            # 按钮样式
            "button": f"""
                QPushButton {{
                    background-color: #2D2824;
                    color: #D4A857;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    padding: 12px 24px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #3A3530;
                    border-color: #D4A857;
                    color: #E8E0D5;
                }}
            """,

            # 按钮 - 主要
            "button_primary": f"""
                QPushButton {{
                    background-color: #E86E3D;
                    color: #1A1714;
                    border: 2px solid #E86E3D;
                    border-radius: 0px;
                    padding: 12px 24px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-weight: 700;
                    letter-spacing: 2px;
                }}
                QPushButton:hover {{
                    background-color: #D4A857;
                    border-color: #D4A857;
                }}
            """,

            # 按钮 - 成功
            "button_success": f"""
                QPushButton {{
                    background-color: #6B8E23;
                    color: #E8E0D5;
                    border: 2px solid #6B8E23;
                    border-radius: 0px;
                    padding: 12px 24px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-weight: 700;
                }}
            """,

            # 输入框
            "input": f"""
                QLineEdit, QTextEdit {{
                    background-color: #1A1714;
                    color: #E8E0D5;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    padding: 12px 16px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-size: 13px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: #E86E3D;
                }}
            """,

            # 卡片
            "card": f"""
                QFrame {{
                    background-color: #2D2824;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    background-color: #3A3530;
                    border-color: #D4A857;
                }}
            """,

            # 面板
            "panel": f"""
                QGroupBox {{
                    background-color: #2D2824;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    margin-top: 20px;
                    padding-top: 20px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-weight: 700;
                    color: #E8E0D5;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 16px;
                    padding: 4px 12px;
                    background-color: #3A3530;
                    color: #D4A857;
                    border-left: 3px solid #E86E3D;
                }}
            """,

            # 进度条
            "progress": f"""
                QProgressBar {{
                    background-color: #1A1714;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    text-align: center;
                    color: #E8E0D5;
                    font-family: 'Consolas', monospace;
                    font-size: 12px;
                    height: 24px;
                }}
                QProgressBar::chunk {{
                    background-color: #E86E3D;
                    border-right: 1px solid #D4A857;
                }}
            """,

            # 标签页
            "tabs": f"""
                QTabWidget::pane {{
                    background-color: #2D2824;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                }}
                QTabBar::tab {{
                    background-color: #1A1714;
                    color: #A09080;
                    padding: 12px 24px;
                    border: 2px solid #3A3530;
                    border-bottom: none;
                    border-top-left-radius: 0px;
                    border-top-right-radius: 0px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-weight: 600;
                }}
                QTabBar::tab:selected {{
                    background-color: #2D2824;
                    color: #E86E3D;
                    border-bottom: 2px solid #E86E3D;
                }}
            """,

            # 下拉框
            "combobox": f"""
                QComboBox {{
                    background-color: #2D2824;
                    color: #E8E0D5;
                    border: 2px solid #3A3530;
                    border-radius: 0px;
                    padding: 8px 16px;
                    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                    font-size: 12px;
                }}
                QComboBox:hover {{
                    border-color: #E86E3D;
                    background-color: #3A3530;
                }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: #2D2824;
                    color: #E8E0D5;
                    selection-background-color: #3A3530;
                    border: 2px solid #3A3530;
                }}
            """,

            # 滚动条
            "scrollbar": f"""
                QScrollBar:vertical {{
                    background-color: #1A1714;
                    width: 12px;
                    border-radius: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #3A3530;
                    border-radius: 0px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{ background-color: #E86E3D; }}
            """,

            # 标签文字颜色
            "label": "color: #A09080;",
            "label_primary": "color: #E8E0D5;",
            "label_accent": "color: #E86E3D;",
            "label_success": "color: #6B8E23;",
            "label_warning": "color: #D4A857;",
            "label_danger": "color: #B22222;",

            # Logo 样式
            "logo": f"""
                font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                font-size: 20px;
                font-weight: 700;
                color: #E86E3D;
                letter-spacing: 3px;
            """,
        }

    @staticmethod
    def _sunset_styles() -> dict:
        """日落风格 - 暖色调渐变"""
        return {
            "name": "日落",
            "font_family": "'Comfortaa', 'Segoe UI', sans-serif",
            "font_display": "'Comfortaa', 'Segoe UI', sans-serif",
            "font_mono": "'Fira Code', 'Consolas', monospace",

            # 主窗口
            "main_window": """
                QMainWindow { background-color: #1a0a0a; }
            """,

            # 菜单栏
            "menubar": f"""
                QMenuBar {{
                    background-color: #3d2020;
                    color: #fef3c7;
                    border-bottom: 1px solid #4d2a2a;
                    padding: 4px;
                }}
                QMenuBar::item {{
                    background: transparent;
                    padding: 6px 12px;
                    border-radius: 6px;
                }}
                QMenuBar::item:selected {{ background-color: #5d3535; }}
                QMenu {{
                    background-color: #3d2020;
                    border: 1px solid #4d2a2a;
                    border-radius: 8px;
                    padding: 4px;
                }}
                QMenu::item {{
                    color: #FFFFFF;
                    padding: 8px 24px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{ background-color: #4d2a2a; }}
            """,

            # 状态栏
            "statusbar": f"""
                QFrame {{
                    background-color: #2d1515;
                    border-bottom: 1px solid #4d2a2a;
                }}
            """,

            # 导航栏
            "navbar": f"""
                QFrame {{
                    background-color: #1a0a0a;
                    border-bottom: 1px solid #4d2a2a;
                }}
                QPushButton {{
                    background-color: transparent;
                    color: #d97706;
                    border: none;
                    border-radius: 20px;
                    padding: 12px 24px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #3d2020;
                    color: #fbbf24;
                }}
            """,

            # 导航按钮 - 选中状态
            "navbar_active": f"""
                QPushButton {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fb923c, stop:1 #f472b6);
                    color: #1a0a0a;
                    border: none;
                    border-radius: 20px;
                    padding: 12px 24px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 700;
                }}
            """,

            # 按钮样式
            "button": f"""
                QPushButton {{
                    background-color: #4d2a2a;
                    color: #fb923c;
                    border: 1px solid #fb923c;
                    border-radius: 20px;
                    padding: 10px 20px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #fb923c;
                    color: #1a0a0a;
                }}
            """,

            # 按钮 - 主要
            "button_primary": f"""
                QPushButton {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fb923c, stop:1 #f472b6);
                    color: #1a0a0a;
                    border: none;
                    border-radius: 20px;
                    padding: 10px 20px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    box-shadow: none;
                }}
            """,

            # 按钮 - 成功
            "button_success": f"""
                QPushButton {{
                    background-color: #4ade80;
                    color: #1a0a0a;
                    border: none;
                    border-radius: 20px;
                    padding: 10px 20px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-weight: 700;
                }}
            """,

            # 输入框
            "input": f"""
                QLineEdit, QTextEdit {{
                    background-color: #2d1515;
                    color: #fef3c7;
                    border: 1px solid #4d2a2a;
                    border-radius: 12px;
                    padding: 10px 14px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-size: 13px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: #fb923c;
                }}
            """,

            # 卡片
            "card": f"""
                QFrame {{
                    background-color: #3d2020;
                    border: 1px solid #4d2a2a;
                    border-radius: 16px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    background-color: #4d2a2a;
                    border-color: #fb923c;
                }}
            """,

            # 面板
            "panel": f"""
                QGroupBox {{
                    background-color: #3d2020;
                    border: 1px solid #4d2a2a;
                    border-radius: 16px;
                    margin-top: 16px;
                    padding-top: 16px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-weight: 700;
                    color: #fef3c7;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 12px;
                    padding: 4px 8px;
                    color: #fb923c;
                }}
            """,

            # 进度条
            "progress": f"""
                QProgressBar {{
                    background-color: #2d1515;
                    border: 1px solid #4d2a2a;
                    border-radius: 10px;
                    text-align: center;
                    color: #fef3c7;
                    font-family: 'Fira Code', 'Consolas', monospace;
                    font-size: 11px;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fb923c, stop:1 #f472b6);
                    border-radius: 10px;
                }}
            """,

            # 标签页
            "tabs": f"""
                QTabWidget::pane {{
                    background-color: #3d2020;
                    border: 1px solid #4d2a2a;
                    border-radius: 12px;
                }}
                QTabBar::tab {{
                    background-color: #2d1515;
                    color: #d97706;
                    padding: 10px 20px;
                    border: 1px solid #4d2a2a;
                    border-bottom: none;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QTabBar::tab:selected {{
                    background-color: #3d2020;
                    color: #fb923c;
                }}
            """,

            # 下拉框
            "combobox": f"""
                QComboBox {{
                    background-color: #3d2020;
                    color: #fef3c7;
                    border: 1px solid #4d2a2a;
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                    font-size: 12px;
                }}
                QComboBox:hover {{
                    border-color: #fb923c;
                    background-color: #4d2a2a;
                }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: #3d2020;
                    color: #fef3c7;
                    selection-background-color: #4d2a2a;
                    border: 1px solid #4d2a2a;
                }}
            """,

            # 滚动条
            "scrollbar": f"""
                QScrollBar:vertical {{
                    background-color: #2d1515;
                    width: 10px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #4d2a2a;
                    border-radius: 5px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{ background-color: #fb923c; }}
            """,

            # 标签文字颜色
            "label": "color: #d97706;",
            "label_primary": "color: #fef3c7;",
            "label_accent": "color: #fb923c;",
            "label_success": "color: #4ade80;",
            "label_warning": "color: #fbbf24;",
            "label_danger": "color: #f87171;",

            # Logo 样式
            "logo": f"""
                font-family: 'Comfortaa', 'Segoe UI', sans-serif;
                font-size: 18px;
                font-weight: 700;
                color: #fb923c;
            """,
        }

    @staticmethod
    def _forest_styles() -> dict:
        """森林风格 - 自然清新"""
        return {
            "name": "森林",
            "font_family": "'Nunito', 'Segoe UI', sans-serif",
            "font_display": "'Nunito', 'Segoe UI', sans-serif",
            "font_mono": "'JetBrains Mono', 'Consolas', monospace",

            # 主窗口
            "main_window": """
                QMainWindow { background-color: #052e16; }
            """,

            # 菜单栏
            "menubar": f"""
                QMenuBar {{
                    background-color: #065f46;
                    color: #ecfdf5;
                    border-bottom: 1px solid #047857;
                    padding: 4px;
                }}
                QMenuBar::item {{
                    background: transparent;
                    padding: 6px 12px;
                    border-radius: 8px;
                }}
                QMenuBar::item:selected {{ background-color: #059669; }}
                QMenu {{
                    background-color: #065f46;
                    border: 1px solid #047857;
                    border-radius: 12px;
                    padding: 4px;
                }}
                QMenu::item {{
                    color: #FFFFFF;
                    padding: 8px 24px;
                    border-radius: 8px;
                }}
                QMenu::item:selected {{ background-color: #047857; }}
            """,

            # 状态栏
            "statusbar": f"""
                QFrame {{
                    background-color: #064e3b;
                    border-bottom: 1px solid #047857;
                }}
            """,

            # 导航栏
            "navbar": f"""
                QFrame {{
                    background-color: #052e16;
                    border-bottom: 1px solid #047857;
                }}
                QPushButton {{
                    background-color: transparent;
                    color: #6ee7b7;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #065f46;
                    color: #ecfdf5;
                }}
            """,

            # 导航按钮 - 选中状态
            "navbar_active": f"""
                QPushButton {{
                    background-color: #10b981;
                    color: #ecfdf5;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 700;
                }}
            """,

            # 按钮样式
            "button": f"""
                QPushButton {{
                    background-color: #047857;
                    color: #34d399;
                    border: 2px solid #10b981;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #10b981;
                    color: #052e16;
                }}
            """,

            # 按钮 - 主要
            "button_primary": f"""
                QPushButton {{
                    background-color: #10b981;
                    color: #052e16;
                    border: 2px solid #34d399;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: #34d399;
                    box-shadow: none;
                }}
            """,

            # 按钮 - 成功
            "button_success": f"""
                QPushButton {{
                    background-color: #34d399;
                    color: #052e16;
                    border: 2px solid #34d399;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-weight: 700;
                }}
            """,

            # 输入框
            "input": f"""
                QLineEdit, QTextEdit {{
                    background-color: #064e3b;
                    color: #ecfdf5;
                    border: 2px solid #047857;
                    border-radius: 12px;
                    padding: 10px 14px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-size: 13px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: #10b981;
                    box-shadow: none;
                }}
            """,

            # 卡片
            "card": f"""
                QFrame {{
                    background-color: #065f46;
                    border: 1px solid #047857;
                    border-radius: 16px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    background-color: #047857;
                    border-color: #10b981;
                }}
            """,

            # 面板
            "panel": f"""
                QGroupBox {{
                    background-color: #065f46;
                    border: 1px solid #047857;
                    border-radius: 16px;
                    margin-top: 16px;
                    padding-top: 16px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-weight: 700;
                    color: #ecfdf5;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 12px;
                    padding: 4px 8px;
                    color: #34d399;
                }}
            """,

            # 进度条
            "progress": f"""
                QProgressBar {{
                    background-color: #064e3b;
                    border: 1px solid #047857;
                    border-radius: 10px;
                    text-align: center;
                    color: #ecfdf5;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 11px;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: #10b981;
                    border-radius: 10px;
                }}
            """,

            # 标签页
            "tabs": f"""
                QTabWidget::pane {{
                    background-color: #065f46;
                    border: 1px solid #047857;
                    border-radius: 16px;
                }}
                QTabBar::tab {{
                    background-color: #064e3b;
                    color: #6ee7b7;
                    padding: 10px 20px;
                    border: 1px solid #047857;
                    border-bottom: none;
                    border-top-left-radius: 16px;
                    border-top-right-radius: 16px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QTabBar::tab:selected {{
                    background-color: #065f46;
                    color: #10b981;
                }}
            """,

            # 下拉框
            "combobox": f"""
                QComboBox {{
                    background-color: #065f46;
                    color: #ecfdf5;
                    border: 1px solid #047857;
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-family: 'Nunito', 'Segoe UI', sans-serif;
                    font-size: 12px;
                }}
                QComboBox:hover {{
                    border-color: #10b981;
                    background-color: #047857;
                }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: #065f46;
                    color: #ecfdf5;
                    selection-background-color: #047857;
                    border: 1px solid #047857;
                }}
            """,

            # 滚动条
            "scrollbar": f"""
                QScrollBar:vertical {{
                    background-color: #064e3b;
                    width: 10px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #047857;
                    border-radius: 5px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{ background-color: #10b981; }}
            """,

            # 标签文字颜色
            "label": "color: #6ee7b7;",
            "label_primary": "color: #ecfdf5;",
            "label_accent": "color: #34d399;",
            "label_success": "color: #10b981;",
            "label_warning": "color: #fcd34d;",
            "label_danger": "color: #f87171;",

            # Logo 样式
            "logo": f"""
                font-family: 'Nunito', 'Segoe UI', sans-serif;
                font-size: 18px;
                font-weight: 700;
                color: #34d399;
            """,
        }

    @staticmethod
    def _modern_light_styles() -> dict:
        """现代浅色风格 - 黑白简洁设计"""
        return {
            "name": "现代浅色",
            "font_family": "'Inter', 'Segoe UI', sans-serif",
            "font_display": "'Inter', 'Segoe UI', sans-serif",
            "font_mono": "'JetBrains Mono', 'Consolas', monospace",

            # 主窗口
            "main_window": """
                QMainWindow { background-color: #FFFFFF; }
            """,

            # 菜单栏
            "menubar": f"""
                QMenuBar {{
                    background-color: #FAFAFA;
                    color: #1F2937;
                    border-bottom: 1px solid #E5E7EB;
                    padding: 4px;
                }}
                QMenuBar::item {{
                    background: transparent;
                    padding: 6px 12px;
                    border-radius: 4px;
                }}
                QMenuBar::item:selected {{ background-color: #F3F4F6; }}
                QMenu {{
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    padding: 4px;
                    box-shadow: none;
                }}
                QMenu::item {{
                    color: #1F2937;
                    padding: 8px 24px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{ background-color: #F3F4F6; }}
            """,

            # 状态栏
            "statusbar": f"""
                QFrame {{
                    background-color: #FAFAFA;
                    border-bottom: 1px solid #E5E7EB;
                }}
            """,

            # 导航栏
            "navbar": f"""
                QFrame {{
                    background-color: #FFFFFF;
                    border-bottom: 1px solid #E5E7EB;
                }}
                QPushButton {{
                    background-color: transparent;
                    color: #6B7280;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #F3F4F6;
                    color: #1F2937;
                }}
            """,

            # 导航按钮 - 选中状态
            "navbar_active": f"""
                QPushButton {{
                    background-color: #1F2937;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 13px;
                    font-weight: 600;
                }}
            """,

            # 按钮样式
            "button": f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    color: #1F2937;
                    border: 2px solid #E5E7EB;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #F3F4F6;
                    border-color: #1F2937;
                }}
            """,

            # 按钮 - 主要
            "button_primary": f"""
                QPushButton {{
                    background-color: #1F2937;
                    color: #FFFFFF;
                    border: 2px solid #1F2937;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #374151;
                    border-color: #374151;
                }}
            """,

            # 按钮 - 成功
            "button_success": f"""
                QPushButton {{
                    background-color: #10B981;
                    color: #FFFFFF;
                    border: 2px solid #10B981;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #059669;
                    border-color: #059669;
                }}
            """,

            # 输入框
            "input": f"""
                QLineEdit, QTextEdit {{
                    background-color: #FFFFFF;
                    color: #1F2937;
                    border: 2px solid #E5E7EB;
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 13px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: #1F2937;
                }}
                QLineEdit::placeholder, QTextEdit::placeholder {{
                    color: #9CA3AF;
                }}
            """,

            # 卡片
            "card": f"""
                QFrame {{
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 12px;
                    padding: 16px;
                }}
                QFrame:hover {{
                    border-color: #D1D5DB;
                    box-shadow: none;
                }}
            """,

            # 面板
            "panel": f"""
                QGroupBox {{
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 12px;
                    margin-top: 16px;
                    padding-top: 16px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 600;
                    color: #1F2937;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 12px;
                    padding: 4px 8px;
                    color: #1F2937;
                }}
            """,

            # 进度条
            "progress": f"""
                QProgressBar {{
                    background-color: #F3F4F6;
                    border: 1px solid #E5E7EB;
                    border-radius: 6px;
                    text-align: center;
                    color: #1F2937;
                    font-family: 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 11px;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: #1F2937;
                    border-radius: 6px;
                }}
            """,

            # 标签页
            "tabs": f"""
                QTabWidget::pane {{
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                }}
                QTabBar::tab {{
                    background-color: #F9FAFB;
                    color: #6B7280;
                    padding: 10px 20px;
                    border: 1px solid #E5E7EB;
                    border-bottom: none;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 500;
                }}
                QTabBar::tab:selected {{
                    background-color: #FFFFFF;
                    color: #1F2937;
                    border-bottom: 2px solid #1F2937;
                }}
            """,

            # 下拉框
            "combobox": f"""
                QComboBox {{
                    background-color: #FFFFFF;
                    color: #1F2937;
                    border: 2px solid #E5E7EB;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 12px;
                }}
                QComboBox:hover {{
                    border-color: #1F2937;
                    background-color: #F9FAFB;
                }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: #FFFFFF;
                    color: #1F2937;
                    selection-background-color: #F3F4F6;
                    border: 1px solid #E5E7EB;
                }}
            """,

            # 滚动条
            "scrollbar": f"""
                QScrollBar:vertical {{
                    background-color: #F9FAFB;
                    width: 10px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: #D1D5DB;
                    border-radius: 5px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{ background-color: #9CA3AF; }}
            """,

            # 标签文字颜色
            "label": "color: #6B7280;",
            "label_primary": "color: #1F2937;",
            "label_accent": "color: #1F2937;",
            "label_success": "color: #10B981;",
            "label_warning": "color: #F59E0B;",
            "label_danger": "color: #EF4444;",

            # Logo 样式
            "logo": f"""
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 18px;
                font-weight: 700;
                color: #1F2937;
            """,
        }
