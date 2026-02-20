"""
全自动AI小说生成系统
基于 Anthropic 长运行代理最佳实践

核心组件：
- NovelGenerator: 主控制器
- InitializerAgent: 项目初始化
- WriterAgent: 逐章写作
- ReviewerAgent: 质量审查
- ProgressManager: 进度管理
- ChapterManager: 章节管理
- CharacterManager: 角色管理
"""

from .core.novel_generator import NovelGenerator, create_novel
from .config.settings import NovelConfig, AgentPrompts, DEFAULT_CONFIG

__version__ = '1.0.0'
__author__ = 'AI Novel Generator'

__all__ = [
    'NovelGenerator',
    'create_novel',
    'NovelConfig',
    'AgentPrompts',
    'DEFAULT_CONFIG'
]
