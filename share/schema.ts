/**
 * 协议元数据。
 *
 * 协议唯一事实来源是 protocol/schema.json。
 */

import schema from '../protocol/schema.json'

export interface ProtocolMethod {
  name: string
  params?: object
  result?: object
}

export interface ProtocolNotification {
  name: string
  params?: object
}

/** 协议声明的全部 RPC 方法名 */
export const PROTOCOL_METHODS: string[] = (schema as { methods: ProtocolMethod[] }).methods.map(
  (m) => m.name,
)

/** 协议声明的全部通知名 */
export const PROTOCOL_NOTIFICATIONS: string[] = (
  schema as { notifications: ProtocolNotification[] }
).notifications.map((n) => n.name)

/** 协议版本 */
export const PROTOCOL_VERSION: string = (schema as { version: string }).version
