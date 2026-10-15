"""DevTool Manager 启动入口。

实例化主窗口并进入 Tk 事件循环。
"""

from src.ui.app import DevToolManagerApp

if __name__ == "__main__":
    app = DevToolManagerApp()
    app.mainloop()
