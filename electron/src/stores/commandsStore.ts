import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { CommandDetail } from '@/lib/types'

interface CommandsState {
  commandItems: { name: string; installed: boolean }[]
  selectedDetail: CommandDetail | null
  descriptions: Record<string, string>
  isLoading: boolean
  message: string
  filterInstalled: boolean
  searchTerm: string
  refresh: () => Promise<void>
  setFilterInstalled: (installed: boolean) => void
  setSearchTerm: (term: string) => void
  selectCommand: (name: string) => Promise<void>
  getDescription: (name: string) => Promise<string>
}

export const useCommandsStore = create<CommandsState>((set, get) => ({
  commandItems: [],
  selectedDetail: null,
  descriptions: {},
  isLoading: false,
  message: '',
  filterInstalled: true,
  searchTerm: '',
  refresh: async () => {
    set({ isLoading: true, message: '' })
    try {
      const r = await rpc('commands.list', {
        installed_only: get().filterInstalled,
      })
      set({ commandItems: r.items })
    } catch (e: any) {
      set({ message: e.message })
    } finally {
      set({ isLoading: false })
    }
  },
  setFilterInstalled: (installed) => {
    set({ filterInstalled: installed })
    get().refresh()
  },
  setSearchTerm: (term) => set({ searchTerm: term }),
  selectCommand: async (name) => {
    set({ isLoading: true, message: `Loading ${name}...` })
    try {
      const detail = await rpc('commands.detail', { name })
      set({ selectedDetail: detail, message: '' })
    } catch (e: any) {
      set({ message: e.message })
    } finally {
      set({ isLoading: false })
    }
  },
  getDescription: async (name) => {
    const cached = get().descriptions[name]
    if (cached) return cached
    try {
      const r = await rpc('commands.description', { name })
      set({ descriptions: { ...get().descriptions, [name]: r.text } })
      return r.text
    } catch {
      return ''
    }
  },
}))
