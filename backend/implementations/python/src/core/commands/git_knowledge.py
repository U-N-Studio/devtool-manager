"""Git 命令的中文说明知识库。

包含:
- 子命令中文说明字典
- 各子命令的参数/选项中文说明
- 路径位置参数(placeholders)的中文说明

数据存放在 data/git_knowledge.json(实现无关,任何语言可读),
来源:git 官方文档(https://git-scm.com/docs/git),人工翻译整理。
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


def _load_git_knowledge():
    """从 backend/data/git_knowledge.json 加载 git 中文知识库。

    数据目录与实现目录同级(backend/data/),任何后端实现语言均可读取。
    """
    path = os.path.join(_resolve_data_dir(), "git_knowledge.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_data = _load_git_knowledge()

# git 子命令中文说明
GIT_SUBCOMMANDS = _data.get("GIT_SUBCOMMANDS", {})
# 各子命令参数/选项/路径占位符的中文说明
GIT_SUBCOMMAND_PARAMS = _data.get("GIT_SUBCOMMAND_PARAMS", {})


def get_git_subcommand_description(sub: str) -> str:
    """获取 git 子命令的中文说明。"""
    return GIT_SUBCOMMANDS.get(sub, "")


def get_git_subcommand_params(sub: str) -> dict:
    """获取 git 子命令的参数中文说明字典。

    返回 {"flag_or_placeholder": "中文说明"} 字典。
    """
    return GIT_SUBCOMMAND_PARAMS.get(sub, {})
