"""
ui/ui_controller.py - AI 控制 UI 的桥梁引擎
"""
from PyQt6.QtCore import QObject, QTimer


class UIDriver(QObject):
    """
    接收并执行来自 AI 的结构化 UI 控制指令
    """
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard

    def execute_commands(self, commands: list):
        if not commands:
            return
        for cmd in commands:
            action = cmd.get("action")
            target = cmd.get("target")

            if action == "switch_view":
                if target == "preprod":
                    self.dashboard.main_stack.setCurrentIndex(0)
                elif target == "production":
                    self.dashboard.main_stack.setCurrentIndex(1)
                elif target == "vault":
                    self.dashboard.main_stack.setCurrentIndex(2)

            elif action == "fill_text":
                content = cmd.get("content", "")
                view = self.dashboard.view_preprod
                if target == "title":
                    view.edit_title.setText(content)
                elif target == "outline":
                    view.edit_outline.setText(content)
                elif target == "characters":
                    view.edit_chars.setText(content)

            elif action == "click_button":
                view = self.dashboard.view_preprod
                if target == "evaluate_settings":
                    QTimer.singleShot(500, view.btn_evaluate.click)
                elif target == "generate_settings":
                    view.btn_generate.click()
                elif target == "start_writing":
                    QTimer.singleShot(500, view.btn_start.click)

            elif action == "show_notification":
                msg = cmd.get("message", "")
                self.dashboard.global_status_bar.update_status(
                    f"🤖 AI: {msg}", "info"
                )
