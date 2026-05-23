import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { useContext, type ReactNode } from "react"
import { AuthContext, AuthProvider } from "./AuthContext"
import type { UserRead } from "./AuthContext"

// ---- authReducer unit tests ----
// We test the reducer indirectly by exercising AuthProvider state transitions.
// We also import the reducer directly via re-export (see AuthContext.tsx export).
import { authReducer } from "./AuthContext"

const mockUser: UserRead = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  email: "test@example.com",
  display_name: "Test User",
  is_active: true,
  is_verified: true,
  role: "registered",
}

describe("authReducer", () => {
  it("initial state is { user: null, isLoading: true }", () => {
    const initial = authReducer({ user: null, isLoading: true }, { type: "SET_LOADING", payload: true })
    expect(initial.user).toBeNull()
    expect(initial.isLoading).toBe(true)
  })

  it("SET_USER action sets user payload and isLoading: false", () => {
    const state = authReducer({ user: null, isLoading: true }, { type: "SET_USER", payload: mockUser })
    expect(state.user).toEqual(mockUser)
    expect(state.isLoading).toBe(false)
  })

  it("CLEAR_USER action sets user: null and isLoading: false", () => {
    const state = authReducer({ user: mockUser, isLoading: false }, { type: "CLEAR_USER" })
    expect(state.user).toBeNull()
    expect(state.isLoading).toBe(false)
  })

  it("SET_LOADING action updates isLoading", () => {
    const state = authReducer({ user: null, isLoading: false }, { type: "SET_LOADING", payload: true })
    expect(state.isLoading).toBe(true)
  })
})

// ---- AuthProvider mount tests ----

function wrapper({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>
}

describe("AuthProvider", () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("on 200 from /api/users/me dispatches SET_USER", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockUser),
    })
    vi.stubGlobal("fetch", fetchMock)

    const { result } = renderHook(() => useContext(AuthContext), { wrapper })

    // Wait for the effect to settle
    await act(async () => {
      await new Promise((r) => setTimeout(r, 50))
    })

    expect(result.current?.state.user).toEqual(mockUser)
    expect(result.current?.state.isLoading).toBe(false)
  })

  it("when /api/users/me returns 401, calls POST /api/auth/refresh; if refresh 200, retries /me and dispatches SET_USER", async () => {
    const fetchMock = vi
      .fn()
      // First call: GET /api/users/me -> 401
      .mockResolvedValueOnce({ ok: false, status: 401 })
      // Second call: POST /api/auth/refresh -> 200
      .mockResolvedValueOnce({ ok: true, status: 200 })
      // Third call: GET /api/users/me retry -> 200
      .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve(mockUser) })

    vi.stubGlobal("fetch", fetchMock)

    const { result } = renderHook(() => useContext(AuthContext), { wrapper })

    await act(async () => {
      await new Promise((r) => setTimeout(r, 50))
    })

    expect(fetchMock).toHaveBeenCalledTimes(3)
    expect(result.current?.state.user).toEqual(mockUser)
    expect(result.current?.state.isLoading).toBe(false)
  })

  it("when both /api/users/me and /api/auth/refresh fail, dispatches CLEAR_USER", async () => {
    const fetchMock = vi
      .fn()
      // First call: GET /api/users/me -> 401
      .mockResolvedValueOnce({ ok: false, status: 401 })
      // Second call: POST /api/auth/refresh -> 401
      .mockResolvedValueOnce({ ok: false, status: 401 })

    vi.stubGlobal("fetch", fetchMock)

    const { result } = renderHook(() => useContext(AuthContext), { wrapper })

    await act(async () => {
      await new Promise((r) => setTimeout(r, 50))
    })

    expect(result.current?.state.user).toBeNull()
    expect(result.current?.state.isLoading).toBe(false)
  })
})
