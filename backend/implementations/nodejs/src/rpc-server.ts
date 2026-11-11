/**
 * JSON-RPC 2.0 服务器
 * 通过 stdio 进行 newline-delimited JSON 通信
 */

import { EventEmitter } from 'events';
import { createInterface, Interface } from 'readline';

export interface JsonRpcRequest {
  jsonrpc: '2.0';
  id?: string | number;
  method: string;
  params?: Record<string, any>;
}

export interface JsonRpcResponse {
  jsonrpc: '2.0';
  id?: string | number;
  result?: any;
  error?: { code: number; message: string; data?: any };
}

export type RpcHandler = (params: any) => Promise<any> | any;

export class RpcServer extends EventEmitter {
  private handlers = new Map<string, RpcHandler>();
  private rl: Interface | null = null;

  /**
   * 注册 RPC 方法处理器
   */
  registerMethod(method: string, handler: RpcHandler): void {
    this.handlers.set(method, handler);
  }

  /**
   * 发送 JSON-RPC 响应
   */
  sendResponse(id: string | number | undefined, result: any): void {
    const response: JsonRpcResponse = {
      jsonrpc: '2.0',
      id,
      result,
    };
    this.send(response);
  }

  /**
   * 发送 JSON-RPC 错误响应
   */
  sendError(id: string | number | undefined, code: number, message: string): void {
    const response: JsonRpcResponse = {
      jsonrpc: '2.0',
      id,
      error: { code, message },
    };
    this.send(response);
  }

  /**
   * 发送 JSON-RPC 通知
   */
  sendNotification(method: string, params: any): void {
    const notification = {
      jsonrpc: '2.0',
      method,
      params,
    };
    this.send(notification);
  }

  /**
   * 发送消息到 stdout
   */
  private send(msg: any): void {
    const line = JSON.stringify(msg) + '\n';
    process.stdout.write(line);
  }

  /**
   * 启动服务器，开始处理 stdin 输入
   */
  async start(): Promise<void> {
    this.rl = createInterface({
      input: process.stdin,
      terminal: false,
    });

    this.rl.on('line', async (line) => {
      const trimmed = line.trim();
      if (!trimmed) return;

      try {
        const request = JSON.parse(trimmed) as JsonRpcRequest;
        await this.handleRequest(request);
      } catch (err) {
        this.sendError(undefined, -32700, 'Parse error');
      }
    });

    // 保持进程运行
    await new Promise(() => {});
  }

  /**
   * 处理单个 RPC 请求
   */
  private async handleRequest(request: JsonRpcRequest): Promise<void> {
    const { id, method, params = {} } = request;

    const handler = this.handlers.get(method);
    if (!handler) {
      this.sendError(id, -32601, `Method not found: ${method}`);
      return;
    }

    try {
      const result = await handler(params);
      this.sendResponse(id, result);
    } catch (err: any) {
      this.sendError(id, -32603, err.message || 'Internal error');
    }
  }

  /**
   * 停止服务器
   */
  stop(): void {
    if (this.rl) {
      this.rl.close();
      this.rl = null;
    }
  }
}
