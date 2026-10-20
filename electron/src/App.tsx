import { TitleBar } from '@/components/layout/TitleBar'
import { Sidebar } from '@/components/layout/Sidebar'
import { LoadingOverlay } from '@/components/layout/LoadingOverlay'
import { EnvTab } from '@/components/env/EnvTab'
import { useAppStore } from '@/stores/appStore'
import { useEnvStore } from '@/stores/envStore'

export default function App() {
  const activeTab = useAppStore((s) => s.activeTab)
  const envLoading = useEnvStore((s) => s.isLoading)
  const globalLoading = envLoading

  return (
    <div className="relative flex h-screen w-screen flex-col">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden">
          {activeTab === 'env' && <EnvTab />}
          {activeTab === 'packages' && (
            <div className="p-4 text-muted-foreground">
              Packages Tab (Task 4)
            </div>
          )}
          {activeTab === 'commands' && (
            <div className="p-4 text-muted-foreground">
              Commands Tab (Task 5)
            </div>
          )}
          {activeTab === 'executor' && (
            <div className="p-4 text-muted-foreground">
              Execute Tab (Task 6)
            </div>
          )}
        </main>
      </div>
      <LoadingOverlay visible={globalLoading} />
    </div>
  )
}
