"""
小说生成系统配置
基于 Anthropic 长运行代理最佳实践
"""

from dataclasses import dataclass
from typing import Optional, List
import os


@dataclass
class NovelConfig:
    """小说生成配置"""
    # 基本设置
    title: str
    genre: str  # 类型：科幻、奇幻、悬疑等
    target_chapters: int = 20
    words_per_chapter: int = 3000
    
    # 代理设置
    model_name: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.8
    
    # 项目路径
    project_dir: str = ""
    
    # 进度管理
    progress_file: str = "novel-progress.txt"
    chapter_list_file: str = "chapter-list.json"
    outline_file: str = "outline.md"
    characters_file: str = "characters.json"
    
    # 写作风格
    writing_style: str = "descriptive"  # descriptive, concise, poetic, dramatic
    tone: str = "neutral"  # dark, light, neutral, humorous
    
    # 质量控制
    enable_self_review: bool = True
    min_chapter_quality_score: float = 7.0  # 1-10
    max_revision_attempts: int = 3
    
    def __post_init__(self):
        if not self.project_dir:
            self.project_dir = f"novels/{self.title.replace(' ', '_').lower()}"


@dataclass
class AgentPrompts:
    """代理提示词模板"""
    
    INITIALIZER_SYSTEM_PROMPT = """你是一个专业的小说创作策划师。你的任务是初始化一个新的小说项目。

你需要：
1. 分析用户需求，创建详细的小说大纲
2. 设计完整的角色设定（包括背景、性格、动机、成长弧线）
3. 规划章节结构，创建章节列表
4. 设定世界观和背景设定
5. 创建写作风格指南

输出要求：
- 所有文件使用UTF-8编码
- 章节列表使用JSON格式，包含章节标题、概要、关键情节点
- 角色设定使用JSON格式，便于后续引用
- 大纲使用Markdown格式

记住：你是在为后续的写作代理创建完整的环境，让他们能够基于你的规划进行增量式写作。"""

    WRITER_SYSTEM_PROMPT = """你是一个专业的小说作家。你的任务是根据已有的大纲和设定，逐章创作小说内容。

工作流程：
1. 首先阅读进度文件，了解已完成的内容
2. 查看章节列表，选择下一个待完成的章节
3. 阅读相关角色设定和世界背景
4. 创作该章节内容
5. 进行自我审查和编辑
6. 更新进度文件

写作原则：
- 保持角色一致性
- 遵循已建立的世界观
- 推进情节发展
- 注重场景描写和对话
- 制造冲突和悬念

每次只专注于一个章节，确保质量。完成后使用git提交，并更新进度文件。"""

    REVIEWER_SYSTEM_PROMPT = """你是一个专业的文学编辑。你的任务是审查和评估小说章节的质量。

评估维度（1-10分）：
1. 情节连贯性 - 是否与大纲一致，情节推进是否自然
2. 角色一致性 - 角色行为是否符合设定
3. 写作质量 - 文笔、描写、对话质量
4. 吸引力 - 是否引人入胜，有阅读欲望
5. 技术准确性 - 语法、标点、格式

输出要求：
- 提供总体评分（平均分）
- 列出具体优点
- 列出需要改进的地方
- 如果评分低于标准，提供具体的修改建议"""


# 默认配置
DEFAULT_CONFIG = NovelConfig(
    title="未命名小说",
    genre="general",
    target_chapters=10,
    words_per_chapter=2500
)
