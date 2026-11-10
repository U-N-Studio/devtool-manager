import { useEffect, useRef, useState, useCallback } from 'react'
import {
  ChevronDown,
  ChevronUp,
  X,
  Trash2,
  Square,
  TerminalSquare,
  CornerLeftDown,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAppStore } from '@/stores/appStore'
import { useExecutorStore } from '@/stores/executorStore'
import { cn } from '@/lib/utils'

export function BottomTerminal() {
  const collapsed = useAppStore((s) => s.terminalCollapsed)
  const visible = useAppStore((s) => s.terminalVisible)
  const height = useAppStore((s) => s.terminalHeight)
  const toggleTerminal = useAppStore((s) => s.toggleTerminal)
  const setTerminalVisible = useAppStore((s) => s.setTerminalVisible)
  const setTerminalHeight = useAppStore((s) => s.setTerminalHeight)

  const output = useExecutorStore((s) => s.output)
  const isRunning = useExecutorStore((s) => s.isRunning)
  const exitCode = useExecutorStore((s) => s.exitCode)
  const lastCommand = useExecutorStore((s) => s.lastCommand)
  const execute = useExecutorStore((s) => s.execute)
  const kill = useExecutorStore((s) => s.kill)
  const clearOutput = useExecutorStore((s) => s.clearOutput)
  const navigateHistory = useExecutorStore((s) => s.navigateHistory)

  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const resizingRef = useRef(false)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [output])

  useEffect(() => {
    if (visible && !collapsed) {
      inputRef.current?.focus()
    }
  }, [visible, collapsed])

  const startResize = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault()
      resizingRef.current = true
      const startY = e.clientY
      const startH = height
      const onMove = (ev: MouseEvent) => {
        if (!resizingRef.current) return
        const delta = startY - ev.clientY
        const next = Math.min(560, Math.max(80, startH + delta))
        setTerminalHeight(next)
      }
      const onUp = () => {
        resizingRef.current = false
        window.removeEventListener('mousemove', onMove)
        window.removeEventListener('mouseup', onUp)
      }
      window.addEventListener('mousemove', onMove)
      window.addEventListener('mouseup', onUp)
    },
    [height, setTerminalHeight],
  )

  if (!visible) {
    return (
      <div className="terminal-header flex h-7 items-center gap-1 border-t px-2">
        <Button
          variant="ghost"
          size="sm"
          className="h-6 gap-1 px-2 text-xs"
          onClick={() => setTerminalVisible(true)}
          title="显示终端"
        >
          <TerminalSquare className="h-3.5 w-3.5" />
          <span>终端</span>
        </Button>
        {isRunning && (
          <span className="terminal-muted flex items-center gap-1 text-xs">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-green-500" />
            运行中
          </span>
        )}
      </div>
    )
  }

  const lines = output.split('\n')

  const handleSubmit = () => {
    const cmd = input.trim()
    if (!cmd || isRunning) return
    void execute(cmd)
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSubmit()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      const v = navigateHistory('up')
      if (v !== null) setInput(v)
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      const v = navigateHistory('down')
      if (v !== null) setInput(v)
    } else if (e.key === 'l' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      clearOutput()
    }
  }

  return (
    <div
      className="terminal-panel flex flex-col border-t"
      style={{ height: collapsed ? 32 : height }}
    >
      <div className="terminal-header flex h-8 items-center gap-2 border-b px-2">
        <div
          className="flex flex-1 cursor-row-resize items-center gap-2"
          onMouseDown={startResize}
        >
          <TerminalSquare className="terminal-muted h-3.5 w-3.5" />
          <span className="text-xs font-medium">终端</span>
          {isRunning && (
            <span className="terminal-muted flex items-center gap-1 text-[10px]">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-green-500" />
              运行中
            </span>
          )}
          {exitCode !== null && !isRunning && (
            <Badge
              variant={exitCode === 0 ? 'default' : 'destructive'}
              className="text-[10px]"
            >
              Exit: {exitCode}
            </Badge>
          )}
          {lastCommand && (
            <span className="terminal-muted truncate font-mono text-[10px]">
              {lastCommand}
            </span>
          )}
        </div>
        <div className="ml-auto flex items-center gap-0.5">
          <Button
            variant="ghost"
            size="icon"
            className="terminal-btn h-6 w-6"
            onClick={(e) => {
              e.stopPropagation()
              clearOutput()
            }}
            title="清空"
            disabled={isRunning}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
          {isRunning && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-red-500 hover:text-red-400"
              onClick={(e) => {
                e.stopPropagation()
                void kill()
              }}
              title="停止"
            >
              <Square className="h-3 w-3" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="terminal-btn h-6 w-6"
            onClick={(e) => {
              e.stopPropagation()
              toggleTerminal()
            }}
            title={collapsed ? '展开' : '折叠'}
          >
            {collapsed ? (
              <ChevronUp className="h-3.5 w-3.5" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="terminal-btn h-6 w-6"
            onClick={(e) => {
              e.stopPropagation()
              setTerminalVisible(false)
            }}
            title="隐藏"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {!collapsed && (
        <>
          <div
            ref={scrollRef}
            className="terminal-body flex-1 overflow-y-auto px-2 py-1 font-mono text-xs leading-relaxed"
          >
            {lines.length === 0 || (lines.length === 1 && lines[0] === '') ? (
              <div className="terminal-muted flex h-full items-center justify-center gap-1.5">
                <CornerLeftDown className="h-3.5 w-3.5" />
                <span>在下方输入命令并按回车执行</span>
              </div>
            ) : (
              lines.map((line, i) => {
                if (line === '') {
                  return (
                    <div key={i} className="terminal-text">
                      {'\u00A0'}
                    </div>
                  )
                }
                const isError =
                  line.startsWith('Error:') ||
                  line.includes('Traceback') ||
                  (line.startsWith('$ ') === false &&
                    (line.toLowerCase().includes('error') ||
                      line.toLowerCase().includes('failed')))
                const isPrompt = line.startsWith('$ ')
                return (
                  <div
                    key={i}
                    className={cn(
                      isPrompt
                        ? 'terminal-prompt'
                        : isError
                          ? 'terminal-error'
                          : 'terminal-text',
                    )}
                  >
                    {line}
                  </div>
                )
              })
            )}
          </div>
          <div className="terminal-input-row flex items-center gap-2 border-t px-2 py-1">
            <span className="terminal-prompt font-mono text-xs">{'>'}</span>
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入命令（回车执行，↑↓ 浏览历史，Ctrl+L 清屏）"
              className="terminal-text flex-1 bg-transparent font-mono text-xs placeholder:text-muted-foreground focus:outline-none"
              disabled={isRunning}
              spellCheck={false}
              autoComplete="off"
            />
            {isRunning ? (
              <Button
                variant="destructive"
                size="sm"
                className="h-6 gap-1 px-2 text-xs"
                onClick={() => void kill()}
              >
                <Square className="h-3 w-3" />
                停止
              </Button>
            ) : (
              <Button
                size="sm"
                className="h-6 gap-1 px-2 text-xs"
                onClick={handleSubmit}
                disabled={!input.trim()}
              >
                运行
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  )
}
