"""DevTool Manager 应用主窗口。

使用 overrideredirect 移除原生系统标题栏,自建标题栏(app 标题 + 文件/视图/帮助
菜单 + 最小化/最大化/关闭按钮,支持拖拽移动与双击最大化)。下方为左右分区:
左侧全高导航栏,右侧主区含路径栏与内容区。所有 ViewModel 的加载状态汇总到全局进度遮罩。
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
        self.geometry("760x500")
        self.minsize(560, 360)

        # 移除原生标题栏,改用自定义标题栏
        self.overrideredirect(True)
        self._maximized = False
        self._restore_size = (760, 500)
        self._restore_pos = (0, 0)

        Observable.set_ui_scheduler(self._schedule_on_ui)

        self._env_vm = EnvViewModel()
        self._pkgs_vm = PackagesViewModel()
        self._tool_vm = ToolInfoViewModel()
        self._cmd_vm = CommandsViewModel()
        self._exec_vm = ExecutorViewModel()

        # 布局:顶部自定义标题栏 + 下方左右(导航栏 / 主区)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_titlebar()
        self._build_body()
        self._loading = LoadingOverlay(self)
        self._bind_viewmodels()

        # 居中显示;Windows 下注册任务栏图标
        self.update_idletasks()
        self._center_window()
        if sys.platform == "win32":
            self.after(50, self._setup_taskbar_icon)

        self.after(100, self._on_refresh)

    def _build_titlebar(self):
        """自定义标题栏:左侧菜单,右侧最小化/最大化/关闭按钮,支持拖拽。"""
        bar = ctk.CTkFrame(self, height=32, corner_radius=0,
                           fg_color=("gray80", "gray12"))
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        self._titlebar = bar

        # 左侧:菜单区(留空占位由 weight 撑开)
        menu_frame = ctk.CTkFrame(bar, fg_color="transparent")
        menu_frame.grid(row=0, column=0, padx=(4, 8), sticky="w")

        self._make_menu_button(menu_frame, "文件", [
            ("刷新数据", self._on_refresh),
            ("退出", self.quit),
        ])
        self._make_menu_button(menu_frame, "视图", [
            ("深色模式", lambda: ctk.set_appearance_mode("Dark")),
            ("浅色模式", lambda: ctk.set_appearance_mode("Light")),
            ("跟随系统", lambda: ctk.set_appearance_mode("System")),
        ])
        self._make_menu_button(menu_frame, "帮助", [
            ("关于", self._show_about),
        ])

        # 右侧:窗口控制按钮
        ctrl_frame = ctk.CTkFrame(bar, fg_color="transparent")
        ctrl_frame.grid(row=0, column=2, padx=(0, 0), sticky="e")

        ctk.CTkButton(ctrl_frame, text="—", width=38, height=26, text_color=("black", "white"),
                      fg_color="transparent", hover_color=("gray70", "gray30"),
                      font=_font(size=12), command=self._on_minimize).grid(row=0, column=0)
        self._btn_max = ctk.CTkButton(
            ctrl_frame, text="▢", width=38, height=26, text_color=("black", "white"),
            fg_color="transparent", hover_color=("gray70", "gray30"),
            font=_font(size=11), command=self._on_toggle_maximize)
        self._btn_max.grid(row=0, column=1)
        ctk.CTkButton(ctrl_frame, text="✕", width=38, height=26, text_color=("black", "white"),
                      fg_color="transparent", hover_color="#D9534F",
                      font=_font(size=12), command=self._on_close).grid(row=0, column=2)

        # 拖拽移动:绑定到标题栏空白区与菜单区
        for w in (bar, menu_frame):
            w.bind("<ButtonPress-1>", self._on_drag_start)
            w.bind("<B1-Motion>", self._on_drag_move)
            w.bind("<ButtonRelease-1>", self._on_drag_release)
            w.bind("<Double-Button-1>", lambda e: self._on_toggle_maximize())

    def _make_menu_button(self, parent, label, items):
        """创建一个下拉菜单按钮:点击弹出 tkinter Menu。"""
        import tkinter as tk

        btn = ctk.CTkButton(parent, text=label, width=52, height=26,
                            fg_color="transparent", hover_color=("gray75", "gray25"),
                            font=_font(size=11), anchor="center")
        btn.grid(row=0, column=len(parent.winfo_children()), padx=2)

        menu = tk.Menu(btn, tearoff=0, font=("Microsoft YaHei UI", 11))

        def _open_menu():
            btn.update_idletasks()
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height()
            try:
                menu.tk_popup(x, y)
            finally:
                menu.grab_release()

        for item in items:
            text, cmd = item
            menu.add_command(label=text, command=cmd)
        btn.configure(command=_open_menu)

    def _show_about(self):
        win = ctk.CTkToplevel(self)
        win.title("关于")
        win.geometry("360x160")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        ctk.CTkLabel(win, text="DevTool Manager", font=_font(size=16, weight="bold")).pack(pady=(24, 4))
        ctk.CTkLabel(win, text="开发环境管理工具", font=_font(size=12), text_color="#888").pack(pady=(0, 16))
        ctk.CTkButton(win, text="关闭", width=80, command=win.destroy).pack()

    # --- 自定义标题栏:窗口控制 ---

    def _on_drag_start(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._drag_moved = False

    def _on_drag_move(self, event):
        # 最大化状态下:仅在检测到真实位移时才还原并跟随鼠标,纯单击不还原
        if self._maximized:
            if abs(event.x - self._drag_start_x) < 4 and abs(event.y - self._drag_start_y) < 4:
                return
            self._restore_from_maximize(event)
            self._drag_moved = True
            return
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")

    def _on_drag_release(self, event):
        pass

    def _on_minimize(self):
        self.iconify()

    def _on_toggle_maximize(self):
        if self._maximized:
            self._restore_window()
        else:
            self._maximize_window()

    def _maximize_window(self):
        self._restore_size = (self.winfo_width(), self.winfo_height())
        self._restore_pos = (self.winfo_x(), self.winfo_y())
        x, y, w, h = self._get_work_area()
        self.geometry(f"{w}x{h}+{x}+{y}")
        self._maximized = True
        self._btn_max.configure(text="❐")

    def _restore_window(self):
        w, h = self._restore_size
        x, y = self._restore_pos
        self.geometry(f"{w}x{h}+{x}+{y}")
        self._maximized = False
        self._btn_max.configure(text="▢")

    def _get_work_area(self):
        """返回可用工作区 (x, y, w, h),排除任务栏。"""
        if sys.platform == "win32":
            try:
                import ctypes
                class RECT(ctypes.Structure):
                    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
                rc = RECT()
                # SPI_GETWORKAREA=0x0030,取任务栏之外的工作区
                ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rc), 0)
                return rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top
            except Exception:
                pass
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        return 0, 0, sw, sh

    def _restore_from_maximize(self, event):
        # 还原窗口,并按鼠标在标题栏的相对位置平移,使窗口跟随鼠标
        self._restore_window()
        self.update_idletasks()
        x = self.winfo_pointerx() - event.x
        y = self.winfo_pointery() - event.y
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _center_window(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = self.winfo_width()
        h = self.winfo_height()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 3)
        self.geometry(f"+{x}+{y}")

    def _setup_taskbar_icon(self):
        """Windows 下注册任务栏图标,使 overrideredirect 窗口仍能在任务栏显示。"""
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            # GWL_EXSTYLE=-20; WS_EX_APPWINDOW=0x40000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x40000)
            self.withdraw()
            self.after(10, self.deiconify)
        except Exception:
            pass

    def _on_close(self):
        self.quit()

    def _build_body(self):
        # --- 左侧全高导航栏(web 风格) ---
        sidebar = ctk.CTkFrame(self, width=152, corner_radius=0,
                               fg_color=("gray90", "gray16"))
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(0, weight=0)   # 品牌/分组标题
        sidebar.grid_rowconfigure(1, weight=0)   # 导航项
        sidebar.grid_rowconfigure(2, weight=1)   # 弹性间隔
        sidebar.grid_rowconfigure(3, weight=0)   # 底部状态

        # 顶部小标题
        ctk.CTkLabel(sidebar, text="  导航", anchor="w",
                     font=_font(size=10), text_color=("#888", "#666")).grid(
            row=0, column=0, padx=0, pady=(10, 4), sticky="ew")

        # 导航项容器
        nav_wrap = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_wrap.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        nav_wrap.grid_columnconfigure(0, weight=1)

        # --- 右侧主区:顶栏 + 内容 ---
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=0)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # 顶栏:当前路径
        cwd_bar = ctk.CTkFrame(main, height=24, corner_radius=0,
                               fg_color="#2B2B2B" if ctk.get_appearance_mode() == "Dark" else "#E8E8E8")
        cwd_bar.grid(row=0, column=0, sticky="ew")
        cwd_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cwd_bar, text="当前路径:", font=_font(size=10), anchor="w").grid(
            row=0, column=0, padx=(12, 4), pady=3, sticky="w"
        )
        self._cwd_label = ctk.CTkLabel(cwd_bar, text=os.getcwd(), font=_font(size=10), anchor="w",
                                       text_color="#AAAAAA")
        self._cwd_label.grid(row=0, column=1, padx=(0, 12), pady=3, sticky="ew")

        # 内容容器
        self._content_frame = ctk.CTkFrame(main, corner_radius=6)
        self._content_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(2, 8))
        self._content_frame.grid_columnconfigure(0, weight=1)
        self._content_frame.grid_rowconfigure(0, weight=1)

        tabs = [
            ("Environment", "环境变量", "≡"),
            ("Packages", "包管理", "▤"),
            ("Commands", "命令管理", ">_"),
        ]
        self._tab_buttons = {}
        self._tab_frames = {}
        for i, (key, label, icon) in enumerate(tabs):
            row = self._make_nav_item(nav_wrap, i, icon, label, key)
            self._tab_buttons[key] = row

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

        # 底部状态区
        self._status_label = ctk.CTkLabel(sidebar, text="", anchor="w",
                                          font=_font(size=10), text_color=("#888", "#666"))
        self._status_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

    # --- 侧边栏导航项(web 风格) ---

    _NAV_ACTIVE_BG = ("gray75", "gray28")
    _NAV_ACTIVE_FG = ("black", "white")
    _NAV_IDLE_FG = ("gray30", "gray75")
    _NAV_HOVER_BG = ("gray82", "gray24")

    def _make_nav_item(self, parent, row_idx, icon, label, key):
        """创建一个 web 风格导航项:图标 + 文字按钮,hover/选中态高亮。"""
        btn = ctk.CTkButton(
            parent, text=f"{icon}  {label}", anchor="w", height=34,
            fg_color="transparent",
            hover_color=self._NAV_HOVER_BG,
            text_color=self._NAV_IDLE_FG,
            font=_font(size=12), corner_radius=6,
            command=lambda k=key: self._switch_tab(k),
        )
        btn.grid(row=row_idx, column=0, sticky="ew", padx=6, pady=(2, 0))
        btn._selected = False
        return btn

    def _on_nav_hover(self, widgets, entering):
        """hover 效果:仅当该项未选中时改变背景。"""
        pass  # CTkButton 自带 hover_color,无需手动处理

    def _set_nav_active(self, item, active):
        """切换某个导航项的选中态样式。"""
        if active:
            item._selected = True
            item.configure(fg_color=self._NAV_ACTIVE_BG,
                           hover_color=self._NAV_ACTIVE_BG,
                           text_color=self._NAV_ACTIVE_FG)
        else:
            item._selected = False
            item.configure(fg_color="transparent",
                           hover_color=self._NAV_HOVER_BG,
                           text_color=self._NAV_IDLE_FG)

    def _switch_tab(self, key):
        if self._current_tab == key:
            return
        if self._current_tab:
            self._tab_frames[self._current_tab].grid_remove()
            self._set_nav_active(self._tab_buttons[self._current_tab], False)
        self._tab_frames[key].grid()
        self._set_nav_active(self._tab_buttons[key], True)
        self._current_tab = key
        if hasattr(self, "_status_label"):
            self._status_label.configure(text=f"● {key}")

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
