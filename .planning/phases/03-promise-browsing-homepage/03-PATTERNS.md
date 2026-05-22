# Phase 3: Promise Browsing & Homepage - Pattern Map

**Mapped:** 2026-05-23
**Files analyzed:** 16 new/modified files
**Analogs found:** 15 / 16 (1 novel: nginx.conf — no existing Nginx config in codebase)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `backend/app/routers/promises.py` | router | CRUD + request-response | `backend/app/routers/elections.py` | exact |
| `backend/app/routers/stats.py` | router | request-response (aggregate) | `backend/app/routers/politicians.py` (count pattern) | role-match |
| `backend/app/routers/og.py` | router | request-response (HTML response) | `backend/app/routers/elections.py` (slug lookup) | partial |
| `backend/app/schemas/promises.py` (modify) | schema | — | `backend/app/schemas/elections.py` | exact |
| `backend/app/main.py` (modify) | config | — | `backend/app/main.py` | exact |
| `frontend/src/pages/HomePage.tsx` (replace) | page | request-response | `frontend/src/pages/ElectionsListPage.tsx` | role-match |
| `frontend/src/pages/PromisesListPage.tsx` | page | request-response + filter | `frontend/src/pages/PersonsPage.tsx` | exact |
| `frontend/src/pages/FulfilledPage.tsx` | page | request-response | `frontend/src/pages/ElectionsListPage.tsx` | exact |
| `frontend/src/pages/UnfulfilledPage.tsx` | page | request-response | `frontend/src/pages/ElectionsListPage.tsx` | exact |
| `frontend/src/pages/PromiseDetailPage.tsx` | page | request-response | `frontend/src/pages/ElectionDetailPage.tsx` | exact |
| `frontend/src/pages/AboutPage.tsx` | page | static | `frontend/src/pages/ElectionsListPage.tsx` (structure only) | partial |
| `frontend/src/components/PromiseCard.tsx` | component | — | `frontend/src/components/PromiseStub.tsx` | exact |
| `frontend/src/hooks/usePromises.ts` | hook | request-response | `frontend/src/hooks/usePoliticians.ts` | exact |
| `frontend/src/hooks/usePromise.ts` | hook | request-response | `frontend/src/hooks/usePolitician.ts` | exact |
| `frontend/src/hooks/useStats.ts` | hook | request-response | `frontend/src/hooks/useElections.ts` | role-match |
| `frontend/src/types/index.ts` (modify) | types | — | `frontend/src/types/index.ts` | exact |
| `frontend/src/components/Layout.tsx` (modify) | component | — | `frontend/src/components/Layout.tsx` | exact |
| `frontend/src/App.tsx` (modify) | config | — | `frontend/src/App.tsx` | exact |
| `nginx/nginx.conf` | config | request-response (proxy) | no analog | none |
| `docker-compose.yml` (modify) | config | — | `docker-compose.yml` (existing services) | exact |
| `backend/tests/test_promises.py` | test | — | `backend/tests/test_elections.py` | exact |
| `backend/tests/test_stats.py` | test | — | `backend/tests/test_elections.py` | role-match |
| `backend/tests/test_og.py` | test | — | `backend/tests/test_elections.py` | role-match |

---

## Pattern Assignments

### `backend/app/routers/promises.py` (router, CRUD + request-response)

**Analog:** `backend/app/routers/elections.py`

**Imports pattern** (lines 1-10):
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.elections import Election
from app.models.promises import ModerationStatus, Promise, PromiseElectionLink, ResolvedStatus
from app.schemas.common import PaginatedResponse
from app.schemas.promises import PromiseListOut, PromiseDetailOut
```

**Router declaration pattern** (elections.py line 12):
```python
router = APIRouter(prefix="/promises", tags=["promises"])
```

**Multi-filter list pattern** — adapt from elections.py lines 15-65, adding conditional WHERE clauses. Key differences from elections.py: JOIN with `Politician` table; comma-split `status` param; 7 optional filter params:
```python
@router.get("", response_model=PaginatedResponse[PromiseListOut])
async def list_promises(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),           # comma-separated: "broken,stalled"
    politician_id: uuid.UUID | None = Query(None),
    election_id: uuid.UUID | None = Query(None),
    made_date_from: date | None = Query(None),
    made_date_to: date | None = Query(None),
    expected_date_from: date | None = Query(None),
    expected_date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PromiseListOut]:
    stmt = (
        select(Promise, Politician.name_hy.label("politician_name"), Politician.slug.label("politician_slug"))
        .join(Politician, Politician.id == Promise.politician_id)
        .where(Promise.moderation_status == ModerationStatus.approved)
    )
    if status:
        status_values = [ResolvedStatus(s.strip()) for s in status.split(",")]
        stmt = stmt.where(Promise.resolved_status.in_(status_values))
    if politician_id:
        stmt = stmt.where(Promise.politician_id == politician_id)
    if election_id:
        stmt = stmt.join(PromiseElectionLink, PromiseElectionLink.promise_id == Promise.id) \
                   .where(PromiseElectionLink.election_id == election_id)
    if made_date_from:
        stmt = stmt.where(Promise.made_date >= made_date_from)
    if made_date_to:
        stmt = stmt.where(Promise.made_date <= made_date_to)
    if expected_date_from:
        stmt = stmt.where(Promise.expected_date >= expected_date_from)
    if expected_date_to:
        stmt = stmt.where(Promise.expected_date <= expected_date_to)
