#!/usr/bin/env python3
"""
20章小说生成测试
检测agents工作状态、大纲符合度、前后文一致性
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, '.')

from core.novel_generator import create_novel

# 测试配置
config = {
    'title': '星辰觉醒',
    'genre': '科幻',
    'target_chapters': 20,
    'words_per_chapter': 2000,
    'description': '2157年，人类已经在银河系建立了多个殖民地。年轻的星际飞行员林浩在一次任务中意外发现了一个古老的外星文明遗迹，从此卷入了一场关乎人类命运的星际冒险。他必须面对外星威胁、人类内部的权力斗争，以及自己内心深处的秘密。'
}

print("=" * 70)
print("20章小说生成测试")
print("=" * 70)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"标题: {config['title']}")
print(f"目标章节: {config['target_chapters']}")
print("=" * 70)

# 运行生成
start_time = time.time()
result = create_novel(config)
end_time = time.time()

print()
print("=" * 70)
print("测试完成")
print("=" * 70)
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"耗时: {(end_time - start_time) / 60:.1f} 分钟")

if result['success']:
    print(f"项目目录: {result['project_dir']}")
    
    # 统计分析
    project_dir = result['project_dir']
    
    # 检查一致性报告
    consistency_dir = os.path.join(project_dir, 'consistency_reports')
    if os.path.exists(consistency_dir):
        reports = os.listdir(consistency_dir)
        print(f"一致性检查报告: {len(reports)} 个")
    
    # 检查章节
    chapters_dir = os.path.join(project_dir, 'chapters')
    if os.path.exists(chapters_dir):
        chapters = [f for f in os.listdir(chapters_dir) if f.endswith('.md')]
        print(f"生成章节: {len(chapters)} 章")
        
        # 统计字数
        total_words = 0
        for ch_file in chapters:
            with open(os.path.join(chapters_dir, ch_file), 'r', encoding='utf-8') as f:
                total_words += len(f.read())
        print(f"总字数: {total_words:,}")
else:
    print(f"生成失败: {result.get('error', '未知错误')}")
