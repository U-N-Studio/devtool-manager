import sys

_CJK_FONT = "Microsoft YaHei UI" if sys.platform == "win32" else "Noto Sans CJK SC"
_MONO_FONT = "Consolas" if sys.platform == "win32" else "DejaVu Sans Mono"

# 放大基础字号,提升高 DPI 屏可读性
_SCALE = 1.15


def font(size=13, weight="normal", family=None):
    fam = family or _CJK_FONT
    return (fam, round(size * _SCALE), weight)


def mono(size=12, weight="normal"):
    return (_MONO_FONT, round(size * _SCALE), weight)
