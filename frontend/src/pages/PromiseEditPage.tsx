import { useState } from "react"
import { useNavigate, useParams, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useAuth } from "@/hooks/useAuth"
import { useElectionsAll } from "@/hooks/useElectionsAll"
import { usePromise } from "@/hooks/usePromise"
import { apiClient } from "@/api/client"

type ElectionLevel = "national" | "local" | "referendum"

interface PromiseEditIn {
  title_hy: string
  quote_hy: string
  source_url: string
  made_date: string | null
  expected_date: string | null
  description_hy: string | null
  election_ids: string[]
}

function EditForm({ slug, initialData }: {
  slug: string
  initialData: {
    title_hy: string
    quote_hy: string
    source_url: string
    made_date: string | null
    expected_date: string | null
    description_hy: string | null
    politician_name_hy: string
  }
}) {
  const navigate = useNavigate()
  const { state } = useAuth()
  const user = state.user

  const { elections, isLoading: electionsLoading } = useElectionsAll()

  // Form field state — initialized from existing promise data
  const [title_hy, setTitleHy] = useState(initialData.title_hy)
  const [quote_hy, setQuoteHy] = useState(initialData.quote_hy)
  const [source_url, setSourceUrl] = useState(initialData.source_url)
  const [made_date, setMadeDate] = useState(initialData.made_date ?? "")
  const [expected_date, setExpectedDate] = useState(initialData.expected_date ?? "")
  const [description_hy, setDescriptionHy] = useState(initialData.description_hy ?? "")

  // Election picker state — starts unchecked; user can newly link elections
  const [linkElections, setLinkElections] = useState(false)
  const [selectedLevel, setSelectedLevel] = useState<ElectionLevel | "">("")
  const [selectedElectionIds, setSelectedElectionIds] = useState<string[]>([])

  // Error and submit state
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const isEligible = !!user && user.is_verified && user.account_age_days >= 7

  const filteredElections =
    selectedLevel !== ""
      ? elections.filter((e) => e.level === selectedLevel)
      : []

  function toggleElectionId(id: string, checked: boolean) {
    if (checked) {
      setSelectedElectionIds((prev) => [...prev, id])
    } else {
      setSelectedElectionIds((prev) => prev.filter((eid) => eid !== id))
    }
  }

  function validate(): boolean {
    const errors: Record<string, string> = {}

    if (!title_hy || title_hy.trim().length < 5) {
      errors.title_hy = "Վերնագիրը պարտադիր է"
    }
    if (!quote_hy || quote_hy.trim().length < 10) {
      errors.quote_hy = "Մեջբերումը պարտադիր է"
    }
    if (!source_url || !source_url.match(/^https?:\/\//)) {
      errors.source_url = "Անվավեր հղում (http կամ https)"
    }

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setServerError(null)

    if (!validate()) return

    setIsSubmitting(true)

    const payload: PromiseEditIn = {
      title_hy: title_hy.trim(),
      quote_hy: quote_hy.trim(),
      source_url: source_url.trim(),
      made_date: made_date || null,
      expected_date: expected_date || null,
      description_hy: description_hy.trim() || null,
      election_ids: linkElections ? selectedElectionIds : [],
    }

    try {
      await apiClient.put(`/api/promises/${slug}`, payload)
      navigate("/promises?submitted=1")
    } catch (err) {
      const apiErr = err as { status?: number; detail?: string }
      if (apiErr.status === 403) {
        setServerError("Ձեր հաշիվը դեռ պատրաստ չէ ներկայացնելու")
      } else if (apiErr.status === 422) {
        setServerError("Ստուգեք դաշտերը:")
      } else {
        setServerError("Կապի հետ կապված խնդիր կա: Փորձեք կրկին")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>Խմբագրել խոստումը</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Edit notice — UI-SPEC.md Copywriting Contract */}
          <p className="text-sm text-zinc-500 mb-4">
            Փոփոխությունը կուղարկվի ստուգման։ Ներկայիս տարբերակը կշարունակի ցուցադրվել մինչ հաստատումը
          </p>

          <form onSubmit={handleSubmit} noValidate>
            {/* Section 1: Ով */}
            <section aria-labelledby="section-who">
              <h2 id="section-who" className="text-lg font-semibold mb-4">
                Ով
              </h2>

              {/* Politician — read-only display (D-05: politician cannot be changed on edit) */}
              <div className="space-y-2">
                <Label htmlFor="politician-display">Քաղաքական գործիչ</Label>
                <p
                  id="politician-display"
                  className="text-sm text-zinc-900 px-3 py-2 rounded-md border border-input bg-zinc-50"
                >
                  {initialData.politician_name_hy}
                </p>
              </div>

              {/* Election toggle */}
              <div className="flex items-center gap-2 mt-4">
                <Checkbox
                  id="link-elections"
                  checked={linkElections}
                  onCheckedChange={(checked) => {
                    setLinkElections(!!checked)
                    if (!checked) {
                      setSelectedLevel("")
                      setSelectedElectionIds([])
                    }
                  }}
                />
                <Label htmlFor="link-elections">Կապել ընտրություններին</Label>
              </div>

              {/* Cascading election picker */}
              <div className={linkElections ? "mt-4" : "hidden"}>
                {/* Level radio group */}
                <RadioGroup
                  value={selectedLevel}
                  onValueChange={(val) => {
                    setSelectedLevel(val as ElectionLevel)
                    setSelectedElectionIds([])
                  }}
                  className="flex gap-6"
                >
                  <div className="flex items-center gap-2 py-3">
                    <RadioGroupItem value="national" id="level-national" />
                    <Label htmlFor="level-national">Ազգային</Label>
                  </div>
                  <div className="flex items-center gap-2 py-3">
                    <RadioGroupItem value="local" id="level-local" />
                    <Label htmlFor="level-local">Տեղական</Label>
                  </div>
                  <div className="flex items-center gap-2 py-3">
                    <RadioGroupItem value="referendum" id="level-referendum" />
                    <Label htmlFor="level-referendum">Հանրաքվե</Label>
                  </div>
                </RadioGroup>

                {/* Election list */}
                {selectedLevel === "" ? (
                  <p className="text-sm text-zinc-500 mt-2">Ընտրեք մակարդակ</p>
                ) : electionsLoading ? (
                  <p className="text-sm text-zinc-500 mt-2">Բեռնվում է...</p>
                ) : filteredElections.length === 0 ? (
                  <p className="text-sm text-zinc-500 mt-2">Ընտրություններ չկան</p>
                ) : (
                  <div className="space-y-2 mt-2">
                    {filteredElections.map((election) => (
                      <div key={election.id} className="flex items-center gap-2 py-3">
                        <Checkbox
                          id={`election-${election.id}`}
                          checked={selectedElectionIds.includes(election.id)}
                          onCheckedChange={(checked) =>
                            toggleElectionId(election.id, !!checked)
                          }
                        />
                        <Label htmlFor={`election-${election.id}`}>
                          {election.name_hy}
                        </Label>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            <Separator className="my-8" />

            {/* Section 2: Ինչ + Երբ */}
            <section aria-labelledby="section-what">
              <h2 id="section-what" className="text-lg font-semibold mb-4">
                Ինչ + Երբ
              </h2>

              <div className="space-y-4">
                {/* Title */}
                <div className="space-y-2">
                  <Label htmlFor="title_hy">Վերնագիր *</Label>
                  <Input
                    id="title_hy"
                    type="text"
                    value={title_hy}
                    onChange={(e) => setTitleHy(e.target.value)}
                    placeholder="Վերնագիր"
                  />
                  {fieldErrors.title_hy && (
                    <p className="text-sm text-red-600 mt-1" role="alert">
                      {fieldErrors.title_hy}
                    </p>
                  )}
                </div>

                {/* Quote */}
                <div className="space-y-2">
                  <Label htmlFor="quote_hy">Բառացի մեջբերում *</Label>
                  <textarea
                    id="quote_hy"
                    value={quote_hy}
                    onChange={(e) => setQuoteHy(e.target.value)}
                    placeholder="Բառացի մեջբերում"
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y font-normal"
                  />
                  {fieldErrors.quote_hy && (
                    <p className="text-sm text-red-600 mt-1" role="alert">
                      {fieldErrors.quote_hy}
                    </p>
                  )}
                </div>

                {/* Source URL */}
                <div className="space-y-2">
                  <Label htmlFor="source_url">Աղբյուրի հղում *</Label>
                  <Input
                    id="source_url"
                    type="url"
                    value={source_url}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    placeholder="https://..."
                  />
                  {fieldErrors.source_url && (
                    <p className="text-sm text-red-600 mt-1" role="alert">
                      {fieldErrors.source_url}
                    </p>
                  )}
                </div>

                {/* Made date */}
                <div className="space-y-2">
                  <Label htmlFor="made_date">Խոստման ամսաթիվ</Label>
                  <Input
                    id="made_date"
                    type="date"
                    value={made_date}
                    onChange={(e) => setMadeDate(e.target.value)}
                  />
                </div>

                {/* Expected date */}
                <div className="space-y-2">
                  <Label htmlFor="expected_date">Սպասվող կատարման ամսաթիվ</Label>
                  <Input
                    id="expected_date"
                    type="date"
                    value={expected_date}
                    onChange={(e) => setExpectedDate(e.target.value)}
                  />
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description_hy">Նկարագրություն</Label>
                  <textarea
                    id="description_hy"
                    value={description_hy}
                    onChange={(e) => setDescriptionHy(e.target.value)}
                    placeholder="Նկարագրություն (կամընտիր)"
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y font-normal"
                  />
                </div>
              </div>
            </section>

            {/* Server error */}
            {serverError && (
              <p className="text-sm text-red-600 mt-4" role="alert">
                {serverError}
              </p>
            )}

            {/* Submit area */}
            {isEligible ? (
              <Button
                type="submit"
                className="w-full mt-6"
                disabled={isSubmitting}
              >
                {isSubmitting ? "..." : "Ներկայացնել փոփոխություն"}
              </Button>
            ) : (
              <p className="text-sm text-zinc-500 mt-6 p-4 bg-zinc-100 rounded-md">
                Ձեր հաշիվը պետք է ունենա նվազագույնը 7 օրվա վաղեմություն և
                հաստատված էլ. հասցե՝ խոստում ներկայացնելու համար
              </p>
            )}
          </form>
        </CardContent>
      </Card>
    </main>
  )
}

export default function PromiseEditPage() {
  const { slug } = useParams<{ slug: string }>()
  const { data, isLoading, isError } = usePromise(slug!)

  // Loading skeleton — same animate-pulse pattern as PromiseDetailPage
  if (isLoading) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-8 animate-pulse">
        <div className="h-8 w-3/4 bg-zinc-200 rounded mb-6" />
        <div className="h-64 w-full bg-zinc-200 rounded mb-6" />
        <div className="space-y-3">
          <div className="h-4 w-32 bg-zinc-200 rounded" />
          <div className="h-4 w-48 bg-zinc-200 rounded" />
        </div>
      </main>
    )
  }

  // 404 / error — promise not found (covers rejected promises per T-05-17)
  if (isError || !data) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-semibold text-zinc-900 mb-4">Խոստումը չի գտնվել</h1>
        <Link
          to="/promises"
          className="text-blue-600 underline hover:text-blue-800 text-sm"
        >
          Վերադառնալ բոլոր խոստումներ
        </Link>
      </main>
    )
  }

  return (
    <EditForm
      slug={slug!}
      initialData={{
        title_hy: data.title_hy,
        quote_hy: data.quote_hy,
        source_url: data.source_url,
        made_date: data.made_date,
        expected_date: data.expected_date,
        description_hy: null,
        politician_name_hy: data.politician_name_hy,
      }}
    />
  )
}
