const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export function getCsrfToken(): string {
  return (
    document.cookie
      .split("; ")
      .find((r) => r.startsWith("csrftoken="))
      ?.split("=")[1] ?? ""
  )
}

const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(API_BASE + path, { credentials: "include" })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json() as Promise<T>
  },

  async post<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(API_BASE + path, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "x-csrftoken": getCsrfToken(),
      },
      body: JSON.stringify(body),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw { status: response.status, detail: (err as { detail?: string }).detail ?? "Unknown error" }
    }
    return response.json() as Promise<T>
  },

  async put<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(API_BASE + path, {
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "x-csrftoken": getCsrfToken(),
      },
      body: JSON.stringify(body),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw { status: response.status, detail: (err as { detail?: string }).detail ?? "Unknown error" }
    }
    return response.json() as Promise<T>
  },
}

export { apiClient }
