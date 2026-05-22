# Phase 2: Politicians, Parties & Elections Browsing - Research

**Researched:** 2026-05-22
**Domain:** FastAPI paginated REST endpoints + SQLAlchemy 2.x async + TanStack Query v5 + shadcn/ui React pages
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Phase 2 builds a shared `<Layout>` component that wraps all pages with a persistent site header.
- **D-02:** Full planned nav link set rendered from day one as stubs: logo (Խոստումներ → `/`), Կատարված (`/fulfilled`), Չկատարված (`/unfulfilled`), Պերսոններ (`/persons`), Ընտրություններ (`/elections`). Links for unbuilt phases route to NotFoundPage.
- **D-03:** Logo links to `/`. No mobile hamburger menu in Phase 2.
- **D-04:** Filter strategy is **server-side query params** — `?party=<uuid>&level=<national|local|party>`.
- **D-05:** Filter UI is two `<select>` dropdowns: Party + Level. Both default to "All".
- **D-06:** Promise stubs are minimal: truncated `quote_hy` (~120 chars, ellipsis) + `resolved_status` badge.
- **D-07:** Promise stubs link to `/promises/{slug}` — hits NotFoundPage until Phase 3.
- **D-08:** Promise lists on party and election pages are **paginated** (same offset+limit approach).
- **D-09:** All list APIs use offset+limit: `?page=1&per_page=20`, defaults page=1 per_page=20, max per_page=100.
- **D-10:** API response envelope: `{ items: [...], total: N, page: N, per_page: N, pages: N }`.
- **D-11:** Frontend uses the **shadcn/ui Pagination component**.

### Claude's Discretion

- Persons list layout: Card grid (photo/avatar, name, role, party badge) using shadcn/ui `Card`; 3-column desktop, 1-column mobile.
- Photo fallback: initials-based avatar or neutral silhouette when `photo_url` is null.
- Status badge colors: exact Tailwind/shadcn color tokens for each `resolved_status` — must be visually distinct.
- API router file naming: follow `backend/app/routers/health.py` pattern; one file per domain.

### Deferred Ideas (OUT OF SCOPE)

- Mobile hamburger/responsive nav — Phase 3.
- Promise detail page (`/promises/{slug}`) — Phase 3.
- Fulfillment percentage on politician profiles — Phase 8.
- Admin create/edit politician and party profiles — Phase 6.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| POLS-01 | Anyone can view a politician profile page (photo, full name, current role, party affiliation, promise list, fulfillment percentage) | FastAPI `GET /api/politicians/{slug}` + SQLAlchemy join to parties; fulfillment % deferred to Phase 8 (stats_cache not populated yet) |
| POLS-02 | Anyone can browse the "Persons" section — paginated list of all politicians with filtering | FastAPI `GET /api/politicians?party=<uuid>&level=<level>&page=N&per_page=N`; TanStack Query paginated hook |
| POLS-03 | Anyone can view a party or bloc page showing all linked promises and member politicians | FastAPI `GET /api/parties/{slug_or_id}` + `GET /api/parties/{id}/politicians` + `GET /api/parties/{id}/promises`; party has no slug in current schema — see Open Questions |
| ELEC-01 | Anyone can view the elections list page showing all elections with promise counts | FastAPI `GET /api/elections` with subquery count of promise_election_links per election |
| ELEC-02 | Anyone can view an election detail page showing all promises linked to that election across all politicians | FastAPI `GET /api/elections/{slug}` + paginated `GET /api/elections/{slug}/promises` joining promise_election_links |
</phase_requirements>

---

## Summary

Phase 2 delivers the first user-visible pages of Khostumner: read-only browsing of politicians, parties, and elections. All data models are already defined in `backend/app/models/` (built in Phase 1). The work is entirely about wiring the API layer (FastAPI routers + Pydantic schemas) and the frontend display layer (React pages + TanStack Query hooks + shadcn/ui components).

The backend pattern is established by `health.py`: `APIRouter()` + `async def` handler + `db: AsyncSession = Depends(get_db)`. Phase 2 follows this pattern for three new routers: `politicians.py`, `parties.py`, `elections.py`. Each router exposes list (paginated, filterable) and detail (by slug) endpoints. The unified response envelope `{ items, total, page, per_page, pages }` must be consistent across all list endpoints so the frontend can use a single generic pagination component.

The frontend pattern is established by `useHealth.ts`: `useQuery` with typed response and error/loading states. Phase 2 follows this pattern for `usePoliticians`, `usePolitician`, `useParty`, `useElections`, `useElection`. The shadcn/ui Pagination component handles page navigation; shadcn/ui Card handles politician cards; shadcn/ui Badge handles `resolved_status` coloring. One critical gap: `Party` has no `slug` field in the current schema — party detail pages must use `id` (UUID) in the URL unless a slug is added via Alembic migration.

