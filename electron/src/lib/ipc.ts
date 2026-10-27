import type {
  RpcMethod,
  NotificationMethod,
  RpcParamsMap,
  RpcResultMap,
  NotificationParamsMap,
} from './types'

export async function rpc<M extends RpcMethod>(
  method: M,
  params?: RpcParamsMap[M],
): Promise<RpcResultMap[M]> {
  return window.api.rpc(method, params as object | undefined) as Promise<RpcResultMap[M]>
}

export function onNotification<M extends NotificationMethod>(
  method: M,
  handler: (params: NotificationParamsMap[M]) => void,
): () => void {
  return window.api.onNotification(method, handler as (params: unknown) => void)
}
