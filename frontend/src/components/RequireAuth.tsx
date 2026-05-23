import { Navigate, Outlet, useLocation } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"

export default function RequireAuth() {
  const { state } = useAuth()
  const location = useLocation()

  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="h-8 w-8 bg-zinc-200 rounded-full animate-pulse" />
      </div>
    )
  }

  if (!state.user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
