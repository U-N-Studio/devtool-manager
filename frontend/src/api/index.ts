/**
 * 统一后端调用 API。
 *
 * 前端各 store 只依赖本层,不直接接触传输细节或方法名。
 * 后端实现可替换:传输变化只改 client.ts;协议变化改本层函数签名。
 */
import { request, subscribe } from './client'
import type {
  CommandDetail,
  CommandItem,
  SubcommandHelp,
  ToolInfo,
  HistoryEntry,
  FavoriteEntry,
} from '@/lib/types'

/* ------------------------------ 环境变量 ------------------------------ */

export const env = {
  /** 获取分类环境变量列表(分类名 -> 条目列表) */
  list: () =>
    request('env.list', {}).then((r) => r.items),

  /** 获取 Python 运行时信息 */
  pythonInfo: () =>
    request('env.python_info', {}),

  /** 设置环境变量 */
  setVar: (name: string, value: string, source: 'system' | 'user' = 'user') =>
    request('env.set_var', { name, value, source }).then((r) => r.ok),

  /** 删除环境变量 */
  deleteVar: (name: string, source: 'system' | 'user' = 'user') =>
    request('env.delete_var', { name, source }).then((r) => r.ok),

  /** 往 PATH 追加一个条目 */
  addPathEntry: (value: string, source: 'system' | 'user' = 'user') =>
    request('env.add_path_entry', { value, source }).then((r) => r.ok),

  /** 从 PATH 移除一个条目 */
  deletePathEntry: (value: string, source: 'system' | 'user' = 'user') =>
    request('env.delete_path_entry', { value, source }).then((r) => r.ok),

  /** 获取指定来源的原始 PATH 字符串 */
  getRawPath: (source: 'system' | 'user' = 'user') =>
    request('env.get_raw_path', { source }).then((r) => r.value),
}

/* ------------------------------ 工具信息 ------------------------------ */

export const tools = {
  /** 探测指定分类工具链信息 */
  info: (category: string): Promise<ToolInfo> =>
    request('tools.info', { category }),
}

/* ------------------------------ 命令 ------------------------------ */

export const commands = {
  /** 获取命令列表,可选仅显示已安装 */
  list: (installedOnly = false): Promise<CommandItem[]> =>
    request('commands.list', { installed_only: installedOnly }).then((r) => r.items),

  /** 获取命令详情(版本/参数/子命令/环境变量/配置段) */
  detail: (name: string): Promise<CommandDetail> =>
    request('commands.detail', { name }),

  /** 获取命令中文描述 */
  description: (name: string): Promise<string> =>
    request('commands.description', { name }).then((r) => r.text),

  /** 获取子命令帮助(参数与路径参数中文说明) */
  subcommandHelp: (command: string, subcommand: string): Promise<SubcommandHelp> =>
    request('commands.subcommand_help', { command, subcommand }),
}

/* ------------------------------ 执行器 ------------------------------ */

export const executor = {
  /** 启动命令执行,立即返回 sessionId;输出/完成通过 notification 推送 */
  execute: (command: string, cwd?: string, env?: Record<string, string>): Promise<string> =>
    request('executor.execute', { command, cwd, env }).then((r) => r.sessionId),

  /** 按 sessionId 终止正在运行的进程 */
  kill: (sessionId: string): Promise<boolean> =>
    request('executor.kill', { sessionId }).then((r) => r.ok),
}

/* ------------------------------ 历史与收藏 ------------------------------ */

export const history = {
  list: (): Promise<HistoryEntry[]> =>
    request('history.list', {}).then((r) => r.items),
  add: (command: string, exitCode?: number): Promise<boolean> =>
    request('history.add', { command, exitCode }).then((r) => r.ok),
  clear: (): Promise<boolean> =>
    request('history.clear', {}).then((r) => r.ok),
  delete: (id: string): Promise<boolean> =>
    request('history.delete', { id }).then((r) => r.ok),
}

export const favorites = {
  list: (): Promise<FavoriteEntry[]> =>
    request('favorites.list', {}).then((r) => r.items),
  add: (command: string, label?: string): Promise<boolean> =>
    request('favorites.add', { command, label }).then((r) => r.ok),
  remove: (command: string): Promise<boolean> =>
    request('favorites.remove', { command }).then((r) => r.ok),
}

/* ------------------------------ 通知订阅 ------------------------------ */

export const notifications = {
  /** 订阅命令输出流 */
  onOutput: (handler: (params: { sessionId: string; stream: 'stdout' | 'stderr'; line: string }) => void) =>
    subscribe('executor.output', handler),

  /** 订阅命令执行完成 */
  onDone: (handler: (params: { sessionId: string; exitCode: number }) => void) =>
    subscribe('executor.done', handler),

  /** 订阅环境变更广播 */
  onEnvChanged: (handler: () => void) =>
    subscribe('env.changed', handler),

  /** 订阅后端就绪 */
  onReady: (handler: () => void) =>
    subscribe('ready', handler),
}

/* ------------------------------ 生命周期 ------------------------------ */

export const system = {
  /** 协议版本号 */
  protocolVersion: '1.0.0',
  ping: (): Promise<boolean> =>
    request('ping', {}).then((r) => r.pong),
  shutdown: (): Promise<void> =>
    request('shutdown', {}).then(() => undefined),
}

/* 聚合导出:api.env / api.commands / ... */
export const api = { env, tools, commands, executor, history, favorites, notifications, system }
