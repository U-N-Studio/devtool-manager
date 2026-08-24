# packages 模块 — 设计

## 概要

- 已安装包: `pip list --format=json`
- 标签映射: PKG_TAGS 静态表 (~150条)，key=包名小写，value=[func_tag, lang_tag]
- 筛选: 主进程完成，返回已筛选+已排序的完整列表
- 分页: 渲染进程自行切页

## 详细

### PKG_TAGS
- 键: 包名小写 (如 "pytest")
- 值: [func_tag, lang_tag] (如 ["Dev Tools", "Python"])
- 未收录包默认: ["Other", "Python"]

### getCategorizedPackages(funcTag, langTag, installTag)
1. `pip list --format=json` → installedPkgs[]
2. installedSet = 已安装包名集合
3. allNames = installedSet ∪ Object.keys(PKG_TAGS)
4. 遍历 allNames:
   - 查 PKG_TAGS 获取 [func_tag, lang_tag]
   - 判断 installedSet 中是否存在 → install_tag
   - 按 3 个 tag 筛选（空串=不筛选）
5. 已安装取 name+version，未安装 version=""
6. 按 name 排序返回

### installPackage(name)
- `pip install "name"` → { ok, output }

### uninstallPackage(name)
- `pip uninstall -y "name"` → { ok, output }

## API

| 通道 | 参数 | 返回 |
|------|------|------|
| packages:getList | funcTag, langTag, installTag | [{ name, version, func_tag, lang_tag, install_tag }] |
| packages:install | name | { ok, output } |
| packages:uninstall | name | { ok, output } |
| packages:getFuncTags | — | string[] |
| packages:getLangTags | — | string[] |
