const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(API_BASE + path)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json() as Promise<T>
  },
}

export { apiClient }
