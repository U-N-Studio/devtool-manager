# DevTool Manager — 概要设计

## 模块划分

| 模块 | 职责 | 文件 |
|------|------|------|
| App | 窗口创建、IPC注册、生命周期 | src/main/index.js |
| Env | 环境变量分类、注册表CRUD、PATH管理、广播 | src/main/env.js |
| Packages | pip列表、标签映射、安装/卸载 | src/main/packages.js |
| Tools | 版本检测（java/python/node/go/rust/android） | src/main/tools.js |
| Preload | IPC桥接，暴露window.api | src/main/preload.js |
| Renderer | 全部UI逻辑 | src/renderer/renderer.js |

## 数据流

```
用户操作 → renderer.js → window.api.xxx() → ipcRenderer.invoke()
    → ipcMain.handle() → 主进程模块 → execSync / reg.exe
    → 返回结果 → renderer → 更新DOM
```

## 关键数据结构

### 环境变量
```js
{ name: "JAVA_HOME", value: "C:\\jdk", source: "system", isPathEntry?: true }
```

### 包
```js
{ name: "pytest", version: "8.0.0", func_tag: "Dev Tools", lang_tag: "Python", install_tag: "Installed" }
```

### 工具信息
```js
{ installed: true, version: "17.0.1", home: "C:\\jdk", details: ["javac: 17.0.1"] }
```
