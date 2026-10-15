"""DevTool Manager 应用主窗口。

网页式左右布局:左侧全高导航栏,右侧主区(顶部路径栏 + 内容区)。
初始化各标签页及其 ViewModel,并将所有 ViewModel 的加载状态汇总到全局进度遮罩。
"""

import os
import sys
import customtkinter as ctk

# Windows 高 DPI 感知:在 Tk 创建前调用,避免位图拉伸发虚
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PER_MONITOR_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from src.viewmodel.observable import Observable
from src.viewmodel.env_viewmodel import EnvViewModel
from src.viewmodel.packages_viewmodel import PackagesViewModel
from src.viewmodel.tool_info_viewmodel import ToolInfoViewModel
from src.viewmodel.commands_viewmodel import CommandsViewModel
from src.viewmodel.executor_viewmodel import ExecutorViewModel
from src.ui.fonts import font as _font
from src.ui.env_tab import EnvTab
from src.ui.packages_tab import PackagesTab
from src.ui.commands_tab import CommandsTab
from src.ui.execute_tab import ExecuteTab
from src.ui.loading_overlay import LoadingOverlay
from src.core.tools import TOOL_INFO_FUNCS


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class DevToolManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DevTool Manager")
        self.geometry("900x580")
        self.minsize(700, 420)

        Observable.set_ui_scheduler(self._schedule_on_ui)

        self._env_vm = EnvViewModel()
        self._pkgs_vm = PackagesViewModel()
        self._tool_vm = ToolInfoViewModel()
        self._cmd_vm = CommandsViewModel()
        self._exec_vm = ExecutorViewModel()

        # 网页式左右布局:左侧全高导航栏 + 右侧主区(顶栏 + 内容)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_body()
        self._loading = LoadingOverlay(self)
        self._bind_viewmodels()

        self.after(100, self._on_refresh)

    def _build_body(self):
        # --- 左侧全高导航栏 ---
        sidebar = ctk.CTkFrame(self, width=160, corner_radius=0,
                               fg_color=("gray88", "gray18"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)

        # --- 右侧主区:顶栏 + 内容 ---
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=0)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # 顶栏:当前路径
        cwd_bar = ctk.CTkFrame(main, height=28, corner_radius=0,
                               fg_color="#2B2B2B" if ctk.get_appearance_mode() == "Dark" else "#E8E8E8")
        cwd_bar.grid(row=0, column=0, sticky="ew")
        cwd_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cwd_bar, text="当前路径:", font=_font(size=11), anchor="w").grid(
            row=0, column=0, padx=(16, 4), pady=4, sticky="w"
        )
        self._cwd_label = ctk.CTkLabel(cwd_bar, text=os.getcwd(), font=_font(size=11), anchor="w",
                                       text_color="#AAAAAA")
        self._cwd_label.grid(row=0, column=1, padx=(0, 16), pady=4, sticky="ew")

        # 内容容器
        self._content_frame = ctk.CTkFrame(main, corner_radius=6)
        self._content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 10))
        self._content_frame.grid_columnconfigure(0, weight=1)
        self._content_frame.grid_rowconfigure(0, weight=1)

        tabs = [
            ("Environment", "环境变量"),
            ("Packages", "包管理"),
            ("Commands", "命令管理"),
        ]
        self._tab_buttons = {}
        self._tab_frames = {}
        for i, (key, label) in enumerate(tabs):
            btn = ctk.CTkButton(sidebar, text=label, anchor="w", height=36,
                                fg_color="transparent", hover_color=("gray80", "gray25"),
                                font=_font(size=13),
                                command=lambda k=key: self._switch_tab(k))
            btn.grid(row=i, column=0, sticky="ew", padx=4, pady=(4, 0))
            self._tab_buttons[key] = btn

            frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
            frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_remove()
            self._tab_frames[key] = frame

        self._env_tab = EnvTab(self._tab_frames["Environment"], self._env_vm, self._tool_vm)
        self._pkgs_tab = PackagesTab(self._tab_frames["Packages"], self._pkgs_vm)

        # 命令管理:内部用子标签整合命令详情 / 执行
        cmd_frame = self._tab_frames["Commands"]
        # 收紧 CTkTabview 默认间距,消除顶部多余空白
        ctk.CTkTabview._outer_spacing = 2
        ctk.CTkTabview._outer_button_overhang = 2
        ctk.CTkTabview._button_height = 24
        cmd_sub = ctk.CTkTabview(cmd_frame)
        cmd_sub.grid(row=0, column=0, sticky="nsew")
        cmd_sub.grid_columnconfigure(0, weight=1)

        self._cmd_tab = CommandsTab(cmd_sub.add("命令详情"), self._cmd_vm)
        self._exec_tab = ExecuteTab(cmd_sub.add("执行"), self._exec_vm)

        self._current_tab = None
        self._switch_tab("Environment")

    def _switch_tab(self, key):
        if self._current_tab == key:
            return
        if self._current_tab:
            self._tab_frames[self._current_tab].grid_remove()
            self._tab_buttons[self._current_tab].configure(
                fg_color="transparent",
                text_color=("black", "white"))
        self._tab_frames[key].grid()
        self._tab_buttons[key].configure(
            fg_color=("gray70", "gray30"),
            text_color="white")
        self._current_tab = key

    def _bind_viewmodels(self):
        self._env_vm.is_loading.on_change(self._on_loading_changed)
        self._env_tab.bind_viewmodels()
        self._pkgs_tab.bind_viewmodels()
        self._cmd_tab.bind_viewmodels()
        self._exec_tab.bind_viewmodels()

        # 所有 viewmodel 的 is_loading 驱动全局进度框
        self._env_vm.is_loading.on_change(lambda v: self._on_global_loading("环境", v))
        self._pkgs_vm.is_loading.on_change(lambda v: self._on_global_loading("包管理", v))
        self._tool_vm.is_loading.on_change(lambda v: self._on_global_loading("工具信息", v))
        self._cmd_vm.is_loading.on_change(lambda v: self._on_global_loading("命令", v))
        self._exec_vm.is_running.on_change(lambda v: self._on_global_loading("执行", v))

    def _on_global_loading(self, tag, loading):
        if loading:
            self._loading.show(f"{tag} 加载中...")
        else:
            self._loading.hide()

    def _on_loading_changed(self, loading):
        state = "disabled" if loading else "normal"
        self._env_tab.btn_add.configure(state=state)

    def _on_refresh(self):
        self._env_vm.refresh()
        self._cmd_vm.refresh()
        cat = self._env_tab.cat_combobox.get()
        if cat in TOOL_INFO_FUNCS:
            self._tool_vm.refresh(cat)

    def _schedule_on_ui(self, callback: callable):
        self.after(0, callback)