```

**Count + paginate pattern** (elections.py lines 35-65 — copy exactly):
```python
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    stmt = stmt.order_by(Promise.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    items_result = await db.execute(stmt)
    rows = items_result.all()

    items = [
        PromiseListOut(
            id=promise.id,
            slug=promise.slug,
            title_hy=promise.title_hy,
            quote_hy=promise.quote_hy[:120] + "…" if len(promise.quote_hy) > 120 else promise.quote_hy,
            resolved_status=promise.resolved_status,
            politician_name_hy=politician_name,
            made_date=promise.made_date,
        )
        for promise, politician_name, politician_slug in rows
    ]

    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )
```

**Detail endpoint pattern** (elections.py lines 68-81 — adapt for JOIN + explicit construction):
```python
@router.get("/{slug}", response_model=PromiseDetailOut)
async def get_promise(slug: str, db: AsyncSession = Depends(get_db)) -> PromiseDetailOut:
    stmt = (
        select(Promise, Politician.name_hy.label("politician_name"),
               Politician.slug.label("politician_slug"))
        .join(Politician, Politician.id == Promise.politician_id)
        .where(
            Promise.slug == slug,
            Promise.moderation_status == ModerationStatus.approved,
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")
    promise, politician_name, politician_slug = row
    return PromiseDetailOut(
        id=promise.id,
        slug=promise.slug,
        title_hy=promise.title_hy,
        quote_hy=promise.quote_hy,
        resolved_status=promise.resolved_status,
        made_date=promise.made_date,
        expected_date=promise.expected_date,
        source_url=promise.source_url,
        archived_url=promise.archived_url,
        politician_name_hy=politician_name,
        politician_slug=politician_slug,
    )
```

**Error handling pattern** (elections.py line 79):
```python
    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")
```

---

### `backend/app/routers/stats.py` (router, aggregate request-response)

**Analog:** `backend/app/routers/politicians.py` (count subquery pattern, lines 33-36) + elections.py (router structure)

**Imports pattern**:
```python
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.promises import ModerationStatus, Promise, ResolvedStatus
from app.schemas.stats import StatsOut, StatsByStatus
```

**Router declaration**:
```python
router = APIRouter(prefix="/stats", tags=["stats"])
```

**Core aggregate pattern** — uses `func.count()` + `group_by` (same `func` import as elections.py):
```python
@router.get("", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsOut:
    stmt = (
        select(Promise.resolved_status, func.count().label("cnt"))
        .where(Promise.moderation_status == ModerationStatus.approved)
        .group_by(Promise.resolved_status)
    )
    result = await db.execute(stmt)
    rows = result.all()
    by_status = {r.resolved_status: r.cnt for r in rows}
    total = sum(by_status.values())
    return StatsOut(
        total=total,
        by_status=StatsByStatus(
            kept=by_status.get(ResolvedStatus.kept, 0),
            broken=by_status.get(ResolvedStatus.broken, 0),
            in_progress=by_status.get(ResolvedStatus.in_progress, 0),
            stalled=by_status.get(ResolvedStatus.stalled, 0),
            not_rated=by_status.get(ResolvedStatus.not_rated, 0),
        ),
    )
```

Note: `StatsOut` and `StatsByStatus` are new schemas in `backend/app/schemas/stats.py` — plain `BaseModel`, no `from_attributes`.

---

### `backend/app/routers/og.py` (router, HTML response)

**Analog:** `backend/app/routers/elections.py` (slug lookup + 404 pattern, lines 68-81)

**Imports pattern**:
```python
import html
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.politicians import Politician
from app.models.promises import ModerationStatus, Promise
```

**Router declaration**:
```python
router = APIRouter(prefix="/og", tags=["og"])
```

**Core HTML response pattern** — same slug lookup as elections.py detail; `response_class=HTMLResponse`; `html.escape()` on all string values:
```python
@router.get("/promises/{slug}", response_class=HTMLResponse)
async def og_promise(slug: str, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    stmt = (
        select(Promise, Politician.name_hy.label("politician_name"),
               Politician.photo_url.label("photo_url"))
        .join(Politician, Politician.id == Promise.politician_id)
        .where(
            Promise.slug == slug,
            Promise.moderation_status == ModerationStatus.approved,
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")
    promise, politician_name, photo_url = row

    title = html.escape(promise.title_hy)
    description = html.escape(promise.quote_hy[:150] + " — " + politician_name)
    image_url = photo_url or "https://khostumner.am/default-og-image.png"
    canonical_url = f"https://khostumner.am/promises/{promise.slug}"
    # ... return HTMLResponse with <meta og:*> tags
```

**Error handling pattern** — identical to elections.py / politicians.py:
```python
    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")
```

---

### `backend/app/schemas/promises.py` (schema, modify — add PromiseListOut, PromiseDetailOut)

**Analog:** `backend/app/schemas/elections.py` (lines 1-36)

**Critical pattern** — `ElectionWithCountOut` (elections.py lines 22-36) is a plain `BaseModel` with no `from_attributes` because it comes from Row tuples in a JOIN query. `PromiseListOut` and `PromiseDetailOut` MUST follow this exact pattern:

```python
# elections.py lines 22-36 — copy this "no from_attributes" pattern
class ElectionWithCountOut(BaseModel):
    """...NOTE: NOT a subclass...from_attributes does not apply here.
    Instances are constructed explicitly in the router from (Election, int) rows."""
    id: uuid.UUID
    name_hy: str
    # ...no model_config = {"from_attributes": True}
```

**New schemas to add** (append to existing `backend/app/schemas/promises.py`):
```python
import uuid
from datetime import date

from pydantic import BaseModel

from app.models.promises import ResolvedStatus


class PromiseListOut(BaseModel):
    """Promise list item — constructed from JOIN Row(Promise, politician_name, politician_slug).
    NO from_attributes: row tuples, not ORM objects."""
    id: uuid.UUID
    slug: str
    title_hy: str
    quote_hy: str          # first ~120 chars (truncated in router)
    resolved_status: ResolvedStatus
    politician_name_hy: str
    made_date: date | None


class PromiseDetailOut(BaseModel):
    """Promise detail — all fields + politician join data.
    NO from_attributes: constructed explicitly from JOIN row."""
    id: uuid.UUID
    slug: str
    title_hy: str
    quote_hy: str          # full text, no truncation
    resolved_status: ResolvedStatus
    made_date: date | None
    expected_date: date | None
    source_url: str
    archived_url: str | None
    politician_name_hy: str
    politician_slug: str
```

**Existing `PromiseStubOut`** (lines 8-17) stays unchanged — still used by politicians/parties/elections routers.

---

### `backend/app/main.py` (config, modify)

**Analog:** `backend/app/main.py` (lines 7-8, 34-36)

**Import line pattern** (line 7 — copy, extend list):
```python
# Current:
from app.routers import elections, health, parties, politicians
# New:
from app.routers import elections, health, og, parties, politicians, promises, stats
```

**include_router pattern** (lines 34-36 — copy three new lines):
```python
# Current:
app.include_router(elections.router, prefix="/api")
# Add:
app.include_router(promises.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(og.router, prefix="/api")
```

---

### `frontend/src/pages/HomePage.tsx` (page, replace)

**Analog:** `frontend/src/pages/ElectionsListPage.tsx` (loading/error/data state structure, lines 27-86)

**Imports pattern**:
```typescript
import { Link } from "react-router-dom"
import { useStats } from "@/hooks/useStats"
import { usePromises } from "@/hooks/usePromises"
import PromiseCard from "@/components/PromiseCard"
```

**Loading/error/data state pattern** (ElectionsListPage.tsx lines 27-56 — copy structure):
```typescript
// Three-state render: isLoading skeleton → isError message → data
if (isLoading) {
  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-20 bg-zinc-200 rounded animate-pulse" />
        ))}
      </div>
    </main>
  )
}
if (isError) {
  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <p className="text-sm text-red-600">Սխալ տեղի ունեցավ։ Խնդրում ենք կրկին փորձել։</p>
    </main>
  )
}
```

**Main className pattern** (ElectionsListPage.tsx line 59):
```typescript
<main className="max-w-4xl mx-auto px-4 py-8">
```

**Page structure**: two `<section>` blocks — stats block and recent promises list. Stats uses `useStats()`, recent promises uses `usePromises({ page: 1, perPage: 10 })`.

---

### `frontend/src/pages/PromisesListPage.tsx` (page, filter + request-response)

**Analog:** `frontend/src/pages/PersonsPage.tsx` (entire file, lines 1-154)

**Imports pattern** (PersonsPage.tsx lines 1-13):
```typescript
import { useSearchParams } from "react-router-dom"
import { AlertCircle } from "lucide-react"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import PaginationControls from "@/components/PaginationControls"
import PromiseCard from "@/components/PromiseCard"
import { usePromises } from "@/hooks/usePromises"
```

**useSearchParams + filter state pattern** (PersonsPage.tsx lines 22-55 — copy exactly, adapt param names):
```typescript
const [searchParams, setSearchParams] = useSearchParams()

const page = parseInt(searchParams.get("page") ?? "1", 10) || 1
const status = searchParams.get("status") || null
const politician_id = searchParams.get("politician_id") || null
const election_id = searchParams.get("election_id") || null
const made_date_from = searchParams.get("made_date_from") || null
const made_date_to = searchParams.get("made_date_to") || null
const expected_date_from = searchParams.get("expected_date_from") || null
const expected_date_to = searchParams.get("expected_date_to") || null
```

**handleXChange pattern** (PersonsPage.tsx lines 31-55 — copy for each filter):
```typescript
function handleStatusChange(value: string) {
  setSearchParams((prev) => {
    const next = new URLSearchParams(prev)
    if (value === "__all__") { next.delete("status") }
    else { next.set("status", value) }
    next.set("page", "1")
    return next
  })
}
```

**Filter row layout pattern** (PersonsPage.tsx lines 62-96):
```typescript
<div className="flex flex-wrap gap-4 mb-6">
  <div className="flex flex-col gap-1">
    <label className="text-xs text-zinc-500 font-medium">Կարգավիճակ</label>
    <Select value={status ?? "__all__"} onValueChange={handleStatusChange}>
      <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
      <SelectContent>
        <SelectItem value="__all__">Բոլոր կարգավիճակները</SelectItem>
        {/* status options */}
      </SelectContent>
    </Select>
  </div>
  {/* date range inputs using <Input type="date"> */}
</div>
```

**Loading/error/empty/data pattern** (PersonsPage.tsx lines 98-152 — copy structure exactly):
```typescript
{isLoading && ( /* pulse skeleton */ )}
{isError && ( /* AlertCircle + retry link */ )}
{!isLoading && !isError && data && (
  <>
    {data.items.length === 0 ? ( /* empty state */ ) : (
      <>
        <div className="space-y-0">
          {data.items.map((promise) => <PromiseCard key={promise.id} promise={promise} />)}
        </div>
        {data.pages > 1 && <PaginationControls currentPage={page} totalPages={data.pages} />}
      </>
    )}
  </>
)}
```

---

### `frontend/src/pages/FulfilledPage.tsx` (page, request-response, filtered)

**Analog:** `frontend/src/pages/ElectionsListPage.tsx` (entire file, lines 1-86)

**Pattern:** Same structure as ElectionsListPage. Hard-codes `status="kept"` in hook call. No filter UI. Uses `useSearchParams` for `page` only (same as ElectionsListPage.tsx lines 23-24):
```typescript
const [searchParams] = useSearchParams()
const page = parseInt(searchParams.get("page") ?? "1", 10) || 1
const { data, isLoading, isError } = usePromises({ page, status: "kept" })
```

**Loading/error/empty/data structure** (ElectionsListPage.tsx lines 27-86 — copy exactly, adapt heading to "Կատարված"):
```typescript
<h1 className="text-2xl font-semibold text-zinc-900 mb-6">Կատարված</h1>
```

**List rendering pattern** (ElectionsListPage.tsx lines 62-78 — adapt to `<PromiseCard>` instead of `<Card>`):
```typescript
<div className="space-y-0">
  {data.items.map((promise) => (
    <PromiseCard key={promise.id} promise={promise} />
  ))}
</div>
{data.pages > 1 && <PaginationControls currentPage={page} totalPages={data.pages} />}
```

---

### `frontend/src/pages/UnfulfilledPage.tsx` (page, request-response, multi-status)

**Analog:** `frontend/src/pages/ElectionsListPage.tsx` — identical pattern to FulfilledPage.tsx, except:
```typescript
const { data, isLoading, isError } = usePromises({ page, status: "broken,stalled" })
```
Heading: `"Չկատարված"`. Otherwise copy FulfilledPage.tsx exactly.

---

### `frontend/src/pages/PromiseDetailPage.tsx` (page, request-response + detail)

**Analog:** `frontend/src/pages/ElectionDetailPage.tsx` (entire file, lines 1-101) and `frontend/src/pages/PoliticianProfilePage.tsx` (lines 38-48 for error state)

**Imports pattern** (ElectionDetailPage.tsx lines 1-5):
```typescript
import { Link, useParams } from "react-router-dom"
import { usePromise } from "@/hooks/usePromise"
import ResolvedStatusBadge from "@/components/ResolvedStatusBadge"
```

**Slug extraction + hook call pattern** (ElectionDetailPage.tsx lines 19-23):
```typescript
const { slug } = useParams<{ slug: string }>()
const { data, isLoading, isError } = usePromise(slug!)
```

**Loading skeleton pattern** (ElectionDetailPage.tsx lines 29-40 — copy, adapt for promise fields):
```typescript
if (isLoading) {
  return (
    <main className="max-w-4xl mx-auto px-4 py-8 animate-pulse">
      <div className="h-7 w-64 bg-zinc-200 rounded mb-3" />
      <div className="h-20 w-full bg-zinc-200 rounded" />
    </main>
  )
}
```

**404/error state pattern** (PoliticianProfilePage.tsx lines 39-47):
```typescript
if (isError || !data) {
  return (
    <main className="max-w-4xl mx-auto px-4 py-8 text-center">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-4">Խոստումը չի գտնվել</h1>
      <Link to="/promises" className="text-blue-600 underline hover:text-blue-800 text-sm">
        Վերադառնալ խոստումների ցուցակ
      </Link>
    </main>
  )
}
```

**Detail content pattern** — hero quote approach (D-11): `title_hy` as `<h1>`, `quote_hy` as large blockquote, then metadata rows. Omit date rows if null (D-07b):
```typescript
return (
  <main className="max-w-4xl mx-auto px-4 py-8">
    <h1 className="text-2xl font-semibold text-zinc-900">{data.title_hy}</h1>
    <blockquote className="mt-4 text-lg text-zinc-800 border-l-4 border-zinc-300 pl-4">
      {data.quote_hy}
    </blockquote>
    <div className="mt-6 space-y-2">
      <div className="flex items-center gap-2">
        <ResolvedStatusBadge status={data.resolved_status} />
        <Link to={`/persons/${data.politician_slug}`} className="text-sm text-blue-600 underline">
          {data.politician_name_hy}
        </Link>
      </div>
      {data.made_date && <p className="text-sm text-zinc-500">Ասված է՝ {data.made_date}</p>}
      {data.expected_date && <p className="text-sm text-zinc-500">Կատարման ժամկետ՝ {data.expected_date}</p>}
      <a href={data.source_url} target="_blank" rel="noopener noreferrer"
         className="text-sm text-blue-600 underline">Աղբյուր</a>
      {data.archived_url && (
        <a href={data.archived_url} target="_blank" rel="noopener noreferrer"
           className="text-sm text-zinc-500 underline ml-3">Wayback Machine</a>
      )}
    </div>
  </main>
)
```

---

### `frontend/src/pages/AboutPage.tsx` (page, static)

**Analog:** `frontend/src/pages/ElectionsListPage.tsx` (page shell structure only — lines 58-60)

No API calls. Simple static content page:
```typescript
export default function AboutPage() {
  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Մեր մասին</h1>
      {/* TODO: Replace with content from "Our Principles" file in project root */}
      <p className="text-zinc-700">...</p>
    </main>
  )
}
```

---

### `frontend/src/components/PromiseCard.tsx` (component)

**Analog:** `frontend/src/components/PromiseStub.tsx` (entire file, lines 1-22)

**Imports pattern** (PromiseStub.tsx lines 1-3):
```typescript
import { Link } from "react-router-dom"
import type { PromiseListOut } from "@/types"
import ResolvedStatusBadge from "./ResolvedStatusBadge"
```

**Truncation pattern** (PromiseStub.tsx line 11 — same 120-char limit):
```typescript
const truncated =
  promise.quote_hy.length > 120 ? promise.quote_hy.slice(0, 120) + "…" : promise.quote_hy
```

**Link + layout pattern** (PromiseStub.tsx lines 14-21 — extend for `title_hy` and `politician_name_hy`):
```typescript
return (
  <Link
    to={`/promises/${promise.slug}`}
    className="flex justify-between items-start border-b border-zinc-100 py-3 hover:bg-zinc-50 cursor-pointer"
  >
    <div className="flex-1 mr-4">
      <p className="text-sm font-semibold text-zinc-900">{promise.title_hy}</p>
      <p className="text-sm text-zinc-700 line-clamp-2">{truncated}</p>
      {promise.made_date && (
        <p className="text-xs text-zinc-400 mt-1">{promise.politician_name_hy} · {promise.made_date}</p>
      )}
    </div>
    <ResolvedStatusBadge status={promise.resolved_status} />
  </Link>
)
```

---

### `frontend/src/hooks/usePromises.ts` (hook, list with multi-param filter)

**Analog:** `frontend/src/hooks/usePoliticians.ts` (entire file, lines 1-27)

**Imports pattern** (usePoliticians.ts lines 1-3):
```typescript
import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, PromiseListOut } from "@/types"
```

**Params interface + hook pattern** (usePoliticians.ts lines 5-27 — copy, extend params):
```typescript
interface UsePromisesParams {
  page: number
  perPage?: number
  status?: string | null
  politician_id?: string | null
  election_id?: string | null
  made_date_from?: string | null
  made_date_to?: string | null
  expected_date_from?: string | null
  expected_date_to?: string | null
}

