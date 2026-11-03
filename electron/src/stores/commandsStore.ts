import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { CommandDetail, SubcommandHelp } from '@/lib/types'

export type CommandSortMode = 'default' | 'alpha' | 'custom'

interface CommandsState {
  commandItems: { name: string; installed: boolean }[]
  selectedDetail: CommandDetail | null
  descriptions: Record<string, string>
  subcommandHelps: Record<string, SubcommandHelp | undefined>
  isLoading: boolean
  listLoading: boolean
  message: string
  filterInstalled: boolean
  searchTerm: string
  runArgs: string
  sortMode: CommandSortMode
  customOrder: string[]
  setRunArgs: (args: string) => void
  refresh: () => Promise<void>
  setFilterInstalled: (installed: boolean) => void
  setSearchTerm: (term: string) => void
  setSortMode: (mode: CommandSortMode) => void
  moveCommand: (from: string, to: string) => void
  selectCommand: (name: string) => Promise<void>
  getDescription: (name: string) => Promise<string>
  getSubcommandHelp: (command: string, subcommand: string) => Promise<SubcommandHelp | undefined>
}

const SORT_KEY = 'devtool:command-sort'

function loadSort(): { mode: CommandSortMode; order: string[] } {
  try {
    const raw = localStorage.getItem(SORT_KEY)
    if (!raw) return { mode: 'default', order: [] }
    const parsed = JSON.parse(raw)
    return {
      mode: parsed.mode === 'alpha' || parsed.mode === 'custom' ? parsed.mode : 'default',
      order: Array.isArray(parsed.order) ? parsed.order.filter((n: unknown) => typeof n === 'string') : [],
    }
  } catch {
    return { mode: 'default', order: [] }
  }
}

export const useCommandsStore = create<CommandsState>((set, get) => ({
  commandItems: [],
  selectedDetail: null,
  descriptions: {},
  subcommandHelps: {},
  isLoading: false,
  listLoading: false,
  message: '',
  filterInstalled: true,
  searchTerm: '',
  runArgs: '',
  sortMode: loadSort().mode,
  customOrder: loadSort().order,
  setRunArgs: (args) => set({ runArgs: args }),
  setSortMode: (mode) => {
    let order = get().customOrder
    if (mode === 'custom' && !order.length) {
      order = get().commandItems.map((c) => c.name)
      try {
        localStorage.setItem(SORT_KEY, JSON.stringify({ mode, order }))
      } catch {}
    }
    set({ sortMode: mode, customOrder: order })
  },
  moveCommand: (from, to) => {
    const { customOrder, commandItems } = get()
    const order = customOrder.length
      ? [...customOrder]
      : commandItems.map((c) => c.name)
    const fi = order.indexOf(from)
    const ti = order.indexOf(to)
    if (fi === -1 || ti === -1) return
    order.splice(fi, 1)
    order.splice(ti, 0, from)
    try {
      localStorage.setItem(SORT_KEY, JSON.stringify({ mode: 'custom', order }))
    } catch {}
    set({ sortMode: 'custom', customOrder: order })
  },
  refresh: async () => {
    set({ listLoading: true, message: '' })
    try {
      const r = await rpc('commands.list', {
        installed_only: get().filterInstalled,
      })
      set({ commandItems: r.items, listLoading: false })
      const { sortMode, customOrder } = get()
      if (sortMode === 'custom') {
        const names = r.items.map((c) => c.name)
        const merged = [...customOrder]
        for (const n of names) {
          if (!merged.includes(n)) merged.push(n)
        }
        const filtered = merged.filter((n) => names.includes(n))
        try {
          localStorage.setItem(
            SORT_KEY,
            JSON.stringify({ mode: 'custom', order: filtered }),
          )
        } catch {}
        set({ customOrder: filtered })
      }
    } catch (e: any) {
      set({ message: e.message, listLoading: false })
    }
  },
  setFilterInstalled: (installed) => {
    set({ filterInstalled: installed })
    get().refresh()
  },
  setSearchTerm: (term) => set({ searchTerm: term }),
  selectCommand: async (name) => {
    set({ isLoading: true, message: `Loading ${name}...`, runArgs: '' })
    try {
      const detail = await rpc('commands.detail', { name })
      set({ selectedDetail: detail, message: '', isLoading: false })
    } catch (e: any) {
      set({ message: e.message, isLoading: false })
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
  getSubcommandHelp: async (command, subcommand) => {
    const key = `${command}:${subcommand}`
    const cached = get().subcommandHelps[key]
    if (cached !== undefined) return cached
    try {
      const r = await rpc('commands.subcommand_help', { command, subcommand })
      set({ subcommandHelps: { ...get().subcommandHelps, [key]: r } })
      return r
    } catch {
      return undefined
    }
  },
}))
