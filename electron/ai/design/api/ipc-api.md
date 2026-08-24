# DevTool Manager — API 设计 (IPC Contract)

## env 通道

| 通道 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| env:getCategorized | — | `{ [category]: [{ name, value, source, isPathEntry? }] }` | 获取分类环境变量 |
| env:set | name, value, source | `boolean` | 设置环境变量（写入注册表+广播） |
| env:delete | name, source | `boolean` | 删除环境变量 |
| env:addPath | entry, source | `boolean` | 追加 PATH 条目 |
| env:deletePath | entry, source | `boolean` | 删除单条 PATH 条目 |

## packages 通道

| 通道 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| packages:getList | funcTag, langTag, installTag | `[{ name, version, func_tag, lang_tag, install_tag }]` | 获取筛选后的包列表 |
| packages:install | name | `{ ok, output }` | 安装包 |
| packages:uninstall | name | `{ ok, output }` | 卸载包 |
| packages:getFuncTags | — | `string[]` | 获取功能标签列表 |
| packages:getLangTags | — | `string[]` | 获取语言标签列表 |

## tools 通道

| 通道 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| tools:getInfo | category | `{ installed, version?, home?, details[] }` | 获取工具版本信息 |

## 数据类型

### EnvVar
```typescript
interface EnvVar {
  name: string;        // 变量名
  value: string;       // 变量值
  source: "system" | "user";  // 来源
  isPathEntry?: boolean;      // 是否为PATH条目
}
```

### Package
```typescript
interface Package {
  name: string;
  version: string;
  func_tag: string;    // 功能标签
  lang_tag: string;    // 语言标签
  install_tag: "Installed" | "Not Installed";
}
```

### ToolInfo
```typescript
interface ToolInfo {
  installed: boolean;
  version?: string;
  home?: string;
  sdk?: string;       // Android only
  ndk?: string;       // Android only
  compiler?: string;  // Java only
  details: string[];
}
```