export function usePromises({ page, perPage = 20, status, politician_id, election_id,
    made_date_from, made_date_to, expected_date_from, expected_date_to }: UsePromisesParams) {
  return useQuery<PaginatedResponse<PromiseListOut>>({
    queryKey: ["promises", { page, perPage, status, politician_id, election_id,
      made_date_from, made_date_to, expected_date_from, expected_date_to }],
    queryFn: () => {
      const params = new URLSearchParams()
      params.set("page", String(page))
      params.set("per_page", String(perPage))
      if (status) params.set("status", status)
      if (politician_id) params.set("politician_id", politician_id)
      if (election_id) params.set("election_id", election_id)
      if (made_date_from) params.set("made_date_from", made_date_from)
      if (made_date_to) params.set("made_date_to", made_date_to)
      if (expected_date_from) params.set("expected_date_from", expected_date_from)
      if (expected_date_to) params.set("expected_date_to", expected_date_to)
      return apiClient.get<PaginatedResponse<PromiseListOut>>(`/api/promises?${params}`)
    },
    placeholderData: keepPreviousData,
  })
}
```

---

### `frontend/src/hooks/usePromise.ts` (hook, single detail)

**Analog:** `frontend/src/hooks/usePolitician.ts` (entire file, lines 1-13) and `frontend/src/hooks/useElection.ts` (lines 1-13)

**Copy exactly** (usePolitician.ts lines 1-13), changing type and endpoint:
```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PromiseDetailOut } from "@/types"

