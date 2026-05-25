import { useEffect, useRef, useState } from "react"
import { useSearchParams, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

function getCsrfToken(): string {
  return (
    document.cookie
      .split("; ")
      .find((r) => r.startsWith("csrftoken="))
      ?.split("=")[1] ?? ""
  )
}

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")

  const token = searchParams.get("token")
  const attempted = useRef(false)

  useEffect(() => {
    if (!token) {
      setStatus("error")
      return
    }
    // Guard against React StrictMode double-invocation — token is one-time-use.
    if (attempted.current) return
    attempted.current = true

    fetch(`${API_BASE}/api/auth/verify`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "x-csrftoken": getCsrfToken(),
      },
      body: JSON.stringify({ token }),
    })
      .then(async (res) => {
        if (res.ok) {
          setStatus("success")
          return
        }
        // VERIFY_USER_ALREADY_VERIFIED means a prior request (e.g. StrictMode double-effect)
        // already consumed the token successfully — treat it as success.
        const body = await res.json().catch(() => ({}))
        if (body?.detail === "VERIFY_USER_ALREADY_VERIFIED") {
          setStatus("success")
        } else {
          setStatus("error")
        }
      })
      .catch(() => {
        setStatus("error")
      })
  }, [token])

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <Card>
        <CardHeader>
          <CardTitle>Էլ. հասցեի հաստատում</CardTitle>
        </CardHeader>
        <CardContent>
          {status === "loading" && (
            <div className="flex items-center gap-3 py-4">
              <div className="h-5 w-5 bg-zinc-200 rounded-full animate-pulse" />
              <p className="text-zinc-600">Ստուգվում է...</p>
            </div>
          )}
          {status === "success" && (
            <div className="space-y-4">
              <p className="text-zinc-700">Ձեր հաշիվը հաստատվել է</p>
              <Link to="/login" className="text-blue-600 underline text-sm">
                Մուտք
              </Link>
            </div>
          )}
          {status === "error" && (
            <p className="text-red-600">
              Հաստատման հղումն անվավեր է կամ ժամկետանց
            </p>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
