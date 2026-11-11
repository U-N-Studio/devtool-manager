import { app, BrowserWindow, ipcMain, Menu, IpcMainEvent, dialog } from 'electron'
import { createMainWindow } from './window'
import { buildAppMenu } from './menu'
import { PythonBridge } from './pythonBridge'
import { NodeBridge } from './nodeBridge'

let mainWindow: BrowserWindow | null = null
let bridge: PythonBridge | NodeBridge | null = null
let bridgeType: 'python' | 'nodejs' = 'python'

async function bootstrap(): Promise<void> {
  // 通过环境变量选择后端类型
  bridgeType = (process.env.BACKEND_TYPE as 'python' | 'nodejs') || 'python'
  console.log(`[main] Starting with ${bridgeType} backend`)

  if (bridgeType === 'nodejs') {
    bridge = new NodeBridge()
  } else {
    bridge = new PythonBridge()
  }
  
  await bridge.start()

  ipcMain.on('rpc:request', async (event: IpcMainEvent, request: { id: string; method: string; params?: object }) => {
    try {
      if (!bridge) throw new Error('Backend not initialized')
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

  ipcMain.handle('dialog:selectDirectory', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory'],
      title: '选择工作目录',
    })
    if (result.canceled || result.filePaths.length === 0) return null
    return result.filePaths[0]
  })

  Menu.setApplicationMenu(buildAppMenu())
  mainWindow = createMainWindow()
  
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('[main] window loaded')
    mainWindow?.show()
    mainWindow?.focus()
  })
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
