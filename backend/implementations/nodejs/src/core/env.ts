/**
 * 环境变量管理
 */

import { RpcServer } from '../rpc-server';
import { exec } from 'child_process';
import { promisify } from 'util';
import winreg from 'winreg';

const execAsync = promisify(exec);

// Windows 注册表路径
const HKLM_ENV = '\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment';
const HKCU_ENV = '\\Environment';

// 环境变量分类
const ENV_CATEGORIES: Record<string, string[]> = {
  Java: ['JAVA_HOME', 'JRE_HOME', 'JDK_HOME', 'CLASSPATH', 'JAVA_OPTS'],
  Python: ['PYTHONHOME', 'PYTHONPATH', 'PYTHONSTARTUP', 'VIRTUAL_ENV', 'CONDA_PREFIX'],
  Android: ['ANDROID_HOME', 'ANDROID_SDK_ROOT', 'ANDROID_NDK_HOME'],
  'Node.js': ['NODE_HOME', 'NODE_PATH', 'NPM_CONFIG_PREFIX', 'NPM_HOME', 'YARN_HOME', 'PNPM_HOME'],
  Go: ['GOROOT', 'GOPATH', 'GOBIN'],
  Rust: ['RUSTUP_HOME', 'CARGO_HOME'],
  'C/C++': ['MINGW_HOME', 'MSYS2_HOME', 'CYGWIN_HOME'],
  Dotnet: ['DOTNET_HOME', 'DOTNET_ROOT'],
  Docker: ['DOCKER_HOME', 'DOCKER_CONFIG', 'DOCKER_HOST'],
  Git: ['GIT_HOME', 'GIT_INSTALL_ROOT'],
  IDE: ['IDEA_HOME', 'VSCODE_HOME', 'PYCHARM_HOME'],
  Proxy: ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY'],
  Path: ['PATH', 'PATHEXT'],
  System: ['COMPUTERNAME', 'USERNAME', 'USERPROFILE', 'SYSTEMROOT', 'TEMP', 'TMP'],
};

const PATH_KEYWORDS: Record<string, string[]> = {
  Java: ['java', 'jdk', 'jre', 'gradle', 'maven'],
  Python: ['python', 'pip', 'conda', 'venv'],
  Android: ['android', 'sdk', 'ndk', 'adb'],
  'Node.js': ['node', 'npm', 'yarn', 'pnpm'],
  Go: ['go', 'golang'],
  Rust: ['rust', 'cargo'],
};

interface EnvItem {
  name: string;
  value: string;
  source: 'system' | 'user';
  is_path_entry?: boolean;
}

/**
 * 读取注册表环境变量
 */
async function readRegistryVars(hive: string, keyPath: string): Promise<Record<string, string>> {
  const result: Record<string, string> = {};
  const regKey = new winreg({ hive, key: keyPath });

  return new Promise((resolve) => {
    regKey.values((err, items) => {
      if (err) {
        resolve(result);
        return;
      }
      for (const item of items) {
        if (item.name) {
          result[item.name.toUpperCase()] = item.value;
        }
      }
      resolve(result);
    });
  });
}

/**
 * 获取系统和用户环境变量
 */
async function getSystemAndUserEnvVars(): Promise<{ system: Record<string, string>; user: Record<string, string> }> {
  const [system, user] = await Promise.all([
    readRegistryVars(winreg.HKLM, HKLM_ENV),
    readRegistryVars(winreg.HKCU, HKCU_ENV),
  ]);
  return { system, user };
}

/**
 * 分类环境变量
 */
function classifyEnvVar(name: string, systemVars: Record<string, string>, userVars: Record<string, string>): 'system' | 'user' {
  const upper = name.toUpperCase();
  if (upper in systemVars) return 'system';
  if (upper in userVars) return 'user';
  return 'system';
}

/**
 * 对 PATH 条目按语言分类
 */
function classifyPathEntry(pathValue: string): string | null {
  const lower = pathValue.toLowerCase();
  for (const [category, keywords] of Object.entries(PATH_KEYWORDS)) {
    if (keywords.some(kw => lower.includes(kw))) {
      return category;
    }
  }
  return null;
}

