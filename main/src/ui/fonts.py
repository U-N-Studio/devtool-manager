import sys

_CJK_FONT = "Microsoft YaHei UI" if sys.platform == "win32" else "Noto Sans CJK SC"


def font(size=13, weight="normal", family=None):
    fam = family or _CJK_FONT
    return (fam, size)
