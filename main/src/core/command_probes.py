import sys
import os
import subprocess
import json
import shutil

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def _run(args, timeout=5):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           creationflags=_SUBPROCESS_FLAGS, shell=True)
        return (r.stdout or "") + (r.stderr or "")
    except Exception:
        return ""


def _npm_probe():
    sections = []
    if not shutil.which("npm"):
        return sections

    out = _run(["npm", "config", "list", "--json"], timeout=5)
    if out:
        try:
            cfg = json.loads(out)
            items = []
            for k, v in sorted(cfg.items()):
                items.append({"key": k, "value": str(v)})
            if items:
                sections.append({"level": "合并生效配置", "items": items})
        except Exception:
            pass

    for cmd_str, label in [("npm config get prefix --global", "全局前缀"), ("npm config get cache", "缓存目录")]:
        out = _run(cmd_str, timeout=3)
        val = out.strip()
        if val and "undefined" not in val:
            sections.append({"level": label, "items": [{"key": "path", "value": val}]})

    out = _run(["npm", "config", "list"], timeout=5)
    if out:
        lines = [l for l in out.splitlines() if l.strip() and not l.startswith(";")]
        if lines:
            global_items, user_items, project_items = [], [], []
            current = global_items
            for l in lines:
                if "globalconfig" in l.lower():
                    current = global_items
                elif "userconfig" in l.lower():
                    current = user_items
                elif "project config" in l.lower() or l.startswith("; project"):
                    current = project_items
                elif "=" in l:
                    k, v = l.split("=", 1)
                    current.append({"key": k.strip(), "value": v.strip()})
            for items, label in [(global_items, "全局"), (user_items, "用户"), (project_items, "项目")]:
                if items:
                    sections.append({"level": label, "items": items})

    out = _run(["npm", "ls", "-g", "--depth=0", "--json"], timeout=5)
    if out:
        try:
            deps = json.loads(out).get("dependencies", {})
            items = [{"key": k, "value": v.get("version", "?")} for k, v in sorted(deps.items())]
            if items:
                sections.append({"level": "全局安装包", "items": items})
        except Exception:
            pass

    return sections


def _pip_probe():
    sections = []
    py = sys.executable
    if not shutil.which(py):
        return sections

    out = _run([py, "-m", "pip", "config", "list"], timeout=5)
    if out and out.strip():
        items = []
        for l in out.strip().splitlines():
            if "=" in l:
                k, v = l.split("=", 1)
                items.append({"key": k.strip(), "value": v.strip()})
        if items:
            sections.append({"level": "合并生效配置", "items": items})

    for action, label in [("global", "全局"), ("user", "用户"), ("site", "站点 (venv)")]:
        out = _run([py, "-m", "pip", "config", "list", f"--{action}"], timeout=3)
        if out and out.strip():
            items = []
            for l in out.strip().splitlines():
                if "=" in l:
                    k, v = l.split("=", 1)
                    items.append({"key": k.strip(), "value": v.strip()})
            if items:
                sections.append({"level": label, "items": items})

    return sections


def _git_probe():
    sections = []
    if not shutil.which("git"):
        return sections

    out = _run(["git", "config", "--list", "--show-origin"], timeout=5)
    if out:
        levels = {}
        for l in out.strip().splitlines():
            parts = l.split(None, 1)
            if len(parts) == 2:
                origin, kv = parts
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    level = "系统" if "system" in origin.lower() else ("全局" if "global" in origin.lower() or origin.endswith(".gitconfig") else "本地 (项目)")
                    levels.setdefault(level, []).append({"key": k, "value": v, "origin": origin})
        for label in ["系统", "全局", "本地 (项目)"]:
            items = levels.get(label, [])
            if items:
                sections.append({"level": label, "items": items})

    return sections


def _gradle_probe():
    sections = []
    if not shutil.which("gradle"):
        return sections

    out = _run(["gradle", "properties", "--quiet"], timeout=10)
    if out:
        items = []
        for l in out.strip().splitlines():
            if ": " in l:
                k, v = l.split(": ", 1)
                items.append({"key": k.strip(), "value": v.strip()})
        if items:
            sections.append({"level": "属性", "items": items})

    return sections


def _maven_probe():
    sections = []
    if not shutil.which("mvn"):
        return sections

    m2 = os.path.join(os.environ.get("USERPROFILE", ""), ".m2")
    settings = os.path.join(m2, "settings.xml")
    items = []
    if os.path.isfile(settings):
        items.append({"key": "settings.xml", "value": settings})
    repo = os.path.join(m2, "repository")
    if os.path.isdir(repo):
        items.append({"key": "localRepository", "value": repo})
    if items:
        sections.append({"level": "用户", "items": items})

    m2_conf = os.path.join(os.environ.get("MAVEN_HOME", ""), "conf", "settings.xml")
    if os.path.isfile(m2_conf):
        sections.append({"level": "全局", "items": [{"key": "settings.xml", "value": m2_conf}]})

    return sections


def _cargo_probe():
    sections = []
    if not shutil.which("cargo"):
        return sections

    cargo_home = os.environ.get("CARGO_HOME", os.path.join(os.environ.get("USERPROFILE", ""), ".cargo"))
    items = []
    bin_dir = os.path.join(cargo_home, "bin")
    if os.path.isdir(bin_dir):
        items.append({"key": "bin", "value": bin_dir})
    config = os.path.join(cargo_home, "config.toml")
    if os.path.isfile(config):
        items.append({"key": "config.toml", "value": config})
    if items:
        sections.append({"level": "用户 (CARGO_HOME)", "items": items})

    return sections


def _go_probe():
    sections = []
    if not shutil.which("go"):
        return sections

    out = _run(["go", "env"], timeout=5)
    if out:
        items = []
        for l in out.strip().splitlines():
            if "=" in l:
                k, v = l.split("=", 1)
                v = v.strip().strip('"')
                items.append({"key": k.strip(), "value": v})
        if items:
            sections.append({"level": "Go 环境变量", "items": items})

    return sections


def _conda_probe():
    sections = []
    if not shutil.which("conda"):
        return sections

    out = _run(["conda", "info", "--json"], timeout=5)
    if out:
        try:
            info = json.loads(out)
            items = []
            for k in ["active_prefix", "conda_prefix", "envs_dirs", "pkgs_dirs", "channels", "default_prefix"]:
                v = info.get(k)
                if v:
                    items.append({"key": k, "value": str(v) if not isinstance(v, list) else "; ".join(v)})
            if items:
                sections.append({"level": "Conda 信息", "items": items})
        except Exception:
            pass

    out = _run(["conda", "config", "--show-sources"], timeout=5)
    if out and out.strip():
        current_level = "未知"
        items = []
        for l in out.strip().splitlines():
            if l.strip().endswith(":") and not "=" in l:
                if items:
                    sections.append({"level": current_level, "items": items})
                    items = []
                current_level = l.strip().rstrip(":")
            elif "=" in l:
                k, v = l.split("=", 1)
                items.append({"key": k.strip(), "value": v.strip()})
        if items:
            sections.append({"level": current_level, "items": items})

    return sections


_PROBE_FUNCS = {
    "npm": _npm_probe,
    "pip": _pip_probe,
    "git": _git_probe,
    "gradle": _gradle_probe,
    "mvn": _maven_probe,
    "cargo": _cargo_probe,
    "go": _go_probe,
    "conda": _conda_probe,
    "pnpm": _npm_probe,
    "yarn": _npm_probe,
}


def probe_command(name: str) -> list:
    func = _PROBE_FUNCS.get(name)
    if func:
        return func()
    return []
