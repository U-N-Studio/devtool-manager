/**
 * RPC 方法处理器注册
 */

import { RpcServer } from './rpc-server';
import { envHandlers } from './core/env';
import { toolsHandlers } from './core/tools';
import { commandsHandlers } from './core/commands';
import { executorHandlers } from './core/executor';
import { historyHandlers } from './core/history';
import { packagesHandlers } from './core/packages';
import { favoritesHandlers } from './core/favorites';

export function registerHandlers(server: RpcServer): void {
  // ping
  server.registerMethod('ping', () => ({ pong: true }));

  // 注册各模块处理器
  envHandlers(server);
  toolsHandlers(server);
  commandsHandlers(server);
  executorHandlers(server);
  historyHandlers(server);
  packagesHandlers(server);
  favoritesHandlers(server);

  // shutdown
  server.registerMethod('shutdown', async () => {
    server.stop();
    process.exit(0);
  });
}
