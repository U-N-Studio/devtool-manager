import customtkinter as ctk

from src.ui.fonts import font as _font, mono as _mono


class AdbTab:
    def __init__(self, parent, adb_vm):
        self._vm = adb_vm

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=0)
        parent.grid_rowconfigure(3, weight=1)

        # --- 查询栏 ---
        query_bar = ctk.CTkFrame(parent, fg_color="transparent")
        query_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(2, 2))
        query_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(query_bar, text="包名:", font=_font(size=12)).grid(
            row=0, column=0, padx=(0, 6))
        self._pkg_entry = ctk.CTkEntry(query_bar, height=28)
        self._pkg_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        self._pkg_entry.bind("<Return>", self._on_query)

        self._btn_query = ctk.CTkButton(query_bar, text="查询", width=70, height=28,
                                         command=self._on_query)
        self._btn_query.grid(row=0, column=2, padx=(0, 4))

        self._btn_save = ctk.CTkButton(query_bar, text="记忆", width=70, height=28,
                                        fg_color="#5CB85C", hover_color="#449D44",
                                        command=self._on_save)
        self._btn_save.grid(row=0, column=3, padx=(0, 4))

        self._btn_list = ctk.CTkButton(query_bar, text="设备包列表", width=90, height=28,
                                        fg_color="gray", hover_color="gray",
                                        command=self._on_list_device)
        self._btn_list.grid(row=0, column=4)

        # --- 消息栏 ---
        self._msg_label = ctk.CTkLabel(parent, text="", font=_font(size=11), anchor="w",
                                        text_color="#AAAAAA")
        self._msg_label.grid(row=1, column=0, sticky="ew", padx=10)

        # --- 已保存包名栏 ---
        saved_bar = ctk.CTkFrame(parent, fg_color="transparent")
        saved_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 2))
        saved_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(saved_bar, text="已记忆:", font=_font(size=11),
                     text_color="#AAAAAA").grid(row=0, column=0, padx=(0, 6))
        self._saved_combobox = ctk.CTkComboBox(saved_bar, values=[], height=26,
                                                command=self._on_saved_selected)
        self._saved_combobox.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        self._btn_remove = ctk.CTkButton(saved_bar, text="移除", width=60, height=26,
                                          fg_color="#D9534F", hover_color="#C9302C",
                                          command=self._on_remove_saved)
        self._btn_remove.grid(row=0, column=2)

        # --- 结果区 ---
        self._result_frame = ctk.CTkScrollableFrame(parent)
        self._result_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self._result_frame.grid_columnconfigure(0, weight=1)
        self._result_frame.configure(fg_color="transparent")

    def bind_viewmodels(self):
        self._vm.saved_packages.on_change(self._update_saved)
        self._vm.package_info.on_change(self._update_result)
        self._vm.is_loading.on_change(self._on_loading_changed)
        self._vm.message.on_change(lambda v: self._msg_label.configure(text=v))
        self._vm.device_packages.on_change(self._update_device_packages)

    def _on_loading_changed(self, loading):
        state = "disabled" if loading else "normal"
        self._btn_query.configure(state=state)

    def _on_query(self, event=None):
        self._vm.query_package(self._pkg_entry.get())

    def _on_save(self):
        name = self._pkg_entry.get().strip()
        if name:
            self._vm.save_package(name)

    def _on_remove_saved(self):
        name = self._saved_combobox.get()
        if name:
            self._vm.unsave_package(name)

    def _on_saved_selected(self, value):
        self._pkg_entry.delete(0, "end")
        self._pkg_entry.insert(0, value)

    def _on_list_device(self):
        self._vm.load_device_packages()

    def _update_saved(self, packages):
        if packages:
            self._saved_combobox.configure(values=packages)
            self._saved_combobox.set(packages[0])
        else:
            self._saved_combobox.configure(values=[""])
            self._saved_combobox.set("")

    def _update_device_packages(self, packages):
        """设备包列表渲染到结果区"""
        for child in self._result_frame.winfo_children():
            child.destroy()
        if not packages:
            return

        ctk.CTkLabel(self._result_frame, text=f"设备已安装 {len(packages)} 个包",
                     font=_font(size=13, weight="bold"), anchor="w").grid(
            row=0, column=0, padx=8, pady=(4, 6), sticky="w")

        for i, pkg in enumerate(packages):
            row = ctk.CTkFrame(self._result_frame, fg_color="transparent", height=24)
            row.grid(row=i + 1, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkButton(row, text="查询", width=50, height=22,
                          font=_font(size=10),
                          command=lambda p=pkg: self._query_from_list(p)).grid(
                row=0, column=0, padx=(4, 6))
            ctk.CTkLabel(row, text=pkg, anchor="w", font=_mono(size=11)).grid(
                row=0, column=1, sticky="ew")

    def _query_from_list(self, package_name):
        self._pkg_entry.delete(0, "end")
        self._pkg_entry.insert(0, package_name)
        self._vm.query_package(package_name)

    def _update_result(self, info):
        for child in self._result_frame.winfo_children():
            child.destroy()
        if not info:
            return

        f = self._result_frame
        f.grid_columnconfigure(0, weight=1)
        row = 0

        # 包名标题
        ctk.CTkLabel(f, text=info.get("package", ""), font=_font(size=20, weight="bold"),
                     anchor="w").grid(row=row, column=0, padx=8, pady=(8, 2), sticky="w")
        row += 1

        installed = info.get("installed", False)
        if not installed:
            err = info.get("error", "未安装")
            ctk.CTkLabel(f, text=err, font=_font(size=13),
                         text_color="#FF9800", anchor="w").grid(
                row=row, column=0, padx=8, pady=4, sticky="w")
            return

        ctk.CTkLabel(f, text="已安装", font=_font(size=12, weight="bold"),
                     text_color="#4CAF50", anchor="w").grid(
            row=row, column=0, padx=8, pady=(4, 8), sticky="w")
        row += 1

        versions = info.get("versions", [info])
        multi = info.get("multi_version", False)

        for vi, ver in enumerate(versions):
            is_active = (vi == 0)
            tag = "当前生效" if is_active else ("系统预置" if "/system/" in ver.get("path", "") else "其他版本")

            card = ctk.CTkFrame(f, corner_radius=8)
            card.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            inner = 0

            header_color = "#4CAF50" if is_active else "#FF9800"
            ctk.CTkLabel(card, text=f"  {tag}  ", fg_color=header_color, corner_radius=4,
                         font=_font(size=11, weight="bold"), text_color="white").grid(
                row=inner, column=0, columnspan=2, padx=12, pady=(8, 4), sticky="w")
            inner += 1

            fields = [
                ("版本名称", ver.get("version_name", "") or "N/A"),
                ("版本号", ver.get("version_code", "") or "N/A"),
                ("minSdk", ver.get("min_sdk", "") or "N/A"),
                ("targetSdk", ver.get("target_sdk", "") or "N/A"),
                ("最后更新", ver.get("last_update_time", "") or "N/A"),
                ("安装路径", ver.get("path", "") or "N/A"),
            ]
            for label, value in fields:
                ctk.CTkLabel(card, text=label + ":", anchor="w",
                             font=_font(size=12)).grid(
                    row=inner, column=0, padx=(12, 4), pady=4, sticky="w")
                ctk.CTkLabel(card, text=value, anchor="w", font=_font(size=12),
                             wraplength=600).grid(
                    row=inner, column=1, padx=(0, 12), pady=4, sticky="ew")
                inner += 1

            row += 1

        if multi:
            ctk.CTkLabel(f, text="提示:系统预置版无法直接卸载,"
                                "执行 adb uninstall 可回退到系统版",
                         font=_font(size=11), text_color="#AAAAAA", anchor="w",
                         wraplength=700).grid(
                row=row, column=0, padx=8, pady=(8, 4), sticky="w")
            row += 1
