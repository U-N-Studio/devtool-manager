/**
 * 前端侧 API 协议视图。
 *
 * 协议唯一事实来源是 backend/protocol/schema.json。本文件通过相对路径读取
 * 该文件,导出协议声明的方法名集合与通知名集合,供 api/ 层与 lib/types
 * 保持一致。若后端协议变更,方法名集合会自动反映,TS 类型仍由 lib/types 维护。
 */

// 从 backend 读取协议 JSON
import schema from '../../../backend/protocol/schema.json'

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
