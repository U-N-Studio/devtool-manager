import { contextBridge, ipcRenderer } from 'electron'

type PendingEntry = {
  resolve: (value: unknown) => void
  reject: (error: Error) => void
}

const pendingRpc = new Map<string, PendingEntry>()

ipcRenderer.on('rpc:response', (_event, response: { id: string; result?: unknown; error?: { message: string } }) => {
  const pending = pendingRpc.get(response.id)
  if (!pending) return
  pendingRpc.delete(response.id)
  if (response.error) {
    pending.reject(new Error(response.error.message))
  } else {
    pending.resolve(response.result)
  }
})

const notificationHandlerMap = new Map<string, Set<(params: unknown) => void>>()

ipcRenderer.on('rpc:notification', (_event, notification: { method: string; params?: unknown }) => {
  const handlers = notificationHandlerMap.get(notification.method)
  handlers?.forEach((h) => h(notification.params))
})

function newRequestId(): string {
  return globalThis.crypto?.randomUUID?.()
    ?? (Date.now().toString(36) + Math.random().toString(36).slice(2))
}

contextBridge.exposeInMainWorld('api', {
  rpc: (method: string, params?: object): Promise<unknown> => {
    const id = newRequestId()
    return new Promise((resolve, reject) => {
      pendingRpc.set(id, { resolve, reject })
      ipcRenderer.send('rpc:request', { id, method, params })
    })
  },
  onNotification: (method: string, handler: (params: unknown) => void): (() => void) => {
    if (!notificationHandlerMap.has(method)) {
      notificationHandlerMap.set(method, new Set())
    }
    notificationHandlerMap.get(method)!.add(handler)
    return () => {
      notificationHandlerMap.get(method)?.delete(handler)
    }
  },
  onWindowState: (handler: (state: 'maximized' | 'normal') => void): (() => void) => {
    const listener = (_e: unknown, state: 'maximized' | 'normal') => handler(state)
    ipcRenderer.on('window:state', listener)
    return () => ipcRenderer.removeListener('window:state', listener)
  },
  windowMinimize: () => ipcRenderer.send('window:minimize'),
  windowMaximizeToggle: () => ipcRenderer.send('window:maximizeToggle'),
  windowClose: () => ipcRenderer.send('window:close'),
})
