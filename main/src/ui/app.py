import os
import customtkinter as ctk

from src.viewmodel.observable import Observable
from src.viewmodel.env_viewmodel import EnvViewModel
from src.viewmodel.packages_viewmodel import PackagesViewModel
from src.viewmodel.tool_info_viewmodel import ToolInfoViewModel
from src.viewmodel.commands_viewmodel import CommandsViewModel
from src.ui.fonts import font as _font
from src.ui.env_tab import EnvTab
from src.ui.packages_tab import PackagesTab
from src.ui.commands_tab import CommandsTab
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

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_body()
        self._bind_viewmodels()

        self.after(100, self._on_refresh)

    def _build_header(self):
        header = ctk.CTkFrame(self, height=48, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="DevTool Manager", font=_font(size=20, weight="bold")).grid(
            row=0, column=0, padx=(16, 8), pady=10
        )

        self._btn_refresh = ctk.CTkButton(header, text="刷新", width=90, command=self._on_refresh)
        self._btn_refresh.grid(row=0, column=1, sticky="e", padx=(0, 16), pady=10)

        cwd_bar = ctk.CTkFrame(self, height=28, corner_radius=0,
                                fg_color="#2B2B2B" if ctk.get_appearance_mode() == "Dark" else "#E8E8E8")
        cwd_bar.grid(row=1, column=0, sticky="ew")
        cwd_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cwd_bar, text="当前路径:", font=_font(size=11), anchor="w").grid(
            row=0, column=0, padx=(16, 4), pady=4, sticky="w"
        )
        self._cwd_label = ctk.CTkLabel(cwd_bar, text=os.getcwd(), font=_font(size=11), anchor="w",
                                        text_color="#AAAAAA")
        self._cwd_label.grid(row=0, column=1, padx=(0, 16), pady=4, sticky="ew")

    def _build_body(self):
        body = ctk.CTkTabview(self)
        body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self._env_tab = EnvTab(body.add("Environment"), self._env_vm, self._tool_vm)
        self._pkgs_tab = PackagesTab(body.add("Packages"), self._pkgs_vm)
        self._cmd_tab = CommandsTab(body.add("Commands"), self._cmd_vm)

    def _bind_viewmodels(self):
        self._env_vm.is_loading.on_change(self._on_loading_changed)
        self._env_tab.bind_viewmodels()
        self._pkgs_tab.bind_viewmodels()
        self._cmd_tab.bind_viewmodels()

    def _on_loading_changed(self, loading):
        state = "disabled" if loading else "normal"
        self._btn_refresh.configure(state=state)
        self._env_tab.btn_add.configure(state=state)

    def _on_refresh(self):
        self._env_vm.refresh()
        self._pkgs_vm.refresh()
        self._cmd_vm.refresh()
        cat = self._env_tab.cat_combobox.get()
        if cat in TOOL_INFO_FUNCS:
            self._tool_vm.refresh(cat)

    def _schedule_on_ui(self, callback: callable):
        self.after(0, callback)
