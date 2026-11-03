"""环境变量管理核心。

按语言/平台分类读取系统与用户环境变量(含注册表源),支持变量的增删改与
PATH 条目管理,修改后广播 WM_SETTINGCHANGE 使新进程感知变更。
"""

import sys
import os
import subprocess
import ctypes
import winreg

from src.utils.python_finder import get_python_executable

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

# Windows 注册表环境变量存储位置:HKLM 为系统级,HKCU 为用户级
_HKLM_ENV = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
_HKCU_ENV = r"Environment"
# 修改环境变量后广播 WM_SETTINGCHANGE 消息,让新进程感知变更
_WM_SETTINGCHANGE = 0x001A

# 按语言/平台分类的常见环境变量清单,用于 UI 分组展示
ENV_CATEGORIES = {
    "Java": [
        "JAVA_HOME", "JRE_HOME", "JDK_HOME", "CLASSPATH",
        "JAVA_OPTS", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS",
        "GRADLE_HOME", "MAVEN_HOME", "M2_HOME", "ANT_HOME",
    ],
    "Python": [
        "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONIOENCODING",
        "PYTHONUTF8", "PYTHONHASHSEED", "PIP_INDEX_URL", "PIP_TARGET",
        "CONDA_PREFIX", "VIRTUAL_ENV", "POETRY_HOME",
    ],
    "Android": [
        "ANDROID_HOME", "ANDROID_SDK_ROOT", "ANDROID_NDK_HOME",
        "ANDROID_SDK_HOME", "ANDROID_AVD_HOME",
        "ANDROID_PLATFORM_TOOLS", "ANDROID_BUILD_TOOLS",
    ],
    "Node.js": [
        "NODE_HOME", "NODE_PATH", "NPM_CONFIG_PREFIX",
        "NPM_CONFIG_REGISTRY", "NPM_TOKEN", "NPM_HOME",
        "YARN_HOME", "PNPM_HOME", "BUN_INSTALL",
    ],
    "Go": [
        "GOROOT", "GOPATH", "GOBIN", "GOOS", "GOARCH", "GOMODCACHE",
    ],
    "Rust": [
        "RUSTUP_HOME", "CARGO_HOME", "RUST_SRC_PATH",
    ],
    "C/C++": [
        "MINGW_HOME", "MSYS2_HOME", "CYGWIN_HOME",
        "GCC_HOME", "CLANG_HOME", "LLVM_HOME",
        "CMAKE_HOME", "MAKE_HOME",
        "VCPKG_ROOT", "CONAN_HOME",
    ],
    "Dotnet": [
        "DOTNET_HOME", "DOTNET_ROOT", "DOTNET_INSTALL_DIR",
        "NUGET_PACKAGES", "NUGET_HTTP_CACHE",
    ],
    "Docker": [
        "DOCKER_HOME", "DOCKER_CONFIG", "DOCKER_HOST",
        "COMPOSE_HOME", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME",
    ],
    "Git": [
        "GIT_HOME", "GIT_INSTALL_ROOT", "GIT_EXEC_PATH",
        "GIT_EDITOR", "GIT_CONFIG_GLOBAL",
    ],
    "IDE": [
        "IDEA_HOME", "IDEA_PROPERTIES", "WEBIDE_HOME",
        "VSCODE_HOME", "VSCODE_EXTENSIONS",
        "PYCHARM_HOME", "ANDROID_STUDIO_HOME",
    ],
    "Proxy": [
        "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY",
        "NO_PROXY", "ALL_PROXY",
        "http_proxy", "https_proxy", "no_proxy",
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
            [py, "-m", "pip", "--version"],
            text=True,
            creationflags=_SUBPROCESS_FLAGS,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
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
    """读取注册表中某 hive/路径下的全部环境变量,键统一转为大写。"""
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
    """分别读取系统级(HKLM)与用户级(HKCU)注册表环境变量。"""
    system_vars = _read_registry_vars(winreg.HKEY_LOCAL_MACHINE, _HKLM_ENV)
    user_vars = _read_registry_vars(winreg.HKEY_CURRENT_USER, _HKCU_ENV)
    return system_vars, user_vars


def _broadcast_env_change():
    """广播 WM_SETTINGCHANGE,通知资源管理器/新进程环境已变更。"""
    try:
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, _WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, None)
    except Exception:
        pass


def set_env_var(name: str, value: str, source: str = "user"):
    """设置环境变量:写入注册表 + 更新当前进程环境 + 广播变更消息。

    source 为 "system" 时写 HKLM(系统级),否则写 HKCU(用户级)。
    """
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
    """删除环境变量:从注册表移除 + 更新当前进程环境 + 广播变更消息。"""
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
    """判断变量来源:注册表 user 键中存在归为 user,否则归为 system。"""
    upper = name.upper()
    if upper in system_vars:
        return "system"
    if upper in user_vars:
        return "user"
    return "system"


def get_categorized_env_vars():
    """组装全部分类环境变量:按 ENV_CATEGORIES 分类,追加 PATH 条目与其他未分类变量。"""
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
    """把 PATH 按分号拆成单个条目列表(供按语言关键字归类)。"""
    path_value = all_vars.get("PATH", "")
    source = classify_env_var("PATH", system_vars, user_vars)
    entries = [e.strip() for e in path_value.split(";") if e.strip()]
    return [{"name": "PATH", "value": e, "source": source, "is_path_entry": True} for e in entries]


def _classify_path_entries(path_entries):
    """根据路径文本中的语言关键字,把 PATH 条目归类到对应分类下。"""
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
