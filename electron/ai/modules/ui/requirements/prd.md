# ui 模块 — 需求

> 架构: [overview](../../architecture/overview.md) | IPC: [ipc-contract](../../architecture/ipc-contract.md)
> 设计: [design](../design/design.md) | 编码: [coding](../coding/coding.md)
> 源码: `src/renderer/renderer.js` + `src/renderer/css/style.css`
> 依赖模块: [env](../env/requirements/prd.md) | [packages](../packages/requirements/prd.md) | [tools](../tools/requirements/prd.md)

| ID | 需求 | 优先级 |
|----|------|--------|
| UI-1 | 双标签页布局 (Environment / Packages) | P0 |
| UI-2 | 暗色主题 | P1 |
| UI-3 | 响应式布局，最小 800×500 | P1 |
| UI-4 | 环境标签: 分类下拉 + 工具信息卡 + 变量列表 + Add/Edit/Del | P0 |
| UI-5 | 包标签: 3个独立筛选下拉 + 分页列表 + Add/Del | P0 |
| UI-6 | 包列表每行显示 [func_tag] [lang_tag] [install_tag] name version [按钮] | P0 |
| UI-7 | 分页 50/页，Prev/Next + 页码信息 | P0 |
| UI-8 | 删除操作需确认 | P0 |
| UI-9 | Loading 状态提示 | P1 |

## 测试用例

| TC | 步骤 | 预期 |
|----|------|------|
| UI-T1 | 点击 Packages 标签 | 切换到包标签页，环境标签不丢失 |
| UI-T2 | 包标签切换3个筛选器 | 列表实时更新，筛选独立组合 |
| UI-T3 | 205+包列表首次加载 | < 1s 渲染完成（分页50条） |
| UI-T4 | 点击 Del | 弹出 confirm 对话框 |
