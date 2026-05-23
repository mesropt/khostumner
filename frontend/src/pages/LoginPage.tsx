import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

function getCsrfToken(): string {
  return (
    document.cookie
      .split("; ")
      .find((r) => r.startsWith("csrftoken="))
      ?.split("=")[1] ?? ""
  )
}

export default function LoginPage() {
  const { dispatch } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    // FastAPI-Users login uses OAuth2PasswordRequestForm — must use username (not email)
    const body = new URLSearchParams({ username: email, password })

    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "x-csrftoken": getCsrfToken(),
        },
        body: body.toString(),
      })

      if (res.ok) {
        // Fetch user profile after successful login
        const me = await fetch(`${API_BASE}/api/users/me`, {
          credentials: "include",
        }).then((r) => r.json())
        dispatch({ type: "SET_USER", payload: me })
        navigate("/")
      } else {
        setError("Սխալ էլ. հասցե կամ գաղտնաբառ")
      }
    } catch {
      setError("Սխալ էլ. հասցե կամ գաղտնաբառ")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <Card>
        <CardHeader>
          <CardTitle>Մուտք</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              placeholder="Էլ. հասցե"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Գաղտնաբառ"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "..." : "Մուտք"}
            </Button>
          </form>
          <p className="text-sm text-zinc-500 mt-4 text-center">
            Հաշիվ չունե՞ք{" "}
            <Link to="/register" className="text-blue-600 underline">
              Գրանցվել
            </Link>
          </p>
          <p className="text-sm text-zinc-500 mt-2 text-center">
            <Link to="/reset-password" className="text-blue-600 underline">
              Մոռացե՞լ եք գաղտնաբառը
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