**Primary recommendation:** Build three backend routers (politicians, parties, elections) with the paginated envelope pattern, add Pydantic schemas for each, wire routes in `main.py`, then build the Layout + 5 page components on the frontend using TanStack Query hooks. Add the `slug` field to `Party` via Alembic migration before building party detail pages.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Paginated politician list with filters | API / Backend | Database | Filtering/ordering/pagination belongs in SQL; frontend only sends params |
| Politician detail (photo, role, party) | API / Backend | Database | Join to parties table; frontend renders |
| Party page (members + promises) | API / Backend | Database | Multiple queries joined; frontend renders list |
| Elections list with promise counts | API / Backend | Database | COUNT subquery over promise_election_links |
| Election detail (linked promises) | API / Backend | Database | JOIN through promise_election_links |
| Shared Layout + nav header | Frontend Server (Client) | — | Pure React component, no server state |
| Paginated page navigation UI | Frontend Server (Client) | — | shadcn/ui Pagination; page state in URL query params |
| Filter dropdowns (Party, Level) | Frontend Server (Client) | API | UI owns state; API applies filter |
| Photo fallback / initials avatar | Frontend Server (Client) | — | Client-side computed from name_hy |
| Status badge coloring | Frontend Server (Client) | — | Purely presentational; resolved_status drives color choice |

---

## Standard Stack

### Core (already installed — no new installs needed for backend)

| Library | Version (pinned in requirements.txt) | Purpose | Why Standard |
|---------|--------------------------------------|---------|--------------|
| fastapi | 0.115.14 [VERIFIED: PyPI] | HTTP routing, request validation, OpenAPI docs | Already in use; established pattern in health.py |
| sqlalchemy | 2.0.49 [VERIFIED: PyPI] | Async ORM for PostgreSQL | Already in use; all models defined |
| pydantic | 2.13.4 [VERIFIED: PyPI] | Response schema validation and serialization | FastAPI's native schema layer |
| alembic | 1.18.4 [VERIFIED: PyPI] | Schema migrations | Needed if Party slug is added |

### Core (already installed — no new installs needed for frontend)

| Library | Version (in package.json) | Purpose | Why Standard |
|---------|--------------------------|---------|--------------|
| @tanstack/react-query | ^5.0.0 (latest 5.100.11) [VERIFIED: npm registry] | Server state management, pagination | Established in useHealth.ts |
| react-router-dom | ^7.0.0 (latest 7.15.1) [VERIFIED: npm registry] | Client-side routing | Established in App.tsx |
| tailwindcss | ^4.0.0 (latest 4.3.0) [VERIFIED: npm registry] | Utility CSS | Established; CSS-first config in index.css |

### New Frontend Installs — shadcn/ui Components

shadcn/ui components are NOT npm packages — they are code-generated into `src/components/ui/` via the `shadcn` CLI. The `components.json` is already present (zinc base color, CSS variables enabled, `@/components` alias wired).

| Component | Install Command | Purpose |
|-----------|-----------------|---------|
| Card | `npx shadcn@latest add card` | Politician cards in grid |
| Badge | `npx shadcn@latest add badge` | `resolved_status` color badges |
| Pagination | `npx shadcn@latest add pagination` | Page navigation on all list pages |
| Button | `npx shadcn@latest add button` | Used internally by Pagination |
| Select | `npx shadcn@latest add select` | Party/Level filter dropdowns |

shadcn/ui components copy source files into the repo. They bring these peer deps which must be installed:

| Package | Version | Install | Postinstall Risk |
|---------|---------|---------|-----------------|
| @radix-ui/react-slot | 1.2.4 [VERIFIED: npm registry] | `npm install` | None — no postinstall script |
| lucide-react | 1.16.0 [VERIFIED: npm registry] | `npm install` | None |
| class-variance-authority | 0.7.1 [VERIFIED: npm registry] | `npm install` | None |
| clsx | 2.1.1 [VERIFIED: npm registry] | `npm install` | None |
| tailwind-merge | 3.6.0 [VERIFIED: npm registry] | `npm install` | None |

