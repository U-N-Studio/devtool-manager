"""配置项术语表。

术语数据存放在 data/glossary.json(实现无关,任何语言可读),
维护开发工具常见配置键(如 registry / GOROOT / JAVA_HOME)的中文释义,
供命令详情页在展示配置项时附加说明。
"""

import json
import os
import sys


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


def _load_glossary():
    """从 backend/data/glossary.json 加载术语表。

    数据目录与实现目录同级(backend/data/),任何后端实现语言均可读取。
    """
    path = os.path.join(_resolve_data_dir(), "glossary.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_GLOSSARY = _load_glossary()


def get_description(key: str) -> str:
    return _GLOSSARY.get(key, "")
