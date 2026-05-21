import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import App from "./App"

function renderWithProviders(initialPath = "/") {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </MemoryRouter>
  )
}

describe("App", () => {
  it("renders without crashing", () => {
    renderWithProviders()
    expect(document.body).not.toBeNull()
  })

  it("renders homepage heading", () => {
    renderWithProviders("/")
    expect(screen.getByText("Խոստումներ")).toBeInTheDocument()
  })
})
