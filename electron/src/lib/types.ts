// JSON-RPC 2.0 message types
export interface JsonRpcRequest<M extends string = string, P = unknown> {
  jsonrpc: '2.0'
  id: string
  method: M
  params?: P
}

export interface JsonRpcResponse<R = unknown> {
  jsonrpc: '2.0'
  id: string
  result?: R
  error?: { code: number; message: string; data?: unknown }
}

export interface JsonRpcNotification<M extends string = string, P = unknown> {
  jsonrpc: '2.0'
  method: M
  params?: P
}

// Business types
export interface EnvItem {
  name: string
  value: string
  source: 'system' | 'user'
  is_path_entry?: boolean
}

export interface PythonInfo {
  version: string
  pip: string
  platform: string
  executable: string
}

export interface ToolInfoDetail {
  label: string
  value: string
}

export interface ToolInfo {
  installed: boolean
  version?: string | null
  home?: string | null
  compiler?: string | null
  sdk?: string | null
  ndk?: string | null
  details: ToolInfoDetail[]
}

export interface PackageItem {
  name: string
  version: string
  installed: boolean
  func_tag: string
  lang_tag: string
  install_tag?: string
}

export interface CommandParam {
  name: string
  description: string
}

export interface CommandSubcommand {
  name: string
  description: string
}

export interface CommandEnvVar {
  name: string
  value: string
  set: boolean
}

export interface HistoryEntry {
  id: string
  command: string
  timestamp: number
  exitCode: number | null
}

export interface FavoriteEntry {
  command: string
  label: string
  timestamp: number
}

export interface SubcommandParam {
  name: string
  description: string
}

export interface SubcommandHelp {
  command: string
  subcommand: string
  params: SubcommandParam[]
  pathParams: SubcommandParam[]
}

export interface CommandConfigItem {
  key: string
  value: string
}

export interface CommandConfigSection {
  level: string
  items: CommandConfigItem[]
}

export interface CommandDetail {
  name: string
  installed: boolean
  version: string
  path: string
  description: string
  params: CommandParam[]
  subcommands: CommandSubcommand[]
  env_vars: CommandEnvVar[]
  config_sections: CommandConfigSection[]
}

// RPC method union
export type RpcMethod =
  | 'ping'
  | 'env.list'
  | 'env.python_info'
  | 'env.set_var'
  | 'env.delete_var'
  | 'env.add_path_entry'
  | 'env.delete_path_entry'
  | 'env.get_raw_path'
  | 'tools.info'
  | 'packages.list'
  | 'packages.install'
  | 'packages.uninstall'
  | 'commands.list'
  | 'commands.detail'
  | 'commands.description'
  | 'commands.subcommand_help'
  | 'executor.execute'
  | 'executor.kill'
  | 'history.list'
  | 'history.add'
  | 'history.clear'
  | 'history.delete'
  | 'favorites.list'
  | 'favorites.add'
  | 'favorites.remove'
  | 'shutdown'

export type NotificationMethod = 'ready' | 'executor.output' | 'executor.done' | 'env.changed'

// Params map per RPC method
export interface RpcParamsMap {
  ping: Record<string, never>
  'env.list': Record<string, never>
  'env.python_info': Record<string, never>
  'env.set_var': { name: string; value: string; source?: 'system' | 'user' }
  'env.delete_var': { name: string; source?: 'system' | 'user' }
  'env.add_path_entry': { value: string; source?: 'system' | 'user' }
  'env.delete_path_entry': { value: string; source?: 'system' | 'user' }
  'env.get_raw_path': { source?: 'system' | 'user' }
  'tools.info': { category: string }
  'packages.list': { func?: string; lang?: string; install?: string }
  'packages.install': { name: string }
  'packages.uninstall': { name: string }
  'commands.list': { installed_only?: boolean }
  'commands.detail': { name: string }
  'commands.description': { name: string }
  'commands.subcommand_help': { command: string; subcommand: string }
  'executor.execute': {
    command: string
    cwd?: string
    env?: Record<string, string>
  }
  'executor.kill': { sessionId: string }
  'history.list': { items: HistoryEntry[] }
  'history.add': { command: string; exitCode?: number }
  'history.clear': { ok: boolean }
  'history.delete': { id: string }
  'favorites.list': { items: FavoriteEntry[] }
  'favorites.add': { command: string; label?: string }
  'favorites.remove': { command: string }
  shutdown: Record<string, never>
}

// Result map per RPC method
export interface RpcResultMap {
  ping: { pong: boolean }
  'env.list': { items: Record<string, EnvItem[]> }
  'env.python_info': PythonInfo
  'env.set_var': { ok: boolean }
  'env.delete_var': { ok: boolean }
  'env.add_path_entry': { ok: boolean }
  'env.delete_path_entry': { ok: boolean }
  'env.get_raw_path': { value: string }
  'tools.info': ToolInfo
  'packages.list': { items: PackageItem[] }
  'packages.install': { ok: boolean; output: string }
  'packages.uninstall': { ok: boolean; output: string }
  'commands.list': { items: { name: string; installed: boolean }[] }
  'commands.detail': CommandDetail
  'commands.description': { text: string }
  'commands.subcommand_help': SubcommandHelp
  'executor.execute': { sessionId: string }
  'executor.kill': { ok: boolean }
  'history.list': { items: HistoryEntry[] }
  'history.add': { ok: boolean }
  'history.clear': { ok: boolean }
  'history.delete': { ok: boolean }
  'favorites.list': { items: FavoriteEntry[] }
  'favorites.add': { ok: boolean }
  'favorites.remove': { ok: boolean }
  shutdown: Record<string, never>
}

// Notification params map
export interface NotificationParamsMap {
  ready: Record<string, never>
  'executor.output': { sessionId: string; stream: 'stdout' | 'stderr'; line: string }
  'executor.done': { sessionId: string; exitCode: number }
  'env.changed': Record<string, never>
}
