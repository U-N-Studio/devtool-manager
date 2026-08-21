import threading

from src.viewmodel.observable import Observable
from src.core.tools import get_tool_info


class ToolInfoViewModel:
    def __init__(self):
        self.tool_info = Observable({})
        self.is_loading = Observable(False)

    def refresh(self, category: str):
        self.is_loading.set(True)
        thread = threading.Thread(target=self._load, args=(category,), daemon=True)
        thread.start()

    def _load(self, category: str):
        try:
            info = get_tool_info(category)
            self.tool_info.set(info)
        finally:
            self.is_loading.set(False)
