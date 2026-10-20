# DevTool Manager — Electron + React 重写设计

**日期**：2026-10-20
**状态**：已通过用户评审，待编写实现计划
**关联**：将现有 `main/`（Python + CustomTkinter）转写为 `electron/`（Electron + React + TypeScript）

---

## 1. 背景与目标

### 1.1 现状

`devtool-manager` 是 Windows 平台的本地开发工具管理 GUI，采用 Python + CustomTkinter 实现，MVVM 架构，包含 4 个功能 Tab：

- **环境变量**：按语言/平台分类读取系统与用户环境变量（含注册表源），支持增删改与 PATH 条目管理，修改后广播 `WM_SETTINGCHANGE`。
- **Python 包**：按功能/语言/安装状态过滤包列表，支持 pip 安装/卸载。
- **命令详情**：探测 30+ 开发工具（git/npm/java/...）的版本、参数、子命令、环境变量、配置段，附术语表释义。
- **命令执行**：流式执行 shell 命令，实时回传 stdout/stderr，支持终止、cwd 切换、历史回溯。

后端代码与 Windows 系统深度集成（`winreg`、`WM_SETTINGCHANGE`、`CREATE_NO_WINDOW`），业务逻辑已被现有 `tests/` 覆盖。

### 1.2 目标

将 UI 层转写到 Electron + React + TypeScript 架构，**保留 Python 后端业务逻辑**，仅新增薄 RPC 适配层。转写完成后：

- UI 现代化（shadcn/ui 默认风格）、可维护性提升。
- Python 后端零重写，业务逻辑风险最低。
- 单一安装包分发（electron-builder 打包，内含 PyInstaller 产物）。

### 1.3 非目标

- 不重写 Python 业务逻辑（`core/` 目录原地保留复用）。
- 不新增功能（首版完整迁移现有 4 Tab，新功能留待后续迭代）。
- 不支持 macOS/Linux（现有 Python 后端本就是 Windows 专用）。

---

## 2. 关键决策（已与用户确认）

| 决策项 | 选择 |
|---|---|
| 后端策略 | 保留 Python 后端，Electron 主进程通过 child_process 调用 |
| IPC 协议 | stdio JSON-RPC（newline-delimited JSON） |
| 项目骨架 | 同仓库新建 `electron/` 子目录，与 `main/` 并存 |
| 前端技术栈 | Vite + React + TypeScript + Zustand + Tailwind + shadcn/ui |
| Python 打包 | PyInstaller 单可执行文件，随 Electron 包分发 |
| UI 风格 | shadcn/ui 默认风格（亮色为主，可切换深色） |
| 功能范围 | 首版完整迁移现有 4 Tab |
| 迁移路径 | 路径 A：渐进式迁移，每步独立可验收 |

---

## 3. 系统架构

```
┌──────────────────────────────────────────────────────────┐
│  Electron Main Process (electron/main/main.ts)           │
│  - 创建 BrowserWindow、菜单、托盘                         │
│  - spawn Python backend (PyInstaller exe) as child_proc  │
│  - 实现 stdio JSON-RPC 桥：forward renderer⇄python        │
│  - 流式输出用 IPC 'executor:output' 事件推给 renderer    │
└────────────┬─────────────────────────────┬────────────────┘
             │ stdio (JSON-RPC over        │ contextBridge
             │  newline-delimited JSON)    │  ipcRenderer.invoke
             ▼                             ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Python Backend          │    │  React Renderer          │
│  backend/server.py       │    │  electron/src/           │
│  - jsonrpcserver loop    │    │  - Zustand stores        │
│  - 调用现有 core/ 函数    │    │  - 4 Tab components      │
│  - executor 流式输出     │    │  - shadcn/ui + Tailwind  │
│    通过 stdout 通知行    │    │                          │
└──────────────────────────┘    └──────────────────────────┘
```

### 3.1 进程模型

