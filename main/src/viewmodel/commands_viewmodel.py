import threading

from src.viewmodel.observable import Observable
from src.core.commands import get_command_names, load_command_detail, clear_cache


class CommandsViewModel:
    def __init__(self):
        self.command_names = Observable([])
        self.selected_detail = Observable(None)
        self.is_loading = Observable(False)
        self.message = Observable("")
        self._all_names = []
        self._filter_installed = False

    def refresh(self):
        clear_cache()
        self._all_names = get_command_names()
        self._apply_filter()

    def set_filter_installed(self, installed_only: bool):
        self._filter_installed = installed_only
        if self._all_names:
            self._apply_filter()

    def _apply_filter(self):
        if self._filter_installed:
            self.is_loading.set(True)
            thread = threading.Thread(target=self._load_installed_names, daemon=True)
            thread.start()
        else:
            self.command_names.set(self._all_names)

    def _load_installed_names(self):
        try:
            installed = []
            for name in self._all_names:
                path = __import__("shutil").which(name)
                if path:
                    installed.append(name)
            self.command_names.set(installed)
        finally:
            self.is_loading.set(False)

    def select_command(self, name: str):
        self.is_loading.set(True)
        self.message.set(f"Loading {name}...")
        thread = threading.Thread(target=self._load_detail, args=(name,), daemon=True)
        thread.start()

    def _load_detail(self, name: str):
        try:
            detail = load_command_detail(name)
            self.selected_detail.set(detail)
            self.message.set("")
        except Exception as e:
            self.message.set(f"Error: {e}")
        finally:
            self.is_loading.set(False)
