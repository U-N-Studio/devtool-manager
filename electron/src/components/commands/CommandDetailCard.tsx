import { useEffect, useState } from 'react'
import { ChevronDown, ChevronRight, Play, Square, Trash2, Star, Copy, Check, Loader2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useCommandsStore } from '@/stores/commandsStore'
import { useExecutorStore } from '@/stores/executorStore'
import { useHistoryFavoritesStore } from '@/stores/historyFavoritesStore'
import { OutputConsole } from '@/components/executor/OutputConsole'
import type { CommandDetail, CommandEnvVar, SubcommandHelp } from '@/lib/types'

interface CommandDetailCardProps {
  detail: CommandDetail
}

export function CommandDetailCard({ detail }: CommandDetailCardProps) {
  const getDescription = useCommandsStore((s) => s.getDescription)
  const getSubcommandHelp = useCommandsStore((s) => s.getSubcommandHelp)
  const [descMap, setDescMap] = useState<Record<string, string>>({})
  const [args, setArgs] = useState('')
  const [copied, setCopied] = useState(false)
  const execute = useExecutorStore((s) => s.execute)
  const kill = useExecutorStore((s) => s.kill)
  const isRunning = useExecutorStore((s) => s.isRunning)
  const exitCode = useExecutorStore((s) => s.exitCode)
  const clearOutput = useExecutorStore((s) => s.clearOutput)

  const favorites = useHistoryFavoritesStore((s) => s.favorites)
  const addFavorite = useHistoryFavoritesStore((s) => s.addFavorite)
  const removeFavorite = useHistoryFavoritesStore((s) => s.removeFavorite)
  const isFav = favorites.some((f) => f.command === detail.name)

  const [expandedSubs, setExpandedSubs] = useState<Set<string>>(new Set())
  const [subHelps, setSubHelps] = useState<Record<string, SubcommandHelp | undefined>>({})
  const [loadingSubs, setLoadingSubs] = useState<Set<string>>(new Set())

  useEffect(() => {
    setArgs('')
    setExpandedSubs(new Set())
    setSubHelps({})
  }, [detail.name])

  useEffect(() => {
    let cancelled = false
    const namesToFetch = new Set<string>()
    detail.env_vars.forEach((v: CommandEnvVar) => namesToFetch.add(v.name))
    detail.params.forEach((p) => namesToFetch.add(p.name))

    const loadAll = async () => {
      const entries = await Promise.all(
        Array.from(namesToFetch).map(async (n) => [n, await getDescription(n)] as const),
      )
      if (cancelled) return
      const next: Record<string, string> = {}
      for (const [n, t] of entries) next[n] = t
      setDescMap(next)
    }
    loadAll()
    return () => {
      cancelled = true
    }
  }, [detail, getDescription])

  const fullCommand = args.trim() ? `${detail.name} ${args.trim()}` : detail.name

  const handleRun = () => {
    void execute(fullCommand)
  }

  const handleStop = () => {
    void kill()
  }

  const handleClear = () => clearOutput()

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fullCommand)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* ignore */
    }
  }

  const handleFavToggle = () => {
    if (isFav) {
      void removeFavorite(detail.name)
    } else {
      void addFavorite(detail.name, detail.name)
    }
  }

  const handleSubcommandClick = (subName: string) => {
    setArgs((prev) => {
      const trimmed = prev.trim()
      if (!trimmed) return subName
      if (trimmed.startsWith(subName + ' ')) return prev
      return `${subName} ${trimmed}`
    })
  }

  const handleParamClick = (flag: string) => {
    setArgs((prev) => {
      const trimmed = prev.trim()
      if (!trimmed) return flag
      return `${trimmed} ${flag}`
    })
  }

  const handleSubExpand = async (subName: string) => {
    const next = new Set(expandedSubs)
    if (next.has(subName)) {
      next.delete(subName)
      setExpandedSubs(next)
      return
    }
    next.add(subName)
    setExpandedSubs(next)

    const key = subName
    if (subHelps[key] !== undefined) return

    setLoadingSubs((prev) => new Set(prev).add(key))
    try {
      const help = await getSubcommandHelp(detail.name, subName)
      setSubHelps((prev) => ({ ...prev, [key]: help }))
    } finally {
      setLoadingSubs((prev) => {
        const n = new Set(prev)
        n.delete(key)
        return n
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle className="font-mono">{detail.name}</CardTitle>
          <Badge variant={detail.installed ? 'default' : 'outline'}>
            {detail.installed ? 'Installed' : 'Not Installed'}
          </Badge>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="ml-auto h-7 w-7"
                  onClick={handleFavToggle}
                  title={isFav ? '取消收藏' : '收藏'}
                >
                  <Star
                    className={`h-4 w-4 ${isFav ? 'fill-yellow-400 text-yellow-400' : 'text-muted-foreground'}`}
                  />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{isFav ? '取消收藏' : '收藏到常用'}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-3 text-xs md:grid-cols-2">
          <div>
            <div className="font-medium">版本</div>
            <div className="break-all font-mono text-muted-foreground">
              {detail.version || '-'}
            </div>
          </div>
          <div>
            <div className="font-medium">路径</div>
            <div className="break-all font-mono text-muted-foreground">
              {detail.path || '-'}
            </div>
          </div>
          <div className="md:col-span-2">
            <div className="font-medium">描述</div>
            <div className="text-muted-foreground">
              {detail.description || '-'}
            </div>
          </div>
        </div>

        {detail.subcommands.length > 0 && (
          <Collapsible defaultOpen>
            <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm font-medium hover:bg-accent">
              <span>子命令 ({detail.subcommands.length}) — 点击展开参数,再点名称插入命令</span>
              <ChevronDown className="h-4 w-4" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              <ul className="mt-1 space-y-0.5 border-l border-border pl-3">
                {detail.subcommands.map((sc) => {
                  const expanded = expandedSubs.has(sc.name)
                  const help = subHelps[sc.name]
                  const loading = loadingSubs.has(sc.name)
                  return (
                    <li key={sc.name} className="py-0.5 text-xs">
                      <div className="flex items-start gap-1">
                        <button
                          onClick={() => handleSubExpand(sc.name)}
                          className="mt-0.5 shrink-0 text-muted-foreground hover:text-foreground"
                          title={expanded ? '收起参数' : '展开参数'}
                        >
                          {expanded ? (
                            <ChevronDown className="h-3 w-3" />
                          ) : (
                            <ChevronRight className="h-3 w-3" />
                          )}
                        </button>
                        <div className="flex flex-1 flex-col gap-0.5">
                          <button
                            onClick={() => handleSubcommandClick(sc.name)}
                            className="text-left font-mono font-medium text-primary hover:underline"
                            title={`插入子命令: ${sc.name}`}
                          >
                            {sc.name}
                          </button>
                          <span className="text-muted-foreground">
                            {sc.description || '-'}
                          </span>
                        </div>
                      </div>
                      {expanded && (
                        <div className="ml-4 mt-1 space-y-2 rounded-md bg-muted/30 p-2">
                          {loading && (
                            <div className="flex items-center gap-1.5 text-muted-foreground">
                              <Loader2 className="h-3 w-3 animate-spin" />
                              <span>加载参数中...</span>
                            </div>
                          )}
                          {!loading && help && help.params.length === 0 && help.pathParams.length === 0 && (
                            <div className="text-muted-foreground">暂无参数说明</div>
                          )}
                          {!loading && help && help.params.length > 0 && (
                            <div>
                              <div className="mb-1 font-medium">选项参数</div>
                              <ul className="space-y-0.5">
                                {help.params.map((p) => (
                                  <li key={p.name} className="flex flex-col gap-0.5">
                                    <TooltipProvider>
                                      <Tooltip>
                                        <TooltipTrigger asChild>
                                          <button
                                            onClick={() => handleParamClick(p.name)}
                                            className="cursor-help border-b border-dashed border-border text-left font-mono font-medium text-primary hover:underline"
                                            title={`插入: ${p.name}`}
                                          >
                                            {p.name}
                                          </button>
                                        </TooltipTrigger>
                                        {p.description && (
                                          <TooltipContent className="max-w-xs">
                                            {p.description}
                                          </TooltipContent>
                                        )}
                                      </Tooltip>
                                    </TooltipProvider>
                                    {p.description && (
                                      <span className="text-muted-foreground">
                                        {p.description}
                                      </span>
                                    )}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {!loading && help && help.pathParams.length > 0 && (
                            <div>
                              <div className="mb-1 font-medium">路径/位置参数</div>
                              <ul className="space-y-0.5">
                                {help.pathParams.map((p) => (
                                  <li key={p.name} className="flex flex-col gap-0.5">
                                    <span className="font-mono font-medium text-blue-600 dark:text-blue-400">
                                      {p.name}
                                    </span>
                                    {p.description && (
                                      <span className="text-muted-foreground">
                                        {p.description}
                                      </span>
                                    )}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </li>
                  )
                })}
              </ul>
            </CollapsibleContent>
          </Collapsible>
        )}

        {detail.params.length > 0 && (
          <Collapsible defaultOpen>
            <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm font-medium hover:bg-accent">
              <span>顶层参数 ({detail.params.length}) — 点击插入</span>
              <ChevronDown className="h-4 w-4" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              <ul className="mt-1 space-y-0.5 border-l border-border pl-3">
                {detail.params.map((p) => (
                  <li
                    key={p.name}
                    className="flex flex-col gap-0.5 py-0.5 text-xs"
                  >
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button
                            onClick={() => handleParamClick(p.name)}
                            className="cursor-help border-b border-dashed border-border text-left font-mono font-medium text-primary hover:underline"
                            title={`插入参数: ${p.name}`}
                          >
                            {p.name}
                          </button>
                        </TooltipTrigger>
                        {descMap[p.name] && (
                          <TooltipContent>{descMap[p.name]}</TooltipContent>
                        )}
                      </Tooltip>
                    </TooltipProvider>
                    <span className="text-muted-foreground">
                      {p.description || '-'}
                    </span>
                  </li>
                ))}
              </ul>
            </CollapsibleContent>
          </Collapsible>
        )}

        {detail.env_vars.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm font-medium hover:bg-accent">
              <span>环境变量 ({detail.env_vars.length})</span>
              <ChevronDown className="h-4 w-4" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              <ul className="mt-1 space-y-0.5 border-l border-border pl-3">
                {detail.env_vars.map((v) => (
                  <li
                    key={v.name}
                    className="flex flex-col gap-0.5 py-0.5 text-xs"
                  >
                    <div className="flex items-center gap-1.5">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <span className="cursor-help font-mono font-medium">
                              {v.name}
                            </span>
                          </TooltipTrigger>
                          {descMap[v.name] && (
                            <TooltipContent>{descMap[v.name]}</TooltipContent>
                          )}
                        </Tooltip>
                      </TooltipProvider>
                      <Badge variant={v.set ? 'default' : 'outline'} className="text-[10px]">
                        {v.set ? '已设置' : '未设置'}
                      </Badge>
                    </div>
                    <span className="break-all font-mono text-muted-foreground">
                      {v.value || '-'}
                    </span>
                  </li>
                ))}
              </ul>
            </CollapsibleContent>
          </Collapsible>
        )}

        {detail.config_sections.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm font-medium hover:bg-accent">
              <span>配置段 ({detail.config_sections.length})</span>
              <ChevronDown className="h-4 w-4" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-1 space-y-3 border-l border-border pl-3">
                {detail.config_sections.map((sec, idx) => (
                  <div key={`${sec.level}-${idx}`} className="space-y-1">
                    <div className="text-xs font-medium">{sec.level}</div>
                    <ul className="space-y-0.5 text-xs">
                      {sec.items.map((item) => (
                        <li
                          key={item.key}
                          className="flex gap-2 font-mono"
                        >
                          <span className="text-muted-foreground">
                            {item.key}:
                          </span>
                          <span className="break-all">{item.value}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        <div className="rounded-md border border-border">
          <div className="flex items-center gap-2 border-b border-border bg-muted/30 px-3 py-2">
            <span className="text-sm font-medium">快速运行</span>
            {exitCode !== null && (
              <Badge variant={exitCode === 0 ? 'default' : 'destructive'}>
                Exit: {exitCode}
              </Badge>
            )}
            <div className="ml-auto flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={handleCopy}
                title="复制完整命令"
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-green-500" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={handleClear}
                title="清空输出"
                disabled={isRunning}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
              {isRunning ? (
                <Button
                  variant="destructive"
                  size="sm"
                  className="h-7"
                  onClick={handleStop}
                >
                  <Square className="h-3.5 w-3.5" />
                  停止
                </Button>
              ) : (
                <Button
                  size="sm"
                  className="h-7"
                  onClick={handleRun}
                  disabled={!detail.installed}
                  title={detail.installed ? '运行' : '命令未安装'}
                >
                  <Play className="h-3.5 w-3.5" />
                  运行
                </Button>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-2">
            <span className="font-mono text-xs text-muted-foreground">
              {detail.name}
            </span>
            <Input
              value={args}
              onChange={(e) => setArgs(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isRunning && detail.installed) {
                  handleRun()
                }
              }}
              placeholder="参数（回车运行，↑↓ 浏览历史）"
              className="h-8 flex-1 font-mono text-xs"
              disabled={isRunning}
            />
          </div>
          <div className="h-48 border-t border-border">
            <OutputConsole />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
