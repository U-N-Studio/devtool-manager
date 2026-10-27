import { useMemo, useState } from 'react'
import { Star, Search, X, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useHistoryFavoritesStore } from '@/stores/historyFavoritesStore'
import { useExecutorStore } from '@/stores/executorStore'

export function FavoritesPanel() {
  const favorites = useHistoryFavoritesStore((s) => s.favorites)
  const removeFavorite = useHistoryFavoritesStore((s) => s.removeFavorite)
  const execute = useExecutorStore((s) => s.execute)
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!search.trim()) return favorites
    const q = search.toLowerCase()
    return favorites.filter(
      (f) =>
        f.command.toLowerCase().includes(q) ||
        (f.label || '').toLowerCase().includes(q),
    )
  }, [favorites, search])

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-border p-2">
        <Star className="h-4 w-4 text-yellow-400" />
        <span className="text-sm font-medium">收藏</span>
        <span className="text-xs text-muted-foreground">({favorites.length})</span>
      </div>
      {favorites.length > 5 && (
        <div className="relative border-b border-border p-2">
          <Search className="absolute left-4 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索收藏..."
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
              {favorites.length === 0 ? '暂无收藏，点击命令详情页星标添加' : '无匹配结果'}
            </div>
          ) : (
            filtered.map((f) => (
              <div
                key={f.command}
                className="group flex items-center gap-1 px-3 py-1.5 hover:bg-accent"
              >
                <button
                  onClick={() => void execute(f.command)}
                  className="flex flex-1 items-center gap-1.5 text-left"
                  title="运行"
                >
                  <Play className="h-3 w-3 shrink-0 text-muted-foreground opacity-0 group-hover:opacity-100" />
                  <span className="break-all font-mono text-xs">{f.command}</span>
                </button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5 shrink-0 opacity-0 group-hover:opacity-100"
                  onClick={() => removeFavorite(f.command)}
                  title="取消收藏"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
