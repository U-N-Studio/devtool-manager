# DevTool Manager Electron + React 重写实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 Python + CustomTkinter 的 DevTool Manager 转写为 Electron + React + TypeScript 架构，保留 Python 后端业务逻辑，新增 stdio JSON-RPC 适配层，前端用 shadcn/ui 重写 4 个 Tab。

**Architecture:** Electron 主进程 spawn PyInstaller 打包的 Python backend 作为长期运行的 RPC server，通过 stdio newline-delimited JSON-RPC 双向通信。前端 React + Zustand + shadcn/ui，每个 Tab 一个 store 映射现有 ViewModel。流式输出（executor）用 JSON-RPC notification 推送。

**Tech Stack:** Electron 30+ / Vite 5 / React 18 / TypeScript 5 / Zustand 4 / Tailwind CSS 3 / shadcn/ui / Python 3.9+ / PyInstaller 6 / electron-builder 24

**关联设计文档:** `docs/superpowers/specs/2026-10-20-electron-react-rewrite-design.md`

---

## 文件结构总览

### 新建文件

```
devtool-manager/
├── backend/                           # Python RPC 适配层
│   ├── server.py                      # JSON-RPC 主循环
│   ├── rpc_handlers.py                # 方法分发到 core/
│   └── pyproject.toml
├── electron/
│   ├── package.json
│   ├── electron-builder.yml
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── index.html
│   ├── .gitignore
│   ├── src/                           # Renderer (React)
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── vite-env.d.ts
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui 组件（按需添加）
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
│   │   │   ├── appStore.ts
│   │   │   ├── envStore.ts
│   │   │   ├── packagesStore.ts
│   │   │   ├── commandsStore.ts
│   │   │   └── executorStore.ts
│   │   ├── lib/
│   │   │   ├── ipc.ts
│   │   │   ├── types.ts
│   │   │   └── utils.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── main/                          # Electron Main
│   │   ├── main.ts
│   │   ├── window.ts
│   │   ├── pythonBridge.ts
│   │   └── menu.ts
│   ├── preload/
│   │   └── preload.ts
│   └── resources/
│       └── backend/                  # PyInstaller 产物（构建时拷入）
└── scripts/
    └── build-backend.ps1             # PyInstaller 打包脚本
```

### 保留不动

- `main/` 整个目录（旧 Python+CustomTkinter 实现，迁移完成后归档）

### 复用（通过 sys.path 注入）

- `main/src/core/env.py` — 环境变量管理
- `main/src/core/tools.py` — 工具链信息采集
- `main/src/core/packages.py` — Python 包管理
- `main/src/core/commands/` — 命令定义、探测、术语表
- `main/src/core/executor.py` — 子进程执行器
- `main/src/utils/python_finder.py` — Python 解释器定位

---

## Task 1: 项目脚手架初始化

**Files:**
- Create: `electron/package.json`
- Create: `electron/.gitignore`
- Create: `electron/index.html`
- Create: `electron/vite.config.ts`
- Create: `electron/tsconfig.json`
- Create: `electron/tsconfig.node.json`
- Create: `electron/tailwind.config.ts`
- Create: `electron/postcss.config.js`
- Create: `electron/src/main.tsx`
- Create: `electron/src/vite-env.d.ts`
- Create: `electron/src/styles/globals.css`
- Create: `electron/src/App.tsx`
- Create: `backend/pyproject.toml`
- Create: `backend/server.py` (空壳)

- [ ] **Step 1: 创建 `electron/package.json`**

```json
{
  "name": "devtool-manager-electron",
  "version": "0.1.0",
  "description": "DevTool Manager - Electron + React 重写版",
  "private": true,
  "main": "dist-electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "dev:electron": "concurrently \"vite\" \"wait-on http://localhost:5173 && cross-env NODE_ENV=development electron .\"",
    "build:electron": "tsc -p tsconfig.node.json && vite build",
    "build:backend": "powershell -ExecutionPolicy Bypass -File ../scripts/build-backend.ps1",
    "build:all": "pnpm build:backend && pnpm build:electron",
    "package": "electron-builder",
    "lint": "eslint src --ext .ts,.tsx",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "zustand": "^4.5.5",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4",
    "class-variance-authority": "^0.7.0",
    "lucide-react": "^0.454.0",
    "@radix-ui/react-dialog": "^1.1.2",
    "@radix-ui/react-select": "^2.1.2",
    "@radix-ui/react-checkbox": "^1.1.2",
    "@radix-ui/react-tooltip": "^1.1.3",
    "@radix-ui/react-scroll-area": "^1.2.0",
    "@radix-ui/react-collapsible": "^1.1.1",
    "@radix-ui/react-slot": "^1.1.0"
  },
  "devDependencies": {
    "@types/node": "^22.7.5",
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.2",
    "autoprefixer": "^10.4.20",
    "concurrently": "^9.0.1",
    "cross-env": "^7.0.3",
    "electron": "^30.5.1",
    "electron-builder": "^25.0.5",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.13",
    "typescript": "^5.6.2",
    "vite": "^5.4.8",
    "vite-plugin-electron": "^0.28.0",
    "vite-plugin-electron-renderer": "^0.14.0",
    "wait-on": "^8.0.1"
  },
  "build": {
    "appId": "com.vivo.devtoolmanager",
    "productName": "DevTool Manager",
    "directories": { "output": "release" },
    "files": ["dist/**/*", "dist-electron/**/*", "resources/**/*"],
    "extraResources": [{ "from": "resources/backend", "to": "backend" }],
    "win": { "target": "nsis", "icon": "resources/icon.ico" }
  }
}
```

- [ ] **Step 2: 创建 `electron/.gitignore`**

```gitignore
node_modules/
dist/
dist-electron/
release/
resources/backend/
*.log
.DS_Store
```

- [ ] **Step 3: 创建 `electron/index.html`**

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DevTool Manager</title>
  </head>
  <body class="bg-background text-foreground">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 4: 创建 `electron/vite.config.ts`**

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    electron([
      { entry: 'main/main.ts', vite: { build: { outDir: 'dist-electron', rollupOptions: { external: ['electron'] } } } },
      { entry: 'preload/preload.ts', vite: { build: { outDir: 'dist-electron', rollupOptions: { external: ['electron'] } } } },
    ]),
    renderer(),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: { port: 5173 },
})
```

- [ ] **Step 5: 创建 `electron/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src", "preload"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 6: 创建 `electron/tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noEmit": false,
    "outDir": "dist-electron"
  },
  "include": ["main/**/*", "vite.config.ts"]
}
```

- [ ] **Step 7: 创建 `electron/tailwind.config.ts`**

```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: { DEFAULT: 'hsl(var(--primary))', foreground: 'hsl(var(--primary-foreground))' },
        secondary: { DEFAULT: 'hsl(var(--secondary))', foreground: 'hsl(var(--secondary-foreground))' },
        destructive: { DEFAULT: 'hsl(var(--destructive))', foreground: 'hsl(var(--destructive-foreground))' },
        muted: { DEFAULT: 'hsl(var(--muted))', foreground: 'hsl(var(--muted-foreground))' },
        accent: { DEFAULT: 'hsl(var(--accent))', foreground: 'hsl(var(--accent-foreground))' },
        card: { DEFAULT: 'hsl(var(--card))', foreground: 'hsl(var(--card-foreground))' },
      },
      borderRadius: { lg: 'var(--radius)', md: 'calc(var(--radius) - 2px)', sm: 'calc(var(--radius) - 4px)' },
    },
  },
  plugins: [],
}
export default config
```

- [ ] **Step 8: 创建 `electron/postcss.config.js`**

```js
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }
```

- [ ] **Step 9: 创建 `electron/src/styles/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 240 10% 3.9%;
    --radius: 0.5rem;
  }
  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }
}