**Installation sequence:**
```bash
# 1. Install peer deps
npm install @radix-ui/react-slot lucide-react class-variance-authority clsx tailwind-merge

# 2. Add shadcn components (copies source into src/components/ui/)
npx shadcn@latest add card badge pagination button select

# 3. Verify components generated
ls frontend/src/components/ui/
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| shadcn/ui Pagination | Custom pagination | shadcn/ui matches the established component library; custom = more work, visual inconsistency |
| Initials avatar (CSS) | dicebear avatar API | CSS initials work offline, no external dep, simpler |
| Server-side filter params | Client-side filter (filter after fetch) | Server-side enables shareable URLs, smaller payloads — locked by D-04 |

---

## Package Legitimacy Audit

> slopcheck ran in PyPI mode and flagged npm packages as SLOP (false positives — the tool is ecosystem-unaware). All packages below were verified manually via `npm view <pkg> version`.

| Package | Registry | Notes | npm view result | Disposition |
|---------|----------|-------|-----------------|-------------|
| @tanstack/react-query | npm | Major library, millions of downloads | 5.100.11 [VERIFIED: npm registry] | Approved |
| react-router-dom | npm | Official React Router package | 7.15.1 [VERIFIED: npm registry] | Approved |
| tailwindcss | npm | CSS framework | 4.3.0 [VERIFIED: npm registry] | Approved |
| shadcn | npm (CLI only) | Code generator; copies files into repo | 4.8.0 [VERIFIED: npm registry] | Approved (no runtime dep) |
| @radix-ui/react-slot | npm | Radix UI primitive | 1.2.4 [VERIFIED: npm registry] | Approved |
| lucide-react | npm | Icon library | 1.16.0 [VERIFIED: npm registry] | Approved |
| class-variance-authority | npm | CVA for shadcn/ui variants | 0.7.1 [VERIFIED: npm registry] | Approved |
| clsx | npm | Class merging utility | 2.1.1 [VERIFIED: npm registry] | Approved |
| tailwind-merge | npm | Tailwind class deduplication | 3.6.0 [VERIFIED: npm registry] | Approved |

**slopcheck note:** Tool ran in Python/PyPI mode (not npm). All npm packages above were individually verified via `npm view <pkg> version`. No postinstall scripts found on any of the above packages. Marking all `[VERIFIED: npm registry]` based on direct registry verification.

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
Browser
  │
  ├── GET /persons?party=X&level=Y&page=N
  │     └─► React PersonsPage
  │           └─► usePoliticians(filters, page)
  │                 └─► TanStack Query ["politicians", {party, level, page}]
  │                       └─► apiClient.get("/api/politicians?...")
  │                             └─► FastAPI GET /api/politicians
  │                                   └─► SQLAlchemy select(Politician)
  │                                         .where(party_id=X, level=Y)
  │                                         .offset().limit()
  │                                         → PostgreSQL
  │                                   └─► response: {items, total, page, per_page, pages}
  │
  ├── GET /persons/:slug
  │     └─► React PoliticianProfilePage
  │           └─► usePolitician(slug)
  │                 └─► TanStack Query ["politician", slug]
  │                       └─► GET /api/politicians/{slug}
  │                             └─► SQLAlchemy select(Politician).where(slug=slug)
  │                                   JOIN parties (via party_id)
  │                             └─► GET /api/politicians/{slug}/promises (paginated)
  │
  ├── GET /parties/:id
  │     └─► React PartyPage
  │           └─► useParty(id) + usePartyPoliticians(id) + usePartyPromises(id, page)
  │                 └─► GET /api/parties/{id}
  │                 └─► GET /api/parties/{id}/politicians
  │                 └─► GET /api/parties/{id}/promises?page=N
  │
  ├── GET /elections
  │     └─► React ElectionsListPage
  │           └─► useElections(page)
  │                 └─► GET /api/elections
  │                       └─► SELECT elections + COUNT(promise_election_links)
  │
  └── GET /elections/:slug
        └─► React ElectionDetailPage
              └─► useElection(slug) + useElectionPromises(slug, page)
                    └─► GET /api/elections/{slug}
                    └─► GET /api/elections/{slug}/promises?page=N
```

### Recommended Project Structure

New files to create in Phase 2:

```
backend/
├── app/
│   ├── routers/
│   │   ├── politicians.py    # GET /api/politicians, GET /api/politicians/{slug}
│   │   │                     # GET /api/politicians/{slug}/promises
│   │   ├── parties.py        # GET /api/parties/{id}, GET /api/parties/{id}/politicians
│   │   │                     # GET /api/parties/{id}/promises
│   │   └── elections.py      # GET /api/elections, GET /api/elections/{slug}
│   │                         # GET /api/elections/{slug}/promises
│   └── schemas/
│       ├── politicians.py    # PoliticianOut, PoliticianListOut, PaginatedResponse[T]
│       ├── parties.py        # PartyOut
│       ├── elections.py      # ElectionOut, ElectionWithCountOut
│       └── promises.py       # PromiseStubOut (truncated quote + status badge)
├── alembic/versions/
│   └── YYYYMMDDHHMMSS_add_party_slug.py   # if Party.slug is added

frontend/src/
├── components/
│   ├── Layout.tsx             # Persistent header + nav (D-01, D-02)
│   ├── ui/                    # shadcn/ui generated components (card, badge, etc.)
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── pagination.tsx
│   │   ├── button.tsx
│   │   └── select.tsx
│   ├── PoliticianCard.tsx     # Card component for persons grid
│   ├── PromiseStub.tsx        # Truncated quote + ResolvedStatus badge
│   ├── PaginationControls.tsx # Wrapper around shadcn Pagination
│   └── Avatar.tsx             # Initials/photo fallback
├── hooks/
│   ├── usePoliticians.ts      # Paginated list with filters
│   ├── usePolitician.ts       # Single politician by slug
│   ├── useParty.ts            # Party detail
│   ├── useElections.ts        # Paginated elections list
│   └── useElection.ts         # Single election by slug + promises
├── pages/
│   ├── PersonsPage.tsx        # /persons — grid + filters + pagination
│   ├── PoliticianProfilePage.tsx  # /persons/:slug
│   ├── PartyPage.tsx          # /parties/:id
│   ├── ElectionsListPage.tsx  # /elections
│   └── ElectionDetailPage.tsx # /elections/:slug
├── api/
│   └── client.ts              # Extend with query-string support (already has get<T>)
└── types/
    └── index.ts               # Add PoliticianOut, PartyOut, ElectionOut, PaginatedResponse<T>
```

### Pattern 1: Paginated Response Envelope (Backend)

