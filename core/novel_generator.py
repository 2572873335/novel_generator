"""
全自动AI小说生成系统主控制器
基于 Anthropic 长运行代理最佳实践

系统架构：
1. Initializer Agent - 初始化项目环境
2. Writer Agent - 逐章增量式写作
3. Reviewer Agent - 质量审查
4. Progress Manager - 进度管理
5. Chapter Manager - 章节列表管理
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入各个组件
try:
    from progress_manager import ProgressManager
    from chapter_manager import ChapterManager
    from character_manager import CharacterManager
except ImportError:
    from .progress_manager import ProgressManager
    from .chapter_manager import ChapterManager
    from .character_manager import CharacterManager


class NovelGenerator:
    """
    全自动小说生成器
    
    工作流程：
    1. 初始化阶段：Initializer Agent 创建项目结构
    2. 写作阶段：Writer Agent 循环写作，直到完成所有章节
    3. 审查阶段：Reviewer Agent 审查所有章节
    4. 合并阶段：将所有章节合并为完整小说
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化小说生成器
        
        Args:
            config: 配置字典，包含title, genre, target_chapters等
        """
        self.config = config
        self.project_dir = config.get('project_dir', f"novels/{config.get('title', 'untitled').replace(' ', '_').lower()}")
        
        # 初始化管理器
        self.progress_manager = ProgressManager(self.project_dir)
        self.chapter_manager = ChapterManager(self.project_dir)
        self.character_manager = CharacterManager(self.project_dir)
        
        # 代理将在需要时初始化
        self.initializer = None
        self.writer = None
        self.reviewer = None
        
        print("="*60)
        print("📚 全自动AI小说生成系统")
        print("="*60)
        print(f"项目: {config.get('title', '未命名')}")
        print(f"类型: {config.get('genre', '通用')}")
        print(f"目标章节: {config.get('target_chapters', 20)}")
        print(f"项目目录: {self.project_dir}")
        print("="*60)
    
    def run(self) -> Dict[str, Any]:
        """
        运行完整的小说生成流程
        
        Returns:
            生成结果统计
        """
        start_time = time.time()
        
        print("\n🚀 开始小说生成流程\n")
        
        # 阶段1: 初始化
        if not self._is_initialized():
            self._initialize_project()
        else:
            print("✓ 项目已初始化，跳过初始化阶段")
        
        # 阶段2: 写作
        self._write_novel()
        
        # 阶段3: 审查
        self._review_novel()
        
        # 阶段4: 合并
        self._merge_chapters()
        
        # 生成最终报告
        elapsed_time = time.time() - start_time
        report = self._generate_final_report(elapsed_time)
        
        print("\n" + "="*60)
        print("✅ 小说生成完成！")
        print("="*60)
        print(report)
        
        return {
            'success': True,
            'project_dir': self.project_dir,
            'elapsed_time': elapsed_time,
            'report': report
        }
    
    def _is_initialized(self) -> bool:
        """检查项目是否已初始化"""
        required_files = [
            'novel-progress.txt',
            'chapter-list.json',
            'characters.json',
            'outline.md'
        ]
        
        for file in required_files:
            if not os.path.exists(os.path.join(self.project_dir, file)):
                return False
        
        return True
    
    def _initialize_project(self):
        """初始化项目"""
        print("📦 阶段1: 项目初始化\n")
        
        # 延迟导入以避免循环依赖
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from agents.initializer_agent import InitializerAgent
        
        # 创建模拟的LLM客户端
        llm_client = MockLLMClient()
        
        # 初始化代理
        self.initializer = InitializerAgent(llm_client, self.project_dir)
        
        # 执行初始化
        result = self.initializer.initialize_project(self.config)
        
        print(f"\n✓ 项目初始化完成")
        print(f"  创建文件: {len(result['files_created'])}个")
        
        # 加载到管理器
        self.chapter_manager.load_chapters()
        self.character_manager.load_characters()
    
    def _write_novel(self):
        """写作阶段"""
        print("\n" + "="*60)
        print("✍️ 阶段2: 小说写作")
        print("="*60)
        
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from agents.writer_agent import WriterAgent
        
        llm_client = MockLLMClient()
        self.writer = WriterAgent(llm_client, self.project_dir)
        
        # 加载进度
        progress = self.progress_manager.load_progress()
        if not progress:
            print("❌ 错误: 无法加载进度文件")
            return
        
        total_chapters = progress.total_chapters
        completed = progress.completed_chapters
        
        print(f"\n总章节: {total_chapters}")
        print(f"已完成: {completed}")
        print(f"待完成: {total_chapters - completed}\n")
        
        # 循环写作直到完成
        session_count = 0
        max_sessions = total_chapters * 2  # 防止无限循环
        
        while completed < total_chapters and session_count < max_sessions:
            session_count += 1
            
            print(f"\n--- 写作会话 #{session_count} ---")
            
            # 执行一次写作会话
            result = self.writer.write_session()
            
            if not result['success']:
                if result.get('status') == 'completed':
                    print("✅ 所有章节已完成")
                    break
                else:
                    print(f"❌ 写作失败: {result.get('error', '未知错误')}")
                    break
            
            # 更新进度
            completed += 1
            
            # 显示进度
            percentage = (completed / total_chapters) * 100
            print(f"\n总体进度: {completed}/{total_chapters} ({percentage:.1f}%)")
            
            # 短暂暂停（实际系统中可以配置）
            time.sleep(0.5)
        
        print(f"\n✓ 写作阶段完成，共完成 {completed} 章")
    
    def _review_novel(self):
        """审查阶段"""
        print("\n" + "="*60)
        print("🔍 阶段3: 质量审查")
        print("="*60)
        
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from agents.reviewer_agent import ReviewerAgent
        
        llm_client = MockLLMClient()
        self.reviewer = ReviewerAgent(llm_client, self.project_dir)
        
        # 审查所有章节
        results = self.reviewer.review_all_chapters()
        
        # 统计结果
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        avg_score = sum(r.overall_score for r in results) / total if total > 0 else 0
        
        print(f"\n审查统计:")
        print(f"  总章节: {total}")
        print(f"  通过: {passed}")
        print(f"  需要修改: {total - passed}")
        print(f"  平均评分: {avg_score:.1f}/10")
    
    def _merge_chapters(self):
        """合并章节为完整小说"""
        print("\n" + "="*60)
        print("📖 阶段4: 合并章节")
        print("="*60)
        
        chapters_dir = os.path.join(self.project_dir, 'chapters')
        
        if not os.path.exists(chapters_dir):
            print("❌ 错误: 章节目录不存在")
            return
        
        # 获取所有章节文件
        chapter_files = sorted([
            f for f in os.listdir(chapters_dir) 
            if f.startswith('chapter-') and f.endswith('.md')
        ])
        
        if not chapter_files:
            print("❌ 错误: 未找到章节文件")
            return
        
        # 合并内容
        merged_content = f"""# {self.config.get('title', '未命名小说')}

