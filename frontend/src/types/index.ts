export interface HealthResponse {
  status: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface PoliticianOut {
  id: string
  name_hy: string
  slug: string
  photo_url: string | null
  position: string | null
  level: "national" | "local" | "party"
  party_id: string | null
  bio_hy: string | null
  is_active: boolean
}

export interface PartyOut {
  id: string
  name_hy: string
  short_name_hy: string | null
  logo_url: string | null
  founded_year: number | null
  is_active: boolean
  slug: string
}

export interface PartyListItemOut {
  id: string
  name_hy: string
  short_name_hy: string | null
  slug: string
}

export interface ElectionOut {
  id: string
  name_hy: string
  slug: string
  election_date: string
  level: "national" | "local" | "referendum"
  description_hy: string | null
}

export interface ElectionWithCountOut extends ElectionOut {
  promise_count: number
}

export interface PromiseStubOut {
  id: string
  slug: string
  title_hy: string
  quote_hy: string
  resolved_status: "not_rated" | "kept" | "broken" | "in_progress" | "stalled"
}
