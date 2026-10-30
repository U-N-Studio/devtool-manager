import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { CommandDetail, SubcommandHelp } from '@/lib/types'

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
  setRunArgs: (args: string) => void
  refresh: () => Promise<void>
  setFilterInstalled: (installed: boolean) => void
  setSearchTerm: (term: string) => void
  selectCommand: (name: string) => Promise<void>
  getDescription: (name: string) => Promise<string>
  getSubcommandHelp: (command: string, subcommand: string) => Promise<SubcommandHelp | undefined>
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
  setRunArgs: (args) => set({ runArgs: args }),
  refresh: async () => {
    set({ listLoading: true, message: '' })
    try {
      const r = await rpc('commands.list', {
        installed_only: get().filterInstalled,
      })
      set({ commandItems: r.items, listLoading: false })
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