export function usePromise(slug: string) {
  const { data, isLoading, isError } = useQuery<PromiseDetailOut>({
    queryKey: ["promise", slug],
    queryFn: () => apiClient.get<PromiseDetailOut>(`/api/promises/${slug}`),
    enabled: Boolean(slug),
  })
  return { data, isLoading, isError }
}
```

---

### `frontend/src/hooks/useStats.ts` (hook, single endpoint no params)

**Analog:** `frontend/src/hooks/useElections.ts` (lines 1-14) — simplified (no `page` param, no `keepPreviousData`):
```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { StatsOut } from "@/types"

export function useStats() {
  const { data, isLoading, isError } = useQuery<StatsOut>({
    queryKey: ["stats"],
    queryFn: () => apiClient.get<StatsOut>("/api/stats"),
    staleTime: 5 * 60 * 1000,  // stats can be stale for 5 min on homepage
  })
  return { data, isLoading, isError }
}
```

---

### `frontend/src/types/index.ts` (modify — add new interfaces)

**Analog:** `frontend/src/types/index.ts` (existing lines 55-61 — `PromiseStubOut` pattern)

**Append to existing file** — follow same interface style (string for UUID, string for date):
```typescript
export interface PromiseListOut {
  id: string
  slug: string
  title_hy: string
  quote_hy: string          // pre-truncated to ~120 chars by router
  resolved_status: "not_rated" | "kept" | "broken" | "in_progress" | "stalled"
  politician_name_hy: string
  made_date: string | null
}

