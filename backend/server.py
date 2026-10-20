"""DevTool Manager Python RPC backend.

通过 stdio 与 Electron 主进程通信,使用 newline-delimited JSON-RPC 2.0 协议。
复用 main/src/core/ 的业务逻辑,仅在此层做 RPC 适配。
"""

import sys
import os

_MAIN_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main", "src"))
if _MAIN_SRC not in sys.path:
    sys.path.insert(0, _MAIN_SRC)


def main():
    """RPC 主循环,Task 2 实现。"""
    for line in sys.stdin:
        sys.stdout.write('{"jsonrpc":"2.0","method":"ready","params":{}}\n')
        sys.stdout.flush()
        break


if __name__ == "__main__":
    main()
