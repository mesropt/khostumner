import { useEffect, useState } from "react"
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

  useEffect(() => {
    const token = searchParams.get("token")

    if (!token) {
      setStatus("error")
      return
    }

    fetch(`${API_BASE}/api/auth/verify`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "x-csrftoken": getCsrfToken(),
      },
      body: JSON.stringify({ token }),
    })
      .then((res) => {
        if (res.ok) {
          setStatus("success")
        } else {
          setStatus("error")
        }
      })
      .catch(() => {
        setStatus("error")
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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