- Python 后端是**长期运行的 RPC server**，启动时由 Electron 主进程 spawn 一次，整个应用生命周期共用，不是每次调用都 spawn。
- Electron 主进程负责：
  - spawn Python 子进程，pipe 其 stdin/stdout。
  - 从 Python stdout 读取 newline-delimited JSON，解析为 JSON-RPC 消息。
  - 对 response：按 `id` 匹配 pending request 的 Promise resolve/reject。
  - 对 notification（`executor.output`/`executor.done`/`env.changed`）：通过 `webContents.send` 推给 renderer。
  - 从 renderer 收到 `rpc` 调用时，把 request JSON 写入 Python stdin。

### 3.2 并发模型

- Python 端用 `concurrent.futures.ThreadPoolExecutor`（max_workers=4）处理耗时调用（env 读取、pip 安装、命令探测），不阻塞 RPC 消息循环。
- 消息循环单线程读取 stdin，分发到线程池；response 通过队列回主循环写出。
- executor 的子进程流式输出在独立线程读取，通过 notification 推送，不经过线程池。

### 3.3 生命周期

- Electron `app.whenReady()` → spawn Python backend → 等待 `ready` notification → 创建 BrowserWindow。
- `before-quit` → 向 Python 发 `shutdown` request → 等 2s → 超时 kill 子进程。
- Python backend 收到 `shutdown` 后优雅关闭线程池、清理 executor 子进程、退出。

---

## 4. 目录结构与构建

```
devtool-manager/
├── main/                          # 旧 Python+CustomTkinter，保留不动
├── electron/
│   ├── package.json
│   ├── electron-builder.yml
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── index.html
│   ├── src/                       # Renderer (React)
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ui/                # shadcn/ui 组件（手动添加，非全量）
│   │   │   ├── layout/
│   │   │   │   ├── TitleBar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── LoadingOverlay.tsx
│   │   │   ├── env/
│   │   │   │   ├── EnvTab.tsx
│   │   │   │   ├── EnvVarRow.tsx
│   │   │   │   ├── EnvVarDialog.tsx
│   │   │   │   └── ToolInfoCard.tsx
│   │   │   ├── packages/
│   │   │   │   ├── PackagesTab.tsx
│   │   │   │   └── PackageRow.tsx
│   │   │   ├── commands/
│   │   │   │   ├── CommandsTab.tsx
│   │   │   │   └── CommandDetailCard.tsx
│   │   │   └── executor/
│   │   │       ├── ExecuteTab.tsx
│   │   │       └── OutputConsole.tsx
│   │   ├── stores/
│   │   │   ├── envStore.ts
│   │   │   ├── packagesStore.ts
│   │   │   ├── commandsStore.ts
│   │   │   ├── executorStore.ts
│   │   │   └── appStore.ts
│   │   ├── lib/
│   │   │   ├── ipc.ts
│   │   │   └── types.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── main/                      # Electron Main
│   │   ├── main.ts
│   │   ├── window.ts
│   │   ├── pythonBridge.ts
│   │   └── menu.ts
│   ├── preload/
│   │   └── preload.ts
│   └── resources/
│       └── backend/              # PyInstaller 产物（构建时拷入）
│           └── devtool-backend.exe
└── backend/                       # 新增 Python RPC 适配层
    ├── server.py
    ├── rpc_handlers.py
    └── pyproject.toml
```

### 4.1 Python 后端复用方式

`backend/` 通过 `sys.path` 注入 `main/src/`（或 `pip install -e main/`），直接 `from src.core.env import ...` 复用现有业务逻辑，零重写。

### 4.2 构建流程

1. `backend/` PyInstaller 打包 `server.py` → `backend/dist/devtool-backend.exe`（单文件，含 Python 运行时与所有依赖）。
2. 构建脚本把 `devtool-backend.exe` 拷到 `electron/resources/backend/`。
3. `electron-builder` 打包 `electron/`，把 `resources/backend/` 打进最终安装包。
4. 用户安装后，Electron 主进程从 `process.resourcesPath` 找到 `backend/devtool-backend.exe` 并 spawn。

### 4.3 开发模式

