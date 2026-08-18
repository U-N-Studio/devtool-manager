import sys
import os
import shutil


def get_python_executable():
    if getattr(sys, "frozen", False):
        for name in ("python3", "python"):
            path = shutil.which(name)
            if path:
                return path
        return "python"
    return sys.executable
