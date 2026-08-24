# DevTool Manager — 编码指南

## 项目结构

```
electron/
├── package.json
├── .gitignore
├── src/
│   ├── main/
│   │   ├── index.js        # BrowserWindow + IPC 注册
│   │   ├── preload.js      # contextBridge → window.api
│   │   ├── env.js          # 注册表 CRUD, PATH, 广播
│   │   ├── packages.js     # pip list, 标签映射, 安装/卸载
│   │   └── tools.js        # 版本检测
│   └── renderer/
│       ├── index.html      # 标签页布局
│       ├── renderer.js     # 全部 UI 逻辑
│       └── css/style.css   # 暗色主题
```

## 编码规范

- 主进程: CommonJS (require/module.exports)
- 渲染进程: 原生 JS，无框架无构建
- 子进程: 全部使用 `execSync({ windowsHide: true, timeout })`
- 注册表: 全部使用 `reg.exe`，加 `/reg:64` 标志
- XSS: 渲染进程用 `esc()` 函数转义所有动态内容
- 错误处理: 主进程 try-catch 返回默认值，渲染进程 try-finally 清理状态

## 实现顺序

1. env.js → 2. packages.js → 3. tools.js → 4. preload.js → 5. index.js → 6. renderer.js → 7. style.css
