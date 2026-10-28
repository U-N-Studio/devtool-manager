import { create } from 'zustand'

export type TabId = 'commands' | 'env' | 'packages'
export type ThemeMode = 'light' | 'dark'

interface AppState {
  activeTab: TabId
  setActiveTab: (tab: TabId) => void
  globalLoading: boolean
  setGlobalLoading: (loading: boolean) => void
  terminalCollapsed: boolean
  terminalHeight: number
  terminalVisible: boolean
  toggleTerminal: () => void
  setTerminalVisible: (visible: boolean) => void
  setTerminalHeight: (h: number) => void
  theme: ThemeMode
  toggleTheme: () => void
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'commands',
  setActiveTab: (tab) => set({ activeTab: tab }),
  globalLoading: false,
  setGlobalLoading: (loading) => set({ globalLoading: loading }),
  terminalCollapsed: false,
  terminalHeight: 220,
  terminalVisible: true,
  toggleTerminal: () =>
    set((s) => ({
      terminalCollapsed: !s.terminalCollapsed,
      terminalVisible: s.terminalCollapsed ? true : s.terminalVisible,
    })),
  setTerminalVisible: (visible) =>
    set({ terminalVisible: visible, terminalCollapsed: !visible }),
  setTerminalHeight: (h) => set({ terminalHeight: h }),
  theme: 'dark',
  toggleTheme: () =>
    set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
}))
