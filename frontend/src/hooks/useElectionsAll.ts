import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { ElectionOut, ElectionWithCountOut, PaginatedResponse } from "@/types"

/**
 * Loads all elections once on mount (per_page=100) for client-side level filtering.
 * Used by the cascading election picker on the promise submission form.
 * Per CONTEXT.md D-15: election list is ≤20 items in v1; client-side filtering is sufficient.
 */
export function useElectionsAll() {
  const { data, isLoading } = useQuery<PaginatedResponse<ElectionWithCountOut>>({
    queryKey: ["elections-all"],
    queryFn: () =>
      apiClient.get<PaginatedResponse<ElectionWithCountOut>>(
        "/api/elections?page=1&per_page=100"
      ),
    staleTime: 5 * 60 * 1000, // 5 minutes — elections list changes rarely
  })

  // Strip promise_count — consumers only need ElectionOut fields
  const elections: ElectionOut[] = (data?.items ?? []).map(
    ({ promise_count: _pc, ...election }) => election
  )

  return { elections, isLoading }
}
