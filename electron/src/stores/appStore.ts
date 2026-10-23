import { create } from 'zustand'

export type TabId = 'commands' | 'env' | 'packages'

interface AppState {
  activeTab: TabId
  setActiveTab: (tab: TabId) => void
  globalLoading: boolean
  setGlobalLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'commands',
  setActiveTab: (tab) => set({ activeTab: tab }),
  globalLoading: false,
  setGlobalLoading: (loading) => set({ globalLoading: loading }),
}))
