import { useEffect, useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
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
import type { CommandDetail } from '@/lib/types'

interface CommandDetailCardProps {
  detail: CommandDetail
}

export function CommandDetailCard({ detail }: CommandDetailCardProps) {
  const getDescription = useCommandsStore((s) => s.getDescription)
  const [descMap, setDescMap] = useState<Record<string, string>>({})

  useEffect(() => {
    let cancelled = false
    const namesToFetch = new Set<string>()
    detail.env_vars.forEach((v) => namesToFetch.add(v))
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

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle className="font-mono">{detail.name}</CardTitle>
          <Badge variant={detail.installed ? 'default' : 'outline'}>
            {detail.installed ? 'Installed' : 'Not Installed'}
          </Badge>
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
              <span>子命令 ({detail.subcommands.length})</span>
              <ChevronDown className="h-4 w-4" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              <ul className="mt-1 space-y-1 border-l border-border pl-3">
                {detail.subcommands.map((sc) => (
                  <li
                    key={sc.name}
                    className="flex flex-col gap-0.5 py-1 text-xs"
                  >
                    <span className="font-mono font-medium">{sc.name}</span>
                    <span className="text-muted-foreground">
                      {sc.description || '-'}
                    </span>
                  </li>
                ))}
              </ul>
            </CollapsibleContent>
          </Collapsible>
        )}

        {detail.params.length > 0 && (
          <Collapsible defaultOpen>
            <CollapsibleTrigger className="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm font-medium hover:bg-accent">
              <span>参数 ({detail.params.length})</span>
              <ChevronDown className="h-4 w-4" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              <ul className="mt-1 space-y-1 border-l border-border pl-3">
                {detail.params.map((p) => (
                  <li
                    key={p.name}
                    className="flex flex-col gap-0.5 py-1 text-xs"
                  >
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="cursor-help border-b border-dashed border-border font-mono font-medium">
                            {p.name}
                          </span>
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
              <div className="mt-2 flex flex-wrap gap-1.5">
                {detail.env_vars.map((v) => (
                  <TooltipProvider key={v}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Badge variant="secondary" className="cursor-help font-mono">
                          {v}
                        </Badge>
                      </TooltipTrigger>
                      {descMap[v] && (
                        <TooltipContent>{descMap[v]}</TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                ))}
              </div>
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
      </CardContent>
    </Card>
  )
}
