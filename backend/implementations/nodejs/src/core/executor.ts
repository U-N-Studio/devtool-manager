/**
 * 命令执行器
 */

import { RpcServer } from '../rpc-server';
import { spawn, ChildProcess } from 'child_process';
import { v4 as uuidv4 } from 'uuid';

interface Executor {
  process: ChildProcess | null;
  running: boolean;
}

const executors = new Map<string, Executor>();

export function executorHandlers(server: RpcServer): void {
  server.registerMethod('executor.execute', async (params) => {
    const { command, cwd, env } = params;
    const sessionId = uuidv4();
    
    const executor: Executor = {
      process: null,
      running: true,
    };
    
    executors.set(sessionId, executor);
    
    // 合并环境变量
    const mergedEnv = { ...process.env, ...env };
    
    // 启动子进程
    const child = spawn('cmd.exe', ['/c', command], {
      cwd: cwd || process.cwd(),
      env: mergedEnv,
      shell: false,
      windowsHide: true,
    });
    
    executor.process = child;
    
    // 处理 stdout
    child.stdout?.on('data', (data) => {
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          server.sendNotification('executor.output', {
            sessionId,
            stream: 'stdout',
            line: line,
          });
        }
      }
    });
    
    // 处理 stderr
    child.stderr?.on('data', (data) => {
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          server.sendNotification('executor.output', {
            sessionId,
            stream: 'stderr',
            line: line,
          });
        }
      }
    });
    
    // 处理进程退出
    child.on('exit', (code) => {
      executor.running = false;
      executors.delete(sessionId);
      server.sendNotification('executor.done', {
        sessionId,
        exitCode: code ?? -1,
      });
    });
    
    child.on('error', (err) => {
      executor.running = false;
      executors.delete(sessionId);
      server.sendNotification('executor.output', {
        sessionId,
        stream: 'stderr',
        line: `Error: ${err.message}`,
      });
      server.sendNotification('executor.done', {
        sessionId,
        exitCode: -1,
      });
    });
    
    return { sessionId };
  });
  
  server.registerMethod('executor.kill', async (params) => {
    const { sessionId } = params;
    const executor = executors.get(sessionId);
    
    if (executor && executor.process) {
      executor.process.kill('SIGTERM');
      executor.running = false;
      executors.delete(sessionId);
      return { ok: true };
    }
    
    return { ok: false };
  });
}
