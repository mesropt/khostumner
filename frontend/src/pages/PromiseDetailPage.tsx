import { Link, useParams } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import ResolvedStatusBadge from "@/components/ResolvedStatusBadge"
import { usePromise } from "@/hooks/usePromise"

export default function PromiseDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const { data, isLoading, isError } = usePromise(slug!)

  // Loading skeleton — animate-pulse per UI-SPEC
  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8 animate-pulse">
        <div className="h-8 w-3/4 bg-zinc-200 rounded mb-6" />
        <div className="h-32 w-full bg-zinc-200 rounded mb-6" />
        <div className="space-y-3">
          <div className="h-4 w-24 bg-zinc-200 rounded" />
          <div className="h-4 w-48 bg-zinc-200 rounded" />
          <div className="h-4 w-32 bg-zinc-200 rounded" />
          <div className="h-4 w-40 bg-zinc-200 rounded" />
        </div>
      </main>
    )
  }

  // 404 / error state — exact Armenian from UI-SPEC Copywriting Contract
  if (isError || !data) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-4">Խոստումը չի գտնվել</h1>
        <Link
          to="/promises"
          className="text-blue-600 underline hover:text-blue-800 text-sm"
        >
          Վերադառնալ բոլոր խոստումներ
        </Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      {/* H1 title — D-13 */}
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">{data.title_hy}</h1>

      {/* Quote hero — D-11: full verbatim text, Display 28px regular, UI-SPEC quote hero spec */}
      <blockquote className="bg-zinc-50 rounded px-6 py-6 text-[28px] font-normal text-zinc-700 leading-relaxed">
        {data.quote_hy}
      </blockquote>

      <Separator className="my-6" />

      {/* Metadata section — UI-SPEC Promise Detail Labels */}
      <div className="space-y-3">
        {/* Status badge */}
        <div>
          <ResolvedStatusBadge status={data.resolved_status} />
        </div>

        {/* Politician row — T-03-11: link to /persons/:slug */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Քաղաքական գործիչ</span>
          <Link
            to={`/persons/${data.politician_slug}`}
            className="text-sm font-semibold text-zinc-900 underline"
          >
            {data.politician_name_hy}
          </Link>
        </div>

        {/* made_date row — omitted entirely when null (D-11) */}
        {data.made_date && (
          <p className="text-sm text-zinc-500">Ստեղծված: {data.made_date}</p>
        )}

        {/* expected_date row — omitted entirely when null (D-07b, D-11) */}
        {data.expected_date && (
          <p className="text-sm text-zinc-500">Ժամկետ: {data.expected_date}</p>
        )}
      </div>

      {/* Source links — T-03-11: rel="noopener noreferrer" on all external links */}
      <div className="flex gap-3 mt-4">
        <a
          href={data.source_url}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="outline">Աղբյուր</Button>
        </a>
        {/* Wayback Machine — D-12: only when archived_url present */}
        {data.archived_url && (
          <a
            href={data.archived_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="ghost">Wayback Machine</Button>
          </a>
        )}
      </div>
    </main>
  )
}