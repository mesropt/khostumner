import { Link, useParams, useSearchParams } from "react-router-dom"
import Avatar from "@/components/Avatar"
import PoliticianCard from "@/components/PoliticianCard"
import PromiseStub from "@/components/PromiseStub"
import PaginationControls from "@/components/PaginationControls"
import { useParty } from "@/hooks/useParty"
import { usePartyPoliticians } from "@/hooks/usePartyPoliticians"
import { usePartyPromises } from "@/hooks/usePartyPromises"

export default function PartyPage() {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams] = useSearchParams()

  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1

  const { data, isLoading, isError } = useParty(slug!)
  const { data: politiciansData, isLoading: politiciansLoading } = usePartyPoliticians(slug!)
  const { data: promisesData, isLoading: promisesLoading } = usePartyPromises({
    slug: slug!,
    page,
  })

  // Loading skeleton
  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex flex-col items-center gap-4 animate-pulse">
          <div className="w-16 h-16 rounded-full bg-zinc-200" />
          <div className="h-6 w-48 bg-zinc-200 rounded" />
          <div className="h-4 w-32 bg-zinc-200 rounded" />
        </div>
        <div className="mt-8 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-200 rounded animate-pulse" />
          ))}
        </div>
      </main>
    )
  }

  // 404 or error
  if (isError || !data) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-4">Կուսակցությունը չի գտնվել</h1>
        <Link to="/persons" className="text-blue-600 underline hover:text-blue-800 text-sm">
          Վերադառնալ անձանց ցուցակ
        </Link>
      </main>
    )
  }

  const memberCount = politiciansData?.length ?? 0

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      {/* Header section */}
      <div className="flex flex-col items-center text-center gap-3 mb-6">
        <Avatar
          photoUrl={data.logo_url}
          nameHy={data.short_name_hy ?? data.name_hy}
          size="md"
        />
        <h1 className="text-2xl font-semibold text-zinc-900">{data.name_hy}</h1>
        {data.founded_year && (
          <p className="text-sm text-zinc-500">Հիմնվել է {data.founded_year} թ.</p>
        )}
      </div>

      {/* Members section */}
      <section className="mt-8">
        <h2 className="text-xl font-semibold text-zinc-900 mt-8 mb-4">Անդամներ</h2>

        {politiciansLoading && (
          <div className="flex gap-3 overflow-x-auto pb-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="w-32 h-36 bg-zinc-200 rounded animate-pulse flex-shrink-0" />
            ))}
          </div>
        )}

        {!politiciansLoading && politiciansData && (
          <>
            {politiciansData.length === 0 ? (
              <p className="text-sm text-zinc-500 py-4 text-center">Անդամներ չեն գտնվել</p>
            ) : memberCount <= 6 ? (
              <div className="flex flex-wrap gap-3">
                {politiciansData.map((politician) => (
                  <div key={politician.id} className="w-36">
                    <PoliticianCard politician={politician} />
                  </div>
                ))}
              </div>
            ) : (
              <ul className="divide-y divide-zinc-100">
                {politiciansData.map((politician) => (
                  <li key={politician.id}>
                    <Link
                      to={`/persons/${politician.slug}`}
                      className="flex items-center justify-between py-3 hover:bg-zinc-50 px-2 rounded"
                    >
                      <span className="text-sm font-medium text-zinc-900">{politician.name_hy}</span>
                      {politician.position && (
                        <span className="text-xs text-zinc-500 ml-4">{politician.position}</span>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>

      {/* Promises section */}
      <section className="mt-8">
        <h2 className="text-xl font-semibold text-zinc-900 mt-8 mb-4">Խոստումներ</h2>

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
              <PaginationControls
                currentPage={page}
                totalPages={promisesData.pages}
              />
            )}
          </>
        )}
      </section>
    </main>
  )
}
