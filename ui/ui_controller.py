"""
ui/ui_controller.py - AI 控制 UI 的桥梁引擎 + IPC 远程控制服务
"""
import socket
import json
from PyQt6.QtCore import QObject, QTimer, QThread, pyqtSignal


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
                if hasattr(view, 'stack'):
                    view.stack.setCurrentIndex(1)
                if target == "title":
                    view.edit_title.setText(content)
                elif target == "outline":
                    view.edit_outline.setText(content)
                elif target == "characters":
                    view.edit_chars.setText(content)
                elif target == "genre" and hasattr(view, 'edit_genre'):
                    idx = view.edit_genre.findText(content)
                    if idx >= 0:
                        view.edit_genre.setCurrentIndex(idx)
                    else:
                        view.edit_genre.setCurrentText(content)

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


class UIRemoteServer(QThread):
    """TCP socket 服务器，接收远程 JSON 指令并转发到主线程"""
    command_received = pyqtSignal(list)

    def __init__(self, host="127.0.0.1", port=9999, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self._running = True

    def run(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(1)
        srv.settimeout(1.0)
        print(f"[UIRemoteServer] listening on {self.host}:{self.port}")
        while self._running:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            try:
                data = conn.recv(65536).decode("utf-8")
                if data:
                    commands = json.loads(data)
                    if isinstance(commands, dict):
                        commands = [commands]
                    self.command_received.emit(commands)
                    conn.sendall(b'{"status":"ok"}')
            except Exception as e:
                try:
                    conn.sendall(json.dumps({"status": "error", "msg": str(e)}).encode())
                except OSError:
                    pass
            finally:
                conn.close()
        srv.close()

    def stop(self):
        self._running = False
        self.wait(2000)
