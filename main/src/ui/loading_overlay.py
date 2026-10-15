"""全局加载遮罩。

引用计数式遮罩:任一 ViewModel 标记加载时显示旋转指示器,
全部空闲后销毁,避免并发加载时遮罩闪烁。
"""

import customtkinter as ctk

from src.ui.fonts import font as _font


class LoadingOverlay:
    """全局旋转进度框覆盖层。任一 viewmodel 加载时显示,全部空闲时隐藏。"""

    def __init__(self, parent):
        self._parent = parent
        self._overlay = None
        self._spinner = None
        self._label = None
        self._loading_count = 0
        self._after_id = None
        self._angle = 0

    def show(self, msg="加载中..."):
        self._loading_count += 1
        self._ensure_overlay()
        if self._label:
            self._label.configure(text=msg)
        if not self._after_id:
            self._animate()
        self._overlay.lift()

    def hide(self):
        if self._loading_count > 0:
            self._loading_count -= 1
        if self._loading_count <= 0:
            self._loading_count = 0
            self._destroy_overlay()

    def _ensure_overlay(self):
        if self._overlay is not None:
            return
        self._overlay = ctk.CTkFrame(self._parent, fg_color=("gray90", "gray17"),
                                    corner_radius=12)
        self._overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.3, relheight=0.25)

        container = ctk.CTkFrame(self._overlay, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        self._spinner = ctk.CTkLabel(container, text="◐", font=_font(size=36),
                                     text_color="#4A90D9")
        self._spinner.pack(pady=(0, 12))

        self._label = ctk.CTkLabel(container, text="加载中...", font=_font(size=13),
                                   text_color=("gray20", "gray80"))
        self._label.pack()

    def _animate(self):
        if self._overlay is None:
            self._after_id = None
            return
        self._angle = (self._angle + 30) % 360
        glyphs = ["◐", "◓", "◑", "◒", "◷", "◶", "◵", "◴"]
        idx = (self._angle // 45) % len(glyphs)
        if self._spinner and self._overlay.winfo_exists():
            self._spinner.configure(text=glyphs[idx])
        self._after_id = self._parent.after(100, self._animate)

    def _destroy_overlay(self):
        if self._after_id:
            self._parent.after_cancel(self._after_id)
            self._after_id = None
        if self._overlay is not None:
            try:
                self._overlay.destroy()
            except Exception:
                pass
            self._overlay = None
            self._spinner = None
            self._label = None
            self._angle = 0
