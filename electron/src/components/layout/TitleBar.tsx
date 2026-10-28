import { useEffect, useState } from 'react'
import { Minus, Square, X, Copy, Sun, Moon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/stores/appStore'

export function TitleBar() {
  const [maximized, setMaximized] = useState(false)
  const theme = useAppStore((s) => s.theme)
  const toggleTheme = useAppStore((s) => s.toggleTheme)

  useEffect(() => {
    const unsubscribe = window.api.onWindowState((state) => {
      setMaximized(state === 'maximized')
    })
    return unsubscribe
  }, [])

  return (
    <div className="titlebar-drag flex h-9 items-center justify-between border-b bg-background px-3">
      <span className="select-none text-sm font-semibold">
        DevTool Manager
      </span>
      <div className="titlebar-no-drag flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={toggleTheme}
          title={theme === 'dark' ? '切换到浅色' : '切换到深色'}
        >
          {theme === 'dark' ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={() => window.api.windowMinimize()}
          title="最小化"
        >
          <Minus className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={() => window.api.windowMaximizeToggle()}
          title={maximized ? '还原' : '最大化'}
        >
          {maximized ? (
            <Copy className="h-3.5 w-3.5" />
          ) : (
            <Square className="h-3.5 w-3.5" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 hover:bg-destructive hover:text-destructive-foreground"
          onClick={() => window.api.windowClose()}
          title="关闭"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
