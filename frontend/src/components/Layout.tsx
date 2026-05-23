import { NavLink, Outlet, useNavigate } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export default function Layout() {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? "text-sm font-semibold text-zinc-900"
      : "text-sm text-zinc-600 hover:text-zinc-900"

  const { state, dispatch } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    const csrfToken =
      document.cookie
        .split("; ")
        .find((r) => r.startsWith("csrftoken="))
        ?.split("=")[1] ?? ""
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: "POST",
      credentials: "include",
      headers: { "x-csrftoken": csrfToken },
    })
    dispatch({ type: "CLEAR_USER" })
    navigate("/")
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="sticky top-0 z-10 bg-white border-b border-zinc-200">
        <nav className="max-w-7xl mx-auto px-4 flex items-center gap-6 h-14">
          <NavLink to="/" className={navLinkClass} end>
            <span className="font-bold text-lg text-zinc-900">Խոստումներ</span>
          </NavLink>
          <NavLink to="/fulfilled" className={navLinkClass}>
            Կատարված
          </NavLink>
          <NavLink to="/unfulfilled" className={navLinkClass}>
            Չկատարված
          </NavLink>
          <NavLink to="/persons" className={navLinkClass}>
            Անձինք
          </NavLink>
          <NavLink to="/elections" className={navLinkClass}>
            Ընտրություններ
          </NavLink>
          <NavLink to="/about" className={navLinkClass}>
            Մեր մասին
          </NavLink>
          <div className="ml-auto flex items-center gap-4">
            {state.user ? (
              <>
                <span className="text-sm text-zinc-600">{state.user.display_name}</span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-zinc-600 hover:text-zinc-900"
                >
                  Ելք
                </button>
              </>
            ) : (
              <NavLink to="/login" className={navLinkClass}>
                Մուտք
              </NavLink>
            )}
          </div>
        </nav>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
