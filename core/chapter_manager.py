"""
章节列表管理器
对应 Anthropic 文章中的 feature_list.json 模式
"""

import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ChapterSpec:
    """章节规格 - 对应文章中的 feature 规格"""
    chapter_number: int
    title: str
    summary: str  # 章节概要
    key_plot_points: List[str]  # 关键情节点
    characters_involved: List[str]  # 涉及的角色
    word_count_target: int
    status: str = "pending"  # pending, writing, completed
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterSpec':
        return cls(**data)


class ChapterManager:
    """章节管理器 - 管理章节列表"""
    
    def __init__(self, project_dir: str, chapter_file: str = "chapter-list.json"):
        self.project_dir = project_dir
        self.chapter_file = os.path.join(project_dir, chapter_file)
        self.chapters: List[ChapterSpec] = []
    
    def create_chapter_list(self, outline_data: Dict[str, Any]) -> List[ChapterSpec]:
        """
        基于大纲创建章节列表
        
        Args:
            outline_data: 包含章节规划的字典
        """
        chapters_data = outline_data.get('chapters', [])
        
        self.chapters = []
        for i, ch_data in enumerate(chapters_data, 1):
            chapter = ChapterSpec(
                chapter_number=i,
                title=ch_data.get('title', f'第{i}章'),
                summary=ch_data.get('summary', ''),
                key_plot_points=ch_data.get('key_plot_points', []),
                characters_involved=ch_data.get('characters_involved', []),
                word_count_target=ch_data.get('word_count_target', 3000)
            )
            self.chapters.append(chapter)
        
        self._save_chapters()
        return self.chapters
    
    def load_chapters(self) -> List[ChapterSpec]:
        """加载章节列表"""
        if not os.path.exists(self.chapter_file):
            return []
        
        try:
            with open(self.chapter_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.chapters = [ChapterSpec.from_dict(ch) for ch in data]
            return self.chapters
        except Exception as e:
            print(f"加载章节列表失败: {e}")
            return []
    
    def _save_chapters(self):
        """保存章节列表"""
        os.makedirs(self.project_dir, exist_ok=True)
        
        data = [ch.to_dict() for ch in self.chapters]
        
        with open(self.chapter_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_chapter_status(self, chapter_number: int, status: str, notes: str = ""):
        """更新章节状态"""
        for chapter in self.chapters:
            if chapter.chapter_number == chapter_number:
                chapter.status = status
                if notes:
                    chapter.notes = notes
                break
        
        self._save_chapters()
    
    def get_chapter(self, chapter_number: int) -> Optional[ChapterSpec]:
        """获取特定章节"""
        for chapter in self.chapters:
            if chapter.chapter_number == chapter_number:
                return chapter
        return None
    
    def get_pending_chapters(self) -> List[ChapterSpec]:
        """获取所有待完成的章节"""
        return [ch for ch in self.chapters if ch.status == 'pending']
    
    def get_completed_chapters(self) -> List[ChapterSpec]:
        """获取所有已完成的章节"""
        return [ch for ch in self.chapters if ch.status == 'completed']
    
    def generate_writing_prompt(self, chapter_number: int) -> str:
        """
        为特定章节生成写作提示
        这是给 Writer Agent 的详细指导
        """
        chapter = self.get_chapter(chapter_number)
        if not chapter:
            return ""
        
        prompt = f"""# 第{chapter.chapter_number}章写作指导

## 章节标题
{chapter.title}

## 章节概要
{chapter.summary}

## 关键情节点（必须包含）
"""
        for i, point in enumerate(chapter.key_plot_points, 1):
            prompt += f"{i}. {point}\n"
        
        prompt += f"""
## 涉及角色
{', '.join(chapter.characters_involved)}

## 字数目标
{chapter.word_count_target} 字

## 写作要求
1. 确保所有关键情节点都得到展开
2. 保持角色行为和对话符合其性格设定
3. 注意章节之间的连贯性
4. 在结尾处制造适当的悬念或过渡
5. 注重场景描写，让读者有身临其境的感觉

请开始创作这一章节的内容。
"""
        return prompt
    
    def validate_completion(self, chapter_number: int, content: str) -> Dict[str, Any]:
        """
        验证章节是否完成所有要求
        对应文章中的测试验证
        """
        chapter = self.get_chapter(chapter_number)
        if not chapter:
            return {'valid': False, 'errors': ['章节不存在']}
        
        errors = []
        warnings = []
        
        # 检查字数
        word_count = len(content)
        if word_count < chapter.word_count_target * 0.8:
            errors.append(f"字数不足: 当前{word_count}字，目标{chapter.word_count_target}字")
        elif word_count > chapter.word_count_target * 1.3:
            warnings.append(f"字数超出: 当前{word_count}字，目标{chapter.word_count_target}字")
        
        # 检查关键情节点（简化版本，实际可以使用LLM进行更复杂的检查）
        # 这里只是检查关键词出现
        for point in chapter.key_plot_points:
            key_terms = point.split()[:3]  # 取前3个词作为关键词
            if not any(term in content for term in key_terms if len(term) > 2):
                warnings.append(f"可能缺少情节点: {point[:30]}...")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'word_count': word_count
        }