@layer base {
  * { @apply border-border; }
  body {
    @apply bg-background text-foreground;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    margin: 0;
    overflow: hidden;
  }
}

.titlebar-drag { -webkit-app-region: drag; }
.titlebar-no-drag { -webkit-app-region: no-drag; }
```

- [ ] **Step 10: 创建 `electron/src/vite-env.d.ts`**

```ts
/// <reference types="vite/client" />

interface Window {
  api: {
    rpc: (method: string, params?: object) => Promise<any>
    onNotification: (method: string, handler: (params: any) => void) => () => void
    onWindowState: (handler: (state: 'maximized' | 'normal') => void) => () => void
    windowMinimize: () => void
    windowMaximizeToggle: () => void
    windowClose: () => void
  }
}
```

- [ ] **Step 11: 创建 `electron/src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 12: 创建 `electron/src/App.tsx`（空壳）**

```tsx
export default function App() {
  return (
    <div className="flex h-screen w-screen flex-col">
      <div className="flex flex-1 items-center justify-center">
        <h1 className="text-2xl font-bold">DevTool Manager</h1>
      </div>
    </div>
  )
}
```

- [ ] **Step 13: 创建 `backend/pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "devtool-backend"
version = "0.1.0"
description = "DevTool Manager Python RPC backend"
requires-python = ">=3.9"
dependencies = ["pyinstaller>=6.0"]

[tool.setuptools]
py-modules = ["server", "rpc_handlers"]
```

- [ ] **Step 14: 创建 `backend/server.py`（空壳）**

```python
"""DevTool Manager Python RPC backend.

通过 stdio 与 Electron 主进程通信,使用 newline-delimited JSON-RPC 2.0 协议。
复用 main/src/core/ 的业务逻辑,仅在此层做 RPC 适配。
"""

import sys
import os

_MAIN_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main", "src"))
if _MAIN_SRC not in sys.path:
    sys.path.insert(0, _MAIN_SRC)


def main():
    """RPC 主循环,Task 2 实现。"""
    for line in sys.stdin:
        sys.stdout.write('{"jsonrpc":"2.0","method":"ready","params":{}}\n')
        sys.stdout.flush()
        break


if __name__ == "__main__":
    main()
```

- [ ] **Step 15: 安装依赖并验证脚手架**

Run:
```bash
cd D:\Project\devtool-manager\electron
pnpm install
```

Expected: 依赖安装成功，无报错。

- [ ] **Step 16: 验证 Python backend 空壳可运行**

Run:
```bash
cd D:\Project\devtool-manager\backend
python -c "import server; server.main()" < /dev/null
```

Expected: 输出一行 `{"jsonrpc":"2.0","method":"ready","params":{}}` 后退出。

- [ ] **Step 17: Commit**

```bash
cd D:\Project\devtool-manager
git add -A
git commit -m "feat(electron): scaffold Electron + React + Python backend structure"
```

---

## Task 2: PythonBridge + IPC 基础

**Files:**
- Create: `electron/main/main.ts`
- Create: `electron/main/window.ts`
- Create: `electron/main/pythonBridge.ts`
- Create: `electron/main/menu.ts`
- Create: `electron/preload/preload.ts`
- Create: `electron/src/lib/ipc.ts`
- Create: `electron/src/lib/types.ts`
- Create: `electron/src/lib/utils.ts`
- Modify: `backend/server.py`
- Create: `backend/rpc_handlers.py`

- [ ] **Step 1: 创建 `electron/src/lib/utils.ts`**

```ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

- [ ] **Step 2: 创建 `electron/src/lib/types.ts`**

定义 JSON-RPC 2.0 消息类型、业务类型（EnvItem/PythonInfo/ToolInfo/PackageItem/CommandDetail 等）、RpcMethod 联合类型、RpcParamsMap/RpcResultMap/NotificationParamsMap 类型映射。

完整内容见设计文档 §5.3-5.6 的方法清单，每个方法对应 params 与 result 类型。关键类型：

```ts
export interface EnvItem { name: string; value: string; source: 'system' | 'user'; is_path_entry: boolean }
export interface PythonInfo { version: string; pip: string; platform: string; executable: string }
export interface ToolInfo { installed: boolean; details: { label: string; value: string }[] }
export interface PackageItem { name: string; version: string; installed: boolean; func_tag: string; lang_tag: string }
export interface CommandDetail {
  name: string; installed: boolean; version: string; path: string; description: string;
  params: { name: string; description: string }[];
  subcommands: { name: string; description: string }[];
  env_vars: string[];
  config_sections: { level: string; items: { key: string; value: string }[] }[];
}

export type RpcMethod = 'ping' | 'env.list' | 'env.python_info' | 'env.set_var' | 'env.delete_var'
  | 'env.add_path_entry' | 'env.delete_path_entry' | 'env.get_raw_path' | 'tools.info'
  | 'packages.list' | 'packages.install' | 'packages.uninstall' | 'commands.list'
  | 'commands.detail' | 'commands.description' | 'executor.execute' | 'executor.kill' | 'shutdown'

export type NotificationMethod = 'ready' | 'executor.output' | 'executor.done' | 'env.changed'

// RpcParamsMap / RpcResultMap / NotificationParamsMap 按设计文档 §5.3-5.4 完整定义
// 每个 method 的 params 和 result 类型一一对应
```

- [ ] **Step 3: 创建 `electron/src/lib/ipc.ts`**

```ts
import type { RpcMethod, NotificationMethod, RpcParamsMap, RpcResultMap, NotificationParamsMap } from './types'

export async function rpc<M extends RpcMethod>(
  method: M,
  params?: RpcParamsMap[M],
): Promise<RpcResultMap[M]> {
  return window.api.rpc(method, params) as Promise<RpcResultMap[M]>
}

