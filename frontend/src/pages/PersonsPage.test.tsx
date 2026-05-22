import { describe, it, expect } from "vitest"
import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import PersonsPage from "./PersonsPage"

function renderPersonsPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <PersonsPage />
      </QueryClientProvider>
    </MemoryRouter>
  )
}

describe("PersonsPage", () => {
  it("renders without crashing", () => {
    const { container } = renderPersonsPage()
    expect(container).toBeTruthy()
  })
})
