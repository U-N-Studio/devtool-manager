import customtkinter as ctk

from src.core.env import get_python_version, get_pip_version, get_platform, get_executable, get_all_env_vars
from src.core.packages import get_installed_packages


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class DevToolManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DevTool Manager")
        self.geometry("800x520")
        self.minsize(640, 400)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_body()

        self.after(100, self._refresh_info)

    def _build_header(self):
        header = ctk.CTkFrame(self, height=48, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="DevTool Manager", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=(16, 8), pady=10
        )

        self._btn_refresh = ctk.CTkButton(header, text="Refresh", width=90, command=self._refresh_info)
        self._btn_refresh.grid(row=0, column=1, sticky="e", padx=(0, 16), pady=10)

    def _build_body(self):
        body = ctk.CTkTabview(self)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        tab_env = body.add("Environment")
        tab_pkgs = body.add("Packages")

        self._build_env_tab(tab_env)
        self._build_pkgs_tab(tab_pkgs)

    def _build_env_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)

        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)

        labels = ["Python", "Pip", "Platform", "Executable"]
        self._env_values = {}
        for i, name in enumerate(labels):
            ctk.CTkLabel(info_frame, text=f"{name}:", anchor="w", width=90).grid(
                row=i, column=0, sticky="w", pady=3
            )
            val = ctk.CTkLabel(info_frame, text="...", anchor="w")
            val.grid(row=i, column=1, sticky="ew", padx=(8, 0), pady=3)
            self._env_values[name] = val

        ctk.CTkLabel(parent, text="Environment Variables", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(
            row=1, column=0, sticky="w", padx=10, pady=(10, 2)
        )

        self._env_textbox = ctk.CTkTextbox(parent, height=180)
        self._env_textbox.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        parent.grid_rowconfigure(2, weight=1)

    def _build_pkgs_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self._pkg_textbox = ctk.CTkTextbox(parent)
        self._pkg_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _refresh_info(self):
        self._btn_refresh.configure(state="disabled")
        self.update_idletasks()

        self._env_values["Python"].configure(text=get_python_version().split()[0])
        self._env_values["Pip"].configure(text=get_pip_version())
        self._env_values["Platform"].configure(text=get_platform())
        self._env_values["Executable"].configure(text=get_executable())

        env_lines = [f"{k}={v}" for k, v in sorted(get_all_env_vars().items())]
        self._env_textbox.configure(state="normal")
        self._env_textbox.delete("1.0", "end")
        self._env_textbox.insert("end", "\n".join(env_lines))
        self._env_textbox.configure(state="disabled")

        pkgs = get_installed_packages()
        self._pkg_textbox.configure(state="normal")
        self._pkg_textbox.delete("1.0", "end")
        if pkgs:
            header = f"{'Package':<35}{'Version'}\n{'-'*55}\n"
            self._pkg_textbox.insert("end", header)
            for p in pkgs:
                self._pkg_textbox.insert("end", f"{p['name']:<35}{p['version']}\n")
        else:
            self._pkg_textbox.insert("end", "No packages found.")
        self._pkg_textbox.configure(state="disabled")

        self._btn_refresh.configure(state="normal")
