import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { HealthResponse } from "@/types"

export function useHealth() {
  const { data, isLoading, isError } = useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: () => apiClient.get<HealthResponse>("/health"),
    retry: 3,
  })

  return {
    status: data?.status ?? null,
    isLoading,
    isError,
  }
}
