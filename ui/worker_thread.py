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