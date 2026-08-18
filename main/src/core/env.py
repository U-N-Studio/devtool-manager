import sys
import os
import subprocess
import ctypes
import winreg

from src.utils.python_finder import get_python_executable

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

_HKLM_ENV = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
_HKCU_ENV = r"Environment"
_WM_SETTINGCHANGE = 0x001A

ENV_CATEGORIES = {
    "Java": [
        "JAVA_HOME", "JRE_HOME", "JDK_HOME", "CLASSPATH",
        "JAVA_OPTS", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS",
    ],
    "Python": [
        "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONIOENCODING",
        "PYTHONUTF8", "PYTHONHASHSEED", "PIP_INDEX_URL", "PIP_TARGET",
        "CONDA_PREFIX", "VIRTUAL_ENV",
    ],
    "Android": [
        "ANDROID_HOME", "ANDROID_SDK_ROOT", "ANDROID_NDK_HOME",
        "ANDROID_SDK_HOME", "ANDROID_AVD_HOME",
        "ANDROID_PLATFORM_TOOLS", "ANDROID_BUILD_TOOLS",
    ],
    "Node.js": [
        "NODE_HOME", "NODE_PATH", "NPM_CONFIG_PREFIX",
        "NPM_CONFIG_REGISTRY", "NPM_TOKEN",
    ],
    "Go": [
        "GOROOT", "GOPATH", "GOBIN", "GOOS", "GOARCH", "GOMODCACHE",
    ],
    "Rust": [
        "RUSTUP_HOME", "CARGO_HOME", "RUST_SRC_PATH",
    ],
    "Path": [
        "PATH", "PATHEXT",
    ],
    "System": [
        "COMPUTERNAME", "USERNAME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH",
        "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "OS",
        "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
        "TEMP", "TMP", "COMSPEC", "PSMODULEPATH",
    ],
}

PATH_KEYWORDS = {
    "Java": ["java", "jdk", "jre", "oracle", "openjdk", "gradle", "maven", "ant"],
    "Python": ["python", "pip", "conda", "venv", "virtualenv", "poetry"],
    "Android": ["android", "sdk", "ndk", "adb", "gradle", "avd"],
    "Node.js": ["node", "npm", "npx", "yarn", "pnpm", "bun"],
    "Go": ["go", "golang", "goroot", "gopath"],
    "Rust": ["rust", "cargo", "rustup"],
}


def get_python_version():
    return sys.version


def get_pip_version():
    try:
        py = get_python_executable()
        return subprocess.check_output(
            [py, "-m", "pip", "--version"], text=True, creationflags=_SUBPROCESS_FLAGS
        ).strip()
    except Exception:
        return "N/A"


def get_platform():
    return sys.platform


def get_executable():
    return sys.executable


def get_all_env_vars():
    return dict(os.environ)


def _read_registry_vars(hive, key_path):
    result = {}
    try:
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name:
                        result[name.upper()] = str(value) if not isinstance(value, str) else value
                    i += 1
                except OSError:
                    break
    except OSError:
        pass
    return result


def get_system_and_user_env_vars():
    system_vars = _read_registry_vars(winreg.HKEY_LOCAL_MACHINE, _HKLM_ENV)
    user_vars = _read_registry_vars(winreg.HKEY_CURRENT_USER, _HKCU_ENV)
    return system_vars, user_vars


def _broadcast_env_change():
    try:
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, _WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, None)
    except Exception:
        pass


def set_env_var(name: str, value: str, source: str = "user"):
    if source == "system":
        hive = winreg.HKEY_LOCAL_MACHINE
        key_path = _HKLM_ENV
    else:
        hive = winreg.HKEY_CURRENT_USER
        key_path = _HKCU_ENV

    with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)

    os.environ[name] = value
    _broadcast_env_change()


def delete_env_var(name: str, source: str = "user"):
    if source == "system":
        hive = winreg.HKEY_LOCAL_MACHINE
        key_path = _HKLM_ENV
    else:
        hive = winreg.HKEY_CURRENT_USER
        key_path = _HKCU_ENV

    with winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
        winreg.DeleteValue(key, name)

    os.environ.pop(name, None)
    _broadcast_env_change()


def classify_env_var(name, system_vars, user_vars):
    upper = name.upper()
    if upper in system_vars:
        return "system"
    if upper in user_vars:
        return "user"
    return "system"


def get_categorized_env_vars():
    all_vars = get_all_env_vars()
    system_vars, user_vars = get_system_and_user_env_vars()

    path_entries = _get_path_entries(all_vars, system_vars, user_vars)
    path_by_cat = _classify_path_entries(path_entries)

    result = {}
    for cat_name, var_names in ENV_CATEGORIES.items():
        if cat_name == "Path":
            continue
        items = []
        for var in var_names:
            upper = var.upper()
            if upper in all_vars:
                source = classify_env_var(upper, system_vars, user_vars)
                items.append({"name": var, "value": all_vars[upper], "source": source})
        for pe in path_by_cat.get(cat_name, []):
            items.append(pe)
        if items:
            result[cat_name] = items

    all_path_items = _build_path_items(all_vars, system_vars, user_vars)
    if all_path_items:
        result["Path"] = all_path_items

    categorized_names = set()
    for var_names in ENV_CATEGORIES.values():
        for v in var_names:
            categorized_names.add(v.upper())

    other_system = []
    other_user = []
    for name, value in sorted(all_vars.items()):
        if name.upper() in categorized_names:
            continue
        source = classify_env_var(name, system_vars, user_vars)
        entry = {"name": name, "value": value, "source": source}
        if source == "user":
            other_user.append(entry)
        else:
            other_system.append(entry)

    if other_system:
        result["Other (System)"] = other_system
    if other_user:
        result["Other (User)"] = other_user

    return result


def _get_path_entries(all_vars, system_vars, user_vars):
    path_value = all_vars.get("PATH", "")
    source = classify_env_var("PATH", system_vars, user_vars)
    entries = [e.strip() for e in path_value.split(";") if e.strip()]
    return [{"name": "PATH", "value": e, "source": source, "is_path_entry": True} for e in entries]


def _classify_path_entries(path_entries):
    result = {}
    for entry in path_entries:
        path_lower = entry["value"].lower()
        for cat_name, keywords in PATH_KEYWORDS.items():
            if any(kw in path_lower for kw in keywords):
                result.setdefault(cat_name, []).append(entry)
                break
    return result


def _build_path_items(all_vars, system_vars, user_vars):
    items = []
    for var_name in ("PATH", "PATHEXT"):
        upper = var_name.upper()
        if upper not in all_vars:
            continue
        source = classify_env_var(upper, system_vars, user_vars)
        full_value = all_vars[upper]
        if upper == "PATH":
            entries = [e.strip() for e in full_value.split(";") if e.strip()]
            for entry in entries:
                items.append({"name": "PATH", "value": entry, "source": source, "is_path_entry": True})
        else:
            items.append({"name": var_name, "value": full_value, "source": source})
    return items
