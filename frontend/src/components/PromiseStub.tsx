import { Link } from "react-router-dom"
import type { PromiseStubOut } from "@/types"
import ResolvedStatusBadge from "./ResolvedStatusBadge"

interface PromiseStubProps {
  promise: PromiseStubOut
}

export default function PromiseStub({ promise }: PromiseStubProps) {
  const truncated =
    promise.quote_hy.length > 120 ? promise.quote_hy.slice(0, 120) + "…" : promise.quote_hy

  return (
    <Link
      to={`/promises/${promise.slug}`}
      className="flex justify-between items-start border-b border-zinc-100 py-3 hover:bg-zinc-50 cursor-pointer"
    >
      <p className="text-sm text-zinc-700 line-clamp-2 flex-1 mr-4">{truncated}</p>
      <ResolvedStatusBadge status={promise.resolved_status} />
    </Link>
  )
}
