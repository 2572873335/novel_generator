"""
核心模块
包含主控制器和各种管理器
"""

from .novel_generator import NovelGenerator, create_novel, MockLLMClient
from .progress_manager import ProgressManager, NovelProgress, ChapterProgress
from .chapter_manager import ChapterManager, ChapterSpec
from .character_manager import CharacterManager, Character

__all__ = [
    'NovelGenerator',
    'create_novel',
    'MockLLMClient',
    'ProgressManager',
    'NovelProgress',
    'ChapterProgress',
    'ChapterManager',
    'ChapterSpec',
    'CharacterManager',
    'Character'
]