export function onNotification<M extends NotificationMethod>(
  method: M,
  handler: (params: NotificationParamsMap[M]) => void,
): () => void {
  return window.api.onNotification(method, handler as (params: unknown) => void)
}
```

- [ ] **Step 4: 创建 `electron/preload/preload.ts`**

```ts
import { contextBridge, ipcRenderer } from 'electron'

const pendingRpc = new Map<string, { resolve: (v: unknown) => void; reject: (e: Error) => void }>()

ipcRenderer.on('rpc:response', (_event, response) => {
  const pending = pendingRpc.get(response.id)
  if (!pending) return
  pendingRpc.delete(response.id)
  if (response.error) pending.reject(new Error(response.error.message))
  else pending.resolve(response.result)
})

const notificationHandlerMap = new Map<string, Set<(params: unknown) => void>>()

ipcRenderer.on('rpc:notification', (_event, notification) => {
  const handlers = notificationHandlerMap.get(notification.method)
  handlers?.forEach((h) => h(notification.params))
})

contextBridge.exposeInMainWorld('api', {
  rpc: (method: string, params?: object): Promise<unknown> => {
    const id = crypto.randomUUID()
    return new Promise((resolve, reject) => {
      pendingRpc.set(id, { resolve, reject })
      ipcRenderer.send('rpc:request', { id, method, params })
    })
  },
  onNotification: (method: string, handler: (params: unknown) => void): (() => void) => {
    if (!notificationHandlerMap.has(method)) notificationHandlerMap.set(method, new Set())
    notificationHandlerMap.get(method)!.add(handler)
    return () => { notificationHandlerMap.get(method)?.delete(handler) }
  },
  onWindowState: (handler: (state: 'maximized' | 'normal') => void): (() => void) => {
    const listener = (_e: unknown, state: 'maximized' | 'normal') => handler(state)
    ipcRenderer.on('window:state', listener)
    return () => ipcRenderer.removeListener('window:state', listener)
  },
  windowMinimize: () => ipcRenderer.send('window:minimize'),
  windowMaximizeToggle: () => ipcRenderer.send('window:maximizeToggle'),
  windowClose: () => ipcRenderer.send('window:close'),
})
```

- [ ] **Step 5: 创建 `electron/main/pythonBridge.ts`**

```ts
import { spawn, ChildProcess } from 'child_process'
import { app } from 'electron'
import path from 'path'
import { randomUUID } from 'crypto'
import { EventEmitter } from 'events'

interface PendingRequest {
  resolve: (v: unknown) => void
  reject: (e: Error) => void
  timer: NodeJS.Timeout
}

export class PythonBridge extends EventEmitter {
  private proc: ChildProcess | null = null
  private pending = new Map<string, PendingRequest>()
  private notificationHandlers = new Map<string, Set<(params: any) => void>>()
  private buffer = ''

  async start(): Promise<void> {
    const args = app.isPackaged ? [] : [path.resolve(__dirname, '../../backend/server.py')]
    const command = app.isPackaged
      ? path.join(process.resourcesPath, 'backend', 'devtool-backend.exe')
      : 'python'

    this.proc = spawn(command, args, { stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true })
    this.proc.stdout?.setEncoding('utf8')
    this.proc.stdout?.on('data', (data: string) => this.onStdout(data))
    this.proc.stderr?.on('data', (data: Buffer) => console.error('[backend stderr]', data.toString()))
    this.proc.on('exit', (code) => { console.log(`[backend] exited with code ${code}`); this.proc = null })

    await this.waitForReady()
  }

  private waitForReady(): Promise<void> {
    return new Promise((resolve) => {
      const handler = () => { this.off('ready', handler); resolve() }
      this.once('ready', handler)
      setTimeout(() => { this.off('ready', handler); resolve() }, 5000)
    })
  }

  private onStdout(data: string): void {
    this.buffer += data
    const lines = this.buffer.split('\n')
    this.buffer = lines.pop() || ''
    for (const line of lines) {
      if (!line.trim()) continue
      try { this.handleMessage(JSON.parse(line)) }
      catch (e) { console.error('[pythonBridge] failed to parse line:', line, e) }
    }
  }

  private handleMessage(msg: any): void {
    if (msg.method && !msg.id) {
      if (msg.method === 'ready') this.emit('ready')
      this.notificationHandlers.get(msg.method)?.forEach((h) => h(msg.params || {}))
    } else if (msg.id) {
      const pending = this.pending.get(msg.id)
      if (!pending) return
      this.pending.delete(msg.id)
      clearTimeout(pending.timer)
      if (msg.error) pending.reject(new Error(msg.error.message))
      else pending.resolve(msg.result)
    }
  }

  rpc(method: string, params?: object): Promise<unknown> {
    return new Promise((resolve, reject) => {
      if (!this.proc || !this.proc.stdin) { reject(new Error('Python backend not started')); return }
      const id = randomUUID()
      const timer = setTimeout(() => { this.pending.delete(id); reject(new Error(`RPC timeout: ${method}`)) }, 60000)
      this.pending.set(id, { resolve, reject, timer })
      this.proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params: params || {} }) + '\n')
    })
  }

  onNotification(method: string, handler: (params: any) => void): () => void {
    if (!this.notificationHandlers.has(method)) this.notificationHandlers.set(method, new Set())
    this.notificationHandlers.get(method)!.add(handler)
    return () => { this.notificationHandlers.get(method)?.delete(handler) }
  }

  async shutdown(): Promise<void> {
    if (!this.proc) return
    try {
      await Promise.race([
        this.rpc('shutdown'),
        new Promise((_, reject) => setTimeout(() => reject(new Error('shutdown timeout')), 2000)),
      ])
    } catch { /* 超时则强制 kill */ }
    if (this.proc) { this.proc.kill(); this.proc = null }
  }
}
```

- [ ] **Step 6: 创建 `electron/main/window.ts`**

```ts
import { BrowserWindow } from 'electron'
import path from 'path'

export function createMainWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1280, height: 820, minWidth: 960, minHeight: 640,
    frame: false, titleBarStyle: 'hidden',
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      contextIsolation: true, nodeIntegration: false,
    },
  })
  win.on('maximize', () => win.webContents.send('window:state', 'maximized'))
  win.on('unmaximize', () => win.webContents.send('window:state', 'normal'))
  if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV_SERVER_URL) {
    win.loadURL('http://localhost:5173')
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
  return win
}
```

- [ ] **Step 7: 创建 `electron/main/menu.ts`**

标准 Electron 菜单模板（文件/编辑/视图），含重新加载、开发者工具、退出等。完整代码见设计文档。

- [ ] **Step 8: 创建 `electron/main/main.ts`**

```ts
import { app, BrowserWindow, ipcMain, Menu } from 'electron'
import { createMainWindow } from './window'
import { buildAppMenu } from './menu'
import { PythonBridge } from './pythonBridge'

let mainWindow: BrowserWindow | null = null
let bridge: PythonBridge | null = null

