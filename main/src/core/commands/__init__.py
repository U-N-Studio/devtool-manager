"""命令管理子包。

聚合命令定义 (:mod:`.definitions`)、配置探测 (:mod:`.probes`) 与术语表
(:mod:`.glossary`),对外统一导出常用入口。
"""

from src.core.commands.definitions import (
    get_command_names,
    load_command_detail,
    clear_cache,
)
from src.core.commands.probes import probe_command
from src.core.commands.glossary import get_description

__all__ = [
    "get_command_names",
    "load_command_detail",
    "clear_cache",
    "probe_command",
    "get_description",
]
