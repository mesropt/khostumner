import { useState } from "react"
import { Link } from "react-router-dom"
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

export default function RegisterPage() {
  const [displayName, setDisplayName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (password !== confirmPassword) {
      setError("Գաղտնաբառերը չեն համընկնում")
      return
    }

    setIsSubmitting(true)

    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "x-csrftoken": getCsrfToken(),
        },
        body: JSON.stringify({
          email,
          password,
          display_name: displayName,
        }),
      })

      if (res.status === 201) {
        setSuccess(true)
      } else if (res.status === 400) {
        setError("Այս էլ. հասցեն արդեն գրանցված է")
      } else {
        setError("Գրանցման ժամանակ սխալ է տեղի ունեցել")
      }
    } catch {
      setError("Գրանցման ժամանակ սխալ է տեղի ունեցել")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (success) {
    return (
      <main className="max-w-md mx-auto px-4 py-16">
        <Card>
          <CardContent className="pt-6">
            <p className="text-zinc-700 text-center">
              Շնորհակալություն։ Ստուգեք Ձեր փոստը հաստատման հղման համար
            </p>
            <p className="text-sm text-zinc-500 mt-4 text-center">
              <Link to="/login" className="text-blue-600 underline">
                Մուտք
              </Link>
            </p>
          </CardContent>
        </Card>
      </main>
    )
  }

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <Card>
        <CardHeader>
          <CardTitle>Գրանցվել</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="text"
              placeholder="Անուն"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              required
            />
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
            <Input
              type="password"
              placeholder="Կրկնեք գաղտնաբառը"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "..." : "Գրանցվել"}
            </Button>
          </form>
          <p className="text-sm text-zinc-500 mt-4 text-center">
            Արդեն հաշիվ ունե՞ք{" "}
            <Link to="/login" className="text-blue-600 underline">
              Մուտք
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
