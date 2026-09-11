import customtkinter as ctk

from src.ui.fonts import font as _font

_SOURCE_COLORS = {"system": "#4A90D9", "user": "#50C878"}
_SOURCE_LABELS = {"system": "S", "user": "U"}


class EnvVarDialog(ctk.CTkToplevel):
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


class EnvVarRow(ctk.CTkFrame):
    def __init__(self, parent, name, value, source, is_path_entry=False, on_edit=None, on_delete=None):
        super().__init__(parent, fg_color="transparent", height=32)
        self.grid_columnconfigure(1, weight=1)

        badge = _SOURCE_LABELS.get(source, "?")
        color = _SOURCE_COLORS.get(source, "#888")
        ctk.CTkLabel(self, text=f" {badge} ", fg_color=color, corner_radius=4,
                     font=_font(size=11, weight="bold"), width=24).grid(row=0, column=0, padx=(0, 6))

        if is_path_entry:
            prefix = "PATH> "
            display = value if len(value) <= 74 else value[:71] + "..."
        else:
            prefix = ""
            display = f"{name}={value}" if len(value) <= 80 else f"{name}={value[:77]}..."
        ctk.CTkLabel(self, text=prefix + display, anchor="w", font=_font(size=13)).grid(
            row=0, column=1, sticky="ew", padx=(0, 8)
        )

        if on_edit:
            ctk.CTkButton(self, text="Edit", width=56, height=26,
                          font=_font(size=12), command=on_edit).grid(row=0, column=2, padx=(0, 4))
        if on_delete:
            ctk.CTkButton(self, text="Del", width=56, height=26,
                          font=_font(size=12), fg_color="#D9534F", hover_color="#C9302C",
                          command=on_delete).grid(row=0, column=3)


class ToolInfoCard(ctk.CTkFrame):
    def __init__(self, parent, info: dict):
        super().__init__(parent, corner_radius=6)
        self.grid_columnconfigure(0, weight=1)

        installed = info.get("installed", False)
        version = info.get("version")
        details = info.get("details", [])

        if not installed and not details:
            ctk.CTkLabel(self, text="Not installed", text_color="gray",
                         font=_font(size=12)).grid(row=0, column=0, padx=8, pady=4, sticky="w")
            return

        row_idx = 0
        if version:
            ctk.CTkLabel(self, text=str(version), font=_font(size=13, weight="bold"),
                         anchor="w").grid(row=row_idx, column=0, padx=8, pady=(4, 0), sticky="ew")
            row_idx += 1

        for detail in details:
            ctk.CTkLabel(self, text=detail, font=_font(size=11), anchor="w",
                         text_color="#AAAAAA").grid(row=row_idx, column=0, padx=8, pady=0, sticky="ew")
            row_idx += 1

        home = info.get("home")
        if home:
            ctk.CTkLabel(self, text=f"Home: {home}", font=_font(size=11), anchor="w",
                         text_color="#AAAAAA").grid(row=row_idx, column=0, padx=8, pady=(0, 4), sticky="ew")
