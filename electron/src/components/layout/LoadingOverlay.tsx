import { Progress } from '@/components/ui/progress'

interface LoadingOverlayProps {
  visible: boolean
}

export function LoadingOverlay({ visible }: LoadingOverlayProps) {
  if (!visible) return null
  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center justify-center gap-3 bg-background/80 backdrop-blur-sm">
      <Progress className="w-48" />
      <p className="text-sm text-muted-foreground">加载中...</p>
    </div>
  )
}
