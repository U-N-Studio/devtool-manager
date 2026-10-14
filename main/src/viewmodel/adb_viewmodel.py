import threading

from src.viewmodel.observable import Observable
from src.core.adb import (
    is_adb_available, get_package_info, list_installed_packages,
    load_saved_packages, add_saved_package, remove_saved_package,
)


class AdbViewModel:
    def __init__(self):
        self.saved_packages = Observable([])
        self.package_info = Observable(None)
        self.device_packages = Observable([])
        self.is_loading = Observable(False)
        self.adb_available = Observable(None)
        self.message = Observable("")
        self._load_saved()

    def _load_saved(self):
        self.saved_packages.set(load_saved_packages())

    def check_adb(self):
        self.adb_available.set(is_adb_available())
        return self.adb_available.value

    def query_package(self, package_name):
        name = (package_name or "").strip()
        if not name:
            self.message.set("请输入包名")
            return
        self.is_loading.set(True)
        self.message.set(f"查询 {name}...")
        thread = threading.Thread(target=self._do_query, args=(name,), daemon=True)
        thread.start()

    def _do_query(self, name):
        try:
            info = get_package_info(name)
            self.package_info.set(info)
            if info.get("installed"):
                self.message.set(f"已查询: {name}")
            else:
                self.message.set(info.get("error", "未安装"))
        except Exception as e:
            self.message.set(f"查询失败: {e}")
        finally:
            self.is_loading.set(False)

    def save_package(self, package_name):
        name = (package_name or "").strip()
        if not name:
            return
        packages = add_saved_package(name)
        self.saved_packages.set(packages)
        self.message.set(f"已记忆包名: {name}")

    def unsave_package(self, package_name):
        packages = remove_saved_package(package_name)
        self.saved_packages.set(packages)
        self.message.set(f"已移除包名: {package_name}")

    def load_device_packages(self):
        if not is_adb_available():
            self.message.set("adb 未安装")
            return
        self.is_loading.set(True)
        self.message.set("正在获取设备包列表...")
        thread = threading.Thread(target=self._do_load_device, daemon=True)
        thread.start()

    def _do_load_device(self):
        try:
            packages, err = list_installed_packages()
            if err:
                self.message.set(err)
            else:
                self.device_packages.set(packages)
                self.message.set(f"设备已安装 {len(packages)} 个包")
        finally:
            self.is_loading.set(False)
