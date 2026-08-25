# DevTool Manager — 架构决策记录 (ADR)

> 架构: [overview](overview.md) | IPC: [ipc-contract](ipc-contract.md)

## ADR-1: 渲染进程不用框架
- **决策**: 使用原生 HTML/CSS/JS，不用 React/Vue
- **原因**: 无构建步骤，包体积小，依赖少，Electron 自带浏览器引擎
- **代价**: 无组件复用、无状态管理库，靠 DOM 操作

## ADR-2: 主进程用 execSync
- **决策**: 所有子进程调用用 execSync 而非 spawn
- **原因**: 注册表查询/pip list 都是短命令，同步简单直接
- **代价**: 长时间命令（pip install）会阻塞主进程；用 timeout 限制

## ADR-3: 注册表用 reg.exe
- **决策**: 通过 reg.exe 命令行操作注册表，不用 native 模块
- **原因**: 无需编译 native addon，兼容性好，Electron 升级无风险
- **代价**: 需解析命令行输出；权限不足时需管理员运行

## ADR-4: 标签筛选在主进程完成
- **决策**: 205+包的标签匹配和筛选在主进程完成，渲染进程只渲染当前页
- **原因**: 避免传输全量数据到渲染进程，减少 IPC 开销
- **代价**: 每次筛选变化都触发一次 IPC 调用

## ADR-5: 分页在渲染进程
- **决策**: 主进程返回全量筛选结果，渲染进程自行分页
- **原因**: 分页是纯 UI 逻辑，切页无需 IPC
- **代价**: 大结果集全量传输一次（但已筛选，通常 <200 条）

## ADR-6: contextIsolation=true
- **决策**: 启用上下文隔离，通过 contextBridge 暴露 API
- **原因**: 安全最佳实践，防止渲染进程访问 Node API
- **代价**: 需显式定义 preload 桥接
