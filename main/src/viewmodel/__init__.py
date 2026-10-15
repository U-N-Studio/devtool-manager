"""视图模型层。

为每个 UI 标签页提供专属 ViewModel,在 core 纯逻辑与 ui 控件之间充当中介:
后台线程执行耗时的探测/读写,通过 :class:`Observable` 将结果安全回传 UI 线程。
"""

from src.viewmodel.observable import Observable
from src.viewmodel.env_viewmodel import EnvViewModel
from src.viewmodel.packages_viewmodel import PackagesViewModel
from src.viewmodel.tool_info_viewmodel import ToolInfoViewModel
from src.viewmodel.commands_viewmodel import CommandsViewModel
from src.viewmodel.executor_viewmodel import ExecutorViewModel

__all__ = [
    "Observable",
    "EnvViewModel",
    "PackagesViewModel",
    "ToolInfoViewModel",
    "CommandsViewModel",
    "ExecutorViewModel",
]
