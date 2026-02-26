"""
UI Package - 赛博朋克UI组件库
"""

# 主题系统
from ui.themes import (
    CyberpunkTheme,
    Typography,
    Spacing,
    Layout,
    ThemeManager,
    ThemeSelector
)

# 组件
from ui.components import (
    FlipCard,
    AgentCardBack,
    MiniAgentBadge,
    MinimalistBadge,
    AgentDetailPanel,
    AgentMatrixPanel,
    EmotionWavePanel,
    AutoSaveIndicator,
    EvaluationCard,
    LogPanel,
    CircuitBreakerPanel,
    StatusLightIndicator,
    RollbackHistoryBars,
    TopControlPanel
)

# 对话框
from ui.dialogs import (
    ProgressResumeDialog,
    PreProductionPanel,
    ChapterFeedbackDialog,
    SettingsDialog,
    DocumentViewerDialog
)

# 视图
from ui.views import (
    GlobalStatusBar,
    MainNavigationBar,
    PreProductionView,
    ProjectVaultView
)

# 主窗口
from ui.main_window import ProducerDashboard, run_dashboard

__all__ = [
    # 主题
    'CyberpunkTheme',
    'Typography',
    'Spacing',
    'Layout',
    'ThemeManager',
    'ThemeSelector',

    # 组件
    'FlipCard',
    'AgentCardBack',
    'MiniAgentBadge',
    'MinimalistBadge',
    'AgentDetailPanel',
    'AgentMatrixPanel',
    'EmotionWavePanel',
    'AutoSaveIndicator',
    'EvaluationCard',
    'LogPanel',
    'CircuitBreakerPanel',
    'StatusLightIndicator',
    'RollbackHistoryBars',
    'TopControlPanel',

    # 对话框
    'ProgressResumeDialog',
    'PreProductionPanel',
    'ChapterFeedbackDialog',
    'SettingsDialog',
    'DocumentViewerDialog',

    # 视图
    'GlobalStatusBar',
    'MainNavigationBar',
    'PreProductionView',
    'ProjectVaultView',

    # 主窗口
    'ProducerDashboard',
    'run_dashboard'
]
