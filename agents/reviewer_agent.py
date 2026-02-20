"""
Reviewer Agent
负责审查和评估小说章节的质量
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ReviewResult:
    """审查结果"""
    chapter_number: int
    overall_score: float  # 1-10
    plot_coherence: float  # 情节连贯性
    character_consistency: float  # 角色一致性
    writing_quality: float  # 写作质量
    engagement: float  # 吸引力
    technical_accuracy: float  # 技术准确性
    strengths: List[str]  # 优点
    weaknesses: List[str]  # 缺点
    suggestions: List[str]  # 修改建议
    passed: bool  # 是否通过


class ReviewerAgent:
    """
    审查代理
    
    评估维度（基于 Anthropic 文章）：
    1. 情节连贯性 - 是否与大纲一致
    2. 角色一致性 - 角色行为是否符合设定
    3. 写作质量 - 文笔、描写、对话
    4. 吸引力 - 是否引人入胜
    5. 技术准确性 - 语法、标点、格式
    """
    
    def __init__(self, llm_client, project_dir: str):
        self.llm = llm_client
        self.project_dir = project_dir
        self.chapters_dir = os.path.join(project_dir, 'chapters')
    
    def review_chapter(self, chapter_number: int) -> ReviewResult:
        """
        审查特定章节
        
        Args:
            chapter_number: 章节编号
        
        Returns:
            审查结果
        """
        print(f"\n🔍 Reviewer Agent: 正在审查第{chapter_number}章")
        
        # 1. 加载章节内容
        chapter_content = self._load_chapter(chapter_number)
        if not chapter_content:
            print(f"❌ 错误: 无法加载第{chapter_number}章")
            return self._create_error_result(chapter_number, "无法加载章节")
        
        # 2. 加载上下文
        context = self._load_context(chapter_number)
        
        # 3. 执行各项评估
        print("   正在评估情节连贯性...")
        plot_score = self._evaluate_plot_coherence(chapter_content, context)
        
        print("   正在评估角色一致性...")
        character_score = self._evaluate_character_consistency(chapter_content, context)
        
        print("   正在评估写作质量...")
        writing_score = self._evaluate_writing_quality(chapter_content)
        
        print("   正在评估吸引力...")
        engagement_score = self._evaluate_engagement(chapter_content)
        
        print("   正在评估技术准确性...")
        technical_score = self._evaluate_technical_accuracy(chapter_content)
        
        # 4. 计算总分
        overall_score = (plot_score + character_score + writing_score + 
                        engagement_score + technical_score) / 5
        
        # 5. 生成建议
        strengths, weaknesses, suggestions = self._generate_feedback(
            chapter_content, context, 
            plot_score, character_score, writing_score, 
            engagement_score, technical_score
        )
        
        # 6. 判断是否通过
        passed = overall_score >= 7.0
        
        result = ReviewResult(
            chapter_number=chapter_number,
            overall_score=overall_score,
            plot_coherence=plot_score,
            character_consistency=character_score,
            writing_quality=writing_score,
            engagement=engagement_score,
            technical_accuracy=technical_score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            passed=passed
        )
        
        # 7. 保存审查报告
        self._save_review_report(result)
        
        # 8. 输出结果
        self._print_review_result(result)
        
        return result
    
    def review_all_chapters(self) -> List[ReviewResult]:
        """审查所有已完成的章节"""
        progress = self._load_progress()
        if not progress:
            print("❌ 错误: 未找到进度文件")
            return []
        
        results = []
        for ch in progress['chapters']:
            if ch['status'] == 'completed':
                result = self.review_chapter(ch['chapter_number'])
                results.append(result)
        
        return results
    
    def _load_chapter(self, chapter_number: int) -> Optional[str]:
        """加载章节内容"""
        chapter_file = os.path.join(self.chapters_dir, f'chapter-{chapter_number:03d}.md')
        
        if not os.path.exists(chapter_file):
            return None
        
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def _load_context(self, chapter_number: int) -> Dict[str, Any]:
        """加载审查所需的上下文"""
        context = {}
        
        # 加载章节规格
        chapter_list_file = os.path.join(self.project_dir, 'chapter-list.json')
        if os.path.exists(chapter_list_file):
            with open(chapter_list_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
                for ch in chapters:
                    if ch['chapter_number'] == chapter_number:
                        context['chapter_spec'] = ch
                        break
        
        # 加载角色设定
        characters_file = os.path.join(self.project_dir, 'characters.json')
        if os.path.exists(characters_file):
            with open(characters_file, 'r', encoding='utf-8') as f:
                context['characters'] = json.load(f)
        
        # 加载大纲
        outline_file = os.path.join(self.project_dir, 'outline.md')
        if os.path.exists(outline_file):
            with open(outline_file, 'r', encoding='utf-8') as f:
                context['outline'] = f.read()
        
        # 加载前一章节
        if chapter_number > 1:
            prev_file = os.path.join(self.chapters_dir, f'chapter-{chapter_number-1:03d}.md')
            if os.path.exists(prev_file):
                with open(prev_file, 'r', encoding='utf-8') as f:
                    context['previous_chapter'] = f.read()
        
        return context
    
    def _load_progress(self) -> Optional[Dict[str, Any]]:
        """加载进度文件"""
        progress_file = os.path.join(self.project_dir, 'novel-progress.txt')
        
        if not os.path.exists(progress_file):
            return None
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def _evaluate_plot_coherence(self, content: str, context: Dict[str, Any]) -> float:
        """评估情节连贯性"""
        chapter_spec = context.get('chapter_spec', {})
        score = 8.0  # 基础分
        
        # 检查关键情节点
        key_points = chapter_spec.get('key_plot_points', [])
        if key_points:
            covered = 0
            for point in key_points:
                keywords = point.split()[:2]
                if any(kw in content for kw in keywords if len(kw) > 2):
                    covered += 1
            
            coverage = covered / len(key_points)
            if coverage < 0.5:
                score -= 2.0
            elif coverage < 0.8:
                score -= 1.0
            elif coverage >= 0.9:
                score += 0.5
        
        # 检查章节概要匹配度（简化）
        summary = chapter_spec.get('summary', '')
        if summary:
            summary_keywords = summary.split()[:3]
            matches = sum(1 for kw in summary_keywords if kw in content)
            if matches < len(summary_keywords) * 0.5:
                score -= 0.5
        
        return max(1.0, min(10.0, score))
    
    def _evaluate_character_consistency(self, content: str, context: Dict[str, Any]) -> float:
        """评估角色一致性"""
        characters = context.get('characters', [])
        chapter_spec = context.get('chapter_spec', {})
        score = 8.0
        
        involved = chapter_spec.get('characters_involved', [])
        
        for char_name in involved:
            char = next((c for c in characters if c['name'] == char_name), None)
            if not char:
                continue
            
            # 检查角色名是否出现
            if char_name not in content:
                score -= 1.0
                continue
            
            # 检查角色特征词（简化）
            personality = char.get('personality', '')
            if personality:
                traits = personality.split()[:2]
                if not any(trait in content for trait in traits if len(trait) > 2):
                    score -= 0.3
        
        return max(1.0, min(10.0, score))
    
    def _evaluate_writing_quality(self, content: str) -> float:
        """评估写作质量"""
        score = 7.5
        
        # 检查段落结构
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 5:
            score -= 1.0
        
        # 检查对话（简化）
        dialogue_count = content.count('"') + content.count('"') + content.count('"')
        if dialogue_count < 10:
            score -= 0.5
        
        # 检查描写（寻找形容词和副词）
        descriptive_words = ['美丽', '黑暗', '明亮', '寂静', '喧闹', '温暖', '寒冷']
        has_description = any(word in content for word in descriptive_words)
        if not has_description:
            score -= 0.5
        
        # 检查场景转换
        if '---' in content or '***' in content:
            score += 0.3
        
        return max(1.0, min(10.0, score))
    
    def _evaluate_engagement(self, content: str) -> float:
        """评估吸引力"""
        score = 7.0
        
        # 检查开头吸引力
        first_para = content[:200]
        hooks = ['突然', '然而', '但是', '没想到', '意外', '神秘', '秘密']
        if any(hook in first_para for hook in hooks):
            score += 0.5
        
        # 检查冲突元素
        conflicts = ['冲突', '矛盾', '斗争', '对抗', '挑战', '困难', '问题']
        conflict_count = sum(content.count(c) for c in conflicts)
        if conflict_count >= 3:
            score += 0.5
        elif conflict_count == 0:
            score -= 1.0
        
        # 检查悬念
        cliffhangers = ['？', '...', '难道', '究竟', '到底', '悬念']
        if any(c in content[-200:] for c in cliffhangers):
            score += 0.5
        
        # 检查情感表达
        emotions = ['感到', '觉得', '心情', '情绪', '激动', '紧张', '兴奋']
        if any(e in content for e in emotions):
            score += 0.3
        
        return max(1.0, min(10.0, score))
    
    def _evaluate_technical_accuracy(self, content: str) -> float:
        """评估技术准确性"""
        score = 9.0
        
        # 检查标点使用
        if content.count('"') % 2 != 0:
            score -= 0.5  # 引号不匹配
        
        # 检查段落格式
        lines = content.split('\n')
        for line in lines:
            if line.strip() and len(line) > 500:
                score -= 0.2  # 段落过长
        
        # 检查重复（简化）
        words = content.split()
        if len(words) > 100:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:
                score -= 0.5  # 词汇重复过多
        
        # 检查标题格式
        if not content.strip().startswith('#'):
            score -= 0.3
        
        return max(1.0, min(10.0, score))
    
    def _generate_feedback(self, content: str, context: Dict[str, Any],
                          plot_score: float, character_score: float,
                          writing_score: float, engagement_score: float,
                          technical_score: float) -> tuple:
        """生成反馈意见"""
        strengths = []
        weaknesses = []
        suggestions = []
        
        # 基于各项评分生成反馈
        if plot_score >= 8:
            strengths.append("情节连贯，符合大纲规划")
        elif plot_score < 6:
            weaknesses.append("情节连贯性有待提高")
            suggestions.append("确保所有关键情节点都得到展开")
        
        if character_score >= 8:
            strengths.append("角色表现一致，性格鲜明")
        elif character_score < 6:
            weaknesses.append("角色一致性需要加强")
            suggestions.append("检查角色行为是否符合其性格设定")
        
        if writing_score >= 8:
            strengths.append("文笔流畅，描写生动")
        elif writing_score < 6:
            weaknesses.append("写作质量需要提升")
            suggestions.append("增加场景描写，让对话更加自然")
        
        if engagement_score >= 8:
            strengths.append("内容引人入胜，有阅读欲望")
        elif engagement_score < 6:
            weaknesses.append("吸引力不足")
            suggestions.append("增加冲突和悬念，提升故事张力")
        
        if technical_score >= 8:
            strengths.append("格式规范，无明显错误")
        elif technical_score < 6:
            weaknesses.append("存在技术性问题")
            suggestions.append("检查标点符号和段落格式")
        
        # 字数检查
        chapter_spec = context.get('chapter_spec', {})
        target = chapter_spec.get('word_count_target', 3000)
        actual = len(content)
        if actual < target * 0.8:
            weaknesses.append(f"字数不足（{actual}/{target}）")
            suggestions.append(f"扩充内容至目标字数附近")
        elif actual > target * 1.3:
            weaknesses.append(f"字数超出（{actual}/{target}）")
            suggestions.append(f"精简内容，控制在目标字数范围内")
        
        return strengths, weaknesses, suggestions
    
    def _save_review_report(self, result: ReviewResult):
        """保存审查报告"""
        reviews_dir = os.path.join(self.project_dir, 'reviews')
        os.makedirs(reviews_dir, exist_ok=True)
        
        report_file = os.path.join(reviews_dir, f'review-{result.chapter_number:03d}.md')
        
        report = f"""# 第{result.chapter_number}章审查报告

