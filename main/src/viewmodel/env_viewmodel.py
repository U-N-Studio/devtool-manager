import os
import threading

from src.viewmodel.observable import Observable
from src.core.env import (
    get_python_version, get_pip_version, get_platform, get_executable,
    get_categorized_env_vars, set_env_var, delete_env_var,
    get_system_and_user_env_vars, classify_env_var,
)


class EnvViewModel:
    def __init__(self):
        self.python_version = Observable("")
        self.pip_version = Observable("")
        self.platform = Observable("")
        self.executable = Observable("")
        self.categorized_env = Observable({})
        self.is_loading = Observable(False)
        self.message = Observable("")

    def refresh(self):
        self.is_loading.set(True)
        thread = threading.Thread(target=self._load, daemon=True)
        thread.start()

    def _load(self):
        try:
            self.python_version.set(get_python_version().split()[0])
            self.pip_version.set(get_pip_version())
            self.platform.set(get_platform())
            self.executable.set(get_executable())
            self.categorized_env.set(get_categorized_env_vars())
            self.message.set("")
        finally:
            self.is_loading.set(False)

    def add_var(self, name: str, value: str, source: str = "user"):
        self.is_loading.set(True)
        self.message.set(f"Setting {name}...")
        thread = threading.Thread(target=self._do_set, args=(name, value, source), daemon=True)
        thread.start()

    def update_var(self, name: str, value: str, source: str = "user"):
        self.is_loading.set(True)
        self.message.set(f"Updating {name}...")
        thread = threading.Thread(target=self._do_set, args=(name, value, source), daemon=True)
        thread.start()

    def _do_set(self, name: str, value: str, source: str):
        try:
            set_env_var(name, value, source)
            self.message.set(f"OK: {name} set in {source}")
            self.categorized_env.set(get_categorized_env_vars())
        except PermissionError:
            self.message.set("Permission denied: need admin for system vars")
        except Exception as e:
            self.message.set(f"Error: {e}")
        finally:
            self.is_loading.set(False)

    def delete_var(self, name: str, source: str = "user"):
        self.is_loading.set(True)
        self.message.set(f"Deleting {name}...")
        thread = threading.Thread(target=self._do_delete, args=(name, source), daemon=True)
        thread.start()

    def _do_delete(self, name: str, source: str):
        try:
            delete_env_var(name, source)
            self.message.set(f"OK: {name} deleted from {source}")
            self.categorized_env.set(get_categorized_env_vars())
        except PermissionError:
            self.message.set("Permission denied: need admin for system vars")
        except Exception as e:
            self.message.set(f"Error: {e}")
        finally:
            self.is_loading.set(False)

    def add_path_entry(self, entry: str, source: str = "user"):
        self.is_loading.set(True)
        self.message.set(f"Adding to PATH: {entry}...")
        thread = threading.Thread(target=self._do_add_path, args=(entry, source), daemon=True)
        thread.start()

    def _do_add_path(self, entry: str, source: str):
        try:
            current = self._get_raw_path(source)
            entries = [e.strip() for e in current.split(";") if e.strip()]
            if entry in entries:
                self.message.set(f"Already in PATH: {entry}")
                return
            entries.append(entry)
            new_path = ";".join(entries)
            set_env_var("PATH", new_path, source)
            self.message.set(f"OK: added to PATH")
            self.categorized_env.set(get_categorized_env_vars())
        except PermissionError:
            self.message.set("Permission denied: need admin for system vars")
        except Exception as e:
            self.message.set(f"Error: {e}")
        finally:
            self.is_loading.set(False)

    def update_path_entry(self, old_entry: str, new_entry: str, source: str = "user"):
        self.is_loading.set(True)
        self.message.set(f"Updating PATH entry...")
        thread = threading.Thread(target=self._do_update_path, args=(old_entry, new_entry, source), daemon=True)
        thread.start()

    def _do_update_path(self, old_entry: str, new_entry: str, source: str):
        try:
            current = self._get_raw_path(source)
            entries = [e.strip() for e in current.split(";") if e.strip()]
            if old_entry in entries:
                idx = entries.index(old_entry)
                entries[idx] = new_entry
            else:
                entries.append(new_entry)
            new_path = ";".join(entries)
            set_env_var("PATH", new_path, source)
            self.message.set(f"OK: PATH entry updated")
            self.categorized_env.set(get_categorized_env_vars())
        except PermissionError:
            self.message.set("Permission denied: need admin for system vars")
        except Exception as e:
            self.message.set(f"Error: {e}")
        finally:
            self.is_loading.set(False)

    def delete_path_entry(self, entry: str, source: str = "user"):
        self.is_loading.set(True)
        self.message.set(f"Removing from PATH: {entry}...")
        thread = threading.Thread(target=self._do_delete_path, args=(entry, source), daemon=True)
        thread.start()

    def _do_delete_path(self, entry: str, source: str):
        try:
            current = self._get_raw_path(source)
            entries = [e.strip() for e in current.split(";") if e.strip()]
            entries = [e for e in entries if e != entry]
            new_path = ";".join(entries)
            set_env_var("PATH", new_path, source)
            self.message.set(f"OK: removed from PATH")
            self.categorized_env.set(get_categorized_env_vars())
        except PermissionError:
            self.message.set("Permission denied: need admin for system vars")
        except Exception as e:
            self.message.set(f"Error: {e}")
        finally:
            self.is_loading.set(False)

    @staticmethod
    def _get_raw_path(source: str) -> str:
        system_vars, user_vars = get_system_and_user_env_vars()
        if source == "system":
            return system_vars.get("PATH", "")
        return user_vars.get("PATH", "")
