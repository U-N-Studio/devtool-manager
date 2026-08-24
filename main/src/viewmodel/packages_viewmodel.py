import threading

from src.viewmodel.observable import Observable
from src.core.packages import get_categorized_packages, install_package, uninstall_package, FUNC_TAGS, LANG_TAGS, INSTALL_TAGS


class PackagesViewModel:
    def __init__(self):
        self.filtered_packages = Observable([])
        self.is_loading = Observable(False)
        self.message = Observable("")
        self.func_tags = FUNC_TAGS
        self.lang_tags = LANG_TAGS
        self.install_tags = INSTALL_TAGS
        self._func_tag = ""
        self._lang_tag = ""
        self._install_tag = ""

    def set_filters(self, func_tag: str = "", lang_tag: str = "", install_tag: str = ""):
        self._func_tag = func_tag
        self._lang_tag = lang_tag
        self._install_tag = install_tag
        self.refresh()

    def refresh(self):
        self.is_loading.set(True)
        thread = threading.Thread(target=self._load, daemon=True)
        thread.start()

    def _load(self):
        try:
            self.filtered_packages.set(get_categorized_packages(self._func_tag, self._lang_tag, self._install_tag))
            self.message.set("")
        finally:
            self.is_loading.set(False)

    def install(self, name: str):
        self.is_loading.set(True)
        self.message.set(f"Installing {name}...")
        thread = threading.Thread(target=self._do_install, args=(name,), daemon=True)
        thread.start()

    def _do_install(self, name: str):
        try:
            ok, output = install_package(name)
            self.message.set(f"Install {'success' if ok else 'failed'}: {name}")
        finally:
            self.is_loading.set(False)
            self._load()

    def uninstall(self, name: str):
        self.is_loading.set(True)
        self.message.set(f"Uninstalling {name}...")
        thread = threading.Thread(target=self._do_uninstall, args=(name,), daemon=True)
        thread.start()

    def _do_uninstall(self, name: str):
        try:
            ok, output = uninstall_package(name)
            self.message.set(f"Uninstall {'success' if ok else 'failed'}: {name}")
        finally:
            self.is_loading.set(False)
            self._load()
