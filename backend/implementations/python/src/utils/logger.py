"""统一日志器。

提供带时间戳的 StreamHandler,供各模块通过 ``get_logger(name)`` 获取
共享日志器实例。
"""

import logging


def get_logger(name="devtool", level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
