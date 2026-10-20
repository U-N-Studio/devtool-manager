/// <reference types="vite/client" />

interface Window {
  api: {
    rpc: (method: string, params?: object) => Promise<any>
    onNotification: (method: string, handler: (params: any) => void) => () => void
    onWindowState: (handler: (state: 'maximized' | 'normal') => void) => () => void
    windowMinimize: () => void
    windowMaximizeToggle: () => void
    windowClose: () => void
  }
}
