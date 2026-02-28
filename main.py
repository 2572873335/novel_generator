#!/usr/bin/env python3
"""
NovelForge v5.0 - 统一入口点
=============================
使用 argparse 子命令统一管理 GUI 和 CLI 模式

使用方法:
    python main.py gui                          # 启动 GUI（使用默认项目）
    python main.py gui -p novels/my_project    # 启动 GUI（指定项目）
    python main.py cli -p novels/my_project -c 100  # CLI 模式生成
"""

import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_gui(project_dir: str):
    """启动 PyQt6 GUI"""
    from pathlib import Path
    from ui.main_window import run_dashboard

    # 确保项目目录存在
    Path(project_dir).mkdir(parents=True, exist_ok=True)

    print(f"[GUI] 启动 NovelForge Studio，项目目录: {project_dir}")
    run_dashboard(project_dir)


def run_cli(project_dir: str, chapters: int, batch_size: int = 20):
    """运行无头 CLI 生成模式"""
    from core.novel_generator import create_novel

    # 加载项目配置
    from core.project_context import NovelProject

    project = NovelProject(project_dir)
    config = project.load_config()

    if not config:
        print(f"[ERROR] 项目目录不存在或无配置文件: {project_dir}")
        print("[提示] 请先使用 GUI 创建项目，或使用 --init 初始化")
        return

    # 更新配置
    config['project_dir'] = project_dir
    config['target_chapters'] = chapters
    config['batch_size'] = batch_size

    print(f"[CLI] 开始生成，目标: {chapters} 章")
    print(f"[CLI] 项目: {config.get('title', '未命名')}")

    result = create_novel(config)

    if result['success']:
        print(f"\n[OK] 生成完成！")
        print(f"项目位置: {result['project_dir']}")
    else:
        print(f"\n[FAIL] 生成失败")


def init_project(project_dir: str, title: str, genre: str, chapters: int):
    """初始化新项目"""
    from core.project_context import NovelProject

    project = NovelProject(project_dir)

    config = {
        "title": title,
        "genre": genre,
        "target_chapters": chapters,
        "words_per_chapter": 3000,
        "description": ""
    }

    project.save_config(config)

    # 创建空的大纲和人物文件
    project.save_outline("# 故事大纲\n\n请在此输入大纲内容...")
    project.save_characters('{\n  "characters": []\n}')

    print(f"[OK] 项目已创建: {project_dir}")
    print(f"  标题: {title}")
    print(f"  类型: {genre}")
    print(f"  章节: {chapters}")


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='NovelForge v5.0 - AI 小说生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # GUI 模式
  python main.py gui
  python main.py gui -p novels/my_project

  # CLI 模式
  python main.py cli -p novels/my_project -c 100
  python main.py cli -p novels/my_project -c 50 --batch-size 10

  # 初始化新项目
  python main.py init -t "我的小说" -g 科幻 -n 50
        """
    )

    # 子命令解析器
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ===== GUI 子命令 =====
    gui_parser = subparsers.add_parser("gui", help="启动 PyQt6 Studio")
    gui_parser.add_argument(
        "--project", "-p",
        default="novels/default",
        help="项目目录路径 (默认: novels/default)"
    )

    # ===== CLI 子命令 =====
    cli_parser = subparsers.add_parser("cli", help="运行无头生成模式")
    cli_parser.add_argument(
        "--project", "-p",
        required=True,
        help="项目目录路径"
    )
    cli_parser.add_argument(
        "--chapters", "-c",
        type=int,
        default=10,
        help="目标章节数 (默认: 10)"
    )
    cli_parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=20,
        help="每批次写作章节数 (默认: 20)"
    )

    # ===== Init 子命令 =====
    init_parser = subparsers.add_parser("init", help="初始化新项目")
    init_parser.add_argument(
        "--project", "-p",
        default="novels/default",
        help="项目目录路径"
    )
    init_parser.add_argument(
        "--title", "-t",
        required=True,
        help="小说标题"
    )
    init_parser.add_argument(
        "--genre", "-g",
        default="general",
        help="小说类型 (默认: general)"
    )
    init_parser.add_argument(
        "--chapters", "-n",
        type=int,
        default=50,
        help="目标章节数 (默认: 50)"
    )

    args = parser.parse_args()

    # 分发到对应处理函数
    if args.command == "gui":
        run_gui(args.project)

    elif args.command == "cli":
        run_cli(args.project, args.chapters, args.batch_size)

    elif args.command == "init":
        init_project(args.project, args.title, args.genre, args.chapters)


if __name__ == "__main__":
    main()
