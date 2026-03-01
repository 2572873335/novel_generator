"""
tools/ui_cli.py - CLI 远程控制 NovelForge UI
用法:
  python tools/ui_cli.py switch_view production
  python tools/ui_cli.py fill_text edit_title "我的小说"
  python tools/ui_cli.py fill_text edit_outline "大纲内容"
  python tools/ui_cli.py click_button btn_golden_check
  python tools/ui_cli.py click_button btn_start
  python tools/ui_cli.py notify "Hello from CLI"

注意: fill_text 和 click_button 的 target 参数是 UI 元素的具体变量名
"""
import socket
import json
import argparse
import sys


def send_command(cmd: dict, host="127.0.0.1", port=9999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(json.dumps(cmd).encode("utf-8"))
        resp = sock.recv(4096).decode("utf-8")
        print(resp)
    finally:
        sock.close()


def main():
    p = argparse.ArgumentParser(description="NovelForge UI 远程控制")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9999)
    sub = p.add_subparsers(dest="action", required=True)

    sw = sub.add_parser("switch_view")
    # 移除 choices 限制，接受任意视图名称
    sw.add_argument("target", help="视图名称 (preprod, production, vault, market)")

    ft = sub.add_parser("fill_text")
    # 移除 choices 限制，接受任意目标名称
    ft.add_argument("target", help="UI元素的变量名 (如 edit_title, edit_outline, edit_genre)")
    ft.add_argument("content", help="要填充的文本内容")

    cb = sub.add_parser("click_button")
    # 移除 choices 限制，接受任意按钮名称
    cb.add_argument("target", help="按钮的变量名 (如 btn_golden_check, btn_start)")

    nt = sub.add_parser("notify")
    nt.add_argument("message")

    args = p.parse_args()
    if args.action == "switch_view":
        cmd = {"action": "switch_view", "target": args.target}
    elif args.action == "fill_text":
        cmd = {"action": "fill_text", "target": args.target,
               "content": args.content}
    elif args.action == "click_button":
        cmd = {"action": "click_button", "target": args.target}
    elif args.action == "notify":
        cmd = {"action": "show_notification", "message": args.message}
    else:
        p.print_help()
        sys.exit(1)

    send_command(cmd, args.host, args.port)


if __name__ == "__main__":
    main()
