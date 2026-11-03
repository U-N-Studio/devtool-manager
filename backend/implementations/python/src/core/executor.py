"""子进程执行器。

以独立线程运行 shell 命令,实时流式回传 stdout/stderr,支持终止进程
与自定义环境变量,供执行标签页使用。
"""

import sys
import os
import subprocess
import threading

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


class CommandExecutor:
    """单命令子进程执行器。

    在独立线程运行 shell 命令,通过回调实时回传 stdout/stderr 行,
    支持中途 kill 与自定义环境变量。
    """

    def __init__(self):
        self._process = None  # 当前子进程句柄
        self._running = False  # 是否有命令正在执行

    @property
    def running(self) -> bool:
        return self._running

    def execute(self, command: str, cwd: str = None,
                on_output=None, on_error=None, on_done=None,
                env: dict = None):
        """启动命令执行。

        - on_output/on_error: 每行 stdout/stderr 的回调
        - on_done: 命令结束时回调,参数为退出码(异常时为 -1)
        - env: 追加到当前进程环境上的额外变量
        """
        if self._running:
            return
        self._running = True
        thread = threading.Thread(
            target=self._run,
            args=(command, cwd, on_output, on_error, on_done, env),
            daemon=True,
        )
        thread.start()

    def kill(self):
        """强制终止正在运行的子进程。"""
        if self._process and self._running:
            try:
                self._process.kill()
            except Exception:
                pass

    def _run(self, command: str, cwd: str,
             on_output, on_error, on_done, env: dict):
        """执行线程主体:启动子进程、并行读两个管道、等待结束。"""
        try:
            # 若传了 env,则复制当前环境并覆盖其中的键
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)

            # shell=True 允许执行带管道/重定向的复合命令
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
                cwd=cwd or os.getcwd(),
                creationflags=_SUBPROCESS_FLAGS,
                env=merged_env,
            )

            def _read_stream(stream, callback):
                try:
                    for line in iter(stream.readline, b""):
                        if not line:
                            break
                        if callback:
                            callback(line)
                except (ValueError, OSError):
                    pass

            t_out = threading.Thread(
                target=_read_stream,
                args=(self._process.stdout, on_output),
                daemon=True,
            )
            t_err = threading.Thread(
                target=_read_stream,
                args=(self._process.stderr, on_error),
                daemon=True,
            )
            t_out.start()
            t_err.start()

            self._process.wait()
            t_out.join(timeout=2)
            t_err.join(timeout=2)

            exit_code = self._process.returncode
            if on_done:
                on_done(exit_code)
        except Exception as e:
            if on_error:
                on_error(f"Error: {e}\n")
            if on_done:
                on_done(-1)
        finally:
            self._running = False
            self._process = None
