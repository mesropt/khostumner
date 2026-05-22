import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PoliticianOut } from "@/types"

export function usePolitician(slug: string) {
  const { data, isLoading, isError } = useQuery<PoliticianOut>({
    queryKey: ["politician", slug],
    queryFn: () => apiClient.get<PoliticianOut>(`/api/politicians/${slug}`),
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
