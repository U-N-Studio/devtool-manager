import customtkinter as ctk

from src.ui.fonts import font as _font
from src.core.config_glossary import get_description


class CommandsTab:
    def __init__(self, parent, cmd_vm):
        self._cmd_vm = cmd_vm

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        top_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_bar, text="命令:", font=_font(size=12)).grid(row=0, column=0, padx=(0, 6))
        self._cmd_combobox = ctk.CTkComboBox(top_bar, values=[""], command=self._on_cmd_selected, height=28)
        self._cmd_combobox.grid(row=0, column=1, sticky="ew")

        self._cmd_filter_var = ctk.StringVar(value="全部")
        ctk.CTkSegmentedButton(top_bar, values=["全部", "已安装"], variable=self._cmd_filter_var,
                               command=self._on_cmd_filter).grid(row=0, column=2, padx=(8, 0))

        self._btn_cmd_refresh = ctk.CTkButton(top_bar, text="刷新", width=80, height=28, command=self._on_cmd_refresh)
        self._btn_cmd_refresh.grid(row=0, column=3, padx=(8, 0))

        self._cmd_msg_label = ctk.CTkLabel(top_bar, text="", font=_font(size=11), anchor="w")
        self._cmd_msg_label.grid(row=0, column=4, padx=(8, 0), sticky="w")

        self._cmd_detail_frame = ctk.CTkScrollableFrame(parent)
        self._cmd_detail_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self._cmd_detail_frame.grid_columnconfigure(0, weight=1)

    @property
    def btn_refresh(self):
        return self._btn_cmd_refresh

    def bind_viewmodels(self):
        self._cmd_vm.command_names.on_change(self._update_cmd_names)
        self._cmd_vm.selected_detail.on_change(self._update_cmd_detail)
        self._cmd_vm.is_loading.on_change(self._on_cmd_loading_changed)
        self._cmd_vm.message.on_change(lambda v: self._cmd_msg_label.configure(text=v))

    def _on_cmd_selected(self, name: str):
        self._cmd_vm.select_command(name)

    def _on_cmd_filter(self, value: str):
        self._cmd_vm.set_filter_installed(value == "已安装")

    def _on_cmd_refresh(self):
        self._cmd_vm.refresh()

    def _on_cmd_loading_changed(self, loading):
        state = "disabled" if loading else "normal"
        self._btn_cmd_refresh.configure(state=state)

    def _update_cmd_names(self, names: list):
        if names:
            self._cmd_combobox.configure(values=names)
            self._cmd_combobox.set(names[0])
            self._cmd_vm.select_command(names[0])
        else:
            self._cmd_combobox.configure(values=[""])
            self._cmd_combobox.set("")
            self._clear_cmd_detail()

    def _update_cmd_detail(self, cmd):
        if cmd:
            self._render_cmd_detail(cmd)

    def _clear_cmd_detail(self):
        for child in self._cmd_detail_frame.winfo_children():
            child.destroy()

    def _render_cmd_detail(self, cmd: dict):
        self._clear_cmd_detail()
        f = self._cmd_detail_frame
        f.grid_columnconfigure(0, weight=1)

        row = 0
        ctk.CTkLabel(f, text=cmd["name"], font=_font(size=20, weight="bold")).grid(
            row=row, column=0, padx=8, pady=(8, 2), sticky="w")
        row += 1

        ctk.CTkLabel(f, text=cmd.get("description", ""), font=_font(size=12),
                     text_color="#AAAAAA").grid(row=row, column=0, padx=8, pady=0, sticky="w")
        row += 1

        installed = cmd.get("installed", False)
        status_text = "已安装" if installed else "未安装"
        status_color = "#4CAF50" if installed else "#FF9800"
        ctk.CTkLabel(f, text=status_text, font=_font(size=12, weight="bold"),
                     text_color=status_color).grid(row=row, column=0, padx=8, pady=(4, 8), sticky="w")
        row += 1

        card = ctk.CTkFrame(f, corner_radius=8)
        card.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        inner = 0
        fields = [
            ("版本", cmd.get("version", "") or "N/A"),
            ("路径", cmd.get("path", "") or "N/A"),
        ]
        for label, value in fields:
            ctk.CTkLabel(card, text=label + ":", anchor="w", font=_font(size=12)).grid(
                row=inner, column=0, padx=(12, 4), pady=4, sticky="w")
            ctk.CTkLabel(card, text=value, anchor="w", font=_font(size=12), wraplength=600).grid(
                row=inner, column=1, padx=(0, 12), pady=4, sticky="ew")
            inner += 1
        row += 1

        env_vars = cmd.get("env_vars", [])
        if env_vars:
            card = ctk.CTkFrame(f, corner_radius=8)
            card.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            inner = 0
            ctk.CTkLabel(card, text="环境变量", font=_font(size=13, weight="bold"),
                         text_color="#6BA3D6").grid(row=inner, column=0, columnspan=2, padx=12, pady=(8, 4), sticky="w")
            inner += 1
            for ev in env_vars:
                color = "#4CAF50" if ev["set"] else "#888888"
                ctk.CTkLabel(card, text=ev["name"], anchor="w", font=_font(size=12),
                             width=200).grid(row=inner, column=0, padx=(12, 4), pady=2, sticky="w")
                val = ev["value"] if ev["set"] else "(未设置)"
                ctk.CTkLabel(card, text=val, anchor="w", font=_font(size=12),
                             text_color=color, wraplength=500).grid(row=inner, column=1, padx=(0, 12), pady=2, sticky="ew")
                inner += 1
            row += 1

        params = cmd.get("params", [])
        if params:
            card = ctk.CTkFrame(f, corner_radius=8)
            card.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            inner = 0
            ctk.CTkLabel(card, text="参数列表", font=_font(size=13, weight="bold"),
                         text_color="#6BA3D6").grid(row=inner, column=0, columnspan=2, padx=12, pady=(8, 4), sticky="w")
            inner += 1
            for p in params:
                ctk.CTkLabel(card, text=p["flag"], anchor="w", font=_font(family="Courier", size=12),
                             width=200).grid(row=inner, column=0, padx=(12, 4), pady=2, sticky="w")
                ctk.CTkLabel(card, text=p.get("desc", ""), anchor="w", font=_font(size=12),
                             text_color="#AAAAAA", wraplength=500).grid(row=inner, column=1, padx=(0, 12), pady=2, sticky="ew")
                inner += 1
            row += 1

        config_sections = cmd.get("config_sections", [])
        if config_sections:
            for section in config_sections:
                level = section.get("level", "")
                card = ctk.CTkFrame(f, corner_radius=8)
                card.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
                card.grid_columnconfigure(1, weight=1)
                inner = 0
                ctk.CTkLabel(card, text=f"配置 - {level}", font=_font(size=13, weight="bold"),
                             text_color="#6BA3D6").grid(row=inner, column=0, columnspan=2, padx=12, pady=(8, 4), sticky="w")
                inner += 1
                for item in section.get("items", []):
                    key = item["key"]
                    ctk.CTkLabel(card, text=key, anchor="w", font=_font(size=12),
                                 width=200).grid(row=inner, column=0, padx=(12, 4), pady=1, sticky="w")
                    val = item.get("value", "")
                    if len(val) > 80:
                        val = val[:77] + "..."
                    ctk.CTkLabel(card, text=val, anchor="w", font=_font(size=12),
                                 text_color="#AAAAAA", wraplength=500).grid(row=inner, column=1, padx=(0, 12), pady=1, sticky="ew")
                    inner += 1
                    desc = get_description(key)
                    if desc:
                        ctk.CTkLabel(card, text=desc, anchor="w", font=_font(size=11),
                                     text_color="#666666", wraplength=500).grid(row=inner, column=1, padx=(0, 12), pady=0, sticky="ew")
                        inner += 1
                row += 1