- `pnpm dev`：Vite dev server + Electron 主进程 spawn 开发用 Python（`python backend/server.py`），不打包 exe。
- `pnpm build`：Vite 构建 renderer。
- `pnpm build:backend`：PyInstaller 打包。
- `pnpm build:all`：全量打包，产出安装包。

---

## 5. IPC 契约（JSON-RPC 协议）

### 5.1 传输层

newline-delimited JSON over stdio：每条消息一行 `\n` 结尾。Python stdout 只输出 JSON-RPC 消息（业务日志走 stderr，由 Electron 主进程转发到控制台或文件）。

### 5.2 消息格式（JSON-RPC 2.0）

- **Request**：`{"jsonrpc":"2.0","id":"<uuid>","method":"<name>","params":{...}}`
- **Response**：`{"jsonrpc":"2.0","id":"<uuid>","result":{...}}` 或 `{"jsonrpc":"2.0","id":"<uuid>","error":{"code":<int>,"message":"<str>"}}`
- **Notification**（无需回复，用于流式推送）：`{"jsonrpc":"2.0","method":"<name>","params":{...}}`

### 5.3 方法清单

| Method | Params | Result | 对应 Python 函数 |
|---|---|---|---|
| `env.list` | `{category?: str}` | `{items: EnvItem[]}` | `env.get_categorized_env_vars()` |
| `env.python_info` | `{}` | `{version, pip, platform, executable}` | `env.get_python_version()` 等 |
| `env.set_var` | `{name, value, source}` | `{ok: bool}` | `env.set_env_var()` |
| `env.delete_var` | `{name, source}` | `{ok: bool}` | `env.delete_env_var()` |
| `env.add_path_entry` | `{value, source}` | `{ok: bool}` | `env` PATH 新增 |
| `env.delete_path_entry` | `{value, source}` | `{ok: bool}` | `env` PATH 删除 |
| `env.get_raw_path` | `{source}` | `{value: str}` | `env.get_system_and_user_env_vars()` |
| `tools.info` | `{category: str}` | `ToolInfo` | `tools.get_tool_info()` |
| `packages.list` | `{func?, lang?, install?}` | `{items: PkgItem[]}` | `packages.get_categorized_packages()` |
| `packages.install` | `{name}` | `{ok, output}` | `packages.install_package()` |
| `packages.uninstall` | `{name}` | `{ok, output}` | `packages.uninstall_package()` |
| `commands.list` | `{}` | `{names: str[]}` | `commands.get_command_names()` |
| `commands.detail` | `{name}` | `CommandDetail` | `commands.load_command_detail()` |
| `commands.description` | `{name}` | `{text: str}` | `commands.get_description()` |
| `executor.execute` | `{command, cwd?, env?}` | `{sessionId: str}` | 启动子进程 |
| `executor.kill` | `{sessionId}` | `{ok: bool}` | `CommandExecutor.kill()` |
| `shutdown` | `{}` | `{}` | 优雅退出 |

### 5.4 流式通知（Python → Electron → Renderer）

- `executor.output`：`{sessionId, stream: "stdout"|"stderr", line: str}`
- `executor.done`：`{sessionId, exitCode: int}`
- `env.changed`（可选）：环境变量修改后广播，用于多窗口同步。

### 5.5 Renderer 侧封装

`electron/preload/preload.ts` 通过 `contextBridge` 暴露：

```ts
window.api.rpc(method: string, params?: object): Promise<any>
window.api.onNotification(method: string, handler: (params) => void): () => void  // 返回 unsubscribe
```

Zustand store 直接调用 `window.api.rpc(...)`，通知通过 `onNotification` 订阅。

### 5.6 TypeScript 类型契约

`electron/src/lib/types.ts` 定义所有 method 的 params/result 类型，`ipc.ts` 提供类型安全的 `rpc<T>(method, params)` 泛型封装。

---

## 6. 状态管理（Zustand 映射现有 ViewModel）

现有 `viewmodel/observable.py` 的 Observable 模式直接映射为 Zustand store。每个 Tab 一个 store，外加全局 `appStore`。

### 6.1 appStore（对应 `DevToolManagerApp` 全局状态）

