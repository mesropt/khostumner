import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { StatsOut } from "@/types"

export function useStats() {
  const { data, isLoading, isError } = useQuery<StatsOut>({
    queryKey: ["stats"],
    queryFn: () => apiClient.get<StatsOut>("/api/stats"),
    staleTime: 5 * 60 * 1000, // 5 minutes — stats tolerate minor staleness on homepage
  })

  return { data, isLoading, isError }
}
