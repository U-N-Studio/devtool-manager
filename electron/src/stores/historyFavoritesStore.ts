import { create } from 'zustand'
import { api } from '@/api'
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
      const items = await api.history.list()
      set({ history: items })
    } catch {
      /* ignore */
    }
  },
  loadFavorites: async () => {
    try {
      const items = await api.favorites.list()
      set({ favorites: items })
    } catch {
      /* ignore */
    }
  },
  addHistory: async (command, exitCode) => {
    try {
      await api.history.add(command, exitCode)
      await get().loadHistory()
    } catch {
      /* ignore */
    }
  },
  clearHistory: async () => {
    try {
      await api.history.clear()
      set({ history: [] })
    } catch {
      /* ignore */
    }
  },
  deleteHistory: async (id) => {
    try {
      await api.history.delete(id)
      await get().loadHistory()
    } catch {
      /* ignore */
    }
  },
  addFavorite: async (command, label) => {
    try {
      await api.favorites.add(command, label)
      await get().loadFavorites()
    } catch {
      /* ignore */
    }
  },
  removeFavorite: async (command) => {
    try {
      await api.favorites.remove(command)
      await get().loadFavorites()
    } catch {
      /* ignore */
    }
  },
  isFavorite: (command) => get().favorites.some((f) => f.command === command),
}))
