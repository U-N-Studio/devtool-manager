/**
 * 收藏夹管理
 */

import { RpcServer } from '../rpc-server';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as winreg from 'winreg';
import { exec as childExec } from 'child_process';

const execAsync = promisify(exec);

export function favoritesHandlers(server: RpcServer): void {
  // favorites.list - 列出所有收藏的命令
  server.registerMethod('favorites.list', async () => {
    try {
      const { stdout } = await execAsync('node -e "const fs=require(\'fs\');const p=require(\'path\').join(process.env.USERPROFILE,\'.devtool-manager\',\'favorites.json\');console.log(fs.existsSync(p)?fs.readFileSync(p,\'utf8\'):\'[]\')"');
      const favorites = JSON.parse(stdout.trim());
      return { items: favorites };
    } catch (e) {
      return { items: [] };
    }
  });

  // favorites.add - 添加命令到收藏
  server.registerMethod('favorites.add', async (params) => {
    const { command, label } = params;
    try {
      await execAsync(`node -e "const fs=require('fs');const p=require('path').join(process.env.USERPROFILE,'.devtool-manager','favorites.json');let f=fs.existsSync(p)?JSON.parse(fs.readFileSync(p,'utf8')):[];f.push({command:'${command.replace(/'/g, "\\'")}',label:'${label || command}'});fs.writeFileSync(p,JSON.stringify(f,null,2))"`);
      return { ok: true };
    } catch (e) {
      return { ok: false, error: String(e) };
    }
  });

  // favorites.remove - 从收藏中移除命令
  server.registerMethod('favorites.remove', async (params) => {
    const { command } = params;
    try {
      await execAsync(`node -e "const fs=require('fs');const p=require('path').join(process.env.USERPROFILE,'.devtool-manager','favorites.json');let f=fs.existsSync(p)?JSON.parse(fs.readFileSync(p,'utf8')):[];f=f.filter(x=>x.command!=='${command.replace(/'/g, "\\'")}');fs.writeFileSync(p,JSON.stringify(f,null,2))"`);
      return { ok: true };
    } catch (e) {
      return { ok: false, error: String(e) };
    }
  });
}
