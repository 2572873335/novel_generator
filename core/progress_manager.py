"""
进度管理系统
基于 Anthropic 的 claude-progress.txt 模式
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ChapterProgress:
    """单个章节的进度信息"""
    chapter_number: int
    title: str
    status: str  # pending, writing, reviewing, completed, revision_needed
    word_count: int = 0
    quality_score: float = 0.0
    created_at: str = ""
    completed_at: str = ""
    notes: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class NovelProgress:
    """小说整体进度"""
    title: str
    genre: str
    total_chapters: int
    completed_chapters: int = 0
    current_chapter: int = 1
    total_word_count: int = 0
    start_date: str = ""
    last_updated: str = ""
    status: str = "initialized"  # initialized, writing, reviewing, completed
    chapters: List[ChapterProgress] = None
    
    def __post_init__(self):
        if not self.start_date:
            self.start_date = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()
        if self.chapters is None:
            self.chapters = []


class ProgressManager:
    """进度管理器 - 核心组件"""
    
    def __init__(self, project_dir: str, progress_file: str = "novel-progress.txt"):
        self.project_dir = project_dir
        self.progress_file = os.path.join(project_dir, progress_file)
        self.progress: Optional[NovelProgress] = None
        
    def initialize_progress(self, title: str, genre: str, total_chapters: int, 
                          chapter_titles: List[str]) -> NovelProgress:
        """初始化小说进度"""
        chapters = [
            ChapterProgress(
                chapter_number=i+1,
                title=title,
                status="pending"
            )
            for i, title in enumerate(chapter_titles)
        ]
        
        self.progress = NovelProgress(
            title=title,
            genre=genre,
            total_chapters=total_chapters,
            chapters=chapters
        )
        
        self._save_progress()
        return self.progress
    
    def load_progress(self) -> Optional[NovelProgress]:
        """加载进度文件"""
        if not os.path.exists(self.progress_file):
            return None
            
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换章节数据
            chapters_data = data.pop('chapters', [])
            chapters = [ChapterProgress(**ch) for ch in chapters_data]
            
            self.progress = NovelProgress(chapters=chapters, **data)
            return self.progress
        except Exception as e:
            print(f"加载进度文件失败: {e}")
            return None
    
    def _save_progress(self):
        """保存进度到文件"""
        if not self.progress:
            return
            
        os.makedirs(self.project_dir, exist_ok=True)
        
        # 转换为字典
        data = asdict(self.progress)
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_chapter_progress(self, chapter_number: int, **kwargs):
        """更新章节进度"""
        if not self.progress:
            return
            
        for chapter in self.progress.chapters:
            if chapter.chapter_number == chapter_number:
                for key, value in kwargs.items():
                    if hasattr(chapter, key):
                        setattr(chapter, key, value)
                
                if kwargs.get('status') == 'completed':
                    chapter.completed_at = datetime.now().isoformat()
                break
        
        # 更新整体进度
        self._update_overall_progress()
        self._save_progress()
    
    def _update_overall_progress(self):
        """更新整体进度统计"""
        if not self.progress:
            return
            
        completed = sum(1 for ch in self.progress.chapters if ch.status == 'completed')
        self.progress.completed_chapters = completed
        self.progress.total_word_count = sum(ch.word_count for ch in self.progress.chapters)
        self.progress.last_updated = datetime.now().isoformat()
        
        # 找到下一个待完成的章节
        for ch in self.progress.chapters:
            if ch.status == 'pending':
                self.progress.current_chapter = ch.chapter_number
                break
        
        # 更新整体状态
        if completed == self.progress.total_chapters:
            self.progress.status = 'completed'
        elif completed > 0:
            self.progress.status = 'writing'
    
    def get_next_pending_chapter(self) -> Optional[ChapterProgress]:
        """获取下一个待完成的章节"""
        if not self.progress:
            return None
            
        for chapter in self.progress.chapters:
            if chapter.status == 'pending':
                return chapter
        return None
    
    def get_chapter_progress(self, chapter_number: int) -> Optional[ChapterProgress]:
        """获取特定章节的进度"""
        if not self.progress:
            return None
            
        for chapter in self.progress.chapters:
            if chapter.chapter_number == chapter_number:
                return chapter
        return None
    
    def generate_progress_report(self) -> str:
        """生成进度报告"""
        if not self.progress:
            return "无进度信息"
        
        p = self.progress
        percentage = (p.completed_chapters / p.total_chapters * 100) if p.total_chapters > 0 else 0
        
        report = f"""
{'='*60}
📚 小说进度报告: {p.title}
{'='*60}
类型: {p.genre}
总章节: {p.total_chapters}
已完成: {p.completed_chapters} ({percentage:.1f}%)
总字数: {p.total_word_count:,}
开始日期: {p.start_date[:10]}
最后更新: {p.last_updated[:10]}
状态: {p.status}
{'='*60}
章节详情:
"""
        
        for ch in p.chapters:
            status_icon = {
                'pending': '⏳',
                'writing': '✍️',
                'reviewing': '👀',
                'completed': '✅',
                'revision_needed': '🔧'
            }.get(ch.status, '❓')
            
            report += f"  {status_icon} 第{ch.chapter_number}章: {ch.title} - {ch.status}"
            if ch.word_count > 0:
                report += f" ({ch.word_count}字)"
            if ch.quality_score > 0:
                report += f" [质量:{ch.quality_score:.1f}]"
            report += "\n"
        
        report += "="*60
        return report
    
    def is_novel_complete(self) -> bool:
        """检查小说是否已完成"""
        if not self.progress:
            return False
        return self.progress.completed_chapters >= self.progress.total_chapters
