/* eslint-disable */
// 此文件由 scripts/generate-types.mjs 自动生成，请勿手动修改
// 源文件: protocol/schema.json

// ============== 数据类型 ==============

export type EnvItem = { name: string; value: string; source: "system" | "user"; is_path_entry?: boolean }

export type ToolInfoDetail = { label: string; value: string }

export type ToolInfo = { installed: boolean; version?: string | null; home?: string | null; compiler?: string | null; sdk?: string | null; ndk?: string | null; details: ToolInfoDetail[] }

export type CommandSubcommand = { name: string; description: string; category?: string; has_params?: boolean }

export type CommandEnvVar = { name: string; value: string; set: boolean }

export type CommandConfigItem = { key: string; value: string }

export type CommandConfigSection = { level: string; items: CommandConfigItem[] }

export type CommandDetail = { name: string; installed: boolean; version: string; path: string; description: string; subcommands?: CommandSubcommand[]; env_vars?: CommandEnvVar[]; config_sections?: CommandConfigSection[] }

export type SubcommandParam = { name: string; description: string }

export type SubcommandHelp = { command: string; subcommand: string; params?: SubcommandParam[]; pathParams?: SubcommandParam[] }

export type HistoryEntry = { id: string; command: string; timestamp: number; exitCode?: number | null }

export type FavoriteEntry = { command: string; label: string; timestamp: number }

export type CommandItem = { name: string; installed: boolean }

export type OkResult = { ok: boolean }

// ============== 方法类型 ==============

export interface RpcParamsMap {
  'ping': Record<string, never>
  'env.list': Record<string, never>
  'env.set_var': { name: string; value: string; source?: "system" | "user" }
  'env.delete_var': { name: string; source?: "system" | "user" }
  'env.add_path_entry': { value: string; source?: "system" | "user" }
  'env.delete_path_entry': { value: string; source?: "system" | "user" }
  'env.get_raw_path': { source?: "system" | "user" }
  'env.python_info': Record<string, never>
  'tools.info': { category: string }
  'packages.list': { func?: string; lang?: string; install?: string }
  'packages.install': { name: string }
  'packages.uninstall': { name: string }
  'commands.list': { installed_only?: boolean }
  'commands.detail': { name: string }
  'commands.description': { name: string }
  'commands.subcommand_help': { command: string; subcommand: string }
  'executor.execute': { command: string; cwd?: string; env?: Record<string, string> }
  'executor.kill': { sessionId: string }
  'history.list': Record<string, never>
  'history.add': { command: string; exitCode?: number | null }
  'history.clear': Record<string, never>
  'history.delete': { id: string }
  'favorites.list': Record<string, never>
  'favorites.add': { command: string; label?: string }
  'favorites.remove': { command: string }
  'shutdown': Record<string, never>
}

export interface RpcResultMap {
  'ping': { pong: boolean }
  'env.list': { items: Record<string, EnvItem[]> }
  'env.set_var': OkResult
  'env.delete_var': OkResult
  'env.add_path_entry': OkResult
  'env.delete_path_entry': OkResult
  'env.get_raw_path': { value: string }
  'env.python_info': { version: string; pip: string; platform: string; executable: string }
  'tools.info': ToolInfo
  'packages.list': { items: { name: string; version?: string; installed: boolean; func_tag?: string; lang_tag?: string }[] }
  'packages.install': { ok: boolean; output: string }
  'packages.uninstall': { ok: boolean; output: string }
  'commands.list': { items: CommandItem[] }
  'commands.detail': CommandDetail
  'commands.description': { text: string }
  'commands.subcommand_help': SubcommandHelp
  'executor.execute': { sessionId: string }
  'executor.kill': OkResult
  'history.list': { items: HistoryEntry[] }
  'history.add': OkResult
  'history.clear': OkResult
  'history.delete': OkResult
  'favorites.list': { items: FavoriteEntry[] }
  'favorites.add': OkResult
  'favorites.remove': OkResult
  'shutdown': {  }
}

export type RpcMethod = keyof RpcParamsMap

// ============== 通知类型 ==============

export interface NotificationParamsMap {
  'ready': Record<string, never>
  'executor.output': { sessionId: string; stream: "stdout" | "stderr"; line: string }
  'executor.done': { sessionId: string; exitCode: number }
  'env.changed': Record<string, never>
}

export type NotificationMethod = keyof NotificationParamsMap

// ============== 错误码 ==============

export const ERROR_CODES = {
  '-32700': 'Parse error',
  '-32600': 'Invalid request',
  '-32601': 'Method not found',
  '-32602': 'Invalid params',
  '-32603': 'Internal error',
} as const

export type ErrorCode = keyof typeof ERROR_CODES

// ============== JSON-RPC 类型 ==============

export interface JsonRpcRequest<M extends RpcMethod = RpcMethod> {
  jsonrpc: "2.0"
  id: string
  method: M
  params: RpcParamsMap[M]
}

export interface JsonRpcResponse<R = unknown> {
  jsonrpc: "2.0"
  id: string
  result?: R
  error?: { code: number; message: string; data?: unknown }
}

export interface JsonRpcNotification<N extends NotificationMethod = NotificationMethod> {
  jsonrpc: "2.0"
  method: N
  params: NotificationParamsMap[N]
}

// ============== 协议元数据 ==============

export const PROTOCOL_VERSION = '1.0.0'