export interface PromiseDetailOut {
  id: string
  slug: string
  title_hy: string
  quote_hy: string          // full text
  resolved_status: "not_rated" | "kept" | "broken" | "in_progress" | "stalled"
  made_date: string | null
  expected_date: string | null
  source_url: string
  archived_url: string | null
  politician_name_hy: string
  politician_slug: string
}

export interface StatsByStatus {
  kept: number
  broken: number
  in_progress: number
  stalled: number
  not_rated: number
}

export interface StatsOut {
  total: number
  by_status: StatsByStatus
}
```

---

### `frontend/src/components/Layout.tsx` (modify — add Մեր մասին nav link)

**Analog:** `frontend/src/components/Layout.tsx` (lines 25-26 — existing NavLink pattern)

**Copy pattern** from existing NavLink entries (lines 13-26), append last in nav:
```typescript
// Existing pattern to copy:
<NavLink to="/elections" className={navLinkClass}>
  Ընտրություններ
</NavLink>
// Add after this:
<NavLink to="/about" className={navLinkClass}>
  Մեր մասին
</NavLink>
```

---

### `frontend/src/App.tsx` (modify — add new routes)

**Analog:** `frontend/src/App.tsx` (lines 14-21 — existing Route entries)

**Copy pattern** (lines 14-21 — add 5 new Route entries):
```typescript
// Existing pattern:
<Route path="/elections/:slug" element={<ElectionDetailPage />} />
// Add these routes inside the Layout Route:
<Route path="/" element={<HomePage />} />               // replaces existing
<Route path="/promises" element={<PromisesListPage />} />
<Route path="/fulfilled" element={<FulfilledPage />} />
<Route path="/unfulfilled" element={<UnfulfilledPage />} />
<Route path="/promises/:slug" element={<PromiseDetailPage />} />
<Route path="/about" element={<AboutPage />} />
```

Note: The `/` route already exists (line 15) pointing to the current `HomePage`. Replace its element — don't add a duplicate.

---

### `nginx/nginx.conf` (config, new file — no analog)

**No existing analog.** Pattern from RESEARCH.md Architecture Patterns section (Pattern 4). Use `map` + `if ($is_bot)` approach:
```nginx
map $http_user_agent $is_bot {
    default     0;
    "~*Facebookbot"   1;
    "~*Twitterbot"    1;
    "~*TelegramBot"   1;
    "~*LinkedInBot"   1;
    "~*Googlebot"     1;
}

