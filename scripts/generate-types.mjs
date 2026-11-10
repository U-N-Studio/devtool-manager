#!/usr/bin/env node
/**
 * 从 protocol/schema.json 生成 TypeScript 类型定义
 * 用法: node scripts/generate-types.mjs
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')

const schemaPath = path.join(ROOT, 'protocol/schema.json')
const outputPath = path.join(ROOT, 'share/types.ts')

const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'))

// JSON Schema type -> TypeScript type
function jsonTypeToTs(schema) {
  if (schema.$ref) {
    const refName = schema.$ref.split('/').pop()
    return refName
  }
  
  if (schema.enum) {
    return schema.enum.map(v => JSON.stringify(v)).join(' | ')
  }
  
  if (Array.isArray(schema.type)) {
    return schema.type.map(t => jsonTypeToTs({ ...schema, type: t })).join(' | ')
  }
  
  switch (schema.type) {
    case 'string':
      return 'string'
    case 'number':
    case 'integer':
      return 'number'
    case 'boolean':
      return 'boolean'
    case 'null':
      return 'null'
    case 'array':
      const itemType = jsonTypeToTs(schema.items)
      return `${itemType}[]`
    case 'object':
      if (schema.additionalProperties === false || !schema.additionalProperties) {
        // 具体属性的对象
        const props = schema.properties || {}
        const required = new Set(schema.required || [])
        const fields = Object.entries(props).map(([key, propSchema]) => {
          const tsType = jsonTypeToTs(propSchema)
          const optional = required.has(key) ? '' : '?'
          return `${key}${optional}: ${tsType}`
        })
        return `{ ${fields.join('; ')} }`
      } else {
        // 字典类型
        const valueType = jsonTypeToTs(schema.additionalProperties)
        return `Record<string, ${valueType}>`
      }
    default:
      return 'unknown'
  }
}

function generateTypes() {
  const lines = []
  
  lines.push('/* eslint-disable */')
  lines.push('// 此文件由 scripts/generate-types.mjs 自动生成，请勿手动修改')
  lines.push('// 源文件: protocol/schema.json')
  lines.push('')
  
  // 生成 definitions
  lines.push('// ============== 数据类型 ==============')
  lines.push('')
  
  for (const [name, def] of Object.entries(schema.definitions)) {
    const tsType = jsonTypeToTs(def)
    lines.push(`export type ${name} = ${tsType}`)
    lines.push('')
  }
  
  // 生成方法类型
  lines.push('// ============== 方法类型 ==============')
  lines.push('')
  
  // 方法参数映射
  lines.push('export interface RpcParamsMap {')
  for (const method of schema.methods) {
    const params = method.params
    if (!params.properties || Object.keys(params.properties).length === 0) {
      lines.push(`  '${method.name}': Record<string, never>`)
    } else {
      const tsType = jsonTypeToTs(params)
      lines.push(`  '${method.name}': ${tsType}`)
    }
  }
  lines.push('}')
  lines.push('')
  
  // 方法结果映射
  lines.push('export interface RpcResultMap {')
  for (const method of schema.methods) {
    const result = method.result
    const tsType = jsonTypeToTs(result)
    lines.push(`  '${method.name}': ${tsType}`)
  }
  lines.push('}')
  lines.push('')
  
  // 方法名类型
  lines.push('export type RpcMethod = keyof RpcParamsMap')
  lines.push('')
  
  // 生成通知类型
  lines.push('// ============== 通知类型 ==============')
  lines.push('')
  
  lines.push('export interface NotificationParamsMap {')
  for (const notification of schema.notifications) {
    const params = notification.params
    if (!params.properties || Object.keys(params.properties).length === 0) {
      lines.push(`  '${notification.name}': Record<string, never>`)
    } else {
      const tsType = jsonTypeToTs(params)
      lines.push(`  '${notification.name}': ${tsType}`)
    }
  }
  lines.push('}')
  lines.push('')
  
  lines.push('export type NotificationMethod = keyof NotificationParamsMap')
  lines.push('')
  
  // 生成错误码
  lines.push('// ============== 错误码 ==============')
  lines.push('')
  
  lines.push('export const ERROR_CODES = {')
  for (const [code, message] of Object.entries(schema.errorCodes)) {
    lines.push(`  '${code}': '${message}',`)
  }
  lines.push('} as const')
  lines.push('')
  
  lines.push('export type ErrorCode = keyof typeof ERROR_CODES')
  lines.push('')
  
  // JSON-RPC 基础类型
  lines.push('// ============== JSON-RPC 类型 ==============')
  lines.push('')
  
  lines.push('export interface JsonRpcRequest<M extends RpcMethod = RpcMethod> {')
  lines.push('  jsonrpc: "2.0"')
  lines.push('  id: string')
  lines.push('  method: M')
  lines.push('  params: RpcParamsMap[M]')
  lines.push('}')
  lines.push('')
  
  lines.push('export interface JsonRpcResponse<R = unknown> {')
  lines.push('  jsonrpc: "2.0"')
  lines.push('  id: string')
  lines.push('  result?: R')
  lines.push('  error?: { code: number; message: string; data?: unknown }')
  lines.push('}')
  lines.push('')
  
  lines.push('export interface JsonRpcNotification<N extends NotificationMethod = NotificationMethod> {')
  lines.push('  jsonrpc: "2.0"')
  lines.push('  method: N')
  lines.push('  params: NotificationParamsMap[N]')
  lines.push('}')
  lines.push('')
  
  // 协议版本
  lines.push('// ============== 协议元数据 ==============')
  lines.push('')
  lines.push(`export const PROTOCOL_VERSION = '${schema.version}'`)
  
  return lines.join('\n')
}

const output = generateTypes()
fs.writeFileSync(outputPath, output, 'utf-8')
console.log(`✓ 已生成 ${outputPath}`)
