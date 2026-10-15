"""DevTool Manager 源码包。

按 MVVM 分层组织:
- :mod:`src.core`       — 业务核心(环境变量 / 包管理 / 命令 / 工具探测 / 进程执行)
- :mod:`src.viewmodel`  — 视图模型,连接 core 与 ui
- :mod:`src.ui`         — customtkinter 桌面 UI
- :mod:`src.utils`      — 跨层工具(日志 / Python 解释器定位)
"""

from src.core.env import get_python_version, get_pip_version, get_platform, get_executable, get_all_env_vars
from src.core.packages import get_installed_packages, install_package, uninstall_package
