import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { HistoryEntry, FavoriteEntry } from '@/lib/types'

interface HistoryFavoritesState {
  history: HistoryEntry[]
  favorites: FavoriteEntry[]
  isLoading: boolean
  loadHistory: () => Promise<void>
  loadFavorites: () => Promise<void>
  addHistory: (command: string, exitCode?: number) => Promise<void>
  clearHistory: () => Promise<void>
  deleteHistory: (id: string) => Promise<void>
  addFavorite: (command: string, label?: string) => Promise<void>
  removeFavorite: (command: string) => Promise<void>
  isFavorite: (command: string) => boolean
}

export const useHistoryFavoritesStore = create<HistoryFavoritesState>((set, get) => ({
  history: [],
  favorites: [],
  isLoading: false,
  loadHistory: async () => {
    try {
      const r = await rpc('history.list')
      set({ history: r.items })
    } catch {
      /* ignore */
    }
  },
  loadFavorites: async () => {
    try {
      const r = await rpc('favorites.list')
      set({ favorites: r.items })
    } catch {
      /* ignore */
    }
  },
  addHistory: async (command, exitCode) => {
    try {
      await rpc('history.add', { command, exitCode })
      await get().loadHistory()
    } catch {
      /* ignore */
    }
  },
  clearHistory: async () => {
    try {
      await rpc('history.clear')
      set({ history: [] })
    } catch {
      /* ignore */
    }
  },
  deleteHistory: async (id) => {
    try {
      await rpc('history.delete', { id })
      await get().loadHistory()
    } catch {
      /* ignore */
    }
  },
  addFavorite: async (command, label) => {
    try {
      await rpc('favorites.add', { command, label })
      await get().loadFavorites()
    } catch {
      /* ignore */
    }
  },
  removeFavorite: async (command) => {
    try {
      await rpc('favorites.remove', { command })
      await get().loadFavorites()
    } catch {
      /* ignore */
    }
  },
  isFavorite: (command) => get().favorites.some((f) => f.command === command),
}))
