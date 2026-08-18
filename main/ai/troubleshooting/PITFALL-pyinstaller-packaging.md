# 踩坑记录

## PITFALL-001: PyInstaller 打包后 subprocess 无限循环

- **现象**: 打包后 exe 启动时无限打开自身
- **原因**: `sys.executable` 在 frozen 环境下指向 exe 自身，`subprocess([sys.executable, "-m", "pip", ...])` 又启动了 GUI
- **解决**: `src/utils/python_finder.py` 在 frozen 环境下用 `shutil.which("python3")` 找系统 Python

## PITFALL-002: --windowed 模式 subprocess 挂起

- **现象**: exe 启动后卡很久无响应
- **原因**: `--windowed` 无控制台，subprocess 子进程等待控制台输入
- **解决**: 所有 subprocess 调用加 `creationflags=subprocess.CREATE_NO_WINDOW`

## PITFALL-003: CustomTkinter 资源打包缺失

- **现象**: 打包后 exe 运行报 CustomTkinter 主题文件找不到
- **解决**: PyInstaller 加 `--collect-data customtkinter`