**What:** A generic Pydantic model for all paginated list responses.
**When to use:** Every list endpoint in Phase 2 (and beyond).

```python
# Source: Pydantic v2 docs + FastAPI response model pattern
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int
```

Usage in router:
```python
# Source: FastAPI query params docs + SQLAlchemy async docs
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.politicians import Politician, PoliticianLevel
from app.schemas.politicians import PoliticianOut
from app.schemas.common import PaginatedResponse
import uuid

router = APIRouter(prefix="/api/politicians", tags=["politicians"])

@router.get("/", response_model=PaginatedResponse[PoliticianOut])
async def list_politicians(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    party: uuid.UUID | None = Query(None),
    level: PoliticianLevel | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    stmt = select(Politician)
    if party:
        stmt = stmt.where(Politician.party_id == party)
    if level:
        stmt = stmt.where(Politician.level == level)

    # Count query (reuse same filters)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Data query
    items_result = await db.execute(stmt.offset(offset).limit(per_page))
    items = items_result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )
```

### Pattern 2: Pydantic v2 Schema for ORM Objects

**What:** `model_config = ConfigDict(from_attributes=True)` enables direct ORM → Pydantic serialization.
**When to use:** Every response schema that maps from a SQLAlchemy model.

```python
# Source: Pydantic v2 docs
from pydantic import BaseModel, ConfigDict
import uuid
from app.models.politicians import PoliticianLevel

class PoliticianOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    slug: str
    photo_url: str | None
    position: str | None
    level: PoliticianLevel
    party_id: uuid.UUID | None
    bio_hy: str | None
    is_active: bool
```

### Pattern 3: TanStack Query v5 Paginated Hook

**What:** `useQuery` with filters + page in the queryKey; `placeholderData: keepPreviousData` prevents flash to loading state on page change.
**When to use:** All paginated list hooks.

```typescript
// Source: TanStack Query v5 docs — Paginated Queries
import { useQuery, keepPreviousData } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PoliticianOut } from "@/types"

interface UsePoliticiansParams {
  page: number
  perPage?: number
  party?: string | null
  level?: string | null
}

export function usePoliticians({ page, perPage = 20, party, level }: UsePoliticiansParams) {
  return useQuery<PaginatedResponse<PoliticianOut>>({
    queryKey: ["politicians", { page, perPage, party, level }],
    queryFn: () => {
      const params = new URLSearchParams()
      params.set("page", String(page))
      params.set("per_page", String(perPage))
      if (party) params.set("party", party)
      if (level) params.set("level", level)
      return apiClient.get<PaginatedResponse<PoliticianOut>>(`/api/politicians?${params}`)
    },
    placeholderData: keepPreviousData,
  })
}
```

### Pattern 4: shadcn/ui Pagination with URL State

**What:** Pagination state stored in URL query params (`?page=N`) via `useSearchParams`.
**When to use:** All paginated pages. URL state makes pages shareable and bookmarkable (aligns with D-04 for filters).

```typescript
// Source: shadcn/ui Pagination docs + react-router-dom useSearchParams
import { useSearchParams } from "react-router-dom"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  PaginationEllipsis,
} from "@/components/ui/pagination"

interface PaginationControlsProps {
  totalPages: number
  currentPage: number
}

export function PaginationControls({ totalPages, currentPage }: PaginationControlsProps) {
  const [searchParams, setSearchParams] = useSearchParams()

  const goToPage = (p: number) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      next.set("page", String(p))
      return next
    })
  }

  return (
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            onClick={() => goToPage(currentPage - 1)}
            aria-disabled={currentPage <= 1}
          />
        </PaginationItem>
        {/* Page links omitted for brevity — generate 1..totalPages with ellipsis */}
        <PaginationItem>
          <PaginationNext
            onClick={() => goToPage(currentPage + 1)}
            aria-disabled={currentPage >= totalPages}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  )
}
```

### Pattern 5: Initials Avatar (Photo Fallback)

**What:** When `photo_url` is null (most seed politicians), derive 1-2 initial characters from `name_hy` and render a colored circle.
**When to use:** PoliticianCard and PoliticianProfilePage whenever `photo_url` is falsy.

```typescript
// Source: Claude's Discretion (D — photo fallback)
// Armenian names: first letter of first word + first letter of last word
function getInitials(nameHy: string): string {
  const parts = nameHy.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase()
}

export function Avatar({ photoUrl, nameHy, size = "md" }: AvatarProps) {
  if (photoUrl) {
    return <img src={photoUrl} alt={nameHy} className={sizeClasses[size]} />
  }
  return (
    <div className={`flex items-center justify-center rounded-full bg-zinc-200 text-zinc-700 font-semibold ${sizeClasses[size]}`}>
      {getInitials(nameHy)}
    </div>
  )
}
```

### Pattern 6: ResolvedStatus Badge Colors

**What:** Color-coded badge for each `resolved_status` value. Uses Tailwind classes directly since shadcn Badge `variant` only covers default/secondary/destructive/outline/ghost.
**When to use:** Every PromiseStub.

