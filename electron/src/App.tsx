import { useEffect } from 'react'
import { TitleBar } from '@/components/layout/TitleBar'
import { Sidebar } from '@/components/layout/Sidebar'
import { LoadingOverlay } from '@/components/layout/LoadingOverlay'
import { EnvTab } from '@/components/env/EnvTab'
import { PackagesTab } from '@/components/packages/PackagesTab'
import { CommandsTab } from '@/components/commands/CommandsTab'
import { BottomTerminal } from '@/components/executor/BottomTerminal'
import { QuickRunBar } from '@/components/commands/QuickRunBar'
import { useAppStore } from '@/stores/appStore'
import { useEnvStore } from '@/stores/envStore'
import { usePackagesStore } from '@/stores/packagesStore'
import { useCommandsStore } from '@/stores/commandsStore'
import { useExecutorStore } from '@/stores/executorStore'
import { useHistoryFavoritesStore } from '@/stores/historyFavoritesStore'

export default function App() {
  const activeTab = useAppStore((s) => s.activeTab)
  const theme = useAppStore((s) => s.theme)
  const envLoading = useEnvStore((s) => s.isLoading)
  const pkgsLoading = usePackagesStore((s) => s.isLoading)
  const cmdsLoading = useCommandsStore((s) => s.isLoading)
  const globalLoading = envLoading || pkgsLoading || cmdsLoading

  const initExecutor = useExecutorStore((s) => s.initSubscriptions)
  const loadHistory = useHistoryFavoritesStore((s) => s.loadHistory)
  const loadFavorites = useHistoryFavoritesStore((s) => s.loadFavorites)

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [theme])

  useEffect(() => {
    const unsub = initExecutor()
    return unsub
  }, [initExecutor])

  useEffect(() => {
    void loadHistory()
    void loadFavorites()
  }, [loadHistory, loadFavorites])

  return (
    <div className="relative flex h-screen w-screen flex-col">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <main className="flex-1 overflow-hidden">
            {activeTab === 'commands' && <CommandsTab />}
            {activeTab === 'env' && <EnvTab />}
            {activeTab === 'packages' && <PackagesTab />}
          </main>
          <QuickRunBar />
          <BottomTerminal />
        </div>
      </div>
      <LoadingOverlay visible={globalLoading} />
    </div>
  )
}
