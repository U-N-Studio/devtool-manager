/**
 * 工具链信息采集
 */

import { RpcServer } from '../rpc-server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface ToolInfoDetail {
  label: string;
  value: string;
}

interface ToolInfo {
  installed: boolean;
  version?: string | null;
  home?: string | null;
  compiler?: string | null;
  sdk?: string | null;
  ndk?: string | null;
  details: ToolInfoDetail[];
}

async function runVersionCmd(cmd: string): Promise<string | null> {
  try {
    const { stdout, stderr } = await execAsync(cmd, { timeout: 5000 });
    return (stdout || stderr || '').trim();
  } catch {
    return null;
  }
}

async function getJavaInfo(): Promise<ToolInfo> {
  const info: ToolInfo = { installed: false, version: null, home: null, compiler: null, details: [] };
  
  const javaHome = process.env.JAVA_HOME;
  if (javaHome) info.home = javaHome;
  
  const output = await runVersionCmd('java -version');
  if (output) {
    info.installed = true;
    const lines = output.split('\n');
    info.version = lines[0] || output;
    info.details.push({ label: 'java', value: lines[0] || output });
  }
  
  const javacOutput = await runVersionCmd('javac -version');
  if (javacOutput) {
    info.compiler = javacOutput;
    info.details.push({ label: 'javac', value: javacOutput });
  }
  
  return info;
}

async function getPythonInfo(): Promise<ToolInfo> {
  const info: ToolInfo = { installed: false, version: null, home: null, details: [] };
  
  const output = await runVersionCmd('python --version');
  if (output) {
    info.installed = true;
    info.version = output;
    info.details.push({ label: 'python', value: output });
  }
  
  const pipOutput = await runVersionCmd('python -m pip --version');
  if (pipOutput) {
    info.details.push({ label: 'pip', value: pipOutput });
  }
  
  return info;
}

async function getAndroidInfo(): Promise<ToolInfo> {
  const info: ToolInfo = { installed: false, sdk: null, ndk: null, details: [] };
  
  const sdk = process.env.ANDROID_HOME || process.env.ANDROID_SDK_ROOT;
  if (sdk) {
    info.sdk = sdk;
    info.installed = true;
    info.details.push({ label: 'SDK', value: sdk });
  }
  
  const ndk = process.env.ANDROID_NDK_HOME;
  if (ndk) {
    info.ndk = ndk;
    info.details.push({ label: 'NDK', value: ndk });
  }
  
  const adbOutput = await runVersionCmd('adb version');
  if (adbOutput) {
    info.installed = true;
    info.details.push({ label: 'adb', value: adbOutput.split('\n')[0] });
  }
  
  return info;
}

async function getNodeInfo(): Promise<ToolInfo> {
  const info: ToolInfo = { installed: false, version: null, home: null, details: [] };
  
  const nodeOutput = await runVersionCmd('node --version');
  if (nodeOutput) {
    info.installed = true;
    info.version = nodeOutput;
    info.details.push({ label: 'node', value: nodeOutput });
  }
  
  const npmOutput = await runVersionCmd('npm --version');
  if (npmOutput) {
    info.details.push({ label: 'npm', value: npmOutput });
  }
  
  const yarnOutput = await runVersionCmd('yarn --version');
  if (yarnOutput) {
    info.details.push({ label: 'yarn', value: yarnOutput });
  }
  
  const pnpmOutput = await runVersionCmd('pnpm --version');
  if (pnpmOutput) {
    info.details.push({ label: 'pnpm', value: pnpmOutput });
  }
  
  return info;
}

async function getGoInfo(): Promise<ToolInfo> {
  const info: ToolInfo = { installed: false, version: null, home: null, details: [] };
  
  const output = await runVersionCmd('go version');
  if (output) {
    info.installed = true;
    info.version = output;
    info.details.push({ label: 'go', value: output });
  }
  
  const goroot = process.env.GOROOT;
  if (goroot) {
    info.home = goroot;
    info.details.push({ label: 'GOROOT', value: goroot });
  }
  
  const gopath = process.env.GOPATH;
  if (gopath) {
    info.details.push({ label: 'GOPATH', value: gopath });
  }
  
  return info;
}

async function getRustInfo(): Promise<ToolInfo> {
  const info: ToolInfo = { installed: false, version: null, home: null, details: [] };
  
  const rustcOutput = await runVersionCmd('rustc --version');
  if (rustcOutput) {
    info.installed = true;
    info.version = rustcOutput;
    info.details.push({ label: 'rustc', value: rustcOutput });
  }
  
  const cargoOutput = await runVersionCmd('cargo --version');
  if (cargoOutput) {
    info.details.push({ label: 'cargo', value: cargoOutput });
  }
  
  const rustupOutput = await runVersionCmd('rustup --version');
  if (rustupOutput) {
    info.details.push({ label: 'rustup', value: rustupOutput.split('\n')[0] });
  }
  
  return info;
}

const TOOL_INFO_FUNCS: Record<string, () => Promise<ToolInfo>> = {
  Java: getJavaInfo,
  Python: getPythonInfo,
  Android: getAndroidInfo,
  'Node.js': getNodeInfo,
  Go: getGoInfo,
  Rust: getRustInfo,
};

export function toolsHandlers(server: RpcServer): void {
  server.registerMethod('tools.info', async (params) => {
    const category = params.category || '';
    const func = TOOL_INFO_FUNCS[category];
    if (func) {
      return func();
    }
    return { installed: false, details: [] };
  });
}
