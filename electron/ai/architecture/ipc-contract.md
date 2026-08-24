# DevTool Manager — 全局 IPC 契约

## env

| 通道 | 参数 | 返回值 |
|------|------|--------|
| env:getCategorized | — | `{ [category]: [{ name, value, source, isPathEntry? }] }` |
| env:set | name, value, source | `boolean` |
| env:delete | name, source | `boolean` |
| env:addPath | entry, source | `boolean` |
| env:deletePath | entry, source | `boolean` |

## packages

| 通道 | 参数 | 返回值 |
|------|------|--------|
| packages:getList | funcTag, langTag, installTag | `[{ name, version, func_tag, lang_tag, install_tag }]` |
| packages:install | name | `{ ok, output }` |
| packages:uninstall | name | `{ ok, output }` |
| packages:getFuncTags | — | `string[]` |
| packages:getLangTags | — | `string[]` |

## tools

| 通道 | 参数 | 返回值 |
|------|------|--------|
| tools:getInfo | category | `{ installed, version?, home?, details[] }` |
