import {
  Settings2,
  Package,
  Cpu,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAppStore, type TabId } from '@/stores/appStore'

interface NavItemDef {
  id: TabId
  label: string
  icon: LucideIcon
}

const NAV_ITEMS: NavItemDef[] = [
  { id: 'commands', label: '命令详情', icon: Cpu },
  { id: 'env', label: '环境变量', icon: Settings2 },
  { id: 'packages', label: 'Python 包', icon: Package },
]

export function Sidebar() {
  const activeTab = useAppStore((s) => s.activeTab)
  const setActiveTab = useAppStore((s) => s.setActiveTab)

  return (
    <nav className="flex w-40 flex-col border-r bg-background">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon
        const active = activeTab === item.id
        return (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors',
              active
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground',
            )}
          >
            <Icon className="h-4 w-4" />
            <span>{item.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
