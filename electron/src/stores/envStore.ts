import { create } from 'zustand'
import { api } from '@/api'
import type { EnvItem, ToolInfo } from '@/lib/types'

interface EnvState {
  /** 分类 -> 条目列表(后端返回的 categorized map) */
  categorizedItems: Record<string, EnvItem[]>
  /** 当前选中分类对应的扁平条目列表(派生) */
  envItems: EnvItem[]
  toolInfo: ToolInfo | null
  selectedCategory: string
  isLoading: boolean
  message: string
  refresh: () => Promise<void>
  refreshToolInfo: (category: string) => Promise<void>
  setCategory: (category: string) => void
  setVar: (
    name: string,
    value: string,
    source: 'system' | 'user',
  ) => Promise<boolean>
  deleteVar: (
    name: string,
    source: 'system' | 'user',
  ) => Promise<boolean>
  addPathEntry: (
    value: string,
    source: 'system' | 'user',
  ) => Promise<boolean>
  deletePathEntry: (
    value: string,
    source: 'system' | 'user',
  ) => Promise<boolean>
}

/**
 * 从 categorized map 中按 selectedCategory 提取扁平列表。
 * - 'All': 合并所有分类条目
 * - 'PATH': 仅 Path 分类
 * - 其他: 对应分类(不存在则空数组)
 */
function flattenByCategory(
  categorized: Record<string, EnvItem[]>,
  category: string,
): EnvItem[] {
  if (category === 'All') {
    return Object.values(categorized).flat()
  }
  if (category === 'PATH') {
    return categorized['Path'] ?? []
  }
  return categorized[category] ?? []
}

export const useEnvStore = create<EnvState>((set, get) => ({
  categorizedItems: {},
  envItems: [],
  toolInfo: null,
  selectedCategory: 'All',
  isLoading: false,
  message: '',

  refresh: async () => {
    set({ isLoading: true, message: '' })
    try {
      const categorized = await api.env.list()
      const envItems = flattenByCategory(categorized, get().selectedCategory)
      set({ categorizedItems: categorized, envItems })
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
    } finally {
      set({ isLoading: false })
    }
  },

  refreshToolInfo: async (category) => {
    set({ isLoading: true })
    try {
      set({ toolInfo: await api.tools.info(category) })
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
    } finally {
      set({ isLoading: false })
    }
  },

  setCategory: (category) => {
    set({
      selectedCategory: category,
      envItems: flattenByCategory(get().categorizedItems, category),
    })
  },

  setVar: async (name, value, source) => {
    set({ isLoading: true, message: `Setting ${name}...` })
    try {
      const ok = await api.env.setVar(name, value, source)
      await get().refresh()
      set({ message: ok ? `OK: ${name} set` : `Failed: ${name}` })
      return ok
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  deleteVar: async (name, source) => {
    set({ isLoading: true, message: `Deleting ${name}...` })
    try {
      const ok = await api.env.deleteVar(name, source)
      await get().refresh()
      set({ message: ok ? `OK: ${name} deleted` : `Failed: ${name}` })
      return ok
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  addPathEntry: async (value, source) => {
    set({ isLoading: true, message: `Adding to PATH: ${value}...` })
    try {
      const ok = await api.env.addPathEntry(value, source)
      await get().refresh()
      set({ message: ok ? 'OK: added to PATH' : 'Failed' })
      return ok
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  deletePathEntry: async (value, source) => {
    set({ isLoading: true, message: `Removing from PATH: ${value}...` })
    try {
      const ok = await api.env.deletePathEntry(value, source)
      await get().refresh()
      set({ message: ok ? 'OK: removed from PATH' : 'Failed' })
      return ok
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
      return false
    } finally {
      set({ isLoading: false })
    }
  },
}))
