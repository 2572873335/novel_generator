"""
Producer Dashboard - 赛博朋克UI重构 (v4.2)
NovelForge v4.2 制片人控制台 - 全面升级版

此文件保留用于向后兼容。请使用新的模块化导入:
    from ui.producer_dashboard import ProducerDashboard
    或
    from ui.main_window import ProducerDashboard
"""

# 向后兼容导入 - 所有类现在从子模块导入
from ui.themes import (
    CyberpunkTheme,
    Typography,
    Spacing,
    Layout,
    ThemeManager,
    ThemeSelector
)

from ui.views import (
    GlobalStatusBar,
    MainNavigationBar,
    PreProductionView,
    ProductionView,
    ProjectVaultView
)

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

from ui.dialogs import (
    ProgressResumeDialog,
    PreProductionPanel,
    ChapterFeedbackDialog,
    SettingsDialog,
    DocumentViewerDialog
)

from ui.main_window import ProducerDashboard, run_dashboard

# 导出所有类和函数
__all__ = [
    # 主题
    'CyberpunkTheme',
    'Typography',
    'Spacing',
    'Layout',
    'ThemeManager',
    'ThemeSelector',

    # 视图
    'GlobalStatusBar',
    'MainNavigationBar',
    'PreProductionView',
    'ProductionView',
    'ProjectVaultView',

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

    # 主窗口
    'ProducerDashboard',
    'run_dashboard'
]


if __name__ == "__main__":
    import sys
    from pathlib import Path

    project_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_dashboard(project_dir)
