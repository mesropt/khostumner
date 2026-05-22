import { useSearchParams } from "react-router-dom"
import { AlertCircle } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import PoliticianCard from "@/components/PoliticianCard"
import PaginationControls from "@/components/PaginationControls"
import { usePoliticians } from "@/hooks/usePoliticians"
import { useParties } from "@/hooks/useParties"

const LEVEL_OPTIONS = [
  { value: "national", label: "Ազգային" },
  { value: "local", label: "Տեղական" },
  { value: "party", label: "Կուսակցական" },
]

export default function PersonsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1
  const party = searchParams.get("party") || null
  const level = searchParams.get("level") || null

  const { data, isLoading, isError } = usePoliticians({ page, party, level })
  const { data: partiesData } = useParties()

  function handlePartyChange(value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === "__all__") {
        next.delete("party")
      } else {
        next.set("party", value)
      }
      next.set("page", "1")
      return next
    })
  }

  function handleLevelChange(value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === "__all__") {
        next.delete("level")
      } else {
        next.set("level", value)
      }
      next.set("page", "1")
      return next
    })
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Անձինք</h1>

      {/* Filter row */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Կուսակցություն</label>
          <Select value={party ?? "__all__"} onValueChange={handlePartyChange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Բոլոր կուսակցությունները" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Բոլոր կուսակցությունները</SelectItem>
              {partiesData?.map((p) => (
                <SelectItem key={p.id} value={p.id}>
                  {p.name_hy}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-zinc-500 font-medium">Մակարդակ</label>
          <Select value={level ?? "__all__"} onValueChange={handleLevelChange}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Բոլոր մակարդակները" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Բոլոր մակարդակները</SelectItem>
              {LEVEL_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Loading skeleton */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="rounded-lg border bg-zinc-200 animate-pulse h-40"
              aria-hidden="true"
            />
          ))}
        </div>
      )}

      {/* Error state */}
      {isError && (
        <div className="flex flex-col items-center gap-4 py-16 text-center">
          <AlertCircle className="w-8 h-8 text-red-500" />
          <p className="text-zinc-700">Տվյալները բեռնելու ժամանակ սխալ է տեղի ունեցել</p>
          <a
            href="/persons"
            className="text-sm text-blue-600 underline hover:text-blue-800"
          >
            Կրկին փորձել
          </a>
        </div>
      )}

      {/* Data state */}
      {!isLoading && !isError && data && (
        <>
          {data.items.length === 0 ? (
            <div className="flex flex-col items-center gap-4 py-16 text-center">
              <h2 className="text-lg font-semibold text-zinc-900">
                Ոչ մի անձ չի գտնվել
              </h2>
              <p className="text-sm text-zinc-500">
                Փոխեք ֆիլտրի կարգավորումները...
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {data.items.map((politician) => (
                  <PoliticianCard key={politician.id} politician={politician} />
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
