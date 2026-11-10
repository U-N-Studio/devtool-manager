# DevTool Manager 架构文档

## 项目结构

```
devtool-manager/
├── frontend/              # React 前端（独立模块）
│   ├── src/
│   │   ├── components/    # UI 组件（含 ui/ 基础组件）
│   │   ├── stores/        # Zustand 状态管理
│   │   ├── api/           # 后端 API 调用层
│   │   ├── lib/           # 工具函数、IPC、类型重导出
│   │   └── styles/        # 全局样式
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── electron/              # Electron 主进程
│   ├── main/              # 主进程代码
│   │   ├── main.ts        # 入口，IPC 路由
│   │   ├── pythonBridge.ts    # stdio 桥接
│   │   ├── window.ts      # 窗口管理
│   │   └── menu.ts        # 菜单
│   ├── preload/
│   │   └── preload.ts     # contextBridge
│   └── package.json
│
├── backend/               # Python 后端
│   ├── implementations/python/
│   │   ├── server.py      # JSON-RPC stdio 入口
│   │   ├── rpc_handlers.py    # 路由分发
│   │   ├── protocol.py    # 协议校验
│   │   └── src/core/      # 业务逻辑
│   │       ├── env.py
│   │       ├── tools.py
│   │       ├── packages.py
│   │       ├── store.py
│   │       ├── executor.py
│   │       └── commands/
│   └── data/              # 静态数据文件
│
├── protocol/              # 前后端接口协议
│   ├── schema.json        # JSON-RPC 协议定义（事实来源）
│   └── README.md
│
└── share/                 # 前后端共享类型
    ├── types.ts           # TypeScript 类型定义
    └── schema.ts          # 协议元数据（加载 protocol/schema.json）
```

## 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Frontend (frontend/src/)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐ │
│  │ components/ │  │   stores/   │  │         api/                    │ │
│  │  (UI views) │  │ (Zustand)   │  │  ┌─────────┐ ┌──────────────┐  │ │
│  │             │  │             │  │  │client.ts│ │   index.ts   │  │ │
│  └─────────────┘  └─────────────┘  │  └────┬────┘ └──────────────┘  │ │
│                                      │       │                        │ │
│  ┌─────────────────────────────────┐ │  ┌────▼────┐  ┌───────────┐  │ │
│  │           lib/                  │ │  │schema.ts│  │  types.ts │  │ │
│  │  ┌─────────┐  ┌─────────────┐  │ │  └─────────┘  └───────────┘  │ │
│  │  │ ipc.ts  │  │   types.ts  │  │ │                              │ │
│  │  └────┬────┘  └─────────────┘  │ │                              │ │
│  │         │                        │ └────────────────────────────────┘ │
│           │                         │                                   │
└───────────┼─────────────────────────┼───────────────────────────────────┘
            │                         │
            ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 Electron Main Process (electron/)                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │    main.ts      │  │ pythonBridge.ts │  │     preload.ts          │ │
│  │  (IPC routing)  │  │ (stdio bridge)  │  │  (contextBridge)        │ │
│  └────────┬────────┘  └────────┬────────┘  └───────────┬─────────────┘ │
│           │                    │                       │                │
│           └────────────────────┼───────────────────────┘                │
│                                │                                        │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │ stdio (JSON-RPC 2.0)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Backend (Python)                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │   server.py     │  │ rpc_handlers.py │  │    protocol.py          │ │
│  │  (main loop)    │  │  (HANDLERS)     │  │  (schema validation)    │ │
│  └────────┬────────┘  └────────┬────────┘  └───────────┬─────────────┘ │
│           │                    │                       │                │
│           └────────────────────┼───────────────────────┘                │
│                                │                                        │
│  ┌─────────────────────────────▼───────────────────────────────────────┐│
│  │                        src/core/                                    ││
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐ ││
│  │  │  env.py │ │ tools.py│ │packages.py│ │store.py │ │  commands/  │ ││
│  │  └─────────┘ └─────────┘ └──────────┘ └─────────┘ │ definitions │ ││
│  │                                                     │   probes    │ ││
│  │                                                     │  glossary   │ ││
│  │                                                     └─────────────┘ ││
│  │  ┌─────────────────────────────────────────────────────────────────┐││
│  │  │                     executor.py                                │││
│  │  │              (子进程执行器,流式输出)                              │││
│  │  └─────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Runtime (OS/External)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ registry │  │   PATH   │  │  git/npm │  │  python  │  │   adb    │ │
│  │ (env)    │  │  system  │  │   etc.   │  │   pip    │  │  gradle  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 协议

### 前后端接口协议 (`protocol/`)

定义前端与后端之间的 RPC 通信契约。前后端通过 `protocol/schema.json` 保持同步，
任何满足该协议的实现（当前为 Python stdio JSON-RPC，未来可以是 Go/Node/远程 HTTP）都可替换，
前端无需改动。

