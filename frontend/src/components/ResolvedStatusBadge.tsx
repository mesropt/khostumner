import type { PromiseStubOut } from "@/types"

interface ResolvedStatusBadgeProps {
  status: PromiseStubOut["resolved_status"]
}

const STATUS_CONFIG: Record<
  PromiseStubOut["resolved_status"],
  { className: string; label: string }
> = {
  kept: {
    className: "bg-green-100 text-green-800 border-green-200",
    label: "Կատարված",
  },
  broken: {
    className: "bg-red-100 text-red-800 border-red-200",
    label: "Չկատարված",
  },
  in_progress: {
    className: "bg-yellow-100 text-yellow-800 border-yellow-200",
    label: "Ընթացքի մեջ",
  },
  stalled: {
    className: "bg-gray-100 text-gray-600 border-gray-200",
    label: "Կասեցված",
  },
  not_rated: {
    className: "bg-zinc-100 text-zinc-500 border-zinc-200",
    label: "Չգնահատված",
  },
}

export default function ResolvedStatusBadge({ status }: ResolvedStatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.not_rated

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${config.className}`}
    >
      {config.label}
    </span>
  )
}
