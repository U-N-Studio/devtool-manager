import os
import sys
import json
import shutil
import subprocess

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
_PACKAGES_FILE = os.path.join(_CONFIG_DIR, "adb_packages.json")


def is_adb_available():
    return shutil.which("adb") is not None


def _run_adb(args, timeout=10):
    if not is_adb_available():
        return "", "adb 未安装或不在 PATH 中"
    try:
        result = subprocess.run(
            ["adb"] + args, capture_output=True, text=True, timeout=timeout,
            creationflags=_SUBPROCESS_FLAGS,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip(), None
    except subprocess.TimeoutExpired:
        return "", "命令执行超时"
    except FileNotFoundError:
        return "", "adb 未安装或不在 PATH 中"
    except Exception as e:
        return "", f"执行失败: {e}"


def get_package_info(package_name):
    """查询指定包的版本信息,解析 adb shell dumpsys package 输出"""
    output, err = _run_adb(["shell", "dumpsys", "package", package_name], timeout=10)
    if err:
        return {"installed": False, "error": err, "package": package_name}

    if not output:
        return {"installed": False, "error": "无输出,请确认设备已连接", "package": package_name}

    lower = output.lower()
    if "no devices" in lower or "no emulators" in lower or "device not found" in lower:
        return {"installed": False, "error": "未检测到设备,请确认 ADB 已连接", "package": package_name}

    versions = []
    current = None

    for line in output.splitlines():
        s = line.strip()
        if s.startswith("Package ["):
            if current:
                versions.append(current)
            current = {
                "version_name": "", "version_code": "", "min_sdk": "",
                "target_sdk": "", "last_update_time": "", "path": "",
            }
        elif current is not None:
            if s.startswith("versionName="):
                current["version_name"] = s.split("=", 1)[1].strip()
            elif s.startswith("versionCode="):
                rest = s.split("=", 1)[1].strip()
                parts = rest.split()
                current["version_code"] = parts[0] if parts else ""
                for part in parts[1:]:
                    if part.startswith("minSdk="):
                        current["min_sdk"] = part.split("=", 1)[1]
                    elif part.startswith("targetSdk="):
                        current["target_sdk"] = part.split("=", 1)[1]
            elif s.startswith("minSdkVersion="):
                current["min_sdk"] = s.split("=", 1)[1].strip()
            elif s.startswith("targetSdkVersion="):
                current["target_sdk"] = s.split("=", 1)[1].strip()
            elif s.startswith("lastUpdateTime="):
                current["last_update_time"] = s.split("=", 1)[1].strip()
            elif s.startswith("codePath="):
                current["path"] = s.split("=", 1)[1].strip()

    if current:
        versions.append(current)

    versions = [v for v in versions if v.get("version_code") or v.get("version_name")]

    if not versions:
        return {"installed": False, "error": f"包 {package_name} 未安装", "package": package_name}

    # 按 versionCode 降序,第一个为当前生效版本
    versions.sort(key=lambda v: int(v["version_code"]) if v.get("version_code", "").isdigit() else 0, reverse=True)
    active = versions[0]

    return {
        "installed": True,
        "package": package_name,
        "version_name": active["version_name"],
        "version_code": active["version_code"],
        "min_sdk": active["min_sdk"],
        "target_sdk": active["target_sdk"],
        "last_update_time": active["last_update_time"],
        "path": active["path"],
        "versions": versions,
        "multi_version": len(versions) > 1,
    }


def list_installed_packages():
    """列出设备上所有已安装包名"""
    output, err = _run_adb(["shell", "pm", "list", "packages"], timeout=15)
    if err:
        return [], err
    packages = []
    for line in output.splitlines():
        s = line.strip()
        if s.startswith("package:"):
            packages.append(s[len("package:"):])
    return sorted(packages), None


def load_saved_packages():
    """加载已保存的包名列表"""
    if not os.path.isfile(_PACKAGES_FILE):
        return []
    try:
        with open(_PACKAGES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_packages(packages):
    """保存包名列表到 JSON 文件"""
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    try:
        with open(_PACKAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(packages, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add_saved_package(package_name):
    """添加一个包名到已保存列表(去重)"""
    packages = load_saved_packages()
    if package_name not in packages:
        packages.append(package_name)
        save_packages(packages)
    return packages


def remove_saved_package(package_name):
    """从已保存列表移除一个包名"""
    packages = load_saved_packages()
    if package_name in packages:
        packages.remove(package_name)
        save_packages(packages)
    return packages
