import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PoliticianOut } from "@/types"

export function usePartyPoliticians(slug: string) {
  const { data, isLoading, isError } = useQuery<PoliticianOut[]>({
    queryKey: ["party-politicians", slug],
    queryFn: () => apiClient.get<PoliticianOut[]>(`/api/parties/${slug}/politicians`),
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
