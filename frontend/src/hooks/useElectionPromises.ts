import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PromiseStubOut } from "@/types"

interface UseElectionPromisesParams {
  slug: string
  page: number
  perPage?: number
}

export function useElectionPromises({ slug, page, perPage = 20 }: UseElectionPromisesParams) {
  const { data, isLoading, isError } = useQuery<PaginatedResponse<PromiseStubOut>>({
    queryKey: ["election-promises", slug, { page, perPage }],
    queryFn: () =>
      apiClient.get<PaginatedResponse<PromiseStubOut>>(
        `/api/elections/${slug}/promises?page=${page}&per_page=${perPage}`
      ),
    placeholderData: keepPreviousData,
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
