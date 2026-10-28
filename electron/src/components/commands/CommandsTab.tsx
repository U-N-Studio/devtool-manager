import { useEffect, useMemo, useState } from 'react'
import { RefreshCw, Search, Terminal, Clock, Star } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { CommandDetailCard } from './CommandDetailCard'
import { HistoryPanel } from './HistoryPanel'
import { FavoritesPanel } from './FavoritesPanel'
import { useCommandsStore } from '@/stores/commandsStore'
import { useHistoryFavoritesStore } from '@/stores/historyFavoritesStore'
import { cn } from '@/lib/utils'

type SidebarTab = 'commands' | 'history' | 'favorites'

const SIDEBAR_TABS: { id: SidebarTab; label: string; icon: typeof Terminal }[] = [
  { id: 'commands', label: '命令', icon: Terminal },
  { id: 'history', label: '历史', icon: Clock },
  { id: 'favorites', label: '收藏', icon: Star },
]

export function CommandsTab() {
  const {
    commandItems,
    selectedDetail,
    isLoading,
    message,
    filterInstalled,
    searchTerm,
    refresh,
    setFilterInstalled,
    setSearchTerm,
    selectCommand,
  } = useCommandsStore()

  const loadHistory = useHistoryFavoritesStore((s) => s.loadHistory)
  const loadFavorites = useHistoryFavoritesStore((s) => s.loadFavorites)
  const historyCount = useHistoryFavoritesStore((s) => s.history.length)
  const favoritesCount = useHistoryFavoritesStore((s) => s.favorites.length)

  const [sidebarTab, setSidebarTab] = useState<SidebarTab>('commands')

  useEffect(() => {
    refresh()
  }, [refresh])

  useEffect(() => {
    void loadHistory()
    void loadFavorites()
  }, [loadHistory, loadFavorites])

  const filteredItems = useMemo(() => {
    if (!searchTerm) return commandItems
    const q = searchTerm.toLowerCase()
    return commandItems.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (selectedDetail?.name === c.name && selectedDetail.description?.toLowerCase().includes(q)),
    )
  }, [commandItems, searchTerm, selectedDetail])

  const handleClick = (name: string) => {
    selectCommand(name)
  }

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text
    const idx = text.toLowerCase().indexOf(query.toLowerCase())
    if (idx === -1) return text
    return (
      <>
        {text.slice(0, idx)}
        <mark className="rounded bg-yellow-400/30 px-0.5">{text.slice(idx, idx + query.length)}</mark>
        {text.slice(idx + query.length)}
      </>
    )
  }

  return (
    <div className="flex h-full">
      <aside className="flex w-72 flex-col border-r border-border">
        <div className="flex border-b border-border">
          {SIDEBAR_TABS.map((tab) => {
            const Icon = tab.icon
            const active = sidebarTab === tab.id
            const count = tab.id === 'history' ? historyCount : tab.id === 'favorites' ? favoritesCount : commandItems.length
            return (
              <button
                key={tab.id}
                onClick={() => setSidebarTab(tab.id)}
                className={cn(
                  'flex flex-1 flex-col items-center gap-0.5 py-2 text-xs transition-colors',
                  active
                    ? 'border-b-2 border-primary text-foreground'
                    : 'text-muted-foreground hover:text-foreground',
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {count > 0 && (
                  <span className="text-[10px] text-muted-foreground">{count}</span>
                )}
              </button>
            )
          })}
        </div>

        {sidebarTab === 'commands' && (
          <>
            <div className="space-y-2 border-b border-border p-3">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="搜索命令..."
                  className="pl-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={refresh}
                  disabled={isLoading}
                  title="刷新"
                >
                  <RefreshCw
                    className={cn('h-4 w-4', isLoading && 'animate-spin')}
                  />
                </Button>
                <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Checkbox
                    checked={filterInstalled}
                    onCheckedChange={(v) => setFilterInstalled(Boolean(v))}
                  />
                  仅显示已安装
                </label>
              </div>
            </div>
            <ScrollArea className="flex-1">
              <div className="py-1">
                {filteredItems.length === 0 ? (
                  <div className="px-3 py-6 text-center text-xs text-muted-foreground">
                    {isLoading ? '加载中...' : '无命令'}
                  </div>
                ) : (
                  filteredItems.map((item) => {
                    const active = selectedDetail?.name === item.name
                    return (
                      <button
                        key={item.name}
                        onClick={() => handleClick(item.name)}
                        className={cn(
                          'flex w-full items-center gap-2 px-3 py-1.5 text-left font-mono text-sm hover:bg-accent',
                          active && 'bg-accent text-accent-foreground',
                        )}
                      >
                        <span
                          className={cn(
                            'h-1.5 w-1.5 shrink-0 rounded-full',
                            item.installed ? 'bg-green-500' : 'bg-zinc-400',
                          )}
                        />
                        <span className={cn(!item.installed && 'text-muted-foreground')}>
                          {highlightMatch(item.name, searchTerm)}
                        </span>
                      </button>
                    )
                  })
                )}
              </div>
            </ScrollArea>
          </>
        )}

        {sidebarTab === 'history' && <HistoryPanel />}
        {sidebarTab === 'favorites' && <FavoritesPanel />}
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <ScrollArea className="flex-1">
          <div className="p-4">
            {selectedDetail ? (
              <CommandDetailCard detail={selectedDetail} />
            ) : (
              <div className="p-8 text-center text-sm text-muted-foreground">
                选择一个命令查看详情，或在历史/收藏中点击重新运行
              </div>
            )}
            {message && (
              <div className="mt-3 text-xs text-muted-foreground">{message}</div>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}