server {
    listen 80;

    location ~* ^/promises/(.+)$ {
        if ($is_bot) {
            proxy_pass http://backend:8000/api/og/promises/$1;
            break;
        }
        proxy_pass http://frontend:5173;
    }

    location / {
        proxy_pass http://frontend:5173;
    }
}
```

**See RESEARCH.md Pitfall 3** for `if` + `proxy_pass` caveats.

---

### `docker-compose.yml` (modify — add nginx service)

**Analog:** `docker-compose.yml` (existing `frontend` service block, lines 44-58)

**Copy service block pattern** (lines 23-42 — backend service structure) and adapt:
```yaml
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

**Network note:** All services in this compose file share the default network automatically (no explicit `networks:` key). Nginx reaches `backend:8000` and `frontend:5173` by service name.

---

### `backend/tests/test_promises.py` (test)

**Analog:** `backend/tests/test_elections.py` (entire file, lines 1-36) and `backend/tests/conftest.py`

**Test structure pattern** (test_elections.py lines 9-35 — copy exactly, adapt assertions):
```python
import pytest

@pytest.mark.asyncio
async def test_list_promises(client):
    response = await client.get("/api/promises")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "pages" in body

@pytest.mark.asyncio
async def test_list_promises_filter_status(client):
    response = await client.get("/api/promises?status=kept")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["resolved_status"] == "kept"

@pytest.mark.asyncio
async def test_list_promises_multi_status(client):
    response = await client.get("/api/promises?status=broken,stalled")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["resolved_status"] in ("broken", "stalled")

@pytest.mark.asyncio
async def test_list_promises_moderation_filter(client):
    # Must never return non-approved promises
    response = await client.get("/api/promises")
    assert response.status_code == 200
    # All items must come from approved promises only — verified via seed data

@pytest.mark.asyncio
async def test_get_promise_not_found(client):
    response = await client.get("/api/promises/nonexistent-slug")
    assert response.status_code == 404
    assert response.json()["detail"] == "Promise not found"
```

