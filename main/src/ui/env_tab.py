import customtkinter as ctk

from src.ui.fonts import font as _font
from src.ui.widgets import EnvVarDialog, EnvVarRow, ToolInfoCard, _SOURCE_COLORS, _SOURCE_LABELS
from src.core.tools import TOOL_INFO_FUNCS


class EnvTab:
    def __init__(self, parent, env_vm, tool_vm):
        self._env_vm = env_vm
        self._tool_vm = tool_vm
        self._env_data = {}

        parent.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 2))
        top_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_bar, text="Category:", font=_font(size=12)).grid(row=0, column=0, padx=(0, 6))

        self._cat_combobox = ctk.CTkComboBox(top_bar, values=[""], command=self._on_category_selected, height=28)
        self._cat_combobox.grid(row=0, column=1, sticky="ew")

        legend_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        legend_frame.grid(row=0, column=2, padx=(12, 0))
        ctk.CTkLabel(legend_frame, text="Source: ", font=_font(size=11)).grid(row=0, column=0)
        for i, (src, color) in enumerate(_SOURCE_COLORS.items()):
            ctk.CTkLabel(legend_frame, text=f" {_SOURCE_LABELS[src]} ", fg_color=color,
                         corner_radius=4, font=_font(size=10, weight="bold")).grid(row=0, column=1 + i * 2, padx=(0, 2))
            ctk.CTkLabel(legend_frame, text=f"={src.capitalize()}", font=_font(size=11)).grid(row=0, column=2 + i * 2, padx=(0, 8))

        self._btn_add = ctk.CTkButton(top_bar, text="+ Add", width=80, height=28, command=self._on_add_var)
        self._btn_add.grid(row=0, column=3, padx=(8, 0))

        self._msg_label = ctk.CTkLabel(top_bar, text="", font=_font(size=11), anchor="w")
        self._msg_label.grid(row=0, column=4, padx=(8, 0), sticky="w")

        self._tool_info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._tool_info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 2))

        self._var_list = ctk.CTkScrollableFrame(parent)
        self._var_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 6))
        self._var_list.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

    @property
    def cat_combobox(self):
        return self._cat_combobox

    @property
    def btn_add(self):
        return self._btn_add

    @property
    def msg_label(self):
        return self._msg_label

    def bind_viewmodels(self):
        self._env_vm.categorized_env.on_change(self._update_env_categories)
        self._env_vm.is_loading.on_change(self._on_loading_changed)
        self._env_vm.message.on_change(lambda v: self._msg_label.configure(text=v))
        self._tool_vm.tool_info.on_change(self._update_tool_info)

    def _on_loading_changed(self, loading):
        pass

    def _update_tool_info(self, info: dict):
        for child in self._tool_info_frame.winfo_children():
            child.destroy()
        if info:
            card = ToolInfoCard(self._tool_info_frame, info)
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
            row = EnvVarRow(
                self._var_list, name=item["name"], value=item["value"],
                source=item["source"], on_edit=lambda v=item: self._on_edit_var(v),
                on_delete=lambda v=item: self._on_delete_var(v),
            )
            row.grid(row=row_idx, column=0, sticky="ew", pady=1)
            row_idx += 1

        if path_items:
            if env_items:
                sep = ctk.CTkLabel(self._var_list, text="── PATH Entries ──", font=_font(size=12), text_color="gray")
                sep.grid(row=row_idx, column=0, sticky="w", pady=(8, 4))
                row_idx += 1
            for item in path_items:
                row = EnvVarRow(
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
            dialog = EnvVarDialog(self._var_list, title="Add PATH Entry", name="PATH", readonly_name=True)
        else:
            dialog = EnvVarDialog(self._var_list, title="Add Environment Variable")
        self._var_list.winfo_toplevel().wait_window(dialog)
        if dialog.result:
            r = dialog.result
            if cat == "Path":
                self._env_vm.add_path_entry(r["value"], r["source"])
            else:
                self._env_vm.add_var(r["name"], r["value"], r["source"])

    def _on_edit_var(self, var: dict):
        is_path = var.get("is_path_entry", False)
        if is_path:
            dialog = EnvVarDialog(
                self._var_list, title="Edit PATH Entry", name="PATH", value=var["value"],
                source=var["source"], readonly_name=True,
            )
            self._var_list.winfo_toplevel().wait_window(dialog)
            if dialog.result:
                self._env_vm.update_path_entry(var["value"], dialog.result["value"], dialog.result["source"])
        else:
            dialog = EnvVarDialog(
                self._var_list, title="Edit Environment Variable",
                name=var["name"], value=var["value"], source=var["source"],
                readonly_name=True,
            )
            self._var_list.winfo_toplevel().wait_window(dialog)
            if dialog.result:
                r = dialog.result
                self._env_vm.update_var(r["name"], r["value"], r["source"])

    def _on_delete_var(self, var: dict):
        is_path = var.get("is_path_entry", False)
        prompt = f"Type 'yes' to remove from PATH:\n{var['value']}" if is_path else f"Type 'yes' to delete {var['name']}:"
        confirm = ctk.CTkInputDialog(text=prompt, title="Confirm Delete")
        self._var_list.winfo_toplevel().wait_window(confirm)
        if confirm.get_input() and confirm.get_input().strip().lower() == "yes":
            if is_path:
                self._env_vm.delete_path_entry(var["value"], var["source"])
            else:
                self._env_vm.delete_var(var["name"], var["source"])
