#!/usr/bin/env python3
"""
全自动AI小说生成系统 - 主入口

使用方法:
    python main.py --config config.json
    python main.py --title "我的小说" --genre "科幻" --chapters 10
    python main.py --interactive
"""

import argparse
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from novel_generator import create_novel, NovelGenerator


def load_config(config_file: str) -> dict:
    """从JSON文件加载配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def interactive_mode():
    """交互式模式"""
    print("\n" + "="*60)
    print("[BOOK] 全自动AI小说生成系统 - 交互模式")
    print("="*60 + "\n")
    
    # 收集用户输入
    title = input("请输入小说标题: ").strip()
    if not title:
        title = "未命名小说"
    
    print("\n请选择小说类型:")
    genres = ['科幻', '奇幻', '悬疑', '言情', '历史', '武侠', '现代', '其他']
    for i, genre in enumerate(genres, 1):
        print(f"  {i}. {genre}")
    
    genre_choice = input("\n请输入编号 (默认1): ").strip()
    try:
        genre = genres[int(genre_choice) - 1] if genre_choice else '科幻'
    except:
        genre = '科幻'
    
    chapters_input = input("\n请输入目标章节数 (默认10): ").strip()
    try:
        chapters = int(chapters_input) if chapters_input else 10
    except:
        chapters = 10
    
    words_input = input("\n请输入每章字数 (默认3000): ").strip()
    try:
        words = int(words_input) if words_input else 3000
    except:
        words = 3000
    
    description = input("\n请输入故事简介 (可选): ").strip()
    
    # 构建配置
    config = {
        'title': title,
        'genre': genre,
        'target_chapters': chapters,
        'words_per_chapter': words,
        'description': description
    }
    
    print("\n" + "="*60)
    print("配置确认:")
    print(f"  标题: {title}")
    print(f"  类型: {genre}")
    print(f"  章节: {chapters}")
    print(f"  每章字数: {words}")
    print("="*60)
    
    confirm = input("\n确认开始生成? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 开始生成
    print("\n")
    result = create_novel(config)
    
    if result['success']:
        print(f"\n[OK] 小说生成成功！")
        print(f"项目位置: {result['project_dir']}")
    else:
        print(f"\n[FAIL] 生成失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='全自动AI小说生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式模式
  python main.py --interactive
  
  # 使用配置文件
  python main.py --config novel_config.json
  
  # 命令行参数
  python main.py --title "我的科幻小说" --genre "科幻" --chapters 10
        """
    )
    
    parser.add_argument('--config', '-c', type=str,
                       help='配置文件路径 (JSON格式)')
    parser.add_argument('--title', '-t', type=str,
                       help='小说标题')
    parser.add_argument('--genre', '-g', type=str, default='general',
                       help='小说类型 (默认: general)')
    parser.add_argument('--chapters', '-n', type=int, default=10,
                       help='目标章节数 (默认: 10)')
    parser.add_argument('--words', '-w', type=int, default=3000,
                       help='每章字数 (默认: 3000)')
    parser.add_argument('--description', '-d', type=str,
                       help='故事简介')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='交互式模式')
    parser.add_argument('--progress', '-p', type=str,
                       help='查看指定项目的进度')
    
    args = parser.parse_args()
    
    # 查看进度模式
    if args.progress:
        from novel_generator.core.progress_manager import ProgressManager
        
        pm = ProgressManager(args.progress)
        progress = pm.load_progress()
        
        if progress:
            print(pm.generate_progress_report())
        else:
            print(f"[FAIL] 未找到项目: {args.progress}")
        return
    
    # 交互式模式
    if args.interactive:
        interactive_mode()
        return
    
    # 配置文件模式
    if args.config:
        if not os.path.exists(args.config):
            print(f"[FAIL] 配置文件不存在: {args.config}")
            return
        
        config = load_config(args.config)
        result = create_novel(config)
        
        if result['success']:
            print(f"\n[OK] 小说生成成功！")
            print(f"项目位置: {result['project_dir']}")
        return
    
    # 命令行参数模式
    if args.title:
        config = {
            'title': args.title,
            'genre': args.genre,
            'target_chapters': args.chapters,
            'words_per_chapter': args.words,
            'description': args.description or ''
        }
        
        result = create_novel(config)
        
        if result['success']:
            print(f"\n[OK] 小说生成成功！")
            print(f"项目位置: {result['project_dir']}")
        return
    
    # 没有参数，显示帮助
    parser.print_help()
    print("\n提示: 使用 --interactive 进入交互式模式")


if __name__ == '__main__':
    main()
