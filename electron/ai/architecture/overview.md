# DevTool Manager — 架构总览

> IPC契约: [ipc-contract](ipc-contract.md) | 决策记录: [design-decisions](design-decisions.md)
> 模块: [env](../modules/env/requirements/prd.md) | [packages](../modules/packages/requirements/prd.md) | [tools](../modules/tools/requirements/prd.md) | [ui](../modules/ui/requirements/prd.md)

## 技术栈

| 层 | 技术 |
|----|------|
| 壳 | Electron 33+ |
| 主进程 | Node.js (CommonJS, IPC handlers) |
| 渲染进程 | 原生 HTML/CSS/JS |
| IPC 桥 | contextBridge + ipcMain/ipcRenderer |
| 构建 | electron-builder → NSIS |

## 进程模型

```
┌──────────────────────────────────────┐
│           主进程 (Main)               │
│  ┌─────────┐ ┌──────────┐ ┌───────┐ │
│  │ env.js  │ │packages.js│ │tools.js│ │
│  └────┬────┘ └─────┬────┘ └───┬───┘ │
│       └────────────┼───────────┘      │
│              ipcMain.handle           │
├────────────────────┼──────────────────┤
│        预加载 (contextBridge)         │
│              window.api               │
├────────────────────┼──────────────────┤
│         渲染进程 (Renderer)           │
│  ┌─────────────────────────────────┐ │
│  │     renderer.js                 │ │
│  │  env tab │ packages tab         │ │
│  └─────────────────────────────────┘ │
└──────────────────────────────────────┘
```

## 模块职责

| 模块 | 职责 | 进程 |
|------|------|------|
| env | 环境变量分类、注册表CRUD、PATH管理 | 主 |
| packages | pip列表、标签映射、安装/卸载 | 主 |
| tools | 版本检测（java/python/node/go/rust/android） | 主 |
| ui | 标签页、筛选器、列表渲染、分页、对话框 | 渲染 |

## 数据流

```
用户操作 → renderer.js → window.api.xxx()
  → ipcRenderer.invoke() → ipcMain.handle()
  → 主进程模块 → execSync / reg.exe
  → 返回结果 → renderer → 更新DOM
```