```typescript
// Source: Claude's Discretion (D — status badge colors)
const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  kept:        { label: "Կատարված",        className: "bg-green-100 text-green-800 border-green-200" },
  broken:      { label: "Չկատարված",       className: "bg-red-100 text-red-800 border-red-200" },
  in_progress: { label: "Ընթացքի մեջ",    className: "bg-yellow-100 text-yellow-800 border-yellow-200" },
  stalled:     { label: "Կասեցված",        className: "bg-gray-100 text-gray-600 border-gray-200" },
  not_rated:   { label: "Չգնահատված",     className: "bg-zinc-100 text-zinc-500 border-zinc-200" },
}

export function ResolvedStatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.not_rated
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
```

### Pattern 7: Layout with Nav Stubs

**What:** Shared `<Layout>` component wrapping all pages. Nav links present from day one — unimplemented routes point to `/` or hit NotFoundPage.
**When to use:** All Phase 2+ pages wrapped in `<Layout>`.

```tsx
// Source: D-01, D-02, D-03
import { Link } from "react-router-dom"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <nav className="max-w-7xl mx-auto px-4 flex items-center gap-6 h-14">
          <Link to="/" className="font-bold text-lg text-gray-900">Խոստումներ</Link>
          <Link to="/fulfilled" className="text-sm text-gray-600 hover:text-gray-900">Կատարված</Link>
          <Link to="/unfulfilled" className="text-sm text-gray-600 hover:text-gray-900">Չկատարված</Link>
          <Link to="/persons" className="text-sm text-gray-600 hover:text-gray-900">Պերսոններ</Link>
          <Link to="/elections" className="text-sm text-gray-600 hover:text-gray-900">Ընտրություններ</Link>
        </nav>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
```

### Pattern 8: Election Promise Count (Backend SQL)

**What:** Elections list needs a promise count per election. This requires a subquery — do not compute it in Python.
**When to use:** `GET /api/elections` list endpoint.

```python
# Source: SQLAlchemy 2.x docs — correlated subquery / label
from sqlalchemy import select, func
from app.models.elections import Election
from app.models.promises import PromiseElectionLink

promise_count = (
    select(func.count())
    .where(PromiseElectionLink.election_id == Election.id)
    .correlate(Election)
    .scalar_subquery()
    .label("promise_count")
)

stmt = select(Election, promise_count)
```

### Anti-Patterns to Avoid

- **Returning ORM objects directly without `from_attributes=True`:** Pydantic v2 raises `PydanticUserError`. Always set `model_config = ConfigDict(from_attributes=True)`.
- **Missing CORS update for new prefixes:** The current `main.py` CORS allows `http://localhost:5173`. Phase 2 doesn't need changes (same origin), but new `/api/...` prefixed routers must be included via `include_router(router, prefix="/api")`.
- **Counting with `len(items)` instead of a count query:** N+1 pattern; always run a separate `SELECT COUNT(*)` with the same filters.
- **Filtering on `party_id` when Party has no slug:** Party page URL must use UUID until slug is added.
- **Rendering all promise stubs without moderation filter:** Only show `moderation_status=approved` promises on public pages. Seed data already sets `approved`, but the query must filter explicitly.
- **Storing page in component state instead of URL:** Breaks browser back button and makes links unshare-able. Use `useSearchParams`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pagination UI | Custom page links | shadcn/ui `Pagination` | RTL support, accessible, consistent style |
| Badge styling | Conditional class logic per status | Status config map + className | Centralizes all label/color decisions |
| Request deduplication | Manual cache/abort logic | TanStack Query cache | Handles stale-while-revalidate, background refetch, dedup |
| ORM→JSON serialization | Manual `__dict__` conversion | Pydantic `from_attributes=True` | Handles nested types, enums, UUID serialization |
| Generic list type | Per-entity response models | `PaginatedResponse[T]` generic | Single source of truth for envelope shape |
| Armenian initials | Transliteration library | Simple `split/charAt` on `name_hy` | Armenian is Unicode; split on whitespace works reliably |

**Key insight:** The biggest time saver is a single `PaginatedResponse[T]` generic on the backend and a single `PaginationControls` component on the frontend — every new list endpoint and list page reuses these with zero extra work.

---

## Common Pitfalls

### Pitfall 1: Party Has No `slug` Field

**What goes wrong:** Planner writes a route `/parties/:slug` but `Party` model has no `slug` column. Detail pages 404 or require UUID in URL.
**Why it happens:** Phase 1 schema review shows `Party` fields: `id, name_hy, short_name_hy, logo_url, founded_year, is_active, notes` — no `slug`.
**How to avoid:** Add `slug` to `Party` via an Alembic migration as Wave 0 in Phase 2. Populate slugs for existing seed parties (e.g., "qaghaqaciakan-paymanagir" for ՔՊ). Or use `id` (UUID) in the URL — less human-readable but avoids migration.
**Warning signs:** If party detail route is `/parties/:slug` and there's no migration task, the plan is incomplete.

### Pitfall 2: Pydantic v2 `from_attributes` Not Set

**What goes wrong:** `response_model=PoliticianOut` + returning ORM object → `PydanticUserError: from_orm is not supported`. Runtime error, not a type error.
**Why it happens:** Pydantic v2 changed `orm_mode = True` (v1) to `model_config = ConfigDict(from_attributes=True)` (v2).
**How to avoid:** Every schema that wraps an ORM model must include `model_config = ConfigDict(from_attributes=True)`.
**Warning signs:** Health schema (`backend/app/schemas/health.py`) doesn't use `from_attributes` because it returns a dict — new ORM-mapped schemas need it.

