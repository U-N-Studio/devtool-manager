"""桌面 UI 层。

基于 customtkinter 实现主窗口与各功能标签页(环境变量 / 包管理 / 命令管理 / 执行)。
UI 控件不直接访问 core,而是绑定对应 ViewModel 的 Observable 属性。
"""

from src.ui.app import DevToolManagerApp

__all__ = ["DevToolManagerApp"]
