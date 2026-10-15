"""命令执行视图模型。

封装 :class:`CommandExecutor` 的流式输出,维护工作目录、退出码与
输出缓冲(上限 5000 行),驱动执行标签页的输出区与状态栏。
"""

import os

from src.viewmodel.observable import Observable
from src.core.executor import CommandExecutor


class ExecutorViewModel:
    def __init__(self):
        self.output = Observable("")
        self.is_running = Observable(False)
        self.exit_code = Observable(None)
        self.cwd = Observable(os.getcwd())
        self._executor = CommandExecutor()
        self._output_lines = []
        self._max_lines = 5000

    def execute(self, command: str):
        if not command.strip():
            return
        self._output_lines = []
        self.output.set("")
        self.exit_code.set(None)
        self.is_running.set(True)

        self._append_output(f"$ {command}\n")

        self._executor.execute(
            command,
            cwd=self.cwd.value,
            on_output=self._on_output,
            on_error=self._on_error,
            on_done=self._on_done,
        )

    def kill(self):
        self._executor.kill()

    def set_cwd(self, path: str):
        if os.path.isdir(path):
            self.cwd.set(path)

    def clear_output(self):
        self._output_lines = []
        self.output.set("")

    def _append_output(self, text: str):
        self._output_lines.append(text)
        if len(self._output_lines) > self._max_lines:
            self._output_lines = self._output_lines[-self._max_lines:]
        self.output.set("".join(self._output_lines))

    def _on_output(self, line: str):
        self._append_output(line)

    def _on_error(self, line: str):
        self._append_output(line)

    def _on_done(self, exit_code: int):
        self._append_output(f"\nProcess exited with code {exit_code}\n")
        self.exit_code.set(exit_code)
        self.is_running.set(False)
