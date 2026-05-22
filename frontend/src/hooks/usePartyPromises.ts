import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PromiseStubOut } from "@/types"

interface UsePartyPromisesParams {
  slug: string
  page: number
  perPage?: number
}

export function usePartyPromises({ slug, page, perPage = 20 }: UsePartyPromisesParams) {
  const { data, isLoading, isError } = useQuery<PaginatedResponse<PromiseStubOut>>({
    queryKey: ["party-promises", slug, { page, perPage }],
    queryFn: () =>
      apiClient.get<PaginatedResponse<PromiseStubOut>>(
        `/api/parties/${slug}/promises?page=${page}&per_page=${perPage}`
      ),
    placeholderData: keepPreviousData,
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