**文件**：
- `protocol/schema.json` — JSON-RPC 2.0 协议事实来源（方法/入参/出参/通知/错误码）
- `protocol/README.md` — 协议说明
- `share/types.ts` — TypeScript 类型定义，与 schema.json 保持同步
- `share/schema.ts` — 加载 schema.json 供前端消费

---

## 三层接口定义

### 第一层：前端 → 后端 (Frontend API)

**传输路径**：
```
Renderer → preload.ts → IPC → main.ts → pythonBridge.ts → stdio → Backend
```

**接口文件**：
- `protocol/schema.json` — JSON-RPC 协议事实来源
- `share/types.ts` — TypeScript 类型定义（RPC 方法、参数、返回值）
- `frontend/src/api/index.ts` — 前端 API 封装（强类型调用函数）
- `frontend/src/api/client.ts` — 传输层适配器

**RPC 方法清单**：

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `ping` | - | `{ pong: bool }` | 心跳检测 |
| `env.list` | - | `{ items: Record<category, EnvItem[]> }` | 获取分类环境变量 |
| `env.set_var` | `{ name, value, source? }` | `{ ok: bool }` | 设置环境变量 |
| `env.delete_var` | `{ name, source? }` | `{ ok: bool }` | 删除环境变量 |
| `env.add_path_entry` | `{ value, source? }` | `{ ok: bool }` | 添加 PATH 条目 |
| `env.delete_path_entry` | `{ value, source? }` | `{ ok: bool }` | 删除 PATH 条目 |
| `env.get_raw_path` | `{ source? }` | `{ value: string }` | 获取原始 PATH 值 |
| `env.python_info` | - | `{ version, pip, platform, executable }` | Python 环境信息 |
| `tools.info` | `{ category: string }` | `ToolInfo` | 工具链信息 |
| `packages.list` | `{ func?, lang?, install? }` | `{ items: PackageItem[] }` | 包列表 |
| `packages.install` | `{ name: string }` | `{ ok: bool, output: string }` | 安装包 |
| `packages.uninstall` | `{ name: string }` | `{ ok: bool, output: string }` | 卸载包 |
| `commands.list` | `{ installed_only? }` | `{ items: CommandItem[] }` | 命令列表 |
| `commands.detail` | `{ name: string }` | `CommandDetail` | 命令详情 |
| `commands.description` | `{ name: string }` | `{ text: string }` | 命令描述 |
| `commands.subcommand_help` | `{ command, subcommand }` | `SubcommandHelp` | 子命令帮助 |
| `executor.execute` | `{ command, cwd?, env? }` | `{ sessionId: string }` | 执行命令 |
| `executor.kill` | `{ sessionId: string }` | `{ ok: bool }` | 终止进程 |
| `history.list` | - | `{ items: HistoryEntry[] }` | 历史记录 |
| `history.add` | `{ command, exitCode? }` | `{ ok: bool }` | 添加历史 |
| `history.clear` | - | `{ ok: bool }` | 清空历史 |
| `history.delete` | `{ id: string }` | `{ ok: bool }` | 删除历史 |
| `favorites.list` | - | `{ items: FavoriteEntry[] }` | 收藏列表 |
| `favorites.add` | `{ command, label? }` | `{ ok: bool }` | 添加收藏 |
| `favorites.remove` | `{ command: string }` | `{ ok: bool }` | 移除收藏 |
| `shutdown` | - | - | 关闭后端 |

**通知 (Backend → Frontend)**：

| 通知 | 参数 | 说明 |
|------|------|------|
| `ready` | - | 后端就绪 |
| `executor.output` | `{ sessionId, stream, line }` | 命令输出流 |
| `executor.done` | `{ sessionId, exitCode }` | 命令完成 |
| `env.changed` | - | 环境变量变更 |

---

### 第二层：后端 RPC → Core (Handler → Business)

**接口文件**：
- `backend/implementations/python/rpc_handlers.py` — HANDLERS 字典，映射方法名到处理函数
- `backend/implementations/python/src/core/*.py` — 业务逻辑模块

**Handler → Core 函数映射**：

