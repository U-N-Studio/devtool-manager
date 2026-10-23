"""DevTool Manager RPC handlers.

将 JSON-RPC 方法分发到 main/src/core/ 业务逻辑层。所有 handler 接收 params dict,
返回 JSON-serializable 结果。executor.execute 特殊:接收 notify 回调,返回 sessionId,
实际输出/完成通过 notification 异步推送。
"""

import os
import shutil
import threading
import uuid

from src.core.env import (
    get_python_version,
    get_pip_version,
    get_platform,
    get_executable,
    get_categorized_env_vars,
    get_system_and_user_env_vars,
    set_env_var,
    delete_env_var,
)
from src.core.tools import get_tool_info
from src.core.packages import (
    get_categorized_packages,
    install_package,
    uninstall_package,
)
from src.core.commands import (
    get_command_names,
    load_command_detail,
    get_description,
)
from src.core.executor import CommandExecutor

_executors: dict[str, CommandExecutor] = {}
_executors_lock = threading.Lock()


def handle_ping(_params):
    return {"pong": True}


def handle_env_list(_params):
    return {"items": get_categorized_env_vars()}


def handle_env_python_info(_params):
    return {
        "version": get_python_version(),
        "pip": get_pip_version(),
        "platform": get_platform(),
        "executable": get_executable(),
    }


def handle_env_set_var(params):
    name = params["name"]
    value = params["value"]
    source = params.get("source", "user")
    set_env_var(name, value, source)
    return {"ok": True}


def handle_env_delete_var(params):
    name = params["name"]
    source = params.get("source", "user")
    delete_env_var(name, source)
    return {"ok": True}


def _modify_path_entries(params, add: bool):
    """读取现有 PATH, 追加或移除条目, 写回注册表。"""
    entry = params["value"]
    source = params.get("source", "user")
    system_vars, user_vars = get_system_and_user_env_vars()
    current = system_vars.get("PATH", "") if source == "system" else user_vars.get("PATH", "")
    entries = [e.strip() for e in current.split(";") if e.strip()]
    if add:
        if entry in entries:
            return {"ok": True}
        entries.append(entry)
    else:
        entries = [e for e in entries if e != entry]
    new_path = ";".join(entries)
    set_env_var("PATH", new_path, source)
    return {"ok": True}


def handle_env_add_path_entry(params):
    return _modify_path_entries(params, add=True)


def handle_env_delete_path_entry(params):
    return _modify_path_entries(params, add=False)


def handle_env_get_raw_path(params):
    source = params.get("source", "user")
    system_vars, user_vars = get_system_and_user_env_vars()
    value = system_vars.get("PATH", "") if source == "system" else user_vars.get("PATH", "")
    return {"value": value}


def handle_tools_info(params):
    category = params.get("category", "")
    info = get_tool_info(category)
    # 统一字段:details 转换为 {label, value} 列表
    details_list = []
    for d in info.get("details", []):
        if isinstance(d, str):
            # 形如 "java: openjdk version \"17.0.1\""
            if ":" in d:
                label, value = d.split(":", 1)
                details_list.append({"label": label.strip(), "value": value.strip()})
            else:
                details_list.append({"label": "info", "value": d.strip()})
        elif isinstance(d, dict):
            details_list.append(d)
    info["details"] = details_list
    return info


def handle_packages_list(params):
    func = params.get("func", "")
    lang = params.get("lang", "")
    install = params.get("install", "")
    raw = get_categorized_packages(func, lang, install)
    items = []
    for p in raw:
        items.append({
            "name": p["name"],
            "version": p.get("version", ""),
            "installed": p.get("install_tag") == "Installed",
            "func_tag": p.get("func_tag", "Other"),
            "lang_tag": p.get("lang_tag", "Python"),
        })
    return {"items": items}


def handle_packages_install(params):
    ok, output = install_package(params["name"])
    return {"ok": ok, "output": output}


def handle_packages_uninstall(params):
    ok, output = uninstall_package(params["name"])
    return {"ok": ok, "output": output}


def handle_commands_list(params):
    names = get_command_names()
    installed_only = params.get("installed_only")
    items = []
    for n in names:
        is_installed = shutil.which(n) is not None
        if installed_only and not is_installed:
            continue
        items.append({"name": n, "installed": is_installed})
    return {"items": items}


def handle_commands_detail(params):
    return load_command_detail(params["name"])


def handle_commands_description(params):
    return {"text": get_description(params["name"])}


def handle_executor_execute(params, notify):
    """启动子进程执行命令, 立即返回 sessionId。

    输出通过 notify("executor.output", {...}) 推送,
    完成时通过 notify("executor.done", {...}) 推送。
    """
    session_id = str(uuid.uuid4())
    executor = CommandExecutor()
    with _executors_lock:
        _executors[session_id] = executor

    def _decode(line):
        if isinstance(line, bytes):
            return line.decode("utf-8", errors="replace")
        return line

    def on_output(line):
        notify("executor.output", {
            "sessionId": session_id,
            "stream": "stdout",
            "line": _decode(line),
        })

    def on_error(line):
        notify("executor.output", {
            "sessionId": session_id,
            "stream": "stderr",
            "line": _decode(line),
        })

    def on_done(exit_code):
        notify("executor.done", {
            "sessionId": session_id,
            "exitCode": exit_code,
        })
        with _executors_lock:
            _executors.pop(session_id, None)

    executor.execute(
        params["command"],
        cwd=params.get("cwd"),
        on_output=on_output,
        on_error=on_error,
        on_done=on_done,
        env=params.get("env"),
    )
    return {"sessionId": session_id}


def handle_executor_kill(params):
    with _executors_lock:
        executor = _executors.get(params["sessionId"])
    if executor:
        executor.kill()
        return {"ok": True}
    return {"ok": False}


def handle_shutdown(_params):
    with _executors_lock:
        for executor in _executors.values():
            try:
                executor.kill()
            except Exception:
                pass
        _executors.clear()
    return {}


HANDLERS = {
    "ping": handle_ping,
    "env.list": handle_env_list,
    "env.python_info": handle_env_python_info,
    "env.set_var": handle_env_set_var,
    "env.delete_var": handle_env_delete_var,
    "env.add_path_entry": handle_env_add_path_entry,
    "env.delete_path_entry": handle_env_delete_path_entry,
    "env.get_raw_path": handle_env_get_raw_path,
    "tools.info": handle_tools_info,
    "packages.list": handle_packages_list,
    "packages.install": handle_packages_install,
    "packages.uninstall": handle_packages_uninstall,
    "commands.list": handle_commands_list,
    "commands.detail": handle_commands_detail,
    "commands.description": handle_commands_description,
    "executor.kill": handle_executor_kill,
    "shutdown": handle_shutdown,
}
