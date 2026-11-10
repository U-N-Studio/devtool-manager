# devtool-manager

Windows 平台本地开发工具管理工具（DevTool Manager），Electron + React 前端 + Python JSON-RPC 后端。

## 架构

```
┌─ frontend/ (React + Vite + TypeScript) ─────────────────────┐
│  src/                                                         │
│    ├─ api/        后端调用层: 传输适配/统一 API               │
│    ├─ components/  commands / executor / layout / ui         │
│    ├─ stores/      Zustand 状态 (commands/env/executor/…)    │
│    ├─ lib/         ipc.ts (RPC 封装) / utils                 │
│    └─ styles/      globals.css                               │
└───────────────────────────────────────────────────────────────┘
           ▲ IPC (window.api)
           │
┌─ share/ (UI端到Electron的接口类型) ──────────────────────────┐
│  types.ts      TypeScript 类型定义                           │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌─ electron/ (Electron 主进程) ───────────────────────────────┐
│  main/      窗口/菜单/pythonBridge                          │
│  preload/   安全桥: 暴露 window.api                         │
└──────────────────────────────────────────────────────────────┘
           │ stdio (JSON-RPC 2.0)
           │
┌─ protocol/ (Electron到后端的接口协议) ──────────────────────┐
│  schema.json   JSON-RPC 2.0 协议定义                        │
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌─ backend/ (独立后端服务) ────────────────────────────────────┐
│  data/              命令/术语/知识库数据                      │
│    ├─ command_defs.json   命令清单                            │
│    ├─ glossary.json       配置术语表                          │
│    └─ git_knowledge.json  git 中文知识库                      │
│  implementations/   后端实现                                  │
│    └─ python/                                                 │
│       ├─ server.py        stdio 入口                          │
│       ├─ rpc_handlers.py  方法分发                            │
│       ├─ protocol.py      协议校验                            │
│       ├─ src/core/        业务逻辑                            │
│       └─ devtool-backend.spec 打包 → exe                      │
└──────────────────────────────────────────────────────────────┘
```

### 协议层

两个独立的协议层，分别连接不同的系统边界：

- **`share/`** — UI端到Electron的接口，定义IPC通信的TypeScript类型
- **`protocol/`** — Electron到后端的接口，定义JSON-RPC 2.0方法/参数/返回值

前端UI通过 `window.api` 调用Electron主进程（类型来自 `share/types.ts`）；
Electron主进程通过 `pythonBridge` 调用后端（遵循 `protocol/schema.json`）。

### 数据流

React 渲染层 → `window.api` (preload) → Electron 主进程 `pythonBridge` → spawn
后端实现进程（开发态 `python ../backend/implementations/python/server.py`，
生产态 `devtool-backend.exe`）→ 通过 stdin/stdout 以一行一条 JSON-RPC 2.0
消息交互 → 结果返回渲染层。

后端实现可替换：新增一个满足 `protocol/schema.json` 的实现的目录即可
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
# 1. 启动前端开发服务器（新窗口）
cd frontend
npm run dev

# 2. 启动 Electron 主进程（另一个窗口）
cd electron
npm start
```

或双击根目录 `start-electron.bat`（自动启动两者）。

- 后端为独立 Python 进程，代码在 `backend/`，改动后重启应用生效（无需重新打包）。
- 前端热更新（Vite），改动即时生效。

## 打包

```bash
# 1) 打包前端
cd frontend
npm run build

# 2) 打包 Python 后端为单 exe（PyInstaller）
cd backend/implementations/python
pyinstaller devtool-backend.spec

# 3) 打包 Electron 应用（electron-builder，内含前端+后端 exe）
cd electron
npm run build
npm run package
```

## 目录说明

| 路径 | 说明 |
|------|------|
| `frontend/` | React 前端（独立模块，可独立开发和构建） |
| `electron/` | Electron 主进程（窗口管理、IPC 桥接、后端进程管理） |
| `protocol/` | Electron到后端的接口协议（JSON-RPC 2.0） |
| `backend/` | Python 后端服务 |
| `backend/data/` | 命令/术语/知识库数据（与实现同级，任何实现可读） |
| `backend/implementations/` | 后端具体实现（当前为 `python/`，可扩展其他实现） |
| `share/` | UI端到Electron的接口类型定义（IPC） |
| `docs/` | 架构设计与实现计划文档 |
