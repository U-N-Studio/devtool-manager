import sys
import os
import subprocess
import threading

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


class CommandExecutor:
    def __init__(self):
        self._process = None
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def execute(self, command: str, cwd: str = None,
                on_output=None, on_error=None, on_done=None,
                env: dict = None):
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
        if self._process and self._running:
            try:
                self._process.kill()
            except Exception:
                pass

    def _run(self, command: str, cwd: str,
             on_output, on_error, on_done, env: dict):
        try:
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)

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
                    for line in iter(stream.readline, ""):
                        if callback:
                            callback(line)
                except ValueError:
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
