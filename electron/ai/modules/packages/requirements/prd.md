# packages 模块 — 需求

> 架构: [overview](../../architecture/overview.md) | IPC: [ipc-contract](../../architecture/ipc-contract.md)
> 设计: [design](../design/design.md) | 编码: [coding](../coding/coding.md)
> 源码: `src/main/packages.js`

| ID | 需求 | 优先级 |
|----|------|--------|
| PKG-1 | 列出所有已知包（已安装+目录），每包3个tag：func_tag, lang_tag, install_tag | P0 |
| PKG-2 | 按功能标签筛选（UI Framework/Web Framework/.../Crypto） | P0 |
| PKG-3 | 按语言标签筛选（Python/Node.js/Java/Rust/Go/C-C++/Dotnet） | P0 |
| PKG-4 | 按安装状态筛选（Installed/Not Installed） | P0 |
| PKG-5 | 三个筛选器独立且可组合 | P0 |
| PKG-6 | 分页：每页50条，Prev/Next | P0 |
| PKG-7 | 未安装行显示 Add 按钮 (pip install) | P0 |
| PKG-8 | 已安装行显示 Del 按钮 (pip uninstall -y) | P0 |
| PKG-9 | 自定义包名安装 | P1 |

## 测试用例

| TC | 步骤 | 预期 |
|----|------|------|
| PKG-T1 | Function=Dev Tools, Language=Python, Status=Installed | 仅显示已安装的 Python Dev Tools 包 |
| PKG-T2 | 筛选结果 > 50 条，点 Next → Prev | 页面切换正确，显示 1-50/总数 |
| PKG-T3 | Not Installed 行点 Add → 确认 | 包安装成功，状态变 Installed |
| PKG-T4 | Installed 行点 Del → 确认 | 包卸载成功，状态变 Not Installed |
| PKG-T5 | 三个筛选器全选 All | 显示全部 205+ 包 |
