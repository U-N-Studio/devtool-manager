import { useEffect, useState, type KeyboardEvent } from 'react'
import { FolderOpen, Play, Square, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useExecutorStore } from '@/stores/executorStore'
import { OutputConsole } from './OutputConsole'

export function ExecuteTab() {
  const {
    cwd,
    isRunning,
    exitCode,
    execute,
    kill,
    setCwd,
    clearOutput,
    navigateHistory,
    initSubscriptions,
  } = useExecutorStore()

  const [command, setCommand] = useState('')
  const [cwdInput, setCwdInput] = useState(cwd)

  useEffect(() => {
    setCwdInput(cwd)
  }, [cwd])

  useEffect(() => {
    return initSubscriptions()
  }, [initSubscriptions])

  const handleExecute = () => {
    if (command.trim()) {
      void execute(command)
      setCommand('')
    }
  }

  const handleBrowse = () => {
    const path = prompt('输入工作目录:', cwd || '')
    if (path) {
      setCwd(path)
      setCwdInput(path)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleExecute()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      const result = navigateHistory('up')
      if (result !== null) setCommand(result)
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      const result = navigateHistory('down')
      if (result !== null) setCommand(result)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b p-2">
        <Input
          placeholder="工作目录(留空使用当前)"
          value={cwdInput}
          onChange={(e) => setCwdInput(e.target.value)}
          onBlur={() => setCwd(cwdInput)}
          className="font-mono text-sm"
        />
        <Button variant="outline" size="icon" onClick={handleBrowse}>
          <FolderOpen className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex items-center gap-2 border-b p-2">
        <Input
          placeholder="输入命令..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isRunning}
          className="font-mono text-sm"
        />
        {isRunning ? (
          <Button variant="destructive" size="icon" onClick={() => void kill()}>
            <Square className="h-4 w-4" />
          </Button>
        ) : (
          <Button size="icon" onClick={handleExecute} disabled={!command.trim()}>
            <Play className="h-4 w-4" />
          </Button>
        )}
        <Button variant="outline" size="icon" onClick={clearOutput}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-hidden">
        <OutputConsole />
      </div>

      <div className="flex items-center justify-between border-t p-2">
        <span className="text-xs text-muted-foreground">
          使用 ↑/↓ 浏览历史命令
        </span>
        {exitCode !== null && (
          <Badge variant={exitCode === 0 ? 'default' : 'destructive'}>
            Exit: {exitCode}
          </Badge>
        )}
      </div>
    </div>
  )
}
