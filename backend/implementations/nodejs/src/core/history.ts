/**
 * 历史记录管理
 */

import { RpcServer } from '../rpc-server';
import * as fs from 'fs';
import * as path from 'path';

const DATA_DIR = path.join(process.env.USERPROFILE || process.env.HOME || '.', '.devtool-manager');
const HISTORY_FILE = path.join(DATA_DIR, 'history.json');
const MAX_HISTORY = 200;

interface HistoryEntry {
  id: string;
  command: string;
  timestamp: number;
  exitCode: number | null;
}

function ensureDataDir(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function readHistory(): HistoryEntry[] {
  try {
    ensureDataDir();
    if (fs.existsSync(HISTORY_FILE)) {
      const data = fs.readFileSync(HISTORY_FILE, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error('Failed to read history:', err);
  }
  return [];
}

function writeHistory(entries: HistoryEntry[]): void {
  try {
    ensureDataDir();
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(entries, null, 2), 'utf-8');
  } catch (err) {
    console.error('Failed to write history:', err);
  }
}

export function historyHandlers(server: RpcServer): void {
  server.registerMethod('history.list', async () => {
    const items = readHistory();
    return { items };
  });
  
  server.registerMethod('history.add', async (params) => {
    const { command, exitCode = null } = params;
    const entry: HistoryEntry = {
      id: uuidv4(),
      command,
      timestamp: Date.now(),
      exitCode,
    };
    
    const entries = readHistory();
    entries.unshift(entry);
    
    // 限制最大数量
    if (entries.length > MAX_HISTORY) {
      entries.splice(MAX_HISTORY);
    }
    
    writeHistory(entries);
    return { ok: true };
  });
  
  server.registerMethod('history.clear', async () => {
    writeHistory([]);
    return { ok: true };
  });
  
  server.registerMethod('history.delete', async (params) => {
    const { id } = params;
    const entries = readHistory();
    const filtered = entries.filter(e => e.id !== id);
    writeHistory(filtered);
    return { ok: true };
  });
}

function uuidv4(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
