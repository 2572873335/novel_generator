"""
ui/ui_controller.py - AI 控制 UI 的桥梁引擎 + IPC 远程控制服务
支持动态 UI 反射：通过变量名自动查找并操作 UI 元素
"""
import socket
import json
import logging
from PyQt6.QtCore import QObject, QTimer, QThread, pyqtSignal

logger = logging.getLogger(__name__)


class UIDriver(QObject):
    """
    接收并执行来自 AI 的结构化 UI 控制指令
    支持动态反射：根据变量名自动查找 UI 元素
    """
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard

    def _find_ui_element(self, target_name: str):
        """
        动态搜索所有主视图，查找具有给定变量名的 UI 元素

        Args:
            target_name: UI 元素的变量名 (如 edit_title, btn_start)

        Returns:
            UI 元素对象，如果未找到则返回 None
        """
        # 获取所有主视图
        views = [
            self.dashboard.view_preprod,
            self.dashboard.view_prod,
            self.dashboard.view_vault,
            self.dashboard.view_market,
            self.dashboard  # 主窗口本身
        ]

        for view in views:
            if view and hasattr(view, target_name):
                element = getattr(view, target_name)
                logger.debug(f"Found UI element: {target_name} in {view.__class__.__name__}")
                return element

        logger.warning(f"UI element '{target_name}' not found on any view")
        return None

    def _switch_to_view(self, target: str):
        """切换视图"""
        view_map = {
            "preprod": 0,
            "production": 1,
            "vault": 2,
            "market": 3
        }
        index = view_map.get(target, 0)
        self.dashboard.main_stack.setCurrentIndex(index)
        logger.info(f"Switched to view: {target} (index: {index})")

    def execute_commands(self, commands: list):
        """执行命令列表"""
        if not commands:
            return

        for cmd in commands:
            action = cmd.get("action")
            target = cmd.get("target")
            content = cmd.get("content", "")

            logger.debug(f"Executing command: {action}, target: {target}")

            if action == "switch_view":
                self._switch_to_view(target)

            elif action == "fill_text":
                element = self._find_ui_element(target)

                if element is None:
                    logger.error(f"fill_text: Element '{target}' not found")
                    continue

                # 如果目标在 market 视图，先切换到 market 视图
                if hasattr(self.dashboard.view_market, target):
                    current_index = self.dashboard.main_stack.currentIndex()
                    if current_index != 3:  # market 视图索引为 3
                        self.dashboard.main_stack.setCurrentIndex(3)
                        logger.info(f"fill_text: switched to market view for '{target}'")

                # 切换到手动编辑页（如果目标在手动页）
                if hasattr(self.dashboard.view_preprod, 'stack'):
                    # 检查元素是否属于 preprod 视图
                    preprod = self.dashboard.view_preprod
                    if hasattr(preprod, target):
                        preprod.stack.setCurrentIndex(1)

                # 鸭子类型：检查元素类型并调用相应方法
                if hasattr(element, "setText"):  # QLineEdit
                    element.setText(content)
                    logger.info(f"fill_text: setText on '{target}'")
                elif hasattr(element, "setPlainText"):  # QTextEdit / QTextBrowser
                    element.setPlainText(content)
                    logger.info(f"fill_text: setPlainText on '{target}'")
                elif hasattr(element, "setCurrentText"):  # QComboBox
                    # 尝试查找匹配的选项
                    idx = element.findText(content)
                    if idx >= 0:
                        element.setCurrentIndex(idx)
                    else:
                        element.setCurrentText(content)
                    logger.info(f"fill_text: setCurrentText on '{target}'")
                elif hasattr(element, "setHtml"):  # QTextBrowser (HTML)
                    element.setHtml(content)
                    logger.info(f"fill_text: setHtml on '{target}'")
                else:
                    logger.warning(f"fill_text: Element '{target}' doesn't support text filling")

            elif action == "click_button":
                element = self._find_ui_element(target)

                if element is None:
                    logger.error(f"click_button: Element '{target}' not found")
                    continue

                # 特殊处理 btn_create_skill：直接调用方法，避免 QTimer 延迟问题
                if target == "btn_create_skill":
                    # 查找 SkillMarketView 并直接调用创建方法
                    market_view = self.dashboard.view_market
                    if hasattr(market_view, '_on_create_skill_from_input'):
                        logger.info(f"click_button: calling _on_create_skill_from_input")
                        market_view._on_create_skill_from_input()
                    continue

                if hasattr(element, "click"):
                    # 使用 QTimer 延迟点击，确保 UI 完全加载
                    QTimer.singleShot(100, element.click)
                    logger.info(f"click_button: clicked '{target}'")
                else:
                    logger.warning(f"click_button: Element '{target}' is not clickable")

            elif action == "show_notification":
                msg = content or cmd.get("message", "")
                self.dashboard.global_status_bar.update_status(
                    f"🤖 AI: {msg}", "info"
                )
                logger.info(f"show_notification: {msg}")


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