### Pitfall 3: `Generic[T]` Pydantic Models Lose Type Info in OpenAPI

**What goes wrong:** `PaginatedResponse[PoliticianOut]` renders as `PaginatedResponse` in OpenAPI schema without parameterization detail. This is a known Pydantic/FastAPI limitation.
**Why it happens:** Python's `Generic[T]` erasure at runtime.
**How to avoid:** Accept the limitation — the OpenAPI schema will show the concrete field types in the `items` array even if the model name is generic. Not a functional issue.
**Warning signs:** None — this is cosmetic only.

### Pitfall 4: Missing `moderation_status=approved` Filter

**What goes wrong:** Promises with `moderation_status=pending` or `rejected` appear in public browsing pages.
**Why it happens:** Forgetting to add `.where(Promise.moderation_status == ModerationStatus.approved)` in promise subqueries.
**How to avoid:** Always filter by `moderation_status=approved` in any public promise list query. Seed data has all 20 promises as `approved` — easy to miss missing filter during development.
**Warning signs:** Seed works fine but adding a `pending` promise in Phase 5 makes it visible.

### Pitfall 5: TanStack Query v5 `keepPreviousData` API Changed

**What goes wrong:** Using `keepPreviousData: true` (v4 syntax) causes a type error or silent failure.
**Why it happens:** TanStack Query v5 renamed `keepPreviousData` to `placeholderData: keepPreviousData` (import the function from the package).
**How to avoid:** `import { keepPreviousData } from "@tanstack/react-query"` and use `placeholderData: keepPreviousData` in the options object.
**Warning signs:** TypeScript error: `Property 'keepPreviousData' does not exist on type 'UndefinedInitialDataOptions'`.

### Pitfall 6: CORS Not Updated for Production

**What goes wrong:** `main.py` hardcodes `allow_origins=["http://localhost:5173"]`. Production deploy will fail with CORS errors.
**Why it happens:** Phase 1 intentionally left this as dev-only.
**How to avoid:** Phase 2 should read allowed origins from `settings` (env var `CORS_ORIGINS`). Low urgency but should be addressed.
**Warning signs:** Browser CORS error when frontend domain differs from `localhost:5173`.

---

## Code Examples

### Backend: Full Router Pattern (politicians.py)

```python
# Source: FastAPI docs + SQLAlchemy 2.x async docs + health.py template
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.politicians import Politician, PoliticianLevel
from app.models.promises import Promise, ModerationStatus
from app.schemas.politicians import PoliticianOut
from app.schemas.promises import PromiseStubOut
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/politicians", tags=["politicians"])


@router.get("/", response_model=PaginatedResponse[PoliticianOut])
async def list_politicians(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    party: uuid.UUID | None = Query(None),
    level: PoliticianLevel | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Politician).where(Politician.is_active == True)
    if party:
        stmt = stmt.where(Politician.party_id == party)
    if level:
        stmt = stmt.where(Politician.level == level)

    total = (await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )).scalar() or 0

    items = (await db.execute(
        stmt.order_by(Politician.name_hy).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()

    return PaginatedResponse(
        items=items, total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{slug}", response_model=PoliticianOut)
async def get_politician(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Politician).where(Politician.slug == slug))
    politician = result.scalars().first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")
    return politician
```

### Backend: `main.py` router inclusion

```python
# Source: FastAPI docs — include_router
from app.routers import health, politicians, parties, elections

app.include_router(health.router)
app.include_router(politicians.router, prefix="/api")
app.include_router(parties.router, prefix="/api")
app.include_router(elections.router, prefix="/api")
```

### Frontend: apiClient extension for query strings

```typescript
// Extend existing frontend/src/api/client.ts
const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(API_BASE + path)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    return response.json() as Promise<T>
  },
}
// Note: query string is built by caller using URLSearchParams and appended to path
```

### Frontend: PersonsPage with filters + pagination

