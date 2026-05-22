import { Link, useSearchParams } from "react-router-dom"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import PaginationControls from "@/components/PaginationControls"
import { useElections } from "@/hooks/useElections"

const LEVEL_LABELS: Record<string, string> = {
  national: "Ազգային",
  local: "Տեղական",
  referendum: "Հանրաքվե",
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("hy-AM")
}

function promiseCountLabel(count: number): string {
  return count === 1 ? `${count} խոստում` : `${count} խոստումներ`
}

export default function ElectionsListPage() {
  const [searchParams] = useSearchParams()
  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1

  const { data, isLoading, isError } = useElections(page)

  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Ընտրություններ</h1>
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-20 bg-zinc-200 rounded animate-pulse" />
          ))}
        </div>
      </main>
    )
  }

  if (isError) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Ընտրություններ</h1>
        <p className="text-sm text-red-600">Սխալ տեղի ունեցավ։ Խնդրում ենք կրկին փորձել։</p>
      </main>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Ընտրություններ</h1>
        <p className="text-sm text-zinc-500">Ընտրությունների տվյալները դեռ ավելացված չեն</p>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Ընտրություններ</h1>

      <div className="space-y-3">
        {data.items.map((election) => (
          <Link key={election.id} to={`/elections/${election.slug}`}>
            <Card className="hover:bg-zinc-50 transition-colors cursor-pointer">
              <CardContent className="flex items-center justify-between py-4 px-5">
                <div>
                  <p className="text-base font-semibold text-zinc-900">{election.name_hy}</p>
                  <p className="text-sm text-zinc-500 mt-1">{formatDate(election.election_date)}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0 ml-4">
                  <Badge variant="secondary">{LEVEL_LABELS[election.level] ?? election.level}</Badge>
                  <Badge variant="outline">{promiseCountLabel(election.promise_count)}</Badge>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {data.pages > 1 && (
        <PaginationControls currentPage={page} totalPages={data.pages} />
      )}
    </main>
  )
}