- `activeTab: 'env' | 'packages' | 'commands' | 'executor'`
- `globalLoading: boolean`（汇总所有 store 的 isLoading）
- `setActiveTab(tab)`：切换 Tab 时按需刷新（与现有 `_on_tab_change` 一致：首次切到 env 时加载环境数据与工具信息）。
- `refreshAll()`：刷新当前 Tab 数据。

### 6.2 envStore（对应 `EnvViewModel + ToolInfoViewModel`）

- state：`pythonInfo`, `envItems`, `toolInfo`, `isLoading`, `message`
- actions：`refresh()`, `setVar()`, `deleteVar()`, `addPathEntry()`, `deletePathEntry()`, `refreshToolInfo(category)`
- 实现：调用 `window.api.rpc('env.*', ...)`，错误写入 `message`。

### 6.3 packagesStore（对应 `PackagesViewModel`）

- state：`filteredPackages`, `isLoading`, `message`, `filters: {func, lang, install}`
- actions：`setFilters()`, `refresh()`, `install(name)`, `uninstall(name)`

### 6.4 commandsStore（对应 `CommandsViewModel`）

- state：`commandNames`, `selectedDetail`, `isLoading`, `message`, `filterInstalled`
- actions：`refresh()`, `setFilterInstalled()`, `selectCommand(name)`

### 6.5 executorStore（对应 `ExecutorViewModel`，差异最大）

- state：`output: string`, `isRunning`, `exitCode`, `cwd`, `sessionId: string | null`
- actions：`execute(command)`, `kill()`, `setCwd(path)`, `clearOutput()`
- **流式订阅**：store 初始化时通过 `window.api.onNotification('executor.output', ...)` 订阅，按 `sessionId` 过滤后 append 到 `output`；`executor.done` 通知到达时更新 `exitCode` 和 `isRunning`。
- `output` 上限 5000 行（与现有一致），超出后截断尾部。

### 6.6 全局 loading 汇总

`appStore.globalLoading` 通过 `useEnvStore(s => s.isLoading)` 等订阅各 store，任一为 true 即显示遮罩。

---

## 7. UI 组件设计（shadcn/ui 默认风格 + 4 Tab）

### 7.1 全局布局（对应 `app.py` 的自建标题栏 + 左导航 + 右内容区）

- **TitleBar**：Electron `frame: false` + `titleBarStyle: 'hidden'`，自建拖拽区（`-webkit-app-region: drag`）+ 最小化/最大化/关闭按钮（shadcn `Button` variant=ghost size=icon，`-webkit-app-region: no-drag`）。
- **Sidebar**：左侧固定宽度（约 152px）导航，4 个 NavItem（图标 + 文字），active 态用 shadcn 默认 accent 背景。
- **LoadingOverlay**：基于 `appStore.globalLoading`，用 shadcn `Progress` 或简单 spinner 遮罩。
- 主内容区按 `activeTab` 切换渲染对应 Tab。

### 7.2 EnvTab（对应 `env_tab.py`）

- 顶部：Python 信息卡（`Card` + `CardHeader` + `CardContent`，展示 version/pip/platform/executable）。
- 分类选择：`Select`（shadcn）。
- 变量列表：`Table`（shadcn）或 `ScrollArea` + 自定义 Row，每行展示 name/value/source 徽章（`Badge` variant 区分 system/user）。
- 右侧/底部：`ToolInfoCard`（动态显示，分类含工具信息时）。
- 操作：`Dialog`（增/改变量）、`AlertDialog`（删除确认）。

### 7.3 PackagesTab（对应 `packages_tab.py`）

- 顶部：3 个 `Select`（func/lang/install 过滤）。
- 列表：分页（每页 50）+ `Table` 或 `ScrollArea` + Row。
- 每行：包名、版本、安装徽章、`Button`（Install/Uninstall）。
- `AlertDialog` 确认卸载。

### 7.4 CommandsTab（对应 `commands_tab.py`）

