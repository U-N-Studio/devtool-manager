# packages 模块 — 编码

## 排坑

| 问题 | 原因 | 解决 |
|------|------|------|
| pip list 超时 | pip 不在 PATH 或网络慢 | timeout 30s，失败返回空数组 |
| install 卡住 | 网络慢或包不存在 | timeout 120s |
| PKG_TAGS 未收录新包 | 新包不在静态表 | 默认 ["Other", "Python"] |

## 审查清单

- [ ] pip 命令带 windowsHide:true
- [ ] PKG_TAGS 覆盖项目实际依赖
- [ ] 筛选逻辑：空串=不筛选，非空=精确匹配
- [ ] install/uninstall 有 timeout
- [ ] 结果按 name 排序
