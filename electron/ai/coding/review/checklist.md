# DevTool Manager — 代码审查清单

| # | 检查项 | 类别 |
|---|--------|------|
| 1 | contextIsolation=true, nodeIntegration=false | 安全 |
| 2 | 所有 execSync 带 windowsHide:true | 安全 |
| 3 | 渲染进程不直接访问 Node API | 安全 |
| 4 | 动态内容经 esc() 转义 | 安全 |
| 5 | IPC 参数校验（非空、类型） | 健壮性 |
| 6 | execSync 有 timeout | 健壮性 |
| 7 | 注册表操作 try-catch | 健壮性 |
| 8 | 分页 PAGE_SIZE=50 | 性能 |
| 9 | 标签筛选在主进程完成 | 性能 |
| 10 | 包列表用 innerHTML 批量渲染 | 性能 |
| 11 | 删除操作有 confirm() | UX |
| 12 | Loading 状态提示 | UX |
