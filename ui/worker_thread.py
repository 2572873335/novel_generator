"""
Worker Thread - 后台工作线程 v5.0 (支持流式文本输出)
"""
import sys
import json
import re
import threading
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal

# 导入领域模型
try:
    from core.project_context import NovelProject
except ImportError:
    from core.project_context import NovelProject
# import openai  # 假设你用的是 OpenAI/DeepSeek 的官方库

class PreProdWorker(QThread):
    """前期筹备专用线程（生成大纲、人物、评估）"""
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, project_dir: str, action: str, data: dict = None):
        super().__init__()
        self.project_dir = project_dir
        self.action = action  # "generate" 或 "evaluate"
        self.data = data or {}

    def run(self):
        import time
        # 模拟大模型思考时间（这里后续可接入你的 InitializerAgent 和 SeniorEditor）
        time.sleep(2) 
        
        if self.action == "generate":
            result = {
                "outline": "# 故事大纲\n\n## 核心冲突\n这是由AI自动生成的初始大纲，请制片人进行修改完善。",
                "characters": '{\n  "characters": [\n    {\n      "name": "主角",\n      "role": "天命之子"\n    }\n  ]\n}',
                "rules": "1. 严禁出现魔法\n2. 遵循黑暗森林法则"
            }
        else: # evaluate
            result = {
                "evaluation": "<h3 style='color:#F44336;'>⚠️ 资深编辑毒舌诊断</h3><p>当前大纲前三章缺少核心爆点，建议在第二章加入直接的生死危机！人物设定过于扁平。</p>"
            }
        self.finished_signal.emit(result)

class GenerationWorker(QThread):
    # --- 核心信号定义 ---
    log_signal = pyqtSignal(str)  
    agent_status_signal = pyqtSignal(dict)  
    emotion_curve_signal = pyqtSignal(dict)  
    circuit_breaker_signal = pyqtSignal(dict)  
    chapter_complete_signal = pyqtSignal(dict)  
    error_signal = pyqtSignal(str)  
    progress_signal = pyqtSignal(int, int)  
    
    # 🔥 新增：流式文本输出信号（用于中间大屏的打字机效果）
    text_stream_signal = pyqtSignal(str)

    def __init__(self, project_dir: str, config: Dict[str, Any]):
        super().__init__()
        self.project_dir = project_dir
        self.config = config
        self.orchestrator = None
        self.is_running = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # 初始状态：未暂停，允许运行

    def run(self):
        self.is_running = True
        try:
            self._initialize_orchestrator()
            self._run_generation()
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")
        finally:
            self.is_running = False

    def _initialize_orchestrator(self):
        from core.orchestrator import create_orchestrator
        self.log_signal.emit("<span style='color: #00f5f5;'>[System] 初始化 IDE 调度总线...</span>")

        # 使用 NovelProject 加载配置
        project = NovelProject(self.project_dir)
        project_config = project.load_config()

        orch_config = {
            "project_dir": self.project_dir,
            "target_chapters": self.config.get("target_chapters", 50),
            "checkpoint_interval": self.config.get("checkpoint_interval", 5),
            "title": project_config.get("title", "未命名小说"),
            "genre": project_config.get("genre", "通用"),
            "protagonist": project_config.get("protagonist", ""),
        }

        self.orchestrator = create_orchestrator(orch_config)
        self.orchestrator.pause_event = self.pause_event  # 注入暂停事件
        self.orchestrator.on_chapter_complete = self._on_chapter_complete
        self.orchestrator.on_error = self._on_error
        self.orchestrator.on_suspended = self._on_suspended
        
        # 🔥 将打字机信号注入给后端
        self.orchestrator.on_text_stream = lambda text: self.text_stream_signal.emit(text)
        self.orchestrator.on_agent_status = lambda data: self.agent_status_signal.emit(data)

    def _run_generation(self):
        start_chapter = self.config.get("start_chapter", 1)
        self.orchestrator.run(start_chapter=start_chapter)

    def _on_chapter_complete(self, result: Dict[str, Any]):
        chapter = result.get("chapter", 0)
        word_count = len(result.get("content", ""))
        self.chapter_complete_signal.emit({"chapter": chapter, "word_count": word_count})
        self.progress_signal.emit(chapter, self.orchestrator.target_chapters)
        self._emit_emotion_curve(chapter)
        self.log_signal.emit(f"<span style='color: #00e676;'>[Success] 第 {chapter} 章生成完毕 ({word_count} 字)</span>")

    def _on_error(self, error: Dict[str, Any]):
        self.error_signal.emit(error.get("error", "Unknown error"))

    def _on_suspended(self, data: Dict[str, Any]):
        self.circuit_breaker_signal.emit({"tripped": True, "chapter": data.get("chapter", 0), "reason": data.get("reason", "Unknown")})

    def _emit_emotion_curve(self, chapter: int):
        import math
        expected = [50 + 30 * math.sin(i / 3) for i in range(1, chapter + 1)]

        # 使用 NovelProject 加载情绪账本
        project = NovelProject(self.project_dir)
        ledger = project.load_emotion_ledger()
        records = ledger.get("records", [])
        actual = [r.get("net_debt", 0) for r in records]

        self.emotion_curve_signal.emit({"expected": expected, "actual": actual, "chapter": chapter})

    def stop(self):
        if self.orchestrator: self.orchestrator.stop()
        self.is_running = False
        self.pause_event.set()  # 解除阻塞，让线程能正常退出

    def pause(self):
        """暂停生成（阻塞 orchestrator 主循环）"""
        self.pause_event.clear()
        if self.orchestrator:
            self.orchestrator.pause_event = self.pause_event

    def resume(self):
        """恢复生成"""
        self.pause_event.set()
        if self.orchestrator:
            self.orchestrator.pause_event = self.pause_event




