import { useSearchParams } from "react-router-dom"
import { AlertCircle } from "lucide-react"
import PaginationControls from "@/components/PaginationControls"
import PromiseCard from "@/components/PromiseCard"
import { usePromises } from "@/hooks/usePromises"

export default function UnfulfilledPage() {
  const [searchParams] = useSearchParams()
  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1

  const { data, isLoading, isError } = usePromises({ page, status: "broken,stalled" })

  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Չկատարված խոստումներ</h1>
        <div className="space-y-2">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 rounded animate-pulse" aria-hidden="true" />
          ))}
        </div>
      </main>
    )
  }

  if (isError) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Չկատարված խոստումներ</h1>
        <div className="flex flex-col items-center gap-4 py-16 text-center">
          <AlertCircle className="w-8 h-8 text-red-500" />
          <p className="text-zinc-700">Տվյալները բեռնելու ժամանակ սխալ է տեղի ունեցել</p>
          <p className="text-sm text-zinc-500">Կրկին փորձեք կամ թարմացրեք էջը</p>
        </div>
      </main>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Չկատարված խոստումներ</h1>
        <div className="flex flex-col items-center gap-4 py-16 text-center">
          <h2 className="text-lg font-semibold text-zinc-900">Չկատարված խոստումներ դեռ չկան</h2>
          <p className="text-sm text-zinc-500">
            Չկատարված խոստումները կհայտնվեն, երբ համայնքը կձայնաբերի
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Չկատարված խոստումներ</h1>

      <div className="space-y-0">
        {data.items.map((promise) => (
          <PromiseCard key={promise.id} promise={promise} />
        ))}
      </div>

      {data.pages > 1 && (
        <PaginationControls currentPage={page} totalPages={data.pages} />
      )}
    </main>
  )
}
