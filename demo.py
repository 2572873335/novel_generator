#!/usr/bin/env python3
"""
全自动AI小说生成系统 - 演示脚本
展示系统的核心功能和工作流程
"""

import os
import sys
import json
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入（不使用包导入）
from core.progress_manager import ProgressManager
from core.chapter_manager import ChapterManager
from core.character_manager import CharacterManager


def demo_progress_manager():
    """演示进度管理器"""
    print("\n" + "="*60)
    print("📊 演示: 进度管理器")
    print("="*60)
    
    # 创建临时项目目录
    demo_dir = "demo_project"
    os.makedirs(demo_dir, exist_ok=True)
    
    # 初始化进度管理器
    pm = ProgressManager(demo_dir)
    
    # 创建章节标题列表
    chapter_titles = [
        "第一章：开端",
        "第二章：发现",
        "第三章：冲突",
        "第四章：转折",
        "第五章：高潮",
        "第六章：结局"
    ]
    
    # 初始化进度
    progress = pm.initialize_progress(
        title="演示小说",
        genre="科幻",
        total_chapters=6,
        chapter_titles=chapter_titles
    )
    
    print(f"✓ 项目初始化完成")
    print(f"  标题: {progress.title}")
    print(f"  总章节: {progress.total_chapters}")
    
    # 模拟完成一些章节
    print("\n模拟写作进度...")
    pm.update_chapter_progress(1, status='completed', word_count=3200, quality_score=8.5)
    pm.update_chapter_progress(2, status='completed', word_count=2800, quality_score=7.8)
    pm.update_chapter_progress(3, status='writing', word_count=1500)
    
    # 生成进度报告
    report = pm.generate_progress_report()
    print(report)
    
    # 检查是否完成
    print(f"小说是否完成: {pm.is_novel_complete()}")
    
    # 获取下一个待完成的章节
    next_chapter = pm.get_next_pending_chapter()
    if next_chapter:
        print(f"下一个待完成章节: 第{next_chapter.chapter_number}章 - {next_chapter.title}")
    
    # 清理
    import shutil
    shutil.rmtree(demo_dir)
    print("\n✓ 演示完成，已清理临时文件")


def demo_chapter_manager():
    """演示章节管理器"""
    print("\n" + "="*60)
    print("📑 演示: 章节管理器")
    print("="*60)
    
    demo_dir = "demo_project"
    os.makedirs(demo_dir, exist_ok=True)
    
    cm = ChapterManager(demo_dir)
    
    # 创建章节列表
    outline_data = {
        'chapters': [
            {
                'title': '第一章：神秘信号',
                'summary': '天文学家林晓接收到一个神秘的外星信号',
                'key_plot_points': ['林晓发现异常信号', '信号来自4光年外', '决定深入研究'],
                'characters_involved': ['林晓', '导师王教授'],
                'word_count_target': 3000
            },
            {
                'title': '第二章：解密开始',
                'summary': '林晓加入解密团队，开始分析信号内容',
                'key_plot_points': ['组建解密团队', '初步分析信号', '发现信号的规律性'],
                'characters_involved': ['林晓', '团队成员'],
                'word_count_target': 3500
            }
        ]
    }
    
    chapters = cm.create_chapter_list(outline_data)
    print(f"✓ 创建了 {len(chapters)} 个章节")
    
    # 显示章节信息
    for ch in chapters:
        print(f"\n第{ch.chapter_number}章: {ch.title}")
        print(f"  概要: {ch.summary[:50]}...")
        print(f"  关键情节点: {len(ch.key_plot_points)}个")
        print(f"  涉及角色: {', '.join(ch.characters_involved)}")
    
    # 生成写作提示
    prompt = cm.generate_writing_prompt(1)
    print(f"\n写作提示示例:\n{prompt[:300]}...")
    
    # 模拟验证
    test_content = "林晓在观测站发现了神秘信号。这个信号来自4光年外，具有明显的规律性。"
    validation = cm.validate_completion(1, test_content)
    print(f"\n验证结果:")
    print(f"  有效: {validation['valid']}")
    print(f"  字数: {validation['word_count']}")
    print(f"  错误: {validation['errors']}")
    print(f"  警告: {validation['warnings']}")
    
    # 清理
    shutil.rmtree(demo_dir)
    print("\n✓ 演示完成，已清理临时文件")


