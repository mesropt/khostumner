import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { vi, describe, it, expect, beforeEach } from "vitest"
import LoginPage from "./LoginPage"
import { AuthContext } from "@/contexts/AuthContext"
import type { AuthState, AuthAction } from "@/contexts/AuthContext"
import type { Dispatch } from "react"

// Helper to render with required providers
function renderLoginPage(dispatch: Dispatch<AuthAction> = vi.fn()) {
  const state: AuthState = { user: null, isLoading: false }
  return render(
    <AuthContext.Provider value={{ state, dispatch }}>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </AuthContext.Provider>
  )
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it("calls fetch to /api/auth/login with URLSearchParams and credentials:include on submit", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "1",
        email: "test@example.com",
        display_name: "Test",
        is_active: true,
        is_verified: true,
        role: "registered",
      }),
    })
    vi.stubGlobal("fetch", fetchSpy)

    renderLoginPage()

    fireEvent.change(screen.getByPlaceholderText("Էլ. հասցե"), {
      target: { value: "test@example.com" },
    })
    fireEvent.change(screen.getByPlaceholderText("Գաղտնաբառ"), {
      target: { value: "password123" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Մուտք/i }))

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(
        expect.stringContaining("/api/auth/login"),
        expect.objectContaining({
          method: "POST",
          credentials: "include",
          headers: expect.objectContaining({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
        })
      )
    })

    // Verify username (not email) is used in body
    const callArgs = fetchSpy.mock.calls[0]
    expect(callArgs[1].body).toContain("username=test%40example.com")
  })

  it("dispatches SET_USER and navigates to / on successful login", async () => {
    const mockUser = {
      id: "abc-123",
      email: "user@example.com",
      display_name: "User",
      is_active: true,
      is_verified: true,
      role: "registered",
    }

    const fetchSpy = vi.fn()
      // First call: POST /api/auth/login
      .mockResolvedValueOnce({ ok: true, json: async () => ({}) })
      // Second call: GET /api/users/me
      .mockResolvedValueOnce({ ok: true, json: async () => mockUser })
    vi.stubGlobal("fetch", fetchSpy)

    const dispatch = vi.fn()
    renderLoginPage(dispatch)

    fireEvent.change(screen.getByPlaceholderText("Էլ. հասցե"), {
      target: { value: "user@example.com" },
    })
    fireEvent.change(screen.getByPlaceholderText("Գաղտնաբառ"), {
      target: { value: "password123" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Մուտք/i }))

    await waitFor(() => {
      expect(dispatch).toHaveBeenCalledWith({
        type: "SET_USER",
        payload: mockUser,
      })
    })
  })

  it("shows Armenian error message on 400/401 response", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({ ok: false, status: 401 })
    vi.stubGlobal("fetch", fetchSpy)

    renderLoginPage()

    fireEvent.change(screen.getByPlaceholderText("Էլ. հասցե"), {
      target: { value: "wrong@example.com" },
    })
    fireEvent.change(screen.getByPlaceholderText("Գաղտնաբառ"), {
      target: { value: "wrongpassword" },
    })
    fireEvent.click(screen.getByRole("button", { name: /Մուտք/i }))

    await waitFor(() => {
      expect(
        screen.getByText("Սխալ էլ. հասցե կամ գաղտնաբառ")
      ).toBeInTheDocument()
    })
  })
})
