import threading
from typing import Callable, Any


class Observable:
    _ui_scheduler: Callable[[Callable], None] = None

    @classmethod
    def set_ui_scheduler(cls, scheduler: Callable[[Callable], None]):
        cls._ui_scheduler = scheduler

    def __init__(self, value: Any = None):
        self._value = value
        self._callbacks: list[Callable] = []

    @property
    def value(self) -> Any:
        return self._value

    def set(self, value: Any):
        if self._value != value:
            self._value = value
            self._notify(value)

    def _notify(self, value: Any):
        for cb in self._callbacks:
            if threading.current_thread() is not threading.main_thread() and self._ui_scheduler:
                self._ui_scheduler(lambda c=cb, v=value: c(v))
            else:
                cb(value)

    def on_change(self, callback: Callable):
        self._callbacks.append(callback)
        if self._value is not None:
            callback(self._value)

    def unbind(self, callback: Callable):
        self._callbacks.remove(callback)

    def __repr__(self):
        return f"Observable({self._value!r})"
