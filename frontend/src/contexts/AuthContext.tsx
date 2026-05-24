import {
  createContext,
  useReducer,
  useEffect,
  type Dispatch,
  type ReactNode,
} from "react"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export type UserRead = {
  id: string
  email: string
  display_name: string
  is_active: boolean
  is_verified: boolean
  role: string
  account_age_days: number
}

export type AuthState = {
  user: UserRead | null
  isLoading: boolean
}

export type AuthAction =
  | { type: "SET_USER"; payload: UserRead }
  | { type: "CLEAR_USER" }
  | { type: "SET_LOADING"; payload: boolean }

export function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "SET_USER":
      return { ...state, user: action.payload, isLoading: false }
    case "CLEAR_USER":
      return { ...state, user: null, isLoading: false }
    case "SET_LOADING":
      return { ...state, isLoading: action.payload }
    default:
      return state
  }
}

export const AuthContext = createContext<{
  state: AuthState
  dispatch: Dispatch<AuthAction>
} | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, { user: null, isLoading: true })

  useEffect(() => {
    async function rehydrate() {
      // Step 1: GET /api/users/me — browser sends httpOnly access cookie automatically
      const meRes = await fetch(`${API_BASE}/api/users/me`, { credentials: "include" })
      if (meRes.ok) {
        const user = await meRes.json()
        dispatch({ type: "SET_USER", payload: user })
        return
      }

      // Step 2: Access token expired — try refresh
      if (meRes.status === 401) {
        const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
          method: "POST",
          credentials: "include",
        })
        if (refreshRes.ok) {
          // Retry /me with the new access cookie
          const retryRes = await fetch(`${API_BASE}/api/users/me`, { credentials: "include" })
          if (retryRes.ok) {
            const user = await retryRes.json()
            dispatch({ type: "SET_USER", payload: user })
            return
          }
        }
      }

      // Step 3: Both /me and /refresh failed — user is truly logged out
      dispatch({ type: "CLEAR_USER" })
    }

    rehydrate().catch(() => {
      dispatch({ type: "CLEAR_USER" })
    })
  }, [])

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  )
}