**conftest.py client fixture** (conftest.py lines 1-9) — reused unchanged.

---

### `backend/tests/test_stats.py` (test)

**Analog:** `backend/tests/test_elections.py` (structure only)

```python
import pytest

@pytest.mark.asyncio
async def test_get_stats(client):
    response = await client.get("/api/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "by_status" in body
    for key in ("kept", "broken", "in_progress", "stalled", "not_rated"):
        assert key in body["by_status"]
```

---

### `backend/tests/test_og.py` (test)

**Analog:** `backend/tests/test_elections.py` (not-found pattern, lines 25-28)

```python
import pytest

@pytest.mark.asyncio
async def test_og_promise_not_found(client):
    response = await client.get("/api/og/promises/nonexistent-slug")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_og_promise_returns_html(client):
    # Requires a known slug from seed data — skip if no seed
    # Full test validates og:title and og:description are present in body
    response = await client.get("/api/og/promises/some-seed-slug")
    if response.status_code == 200:
        assert "og:title" in response.text
        assert "og:description" in response.text
```

---

## Shared Patterns

### Moderation Guard (Apply to ALL public promise queries)
**Source:** `backend/app/routers/elections.py` lines 101-107 and `backend/app/routers/politicians.py` lines 87-90
**Apply to:** `promises.py` router (list + detail), `stats.py` router, `og.py` router
```python
# CRITICAL — Never omit this on public endpoints
Promise.moderation_status == ModerationStatus.approved
```

