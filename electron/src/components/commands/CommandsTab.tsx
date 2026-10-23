import { useEffect } from 'react'
import { RefreshCw, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { CommandDetailCard } from './CommandDetailCard'
import { useCommandsStore } from '@/stores/commandsStore'
import { useExecutorStore } from '@/stores/executorStore'

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

  const initExecutor = useExecutorStore((s) => s.initSubscriptions)

  useEffect(() => {
    refresh()
  }, [refresh])

  useEffect(() => {
    const unsub = initExecutor()
    return unsub
  }, [initExecutor])

  const filteredItems = searchTerm
    ? commandItems.filter((c) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    : commandItems

  const handleClick = (name: string) => {
    selectCommand(name)
  }

  return (
    <div className="flex h-full">
      <aside className="flex w-64 flex-col border-r border-border">
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
                className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`}
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
                    className={`flex w-full items-center gap-2 px-3 py-1.5 text-left font-mono text-sm hover:bg-accent ${
                      active ? 'bg-accent text-accent-foreground' : ''
                    }`}
                  >
                    <span
                      className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                        item.installed ? 'bg-green-500' : 'bg-zinc-400'
                      }`}
                    />
                    <span className={item.installed ? '' : 'text-muted-foreground'}>
                      {item.name}
                    </span>
                  </button>
                )
              })
            )}
          </div>
        </ScrollArea>
      </aside>

      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="p-4">
            {selectedDetail ? (
              <CommandDetailCard detail={selectedDetail} />
            ) : (
              <div className="p-8 text-center text-sm text-muted-foreground">
                选择一个命令查看详情
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
