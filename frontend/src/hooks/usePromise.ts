import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PromiseDetailOut } from "@/types"

export function usePromise(slug: string) {
  const { data, isLoading, isError } = useQuery<PromiseDetailOut>({
    queryKey: ["promise", slug],
    queryFn: () => apiClient.get<PromiseDetailOut>(`/api/promises/${slug}`),
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}