class AgenticChatWorker(QThread):
    """真实 AI 对话线程 - 调用 LLM API 并解析 JSON 指令"""
    chat_reply_signal = pyqtSignal(str)
    ui_command_signal = pyqtSignal(list)

    def __init__(self, user_text: str, history: list):
        super().__init__()
        self.user_text = user_text
        self.history = history

    def run(self):
        try:
            from core.model_manager import create_model_manager
            mm = create_model_manager()

            system_prompt = """你是一个名为NovelForge的AI资深网文责编。你的任务是引导用户构建小说设定。
你还可以控制用户的本地UI界面！当用户确认了某些设定时，请在JSON的 ui_commands 数组中下达指令。
支持的指令(action):
1. switch_view (target: preprod, production, vault)
2. fill_text (target: title, outline, characters. content: "具体文本")
3. click_button (target: evaluate_settings)

【致命格式要求 - 必读】
1. 你必须且只能输出纯JSON对象，绝对不能以 ```json 开头！
2. JSON的字符串值内部如果出现双引号，必须严格使用反斜杠转义（例如：\\"天子\\"）。如果不转义，系统将崩溃！
3. 请严格按照以下格式输出：
{
  "reply": "直接对用户说的话...",
  "ui_commands": [{"action": "fill_text", "target": "title", "content": "书名"}]
}"""

            messages = list(self.history)
            messages.append({"role": "user", "content": self.user_text})

            # 调用模型（system_prompt 通过独立参数传递，不混入 messages）
            response_text = mm.chat(messages=messages, system_prompt=system_prompt, temperature=0.7)

            # --- 鲁棒 JSON 提取 ---
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not match:
                # 没找到 JSON 对象，直接把原文当回复
                self.chat_reply_signal.emit(response_text)
                return

            clean_json = match.group(0)

            try:
                data = json.loads(clean_json)
            except json.JSONDecodeError:
                # JSON 仍然畸形（未转义引号等），优雅降级
                self.chat_reply_signal.emit(
                    f"⚠️ <b>[系统提示]</b> AI返回了极其精彩的设定，"
                    f"但因为格式错误未能自动填表，请手动复制：<br><br>{response_text}"
                )
                return

            if "reply" in data:
                self.chat_reply_signal.emit(data["reply"])
            if "ui_commands" in data and data["ui_commands"]:
                self.ui_command_signal.emit(data["ui_commands"])

        except Exception as e:
            self.chat_reply_signal.emit(
                f"<span style='color:red;'>[系统错误] AI调用失败: {str(e)}</span>"
            )


