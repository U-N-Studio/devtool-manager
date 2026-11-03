# devtool-manager

Windows 平台本地开发工具管理工具（DevTool Manager），Electron + React 前端 + Python JSON-RPC 后端。

## 架构

```
┌─ electron/ (Electron + React + Vite + TypeScript) ────────┐
│  main/      主进程: 窗口/菜单/pythonBridge(spawn 后端 + RPC) │
│  preload/   安全桥: 暴露 window.api 给渲染层                  │
│  src/       渲染层 (React + Zustand + Tailwind + shadcn/ui) │
│    ├─ api/        后端调用层: 协议视图/传输适配/统一 API      │
│    ├─ components/  commands / env / executor / layout / ui │
│    ├─ stores/      Zustand 状态 (commands/env/executor/…)   │
│    ├─ lib/         ipc.ts (RPC 封装) / types / utils        │
│    └─ styles/      globals.css                              │
└────────────────────────────────────────────────────────────┘
          ▲ IPC (preload 暴露的 window.api)
          │
┌─ backend/ (独立后端服务) ────────────────────────────────────┐
│  protocol/          协议(与实现无关, 唯一事实来源)            │
│    ├─ schema.json   JSON-RPC 2.0 协议: 方法/入参/出参/通知    │
│    └─ README.md     协议文档                                  │
│  data/              命令/术语/知识库数据(与实现同级, 任何实现 │
│    ├─ command_defs.json   37 个内置命令清单                  │
│    ├─ glossary.json       107 条配置术语表                    │
│    └─ git_knowledge.json  git 中文知识库                      │
│  implementations/   具体实现(按语言/技术分类)                 │
│    └─ python/       Python 实现 (当前)                        │
│       ├─ server.py        stdio 入口 + 协议校验               │
│       ├─ rpc_handlers.py  方法分发 (commands/env/…)           │
│       ├─ protocol.py      协议加载与校验                      │
│       ├─ src/core/        业务逻辑: env/tools/packages/…      │
│       └─ devtool-backend.spec  PyInstaller 打包 → exe          │
└────────────────────────────────────────────────────────────┘
```

### 数据流

React 渲染层 → `window.api` (preload) → Electron 主进程 `pythonBridge` → spawn
后端实现进程（开发态 `python ../backend/implementations/python/server.py`，
生产态 `devtool-backend.exe`）→ 通过 stdin/stdout 以一行一条 JSON-RPC 2.0
消息交互 → 结果返回渲染层。

后端实现可替换：新增一个满足 `backend/protocol/schema.json` 的实现的目录即可
（如 `implementations/go/`），前端调用层 (`src/api/`) 零改动。

执行类命令（`executor.execute`）特殊：立即返回 sessionId，stdout/stderr 逐行
通过 `executor.output` 通知异步推送，完成时推送 `executor.done`。

## 功能

- **命令管理**：探测 30+ 开发工具（git/npm/java/android/go/rust…）的版本、参数、
  子命令与配置段；子命令/参数点击插入快捷运行栏；支持默认/字母/自定义（拖拽）排序。
- **快捷运行**：底部输入栏组装 `命令 + 子命令 + 参数`，一键执行，输出实时流入终端面板。
- **历史与收藏**：命令执行历史（最多 200 条）与常用命令收藏，JSON 本地持久化。
- **环境变量**：按语言/平台分类读写系统/用户环境变量（注册表源），修改后广播
  `WM_SETTINGCHANGE`；PATH 条目单独管理。
- **工具信息**：Java/Python/Android/Node/Go/Rust 工具链探测。

## 开发

```bash
# 前端 + 后端 + Electron 一并启动（开发模式）
cd electron
npm run dev:electron
```

或双击根目录 `start-electron.bat`。

- 后端为独立 Python 进程，代码在 `backend/`，改动后重启应用生效（无需重新打包）。
- 前端热更新（Vite），改动即时生效。

## 打包

```bash
# 1) 打包 Python 后端为单 exe（PyInstaller）
cd backend
pyinstaller devtool-backend.spec

# 2) 打包 Electron 应用（electron-builder，内含后端 exe）
cd electron
npm run build:electron
npm run package
```

## 目录说明

| 路径 | 说明 |
|------|------|
| `backend/protocol/` | 后端协议（唯一事实来源，与实现无关） |
| `backend/data/` | 命令/术语/知识库数据（与实现同级，任何实现可读） |
| `backend/implementations/` | 后端具体实现（当前为 `python/`，可扩展其他实现） |
| `electron/` | Electron + React 前端 |
| `docs/` | 架构设计与实现计划文档 |
