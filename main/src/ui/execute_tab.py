import os
import customtkinter as ctk

from src.ui.fonts import font as _font, mono as _mono


class ExecuteTab:
    def __init__(self, parent, executor_vm):
        self._vm = executor_vm
        self._command_history = []
        self._history_index = -1

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(3, weight=0)

        cwd_bar = ctk.CTkFrame(parent, fg_color="transparent")
        cwd_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(2, 2))
        cwd_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cwd_bar, text="目录:", font=_font(size=12)).grid(row=0, column=0, padx=(0, 4))
        self._cwd_entry = ctk.CTkEntry(cwd_bar, height=28)
        self._cwd_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        self._cwd_entry.insert(0, self._vm.cwd.value)
        self._cwd_entry.bind("<Return>", self._on_cwd_enter)

        self._btn_cwd = ctk.CTkButton(cwd_bar, text="...", width=36, height=28, command=self._on_browse_cwd)
        self._btn_cwd.grid(row=0, column=2, padx=(0, 4))

        cmd_bar = ctk.CTkFrame(parent, fg_color="transparent")
        cmd_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 4))
        cmd_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cmd_bar, text="命令:", font=_font(size=12)).grid(row=0, column=0, padx=(0, 4))
        self._cmd_entry = ctk.CTkEntry(cmd_bar, height=28)
        self._cmd_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        self._cmd_entry.bind("<Return>", self._on_execute)
        self._cmd_entry.bind("<Up>", self._on_history_up)
        self._cmd_entry.bind("<Down>", self._on_history_down)

        self._btn_run = ctk.CTkButton(cmd_bar, text="执行", width=70, height=28, command=self._on_execute)
        self._btn_run.grid(row=0, column=2, padx=(0, 4))

        self._btn_kill = ctk.CTkButton(cmd_bar, text="终止", width=70, height=28,
                                        fg_color="#D9534F", hover_color="#C9302C",
                                        command=self._on_kill)
        self._btn_kill.grid(row=0, column=3, padx=(0, 4))

        self._btn_clear = ctk.CTkButton(cmd_bar, text="清除", width=70, height=28,
                                         fg_color="gray", hover_color="gray",
                                         command=self._on_clear)
        self._btn_clear.grid(row=0, column=4)

        self._output_text = ctk.CTkTextbox(parent, font=_mono(size=12), state="disabled")
        self._output_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 6))

        self._status_bar = ctk.CTkFrame(parent, fg_color="transparent", height=24)
        self._status_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 4))
        self._status_bar.grid_columnconfigure(1, weight=1)

        self._status_label = ctk.CTkLabel(self._status_bar, text="就绪", font=_font(size=11), anchor="w")
        self._status_label.grid(row=0, column=0, sticky="w")

        self._exit_label = ctk.CTkLabel(self._status_bar, text="", font=_font(size=11), anchor="e")
        self._exit_label.grid(row=0, column=1, sticky="e")

    def bind_viewmodels(self):
        self._vm.output.on_change(self._update_output)
        self._vm.is_running.on_change(self._on_running_changed)
        self._vm.exit_code.on_change(self._on_exit_code_changed)
        self._vm.cwd.on_change(self._on_cwd_changed)

    def _on_execute(self, event=None):
        cmd = self._cmd_entry.get().strip()
        if not cmd:
            return
        self._vm.set_cwd(self._cwd_entry.get().strip())
        if cmd not in self._command_history:
            self._command_history.append(cmd)
        self._history_index = len(self._command_history)
        self._vm.execute(cmd)

    def _on_kill(self):
        self._vm.kill()

    def _on_clear(self):
        self._vm.clear_output()

    def _on_cwd_enter(self, event=None):
        path = self._cwd_entry.get().strip()
        self._vm.set_cwd(path)

    def _on_browse_cwd(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=self._cwd_entry.get())
        if path:
            self._cwd_entry.delete(0, "end")
            self._cwd_entry.insert(0, path)
            self._vm.set_cwd(path)

    def _on_history_up(self, event=None):
        if self._command_history and self._history_index > 0:
            self._history_index -= 1
            self._cmd_entry.delete(0, "end")
            self._cmd_entry.insert(0, self._command_history[self._history_index])
        return "break"

    def _on_history_down(self, event=None):
        if self._history_index < len(self._command_history) - 1:
            self._history_index += 1
            self._cmd_entry.delete(0, "end")
            self._cmd_entry.insert(0, self._command_history[self._history_index])
        elif self._history_index == len(self._command_history) - 1:
            self._history_index = len(self._command_history)
            self._cmd_entry.delete(0, "end")
        return "break"

    def _update_output(self, text: str):
        self._output_text.configure(state="normal")
        self._output_text.delete("1.0", "end")
        self._output_text.insert("1.0", text)
        self._output_text.see("end")
        self._output_text.configure(state="disabled")

    def _on_running_changed(self, running: bool):
        if running:
            self._btn_run.configure(state="disabled")
            self._btn_kill.configure(state="normal")
            self._status_label.configure(text="运行中...", text_color="#FF9800")
            self._exit_label.configure(text="")
        else:
            self._btn_run.configure(state="normal")
            self._btn_kill.configure(state="disabled")
            self._status_label.configure(text="就绪", text_color="white")

    def _on_exit_code_changed(self, code):
        if code is not None:
            color = "#4CAF50" if code == 0 else "#D9534F"
            self._exit_label.configure(text=f"Exit: {code}", text_color=color)

    def _on_cwd_changed(self, path: str):
        if self._cwd_entry.get() != path:
            self._cwd_entry.delete(0, "end")
            self._cwd_entry.insert(0, path)
