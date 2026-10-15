"""核心业务层。

封装与 UI 无关的纯逻辑:环境变量读写、包管理、命令定义与探测、
工具链信息采集、子进程执行。UI 层不直接调用本层,而由 viewmodel 转发。
"""

from src.core.env import get_python_version, get_pip_version, get_all_env_vars
from src.core.packages import get_installed_packages

__all__ = ["get_python_version", "get_pip_version", "get_all_env_vars", "get_installed_packages"]
