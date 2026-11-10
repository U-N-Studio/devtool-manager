import * as React from 'react'
import { cn } from '@/lib/utils'

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'h-2 w-full overflow-hidden rounded-full bg-secondary',
        className,
      )}
      {...props}
    >
      <div className="h-full w-1/3 animate-pulse rounded-full bg-primary" />
    </div>
  ),
)
Progress.displayName = 'Progress'

export { Progress }
