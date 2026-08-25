# tools 模块 — 需求

> 架构: [overview](../../architecture/overview.md) | IPC: [ipc-contract](../../architecture/ipc-contract.md)
> 设计: [design](../design/design.md) | 编码: [coding](../coding/coding.md)
> 源码: `src/main/tools.js`

| ID | 需求 | 优先级 |
|----|------|--------|
| TOOL-1 | 检测 Java 版本、JAVA_HOME、javac、jar | P1 |
| TOOL-2 | 检测 Python 版本、pip、conda、poetry、uv | P1 |
| TOOL-3 | 检测 Android SDK/NDK、adb、gradle | P1 |
| TOOL-4 | 检测 Node.js 版本、npm、yarn、pnpm、bun | P1 |
| TOOL-5 | 检测 Go 版本、GOROOT、GOPATH | P1 |
| TOOL-6 | 检测 Rust 版本、cargo、rustup | P1 |
| TOOL-7 | 分类切换时自动刷新工具信息卡 | P1 |

## 测试用例

| TC | 前置 | 步骤 | 预期 |
|----|------|------|------|
| TOOL-T1 | JDK 已安装 | 选 Java 分类 | 信息卡显示 version/javac/JAVA_HOME |
| TOOL-T2 | Python 已安装 | 选 Python 分类 | 信息卡显示 python/pip 版本 |
| TOOL-T3 | 工具未安装 | 选对应分类 | 信息卡不显示或显示 installed=false |
