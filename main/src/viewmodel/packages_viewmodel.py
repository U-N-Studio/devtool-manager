import threading

from src.viewmodel.observable import Observable
from src.core.packages import get_installed_packages, install_package, uninstall_package


class PackagesViewModel:
    def __init__(self):
        self.packages_text = Observable("")
        self.is_loading = Observable(False)
        self.message = Observable("")

    def refresh(self):
        self.is_loading.set(True)
        thread = threading.Thread(target=self._load, daemon=True)
        thread.start()

    def _load(self):
        try:
            pkgs = get_installed_packages()
            if pkgs:
                header = f"{'Package':<35}{'Version'}\n{'-'*55}\n"
                lines = [f"{p['name']:<35}{p['version']}" for p in pkgs]
                self.packages_text.set(header + "\n".join(lines))
            else:
                self.packages_text.set("No packages found.")
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
            self.refresh()

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
            self.refresh()
