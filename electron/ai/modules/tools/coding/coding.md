# tools 模块 — 编码

## 排坑

| 问题 | 原因 | 解决 |
|------|------|------|
| 版本命令超时 | 工具未安装，命令挂起 | timeout 5s，返回 null |
| stderr 含版本信息 | java -version 输出到 stderr | 合并 stdout+stderr |
| gradle --version 输出多行 | 需提取版本行 | 遍历找含 "version" 的行 |

## 审查清单

- [ ] 所有 runVersionCmd 带 windowsHide:true
- [ ] timeout 不超过 5s
- [ ] stderr 和 stdout 合并处理
- [ ] 未安装工具返回 { installed: false }
- [ ] details 数组每项有意义的前缀 (如 "java:", "npm:")