| RPC 方法 | Handler | Core 模块 | 函数 |
|----------|---------|-----------|------|
| `env.list` | `handle_env_list` | `env.py` | `get_categorized_env_vars()` |
| `env.set_var` | `handle_env_set_var` | `env.py` | `set_env_var(name, value, source)` |
| `env.delete_var` | `handle_env_delete_var` | `env.py` | `delete_env_var(name, source)` |
| `env.add_path_entry` | `handle_env_add_path` | `env.py` | `set_env_var("PATH", ...)` |
| `env.delete_path_entry` | `handle_env_delete_path` | `env.py` | `set_env_var("PATH", ...)` |
| `env.get_raw_path` | `handle_env_get_path` | `env.py` | `os.environ.get("PATH")` |
| `env.python_info` | `handle_env_python_info` | `env.py` | `get_python_version()`, etc. |
| `tools.info` | `handle_tools_info` | `tools.py` | `get_tool_info(category)` |
| `packages.list` | `handle_packages_list` | `packages.py` | `get_categorized_packages(...)` |
| `packages.install` | `handle_packages_install` | `packages.py` | `install_package(name)` |
| `packages.uninstall` | `handle_packages_uninstall` | `packages.py` | `uninstall_package(name)` |
| `commands.list` | `handle_commands_list` | `commands/definitions.py` | `get_command_names()` |
| `commands.detail` | `handle_commands_detail` | `commands/definitions.py` | `load_command_detail(name)` |
| `commands.description` | `handle_commands_description` | `commands/glossary.py` | `get_description(name)` |
| `commands.subcommand_help` | `handle_subcommand_help` | `commands/definitions.py` | `load_subcommand_help(...)` |
| `executor.execute` | `handle_executor_execute` | `executor.py` | `CommandExecutor.execute(...)` |
| `executor.kill` | `handle_executor_kill` | `executor.py` | `executors[session_id].kill()` |
| `history.*` | `handle_history_*` | `store.py` | `list_history()`, etc. |
| `favorites.*` | `handle_favorites_*` | `store.py` | `list_favorites()`, etc. |

---

### 第三层：Core → Runtime (Business → OS)

**Core 模块与运行时交互**：

| Core 模块 | 运行时交互 | 说明 |
|-----------|------------|------|
| `env.py` | Windows Registry | 读写 `HKLM\...\Environment` 和 `HKCU\Environment` |
| `env.py` | `os.environ` | 读写当前进程环境变量 |
| `env.py` | `WM_SETTINGCHANGE` | 广播环境变量变更通知 |
| `tools.py` | `subprocess` | 执行 `java -version`, `node --version` 等 |
| `tools.py` | `shutil.which()` | 查找可执行文件路径 |
| `packages.py` | `subprocess` | 执行 `pip list`, `pip install`, `pip uninstall` |
| `executor.py` | `subprocess.Popen` | 创建子进程执行用户命令 |
| `executor.py` | `threading` | 异步读取 stdout/stderr |
| `commands/definitions.py` | `subprocess` | 执行 `<cmd> --version`, `<cmd> --help` |
| `commands/probes.py` | `subprocess` | 执行 `git config`, `npm config list` 等 |
| `store.py` | `~/.devtool-manager/` | JSON 文件存储历史/收藏 |

---

## 数据文件

| 文件 | 位置 | 说明 |
|------|------|------|
| `schema.json` | `protocol/` | 前后端接口协议定义（事实来源） |
| `command_defs.json` | `backend/data/` | 命令清单（名称、版本参数、描述） |
| `glossary.json` | `backend/data/` | 配置项术语表 |
| `git_knowledge.json` | `backend/data/` | Git 子命令中文知识库 |
| `adb_params.json` | `backend/data/` | ADB 子命令参数定义 |
| `history.json` | `~/.devtool-manager/` | 命令历史 |
| `favorites.json` | `~/.devtool-manager/` | 命令收藏 |

---

## 类型定义

### 核心类型 (share/types.ts)

```typescript
// 环境变量条目
interface EnvItem {
  name: string
  value: string
  source: 'system' | 'user'
  is_path_entry?: boolean
}

// 工具链信息
interface ToolInfo {
  installed: boolean
  version?: string | null
  home?: string | null
  compiler?: string | null
  sdk?: string | null
  ndk?: string | null
  details: { label: string; value: string }[]
}

// 命令项
interface CommandItem {
  name: string
  installed: boolean
}

// 命令详情
interface CommandDetail {
  name: string
  installed: boolean
  version: string
  path: string
  description: string
  subcommands: CommandSubcommand[]
  env_vars: CommandEnvVar[]
  config_sections: CommandConfigSection[]
}

// 命令子命令
interface CommandSubcommand {
  name: string
  description: string
  category?: string
  has_params?: boolean
}

// 子命令帮助
interface SubcommandHelp {
  command: string
  subcommand: string
  params: SubcommandParam[]
  pathParams: SubcommandParam[]
}

// 历史记录
interface HistoryEntry {
  id: string
  command: string
  timestamp: number
  exitCode: number | null
}

// 收藏记录
interface FavoriteEntry {
  command: string
  label: string
  timestamp: number
}
```

---

## 替换后端实现

任何新后端只需满足以下条件即可替换 Python 实现：

1. **传输协议**：支持 newline-delimited JSON-RPC 2.0 over stdio
2. **方法实现**：实现 `protocol/schema.json` 中声明的所有方法
3. **通知支持**：发送 `ready`, `executor.output`, `executor.done`, `env.changed` 通知

前端无需任何修改，只需配置 `electron/main/pythonBridge.ts` 指向新后端可执行文件。
