import { Separator } from "@/components/ui/separator"

// D-19: Static page, no API calls.
// D-20: Content covers principles + mission. Body text uses TODO placeholder until
// "Our Principles" file content is provided by user before deployment.
export default function AboutPage() {
  return (
    <main className="max-w-2xl mx-auto px-4 py-8">
      {/* H1 — UI-SPEC: "Մeр mасин" = "Մեր մասին" */}
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Մեր մասին</h1>

      {/* Section 1 — UI-SPEC About section 1 heading */}
      <section className="mt-8">
        <h2 className="text-xl font-semibold text-zinc-900 mb-4">
          Ինչպես ենք հավաքում խոստումները
        </h2>
        {/* TODO: Replace with content from "Our Principles" file in project root (D-20) */}
        <p className="text-zinc-700 leading-relaxed text-sm">
          Կայքում կհավաքագրվեն բացառապես ճշտված, աղբյուրով հաստատված ընտրախոստումներ։
          Յուրաքանչյուր խոստում պետք է ունենա ուղղակի մեջբերում քաղաքականի ելույթից,
          հրատարակության կամ հարցազրույցի հղում, ինչպես նաև ամսաթիվ։
          Բովանդակությունը չափավորվում է ադմինիստրատորների կողմից՝ ապահովելու ճշտությունը։
        </p>
      </section>

      <Separator className="my-8" />

      {/* Section 2 — UI-SPEC About section 2 heading */}
      <section>
        <h2 className="text-xl font-semibold text-zinc-900 mb-4">
          Ինչու ստեղծվեց Խոստումները
        </h2>
        {/* TODO: Replace with content from "Our Principles" file in project root (D-20) */}
        <p className="text-zinc-700 leading-relaxed text-sm">
          Հայաստանի քաղաքացիները, լրագրողները և քաղաքական ակտիվիստները հաճախ դժվարանում
          են հետևել, թե ընտրությունից ի վեր ինչ է փոխվել։ «Խոստումներ» կայքը ստեղծվել է
          կամավոր հիմունքներով՝ թափանցիկ, ստուգելի տվյալների բազա ձևավորելու համար,
          որտեղ ցանկացած մարդ կարող է ստուգել, թե արդյոք քաղաքականն իր ասածն արել է։
        </p>
      </section>
    </main>
  )
}