export function envHandlers(server: RpcServer): void {
  // env.list - 获取分类的环境变量
  server.registerMethod('env.list', async () => {
    const allVars = process.env;
    const { system, user } = await getSystemAndUserEnvVars();
    
    const result: Record<string, EnvItem[]> = {};
    
    // 按分类处理
    for (const [category, varNames] of Object.entries(ENV_CATEGORIES)) {
      if (category === 'Path') continue;
      
      const items: EnvItem[] = [];
      for (const varName of varNames) {
        const upper = varName.toUpperCase();
        if (upper in allVars) {
          const source = classifyEnvVar(upper, system, user);
          items.push({ name: varName, value: allVars[upper]!, source });
        }
      }
      
      // 添加该分类的 PATH 条目
      const pathValue = allVars.PATH || '';
      const pathEntries = pathValue.split(';').filter(e => e.trim());
      for (const entry of pathEntries) {
        const entryCategory = classifyPathEntry(entry);
        if (entryCategory === category) {
          const source = classifyEnvVar('PATH', system, user);
          items.push({ name: 'PATH', value: entry, source, is_path_entry: true });
        }
      }
      
      if (items.length > 0) {
        result[category] = items;
      }
    }
    
    // 处理 PATH 分类
    const pathItems: EnvItem[] = [];
    const pathValue = allVars.PATH || '';
    const pathEntries = pathValue.split(';').filter(e => e.trim());
    const pathSource = classifyEnvVar('PATH', system, user);
    for (const entry of pathEntries) {
      pathItems.push({ name: 'PATH', value: entry, source: pathSource, is_path_entry: true });
    }
    if (allVars.PATHEXT) {
      pathItems.push({ name: 'PATHEXT', value: allVars.PATHEXT, source: classifyEnvVar('PATHEXT', system, user) });
    }
    if (pathItems.length > 0) {
      result['Path'] = pathItems;
    }
    
    // 处理未分类的变量
    const categorizedNames = new Set<string>();
    for (const varNames of Object.values(ENV_CATEGORIES)) {
      for (const v of varNames) {
        categorizedNames.add(v.toUpperCase());
      }
    }
    
    const otherSystem: EnvItem[] = [];
    const otherUser: EnvItem[] = [];
    for (const [name, value] of Object.entries(allVars)) {
      if (categorizedNames.has(name.toUpperCase())) continue;
      const source = classifyEnvVar(name, system, user);
      const entry = { name, value: value || '', source };
      if (source === 'user') {
        otherUser.push(entry);
      } else {
        otherSystem.push(entry);
      }
    }
    
    if (otherSystem.length > 0) result['Other (System)'] = otherSystem;
    if (otherUser.length > 0) result['Other (User)'] = otherUser;
    
    return { items: result };
  });

  // env.python_info - 获取 Python 信息
  server.registerMethod('env.python_info', async () => {
    try {
      const { stdout } = await execAsync('python --version');
      const version = stdout.trim();
      const { stdout: pipOut } = await execAsync('python -m pip --version');
      return {
        version,
        pip: pipOut.trim(),
        platform: process.platform,
        executable: process.execPath,
      };
    } catch {
      return {
        version: 'N/A',
        pip: 'N/A',
        platform: process.platform,
        executable: process.execPath,
      };
    }
  });

  // env.set_var - 设置环境变量
  server.registerMethod('env.set_var', async (params) => {
    const { name, value, source = 'user' } = params;
    const hive = source === 'system' ? winreg.HKLM : winreg.HKCU;
    const keyPath = source === 'system' ? HKLM_ENV : HKCU_ENV;
    
    const regKey = new winreg({ hive, key: keyPath });
    await new Promise<void>((resolve, reject) => {
      regKey.set(name, winreg.REG_EXPAND_SZ, value, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
    
    process.env[name] = value;
    return { ok: true };
  });

  // env.delete_var - 删除环境变量
  server.registerMethod('env.delete_var', async (params) => {
    const { name, source = 'user' } = params;
    const hive = source === 'system' ? winreg.HKLM : winreg.HKCU;
    const keyPath = source === 'system' ? HKLM_ENV : HKCU_ENV;
    
    const regKey = new winreg({ hive, key: keyPath });
    await new Promise<void>((resolve, reject) => {
      regKey.remove(name, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
    
    delete process.env[name];
    return { ok: true };
  });

  // env.add_path_entry - 添加 PATH 条目
  server.registerMethod('env.add_path_entry', async (params) => {
    const { value, source = 'user' } = params;
    const hive = source === 'system' ? winreg.HKLM : winreg.HKCU;
    const keyPath = source === 'system' ? HKLM_ENV : HKCU_ENV;
    
    const regKey = new winreg({ hive, key: keyPath });
    const currentValue = await new Promise<string>((resolve) => {
      regKey.get('PATH', (err, result) => {
        resolve(err ? '' : result.value);
      });
    });
    
    const entries = currentValue.split(';').filter(e => e.trim());
    if (!entries.includes(value)) {
      entries.push(value);
      const newValue = entries.join(';');
      await new Promise<void>((resolve, reject) => {
        regKey.set('PATH', winreg.REG_EXPAND_SZ, newValue, (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }
    
    return { ok: true };
  });

  // env.delete_path_entry - 删除 PATH 条目
  server.registerMethod('env.delete_path_entry', async (params) => {
    const { value, source = 'user' } = params;
    const hive = source === 'system' ? winreg.HKLM : winreg.HKCU;
    const keyPath = source === 'system' ? HKLM_ENV : HKCU_ENV;
    
    const regKey = new winreg({ hive, key: keyPath });
    const currentValue = await new Promise<string>((resolve) => {
      regKey.get('PATH', (err, result) => {
        resolve(err ? '' : result.value);
      });
    });
    
    const entries = currentValue.split(';').filter(e => e.trim() && e !== value);
    const newValue = entries.join(';');
    
    await new Promise<void>((resolve, reject) => {
      regKey.set('PATH', winreg.REG_EXPAND_SZ, newValue, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
    
    return { ok: true };
  });

  // env.get_raw_path - 获取原始 PATH 值
  server.registerMethod('env.get_raw_path', async (params) => {
    const { source = 'user' } = params;
    const hive = source === 'system' ? winreg.HKLM : winreg.HKCU;
    const keyPath = source === 'system' ? HKLM_ENV : HKCU_ENV;
    
    const regKey = new winreg({ hive, key: keyPath });
    const value = await new Promise<string>((resolve) => {
      regKey.get('PATH', (err, result) => {
        resolve(err ? '' : result.value);
      });
    });
    
    return { value };
  });
}
