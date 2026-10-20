import { spawn, ChildProcess } from 'child_process'
import { app } from 'electron'
import path from 'path'
import { randomUUID } from 'crypto'
import { EventEmitter } from 'events'

interface PendingRequest {
  resolve: (value: unknown) => void
  reject: (error: Error) => void
  timer: NodeJS.Timeout
}

export class PythonBridge extends EventEmitter {
  private proc: ChildProcess | null = null
  private pending = new Map<string, PendingRequest>()
  private notificationHandlers = new Map<string, Set<(params: any) => void>>()
  private buffer = ''

  async start(): Promise<void> {
    const isDev = !app.isPackaged && process.env.NODE_ENV === 'development'
    const args = isDev ? [path.resolve(__dirname, '../../backend/server.py')] : []
    const command = app.isPackaged
      ? path.join(process.resourcesPath, 'backend', 'devtool-backend.exe')
      : 'python'

    this.proc = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    })

    this.proc.stdout?.setEncoding('utf8')
    this.proc.stdout?.on('data', (data: string) => this.onStdout(data))
    this.proc.stderr?.on('data', (data: Buffer) => {
      console.error('[backend stderr]', data.toString())
    })
    this.proc.on('exit', (code) => {
      console.log(`[backend] exited with code ${code}`)
      this.proc = null
    })

    await this.waitForReady()
  }

  private waitForReady(): Promise<void> {
    return new Promise((resolve) => {
      const handler = () => {
        this.off('ready', handler)
        resolve()
      }
      this.once('ready', handler)
      setTimeout(() => {
        this.off('ready', handler)
        resolve()
      }, 5000)
    })
  }

  private onStdout(data: string): void {
    this.buffer += data
    const lines = this.buffer.split('\n')
    this.buffer = lines.pop() || ''
    for (const line of lines) {
      if (!line.trim()) continue
      try {
        this.handleMessage(JSON.parse(line))
      } catch (e) {
        console.error('[pythonBridge] failed to parse line:', line, e)
      }
    }
  }

  private handleMessage(msg: any): void {
    if (msg.method && !msg.id) {
      if (msg.method === 'ready') {
        this.emit('ready')
      }
      this.notificationHandlers.get(msg.method)?.forEach((h) => h(msg.params || {}))
    } else if (msg.id) {
      const pending = this.pending.get(msg.id)
      if (!pending) return
      this.pending.delete(msg.id)
      clearTimeout(pending.timer)
      if (msg.error) {
        pending.reject(new Error(msg.error.message))
      } else {
        pending.resolve(msg.result)
      }
    }
  }

  rpc(method: string, params?: object): Promise<unknown> {
    return new Promise((resolve, reject) => {
      if (!this.proc || !this.proc.stdin) {
        reject(new Error('Python backend not started'))
        return
      }
      const id = randomUUID()
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error(`RPC timeout: ${method}`))
      }, 60000)
      this.pending.set(id, { resolve, reject, timer })
      this.proc.stdin.write(
        JSON.stringify({ jsonrpc: '2.0', id, method, params: params || {} }) + '\n',
      )
    })
  }

  onNotification(method: string, handler: (params: any) => void): () => void {
    if (!this.notificationHandlers.has(method)) {
      this.notificationHandlers.set(method, new Set())
    }
    this.notificationHandlers.get(method)!.add(handler)
    return () => {
      this.notificationHandlers.get(method)?.delete(handler)
    }
  }

  async shutdown(): Promise<void> {
    if (!this.proc) return
    try {
      await Promise.race([
        this.rpc('shutdown'),
        new Promise((_, reject) => setTimeout(() => reject(new Error('shutdown timeout')), 2000)),
      ])
    } catch {
      // timeout: force kill
    }
    if (this.proc) {
      this.proc.kill()
      this.proc = null
    }
  }
}
