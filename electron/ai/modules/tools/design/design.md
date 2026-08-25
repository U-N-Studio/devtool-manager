# tools 模块 — 设计

> 需求: [prd](../requirements/prd.md) | 编码: [coding](../coding/coding.md)
> IPC: [ipc-contract](../../architecture/ipc-contract.md) | 源码: `src/main/tools.js`

## 概要

- 每个工具一个 `getXxxInfo()` 函数
- 底层: `runVersionCmd(args, timeout=5)` → execSync + windowsHide
- 返回统一结构: `{ installed, version?, details[] }`

## 详细

### runVersionCmd(args, timeout=5)
- execSync(args.join(" "), { windowsHide:true, timeout, stdio:["pipe","pipe","pipe"] })
- 返回 (stdout+stderr).trim()，失败返回 null

### getJavaInfo()
- java -version → version 行
- javac -version → compiler
- jar --version
- JAVA_HOME env

### getPythonInfo()
- python --version
- python -m pip --version
- conda/poetry/uv --version (which 检测)

### getAndroidInfo()
- ANDROID_HOME / ANDROID_SDK_ROOT → sdk
- ANDROID_NDK_HOME → ndk
- adb version, gradle --version

### getNodeInfo()
- node --version, npm --version
- yarn/pnpm/bun --version

### getGoInfo()
- go version
- GOROOT, GOPATH env

### getRustInfo()
- rustc --version, cargo --version, rustup --version

## API

| 通道 | 参数 | 返回 |
|------|------|------|
| tools:getInfo | category | { installed, version?, home?, details[] } |
