import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { ElectionOut } from "@/types"

export function useElection(slug: string) {
  const { data, isLoading, isError } = useQuery<ElectionOut>({
    queryKey: ["election", slug],
    queryFn: () => apiClient.get<ElectionOut>(`/api/elections/${slug}`),
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
