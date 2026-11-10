# DevTool Manager 后端 API 协议

**backend 是独立服务**。前端通过本协议消费后端能力，任何满足该协议的实现
（当前为 Python stdio JSON-RPC，未来可以是 Go/Node/远程 HTTP 服务）都可替换，
前端无需改动。

## 协议文件

- `protocol/schema.json` — JSON-RPC 2.0 协议唯一事实来源（方法/入参/出参/通知/错误码）
- `backend/implementations/python/protocol.py` — Python 后端加载协议并校验方法名（未声明的方法拒绝 -32601）
- `share/types.ts` — TypeScript 类型定义，与 schema.json 保持同步

## 传输层

- **协议**：newline-delimited JSON-RPC 2.0（每行一条 JSON 消息）
- **当前传输**：stdio（Electron 主进程 spawn 后端进程，stdin 发请求、stdout 收响应）
- **可替换**：HTTP / WebSocket / 命名管道 等任意传输，只要消息格式是 JSON-RPC 2.0

## 方法总览

| 方法 | 入参 | 出参 |
|------|------|------|
| `ping` | - | `{ pong: boolean }` |
| `env.list` | - | `{ items: Record<分类, EnvItem[]> }` |
| `env.set_var` | `name, value, source?` | `{ ok }` |
| `env.delete_var` | `name, source?` | `{ ok }` |
| `env.add_path_entry` | `value, source?` | `{ ok }` |
| `env.delete_path_entry` | `value, source?` | `{ ok }` |
| `env.get_raw_path` | `source?` | `{ value }` |
| `env.python_info` | - | `{ version, pip, platform, executable }` |
| `tools.info` | `category` | `ToolInfo` |
| `commands.list` | `installed_only?` | `{ items: CommandItem[] }` |
| `commands.detail` | `name` | `CommandDetail` |
| `commands.description` | `name` | `{ text }` |
| `commands.subcommand_help` | `command, subcommand` | `SubcommandHelp` |
| `executor.execute` | `command, cwd?, env?` | `{ sessionId }`（输出走通知） |
| `executor.kill` | `sessionId` | `{ ok }` |
| `history.list` | - | `{ items: HistoryEntry[] }` |
| `history.add` | `command, exitCode?` | `{ ok }` |
| `history.clear` | - | `{ ok }` |
| `history.delete` | `id` | `{ ok }` |
| `favorites.list` | - | `{ items: FavoriteEntry[] }` |
| `favorites.add` | `command, label?` | `{ ok }` |
| `favorites.remove` | `command` | `{ ok }` |
| `shutdown` | - | - |

## 通知（后端 → 前端，无 id）

| 通知 | 参数 |
|------|------|
| `ready` | - |
| `executor.output` | `{ sessionId, stream: 'stdout'\|'stderr', line }` |
| `executor.done` | `{ sessionId, exitCode }` |
| `env.changed` | - |

## 错误码

| code | 含义 |
|------|------|
| -32700 | Parse error（JSON 解析失败） |
| -32600 | Invalid request |
| -32601 | Method not found（不在协议内） |
| -32602 | Invalid params |
| -32603 | Internal error |

## 前端消费

前端 `frontend/src/api/` 层按协议生成强类型调用函数（`api.env.list()` 等），
方法名从 `schema.json` 读取，与后端保持同步。传输替换时仅改 `api/client.ts`。
