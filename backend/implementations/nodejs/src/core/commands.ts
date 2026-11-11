/**
 * 命令管理
 */

import { RpcServer } from '../rpc-server';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

const COMMAND_DEFINITIONS_DIR = path.join(__dirname, '..', '..', '..', 'backend', 'data', 'commands');

interface CommandItem {
  name: string;
  installed: boolean;
}

interface CommandDetail {
  name: string;
  installed: boolean;
  version: string;
  path: string;
  description: string;
  subcommands: any[];
  env_vars: any[];
  config_sections: any[];
}

async function isCommandInstalled(name: string): Promise<boolean> {
  try {
    const cmd = process.platform === 'win32' ? `where ${name}` : `which ${name}`;
    await execAsync(cmd);
    return true;
  } catch {
    return false;
  }
}

async function getCommandVersion(name: string): Promise<string> {
  try {
    const { stdout } = await execAsync(`${name} --version`, { timeout: 5000 });
    return stdout.trim();
  } catch {
    return '';
  }
}

async function getCommandPath(name: string): Promise<string> {
  try {
    const cmd = process.platform === 'win32' ? `where ${name}` : `which ${name}`;
    const { stdout } = await execAsync(cmd);
    return stdout.trim().split('\n')[0];
  } catch {
    return '';
  }
}

function loadCommandDefinition(name: string): any {
  try {
    const filePath = path.join(COMMAND_DEFINITIONS_DIR, `${name}.json`);
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error(`Failed to load command definition for ${name}:`, err);
  }
  return null;
}

export function commandsHandlers(server: RpcServer): void {
  server.registerMethod('commands.list', async (params) => {
    const { installed_only = false } = params || {};
    
    // 读取命令定义目录
    let commandNames: string[] = [];
    try {
      if (fs.existsSync(COMMAND_DEFINITIONS_DIR)) {
        const files = fs.readdirSync(COMMAND_DEFINITIONS_DIR);
        commandNames = files
          .filter(f => f.endsWith('.json'))
          .map(f => f.replace('.json', ''));
      }
    } catch (err) {
      console.error('Failed to read commands directory:', err);
    }
    
    // 添加一些默认命令
    const defaultCommands = ['git', 'node', 'npm', 'python', 'java', 'go', 'rustc', 'cargo'];
    for (const cmd of defaultCommands) {
      if (!commandNames.includes(cmd)) {
        commandNames.push(cmd);
      }
    }
    
    const items: CommandItem[] = [];
    for (const name of commandNames) {
      const installed = await isCommandInstalled(name);
      if (installed_only && !installed) continue;
      items.push({ name, installed });
    }
    
    return { items };
  });
  
  server.registerMethod('commands.detail', async (params) => {
    const { name } = params;
    const installed = await isCommandInstalled(name);
    const version = installed ? await getCommandVersion(name) : '';
    const cmdPath = installed ? await getCommandPath(name) : '';
    
    // 尝试加载定义文件
    const definition = loadCommandDefinition(name);
    
    const detail: CommandDetail = {
      name,
      installed,
      version: version || (definition?.version ?? ''),
      path: cmdPath || (definition?.path ?? ''),
      description: definition?.description || `${name} command`,
      subcommands: definition?.subcommands || [],
      env_vars: definition?.env_vars || [],
      config_sections: definition?.config_sections || [],
    };
    
    return detail;
  });
  
  server.registerMethod('commands.description', async (params) => {
    const { name } = params;
    const definition = loadCommandDefinition(name);
    return { text: definition?.description || `${name} command` };
  });
  
  server.registerMethod('commands.subcommand_help', async (params) => {
    const { command, subcommand } = params;
    const definition = loadCommandDefinition(command);
    
    if (definition?.subcommands) {
      const sub = definition.subcommands.find((s: any) => s.name === subcommand);
      if (sub) {
        return {
          command,
          subcommand,
          params: sub.params || [],
          pathParams: sub.pathParams || [],
        };
      }
    }
    
    return {
      command,
      subcommand,
      params: [],
      pathParams: [],
    };
  });
}
