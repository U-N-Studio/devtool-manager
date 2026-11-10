"""后端 API 协议加载与校验。

协议文件: share/schema.json,是前后端唯一事实来源。
后端在此校验方法是否在协议内,防止暴露未协议化的方法;
前端 api/ 层按协议生成强类型调用函数。替换后端实现时,
任何实现只要满足该协议即可被前端直接消费。
"""

import json
import os
import sys


def _resolve_protocol_path():
    """定位协议文件。

    优先取 share/schema.json(源码开发态,含 PyInstaller 打包进
    MEIPASS 的情况),否则向上三级找 backend/implementations/python -> share/schema.json。
    """
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "share", "schema.json"),
    ]
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.insert(0, os.path.join(meipass, "share", "schema.json"))
    for p in candidates:
        if os.path.isfile(p):
            return p
    return candidates[-1]


_PROTOCOL_PATH = _resolve_protocol_path()


def _load_protocol():
    """加载协议文件;失败时返回空协议(不阻塞后端启动)。"""
    try:
        with open(_PROTOCOL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"methods": [], "notifications": [], "errorCodes": {}}


_protocol = _load_protocol()

# 协议声明的 RPC 方法名集合
_METHODS = {m["name"] for m in _protocol.get("methods", [])}
# 协议声明的通知名集合
_NOTIFICATIONS = {n["name"] for n in _protocol.get("notifications", [])}


def is_known_method(method: str) -> bool:
    """判断方法名是否在协议中声明。"""
    return method in _METHODS


def is_known_notification(name: str) -> bool:
    """判断通知名是否在协议中声明。"""
    return name in _NOTIFICATIONS


def method_requires_params(method: str) -> bool:
    """协议中该方法的 params 是否允许为空。"""
    return True
