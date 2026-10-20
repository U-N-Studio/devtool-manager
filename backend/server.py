"""DevTool Manager Python RPC backend.

通过 stdio 与 Electron 主进程通信,使用 newline-delimited JSON-RPC 2.0 协议。
复用 main/src/core/ 的业务逻辑,仅在此层做 RPC 适配。
"""

import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor

# main/ 父目录上 sys.path,使 `from src.core... import` 可解析(main/src/__init__.py 即 src 包)
# 开发态: backend/server.py -> ../main (即 main/ 父目录, main/src/__init__.py 即 src 包)
# 冻结态(PyInstaller): --add-data "main/src;src" 将内容放在 <MEIPASS>/src/, 故 sys.path 需 <MEIPASS>
def _resolve_main_parent():
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return meipass
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main"))


_MAIN_PARENT = _resolve_main_parent()
if _MAIN_PARENT not in sys.path:
    sys.path.insert(0, _MAIN_PARENT)

from rpc_handlers import HANDLERS, handle_executor_execute  # noqa: E402


def send_message(msg: dict):
    """向 stdout 写入一条 JSON-RPC 消息。"""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def send_notification(method: str, params: dict):
    send_message({"jsonrpc": "2.0", "method": method, "params": params})


def send_response(req_id, result):
    send_message({"jsonrpc": "2.0", "id": req_id, "result": result})


def send_error(req_id, code: int, message: str):
    send_message({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def handle_request(req, executor_pool: ThreadPoolExecutor):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {}) or {}

    # executor.execute 特殊:接收 notify 回调,立即返回 sessionId
    if method == "executor.execute":
        try:
            send_response(req_id, handle_executor_execute(params, send_notification))
        except Exception as e:
            send_error(req_id, -32603, str(e))
        return

    handler = HANDLERS.get(method)
    if not handler:
        send_error(req_id, -32601, f"Method not found: {method}")
        return

    def _run():
        try:
            send_response(req_id, handler(params))
        except Exception as e:
            send_error(req_id, -32603, str(e))

    # ping / shutdown 同步执行,避免阻塞退出
    if method in ("ping", "shutdown"):
        _run()
    else:
        executor_pool.submit(_run)


def main():
    # 启动通知:告知 Electron 后端已就绪
    send_notification("ready", {})

    pool = ThreadPoolExecutor(max_workers=4)
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError as e:
                send_error("unknown", -32700, f"Parse error: {e}")
                continue
            if "method" in req and "id" in req:
                handle_request(req, pool)
    finally:
        pool.shutdown(wait=False)


if __name__ == "__main__":
    main()
