"""命令历史与收藏的本地持久化。

使用 JSON 文件存储在用户主目录下的 ``.devtool-manager`` 文件夹,跨会话保留。
历史最多保留 200 条,收藏无上限。
"""

import json
import os
import time
import uuid
import threading
from pathlib import Path

_DATA_DIR = Path.home() / ".devtool-manager"
_HISTORY_FILE = _DATA_DIR / "history.json"
_FAVORITES_FILE = _DATA_DIR / "favorites.json"
_MAX_HISTORY = 200
_lock = threading.Lock()


def _ensure_dir():
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _write_json(path: Path, data):
    _ensure_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def list_history():
    with _lock:
        return {"items": _read_json(_HISTORY_FILE, [])}


def add_history(command: str, exit_code=None):
    entry = {
        "id": str(uuid.uuid4()),
        "command": command,
        "timestamp": int(time.time()),
        "exitCode": exit_code,
    }
    with _lock:
        items = _read_json(_HISTORY_FILE, [])
        items.insert(0, entry)
        items = items[:_MAX_HISTORY]
        _write_json(_HISTORY_FILE, items)
    return {"ok": True}


def clear_history():
    with _lock:
        _write_json(_HISTORY_FILE, [])
    return {"ok": True}


def delete_history(entry_id: str):
    with _lock:
        items = _read_json(_HISTORY_FILE, [])
        items = [i for i in items if i.get("id") != entry_id]
        _write_json(_HISTORY_FILE, items)
    return {"ok": True}


def list_favorites():
    with _lock:
        return {"items": _read_json(_FAVORITES_FILE, [])}


def add_favorite(command: str, label: str = ""):
    with _lock:
        items = _read_json(_FAVORITES_FILE, [])
        if any(i.get("command") == command for i in items):
            return {"ok": True}
        items.append({
            "command": command,
            "label": label or command,
            "timestamp": int(time.time()),
        })
        _write_json(_FAVORITES_FILE, items)
    return {"ok": True}


def remove_favorite(command: str):
    with _lock:
        items = _read_json(_FAVORITES_FILE, [])
        items = [i for i in items if i.get("command") != command]
        _write_json(_FAVORITES_FILE, items)
    return {"ok": True}
