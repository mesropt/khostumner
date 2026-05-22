import { useSearchParams } from "react-router-dom"
import { AlertCircle } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import PaginationControls from "@/components/PaginationControls"
import PromiseCard from "@/components/PromiseCard"
import { usePromises } from "@/hooks/usePromises"
import { useElections } from "@/hooks/useElections"
import { usePoliticians } from "@/hooks/usePoliticians"

const STATUS_OPTIONS = [
  { value: "kept", label: "Կատարված" },
  { value: "broken", label: "Չկատարված" },
  { value: "in_progress", label: "Ընթացքի մեջ" },
  { value: "stalled", label: "Կասեցված" },
  { value: "not_rated", label: "Չգնահատված" },
]

export default function PromisesListPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1
  const status = searchParams.get("status") || null
  const politician_id = searchParams.get("politician_id") || null
  const election_id = searchParams.get("election_id") || null
  const made_date_from = searchParams.get("made_date_from") || null
  const made_date_to = searchParams.get("made_date_to") || null
  const expected_date_from = searchParams.get("expected_date_from") || null
  const expected_date_to = searchParams.get("expected_date_to") || null

  const { data, isLoading, isError } = usePromises({
    page,
    status,
    politician_id,
    election_id,
    made_date_from,
    made_date_to,
    expected_date_from,
    expected_date_to,
  })
  const { data: politiciansData } = usePoliticians({ page: 1, perPage: 100 })
  const { data: electionsData } = useElections(1)

  function handleStatusChange(value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === "__all__") {
        next.delete("status")
      } else {
        next.set("status", value)
      }
      next.set("page", "1")
      return next
    })
  }

  function handlePoliticianChange(value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === "__all__") {
        next.delete("politician_id")
      } else {
        next.set("politician_id", value)
      }
      next.set("page", "1")
      return next
    })
  }

  function handleElectionChange(value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === "__all__") {
        next.delete("election_id")
      } else {
        next.set("election_id", value)
      }
      next.set("page", "1")
      return next
    })
  }

  function handleDateChange(param: string, value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value) {
        next.set(param, value)
      } else {
        next.delete(param)
      }
      next.set("page", "1")
      return next
    })
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Բոլոր խոստումները</h1>

      {/* Filter row */}
      <div className="flex flex-wrap gap-4 mb-6">
        {/* Status filter */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Կարգավիճակ</label>
          <Select value={status ?? "__all__"} onValueChange={handleStatusChange}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Բոլոր կարգավիճակները</SelectItem>
              {STATUS_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Politician filter */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Քաղաքական գործիչ</label>
          <Select value={politician_id ?? "__all__"} onValueChange={handlePoliticianChange}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Բոլոր անձինք</SelectItem>
              {politiciansData?.items.map((p) => (
                <SelectItem key={p.id} value={p.id}>
                  {p.name_hy}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Election filter */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Ընտրություն</label>
          <Select value={election_id ?? "__all__"} onValueChange={handleElectionChange}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Բոլոր ընտրությունները</SelectItem>
              {electionsData?.items.map((e) => (
                <SelectItem key={e.id} value={e.id}>
                  {e.name_hy}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Made date range */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Ստեղծված ից</label>
          <Input
            type="date"
            className="w-36"
            value={made_date_from ?? ""}
            onChange={(e) => handleDateChange("made_date_from", e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Ստեղծված մինչ</label>
          <Input
            type="date"
            className="w-36"
            value={made_date_to ?? ""}
            onChange={(e) => handleDateChange("made_date_to", e.target.value)}
          />
        </div>

        {/* Expected date range */}
        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Ժամկետ ից</label>
          <Input
            type="date"
            className="w-36"
            value={expected_date_from ?? ""}
            onChange={(e) => handleDateChange("expected_date_from", e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Ժամկետ մինչ</label>
          <Input
            type="date"
            className="w-36"
            value={expected_date_to ?? ""}
            onChange={(e) => handleDateChange("expected_date_to", e.target.value)}
          />
        </div>
      </div>

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 rounded animate-pulse" aria-hidden="true" />
          ))}
        </div>
      )}

      {/* Error state */}
      {isError && (
        <div className="flex flex-col items-center gap-4 py-16 text-center">
          <AlertCircle className="w-8 h-8 text-red-500" />
          <p className="text-zinc-700">Տվյալները բեռնելու ժամանակ սխալ է տեղի ունեցել</p>
          <p className="text-sm text-zinc-500">Կրկին փորձեք կամ թարմացրեք էջը</p>
        </div>
      )}

      {/* Data state */}
      {!isLoading && !isError && data && (
        <>
          {data.items.length === 0 ? (
            <div className="flex flex-col items-center gap-4 py-16 text-center">
              <h2 className="text-lg font-semibold text-zinc-900">Խոստումներ չեն գտնվել</h2>
              <p className="text-sm text-zinc-500">Փոխեք ֆիլտրի կարգավորումները</p>
            </div>
          ) : (
            <>
              <div className="space-y-0">
                {data.items.map((promise) => (
                  <PromiseCard key={promise.id} promise={promise} />
                ))}
              </div>
              {data.pages > 1 && (
                <PaginationControls currentPage={page} totalPages={data.pages} />
              )}
            </>
          )}
        </>
      )}
    </main>
  )
}