## 总体评分: {result.overall_score:.1f}/10

**结果**: {'✅ 通过' if result.passed else '❌ 需要修改'}

## 详细评分

| 维度 | 分数 |
|------|------|
| 情节连贯性 | {result.plot_coherence:.1f}/10 |
| 角色一致性 | {result.character_consistency:.1f}/10 |
| 写作质量 | {result.writing_quality:.1f}/10 |
| 吸引力 | {result.engagement:.1f}/10 |
| 技术准确性 | {result.technical_accuracy:.1f}/10 |

## 优点

"""
        for strength in result.strengths:
            report += f"- {strength}\n"
        
        report += "\n## 需要改进的地方\n\n"
        for weakness in result.weaknesses:
            report += f"- {weakness}\n"
        
        report += "\n## 修改建议\n\n"
        for suggestion in result.suggestions:
            report += f"- {suggestion}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _print_review_result(self, result: ReviewResult):
        """输出审查结果"""
        print(f"\n{'='*60}")
        print(f"📊 第{result.chapter_number}章审查结果")
        print(f"{'='*60}")
        print(f"总体评分: {result.overall_score:.1f}/10")
        print(f"结果: {'✅ 通过' if result.passed else '❌ 需要修改'}")
        print(f"\n详细评分:")
        print(f"  情节连贯性: {result.plot_coherence:.1f}/10")
        print(f"  角色一致性: {result.character_consistency:.1f}/10")
        print(f"  写作质量: {result.writing_quality:.1f}/10")
        print(f"  吸引力: {result.engagement:.1f}/10")
        print(f"  技术准确性: {result.technical_accuracy:.1f}/10")
        
        if result.strengths:
            print(f"\n优点:")
            for s in result.strengths:
                print(f"  ✓ {s}")
        
        if result.weaknesses:
            print(f"\n需要改进:")
            for w in result.weaknesses:
                print(f"  ✗ {w}")
        
        print(f"{'='*60}")
    
    def _create_error_result(self, chapter_number: int, error: str) -> ReviewResult:
        """创建错误结果"""
        return ReviewResult(
            chapter_number=chapter_number,
            overall_score=0,
            plot_coherence=0,
            character_consistency=0,
            writing_quality=0,
            engagement=0,
            technical_accuracy=0,
            strengths=[],
            weaknesses=[error],
            suggestions=["请检查文件是否存在"],
            passed=False
        )
