import { create } from 'zustand'
import { rpc } from '@/lib/ipc'
import type { EnvItem, PythonInfo, ToolInfo } from '@/lib/types'

interface EnvState {
  pythonInfo: PythonInfo | null
  /** 分类 -> 条目列表(后端返回的 categorized map) */
  categorizedItems: Record<string, EnvItem[]>
  /** 当前选中分类对应的扁平条目列表(派生) */
  envItems: EnvItem[]
  toolInfo: ToolInfo | null
  selectedCategory: string
  isLoading: boolean
  message: string
  refresh: () => Promise<void>
  refreshPythonInfo: () => Promise<void>
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
  pythonInfo: null,
  categorizedItems: {},
  envItems: [],
  toolInfo: null,
  selectedCategory: 'All',
  isLoading: false,
  message: '',

  refresh: async () => {
    set({ isLoading: true, message: '' })
    try {
      const r = await rpc('env.list', {})
      const categorized = r.items as Record<string, EnvItem[]>
      const envItems = flattenByCategory(categorized, get().selectedCategory)
      set({ categorizedItems: categorized, envItems })
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
    } finally {
      set({ isLoading: false })
    }
  },

  refreshPythonInfo: async () => {
    try {
      set({ pythonInfo: await rpc('env.python_info', {}) })
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
    }
  },

  refreshToolInfo: async (category) => {
    set({ isLoading: true })
    try {
      set({ toolInfo: await rpc('tools.info', { category }) })
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
      const r = await rpc('env.set_var', { name, value, source })
      await get().refresh()
      set({ message: r.ok ? `OK: ${name} set` : `Failed: ${name}` })
      return r.ok
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
      const r = await rpc('env.delete_var', { name, source })
      await get().refresh()
      set({ message: r.ok ? `OK: ${name} deleted` : `Failed: ${name}` })
      return r.ok
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
      const r = await rpc('env.add_path_entry', { value, source })
      await get().refresh()
      set({ message: r.ok ? 'OK: added to PATH' : 'Failed' })
      return r.ok
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
      const r = await rpc('env.delete_path_entry', { value, source })
      await get().refresh()
      set({ message: r.ok ? 'OK: removed from PATH' : 'Failed' })
      return r.ok
    } catch (e: unknown) {
      set({ message: e instanceof Error ? e.message : String(e) })
      return false
    } finally {
      set({ isLoading: false })
    }
  },
}))
