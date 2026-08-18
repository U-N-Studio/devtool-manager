# 架构决策记录

## ADR-001: CustomTkinter 作为 GUI 框架

- **状态**: 已采纳
- **背景**: 需要跨平台现代风格 GUI
- **决策**: 使用 CustomTkinter（基于 tkinter，现代外观，轻量）
- **替代方案**: tkinter（过时外观）、PyQt6（体积大、许可证限制）

## ADR-002: src 分层结构

- **状态**: 已采纳
- **背景**: 需要分离核心逻辑与 UI，便于测试和维护
- **决策**: `src/core`（业务逻辑）+ `src/ui`（界面）+ `src/utils`（工具）

## ADR-003: PyInstaller --onefile --windowed 打包

- **状态**: 已采纳
- **背景**: 需要单文件无控制台 exe 分发
- **决策**: 使用 `--onefile --windowed`，配合 `--collect-data` 收集 CustomTkinter 资源
- **后果**: `sys.executable` 指向 exe 自身，需 `python_finder.py` 找系统 Python；subprocess 需 `CREATE_NO_WINDOW` 防挂起
