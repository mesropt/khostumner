import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { ElectionWithCountOut, PaginatedResponse } from "@/types"

export function useElections(page: number = 1) {
  const { data, isLoading, isError } = useQuery<PaginatedResponse<ElectionWithCountOut>>({
    queryKey: ["elections", { page }],
    queryFn: () =>
      apiClient.get<PaginatedResponse<ElectionWithCountOut>>(`/api/elections?page=${page}`),
    placeholderData: keepPreviousData,
  })

  return { data, isLoading, isError }
}
