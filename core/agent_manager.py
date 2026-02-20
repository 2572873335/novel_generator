"""
智能体管理器
负责调度和协调各个专业智能体
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class AgentManager:
    """智能体管理器 - 协调多个专业智能体"""

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.agents_dir = Path(__file__).parent
        self.active_agents = []
        self.project_context = {}

    def load_agent_prompt(self, agent_name: str) -> str:
        """加载智能体提示词"""
        prompt_file = self.agents_dir / f"{agent_name}.md"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def get_available_agents(self) -> List[Dict[str, str]]:
        """获取所有可用的智能体"""
        agents = []
        agent_files = [
            "Coordinator.md",
            "WorldBuilder.md",
            "CharacterDesigner.md",
            "PlotArchitect.md",
            "OutlineArchitect.md",
            "SceneWriter.md",
            "Editor.md",
            "VolumeArchitect.md",
            "ChapterArchitect.md",
            "CultivationDesigner.md",
            "CurrencyExpert.md",
            "GeopoliticsExpert.md",
            "SocietyExpert.md",
        ]

        for filename in agent_files:
            filepath = self.agents_dir / filename
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 解析 YAML front matter
                    name = filename.replace(".md", "")
                    description = ""

                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            front_matter = parts[1]
                            for line in front_matter.split("\n"):
                                if line.startswith("description:"):
                                    description = line.split(":", 1)[1].strip()

                    agents.append(
                        {"name": name, "file": filename, "description": description}
                    )

        return agents

    def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定智能体"""
        prompt = self.load_agent_prompt(agent_name)

        # 这里应该调用真实的 LLM API
        # 目前使用模拟实现
        result = self._mock_execute(agent_name, context)

        return {
            "agent": agent_name,
            "success": True,
            "result": result,
            "context": context,
        }

    def _mock_execute(self, agent_name: str, context: Dict) -> str:
        """模拟执行智能体（实际应调用LLM）"""
        return f"【{agent_name}】已处理请求，生成了相关内容。\n\n上下文: {json.dumps(context, ensure_ascii=False, indent=2)}"

    def run_coordinator_workflow(self, novel_config: Dict[str, Any]) -> Dict[str, Any]:
        """运行协调者工作流 - 全流程自动化"""
        workflow_steps = [
            {
                "name": "项目初始化",
                "agent": "Coordinator",
                "action": "initialize_project",
                "description": "创建项目结构，分析需求",
            },
            {
                "name": "世界观构建",
                "agent": "WorldBuilder",
                "action": "build_world",
                "description": "构建完整的世界设定",
            },
            {
                "name": "人物设计",
                "agent": "CharacterDesigner",
                "action": "design_characters",
                "description": "设计主要角色档案",
            },
            {
                "name": "剧情架构",
                "agent": "PlotArchitect",
                "action": "create_plot",
                "description": "生成完整大纲和卷纲",
            },
            {
                "name": "正文创作",
                "agent": "SceneWriter",
                "action": "write_chapters",
                "description": "撰写各章节正文",
            },
            {
                "name": "编辑润色",
                "agent": "Editor",
                "action": "edit_manuscript",
                "description": "全文质量把控",
            },
        ]

        results = []
        for step in workflow_steps:
            print(f"\n{'=' * 60}")
            print(f"步骤: {step['name']}")
            print(f"智能体: {step['agent']}")
            print(f"描述: {step['description']}")
            print("=" * 60)

            # 执行步骤
            result = self.execute_agent(
                step["agent"],
                {"step": step, "config": novel_config, "previous_results": results},
            )

            results.append({"step": step["name"], "result": result})

            # 模拟耗时操作
            import time

            time.sleep(0.5)

        return {
            "success": True,
            "total_steps": len(workflow_steps),
            "completed_steps": len(results),
            "results": results,
        }

    def create_agent_workflow(
        self, selected_agents: List[str], context: Dict[str, Any]
    ) -> List[Dict]:
        """创建自定义智能体工作流"""
        workflow = []

        for idx, agent_name in enumerate(selected_agents):
            workflow.append(
                {
                    "order": idx + 1,
                    "agent": agent_name,
                    "depends_on": selected_agents[idx - 1] if idx > 0 else None,
                    "context": context,
                }
            )

        return workflow

    def execute_workflow(self, workflow: List[Dict]) -> Dict[str, Any]:
        """执行自定义工作流"""
        results = []

        for step in workflow:
            print(f"\n执行步骤 {step['order']}: {step['agent']}")

            result = self.execute_agent(step["agent"], step["context"])
            results.append(result)

        return {"success": True, "total_steps": len(workflow), "results": results}
