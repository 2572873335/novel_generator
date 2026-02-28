"""
NovelForge v5.0 - 核心模块 Facade
===================================
导出所有主要组件，便于外部模块统一导入

遵循依赖倒置原则，通过 NovelProject 抽象文件系统操作
"""

# 领域模型
from .project_context import NovelProject

# 现有核心组件（保持向后兼容）
from .novel_generator import NovelGenerator, create_novel, MockLLMClient
from .progress_manager import ProgressManager, NovelProgress, ChapterProgress
from .chapter_manager import ChapterManager, ChapterSpec
from .character_manager import CharacterManager, Character

__all__ = [
    # 领域模型
    'NovelProject',

    # 核心生成器
    'NovelGenerator',
    'create_novel',
    'MockLLMClient',

    # 进度管理
    'ProgressManager',
    'NovelProgress',
    'ChapterProgress',

    # 章节管理
    'ChapterManager',
    'ChapterSpec',

    # 人物管理
    'CharacterManager',
    'Character',
]
