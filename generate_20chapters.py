#!/usr/bin/env python3
"""生成20章并验证"""
import sys
import io
import json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, ".")

from core.novel_generator import NovelGenerator
from core.writing_constraint_manager import WritingConstraintManager

project_dir = "novels/修复验证_修仙测试"

# 加载配置
config_file = f"{project_dir}/project-config.json"
with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

print("开始生成20章...")
print(f"小说: {config.get('title')}")

# 创建生成器并运行
generator = NovelGenerator(config)
result = generator.run()

print("\n生成完成!")
print(f"状态: {result.get('status')}")
print(f"完成章节: {result.get('completed_chapters')}")

# 验证约束系统
print("\n验证约束系统:")
wcm = WritingConstraintManager(project_dir)
c = wcm.constraints
print(f"  主角名: {c.protagonist_name}")
print(f"  当前境界: {c.current_realm}")
print(f"  境界层级: {c.realm_hierarchy}")
print(f"  locked_names: {c.locked_names}")
