"""Python 解释器定位。

在 PyInstaller 打包环境下(frozen)回退到 PATH 中的 python/python3,
普通运行时直接返回当前解释器路径。
"""

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
