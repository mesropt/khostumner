import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PromiseStubOut } from "@/types"

interface UsePoliticianPromisesParams {
  slug: string
  page: number
  perPage?: number
}

export function usePoliticianPromises({ slug, page, perPage = 10 }: UsePoliticianPromisesParams) {
  const { data, isLoading, isError } = useQuery<PaginatedResponse<PromiseStubOut>>({
    queryKey: ["politician-promises", slug, { page, perPage }],
    queryFn: () =>
      apiClient.get<PaginatedResponse<PromiseStubOut>>(
        `/api/politicians/${slug}/promises?page=${page}&per_page=${perPage}`
      ),
    placeholderData: keepPreviousData,
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
