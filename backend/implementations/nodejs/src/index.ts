/**
 * DevTool Manager Node.js 后端入口
 * 通过 stdio 与 Electron 主进程通信，使用 newline-delimited JSON-RPC 2.0 协议
 */

import { RpcServer } from './rpc-server';
import { registerHandlers } from './rpc-handlers';

async function main() {
  const server = new RpcServer();
  registerHandlers(server);
  
  // 发送 ready 通知
  server.sendNotification('ready', {});
  
  // 启动处理循环
  await server.start();
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