async function bootstrap() {
  bridge = new PythonBridge()
  await bridge.start()

  ipcMain.handle('rpc:request', async (_event, request) => {
    try {
      const result = await bridge.rpc(request.method, request.params)
      return { id: request.id, result }
    } catch (e: any) {
      return { id: request.id, error: { code: -32603, message: e.message } }
    }
  })

  const notificationMethods = ['ready', 'executor.output', 'executor.done', 'env.changed']
  for (const method of notificationMethods) {
    bridge.onNotification(method, (params) => {
      mainWindow?.webContents.send('rpc:notification', { method, params })
    })
  }

  ipcMain.on('window:minimize', () => mainWindow?.minimize())
  ipcMain.on('window:maximizeToggle', () => {
    if (mainWindow?.isMaximized()) mainWindow.unmaximize()
    else mainWindow?.maximize()
  })
  ipcMain.on('window:close', () => mainWindow?.close())

  Menu.setApplicationMenu(buildAppMenu())
  mainWindow = createMainWindow()
}

app.whenReady().then(bootstrap)
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
app.on('before-quit', async (e) => {
  if (bridge) { e.preventDefault(); await bridge.shutdown(); app.exit(0) }
})
```

- [ ] **Step 9: 实现 `backend/rpc_handlers.py`**

完整 RPC 方法路由表，每个 handler 对应一个 method。关键函数：

```python
import uuid, threading
from src.core.env import (get_python_version, get_pip_version, get_platform, get_executable,
    get_categorized_env_vars, get_system_and_user_env_vars, set_env_var, delete_env_var)
from src.core.tools import get_tool_info
from src.core.packages import get_categorized_packages, install_package, uninstall_package
from src.core.commands import get_command_names, load_command_detail, get_description
from src.core.executor import CommandExecutor

_executors: dict[str, CommandExecutor] = {}
_executors_lock = threading.Lock()

def handle_ping(params): return {"pong": True}
def handle_env_list(params): return {"items": get_categorized_env_vars()}
def handle_env_python_info(params):
    return {"version": get_python_version(), "pip": get_pip_version(),
            "platform": get_platform(), "executable": get_executable()}
def handle_env_set_var(params):
    set_env_var(params["name"], params["value"], params.get("source", "user")); return {"ok": True}
def handle_env_delete_var(params):
    delete_env_var(params["name"], params.get("source", "user")); return {"ok": True}
def handle_env_add_path_entry(params):
    # 读取现有 PATH,追加条目,set_env_var("PATH", new_path, source)
    ...
def handle_env_delete_path_entry(params):
    # 读取现有 PATH,移除条目,set_env_var("PATH", new_path, source)
    ...
def handle_env_get_raw_path(params):
    system_vars, user_vars = get_system_and_user_env_vars()
    source = params.get("source", "user")
    value = system_vars.get("PATH", "") if source == "system" else user_vars.get("PATH", "")
    return {"value": value}
def handle_tools_info(params): return get_tool_info(params["category"])
def handle_packages_list(params):
    return {"items": get_categorized_packages(params.get("func",""), params.get("lang",""), params.get("install",""))}
def handle_packages_install(params):
    ok, output = install_package(params["name"]); return {"ok": ok, "output": output}
def handle_packages_uninstall(params):
    ok, output = uninstall_package(params["name"]); return {"ok": ok, "output": output}
def handle_commands_list(params):
    names = get_command_names()
    if params.get("installed_only"):
        import shutil
        names = [n for n in names if shutil.which(n)]
    return {"names": names}
def handle_commands_detail(params): return load_command_detail(params["name"])
def handle_commands_description(params): return {"text": get_description(params["name"])}

def handle_executor_execute(params, notify):
    session_id = str(uuid.uuid4())
    executor = CommandExecutor()
    with _executors_lock: _executors[session_id] = executor
    def on_output(line): notify("executor.output", {"sessionId": session_id, "stream": "stdout", "line": line})
    def on_error(line): notify("executor.output", {"sessionId": session_id, "stream": "stderr", "line": line})
    def on_done(exit_code):
        notify("executor.done", {"sessionId": session_id, "exitCode": exit_code})
        with _executors_lock: _executors.pop(session_id, None)
    executor.execute(params["command"], cwd=params.get("cwd"), on_output=on_output,
                     on_error=on_error, on_done=on_done, env=params.get("env"))
    return {"sessionId": session_id}

def handle_executor_kill(params):
    with _executors_lock: executor = _executors.get(params["sessionId"])
    if executor: executor.kill(); return {"ok": True}
    return {"ok": False}

def handle_shutdown(params):
    with _executors_lock:
        for executor in _executors.values():
            try: executor.kill()
            except Exception: pass
        _executors.clear()
    return {}

HANDLERS = {
    "ping": handle_ping, "env.list": handle_env_list, "env.python_info": handle_env_python_info,
    "env.set_var": handle_env_set_var, "env.delete_var": handle_env_delete_var,
    "env.add_path_entry": handle_env_add_path_entry, "env.delete_path_entry": handle_env_delete_path_entry,
    "env.get_raw_path": handle_env_get_raw_path, "tools.info": handle_tools_info,
    "packages.list": handle_packages_list, "packages.install": handle_packages_install,
    "packages.uninstall": handle_packages_uninstall, "commands.list": handle_commands_list,
    "commands.detail": handle_commands_detail, "commands.description": handle_commands_description,
    "executor.kill": handle_executor_kill, "shutdown": handle_shutdown,
}
```

- [ ] **Step 10: 实现 `backend/server.py`**

```python
import sys, os, json
from concurrent.futures import ThreadPoolExecutor

_MAIN_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main", "src"))
if _MAIN_SRC not in sys.path: sys.path.insert(0, _MAIN_SRC)

from rpc_handlers import HANDLERS, handle_executor_execute

