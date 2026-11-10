/**
 * 后端传输层适配器。
 *
 * 当前实现基于 Electron IPC + Python stdio JSON-RPC(通过 preload 暴露的 window.api,
 * 具体见 lib/ipc.ts)。
 * 若需替换后端(如 HTTP/WebSocket 服务),只需重写本文件的 request/subscribe
 * 两个函数(替换 lib/ipc.ts 的内部实现亦可),上层 api/ 与 store 无需改动。
 */

import type {
  RpcMethod,
  NotificationMethod,
  RpcParamsMap,
  RpcResultMap,
  NotificationParamsMap,
} from '@/lib/types'
import { rpc as ipcRpc, onNotification as ipcOnNotification } from '@/lib/ipc'

/** 发起一次 RPC 请求,返回后端 result。 */
export async function request<M extends RpcMethod>(
  method: M,
  params?: RpcParamsMap[M],
): Promise<RpcResultMap[M]> {
  return ipcRpc(method, params)
}

/** 订阅后端推送的通知,返回取消订阅函数。 */
export function subscribe<M extends NotificationMethod>(
  method: M,
  handler: (params: NotificationParamsMap[M]) => void,
): () => void {
  return ipcOnNotification(method, handler)
}
