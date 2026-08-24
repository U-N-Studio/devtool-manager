# DevTool Manager — 常见问题与排坑

| 问题 | 原因 | 解决 |
|------|------|------|
| 窗口空白 ERR_FILE_NOT_FOUND | loadFile 路径错误 | 用 `path.join(__dirname, "..", "renderer", "index.html")` |
| 注册表写入拒绝访问 | 系统 env var 需要管理员权限 | 以管理员身份运行，或只编辑 user 级变量 |
| pip list 失败/超时 | pip 不在 PATH 或网络超时 | 确保 Python/pip 在 PATH；timeout 设 30s |
| WM_SETTINGCHANGE 不生效 | PowerShell 广播命令静默失败 | 新终端会自动读取；不行则重启 |
| 包列表渲染慢 | 200+ DOM 同时创建 | 分页 50/页已实现 |
| npm install 407 | 公司代理需认证 | `npm config delete proxy; npm config delete https-proxy` |
| 版本命令超时 | 工具未安装，命令挂起 | 所有版本命令 5s timeout，失败返回 null |
| electron-builder 找不到 icon | assets/icon.ico 不存在 | 添加图标或移除 icon 配置 |
