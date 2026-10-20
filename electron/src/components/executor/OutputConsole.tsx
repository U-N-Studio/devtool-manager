import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useExecutorStore } from '@/stores/executorStore'

export function OutputConsole() {
  const output = useExecutorStore((s) => s.output)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [output])

  const lines = output.split('\n')

  return (
    <ScrollArea className="h-full bg-zinc-950">
      <div
        ref={scrollRef}
        className="font-mono text-xs p-3 leading-relaxed"
        style={{ maxHeight: '100%', overflowY: 'auto' }}
      >
        {lines.map((line, i) => {
          if (line === '') {
            return (
              <div key={i} className="text-zinc-200">
                {'\u00A0'}
              </div>
            )
          }
          const isError =
            line.startsWith('Error:') || line.includes('Traceback')
          return (
            <div
              key={i}
              className={isError ? 'text-red-400' : 'text-zinc-200'}
            >
              {line}
            </div>
          )
        })}
      </div>
    </ScrollArea>
  )
}