def send_message(msg: dict):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def send_notification(method, params): send_message({"jsonrpc": "2.0", "method": method, "params": params})
def send_response(req_id, result): send_message({"jsonrpc": "2.0", "id": req_id, "result": result})
def send_error(req_id, code, message): send_message({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

def handle_request(req, executor_pool):
    req_id = req.get("id"); method = req.get("method"); params = req.get("params", {}) or {}
    if method == "executor.execute":
        try: send_response(req_id, handle_executor_execute(params, send_notification))
        except Exception as e: send_error(req_id, -32603, str(e))
        return
    handler = HANDLERS.get(method)
    if not handler: send_error(req_id, -32601, f"Method not found: {method}"); return
    def _run():
        try: send_response(req_id, handler(params))
        except Exception as e: send_error(req_id, -32603, str(e))
    if method in ("ping", "shutdown"): _run()
    else: executor_pool.submit(_run)

def main():
    send_notification("ready", {})
    pool = ThreadPoolExecutor(max_workers=4)
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: req = json.loads(line)
        except json.JSONDecodeError as e: send_error("unknown", -32700, f"Parse error: {e}"); continue
        if "method" in req and "id" in req: handle_request(req, pool)
    pool.shutdown(wait=False)

if __name__ == "__main__": main()
```

- [ ] **Step 11: 验证 Python backend 可独立运行**

Run:
```bash
cd D:\Project\devtool-manager\backend
echo '{"jsonrpc":"2.0","id":"1","method":"ping","params":{}}' | python server.py
```

Expected: 输出两行
```
{"jsonrpc":"2.0","method":"ready","params":{}}
{"jsonrpc":"2.0","id":"1","result":{"pong":true}}
```

- [ ] **Step 12: 验证 Electron + Python 端到端 IPC**

修改 `electron/src/App.tsx` 临时测试 ping:
```tsx
import { useEffect, useState } from 'react'
export default function App() {
  const [status, setStatus] = useState('connecting...')
  useEffect(() => {
    window.api.rpc('ping').then((r: any) => setStatus(JSON.stringify(r))).catch((e: Error) => setStatus(`error: ${e.message}`))
  }, [])
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center">
      <h1 className="text-2xl font-bold">DevTool Manager</h1>
      <p className="mt-4 text-muted-foreground">{status}</p>
    </div>
  )
}
```

Run:
```bash
cd D:\Project\devtool-manager\electron
pnpm dev:electron
```

Expected: Electron 窗口启动,显示 `{"pong":true}`。

- [ ] **Step 13: Commit**

```bash
cd D:\Project\devtool-manager
git add -A
git commit -m "feat(ipc): implement stdio JSON-RPC bridge between Electron and Python backend"
```

---

## Task 3: shadcn/ui 基础组件 + 全局布局 + EnvTab 迁移

**Files:**
- Create: `electron/src/components/ui/button.tsx`
- Create: `electron/src/components/ui/card.tsx`
- Create: `electron/src/components/ui/badge.tsx`
- Create: `electron/src/components/ui/dialog.tsx`
- Create: `electron/src/components/ui/alert-dialog.tsx`
- Create: `electron/src/components/ui/input.tsx`
- Create: `electron/src/components/ui/select.tsx`
- Create: `electron/src/components/ui/scroll-area.tsx`
- Create: `electron/src/components/ui/progress.tsx`
- Create: `electron/src/components/layout/TitleBar.tsx`
- Create: `electron/src/components/layout/Sidebar.tsx`
- Create: `electron/src/components/layout/LoadingOverlay.tsx`
- Create: `electron/src/stores/appStore.ts`
- Create: `electron/src/stores/envStore.ts`
- Create: `electron/src/components/env/EnvTab.tsx`
- Create: `electron/src/components/env/EnvVarRow.tsx`
- Create: `electron/src/components/env/EnvVarDialog.tsx`
- Create: `electron/src/components/env/ToolInfoCard.tsx`
- Modify: `electron/src/App.tsx`

- [ ] **Step 1-9: 创建 shadcn/ui 基础组件**

按 shadcn/ui 标准实现以下组件（每个一个文件，使用 Radix UI 原语 + cva 变体 + cn 工具函数）：
- `button.tsx`：default/destructive/outline/secondary/ghost/link 变体 × default/sm/lg/icon 尺寸
- `card.tsx`：Card/CardHeader/CardTitle/CardDescription/CardContent/CardFooter
- `badge.tsx`：default/secondary/destructive/outline 变体
- `input.tsx`：标准输入框
- `dialog.tsx`：基于 @radix-ui/react-dialog，含 Overlay/Content/Header/Footer/Title/Description
- `alert-dialog.tsx`：基于 @radix-ui/react-dialog，含 Action/Cancel
- `select.tsx`：基于 @radix-ui/react-select，含 Trigger/Content/Item
- `scroll-area.tsx`：基于 @radix-ui/react-scroll-area
- `progress.tsx`：简单进度条

每个组件使用 `React.forwardRef` + `cn()` 类名合并，遵循 shadcn/ui 官方模板。

- [ ] **Step 10: 创建 `electron/src/stores/appStore.ts`**

```ts
import { create } from 'zustand'

export type TabId = 'env' | 'packages' | 'commands' | 'executor'

interface AppState {
  activeTab: TabId
  setActiveTab: (tab: TabId) => void
  globalLoading: boolean
  setGlobalLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'env',
  setActiveTab: (tab) => set({ activeTab: tab }),
  globalLoading: false,
  setGlobalLoading: (loading) => set({ globalLoading: loading }),
}))
```

- [ ] **Step 11: 创建 `electron/src/stores/envStore.ts`**

```ts
import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { EnvItem, PythonInfo, ToolInfo } from '@/lib/types'

interface EnvState {
  pythonInfo: PythonInfo | null
  envItems: EnvItem[]
  toolInfo: ToolInfo | null
  selectedCategory: string
  isLoading: boolean
  message: string
  refresh: () => Promise<void>
  refreshPythonInfo: () => Promise<void>
  refreshToolInfo: (category: string) => Promise<void>
  setCategory: (category: string) => void
  setVar: (name: string, value: string, source: 'system' | 'user') => Promise<boolean>
  deleteVar: (name: string, source: 'system' | 'user') => Promise<boolean>
  addPathEntry: (value: string, source: 'system' | 'user') => Promise<boolean>
  deletePathEntry: (value: string, source: 'system' | 'user') => Promise<boolean>
}

