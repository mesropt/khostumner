import { Link } from "react-router-dom"
import { useStats } from "@/hooks/useStats"
import { usePromises } from "@/hooks/usePromises"
import PromiseStub from "@/components/PromiseStub"

// Status labels and semantic text colors per UI-SPEC Copywriting Contract + Status Badge Colors
const STATUS_CONFIG = [
  { key: "kept" as const, label: "Կատարված", textClass: "text-green-800" },
  { key: "broken" as const, label: "Չկատարված", textClass: "text-red-800" },
  { key: "in_progress" as const, label: "Ընթացքի մեջ", textClass: "text-yellow-800" },
  { key: "stalled" as const, label: "Կասեցված", textClass: "text-gray-600" },
  { key: "not_rated" as const, label: "Չգնահատված", textClass: "text-zinc-500" },
] as const

export default function HomePage() {
  const { data, isLoading, isError } = useStats()
  const { data: recentData, isLoading: recentLoading } = usePromises({ page: 1, perPage: 10 })

  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Stats block skeleton */}
        <section className="bg-zinc-100 rounded p-6 mb-8">
          <div className="h-9 w-32 bg-zinc-200 rounded animate-pulse mb-4" />
          <div className="flex flex-wrap gap-4 mt-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="bg-zinc-50 rounded p-2 min-w-[80px] h-[60px] animate-pulse bg-zinc-200" />
            ))}
          </div>
        </section>

        {/* Recent promises skeleton */}
        <h2 className="text-xl font-semibold text-zinc-900 mb-4">Վերջին խոստումները</h2>
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 rounded animate-pulse" />
          ))}
        </div>
      </main>
    )
  }

  if (isError) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-sm text-red-600">Տվյալները բեռնելու ժամանակ սխալ է տեղի ունեցել</p>
        <p className="text-sm text-red-600">Կրկին փորձեք կամ թարմացրեք էջը</p>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      {/* Stats Block — D-01, D-03, UI-SPEC layout */}
      <section className="bg-zinc-100 rounded p-6 mb-8">
        {/* Total count */}
        <div className="mb-4">
          <p className="text-[28px] font-semibold text-zinc-900 leading-none">
            {data?.total ?? 0}
          </p>
          <p className="text-sm text-zinc-500 mt-1">Ընդամենը</p>
        </div>

        {/* Per-status stat cards */}
        <div className="flex flex-wrap gap-4 mt-4">
          {STATUS_CONFIG.map(({ key, label, textClass }) => (
            <div key={key} className="bg-zinc-50 rounded p-2 min-w-[80px]">
              <p className="text-[28px] font-semibold text-zinc-900 leading-none">
                {data?.by_status[key] ?? 0}
              </p>
              <p className={`text-sm mt-1 ${textClass}`}>{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Recent Promises Section */}
      <div className="flex items-center justify-between mb-4 mt-8">
        <h2 className="text-xl font-semibold text-zinc-900">Վերջին խոստումները</h2>
        <Link to="/promises" className="text-sm text-blue-600 underline">
          Բոլոր խոստումները →
        </Link>
      </div>

      {/* Recent promises list — wired to usePromises (replaces TODO placeholder from 03-02) */}
      {recentLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 rounded animate-pulse" />
          ))}
        </div>
      ) : recentData && recentData.items.length > 0 ? (
        <div>
          {recentData.items.map((p) => (
            <PromiseStub key={p.id} promise={p} />
          ))}
        </div>
      ) : (
        <p className="text-sm text-zinc-500">Խոստումներ դeռ ավelацвад чen</p>
      )}

      <Link to="/promises" className="text-sm text-blue-600 underline mt-4 block">
        Բoлор хostumnernerd →
      </Link>
    </main>
  )
}