```tsx
// Source: TanStack Query v5 docs + D-04/D-05/D-09/D-10/D-11
import { useSearchParams } from "react-router-dom"
import { usePoliticians } from "@/hooks/usePoliticians"
import { PoliticianCard } from "@/components/PoliticianCard"
import { PaginationControls } from "@/components/PaginationControls"

export default function PersonsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const page = Number(searchParams.get("page") ?? "1")
  const party = searchParams.get("party")
  const level = searchParams.get("level")

  const { data, isLoading, isError } = usePoliticians({ page, party, level })

  return (
    <div>
      {/* Filter dropdowns */}
      <div className="flex gap-4 mb-6">
        <select value={party ?? ""} onChange={e => {
          setSearchParams(p => { const n = new URLSearchParams(p); e.target.value ? n.set("party", e.target.value) : n.delete("party"); n.set("page", "1"); return n })
        }}>
          <option value="">Բոլոր կուսակցությունները</option>
          {/* Party options fetched separately */}
        </select>
        <select value={level ?? ""} onChange={e => {
          setSearchParams(p => { const n = new URLSearchParams(p); e.target.value ? n.set("level", e.target.value) : n.delete("level"); n.set("page", "1"); return n })
        }}>
          <option value="">Բոլոր մակարդակները</option>
          <option value="national">Ազգային</option>
          <option value="local">Տեղական</option>
          <option value="party">Կուսակցական</option>
        </select>
      </div>

      {/* Grid */}
      {isLoading && <p>Բեռնվում է...</p>}
      {isError && <p className="text-red-600">Սխալ</p>}
      {data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {data.items.map(p => <PoliticianCard key={p.id} politician={p} />)}
          </div>
          <PaginationControls currentPage={data.page} totalPages={data.pages} />
        </>
      )}
    </div>
  )
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic `orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` | Pydantic v2 (2023) | Must use v2 syntax; project uses pydantic 2.13.4 |
| TanStack Query `keepPreviousData: true` (option) | `placeholderData: keepPreviousData` (imported fn) | TanStack Query v5 (2023) | Import `keepPreviousData` from the package |
| shadcn/ui `npx create-shadcn-ui` | `npx shadcn@latest add <component>` | shadcn CLI v1+ | Per-component install; only install what you need |
| Tailwind `tailwind.config.js` | `@import "tailwindcss"` in CSS (CSS-first) | Tailwind v4 (2024) | Already set up in index.css; no JS config needed |
| React Router `<Switch>` | `<Routes>` + `<Route>` | React Router v6 (2021) | Already in use in App.tsx |

**Deprecated/outdated:**
- `from_orm()` method: replaced by `model_validate(obj, from_attributes=True)` in Pydantic v2. The `from_attributes=True` config enables direct ORM object passing to response_model.
- `keepPreviousData: true` option key: removed in TanStack Query v5; use `placeholderData: keepPreviousData`.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Party pages use `id` (UUID) in the URL since `Party` has no `slug` field | Open Questions | If slug is added, route pattern and Alembic migration must be planned |
| A2 | shadcn/ui Pagination component uses `href` or `onClick` — RTL support available | Standard Stack | Armenian is LTR so RTL irrelevant; but component API must be checked when adding |
| A3 | `Politician.is_active` filter should be applied on all public list endpoints | Code Examples | If inactive politicians need to appear (e.g., for historical record), filter must be removed |
| A4 | The `apiClient.get<T>` can have query strings appended directly to the path | Code Examples | If client is refactored to use a separate params argument, all hook code changes |

**If this table is empty:** N/A — 4 assumptions found.

---

## Open Questions

1. **Does `Party` need a `slug` field in Phase 2?**
   - What we know: `Party` schema has no `slug`. Party detail page URL must be either `/parties/:id` (UUID) or `/parties/:slug`.
   - What's unclear: The CONTEXT.md references `party/bloc pages` but doesn't specify the URL pattern. ROADMAP says `/parties/:slug` is the natural pattern.
   - Recommendation: Add `slug` to `Party` via Alembic migration in Phase 2 Wave 0. Populate slugs for 4 seed parties (short ASCII names). Use `/parties/:slug` route. This is a small migration but avoids UUID-based URLs.

2. **Should the parties list page exist in Phase 2?**
   - What we know: POLS-03 requires a party detail page. The nav has no explicit "Parties" link. D-02 nav stubs don't include a parties list page.
   - What's unclear: How does a user navigate to a party page? Via party badge on a politician card (linking to `/parties/:id`).
   - Recommendation: No dedicated parties list page in Phase 2. Party pages are accessed via the party badge on politician profiles. Add a `GET /api/parties` list endpoint as data source for the Party filter dropdown on the Persons page.

3. **Promise stub on politician profile: paginated or show all?**
   - What we know: D-08 says promise lists on party and election pages are paginated. CONTEXT.md says "Politician profile promise list is also paginated."
   - What's unclear: How many promises per page on a politician profile? Same 20 as list pages?
   - Recommendation: Default to `per_page=10` for promise stubs on profile pages (more compact); same endpoint `GET /api/politicians/{slug}/promises?page=N&per_page=10`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend build + shadcn CLI | ✓ (assumed via Docker) | 20-alpine (Dockerfile) | — |
| Python 3.12 | Backend | ✓ (via Docker) | 3.12-slim (Dockerfile) | — |
| PostgreSQL 17 | Database | ✓ (via Docker Compose) | 17 | — |
| npm | shadcn component generation | ✓ | bundled with Node 20 | — |
| Docker Compose | Local dev | ✓ (Phase 1 verified) | — | Manual start of each service |

No blocking environment gaps identified.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (backend) | pytest + pytest-asyncio 1.3.0 + httpx 0.28.1 |
| Framework (frontend) | vitest 4.x + @testing-library/react |
| Config file (backend) | `backend/pytest.ini` or inline in `pyproject.toml` |
| Quick run command (backend) | `cd backend && pytest tests/test_politicians.py -x` |
| Full suite command (backend) | `cd backend && pytest` |
| Quick run command (frontend) | `cd frontend && npm test -- --run` |
| Full suite command (frontend) | `cd frontend && npm test -- --run` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| POLS-02 | `GET /api/politicians` returns 200 with paginated envelope | integration | `pytest tests/test_politicians.py::test_list_politicians -x` | Wave 0 |
| POLS-02 | `GET /api/politicians?party=<uuid>` filters by party | integration | `pytest tests/test_politicians.py::test_filter_by_party -x` | Wave 0 |
| POLS-02 | `GET /api/politicians?level=national` filters by level | integration | `pytest tests/test_politicians.py::test_filter_by_level -x` | Wave 0 |
| POLS-01 | `GET /api/politicians/{slug}` returns politician detail | integration | `pytest tests/test_politicians.py::test_get_politician_by_slug -x` | Wave 0 |
| POLS-01 | `GET /api/politicians/not-found` returns 404 | integration | `pytest tests/test_politicians.py::test_politician_not_found -x` | Wave 0 |
| POLS-03 | `GET /api/parties/{id}` returns party detail | integration | `pytest tests/test_parties.py::test_get_party -x` | Wave 0 |
| ELEC-01 | `GET /api/elections` returns elections with promise_count | integration | `pytest tests/test_elections.py::test_list_elections -x` | Wave 0 |
| ELEC-02 | `GET /api/elections/{slug}` returns election detail | integration | `pytest tests/test_elections.py::test_get_election -x` | Wave 0 |
| ELEC-02 | `GET /api/elections/{slug}/promises` returns linked promises | integration | `pytest tests/test_elections.py::test_election_promises -x` | Wave 0 |
| POLS-02 | PersonsPage renders politician cards (smoke) | component | `cd frontend && npm test -- --run App` | Wave 0 |
| POLS-01 | PoliticianProfilePage renders name and role | component | `cd frontend && npm test -- --run` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_politicians.py -x` (or relevant test file)
- **Per wave merge:** `cd backend && pytest && cd frontend && npm test -- --run`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `backend/tests/test_politicians.py` — covers POLS-01, POLS-02
- [ ] `backend/tests/test_parties.py` — covers POLS-03
- [ ] `backend/tests/test_elections.py` — covers ELEC-01, ELEC-02
- [ ] `frontend/src/pages/PersonsPage.test.tsx` — smoke render test

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | Phase 2 is read-only, unauthenticated |
| V3 Session Management | No | No sessions in Phase 2 |
| V4 Access Control | No | All Phase 2 endpoints are public read-only |
| V5 Input Validation | Yes | FastAPI Query params auto-validate types; Pydantic schemas validate responses |
| V6 Cryptography | No | No secrets handled in Phase 2 |

