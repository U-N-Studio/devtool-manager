import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { PackageItem } from '@/lib/types'

interface PackagesState {
  filteredPackages: PackageItem[]
  isLoading: boolean
  message: string
  filters: { func: string; lang: string; install: string }
  page: number
  pageSize: number
  setFilters: (filters: Partial<{ func: string; lang: string; install: string }>) => void
  refresh: () => Promise<void>
  install: (name: string) => Promise<void>
  uninstall: (name: string) => Promise<void>
  setPage: (page: number) => void
}

export const usePackagesStore = create<PackagesState>((set, get) => ({
  filteredPackages: [],
  isLoading: false,
  message: '',
  filters: { func: '', lang: '', install: '' },
  page: 1,
  pageSize: 50,
  setFilters: (filters) => {
    set({ filters: { ...get().filters, ...filters }, page: 1 })
    get().refresh()
  },
  refresh: async () => {
    const { filters } = get()
    set({ isLoading: true, message: '' })
    try {
      const r = await rpc('packages.list', {
        func: filters.func,
        lang: filters.lang,
        install: filters.install,
      })
      set({ filteredPackages: r.items })
    } catch (e: any) {
      set({ message: e.message })
    } finally {
      set({ isLoading: false })
    }
  },
  install: async (name) => {
    set({ isLoading: true, message: `Installing ${name}...` })
    try {
      const r = await rpc('packages.install', { name })
      set({ message: r.ok ? `Install success: ${name}` : `Install failed: ${name}` })
      await get().refresh()
    } catch (e: any) {
      set({ message: e.message })
    } finally {
      set({ isLoading: false })
    }
  },
  uninstall: async (name) => {
    set({ isLoading: true, message: `Uninstalling ${name}...` })
    try {
      const r = await rpc('packages.uninstall', { name })
      set({ message: r.ok ? `Uninstall success: ${name}` : `Uninstall failed: ${name}` })
      await get().refresh()
    } catch (e: any) {
      set({ message: e.message })
    } finally {
      set({ isLoading: false })
    }
  },
  setPage: (page) => set({ page }),
}))
