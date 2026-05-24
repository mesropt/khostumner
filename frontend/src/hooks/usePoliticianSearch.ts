import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PoliticianOut } from "@/types"

/**
 * Loads all politicians once on mount (per_page=100) for client-side filtering.
 * Used by the Combobox politician picker on the promise submission form.
 * Per RESEARCH.md open question resolution (D-11): client-side filter is sufficient
 * for v1 politician counts.
 */
export function usePoliticianSearch() {
  const { data, isLoading } = useQuery<PaginatedResponse<PoliticianOut>>({
    queryKey: ["politicians-all"],
    queryFn: () =>
      apiClient.get<PaginatedResponse<PoliticianOut>>(
        "/api/politicians?page=1&per_page=100"
      ),
    staleTime: 5 * 60 * 1000, // 5 minutes — politician list changes rarely
  })

  const politicians: PoliticianOut[] = data?.items ?? []

  return { politicians, isLoading }
}