def demo_character_manager():
    """演示角色管理器"""
    print("\n" + "="*60)
    print("👥 演示: 角色管理器")
    print("="*60)
    
    demo_dir = "demo_project"
    os.makedirs(demo_dir, exist_ok=True)
    
    chm = CharacterManager(demo_dir)
    
    # 创建角色
    characters_data = [
        {
            'name': '林晓',
            'role': 'protagonist',
            'age': 28,
            'appearance': '中等身材，戴着黑框眼镜，眼神中总是充满好奇',
            'personality': '聪明、好奇、有些固执，对未知事物充满热情',
            'background': '顶尖大学天文学博士，从小对星空充满向往',
            'motivation': '想要解开宇宙的奥秘，证明人类并不孤独',
            'character_arc': '从单纯的科学家成长为肩负人类命运的决策者',
            'relationships': {'王教授': '导师和引路人', '陈明': '同事和挚友'},
            'distinctive_features': ['思考时会不自觉地推眼镜', '兴奋时会语速变快'],
            'speech_patterns': '理性、直接，有时会使用专业术语'
        },
        {
            'name': '王教授',
            'role': 'supporting',
            'age': 55,
            'appearance': '头发花白，目光深邃，总是穿着那件旧夹克',
            'personality': '睿智、沉稳、富有远见',
            'background': '天文学界的泰斗，林晓的博士导师',
            'motivation': '培养下一代科学家，推动人类认知边界',
            'character_arc': '从怀疑到支持林晓的研究',
            'relationships': {'林晓': '最得意的学生'},
            'distinctive_features': ['说话慢条斯理', '喜欢在黑板上画图'],
            'speech_patterns': '沉稳、富有哲理，善于用比喻'
        }
    ]
    
    characters = chm.create_characters(characters_data)
    print(f"✓ 创建了 {len(characters)} 个角色")
    
    # 显示角色信息
    for char in characters:
        print(f"\n{char.name} ({char.role})")
        print(f"  年龄: {char.age}")
        print(f"  性格: {char.personality[:60]}...")
        print(f"  动机: {char.motivation[:60]}...")
    
    # 获取主要角色
    main_chars = chm.get_main_characters()
    print(f"\n主要角色: {', '.join(c.name for c in main_chars)}")
    
    # 生成角色写作指南
    guide = chm.generate_character_guide()
    print(f"\n角色写作指南:\n{guide[:400]}...")
    
    # 一致性检查
    test_content = "林晓推了推眼镜，兴奋地说：'这个信号太不可思议了！'"
    consistency = chm.check_character_consistency(test_content, ['林晓'])
    print(f"\n一致性检查:")
    print(f"  一致: {consistency['consistent']}")
    print(f"  问题: {consistency['issues']}")
    
    # 清理
    shutil.rmtree(demo_dir)
    print("\n✓ 演示完成，已清理临时文件")


def demo_full_workflow():
    """演示完整工作流程"""
    print("\n" + "="*60)
    print("🚀 演示: 完整工作流程")
    print("="*60)
    
    from core.novel_generator import create_novel
    
    # 创建配置
    config = {
        'title': '演示小说：星际信号',
        'genre': '科幻',
        'target_chapters': 3,  # 少量章节用于演示
        'words_per_chapter': 1000,  # 较少字数用于演示
        'description': '关于天文学家发现外星信号的故事'
    }
    
    print("配置:")
    print(f"  标题: {config['title']}")
    print(f"  类型: {config['genre']}")
    print(f"  章节: {config['target_chapters']}")
    print(f"  每章字数: {config['words_per_chapter']}")
    
    print("\n开始生成...")
    print("(注意：当前使用模拟LLM，实际内容需要真实LLM API)")
    
    # 运行生成
    result = create_novel(config)
    
    if result['success']:
        print(f"\n✅ 生成成功！")
        print(f"项目位置: {result['project_dir']}")
        print(f"耗时: {result['elapsed_time']:.2f}秒")
        
        # 显示生成的文件
        project_dir = result['project_dir']
        if os.path.exists(project_dir):
            files = os.listdir(project_dir)
            print(f"\n生成的文件:")
            for f in sorted(files):
                print(f"  - {f}")
            
            # 显示章节目录
            chapters_dir = os.path.join(project_dir, 'chapters')
            if os.path.exists(chapters_dir):
                chapters = os.listdir(chapters_dir)
                print(f"\n章节文件 ({len(chapters)}个):")
                for ch in sorted(chapters):
                    print(f"  - {ch}")
        
        # 清理
        import shutil
        shutil.rmtree(project_dir)
        print(f"\n✓ 演示完成，已清理项目目录")
    else:
        print(f"\n❌ 生成失败")


def main():
    """主函数"""
    print("="*60)
    print("📚 全自动AI小说生成系统 - 演示")
    print("="*60)
    print("\n本演示展示系统的核心组件和工作流程")
    print("使用模拟数据，实际使用时需要配置真实LLM API")
    
    try:
        # 运行各个演示
        demo_progress_manager()
        demo_chapter_manager()
        demo_character_manager()
        demo_full_workflow()
        
        print("\n" + "="*60)
        print("✅ 所有演示完成！")
        print("="*60)
        print("\n要使用真实LLM生成小说，请:")
        print("1. 配置LLM API密钥")
        print("2. 修改 agents/ 中的LLM客户端")
        print("3. 运行: python main.py --interactive")
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