### Known Threat Patterns for FastAPI + PostgreSQL Public Read Endpoints

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection via query params | Tampering | SQLAlchemy ORM parameterized queries — never string-format into SQL |
| Excessive data exposure | Information Disclosure | Response models explicitly list fields; `from_attributes=True` scoped to declared fields only |
| Denial of service via `per_page=10000` | Denial of Service | `Query(per_page, le=100)` hard cap on FastAPI query parameter |
| CORS misconfiguration | Elevation of Privilege | Hardcoded origin list in dev; env-var driven in prod (see Pitfall 6) |

---

## Sources

### Primary (HIGH confidence)
- FastAPI official docs (fastapi.tiangolo.com) — query params, response_model, include_router patterns
- SQLAlchemy 2.x async docs (docs.sqlalchemy.org/en/20/orm/extensions/asyncio) — select, func.count, scalars, offset/limit
- TanStack Query v5 official docs (tanstack.com/query/v5) — paginated queries, keepPreviousData, placeholderData
- shadcn/ui official docs (ui.shadcn.com) — Pagination, Card, Badge, Button, Select component APIs
- Pydantic v2 docs — ConfigDict, from_attributes
- PyPI registry — fastapi 0.115.14, sqlalchemy 2.0.49, alembic 1.18.4, pydantic 2.13.4 [VERIFIED: PyPI]
- npm registry — @tanstack/react-query 5.100.11, react-router-dom 7.15.1, tailwindcss 4.3.0, shadcn 4.8.0 [VERIFIED: npm registry]

### Secondary (MEDIUM confidence)
- Codebase inspection: `backend/app/routers/health.py`, `backend/app/main.py`, `backend/app/database.py`, `frontend/src/hooks/useHealth.ts`, `frontend/src/App.tsx`, `frontend/src/api/client.ts` — direct read confirms patterns
- `backend/app/models/*.py` — all model fields confirmed by direct read
- `frontend/components.json` — confirms shadcn configured with zinc base, CSS variables, `@/components` alias

### Tertiary (LOW confidence)
- None — all critical claims verified from official sources or direct codebase inspection.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified via PyPI/npm, all locked versions confirmed in requirements.txt and package.json
- Architecture: HIGH — patterns verified from FastAPI/SQLAlchemy/TanStack Query official docs and codebase inspection
- Pitfalls: HIGH — pitfall 1 (no Party slug) verified by direct model read; pitfall 2 (Pydantic v2 from_attributes) verified by installed pydantic version; pitfall 5 (TanStack v5 API) verified by official docs
- Open questions: MEDIUM — resolved by recommendation; planner should decide Party slug migration

**Research date:** 2026-05-22
**Valid until:** 2026-06-22 (stable stack; 30-day window)