### PaginatedResponse Envelope
**Source:** `backend/app/schemas/common.py` lines 1-15
**Apply to:** `promises.py` list endpoint
```python
return PaginatedResponse(items=items, total=total, page=page, per_page=per_page, pages=pages)
```

### Count-via-Subquery Pattern
**Source:** `backend/app/routers/politicians.py` lines 33-35 and `backend/app/routers/elections.py` line 110
**Apply to:** `promises.py` list endpoint
```python
count_stmt = select(func.count()).select_from(stmt.subquery())
total_result = await db.execute(count_stmt)
total: int = total_result.scalar_one()
```

### Plain BaseModel for JOIN Results (No from_attributes)
**Source:** `backend/app/schemas/elections.py` lines 22-36 (`ElectionWithCountOut` docstring + class)
**Apply to:** `PromiseListOut`, `PromiseDetailOut` schemas
```python
# DO NOT add: model_config = {"from_attributes": True}
# Construct explicitly in router from unpacked row tuple:
promise, politician_name, politician_slug = row
return PromiseDetailOut(id=promise.id, ..., politician_name_hy=politician_name)
```

### TanStack Query Hook Shape
**Source:** `frontend/src/hooks/usePolitician.ts` lines 5-13 and `frontend/src/hooks/useElections.ts` lines 5-14
**Apply to:** `usePromises.ts`, `usePromise.ts`, `useStats.ts`
```typescript
return { data, isLoading, isError }   // always destructure to this shape
```
Always use `keepPreviousData` on list hooks (avoids flicker on page change). Use `enabled: Boolean(slug)` on detail hooks.

### useSearchParams Filter Pattern
**Source:** `frontend/src/pages/PersonsPage.tsx` lines 22-55
**Apply to:** `PromisesListPage.tsx`
```typescript
// Read from URL:
const value = searchParams.get("paramName") || null
// Write to URL (always reset page to 1):
setSearchParams((prev) => {
  const next = new URLSearchParams(prev)
  if (value === "__all__") { next.delete("paramName") } else { next.set("paramName", value) }
  next.set("page", "1")
  return next
})
```

### Loading/Error/Empty/Data State Pattern
**Source:** `frontend/src/pages/ElectionsListPage.tsx` lines 27-56
**Apply to:** `FulfilledPage.tsx`, `UnfulfilledPage.tsx`, `HomePage.tsx`
```typescript
if (isLoading) { return <main>/* pulse skeleton */</main> }
if (isError) { return <main><p className="text-sm text-red-600">Սխալ...</p></main> }
if (!data || data.items.length === 0) { return <main><p>...Դատ...</p></main> }
return <main>/* full content */</main>
```

### Page Container Class
**Source:** `frontend/src/pages/ElectionsListPage.tsx` line 59, `frontend/src/pages/PoliticianProfilePage.tsx` line 51
**Apply to:** All new page components
```typescript
<main className="max-w-4xl mx-auto px-4 py-8">
```

### NavLink Pattern
**Source:** `frontend/src/components/Layout.tsx` lines 6-7, 13-28
**Apply to:** New "Մեր մասին" nav link in Layout.tsx
```typescript
const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? "text-sm font-semibold text-zinc-900" : "text-sm text-zinc-600 hover:text-zinc-900"
// ...
<NavLink to="/about" className={navLinkClass}>Մեր մասին</NavLink>
```

### Test Client Fixture
**Source:** `backend/tests/conftest.py` lines 1-9
**Apply to:** All new test files — import fixture automatically, no changes needed
```python
# conftest.py reused as-is — pytest discovers fixtures automatically
@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `nginx/nginx.conf` | config | request-response (reverse proxy) | No Nginx configuration exists in the project. No existing proxy layer. Pattern sourced from RESEARCH.md Pattern 4 + general Nginx knowledge. |

---

## Metadata

**Analog search scope:** `backend/app/routers/`, `backend/app/schemas/`, `backend/app/models/`, `backend/tests/`, `frontend/src/pages/`, `frontend/src/hooks/`, `frontend/src/components/`, `frontend/src/types/`, root `docker-compose.yml`
**Files scanned:** 23 files read directly
**Pattern extraction date:** 2026-05-23
