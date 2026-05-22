import { Link, useParams, useSearchParams } from "react-router-dom"
import Avatar from "@/components/Avatar"
import PromiseStub from "@/components/PromiseStub"
import PaginationControls from "@/components/PaginationControls"
import { usePolitician } from "@/hooks/usePolitician"
import { usePoliticianPromises } from "@/hooks/usePoliticianPromises"

export default function PoliticianProfilePage() {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams] = useSearchParams()

  const promisePage = parseInt(searchParams.get("ppage") ?? "1", 10) || 1

  const { data, isLoading, isError } = usePolitician(slug!)
  const {
    data: promisesData,
    isLoading: promisesLoading,
  } = usePoliticianPromises({ slug: slug!, page: promisePage })

  // Loading skeleton
  if (isLoading) {
    return (
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex flex-col items-center gap-4 animate-pulse">
          <div className="w-24 h-24 rounded-full bg-zinc-200" />
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
        <h1 className="text-2xl font-semibold text-zinc-900 mb-4">Պերսոնը չի գտնվել</h1>
        <Link to="/persons" className="text-blue-600 underline hover:text-blue-800 text-sm">
          Վերադառնալ պերսոնների ցուցակ
        </Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      {/* Hero section */}
      <div className="flex flex-col items-center text-center gap-3 mb-6">
        <Avatar photoUrl={data.photo_url} nameHy={data.name_hy} size="lg" />
        <h1 className="text-2xl font-semibold text-zinc-900">{data.name_hy}</h1>
        {data.position && <p className="text-sm text-zinc-500">{data.position}</p>}
      </div>

      {/* Bio */}
      {data.bio_hy && (
        <p className="text-sm text-zinc-700 max-w-prose mt-4 mx-auto">{data.bio_hy}</p>
      )}

      {/* Promises section */}
      <section className="mt-8">
        <h2 className="text-xl font-semibold text-zinc-900 mb-4">Խոստումներ</h2>

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
              <p className="text-sm text-zinc-500 py-8 text-center">
                Խոստումներ չեն գտնվել
              </p>
            ) : (
              <div>
                {promisesData.items.map((promise) => (
                  <PromiseStub key={promise.id} promise={promise} />
                ))}
              </div>
            )}

            {promisesData.pages > 1 && (
              <PaginationControls
                currentPage={promisePage}
                totalPages={promisesData.pages}
                pageParamKey="ppage"
              />
            )}
          </>
        )}
      </section>
    </main>
  )
}
