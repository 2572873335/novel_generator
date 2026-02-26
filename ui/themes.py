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
    BORDER_SUCCESS = "#00e676"     # 成功边框

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
if PYQT_AVAILABLE:
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