class ToolWorker(QThread):
    """创作工具箱 - 后台调用 LLM 生成创意内容"""
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    PROMPTS = {
        "脑洞生成器": "你是一个网文脑洞大师。请根据以下关键词，生成3个极具反差感和吸量特质的网文脑洞设定。要求包含：核心看点、一句话简介、主角开局设定。",
        "书名生成器": "你是一个起点白金作家。请根据以下关键词，生成10个极具吸引力的网文爆款书名。要求：包含主书名和副标题，符合当前网文市场审美。",
        "金手指生成器": "你是一个网文系统架构师。请根据以下关键词，设计一个独特的外挂/金手指。要求包含：系统名称、核心功能、触发条件、升级路线和隐藏代价。",
        "世界观生成器": "你是一个世界观构建大师。请根据以下关键词，构建一个宏大的小说世界观。包含：力量体系、势力阵营、核心矛盾、特殊资源。",
        "反派生成器": "请根据以下关键词，设计一个极其立体且压迫感极强的核心反派。包含：姓名、明面身份、暗中图谋、悲惨过往（洗白点）、核心能力。",
        "核心冲突提炼": "请根据以下关键词，提炼出小说贯穿始末的3个核心冲突（包括：生存冲突、理念冲突、情感冲突），并给出破局的思路。",
    }

    def __init__(self, tool_name: str, keywords: str):
        super().__init__()
        self.tool_name = tool_name
        self.keywords = keywords

    def run(self):
        try:
            from core.model_manager import create_model_manager
            mm = create_model_manager()
            system_prompt = self.PROMPTS.get(self.tool_name, "你是一个网文创作助手。请根据关键词提供创意。")
            messages = [{"role": "user", "content": f"我的关键词/想法是：{self.keywords}"}]
            response = mm.chat(messages=messages, system_prompt=system_prompt, temperature=0.8)
            self.result_signal.emit(response)
        except Exception as e:
            self.error_signal.emit(f"生成失败: {str(e)}")


