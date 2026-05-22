import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PoliticianOut } from "@/types"

interface UsePoliticiansParams {
  page: number
  perPage?: number
  party?: string | null
  level?: string | null
}

export function usePoliticians({ page, perPage = 20, party, level }: UsePoliticiansParams) {
  const { data, isLoading, isError } = useQuery<PaginatedResponse<PoliticianOut>>({
    queryKey: ["politicians", { page, perPage, party, level }],
    queryFn: () => {
      const params = new URLSearchParams()
      params.set("page", String(page))
      params.set("per_page", String(perPage))
      if (party) params.set("party", party)
      if (level) params.set("level", level)
      return apiClient.get<PaginatedResponse<PoliticianOut>>(`/api/politicians?${params}`)
    },
    placeholderData: keepPreviousData,
  })

  return { data, isLoading, isError }
}
