# protocol/ - Electron到后端的接口协议

## 职责

定义**Electron主进程到Python后端**的JSON-RPC 2.0通信协议。

## 文件

- `schema.json` - JSON-RPC 2.0 协议定义
  - 方法定义（methods）
  - 通知定义（notifications）
  - 错误码定义（errorCodes）

## 映射关系

```
┌─────────────────┐
│    Frontend     │
│   (React UI)    │
└────────┬────────┘
         │
         │ share/types.ts
         ↓
┌─────────────────┐
│    Electron     │
│  Main Process   │
└────────┬────────┘
         │
         │ protocol/schema.json  ← 这里
         ↓
┌─────────────────┐
│    Backend      │
│   (Python)      │
└─────────────────┘
```

**Electron 主进程**：
- 在 `electron/main/pythonBridge.ts` 中调用后端
- 遵循此协议发送 JSON-RPC 请求

**后端**：
- 在 `backend/implementations/python/` 中实现这些方法
- 使用 `protocol.py` 校验消息格式

## 与 share/ 的关系

- **share/** - UI端到Electron的接口（IPC）
- **protocol/** - Electron到后端的接口（JSON-RPC）
- 两者独立，分别定义不同层之间的通信契约

## 原则

- 只放协议定义，不放实现代码
- Electron主进程和后端都依赖此目录
- 修改协议需同时更新Electron和后端实现
