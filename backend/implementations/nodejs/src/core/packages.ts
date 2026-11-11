/**
 * 包管理
 */

import { RpcServer } from '../rpc-server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface PackageInfo {
  name: string;
  version: string;
  installed: boolean;
  func_tag: string;
  lang_tag: string;
}

// 包分类标签
const FUNC_TAGS = [
  'UI Framework', 'Web Framework', 'Data Science', 'Dev Tools',
  'Network', 'Database', 'CLI', 'File & IO', 'Automation', 'Crypto',
];

const LANG_TAGS = ['Python', 'Node.js', 'Java', 'Rust', 'Go', 'C/C++', 'Dotnet'];

// 已知包列表（简化版）
const KNOWN_PACKAGES: Record<string, { func: string; lang: string }> = {
  'express': { func: 'Web Framework', lang: 'Node.js' },
  'react': { func: 'UI Framework', lang: 'Node.js' },
  'vue': { func: 'UI Framework', lang: 'Node.js' },
  'typescript': { func: 'Dev Tools', lang: 'Node.js' },
  'webpack': { func: 'Dev Tools', lang: 'Node.js' },
  'vite': { func: 'Dev Tools', lang: 'Node.js' },
  'lodash': { func: 'File & IO', lang: 'Node.js' },
  'axios': { func: 'Network', lang: 'Node.js' },
  'flask': { func: 'Web Framework', lang: 'Python' },
  'django': { func: 'Web Framework', lang: 'Python' },
  'fastapi': { func: 'Web Framework', lang: 'Python' },
  'numpy': { func: 'Data Science', lang: 'Python' },
  'pandas': { func: 'Data Science', lang: 'Python' },
  'requests': { func: 'Network', lang: 'Python' },
  'pytest': { func: 'Dev Tools', lang: 'Python' },
};

async function getInstalledNpmPackages(): Promise<Map<string, string>> {
  const installed = new Map<string, string>();
  try {
    const { stdout } = await execAsync('npm list -g --depth=0 --json', { timeout: 10000 });
    const data = JSON.parse(stdout);
    if (data.dependencies) {
      for (const [name, info] of Object.entries(data.dependencies)) {
        installed.set(name, (info as any).version || '');
      }
    }
  } catch (err) {
    console.error('Failed to get npm packages:', err);
  }
  return installed;
}

async function getInstalledPipPackages(): Promise<Map<string, string>> {
  const installed = new Map<string, string>();
  try {
    const { stdout } = await execAsync('pip list --format=json', { timeout: 10000 });
    const packages = JSON.parse(stdout);
    for (const pkg of packages) {
      installed.set(pkg.name.toLowerCase(), pkg.version);
    }
  } catch (err) {
    console.error('Failed to get pip packages:', err);
  }
  return installed;
}

export function packagesHandlers(server: RpcServer): void {
  server.registerMethod('packages.list', async (params) => {
    const { func = '', lang = '', install = '' } = params || {};
    
    // 获取已安装的包
    const [npmPackages, pipPackages] = await Promise.all([
      lang === '' || lang === 'Node.js' ? getInstalledNpmPackages() : Promise.resolve(new Map()),
      lang === '' || lang === 'Python' ? getInstalledPipPackages() : Promise.resolve(new Map()),
    ]);
    
    const items: PackageInfo[] = [];
    const processedNames = new Set<string>();
    
    // 处理已知包
    for (const [name, info] of Object.entries(KNOWN_PACKAGES)) {
      if (func && info.func !== func) continue;
      if (lang && info.lang !== lang) continue;
      
      const lowerName = name.toLowerCase();
      const npmVersion = npmPackages.get(lowerName);
      const pipVersion = pipPackages.get(lowerName);
      const version = npmVersion || pipVersion || '';
      const isInstalled = !!(npmVersion || pipVersion);
      
      if (install === 'Installed' && !isInstalled) continue;
      if (install === 'Not Installed' && isInstalled) continue;
      
      items.push({
        name,
        version,
        installed: isInstalled,
        func_tag: info.func,
        lang_tag: info.lang,
      });
      processedNames.add(lowerName);
    }
    
    // 添加已安装但未在已知列表中的包
    for (const [name, version] of npmPackages.entries()) {
      if (processedNames.has(name)) continue;
      if (func || lang) continue; // 有过滤条件时不添加未知包
      
      items.push({
        name,
        version,
        installed: true,
        func_tag: 'Other',
        lang_tag: 'Node.js',
      });
    }
    
    for (const [name, version] of pipPackages.entries()) {
      if (processedNames.has(name)) continue;
      if (func || lang) continue;
      
      items.push({
        name,
        version,
        installed: true,
        func_tag: 'Other',
        lang_tag: 'Python',
      });
    }
    
    // 排序
    items.sort((a, b) => a.name.localeCompare(b.name));
    
    return { items };
  });
  
  server.registerMethod('packages.install', async (params) => {
    const { name } = params;
    try {
      // 尝试 npm 安装
      const { stdout, stderr } = await execAsync(`npm install -g ${name}`, { timeout: 60000 });
      return { ok: true, output: stdout + stderr };
    } catch (err: any) {
      return { ok: false, output: err.message };
    }
  });
  
  server.registerMethod('packages.uninstall', async (params) => {
    const { name } = params;
    try {
      const { stdout, stderr } = await execAsync(`npm uninstall -g ${name}`, { timeout: 60000 });
      return { ok: true, output: stdout + stderr };
    } catch (err: any) {
      return { ok: false, output: err.message };
    }
  });
}
