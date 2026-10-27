import { useMemo, useState } from 'react'
import { Clock, Trash2, RotateCw, Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { useHistoryFavoritesStore } from '@/stores/historyFavoritesStore'
import { useExecutorStore } from '@/stores/executorStore'

function formatTime(ts: number): string {
  const d = new Date(ts * 1000)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
}

export function HistoryPanel() {
  const history = useHistoryFavoritesStore((s) => s.history)
  const clearHistory = useHistoryFavoritesStore((s) => s.clearHistory)
  const deleteHistory = useHistoryFavoritesStore((s) => s.deleteHistory)
  const execute = useExecutorStore((s) => s.execute)
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!search.trim()) return history
    const q = search.toLowerCase()
    return history.filter((h) => h.command.toLowerCase().includes(q))
  }, [history, search])

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-border p-2">
        <Clock className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">历史</span>
        <span className="text-xs text-muted-foreground">({history.length})</span>
        {history.length > 0 && (
          <Button
            variant="ghost"
            size="icon"
            className="ml-auto h-6 w-6"
            onClick={clearHistory}
            title="清空历史"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>
      {history.length > 5 && (
        <div className="relative border-b border-border p-2">
          <Search className="absolute left-4 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索历史..."
            className="h-7 pl-7 pr-7 text-xs"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      )}
      <ScrollArea className="flex-1">
        <div className="py-1">
          {filtered.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-muted-foreground">
              {history.length === 0 ? '暂无历史' : '无匹配结果'}
            </div>
          ) : (
            filtered.map((h) => (
              <div
                key={h.id}
                className="group flex flex-col gap-0.5 px-3 py-1.5 hover:bg-accent"
              >
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => void execute(h.command)}
                    className="flex flex-1 items-center gap-1 text-left"
                    title="重新运行"
                  >
                    <RotateCw className="h-3 w-3 shrink-0 text-muted-foreground opacity-0 group-hover:opacity-100" />
                    <span className="break-all font-mono text-xs">{h.command}</span>
                  </button>
                  {h.exitCode !== null && h.exitCode !== undefined && (
                    <Badge
                      variant={h.exitCode === 0 ? 'default' : 'destructive'}
                      className="shrink-0 text-[10px]"
                    >
                      {h.exitCode}
                    </Badge>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5 shrink-0 opacity-0 group-hover:opacity-100"
                    onClick={() => deleteHistory(h.id)}
                    title="删除"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
                <span className="pl-4 text-[10px] text-muted-foreground">
                  {formatTime(h.timestamp)}
                </span>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
