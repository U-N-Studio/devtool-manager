import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { PackageRow } from './PackageRow'
import { usePackagesStore } from '@/stores/packagesStore'

const FUNC_TAGS = ['', 'Web', 'Data', 'Test', 'Dev', 'Tool', 'Doc']
const LANG_TAGS = ['', 'Python', 'Java', 'JS', 'Go', 'Rust']
const INSTALL_TAGS = ['', 'Installed', 'Not Installed']

export function PackagesTab() {
  const {
    filteredPackages,
    isLoading,
    message,
    filters,
    page,
    pageSize,
    setFilters,
    refresh,
    install,
    uninstall,
    setPage,
  } = usePackagesStore()

  const [uninstallTarget, setUninstallTarget] = useState<string | null>(null)

  useEffect(() => {
    refresh()
  }, [refresh])

  const totalPages = Math.max(1, Math.ceil(filteredPackages.length / pageSize))
  const currentPage = Math.min(page, totalPages)
  const start = (currentPage - 1) * pageSize
  const end = start + pageSize
  const pageItems = filteredPackages.slice(start, end)

  const handleInstall = (name: string) => {
    install(name)
  }

  const handleUninstallClick = (name: string) => {
    setUninstallTarget(name)
  }

  const handleUninstallConfirm = () => {
    if (uninstallTarget) {
      uninstall(uninstallTarget)
    }
    setUninstallTarget(null)
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-border p-3">
        <Select
          value={filters.func || 'all'}
          onValueChange={(v) => setFilters({ func: v === 'all' ? '' : v })}
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="全部功能" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部功能</SelectItem>
            {FUNC_TAGS.filter((t) => t).map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filters.lang || 'all'}
          onValueChange={(v) => setFilters({ lang: v === 'all' ? '' : v })}
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="全部语言" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部语言</SelectItem>
            {LANG_TAGS.filter((t) => t).map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filters.install || 'all'}
          onValueChange={(v) => setFilters({ install: v === 'all' ? '' : v })}
        >
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="全部状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部状态</SelectItem>
            {INSTALL_TAGS.filter((t) => t).map((t) => (
              <SelectItem key={t} value={t}>
                {t}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button variant="outline" size="icon" onClick={refresh} title="Refresh">
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
        {message && (
          <span className="ml-2 text-xs text-muted-foreground truncate">{message}</span>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div>
          {pageItems.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              {isLoading ? 'Loading...' : 'No packages found.'}
            </div>
          ) : (
            pageItems.map((pkg) => (
              <PackageRow
                key={pkg.name}
                pkg={pkg}
                onInstall={handleInstall}
                onUninstall={handleUninstallClick}
              />
            ))
          )}
        </div>
      </ScrollArea>

      <div className="flex items-center justify-between border-t border-border px-3 py-2 text-xs text-muted-foreground">
        <span>
          共 {filteredPackages.length} 条,第 {currentPage}/{totalPages} 页
        </span>
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage(currentPage - 1)}
            disabled={currentPage <= 1 || isLoading}
            title="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setPage(currentPage + 1)}
            disabled={currentPage >= totalPages || isLoading}
            title="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <AlertDialog
        open={uninstallTarget !== null}
        onOpenChange={(open) => {
          if (!open) setUninstallTarget(null)
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Uninstall</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to uninstall <span className="font-mono">{uninstallTarget}</span>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleUninstallConfirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Uninstall
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
