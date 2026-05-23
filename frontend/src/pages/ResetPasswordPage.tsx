import { useState } from "react"
import { useSearchParams, useNavigate, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

function getCsrfToken(): string {
  return (
    document.cookie
      .split("; ")
      .find((r) => r.startsWith("csrftoken="))
      ?.split("=")[1] ?? ""
  )
}

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get("token")
  const [step] = useState<"request" | "reset">(token ? "reset" : "request")

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleRequestSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setIsSubmitting(true)

    try {
      await fetch(`${API_BASE}/api/auth/forgot-password`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "x-csrftoken": getCsrfToken(),
        },
        body: JSON.stringify({ email }),
      })
      // Always show the same message regardless of whether email exists (anti-enumeration)
      setMessage(
        "Եթե այդ հասցեն գրանցված է, ստուգեք Ձեր փոստը"
      )
    } catch {
      setError("Սխալ է տեղի ունեցել, խնդրում ենք փորձել կրկին")
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleResetSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)

    if (password !== confirmPassword) {
      setError("Գաղտնաբառերը չեն համընկնում")
      return
    }

    setIsSubmitting(true)

    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "x-csrftoken": getCsrfToken(),
        },
        body: JSON.stringify({ token, password }),
      })

      if (res.ok) {
        setMessage("Գաղտնաբառը հաջողությամբ փոխվել է")
        setTimeout(() => navigate("/login"), 2000)
      } else {
        setError("Վերականգնման հղումն անվավեր է կամ ժամկետանց")
      }
    } catch {
      setError("Սխալ է տեղի ունեցել, խնդրում ենք փորձել կրկին")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <Card>
        <CardHeader>
          <CardTitle>Գաղտնաբառի վերականգնում</CardTitle>
        </CardHeader>
        <CardContent>
          {step === "request" ? (
            <form onSubmit={handleRequestSubmit} className="space-y-4">
              <Input
                type="email"
                placeholder="Էլ. հասցե"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              {error && <p className="text-sm text-red-600">{error}</p>}
              {message && <p className="text-sm text-zinc-700">{message}</p>}
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "..." : "Ուղարկել"}
              </Button>
              <p className="text-sm text-zinc-500 text-center">
                <Link to="/login" className="text-blue-600 underline">
                  Վերադառնալ Մուտք
                </Link>
              </p>
            </form>
          ) : (
            <form onSubmit={handleResetSubmit} className="space-y-4">
              <Input
                type="password"
                placeholder="Նոր գաղտնաբառ"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Input
                type="password"
                placeholder="Կրկնեք գաղտնաբառը"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              {error && <p className="text-sm text-red-600">{error}</p>}
              {message && <p className="text-sm text-zinc-700">{message}</p>}
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "..." : "Հաստատել"}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
