import { Link, useParams, useSearchParams } from "react-router-dom"
import PromiseStub from "@/components/PromiseStub"
import PaginationControls from "@/components/PaginationControls"
import { useElection } from "@/hooks/useElection"
import { useElectionPromises } from "@/hooks/useElectionPromises"

const LEVEL_LABELS: Record<string, string> = {
  national: "Ազգային",
  local: "Տեղական",
  referendum: "Հանրաքվե",
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("hy-AM")
}

export default function ElectionDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams] = useSearchParams()

  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1

  const { data, isLoading, isError } = useElection(slug!)
  const {
    data: promisesData,
    isLoading: promisesLoading,
  } = useElectionPromises({ slug: slug!, page })

  // Loading skeleton
  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8 animate-pulse">
        <div className="h-7 w-64 bg-zinc-200 rounded mb-3" />
        <div className="h-4 w-48 bg-zinc-200 rounded" />
        <div className="mt-10 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 rounded" />
          ))}
        </div>
      </main>
    )
  }

  // 404 or error
  if (isError || !data) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-4">Ընտրությունը չի գտնվել</h1>
        <Link to="/elections" className="text-blue-600 underline hover:text-blue-800 text-sm">
          Վերադառնալ ընտրությունների ցուցակ
        </Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      {/* Election header */}
      <header>
        <h1 className="text-2xl font-semibold text-zinc-900">{data.name_hy}</h1>
        <p className="text-sm text-zinc-500 mt-1">
          {formatDate(data.election_date)} · {LEVEL_LABELS[data.level] ?? data.level}
        </p>
        {data.description_hy && (
          <p className="text-sm text-zinc-700 mt-2">{data.description_hy}</p>
        )}
      </header>

      {/* Promises section */}
      <section className="mt-8">
        <h2 className="text-xl font-semibold text-zinc-900 mt-8 mb-4">Կապված խոստումներ</h2>

        {promisesLoading && (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-12 bg-zinc-200 rounded animate-pulse" />
            ))}
          </div>
        )}

        {!promisesLoading && promisesData && (
          <>
            {promisesData.items.length === 0 ? (
              <p className="text-sm text-zinc-500 py-8 text-center">Խոստումներ չեն գտնվել</p>
            ) : (
              <div>
                {promisesData.items.map((promise) => (
                  <PromiseStub key={promise.id} promise={promise} />
                ))}
              </div>
            )}

            {promisesData.pages > 1 && (
              <PaginationControls currentPage={page} totalPages={promisesData.pages} />
            )}
          </>
        )}
      </section>
    </main>
  )
}
