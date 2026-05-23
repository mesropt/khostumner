import { describe, it, expect, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { MemoryRouter, Routes, Route } from "react-router-dom"
import { AuthContext } from "@/contexts/AuthContext"
import type { UserRead } from "@/contexts/AuthContext"
import RequireAuth from "./RequireAuth"
import type { ReactNode } from "react"

const mockUser: UserRead = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  email: "test@example.com",
  display_name: "Test User",
  is_active: true,
  is_verified: true,
  role: "registered",
}

function makeWrapper(state: { user: UserRead | null; isLoading: boolean }, children: ReactNode) {
  return (
    <AuthContext.Provider value={{ state, dispatch: vi.fn() }}>
      {children}
    </AuthContext.Provider>
  )
}

describe("RequireAuth", () => {
  it("when isLoading=true, renders loading spinner (not Navigate)", () => {
    const { container } = render(
      makeWrapper(
        { user: null, isLoading: true },
        <MemoryRouter initialEntries={["/protected"]}>
          <Routes>
            <Route element={<RequireAuth />}>
              <Route path="/protected" element={<div>Protected Content</div>} />
            </Route>
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </MemoryRouter>
      )
    )

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument()
    expect(screen.queryByText("Login Page")).not.toBeInTheDocument()
    // Loading spinner should be present (animate-pulse class)
    const spinner = container.querySelector(".animate-pulse")
    expect(spinner).toBeInTheDocument()
  })

  it("when user=null and isLoading=false, renders Navigate to /login with state.from=location", () => {
    render(
      makeWrapper(
        { user: null, isLoading: false },
        <MemoryRouter initialEntries={["/protected"]}>
          <Routes>
            <Route element={<RequireAuth />}>
              <Route path="/protected" element={<div>Protected Content</div>} />
            </Route>
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </MemoryRouter>
      )
    )

    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument()
    expect(screen.getByText("Login Page")).toBeInTheDocument()
  })

  it("when user is set, renders Outlet", () => {
    render(
      makeWrapper(
        { user: mockUser, isLoading: false },
        <MemoryRouter initialEntries={["/protected"]}>
          <Routes>
            <Route element={<RequireAuth />}>
              <Route path="/protected" element={<div>Protected Content</div>} />
            </Route>
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </MemoryRouter>
      )
    )

    expect(screen.getByText("Protected Content")).toBeInTheDocument()
    expect(screen.queryByText("Login Page")).not.toBeInTheDocument()
  })
})
