import { Link } from "react-router-dom"
import type { PromiseListOut } from "@/types"
import ResolvedStatusBadge from "./ResolvedStatusBadge"

interface PromiseCardProps {
  promise: PromiseListOut
}

export default function PromiseCard({ promise }: PromiseCardProps) {
  const truncated =
    promise.quote_hy.length > 120 ? promise.quote_hy.slice(0, 120) + "…" : promise.quote_hy

  return (
    <Link
      to={`/promises/${promise.slug}`}
      className="flex justify-between items-start border-b border-zinc-100 py-3 hover:bg-zinc-50 cursor-pointer"
    >
      <div className="flex-1 mr-4">
        <p className="text-sm font-semibold text-zinc-900">{promise.title_hy}</p>
        <p className="text-sm text-zinc-700 line-clamp-2">{truncated}</p>
        {promise.made_date ? (
          <p className="text-xs text-zinc-400 mt-1">
            {promise.politician_name_hy} · {promise.made_date}
          </p>
        ) : (
          <p className="text-xs text-zinc-400 mt-1">{promise.politician_name_hy}</p>
        )}
      </div>
      <ResolvedStatusBadge status={promise.resolved_status} />
    </Link>
  )
}
