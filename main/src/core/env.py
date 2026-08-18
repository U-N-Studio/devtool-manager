import sys
import os
import subprocess

from src.utils.python_finder import get_python_executable

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def get_python_version():
    return sys.version


def get_pip_version():
    try:
        py = get_python_executable()
        return subprocess.check_output(
            [py, "-m", "pip", "--version"], text=True, creationflags=_SUBPROCESS_FLAGS
        ).strip()
    except Exception:
        return "N/A"


def get_platform():
    return sys.platform


def get_executable():
    return sys.executable


def get_all_env_vars():
    return dict(os.environ)
