#!/usr/bin/env python3
"""初始化项目"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, ".")

from agents.initializer_agent import InitializerAgent
from core.model_manager import create_model_manager

# 初始化LLM客户端
model_mgr = create_model_manager()
llm_client = model_mgr

config = {
    "title": "修复验证_修仙测试",
    "genre": "xianxia",
    "target_chapters": 20,
    "words_per_chapter": 3000,
    "description": "用于验证修复效果的修仙小说"
}

agent = InitializerAgent(llm_client, "novels/修复验证_修仙测试")
result = agent.initialize_project(config)

print("\n初始化结果:")
for f in result.get("files_created", []):
    print(f"  - {f}")

# 检查生成的文件
import os
import json

print("\n检查关键文件:")

# 检查world-rules.json
wr_path = "novels/修复验证_修仙测试/world-rules.json"
if os.path.exists(wr_path):
    with open(wr_path, "r", encoding="utf-8") as f:
        wr = json.load(f)
    print(f"  world-rules.json: OK")
    print(f"    - world_type: {wr.get('world_type')}")
    print(f"    - has_cultivation: {wr.get('has_cultivation')}")
    print(f"    - protagonist_name: {wr.get('protagonist_name')}")
    print(f"    - realm_hierarchy: {wr.get('realm_hierarchy')}")
else:
    print(f"  world-rules.json: MISSING!")

# 检查writing_constraints.json
wc_path = "novels/修复验证_修仙测试/writing_constraints.json"
if os.path.exists(wc_path):
    with open(wc_path, "r", encoding="utf-8") as f:
        wc = json.load(f)
    print(f"  writing_constraints.json: OK")
    print(f"    - locked_names: {wc.get('locked_names')}")
    print(f"    - realm_hierarchy: {wc.get('realm_hierarchy')}")
else:
    print(f"  writing_constraints.json: 稍后生成（首次使用时）")

# 检查characters.json
ch_path = "novels/修复验证_修仙测试/characters.json"
if os.path.exists(ch_path):
    with open(ch_path, "r", encoding="utf-8") as f:
        ch = json.load(f)
    print(f"  characters.json: OK")
    print(f"    - {ch}")