export const useEnvStore = create<EnvState>((set, get) => ({
  pythonInfo: null, envItems: [], toolInfo: null, selectedCategory: 'All', isLoading: false, message: '',
  refresh: async () => {
    set({ isLoading: true, message: '' })
    try { const r = await rpc('env.list', {}); set({ envItems: r.items }) }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  refreshPythonInfo: async () => {
    try { set({ pythonInfo: await rpc('env.python_info', {}) }) }
    catch (e: any) { set({ message: e.message }) }
  },
  refreshToolInfo: async (category) => {
    set({ isLoading: true })
    try { set({ toolInfo: await rpc('tools.info', { category }) }) }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  setCategory: (category) => set({ selectedCategory: category }),
  setVar: async (name, value, source) => {
    set({ isLoading: true, message: `Setting ${name}...` })
    try {
      const r = await rpc('env.set_var', { name, value, source })
      await get().refresh()
      set({ message: r.ok ? `OK: ${name} set` : `Failed: ${name}` })
      return r.ok
    } catch (e: any) { set({ message: e.message }); return false }
    finally { set({ isLoading: false }) }
  },
  deleteVar: async (name, source) => {
    set({ isLoading: true, message: `Deleting ${name}...` })
    try {
      const r = await rpc('env.delete_var', { name, source })
      await get().refresh()
      set({ message: r.ok ? `OK: ${name} deleted` : `Failed: ${name}` })
      return r.ok
    } catch (e: any) { set({ message: e.message }); return false }
    finally { set({ isLoading: false }) }
  },
  addPathEntry: async (value, source) => {
    set({ isLoading: true, message: `Adding to PATH: ${value}...` })
    try {
      const r = await rpc('env.add_path_entry', { value, source })
      await get().refresh()
      set({ message: r.ok ? 'OK: added to PATH' : 'Failed' })
      return r.ok
    } catch (e: any) { set({ message: e.message }); return false }
    finally { set({ isLoading: false }) }
  },
  deletePathEntry: async (value, source) => {
    set({ isLoading: true, message: `Removing from PATH: ${value}...` })
    try {
      const r = await rpc('env.delete_path_entry', { value, source })
      await get().refresh()
      set({ message: r.ok ? 'OK: removed from PATH' : 'Failed' })
      return r.ok
    } catch (e: any) { set({ message: e.message }); return false }
    finally { set({ isLoading: false }) }
  },
}))
```

- [ ] **Step 12-14: 创建布局组件**

`TitleBar.tsx`：自定义标题栏，`titlebar-drag` 拖拽区 + 最小化/最大化/关闭按钮（使用 lucide-react 图标 Minus/Square/X/Copy），通过 `window.api.onWindowState` 监听最大化状态。

`Sidebar.tsx`：左侧 152px 导航栏，4 个 NavItem（Settings2/Package/Cpu/Terminal 图标 + 文字），active 态 `bg-accent text-accent-foreground`。

`LoadingOverlay.tsx`：基于 `globalLoading` 的遮罩，Progress + "加载中..." 文案。

- [ ] **Step 15-17: 创建 EnvTab 子组件**

`EnvVarRow.tsx`：展示 name/value/source 徽章/PATH 徽章 + 编辑/删除按钮。

`EnvVarDialog.tsx`：新增/编辑变量对话框，含 name/value/source 字段，保存调用 `onSubmit`。

`ToolInfoCard.tsx`：工具信息卡，展示 category + installed 徽章 + details 列表。

- [ ] **Step 18: 创建 `electron/src/components/env/EnvTab.tsx`**

组合以上组件：Python 信息卡 + 分类下拉 + 变量列表（ScrollArea） + 工具信息卡 + 新增/编辑对话框 + 删除确认 AlertDialog。`useEffect` 初始化加载 pythonInfo 与 envItems，分类切换时按需加载 toolInfo。

- [ ] **Step 19: 更新 `electron/src/App.tsx` 集成布局**

```tsx
import { TitleBar } from '@/components/layout/TitleBar'
import { Sidebar } from '@/components/layout/Sidebar'
import { LoadingOverlay } from '@/components/layout/LoadingOverlay'
import { EnvTab } from '@/components/env/EnvTab'
import { useAppStore } from '@/stores/appStore'
import { useEnvStore } from '@/stores/envStore'

export default function App() {
  const { activeTab } = useAppStore()
  const envLoading = useEnvStore((s) => s.isLoading)
  const globalLoading = envLoading

  return (
    <div className="relative flex h-screen w-screen flex-col">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          {activeTab === 'env' && <EnvTab />}
          {activeTab === 'packages' && <div className="p-4 text-muted-foreground">Packages Tab (Task 4)</div>}
          {activeTab === 'commands' && <div className="p-4 text-muted-foreground">Commands Tab (Task 5)</div>}
          {activeTab === 'executor' && <div className="p-4 text-muted-foreground">Execute Tab (Task 6)</div>}
        </main>
      </div>
      <LoadingOverlay visible={globalLoading} />
    </div>
  )
}
```

- [ ] **Step 20: 验证 EnvTab 运行**

Run: `pnpm dev:electron`

Expected:
- 窗口启动,显示自定义标题栏 + 左侧导航 + 右侧 EnvTab。
- Python 信息卡显示版本/pip/平台/解释器。
- 分类下拉切换后,变量列表更新,选中非 All/PATH 分类时右侧显示工具信息卡。
- 点"新增"弹出对话框,填写后保存,列表刷新。
- 点某行编辑/删除按钮,操作后列表刷新。

- [ ] **Step 21: Commit**

```bash
git add -A
git commit -m "feat(env): migrate EnvTab to React with shadcn/ui, add TitleBar/Sidebar/LoadingOverlay"
```

---

## Task 4: PackagesTab 迁移

**Files:**
- Create: `electron/src/stores/packagesStore.ts`
- Create: `electron/src/components/packages/PackagesTab.tsx`
- Create: `electron/src/components/packages/PackageRow.tsx`
- Create: `electron/src/components/ui/checkbox.tsx`
- Modify: `electron/src/App.tsx`

- [ ] **Step 1: 创建 `electron/src/components/ui/checkbox.tsx`**

基于 @radix-ui/react-checkbox，peer h-4 w-4 rounded-sm border，checked 态 bg-primary。

- [ ] **Step 2: 创建 `electron/src/stores/packagesStore.ts`**

```ts
import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { PackageItem } from '@/lib/types'

interface PackagesState {
  filteredPackages: PackageItem[]
  isLoading: boolean
  message: string
  filters: { func: string; lang: string; install: string }
  page: number
  pageSize: number
  setFilters: (filters: Partial<{ func: string; lang: string; install: string }>) => void
  refresh: () => Promise<void>
  install: (name: string) => Promise<void>
  uninstall: (name: string) => Promise<void>
  setPage: (page: number) => void
}

export const usePackagesStore = create<PackagesState>((set, get) => ({
  filteredPackages: [], isLoading: false, message: '',
  filters: { func: '', lang: '', install: '' }, page: 1, pageSize: 50,
  setFilters: (filters) => {
    set({ filters: { ...get().filters, ...filters }, page: 1 })
    get().refresh()
  },
  refresh: async () => {
    const { filters } = get()
    set({ isLoading: true, message: '' })
    try { const r = await rpc('packages.list', { func: filters.func, lang: filters.lang, install: filters.install }); set({ filteredPackages: r.items }) }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  install: async (name) => {
    set({ isLoading: true, message: `Installing ${name}...` })
    try { const r = await rpc('packages.install', { name }); set({ message: r.ok ? `Install success: ${name}` : `Install failed: ${name}` }); await get().refresh() }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  uninstall: async (name) => {
    set({ isLoading: true, message: `Uninstalling ${name}...` })
    try { const r = await rpc('packages.uninstall', { name }); set({ message: r.ok ? `Uninstall success: ${name}` : `Uninstall failed: ${name}` }); await get().refresh() }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  setPage: (page) => set({ page }),
}))
```

- [ ] **Step 3: 创建 `electron/src/components/packages/PackageRow.tsx`**

展示包名/版本/安装徽章/功能语言徽章 + Install（Download 图标）/Uninstall（Trash2 图标）按钮。

- [ ] **Step 4: 创建 `electron/src/components/packages/PackagesTab.tsx`**

顶部 3 个 Select（func/lang/install 过滤）+ 刷新按钮 + 消息。列表区 ScrollArea 分页（每页 50）渲染 PackageRow。底部翻页按钮 + 计数。卸载确认 AlertDialog。

- [ ] **Step 5: 更新 `electron/src/App.tsx` 集成 PackagesTab**

```tsx
import { PackagesTab } from '@/components/packages/PackagesTab'
import { usePackagesStore } from '@/stores/packagesStore'
// ...
const pkgsLoading = usePackagesStore((s) => s.isLoading)
const globalLoading = envLoading || pkgsLoading
// ...
{activeTab === 'packages' && <PackagesTab />}
```

- [ ] **Step 6: 验证 PackagesTab 运行**

Run: `pnpm dev:electron`

切换到"Python 包"Tab,验证:
- 包列表加载,显示名称/版本/安装徽章/功能标签。
- 三个过滤下拉切换后列表刷新。
- 点击未安装包的下载按钮,触发安装,完成后列表刷新。
- 点击已安装包的卸载按钮,弹出确认对话框,确认后卸载,列表刷新。
- 分页按钮可正常翻页。

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat(packages): migrate PackagesTab with filtering, pagination, install/uninstall"
```

---

## Task 5: CommandsTab 迁移

**Files:**
- Create: `electron/src/stores/commandsStore.ts`
- Create: `electron/src/components/commands/CommandsTab.tsx`
- Create: `electron/src/components/commands/CommandDetailCard.tsx`
- Create: `electron/src/components/ui/tooltip.tsx`
- Create: `electron/src/components/ui/collapsible.tsx`
- Modify: `electron/src/App.tsx`

- [ ] **Step 1: 创建 `electron/src/components/ui/tooltip.tsx`**

基于 @radix-ui/react-tooltip，Provider/Root/Trigger/Content。

- [ ] **Step 2: 创建 `electron/src/components/ui/collapsible.tsx`**

基于 @radix-ui/react-collapsible，Root/Trigger/Content。

- [ ] **Step 3: 创建 `electron/src/stores/commandsStore.ts`**

```ts
import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { CommandDetail } from '@/lib/types'

interface CommandsState {
  commandNames: string[]
  selectedDetail: CommandDetail | null
  descriptions: Record<string, string>
  isLoading: boolean
  message: string
  filterInstalled: boolean
  searchTerm: string
  refresh: () => Promise<void>
  setFilterInstalled: (installed: boolean) => void
  setSearchTerm: (term: string) => void
  selectCommand: (name: string) => Promise<void>
  getDescription: (name: string) => Promise<string>
}

export const useCommandsStore = create<CommandsState>((set, get) => ({
  commandNames: [], selectedDetail: null, descriptions: {}, isLoading: false, message: '',
  filterInstalled: false, searchTerm: '',
  refresh: async () => {
    set({ isLoading: true, message: '' })
    try { const r = await rpc('commands.list', { installed_only: get().filterInstalled }); set({ commandNames: r.names }) }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  setFilterInstalled: (installed) => { set({ filterInstalled: installed }); get().refresh() },
  setSearchTerm: (term) => set({ searchTerm: term }),
  selectCommand: async (name) => {
    set({ isLoading: true, message: `Loading ${name}...` })
    try { set({ selectedDetail: await rpc('commands.detail', { name }), message: '' }) }
    catch (e: any) { set({ message: e.message }) }
    finally { set({ isLoading: false }) }
  },
  getDescription: async (name) => {
    const cached = get().descriptions[name]
    if (cached) return cached
    try {
      const r = await rpc('commands.description', { name })
      set({ descriptions: { ...get().descriptions, [name]: r.text } })
      return r.text
    } catch { return '' }
  },
}))
```

- [ ] **Step 4: 创建 `electron/src/components/commands/CommandDetailCard.tsx`**

展示选中命令详情：基本信息卡（名称/版本/路径/状态/描述）+ 子命令 Collapsible + 参数 Collapsible（每项 Tooltip 显示术语释义）+ 环境变量 Collapsible（Badge + Tooltip）+ 配置段 Collapsible。

- [ ] **Step 5: 创建 `electron/src/components/commands/CommandsTab.tsx`**

左侧：搜索框（Input + Search 图标）+ 刷新按钮 + 仅显示已安装 Checkbox + 命令列表（ScrollArea + Button list，active 态高亮）。右侧：选中命令的 CommandDetailCard 或提示文案。

- [ ] **Step 6: 更新 `electron/src/App.tsx` 集成 CommandsTab**

```tsx
import { CommandsTab } from '@/components/commands/CommandsTab'
import { useCommandsStore } from '@/stores/commandsStore'
// ...
const cmdsLoading = useCommandsStore((s) => s.isLoading)
const globalLoading = envLoading || pkgsLoading || cmdsLoading
// ...
{activeTab === 'commands' && <CommandsTab />}
```

- [ ] **Step 7: 验证 CommandsTab 运行**

Run: `pnpm dev:electron`

切换到"命令详情"Tab,验证:
- 左侧命令列表加载(git/npm/python/java 等)。
- 搜索框过滤命令名。
- "仅显示已安装"勾选后列表过滤（后端 `handle_commands_list` 的 `installed_only` 参数）。
- 点击命令名,右侧详情加载,显示版本/路径/状态/描述。
- 子命令、参数、环境变量、配置段 Collapsible 可展开/收起。
- 环境变量和参数的 Tooltip 显示术语表释义。

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat(commands): migrate CommandsTab with search, detail cards, collapsible sections"
```

---

## Task 6: ExecuteTab 迁移

**Files:**
- Create: `electron/src/stores/executorStore.ts`
- Create: `electron/src/components/executor/ExecuteTab.tsx`
- Create: `electron/src/components/executor/OutputConsole.tsx`
- Modify: `electron/src/App.tsx`

- [ ] **Step 1: 创建 `electron/src/stores/executorStore.ts`**

```ts
import { create } from 'zustand'
import { rpc, onNotification } from '@/lib/ipc'

interface ExecutorState {
  output: string
  isRunning: boolean
  exitCode: number | null
  cwd: string
  sessionId: string | null
  history: string[]
  historyIndex: number
  execute: (command: string) => Promise<void>
  kill: () => Promise<void>
  setCwd: (path: string) => void
  clearOutput: () => void
  navigateHistory: (direction: 'up' | 'down') => string | null
  initSubscriptions: () => () => void
}

const MAX_LINES = 5000

export const useExecutorStore = create<ExecutorState>((set, get) => ({
  output: '', isRunning: false, exitCode: null, cwd: '', sessionId: null, history: [], historyIndex: -1,
  execute: async (command) => {
    if (!command.trim() || get().isRunning) return
    const cwd = get().cwd || undefined
    set((s) => ({ output: s.output + `$ ${command}\n`, isRunning: true, exitCode: null, history: [...s.history, command], historyIndex: -1 }))
    try { const r = await rpc('executor.execute', { command, cwd }); set({ sessionId: r.sessionId }) }
    catch (e: any) { set((s) => ({ output: s.output + `Error: ${e.message}\n`, isRunning: false })) }
  },
  kill: async () => {
    const sid = get().sessionId
    if (!sid) return
    try { await rpc('executor.kill', { sessionId: sid }) } catch { /* 忽略 */ }
  },
  setCwd: (path) => set({ cwd: path }),
  clearOutput: () => set({ output: '', exitCode: null }),
  navigateHistory: (direction) => {
    const { history, historyIndex } = get()
    if (history.length === 0) return null
    let newIdx: number
    if (historyIndex === -1) newIdx = direction === 'up' ? history.length - 1 : -1
    else {
      newIdx = direction === 'up' ? Math.max(0, historyIndex - 1) : historyIndex + 1
      if (newIdx >= history.length) newIdx = -1
    }
    set({ historyIndex: newIdx })
    return newIdx === -1 ? '' : history[newIdx]
  },
  initSubscriptions: () => {
    const unsubOutput = onNotification('executor.output', ({ sessionId, stream, line }) => {
      if (sessionId !== get().sessionId) return
      set((s) => {
        const newOutput = s.output + line
        const lines = newOutput.split('\n')
        if (lines.length > MAX_LINES) return { output: lines.slice(-MAX_LINES).join('\n') }
        return { output: newOutput }
      })
    })
    const unsubDone = onNotification('executor.done', ({ sessionId, exitCode }) => {
      if (sessionId !== get().sessionId) return
      set((s) => ({ isRunning: false, exitCode, output: s.output + `\nProcess exited with code ${exitCode}\n` }))
    })
    return () => { unsubOutput(); unsubDone() }
  },
}))
```

- [ ] **Step 2: 创建 `electron/src/components/executor/OutputConsole.tsx`**

ScrollArea 内 `<pre>` + font-mono text-xs，按行渲染，Error/Traceback 行红色（text-red-400），其他行 zinc-200。背景 bg-zinc-950。useEffect 自动滚动到底部。

- [ ] **Step 3: 创建 `electron/src/components/executor/ExecuteTab.tsx`**

顶部：cwd 输入框 + 浏览按钮（FolderOpen 图标，用 prompt 简化）。命令行：Input + 执行/终止按钮（Play/Square 图标）+ 清除按钮（Trash2 图标）。输出区：OutputConsole。底部：历史提示 + Exit Badge（绿/红）。键盘事件：Enter 执行，ArrowUp/Down 回溯历史。

- [ ] **Step 4: 更新 `electron/src/App.tsx` 集成 ExecuteTab**

```tsx
import { ExecuteTab } from '@/components/executor/ExecuteTab'
// ...
{activeTab === 'executor' && <ExecuteTab />}
```

executor 的 isRunning 不计入 globalLoading（它有自己的运行状态指示）。

- [ ] **Step 5: 验证 ExecuteTab 运行**

Run: `pnpm dev:electron`

切换到"命令执行"Tab,验证:
- 在工作目录输入框输入有效路径,blur 后保存。
- 输入 `echo hello`,按回车,输出区显示 `$ echo hello` 和 `hello`,Exit: 0。
- 输入 `ping -t 127.0.0.1`,点击终止按钮,进程被 kill,Exit 显示非 0。
- 按↑键回溯历史命令。
- 点击清除按钮,输出区清空。
- 输入 `python -c "import sys; sys.stderr.write('err')"` ,stderr 行以红色显示。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(executor): migrate ExecuteTab with streaming output, history, kill support"
```

---

## Task 7: 打包

**Files:**
- Create: `scripts/build-backend.ps1`
- Create: `electron/resources/icon.ico` (占位，可后续替换真实图标)
- Modify: `electron/package.json` (已配置 build 字段)

- [ ] **Step 1: 创建 `scripts/build-backend.ps1`**

```powershell
# PyInstaller 打包 Python backend
$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot/.."
$backendDir = Join-Path $repoRoot "backend"
$electronResources = Join-Path $repoRoot "electron/resources/backend"

Write-Host "Building Python backend with PyInstaller..."
Push-Location $backendDir
try {
    # 安装依赖
    pip install -e .
    pip install pyinstaller

    # 打包
    pyinstaller --onefile --name devtool-backend --console --clean `
        --add-data "$repoRoot/main/src;src" `
        --hidden-import src.core.env --hidden-import src.core.tools `
        --hidden-import src.core.packages --hidden-import src.core.executor `
        --hidden-import src.core.commands `
        server.py

    # 拷贝产物到 electron/resources/backend/
    New-Item -ItemType Directory -Path $electronResources -Force | Out-Null
    Copy-Item "dist/devtool-backend.exe" $electronResources -Force
    Write-Host "Backend built and copied to $electronResources"
} finally {
    Pop-Location
}
```

- [ ] **Step 2: 创建占位图标**

若无真实图标，创建一个简单的 `.ico` 文件或从 lucide-react 导出。electron-builder 在无 icon 时会用默认图标。

- [ ] **Step 3: 执行全量构建**

Run:
```bash
cd D:\Project\devtool-manager\electron
pnpm build:all
```

Expected:
- `scripts/build-backend.ps1` 执行 PyInstaller 打包，产物拷到 `electron/resources/backend/devtool-backend.exe`。
- `tsc -p tsconfig.node.json && vite build` 构建 renderer 与 electron main。
- 无 TypeScript 类型错误，无构建报错。

- [ ] **Step 4: 执行 electron-builder 打包**

Run:
```bash
cd D:\Project\devtool-manager\electron
pnpm package
```

Expected: `electron/release/` 目录生成安装包（NSIS .exe），包含 renderer dist + electron main + Python backend exe。

- [ ] **Step 5: 验证安装包独立运行**

安装 `electron/release/` 下的安装包，启动 DevTool Manager，验证：
- 窗口正常启动，无白屏。
- 4 个 Tab 全部可用（env/packages/commands/executor）。
- Python backend 从 `process.resourcesPath/backend/devtool-backend.exe` 启动。
- 环境变量读取/编辑、pip 安装/卸载、命令详情、命令执行全部正常。
- 关闭窗口时 Python backend 优雅退出。

- [ ] **Step 6: Commit**

```bash
cd D:\Project\devtool-manager
git add -A
git commit -m "build: add PyInstaller + electron-builder packaging pipeline"
```

---

## 完成后的后续工作（不在本计划范围）

- 归档 `main/` 目录（可移到 `legacy/` 或删除，保留 git 历史）。
- 添加端到端测试（Playwright 或 Spectron）。
- 国际化（i18n）。
- 设置页（主题切换、字体大小、启动目录）。
- 自动更新（electron-updater）。
