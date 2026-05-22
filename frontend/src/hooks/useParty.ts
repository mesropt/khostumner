import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PartyOut } from "@/types"

export function useParty(slug: string) {
  const { data, isLoading, isError } = useQuery<PartyOut>({
    queryKey: ["party", slug],
    queryFn: () => apiClient.get<PartyOut>(`/api/parties/${slug}`),
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
