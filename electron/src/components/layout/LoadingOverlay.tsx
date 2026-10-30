import { useEffect, useState } from 'react'

interface LoadingOverlayProps {
  visible: boolean
  delayMs?: number
  minDurationMs?: number
}

export function LoadingOverlay({
  visible,
  delayMs = 200,
  minDurationMs = 500,
}: LoadingOverlayProps) {
  const [show, setShow] = useState(false)

  useEffect(() => {
    if (!visible) {
      return
    }

    let showTimer: ReturnType<typeof setTimeout>
    let hideTimer: ReturnType<typeof setTimeout>
    const startTime = Date.now()

    showTimer = setTimeout(() => {
      setShow(true)
    }, delayMs)

    return () => {
      clearTimeout(showTimer)
      clearTimeout(hideTimer)
      const elapsed = Date.now() - startTime
      const remaining = Math.max(0, minDurationMs - elapsed)

      if (remaining > 0) {
        hideTimer = setTimeout(() => setShow(false), remaining)
      } else {
        setShow(false)
      }
    }
  }, [visible, delayMs, minDurationMs])

  return (
    <div
      className={`absolute inset-0 z-50 flex flex-col items-center justify-center gap-4 bg-background/80 backdrop-blur-sm transition-opacity duration-300 ${
        show ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}
    >
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-muted border-t-primary" />
      <p className="text-sm text-muted-foreground">加载中...</p>
    </div>
  )
}