**类型**: {self.config.get('genre', '通用')}

**生成日期**: {datetime.now().strftime('%Y-%m-%d')}

---

"""
        
        total_word_count = 0
        
        for chapter_file in chapter_files:
            file_path = os.path.join(chapters_dir, chapter_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            merged_content += content + "\n\n---\n\n"
            total_word_count += len(content)
        
        # 保存合并后的文件
        output_file = os.path.join(self.project_dir, 'novel-complete.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        print(f"✓ 合并完成")
        print(f"  章节数: {len(chapter_files)}")
        print(f"  总字数: {total_word_count:,}")
        print(f"  输出文件: novel-complete.md")
    
    def _generate_final_report(self, elapsed_time: float) -> str:
        """生成最终报告"""
        progress = self.progress_manager.load_progress()
        
        if not progress:
            return "无法生成报告"
        
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        report = f"""
{'='*60}
📊 小说生成报告
{'='*60}

项目信息:
  标题: {progress.title}
  类型: {progress.genre}
  总章节: {progress.total_chapters}
  已完成: {progress.completed_chapters}
  总字数: {progress.total_word_count:,}

生成统计:
  耗时: {hours}小时 {minutes}分钟 {seconds}秒
  平均速度: {progress.total_word_count / elapsed_time:.0f} 字/秒

文件位置:
  项目目录: {self.project_dir}
  完整小说: {self.project_dir}/novel-complete.md
  章节目录: {self.project_dir}/chapters/
  审查报告: {self.project_dir}/reviews/

{'='*60}
"""
        
        # 保存报告
        report_file = os.path.join(self.project_dir, 'generation-report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report
    
    def get_progress(self) -> str:
        """获取当前进度报告"""
        return self.progress_manager.generate_progress_report()


class MockLLMClient:
    """
    模拟LLM客户端
    实际实现中应该调用真实的LLM API（如Claude、GPT等）
    """
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        # 这里应该调用真实的LLM API
        return f"[模拟LLM输出] 基于提示: {prompt[:50]}..."
    
    def generate_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成JSON格式的输出"""
        # 这里应该调用真实的LLM API并解析JSON
        return {}


def create_novel(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    便捷函数：创建小说
    
    Args:
        config: 小说配置
        
    Returns:
        生成结果
    
    Example:
        result = create_novel({
            'title': '我的科幻小说',
            'genre': '科幻',
            'target_chapters': 10,
            'description': '关于人工智能觉醒的故事'
        })
    """
    generator = NovelGenerator(config)
    return generator.run()
