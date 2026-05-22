import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PartyListItemOut } from "@/types"

export function useParties() {
  const { data, isLoading, isError } = useQuery<PartyListItemOut[]>({
    queryKey: ["parties"],
    queryFn: () => apiClient.get<PartyListItemOut[]>("/api/parties"),
  })

  return { data, isLoading, isError }
}
