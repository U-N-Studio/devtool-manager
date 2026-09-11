import customtkinter as ctk

from src.ui.fonts import font as _font


class PackagesTab:
    def __init__(self, parent, pkgs_vm):
        self._pkgs_vm = pkgs_vm
        self._pkg_all_items = []
        self._pkg_page = 0
        self._pkg_page_size = 50

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        top_bar.grid_columnconfigure(7, weight=1)

        ctk.CTkLabel(top_bar, text="Function:", font=_font(size=12)).grid(row=0, column=0, padx=(0, 4))
        func_values = ["All"] + pkgs_vm.func_tags
        self._pkg_func_combobox = ctk.CTkComboBox(
            top_bar, values=func_values, command=self._on_pkg_func_filter,
            height=28, width=130,
        )
        self._pkg_func_combobox.set("All")
        self._pkg_func_combobox.grid(row=0, column=1)

        ctk.CTkLabel(top_bar, text="Language:", font=_font(size=12)).grid(row=0, column=2, padx=(8, 4))
        lang_values = ["All"] + pkgs_vm.lang_tags
        self._pkg_lang_combobox = ctk.CTkComboBox(
            top_bar, values=lang_values, command=self._on_pkg_lang_filter,
            height=28, width=100,
        )
        self._pkg_lang_combobox.set("All")
        self._pkg_lang_combobox.grid(row=0, column=3)

        ctk.CTkLabel(top_bar, text="Status:", font=_font(size=12)).grid(row=0, column=4, padx=(8, 4))
        install_values = ["All"] + pkgs_vm.install_tags
        self._pkg_install_combobox = ctk.CTkComboBox(
            top_bar, values=install_values, command=self._on_pkg_install_filter,
            height=28, width=110,
        )
        self._pkg_install_combobox.set("All")
        self._pkg_install_combobox.grid(row=0, column=5)

        self._btn_pkg_install = ctk.CTkButton(top_bar, text="Install", width=80, height=28, command=self._on_install_pkg)
        self._btn_pkg_install.grid(row=0, column=6, padx=(8, 0))

        self._pkg_msg_label = ctk.CTkLabel(top_bar, text="", font=_font(size=11), anchor="w")
        self._pkg_msg_label.grid(row=0, column=5, padx=(8, 0), sticky="w")

        self._pkg_detail_list = ctk.CTkScrollableFrame(parent)
        self._pkg_detail_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self._pkg_detail_list.grid_columnconfigure(0, weight=1)

    @property
    def btn_install(self):
        return self._btn_pkg_install

    def bind_viewmodels(self):
        self._pkgs_vm.filtered_packages.on_change(self._update_pkg_list)
        self._pkgs_vm.is_loading.on_change(self._on_pkg_loading_changed)
        self._pkgs_vm.message.on_change(lambda v: self._pkg_msg_label.configure(text=v))

    def _on_pkg_loading_changed(self, loading):
        state = "disabled" if loading else "normal"
        self._btn_pkg_install.configure(state=state)

    def _on_pkg_func_filter(self, value: str):
        func = "" if value == "All" else value
        lang = "" if self._pkg_lang_combobox.get() == "All" else self._pkg_lang_combobox.get()
        install = "" if self._pkg_install_combobox.get() == "All" else self._pkg_install_combobox.get()
        self._pkgs_vm.set_filters(func, lang, install)

    def _on_pkg_lang_filter(self, value: str):
        lang = "" if value == "All" else value
        func = "" if self._pkg_func_combobox.get() == "All" else self._pkg_func_combobox.get()
        install = "" if self._pkg_install_combobox.get() == "All" else self._pkg_install_combobox.get()
        self._pkgs_vm.set_filters(func, lang, install)

    def _on_pkg_install_filter(self, value: str):
        install = "" if value == "All" else value
        func = "" if self._pkg_func_combobox.get() == "All" else self._pkg_func_combobox.get()
        lang = "" if self._pkg_lang_combobox.get() == "All" else self._pkg_lang_combobox.get()
        self._pkgs_vm.set_filters(func, lang, install)

    def _update_pkg_list(self, items: list):
        self._pkg_all_items = items
        self._pkg_page = 0
        self._render_pkg_page()

    def _render_pkg_page(self):
        for child in self._pkg_detail_list.winfo_children():
            child.destroy()

        items = self._pkg_all_items
        page = self._pkg_page
        ps = self._pkg_page_size
        total = len(items)
        start = page * ps
        end = min(start + ps, total)
        page_items = items[start:end]

        for i, item in enumerate(page_items):
            row = ctk.CTkFrame(self._pkg_detail_list, fg_color="transparent", height=28)
            row.grid(row=i, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(3, weight=1)

            ctk.CTkLabel(row, text=item["func_tag"], anchor="w", font=_font(size=11),
                         text_color="#6BA3D6", width=90).grid(row=0, column=0, padx=(0, 4), sticky="w")
            ctk.CTkLabel(row, text=item["lang_tag"], anchor="w", font=_font(size=11),
                         text_color="#8BC34A", width=60).grid(row=0, column=1, padx=(0, 4), sticky="w")
            status_color = "#4CAF50" if item["install_tag"] == "Installed" else "#FF9800"
            ctk.CTkLabel(row, text=item["install_tag"], anchor="w", font=_font(size=11),
                         text_color=status_color, width=80).grid(row=0, column=2, padx=(0, 8), sticky="w")
            ctk.CTkLabel(row, text=item["name"], anchor="w", font=_font(size=13)).grid(
                row=0, column=3, sticky="w"
            )
            ctk.CTkLabel(row, text=item.get("version", ""), anchor="e", font=_font(size=12),
                         text_color="#AAAAAA").grid(row=0, column=4, sticky="e", padx=(0, 8))

            if item["install_tag"] == "Installed":
                ctk.CTkButton(row, text="Del", width=48, height=24, font=_font(size=11),
                              fg_color="#D9534F", hover_color="#C9302C",
                              command=lambda n=item["name"]: self._on_uninstall_pkg(n)).grid(row=0, column=5)
            else:
                ctk.CTkButton(row, text="Add", width=48, height=24, font=_font(size=11),
                              fg_color="#5CB85C", hover_color="#449D44",
                              command=lambda n=item["name"]: self._on_install_pkg_name(n)).grid(row=0, column=5)

        if total > ps:
            nav = ctk.CTkFrame(self._pkg_detail_list, fg_color="transparent")
            nav.grid(row=len(page_items), column=0, sticky="ew", pady=(6, 0))
            nav.grid_columnconfigure(1, weight=1)

            total_pages = (total + ps - 1) // ps
            info = f"{start+1}-{end} / {total}"
            ctk.CTkLabel(nav, text=info, font=_font(size=11)).grid(row=0, column=1)

            if page > 0:
                ctk.CTkButton(nav, text="< Prev", width=70, height=24, font=_font(size=11),
                              command=self._pkg_prev_page).grid(row=0, column=0, padx=(0, 4))
            if page < total_pages - 1:
                ctk.CTkButton(nav, text="Next >", width=70, height=24, font=_font(size=11),
                              command=self._pkg_next_page).grid(row=0, column=2, padx=(4, 0))

    def _pkg_prev_page(self):
        self._pkg_page = max(0, self._pkg_page - 1)
        self._render_pkg_page()

    def _pkg_next_page(self):
        self._pkg_page += 1
        self._render_pkg_page()

    def _on_install_pkg(self):
        dialog = ctk.CTkInputDialog(text="Package name:", title="Install Package")
        self._pkg_detail_list.winfo_toplevel().wait_window(dialog)
        name = dialog.get_input()
        if name and name.strip():
            self._pkgs_vm.install(name.strip())

    def _on_install_pkg_name(self, name: str):
        self._pkgs_vm.install(name)

    def _on_uninstall_pkg(self, name: str):
        confirm = ctk.CTkInputDialog(text=f"Type 'yes' to uninstall {name}:", title="Confirm Uninstall")
        self._pkg_detail_list.winfo_toplevel().wait_window(confirm)
        if confirm.get_input() and confirm.get_input().strip().lower() == "yes":
            self._pkgs_vm.uninstall(name)