class GoldenThreeWorker(QThread):
    """黄金三章评估Worker - 异步调用LLM评估前三章"""
    result_signal = pyqtSignal(str)  # 评估结果HTML
    error_signal = pyqtSignal(str)   # 错误信息

    def __init__(self, project_dir: str):
        super().__init__()
        self.project_dir = project_dir

    def run(self):
        try:
            from pathlib import Path
            from core.model_manager import create_model_manager

            project_path = Path(self.project_dir)
            chapters_dir = project_path / "chapters"

            # 读取前三章内容
            chapters = []
            for i in range(1, 4):
                ch_file = chapters_dir / f"chapter_{i:03d}.md"
                if ch_file.exists():
                    content = ch_file.read_text(encoding="utf-8")
                    # 截取前2000字（避免过长）
                    chapters.append(f"第{i}章:\n{content[:2000]}")

            if len(chapters) < 3:
                self.error_signal.emit("需要至少3章内容才能进行黄金三章评估")
                return

            # 构建评估Prompt
            combined_chapters = "\n\n".join(chapters)

            evaluate_prompt = f"""你是一位拥有8年网文编辑经验的起点金牌编辑「锐评官」。请对以下小说的黄金三章进行专业评估。

请从以下6个维度进行严格评估并给出分数(0-100)和具体改进建议：

1. **开篇切入点**: 开头是否抓住读者？切入点是否吸引人？
2. **金手指出现时机**: 金手指/金手指是否在前三章出现？出现时机是否恰当？
3. **期待感营造**: 是否有悬念/钩子吸引读者往下读？
4. **节奏把控**: 前三章节奏是否明快？是否有拖沓感？
5. **人设讨喜度**: 主角人设是否讨喜？是否有记忆点？
6. **情绪拉扯**: 是否有情绪起伏？爽点/虐点安排是否合理？

小说内容:
{combined_chapters}

请以JSON格式返回评估结果：
{{
    "开篇切入点": {{"分数": XX, "评价": "...", "建议": "..."}},
    "金手指出现时机": {{"分数": XX, "评价": "...", "建议": "..."}},
    "期待感营造": {{"分数": XX, "评价": "...", "建议": "..."}},
    "节奏把控": {{"分数": XX, "评价": "...", "建议": "..."}},
    "人设讨喜度": {{"分数": XX, "评价": "...", "建议": "..."}},
    "情绪拉扯": {{"分数": XX, "评价": "...", "建议": "..."}},
    "综合评级": "S/A/B/C/D",
    "总体建议": "..."
}}"""

            mm = create_model_manager()
            result = mm.generate(
                prompt=evaluate_prompt,
                temperature=0.7,
                system_prompt="你是一位资深网文编辑，擅长评估网文开头质量。请严格评估并给出可操作的改进建议。"
            )

            # 解析JSON结果并转换为HTML
            import re
            import json

            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                diagnosis = json.loads(json_match.group())
                html = self._build_html_report(diagnosis)
                self.result_signal.emit(html)
            else:
                # 无法解析JSON，返回原始结果
                self.result_signal.emit(f"<pre>{result}</pre>")

        except Exception as e:
            self.error_signal.emit(f"评估失败: {str(e)}")

    def _build_html_report(self, diagnosis: dict) -> str:
        """将诊断结果构建为HTML报告"""

        def get_color(score):
            if score >= 80:
                return "#00e676"
            if score >= 60:
                return "#ffb300"
            return "#ff1744"

        def get_emoji(rating):
            if rating == "S":
                return "🌟"
            if rating == "A":
                return "✨"
            if rating == "B":
                return "👍"
            if rating == "C":
                return "⚠️"
            return "❌"

        html = f"""
        <div style='font-family: "Microsoft YaHei", sans-serif; padding: 10px;'>
            <h2 style='color: #00e676; text-align: center;'>
                {get_emoji(diagnosis.get('综合评级', 'B'))} 黄金三章评估 - {diagnosis.get('综合评级', 'B')}级
            </h2>
            <hr style='border-color: #334155;'>
        """

        dimensions = [
            "开篇切入点", "金手指出现时机", "期待感营造",
            "节奏把控", "人设讨喜度", "情绪拉扯"
        ]

        for dim in dimensions:
            data = diagnosis.get(dim, {})
            score = data.get("分数", 0)
            eval_text = data.get("评价", "")
            suggestion = data.get("建议", "")
            color = get_color(score)

            html += f"""
            <div style='margin: 15px 0; padding: 10px; background: #1e293b; border-radius: 8px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: bold; font-size: 16px;'>{dim}</span>
                    <span style='color: {color}; font-size: 24px; font-weight: bold;'>{score}分</span>
                </div>
                <p style='color: #94a3b8; margin: 8px 0;'>{eval_text}</p>
                <p style='color: #38bdf8; margin: 8px 0; font-size: 14px;'>💡 建议: {suggestion}</p>
            </div>
            """

        overall = diagnosis.get("总体建议", "")
        if overall:
            html += f"""
            <div style='margin-top: 20px; padding: 15px; background: #0f172a; border-radius: 8px; border-left: 4px solid #38bdf8;'>
                <h3 style='color: #38bdf8; margin: 0 0 10px 0;'>📋 总体建议</h3>
                <p style='color: #e2e8f0; margin: 0;'>{overall}</p>
            </div>
            """

        html += "</div>"
        return html