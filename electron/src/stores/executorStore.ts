import { create } from 'zustand'
import { rpc, onNotification } from '@/lib/ipc'
import { useHistoryFavoritesStore } from '@/stores/historyFavoritesStore'

interface ExecutorState {
  output: string
  isRunning: boolean
  exitCode: number | null
  cwd: string
  sessionId: string | null
  lastCommand: string
  history: string[]
  historyIndex: number
  execute: (command: string) => Promise<void>
  kill: () => Promise<void>
  setCwd: (path: string) => void
  clearOutput: () => void
  navigateHistory: (direction: 'up' | 'down') => string | null
  initSubscriptions: () => () => void
}

const MAX_LINES = 5000

export const useExecutorStore = create<ExecutorState>((set, get) => ({
  output: '',
  isRunning: false,
  exitCode: null,
  cwd: '',
  sessionId: null,
  lastCommand: '',
  history: [],
  historyIndex: -1,
  execute: async (command) => {
    if (!command.trim() || get().isRunning) return
    const cwd = get().cwd || undefined
    set((s) => ({
      output: s.output + `$ ${command}\n`,
      isRunning: true,
      exitCode: null,
      lastCommand: command,
      history: [...s.history, command],
      historyIndex: -1,
    }))
    try {
      const r = await rpc('executor.execute', { command, cwd })
      set({ sessionId: r.sessionId })
    } catch (e: any) {
      set((s) => ({
        output: s.output + `Error: ${e.message}\n`,
        isRunning: false,
      }))
    }
  },
  kill: async () => {
    const sid = get().sessionId
    if (!sid) return
    try {
      await rpc('executor.kill', { sessionId: sid })
    } catch {
      /* 忽略 */
    }
  },
  setCwd: (path) => set({ cwd: path }),
  clearOutput: () => set({ output: '', exitCode: null }),
  navigateHistory: (direction) => {
    const { history, historyIndex } = get()
    if (history.length === 0) return null
    let newIdx: number
    if (historyIndex === -1) {
      newIdx = direction === 'up' ? history.length - 1 : -1
    } else {
      newIdx =
        direction === 'up'
          ? Math.max(0, historyIndex - 1)
          : historyIndex + 1
      if (newIdx >= history.length) newIdx = -1
    }
    set({ historyIndex: newIdx })
    return newIdx === -1 ? '' : history[newIdx]
  },
  initSubscriptions: () => {
    const unsubOutput = onNotification(
      'executor.output',
      ({ sessionId, line }) => {
        if (sessionId !== get().sessionId) return
        set((s) => {
          const newOutput = s.output + line
          const lines = newOutput.split('\n')
          if (lines.length > MAX_LINES) {
            return { output: lines.slice(-MAX_LINES).join('\n') }
          }
          return { output: newOutput }
        })
      },
    )
    const unsubDone = onNotification(
      'executor.done',
      ({ sessionId, exitCode }) => {
        if (sessionId !== get().sessionId) return
        const cmd = get().lastCommand
        set((s) => ({
          isRunning: false,
          exitCode,
          output: s.output + `\nProcess exited with code ${exitCode}\n`,
        }))
        if (cmd) {
          void useHistoryFavoritesStore.getState().addHistory(cmd, exitCode)
        }
      },
    )
    return () => {
      unsubOutput()
      unsubDone()
    }
  },
}))
