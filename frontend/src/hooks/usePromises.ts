import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PromiseListOut } from "@/types"

interface UsePromisesParams {
  page: number
  perPage?: number
  status?: string | null
  politician_id?: string | null
  election_id?: string | null
  made_date_from?: string | null
  made_date_to?: string | null
  expected_date_from?: string | null
  expected_date_to?: string | null
}

export function usePromises({
  page,
  perPage = 20,
  status,
  politician_id,
  election_id,
  made_date_from,
  made_date_to,
  expected_date_from,
  expected_date_to,
}: UsePromisesParams) {
  const { data, isLoading, isError } = useQuery<PaginatedResponse<PromiseListOut>>({
    queryKey: [
      "promises",
      {
        page,
        perPage,
        status,
        politician_id,
        election_id,
        made_date_from,
        made_date_to,
        expected_date_from,
        expected_date_to,
      },
    ],
    queryFn: () => {
      const params = new URLSearchParams()
      params.set("page", String(page))
      params.set("per_page", String(perPage))
      if (status) params.set("status", status)
      if (politician_id) params.set("politician_id", politician_id)
      if (election_id) params.set("election_id", election_id)
      if (made_date_from) params.set("made_date_from", made_date_from)
      if (made_date_to) params.set("made_date_to", made_date_to)
      if (expected_date_from) params.set("expected_date_from", expected_date_from)
      if (expected_date_to) params.set("expected_date_to", expected_date_to)
      return apiClient.get<PaginatedResponse<PromiseListOut>>(`/api/promises?${params}`)
    },
    placeholderData: keepPreviousData,
  })

  return { data, isLoading, isError }
}
