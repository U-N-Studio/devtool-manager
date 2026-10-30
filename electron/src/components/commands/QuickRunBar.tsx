import { useState } from 'react'
import { Play, Square, Copy, Check, TerminalSquare } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useCommandsStore } from '@/stores/commandsStore'
import { useExecutorStore } from '@/stores/executorStore'
import { useAppStore } from '@/stores/appStore'

export function QuickRunBar() {
  const selectedDetail = useCommandsStore((s) => s.selectedDetail)
  const args = useCommandsStore((s) => s.runArgs)
  const setArgs = useCommandsStore((s) => s.setRunArgs)
  const execute = useExecutorStore((s) => s.execute)
  const kill = useExecutorStore((s) => s.kill)
  const isRunning = useExecutorStore((s) => s.isRunning)
  const exitCode = useExecutorStore((s) => s.exitCode)
  const setTerminalVisible = useAppStore((s) => s.setTerminalVisible)

  const [copied, setCopied] = useState(false)

  const detail = selectedDetail
  const installed = detail?.installed ?? false

  const fullCommand = detail
    ? args.trim()
      ? `${detail.name} ${args.trim()}`
      : detail.name
    : ''

  const handleRun = () => {
    setTerminalVisible(true)
    void execute(fullCommand)
  }

  const handleStop = () => {
    void kill()
  }

  const handleCopy = async () => {
    if (!fullCommand) return
    try {
      await navigator.clipboard.writeText(fullCommand)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="terminal-panel flex flex-col border-t">
      <div className="terminal-header flex h-8 items-center gap-2 border-b px-2">
        <TerminalSquare className="h-3.5 w-3.5 shrink-0" />
        <span className="shrink-0 text-xs font-medium">快速运行</span>
        {exitCode !== null && !isRunning && (
          <Badge
            variant={exitCode === 0 ? 'default' : 'destructive'}
            className="shrink-0 text-[10px]"
          >
            Exit: {exitCode}
          </Badge>
        )}
        {isRunning && (
          <span className="terminal-muted flex shrink-0 items-center gap-1 text-[10px]">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-green-500" />
            运行中
          </span>
        )}
        <div className="ml-auto flex shrink-0 items-center gap-0.5">
          <Button
            variant="ghost"
            size="icon"
            className="terminal-btn h-6 w-6"
            onClick={handleCopy}
            title="复制完整命令"
            disabled={!detail}
          >
            {copied ? (
              <Check className="h-3 w-3 text-green-500" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </Button>
          {isRunning ? (
            <Button
              variant="destructive"
              size="sm"
              className="h-6 gap-1 px-2 text-xs"
              onClick={handleStop}
            >
              <Square className="h-3 w-3" />
              停止
            </Button>
          ) : (
            <Button
              size="sm"
              className="h-6 gap-1 px-2 text-xs"
              onClick={handleRun}
              disabled={!detail || !installed}
              title={
                !detail
                  ? '请先选择命令'
                  : installed
                    ? '运行（输出显示在底部终端）'
                    : '命令未安装'
              }
            >
              <Play className="h-3 w-3" />
              运行
            </Button>
          )}
        </div>
      </div>
      <div className="terminal-input-row flex flex-wrap items-center gap-1.5 border-t px-2 py-1.5">
        {detail && (
          <span className="terminal-prompt shrink-0 rounded bg-primary px-1.5 py-0.5 font-mono text-xs font-medium text-primary-foreground">
            {detail.name}
          </span>
        )}
        {args.trim().split(/\s+/).filter(Boolean).map((token, i) => (
          <span
            key={i}
            className="shrink-0 rounded bg-muted px-1.5 py-0.5 font-mono text-xs"
          >
            {token}
          </span>
        ))}
        <input
          value={args}
          onChange={(e) => setArgs(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !isRunning && installed) {
              handleRun()
            }
            if (e.key === 'Backspace' && args === '') {
              return
            }
          }}
          placeholder={
            detail
              ? '输入参数后按空格确认…'
              : '请先在左侧选择一个命令'
          }
          className="terminal-text min-w-[120px] flex-1 bg-transparent font-mono text-xs placeholder:text-muted-foreground focus:outline-none"
          disabled={isRunning || !detail || !installed}
          spellCheck={false}
          autoComplete="off"
        />
      </div>
    </div>
  )
}
