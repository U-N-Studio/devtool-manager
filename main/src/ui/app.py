import customtkinter as ctk

from src.viewmodel.observable import Observable
from src.viewmodel.env_viewmodel import EnvViewModel
from src.viewmodel.packages_viewmodel import PackagesViewModel
from src.viewmodel.tool_info_viewmodel import ToolInfoViewModel
from src.core.tools import TOOL_INFO_FUNCS


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

_SOURCE_COLORS = {"system": "#4A90D9", "user": "#50C878"}
_SOURCE_LABELS = {"system": "S", "user": "U"}


class _EnvVarDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Environment Variable", name="", value="", source="user", readonly_name=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x220")
        self.resizable(False, False)
        self.grab_set()

        self.result = None

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Name:", anchor="w").grid(row=0, column=0, padx=(16, 8), pady=(16, 4), sticky="w")
        self._name_entry = ctk.CTkEntry(self, width=280)
        self._name_entry.grid(row=0, column=1, padx=(0, 16), pady=(16, 4), sticky="ew")
        self._name_entry.insert(0, name)
        if readonly_name:
            self._name_entry.configure(state="disabled")

        ctk.CTkLabel(self, text="Value:", anchor="w").grid(row=1, column=0, padx=(16, 8), pady=4, sticky="w")
        self._value_entry = ctk.CTkEntry(self, width=280)
        self._value_entry.grid(row=1, column=1, padx=(0, 16), pady=4, sticky="ew")
        self._value_entry.insert(0, value)

        ctk.CTkLabel(self, text="Source:", anchor="w").grid(row=2, column=0, padx=(16, 8), pady=4, sticky="w")
        self._source_var = ctk.StringVar(value=source)
        self._source_menu = ctk.CTkSegmentedButton(self, values=["user", "system"], variable=self._source_var)
        self._source_menu.grid(row=2, column=1, padx=(0, 16), pady=4, sticky="w")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(16, 16))
        ctk.CTkButton(btn_frame, text="OK", width=100, command=self._on_ok).grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="gray", command=self._on_cancel).grid(row=0, column=1, padx=8)

        self._name_entry.focus_set()

    def _on_ok(self):
        name = self._name_entry.get().strip()
        value = self._value_entry.get()
        source = self._source_var.get()
        if name:
            self.result = {"name": name, "value": value, "source": source}
        self.destroy()

    def _on_cancel(self):
        self.destroy()


class _EnvVarRow(ctk.CTkFrame):
    def __init__(self, parent, name, value, source, is_path_entry=False, on_edit=None, on_delete=None):
        super().__init__(parent, fg_color="transparent", height=32)
        self.grid_columnconfigure(1, weight=1)

        badge = _SOURCE_LABELS.get(source, "?")
        color = _SOURCE_COLORS.get(source, "#888")
        ctk.CTkLabel(self, text=f" {badge} ", fg_color=color, corner_radius=4,
                     font=ctk.CTkFont(size=11, weight="bold"), width=24).grid(row=0, column=0, padx=(0, 6))

        if is_path_entry:
            prefix = "PATH> "
            display = value if len(value) <= 74 else value[:71] + "..."
        else:
            prefix = ""
            display = f"{name}={value}" if len(value) <= 80 else f"{name}={value[:77]}..."
        ctk.CTkLabel(self, text=prefix + display, anchor="w", font=ctk.CTkFont(size=13)).grid(
            row=0, column=1, sticky="ew", padx=(0, 8)
        )

        if on_edit:
            ctk.CTkButton(self, text="Edit", width=56, height=26,
                          font=ctk.CTkFont(size=12), command=on_edit).grid(row=0, column=2, padx=(0, 4))
        if on_delete:
            ctk.CTkButton(self, text="Del", width=56, height=26,
                          font=ctk.CTkFont(size=12), fg_color="#D9534F", hover_color="#C9302C",
                          command=on_delete).grid(row=0, column=3)


