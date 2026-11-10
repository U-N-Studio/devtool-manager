import { BrowserWindow } from 'electron'
import path from 'path'

export function createMainWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 960,
    minHeight: 640,
    frame: false,
    titleBarStyle: 'hidden',
    show: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  win.on('maximize', () => win.webContents.send('window:state', 'maximized'))
  win.on('unmaximize', () => win.webContents.send('window:state', 'normal'))

  if (process.env.NODE_ENV === 'development' || process.env.VITE_DEV_SERVER_URL) {
    win.loadURL('http://localhost:5173')
  } else {
    // 生产环境：resourcesPath 在 asar 外部
    const resourcesPath = process.resourcesPath.replace('app.asar', 'app.asar.unpacked')
    win.loadFile(path.join(resourcesPath, 'frontend', 'index.html'))
  }

  win.webContents.on('console-message', (_e, level, message, line, sourceId) => {
    console.log(`[renderer:${level}] ${message} (${sourceId}:${line})`)
  })
  win.webContents.on('did-fail-load', (_e, code, desc, url) => {
    console.error(`[did-fail-load] ${code} ${desc} url=${url}`)
  })
  win.webContents.on('render-process-gone', (_e, details) => {
    console.error(`[render-process-gone] ${details.reason}`, details)
  })

  return win
}
