import { Link } from "react-router-dom"
import { Card, CardContent } from "@/components/ui/card"
import Avatar from "./Avatar"
import type { PoliticianOut } from "@/types"

interface PoliticianCardProps {
  politician: PoliticianOut
}

export default function PoliticianCard({ politician }: PoliticianCardProps) {
  return (
    <Link to={`/persons/${politician.slug}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardContent className="pt-4 flex flex-col items-center text-center gap-2">
          <Avatar photoUrl={politician.photo_url} nameHy={politician.name_hy} size="md" />
          <p className="font-semibold text-zinc-900 text-sm">{politician.name_hy}</p>
          {politician.position && (
            <p className="text-xs text-zinc-500">{politician.position}</p>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}
