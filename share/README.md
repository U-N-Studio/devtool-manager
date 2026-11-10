# share/ - UI端到Electron的接口类型

## 职责

定义**前端UI（React）到Electron主进程**的通信接口类型。

## 文件

- `types.ts` - TypeScript 类型定义
  - IPC 消息类型
  - 业务实体类型
  - API 接口类型

## 映射关系

```
┌─────────────────┐
│    Frontend     │
│   (React UI)    │
└────────┬────────┘
         │
         │ window.api (share/types.ts)  ← 这里
         ↓
┌─────────────────┐
│    Electron     │
│  Main Process   │
└────────┬────────┘
         │
         │ protocol/schema.json
         ↓
┌─────────────────┐
│    Backend      │
│   (Python)      │
└─────────────────┘
```

**前端**：
- 通过 `frontend/src/lib/types.ts` 重导出
- 导入路径：`import type { EnvItem } from '@/lib/types'`

**Electron 主进程**：
- 在 `electron/main/` 中实现这些接口
- 通过 preload 暴露给前端

## 与 protocol/ 的关系

- **share/** - UI端到Electron的接口（IPC）
- **protocol/** - Electron到后端的接口（JSON-RPC）
- 两者独立，分别定义不同层之间的通信契约

## 原则

- 只放类型定义，不放实现代码
- 前端和Electron主进程都依赖此目录
- 修改类型需同时更新前端和Electron实现
