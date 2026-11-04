"""开发工具命令定义与详情加载。

命令清单数据存放在 data/command_defs.json(实现无关,任何语言可读),
本模块负责加载清单并通过执行 --version / --help 解析版本、参数、子命令,
并委托 :mod:`src.core.commands.probes` 探测配置项,最终组装为
供 UI 展示的命令详情字典。
"""

import sys
import os
import json
import re
import subprocess
import shutil

from src.core.commands.probes import probe_command
from src.core.commands.git_knowledge import (
    get_git_subcommand_description,
    get_git_subcommand_params,
)

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def _resolve_data_dir():
    """定位 backend/data 目录。

    源码态:从本文件向上 5 级 = backend/data。
    冻结态(PyInstaller):数据打包在 <MEIPASS>/data/。
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return os.path.join(meipass, "data")
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "data")


def _load_command_defs():
    """从 backend/data/command_defs.json 加载内置命令清单。

    数据目录与实现目录同级(backend/data/),任何后端实现语言均可读取。
    """
    path = os.path.join(_resolve_data_dir(), "command_defs.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# 内置命令清单:每条包含探测版本/帮助用的参数、中文描述与相关环境变量
_COMMAND_DEFS = _load_command_defs()
_CMD_DEFS_MAP = {d["name"]: d for d in _COMMAND_DEFS}

# 命令详情缓存:name -> detail dict,避免重复探测
_cache = {}


def clear_cache():
    _cache.clear()


def _run_cmd(args, timeout=5):
    """执行子进程并合并输出。Windows 上 .cmd/.bat 脚本需 shell=True。"""
    try:
        # Windows 上 npm/pnpm/yarn 等是 .cmd 脚本,需要 shell=True 才能执行
        use_shell = False
        if sys.platform == "win32" and args:
            exe = shutil.which(args[0])
            if exe and exe.lower().endswith((".cmd", ".bat")):
                use_shell = True
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            creationflags=_SUBPROCESS_FLAGS, shell=use_shell,
            encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip()
    except Exception:
        return None


def _extract_params(help_text, max_items=30):
    if not help_text:
        return []
    params = []
    seen = set()
    for line in help_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-") or stripped.startswith("/"):
            parts = stripped.split()
            if parts:
                token = parts[0]
                if token not in seen:
                    seen.add(token)
                    desc = " ".join(parts[1:]) if len(parts) > 1 else ""
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    params.append({"name": token, "description": desc})
                    if len(params) >= max_items:
                        break
    return params


def _extract_subcommands(help_text, max_items=50):
    """从 help 文本中提取子命令列表。

    支持多种格式:
    - git:  "   clone             Clone a repository..." (缩进命令名 + 描述)
    - pip:  "  install                     Install packages."
    - npm:  "    access, adduser, audit, ..." (逗号分隔)
    - adb:  " devices [-l]             list connected devices"
    """
    if not help_text:
        return []
    # adb help 格式特殊:命令名后跟参数再跟描述,交给专用解析器
    if "Android Debug Bridge" in help_text:
        return _extract_adb_subcommands(help_text, max_items)
    subs = []
    seen = set()

    # 模式 1: 缩进行中的命令名 + 描述(git/pip/adb 风格)
    # 要求:行有前导缩进,token 后有较多空格(列对齐)分隔描述
    for line in help_text.splitlines():
        if not line.startswith(" ") and not line.startswith("\t"):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("-") or stripped.startswith("/"):
            continue
        if stripped.endswith(":"):
            continue
        if "see also" in stripped.lower():
            continue
        # 要求 token 和描述之间有 >= 2 个空格(列对齐),排除 "npm install  ..." 这种
        m = re.match(r"^(\S+)\s{2,}(.+)$", stripped)
        if not m:
            continue
        token = m.group(1).rstrip(",")
        if not _is_subcommand_token(token):
            continue
        desc = m.group(2).strip()
        if len(desc) > 80:
            desc = desc[:77] + "..."
        if token not in seen:
            seen.add(token)
            subs.append({"name": token, "description": desc})
            if len(subs) >= max_items:
                break

    # 模式 2: 逗号分隔的命令列表(npm "All commands:" 风格)
    if len(subs) < 3:
        in_cmd_list = False
        for line in help_text.splitlines():
            stripped = line.strip()
            if not stripped:
                if in_cmd_list and subs:
                    break
                continue
            if "all commands" in stripped.lower():
                in_cmd_list = True
                continue
            if in_cmd_list and "," in stripped:
                tokens = [t.strip() for t in stripped.split(",")]
                if all(_is_subcommand_token(t) for t in tokens if t):
                    for token in tokens:
                        token = token.strip()
                        if token and token not in seen and _is_subcommand_token(token):
                            seen.add(token)
                            subs.append({"name": token, "description": ""})
                            if len(subs) >= max_items:
                                break
                    if len(subs) >= max_items:
                        break

    return subs


def _is_subcommand_token(token):
    """判断一个 token 是否像子命令名(纯小写字母/数字/连字符)"""
    if not token or len(token) > 40:
        return False
    if token.startswith("-"):
        return False
    # 子命令必须全小写,只含字母/数字/连字符
    return token.islower() and all(c.isalnum() or c == "-" for c in token) and token[0].isalpha()


# adb 官方命令名白名单(来自 `adb help` 各小节),用于准确提取子命令
_ADB_COMMANDS = {
    "devices", "help", "version", "connect", "disconnect", "pair",
    "forward", "reverse", "ppp", "push", "pull", "sync", "shell", "emu",
    "install", "install-multiple", "install-multi-package", "uninstall",
    "bugreport", "jdwp", "logcat", "disable-verity", "enable-verity",
    "keygen", "wait-for", "get-state", "get-serialno", "get-devpath",
    "remount", "reboot", "sideload", "root", "unroot", "usb", "tcpip",
    "start-server", "kill-server", "reconnect",
}


def _extract_adb_subcommands(help_text, max_items=50):
    """按 adb help 的 section 格式提取子命令。

    adb 每行是 "  <command> [参数...]   <描述>",命令名是行首缩进 token。
    用官方命令白名单匹配行首,避免把参数(如 HOST、tcp:)误当命令。
    描述可能在同行双空格后,也可能在下一行缩进续行里。
    """
    lines = help_text.splitlines()
    subs = []
    seen = set()
    category = ""  # 当前 section 分类
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # section 标题: 缩进 <=1 空格的小写 "xxx:" 行(续行缩进 >=4 不误判)
        indent = len(line) - len(line.lstrip())
        if (
            stripped.endswith(":")
            and indent <= 1
            and not stripped.startswith("-")
        ):
            key = stripped[:-1].split(" (")[0]  # 去掉 "(see also...)" 说明
            category = _ADB_SECTION_CN.get(key, key)
            continue

        token = stripped.split()[0].rstrip(",")
        if token not in _ADB_COMMANDS or token in seen:
            continue
        seen.add(token)
        # 保留 token 后的原始空白(不能 strip,否则双空格信息丢失)
        desc = stripped[len(token):]
        # 同行描述:取双空格之后
        m = re.search(r"\s{2,}(.+)$", desc)
        desc = m.group(1).strip() if m else ""
        # 若无同行描述,看下一行是否为 4+ 空格缩进的续行(adb 命令续行风格)
        if not desc and i + 1 < len(lines):
            nxt_line = lines[i + 1]
            indent = len(nxt_line) - len(nxt_line.lstrip())
            nxt_stripped = nxt_line.strip()
            if nxt_stripped and indent >= 4 and not nxt_stripped.startswith("-"):
                desc = nxt_stripped
        if len(desc) > 80:
            desc = desc[:77] + "..."
        # help 命令在版本行("help, 174")被匹配,无描述,手动补充
        if not desc and token == "help":
            desc = "show this help message"
        subs.append({
            "name": token,
            "description": desc,
            "category": category or "基础",
        })
        if len(subs) >= max_items:
            break
    return subs


# adb help section 标题 -> 中文分类标签
_ADB_SECTION_CN = {
    "general commands": "基础",
    "networking": "网络连接",
    "file transfer": "文件传输",
    "shell": "Shell",
    "app installation": "应用安装",
    "debugging": "调试",
    "security": "安全",
    "scripting": "脚本化",
    "internal debugging": "内部调试",
}


def _load_adb_params():
    """加载 adb 子命令常用参数(静态数据,避免运行探测挂起)。"""
    data_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "..", "data",
    )
    path = os.path.join(data_dir, "adb_params.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _resolve_env_values(env_var_names):
    result = []
    for name in env_var_names:
        value = os.environ.get(name, "")
        result.append({"name": name, "value": value, "set": bool(value)})
    return result


def get_command_names():
    return [d["name"] for d in _COMMAND_DEFS]


def load_command_detail(name: str) -> dict:
    if name in _cache:
        return _cache[name]

    cmd_def = _CMD_DEFS_MAP.get(name, {})
    path = shutil.which(name)
    installed = path is not None

    version = ""
    help_text = ""
    if installed and cmd_def.get("version_args"):
        output = _run_cmd([name] + cmd_def["version_args"])
        if output:
            first_line = output.splitlines()[0] if output.splitlines() else output
            version = first_line.strip()

    if installed and cmd_def.get("help_args"):
        help_text = _run_cmd([name] + cmd_def["help_args"], timeout=5) or ""

    subcommands = _extract_subcommands(help_text) if help_text else []

    # git 子命令: 用中文知识库覆盖描述,并标记是否有参数
    if name == "git":
        for sub in subcommands:
            cn_desc = get_git_subcommand_description(sub["name"])
            if cn_desc:
                sub["description"] = cn_desc
            sub["has_params"] = bool(get_git_subcommand_params(sub["name"]))
        # 补充知识库中存在但 help 未列出的子命令
        existing_names = {s["name"] for s in subcommands}
        from src.core.commands.git_knowledge import GIT_SUBCOMMANDS
        for sub_name, cn_desc in GIT_SUBCOMMANDS.items():
            if sub_name not in existing_names:
                subcommands.append({
                    "name": sub_name,
                    "description": cn_desc,
                    "has_params": bool(get_git_subcommand_params(sub_name)),
                })

    # adb 子命令: 用静态常用参数数据标记 has_params
    elif name == "adb":
        adb_params = _load_adb_params()
        for sub in subcommands:
            sub["has_params"] = len(adb_params.get(sub["name"], [])) > 0

    # 其他命令: 展开时探测,默认认为可能有参数
    else:
        for sub in subcommands:
            sub["has_params"] = True

    env_vars = _resolve_env_values(cmd_def.get("env_vars", []))

    result = {
        "name": name,
        "installed": installed,
        "version": version,
        "path": path or "",
        "description": cmd_def.get("description", ""),
        "subcommands": subcommands,
        "env_vars": env_vars,
        "config_sections": [],
    }
    _cache[name] = result

    if installed:
        result["config_sections"] = probe_command(name)

    return result


def load_subcommand_help(command: str, subcommand: str) -> dict:
    """查询单个子命令的参数与路径位置参数说明。

    对于 git,返回中文知识库中的参数说明;
    对于其他命令,尝试执行 `command subcommand --help` 解析参数。
    """
    result = {
        "command": command,
        "subcommand": subcommand,
        "params": [],
        "pathParams": [],
    }

    if command == "git":
        param_dict = get_git_subcommand_params(subcommand)
        for flag, desc in param_dict.items():
            if flag.startswith("-"):
                result["params"].append({"name": flag, "description": desc})
            else:
                result["pathParams"].append({"name": flag, "description": desc})
        # 限量: 参数最多 6 个,路径参数最多 2 个(展示最常用的)
        result["params"] = result["params"][:6]
        result["pathParams"] = result["pathParams"][:2]
        return result

    # adb 特判: 返回静态常用参数数据,不运行探测(无设备会挂起)
    if command == "adb":
        adb_params = _load_adb_params()
        for p in adb_params.get(subcommand, []):
            if p.get("name", "").startswith("-"):
                result["params"].append(p)
            else:
                result["pathParams"].append(p)
        return result

    # 通用: 执行 `command subcommand --help` 解析参数
    result = _generic_subcommand_help(command, subcommand, result)
    # 限量: 参数最多 6 个
    result["params"] = result["params"][:6]
    result["pathParams"] = result["pathParams"][:2]
    return result


def _generic_subcommand_help(command: str, subcommand: str, result: dict) -> dict:
    """执行 `command subcommand --help`(-h 兜底)解析参数。"""
    path = shutil.which(command)
    if not path:
        return result

    help_text = _run_cmd([command, subcommand, "--help"], timeout=5) or ""
    if not help_text:
        # 尝试 -h
        help_text = _run_cmd([command, subcommand, "-h"], timeout=5) or ""

    if help_text:
        raw_params = _extract_params(help_text, max_items=50)
        result["params"] = raw_params

    return result
