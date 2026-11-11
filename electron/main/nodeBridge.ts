import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import path from 'path';
import fs from 'fs';
import readline from 'readline';

interface RpcRequest {
  jsonrpc: '2.0';
  id?: number | string;
  method: string;
  params?: any;
}

interface RpcResponse {
  jsonrpc: '2.0';
  id?: number | string;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

interface PendingRequest {
  resolve: (value: any) => void;
  reject: (reason: any) => void;
  timeout: NodeJS.Timeout;
}

export class NodeBridge extends EventEmitter {
  private process: ChildProcess | null = null;
  private requestId = 0;
  private pendingRequests = new Map<number | string, PendingRequest>();
  private rl: readline.Interface | null = null;
  private isDev = process.env.NODE_ENV === 'development';

  async start(): Promise<void> {
    const nodeBackendPath = path.join(
      __dirname,
      '..',
      '..',
      'backend',
      'implementations',
      'nodejs'
    );

    let serverPath: string;
    if (this.isDev) {
      // 开发模式：直接运行 TypeScript
      serverPath = path.join(nodeBackendPath, 'src', 'index.ts');
      this.process = spawn('npx', ['ts-node', serverPath], {
        cwd: nodeBackendPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env },
      });
    } else {
      // 生产模式：运行编译后的 JavaScript
      serverPath = path.join(nodeBackendPath, 'dist', 'index.js');
      this.process = spawn('node', [serverPath], {
        cwd: nodeBackendPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env },
      });
    }

    if (!this.process.stdout || !this.process.stderr) {
      throw new Error('Failed to start Node.js backend: no stdout/stderr');
    }

    // 设置 readline 接口
    this.rl = readline.createInterface({
      input: this.process.stdout,
      crlfDelay: Infinity,
    });

    // 处理 RPC 响应
    this.rl.on('line', (line) => {
      if (!line.trim()) return;
      try {
        const response: RpcResponse = JSON.parse(line);
        this.handleResponse(response);
      } catch (err) {
        console.error('Failed to parse Node.js backend response:', line, err);
      }
    });

    // 处理错误输出
    this.process.stderr.on('data', (data) => {
      console.error('Node.js backend error:', data.toString());
    });

    // 处理进程退出
    this.process.on('exit', (code, signal) => {
      console.log(`Node.js backend exited with code ${code}, signal ${signal}`);
      this.process = null;
      this.emit('exit', code, signal);
    });

    // 处理进程错误
    this.process.on('error', (err) => {
      console.error('Node.js backend process error:', err);
      this.emit('error', err);
    });

    // 等待 ready 通知
    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Node.js backend startup timeout'));
      }, 10000);

      this.once('ready', () => {
        clearTimeout(timeout);
        resolve();
      });
    });

    console.log('Node.js backend started successfully');
  }

  private handleResponse(response: RpcResponse): void {
    // 处理通知
    if (!response.id) {
      if (response.method === 'ready') {
        this.emit('ready');
      }
      // 发出特定事件的通知
      this.emit(`notification:${response.method}`, response.params);
      return;
    }

    // 处理请求响应
    const pending = this.pendingRequests.get(response.id);
    if (!pending) {
      console.warn('Received response for unknown request:', response.id);
      return;
    }

    clearTimeout(pending.timeout);
    this.pendingRequests.delete(response.id);

    if (response.error) {
      pending.reject(new Error(response.error.message));
    } else {
      pending.resolve(response.result);
    }
  }

  async rpc<T = any>(method: string, params?: any): Promise<T> {
    if (!this.process || !this.process.stdin) {
      throw new Error('Node.js backend not started');
    }

    const id = ++this.requestId;
    const request: RpcRequest = {
      jsonrpc: '2.0',
      id,
      method,
      params,
    };

    return new Promise<T>((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout: ${method}`));
      }, 30000);

      this.pendingRequests.set(id, { resolve, reject, timeout });

      const requestStr = JSON.stringify(request) + '\n';
      this.process!.stdin!.write(requestStr, (err) => {
        if (err) {
          clearTimeout(timeout);
          this.pendingRequests.delete(id);
          reject(err);
        }
      });
    });
  }

  onNotification(event: string, callback: (params: any) => void): void {
    this.on(`notification:${event}`, callback);
  }

  async stop(): Promise<void> {
    if (this.process) {
      // 清理所有待处理的请求
      for (const [id, pending] of this.pendingRequests.entries()) {
        clearTimeout(pending.timeout);
        pending.reject(new Error('Backend stopping'));
      }
      this.pendingRequests.clear();

      // 关闭进程
      this.process.kill('SIGTERM');
      
      // 等待进程退出
      await new Promise<void>((resolve) => {
        if (!this.process) {
          resolve();
          return;
        }
        this.process.on('exit', () => resolve());
        setTimeout(() => {
          if (this.process) {
            this.process.kill('SIGKILL');
          }
          resolve();
        }, 5000);
      });

      this.process = null;
    }

    if (this.rl) {
      this.rl.close();
      this.rl = null;
    }
  }
}
