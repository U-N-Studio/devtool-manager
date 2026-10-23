import { app, BrowserWindow, ipcMain, Menu, IpcMainEvent } from 'electron'
import { createMainWindow } from './window'
import { buildAppMenu } from './menu'
import { PythonBridge } from './pythonBridge'

let mainWindow: BrowserWindow | null = null
let bridge: PythonBridge | null = null

async function bootstrap(): Promise<void> {
  bridge = new PythonBridge()
  await bridge.start()

  ipcMain.on('rpc:request', async (event: IpcMainEvent, request: { id: string; method: string; params?: object }) => {
    try {
      if (!bridge) throw new Error('Python bridge not initialized')
      const result = await bridge.rpc(request.method, request.params)
      event.sender.send('rpc:response', { id: request.id, result })
    } catch (e: any) {
      event.sender.send('rpc:response', { id: request.id, error: { code: -32603, message: e?.message ?? String(e) } })
    }
  })

  const notificationMethods = ['ready', 'executor.output', 'executor.done', 'env.changed']
  for (const method of notificationMethods) {
    bridge.onNotification(method, (params) => {
      mainWindow?.webContents.send('rpc:notification', { method, params })
    })
  }

  ipcMain.on('window:minimize', () => mainWindow?.minimize())
  ipcMain.on('window:maximizeToggle', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize()
    } else {
      mainWindow?.maximize()
    }
  })
  ipcMain.on('window:close', () => mainWindow?.close())

  Menu.setApplicationMenu(buildAppMenu())
  mainWindow = createMainWindow()
}

app.whenReady().then(() => {
  bootstrap().catch((e) => {
    console.error('Failed to bootstrap application:', e)
    app.quit()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', async (e) => {
  if (bridge) {
    e.preventDefault()
    await bridge.shutdown()
    app.exit(0)
  }
})