- 左：`Command` 输入框 + `Checkbox`（仅显示已安装）+ 命令列表（`ScrollArea` + Button list）。
- 右：选中命令详情，多个 `Card`：版本/路径/状态、子命令、参数、环境变量、配置段（每项附术语表释义用 `Tooltip` 或 `Collapsible`）。

### 7.5 ExecuteTab（对应 `execute_tab.py`）

- 顶部：cwd 输入（`Input` + 浏览按钮 `Button`）。
- 命令行：`Input` + 执行 `Button`，支持上下方向键历史回溯（用 `useRef` 维护 history 数组 + 索引）。
- 输出区：`ScrollArea` 内 `<pre>` + 等宽字体（Tailwind `font-mono`），stdout 黑色、stderr 红色（用 `<span>` 区分）。
- 底部状态栏：退出码 `Badge`（绿/红配色）。

---

## 8. 迁移顺序与验收策略

### 8.1 渐进式迁移步骤

每步独立可运行、可对照旧版：

1. **脚手架**：`electron/` 目录、package.json、Vite+React+TS+Tailwind+shadcn 初始化、Electron main/preload 空壳、Python backend `server.py` 空壳。验收：`pnpm dev` 能启动空白窗口。
2. **PythonBridge + IPC 基础**：实现 stdio JSON-RPC 双向通信、contextBridge 暴露 `rpc`/`onNotification`、shutdown 机制。验收：renderer 调 `ping` 方法能收到 pong。
3. **EnvTab 迁移**（含 ToolInfoCard）：envStore + EnvTab 组件 + 全局 TitleBar/Sidebar/LoadingOverlay。验收：能读取/编辑环境变量、PATH，工具卡片正确显示，与旧版行为一致。
4. **PackagesTab 迁移**：packagesStore + 组件。验收：过滤、分页、安装/卸载行为一致。
5. **CommandsTab 迁移**：commandsStore + 组件。验收：列表、详情、术语释义一致。
6. **ExecuteTab 迁移**：executorStore + 流式通知订阅 + 输出区。验收：流式输出、kill、cwd 切换、历史回溯、退出码显示一致。
7. **打包**：PyInstaller 打包 backend、electron-builder 打包整个应用、验证安装包能独立运行。

### 8.2 验收基准

每个 Tab 与旧版 CustomTkinter 实现的功能逐项对照：
- 读取结果一致（环境变量分类、包列表过滤、命令详情字段）。
- 操作副作用一致（环境变量改完广播 `WM_SETTINGCHANGE`、pip 安装后列表刷新、executor kill 真正终止子进程）。
- 错误处理一致（系统变量权限不足提示、pip 失败输出、命令不存在处理）。

### 8.3 回退机制

- 迁移期间 `main/` 保持可运行。
- 任一 Tab 验收失败不阻塞其他 Tab 开发。
- 全部完成并打包验证通过后再归档 `main/`。

---

## 9. 风险与缓解

| 风险 | 缓解 |
|---|---|
| PyInstaller 产物在 Electron 包内路径定位失败 | 用 `process.resourcesPath` + 相对路径，开发/生产环境统一通过环境变量 `BACKEND_PATH` 注入 |
| stdio RPC 在大输出（如 npm config list）时阻塞 | Python 端 response 分块写出，每行不超过 1MB；超大输出（executor）走 notification 流式 |
| executor 子进程在应用退出时残留 | `before-quit` 发 `shutdown`，Python 端在 `atexit` 清理所有 executor 子进程 |
| shadcn/ui 组件按需添加遗漏 | 脚手架阶段只装基础组件（Button/Card/Dialog/Input/Select/ScrollArea/Badge/Table），后续 Tab 按需补 |
| Windows 注册表操作需管理员权限 | 与现有实现一致：系统变量写入失败时返回 `PermissionError`，UI 提示"需要管理员权限" |

---

## 10. 后续工作（不在本设计范围）

- 国际化（i18n）支持。
- 设置页（主题切换、字体大小、启动目录）。
- 多窗口支持（`env.changed` 通知已预留）。
- 自动更新（electron-updater）。

---

**下一步**：调用 `writing-plans` skill 基于本设计编写详细实现计划。
