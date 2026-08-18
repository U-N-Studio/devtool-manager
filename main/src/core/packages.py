import sys
import json
import subprocess

from src.utils.python_finder import get_python_executable

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def get_installed_packages():
    try:
        py = get_python_executable()
        output = subprocess.check_output(
            [py, "-m", "pip", "list", "--format=json"], text=True, creationflags=_SUBPROCESS_FLAGS
        )
        return json.loads(output)
    except Exception:
        return []


def install_package(name):
    try:
        py = get_python_executable()
        result = subprocess.run(
            [py, "-m", "pip", "install", name],
            capture_output=True, text=True, creationflags=_SUBPROCESS_FLAGS,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def uninstall_package(name):
    try:
        py = get_python_executable()
        result = subprocess.run(
            [py, "-m", "pip", "uninstall", "-y", name],
            capture_output=True, text=True, creationflags=_SUBPROCESS_FLAGS,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)