class _ToolInfoCard(ctk.CTkFrame):
    def __init__(self, parent, info: dict):
        super().__init__(parent, corner_radius=6)
        self.grid_columnconfigure(0, weight=1)

        installed = info.get("installed", False)
        version = info.get("version")
        details = info.get("details", [])

        if not installed and not details:
            ctk.CTkLabel(self, text="Not installed", text_color="gray",
                         font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=8, pady=4, sticky="w")
            return

        row_idx = 0
        if version:
            ctk.CTkLabel(self, text=str(version), font=ctk.CTkFont(size=13, weight="bold"),
                         anchor="w").grid(row=row_idx, column=0, padx=8, pady=(4, 0), sticky="ew")
            row_idx += 1

        for detail in details:
            ctk.CTkLabel(self, text=detail, font=ctk.CTkFont(size=11), anchor="w",
                         text_color="#AAAAAA").grid(row=row_idx, column=0, padx=8, pady=0, sticky="ew")
            row_idx += 1

        home = info.get("home")
        if home:
            ctk.CTkLabel(self, text=f"Home: {home}", font=ctk.CTkFont(size=11), anchor="w",
                         text_color="#AAAAAA").grid(row=row_idx, column=0, padx=8, pady=(0, 4), sticky="ew")


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
        self._env_data = {}

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_body()
        self._bind_viewmodels()

        self.after(100, self._on_refresh)

    def _build_header(self):
        header = ctk.CTkFrame(self, height=48, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="DevTool Manager", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=(16, 8), pady=10
        )

        self._btn_refresh = ctk.CTkButton(header, text="Refresh", width=90, command=self._on_refresh)
        self._btn_refresh.grid(row=0, column=1, sticky="e", padx=(0, 16), pady=10)

    def _build_body(self):
        body = ctk.CTkTabview(self)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self._build_env_tab(body.add("Environment"))
        self._build_pkgs_tab(body.add("Packages"))

    def _build_env_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 2))
        top_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_bar, text="Category:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(0, 6)
        )

        self._cat_combobox = ctk.CTkComboBox(top_bar, values=[""], command=self._on_category_selected, height=28)
        self._cat_combobox.grid(row=0, column=1, sticky="ew")

        legend_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        legend_frame.grid(row=0, column=2, padx=(12, 0))
        ctk.CTkLabel(legend_frame, text="Source: ", font=ctk.CTkFont(size=11)).grid(row=0, column=0)
        for i, (src, color) in enumerate(_SOURCE_COLORS.items()):
            ctk.CTkLabel(legend_frame, text=f" {_SOURCE_LABELS[src]} ", fg_color=color,
                         corner_radius=4, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=1 + i * 2, padx=(0, 2))
            ctk.CTkLabel(legend_frame, text=f"={src.capitalize()}", font=ctk.CTkFont(size=11)).grid(row=0, column=2 + i * 2, padx=(0, 8))

        self._btn_add = ctk.CTkButton(top_bar, text="+ Add", width=80, height=28, command=self._on_add_var)
        self._btn_add.grid(row=0, column=3, padx=(8, 0))

        self._msg_label = ctk.CTkLabel(top_bar, text="", font=ctk.CTkFont(size=11), anchor="w")
        self._msg_label.grid(row=0, column=4, padx=(8, 0), sticky="w")

        self._tool_info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._tool_info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 2))

        self._var_list = ctk.CTkScrollableFrame(parent)
        self._var_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self._var_list.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

    def _build_pkgs_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        top_bar.grid_columnconfigure(7, weight=1)

        ctk.CTkLabel(top_bar, text="Function:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 4))
        func_values = ["All"] + self._pkgs_vm.func_tags
        self._pkg_func_combobox = ctk.CTkComboBox(
            top_bar, values=func_values, command=self._on_pkg_func_filter,
            height=28, width=130,
        )
        self._pkg_func_combobox.set("All")
        self._pkg_func_combobox.grid(row=0, column=1)

        ctk.CTkLabel(top_bar, text="Language:", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=(8, 4))
        lang_values = ["All"] + self._pkgs_vm.lang_tags
        self._pkg_lang_combobox = ctk.CTkComboBox(
            top_bar, values=lang_values, command=self._on_pkg_lang_filter,
            height=28, width=100,
        )
        self._pkg_lang_combobox.set("All")
        self._pkg_lang_combobox.grid(row=0, column=3)

        ctk.CTkLabel(top_bar, text="Status:", font=ctk.CTkFont(size=12)).grid(row=0, column=4, padx=(8, 4))
        install_values = ["All"] + self._pkgs_vm.install_tags
        self._pkg_install_combobox = ctk.CTkComboBox(
            top_bar, values=install_values, command=self._on_pkg_install_filter,
            height=28, width=110,
        )
        self._pkg_install_combobox.set("All")
        self._pkg_install_combobox.grid(row=0, column=5)

        self._btn_pkg_install = ctk.CTkButton(top_bar, text="Install", width=80, height=28, command=self._on_install_pkg)
        self._btn_pkg_install.grid(row=0, column=6, padx=(8, 0))

        self._pkg_msg_label = ctk.CTkLabel(top_bar, text="", font=ctk.CTkFont(size=11), anchor="w")
        self._pkg_msg_label.grid(row=0, column=5, padx=(8, 0), sticky="w")

        self._pkg_detail_list = ctk.CTkScrollableFrame(parent)
        self._pkg_detail_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self._pkg_detail_list.grid_columnconfigure(0, weight=1)

    def _bind_viewmodels(self):
        vm = self._env_vm
        vm.categorized_env.on_change(self._update_env_categories)
        vm.is_loading.on_change(self._on_loading_changed)
        vm.message.on_change(lambda v: self._msg_label.configure(text=v))

        pvm = self._pkgs_vm
        pvm.filtered_packages.on_change(self._update_pkg_list)
        pvm.is_loading.on_change(self._on_pkg_loading_changed)
        pvm.message.on_change(lambda v: self._pkg_msg_label.configure(text=v))

        self._tool_vm.tool_info.on_change(self._update_tool_info)

    def _on_loading_changed(self, loading):
        state = "disabled" if loading else "normal"
        self._btn_refresh.configure(state=state)
        self._btn_add.configure(state=state)

    def _update_tool_info(self, info: dict):
        for child in self._tool_info_frame.winfo_children():
            child.destroy()
        if info:
            card = _ToolInfoCard(self._tool_info_frame, info)
            card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 6))

    def _update_env_categories(self, data: dict):
        self._env_data = data
        categories = list(data.keys())
        if categories:
            self._cat_combobox.configure(values=categories)
            self._cat_combobox.set(categories[0])
            self._show_category(categories[0])
        else:
            self._cat_combobox.configure(values=[""])
            self._cat_combobox.set("")
            self._clear_var_list()

    def _on_category_selected(self, choice: str):
        self._show_category(choice)

    def _clear_var_list(self):
        for child in self._var_list.winfo_children():
            child.destroy()

    def _show_category(self, cat_name: str):
        self._clear_var_list()

        if cat_name in TOOL_INFO_FUNCS:
            self._tool_vm.refresh(cat_name)
        else:
            self._update_tool_info({})

        items = self._env_data.get(cat_name, [])

        env_items = [item for item in items if not item.get("is_path_entry")]
        path_items = [item for item in items if item.get("is_path_entry")]

        row_idx = 0
        for item in env_items:
            row = _EnvVarRow(
                self._var_list, name=item["name"], value=item["value"],
                source=item["source"], on_edit=lambda v=item: self._on_edit_var(v),
                on_delete=lambda v=item: self._on_delete_var(v),
            )
            row.grid(row=row_idx, column=0, sticky="ew", pady=1)
            row_idx += 1

        if path_items:
            if env_items:
                sep = ctk.CTkLabel(self._var_list, text="── PATH Entries ──", font=ctk.CTkFont(size=12), text_color="gray")
                sep.grid(row=row_idx, column=0, sticky="w", pady=(8, 4))
                row_idx += 1
            for item in path_items:
                row = _EnvVarRow(
                    self._var_list, name=item["name"], value=item["value"],
                    source=item["source"], is_path_entry=True,
                    on_edit=lambda v=item: self._on_edit_var(v),
                    on_delete=lambda v=item: self._on_delete_var(v),
                )
                row.grid(row=row_idx, column=0, sticky="ew", pady=1)
                row_idx += 1

    def _on_add_var(self):
        cat = self._cat_combobox.get()
        if cat == "Path":
            dialog = _EnvVarDialog(self, title="Add PATH Entry", name="PATH", readonly_name=True)
            self.wait_window(dialog)
            if dialog.result:
                self._env_vm.add_path_entry(dialog.result["value"], dialog.result["source"])
        else:
            dialog = _EnvVarDialog(self, title="Add Environment Variable")
            self.wait_window(dialog)
            if dialog.result:
                r = dialog.result
                self._env_vm.add_var(r["name"], r["value"], r["source"])

    def _on_edit_var(self, var: dict):
        is_path = var.get("is_path_entry", False)
        if is_path:
            dialog = _EnvVarDialog(
                self, title="Edit PATH Entry", name="PATH", value=var["value"],
                source=var["source"], readonly_name=True,
            )
            self.wait_window(dialog)
            if dialog.result:
                self._env_vm.update_path_entry(var["value"], dialog.result["value"], dialog.result["source"])
        else:
            dialog = _EnvVarDialog(
                self, title="Edit Environment Variable",
                name=var["name"], value=var["value"], source=var["source"],
                readonly_name=True,
            )
            self.wait_window(dialog)
            if dialog.result:
                r = dialog.result
                self._env_vm.update_var(r["name"], r["value"], r["source"])

    def _on_delete_var(self, var: dict):
        is_path = var.get("is_path_entry", False)
        prompt = f"Type 'yes' to remove from PATH:\n{var['value']}" if is_path else f"Type 'yes' to delete {var['name']}:"
        confirm = ctk.CTkInputDialog(text=prompt, title="Confirm Delete")
        self.wait_window(confirm)
        if confirm.get_input() and confirm.get_input().strip().lower() == "yes":
            if is_path:
                self._env_vm.delete_path_entry(var["value"], var["source"])
            else:
                self._env_vm.delete_var(var["name"], var["source"])

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
        self._pkg_page_size = 50
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

            ctk.CTkLabel(row, text=item["func_tag"], anchor="w", font=ctk.CTkFont(size=11),
                         text_color="#6BA3D6", width=90).grid(row=0, column=0, padx=(0, 4), sticky="w")
            ctk.CTkLabel(row, text=item["lang_tag"], anchor="w", font=ctk.CTkFont(size=11),
                         text_color="#8BC34A", width=60).grid(row=0, column=1, padx=(0, 4), sticky="w")
            status_color = "#4CAF50" if item["install_tag"] == "Installed" else "#FF9800"
            ctk.CTkLabel(row, text=item["install_tag"], anchor="w", font=ctk.CTkFont(size=11),
                         text_color=status_color, width=80).grid(row=0, column=2, padx=(0, 8), sticky="w")
            ctk.CTkLabel(row, text=item["name"], anchor="w", font=ctk.CTkFont(size=13)).grid(
                row=0, column=3, sticky="w"
            )
            ctk.CTkLabel(row, text=item.get("version", ""), anchor="e", font=ctk.CTkFont(size=12),
                         text_color="#AAAAAA").grid(row=0, column=4, sticky="e", padx=(0, 8))

            if item["install_tag"] == "Installed":
                ctk.CTkButton(row, text="Del", width=48, height=24, font=ctk.CTkFont(size=11),
                              fg_color="#D9534F", hover_color="#C9302C",
                              command=lambda n=item["name"]: self._on_uninstall_pkg(n)).grid(row=0, column=5)
            else:
                ctk.CTkButton(row, text="Add", width=48, height=24, font=ctk.CTkFont(size=11),
                              fg_color="#5CB85C", hover_color="#449D44",
                              command=lambda n=item["name"]: self._on_install_pkg_name(n)).grid(row=0, column=5)

        if total > ps:
            nav = ctk.CTkFrame(self._pkg_detail_list, fg_color="transparent")
            nav.grid(row=len(page_items), column=0, sticky="ew", pady=(6, 0))
            nav.grid_columnconfigure(1, weight=1)

            total_pages = (total + ps - 1) // ps
            info = f"{start+1}-{end} / {total}"
            ctk.CTkLabel(nav, text=info, font=ctk.CTkFont(size=11)).grid(row=0, column=1)

            if page > 0:
                ctk.CTkButton(nav, text="< Prev", width=70, height=24, font=ctk.CTkFont(size=11),
                              command=self._pkg_prev_page).grid(row=0, column=0, padx=(0, 4))
            if page < total_pages - 1:
                ctk.CTkButton(nav, text="Next >", width=70, height=24, font=ctk.CTkFont(size=11),
                              command=self._pkg_next_page).grid(row=0, column=2, padx=(4, 0))

    def _pkg_prev_page(self):
        self._pkg_page = max(0, self._pkg_page - 1)
        self._render_pkg_page()

    def _pkg_next_page(self):
        self._pkg_page += 1
        self._render_pkg_page()

    def _on_install_pkg(self):
        dialog = ctk.CTkInputDialog(text="Package name:", title="Install Package")
        self.wait_window(dialog)
        name = dialog.get_input()
        if name and name.strip():
            self._pkgs_vm.install(name.strip())

    def _on_install_pkg_name(self, name: str):
        self._pkgs_vm.install(name)

    def _on_uninstall_pkg(self, name: str):
        confirm = ctk.CTkInputDialog(text=f"Type 'yes' to uninstall {name}:", title="Confirm Uninstall")
        self.wait_window(confirm)
        if confirm.get_input() and confirm.get_input().strip().lower() == "yes":
            self._pkgs_vm.uninstall(name)

    def _on_refresh(self):
        self._env_vm.refresh()
        self._pkgs_vm.refresh()
        cat = self._cat_combobox.get()
        if cat in TOOL_INFO_FUNCS:
            self._tool_vm.refresh(cat)

    def _schedule_on_ui(self, callback: callable):
        self.after(0, callback)
