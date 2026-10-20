import { Download, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { PackageItem } from '@/lib/types'

interface PackageRowProps {
  pkg: PackageItem
  onInstall: (name: string) => void
  onUninstall: (name: string) => void
}

export function PackageRow({ pkg, onInstall, onUninstall }: PackageRowProps) {
  return (
    <div className="flex items-center gap-3 border-b border-border px-3 py-2 hover:bg-accent/50">
      <div className="flex flex-1 min-w-0 items-center gap-2">
        <span className="font-mono text-sm truncate">{pkg.name}</span>
        <span className="text-xs text-muted-foreground shrink-0">{pkg.version}</span>
      </div>
      <div className="flex items-center gap-1.5 shrink-0">
        <Badge variant={pkg.installed ? 'default' : 'outline'}>
          {pkg.installed ? 'Installed' : 'Not Installed'}
        </Badge>
        {pkg.func_tag && (
          <Badge variant="secondary">{pkg.func_tag}</Badge>
        )}
        {pkg.lang_tag && (
          <Badge variant="secondary">{pkg.lang_tag}</Badge>
        )}
      </div>
      <div className="shrink-0">
        {pkg.installed ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onUninstall(pkg.name)}
            title="Uninstall"
          >
            <Trash2 className="h-4 w-4 hover:text-destructive" />
          </Button>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onInstall(pkg.name)}
            title="Install"
          >
            <Download className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}
