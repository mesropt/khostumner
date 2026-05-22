# Phase 2: Politicians, Parties & Elections Browsing - Pattern Map

**Mapped:** 2026-05-22
**Files analyzed:** 21 new/modified files
**Analogs found:** 16 / 21

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `backend/app/routers/politicians.py` | router | request-response | `backend/app/routers/health.py` | role-match |
| `backend/app/routers/parties.py` | router | request-response | `backend/app/routers/health.py` | role-match |
| `backend/app/routers/elections.py` | router | request-response | `backend/app/routers/health.py` | role-match |
| `backend/app/schemas/politicians.py` | schema | transform | `backend/app/schemas/health.py` | role-match |
| `backend/app/schemas/parties.py` | schema | transform | `backend/app/schemas/health.py` | role-match |
| `backend/app/schemas/elections.py` | schema | transform | `backend/app/schemas/health.py` | role-match |
| `backend/app/schemas/common.py` | schema | transform | `backend/app/schemas/health.py` | role-match |
| `backend/app/schemas/promises.py` | schema | transform | `backend/app/schemas/health.py` | role-match |
| `backend/app/main.py` (modify) | config | request-response | `backend/app/main.py` | exact |
| `backend/alembic/versions/*_add_party_slug.py` | migration | CRUD | `backend/alembic/versions/20260521_000001_initial_schema.py` | role-match |
| `backend/tests/test_politicians.py` | test | request-response | `backend/tests/test_health.py` | role-match |
| `backend/tests/test_parties.py` | test | request-response | `backend/tests/test_health.py` | role-match |
| `backend/tests/test_elections.py` | test | request-response | `backend/tests/test_health.py` | role-match |
| `frontend/src/App.tsx` (modify) | config | request-response | `frontend/src/App.tsx` | exact |
| `frontend/src/components/Layout.tsx` | component | request-response | `frontend/src/pages/NotFoundPage.tsx` | partial |
| `frontend/src/components/PoliticianCard.tsx` | component | request-response | `frontend/src/pages/HomePage.tsx` | partial |
| `frontend/src/components/PromiseStub.tsx` | component | request-response | `frontend/src/pages/HomePage.tsx` | partial |
| `frontend/src/components/PaginationControls.tsx` | component | request-response | no analog | none |
| `frontend/src/components/Avatar.tsx` | component | transform | no analog | none |
| `frontend/src/hooks/usePoliticians.ts` | hook | request-response | `frontend/src/hooks/useHealth.ts` | role-match |
| `frontend/src/hooks/usePolitician.ts` | hook | request-response | `frontend/src/hooks/useHealth.ts` | role-match |
| `frontend/src/hooks/useParty.ts` | hook | request-response | `frontend/src/hooks/useHealth.ts` | role-match |
| `frontend/src/hooks/useElections.ts` | hook | request-response | `frontend/src/hooks/useHealth.ts` | role-match |
| `frontend/src/hooks/useElection.ts` | hook | request-response | `frontend/src/hooks/useHealth.ts` | role-match |
| `frontend/src/pages/PersonsPage.tsx` | page | request-response | `frontend/src/pages/HomePage.tsx` | role-match |
| `frontend/src/pages/PoliticianProfilePage.tsx` | page | request-response | `frontend/src/pages/HomePage.tsx` | role-match |
| `frontend/src/pages/PartyPage.tsx` | page | request-response | `frontend/src/pages/HomePage.tsx` | role-match |
| `frontend/src/pages/ElectionsListPage.tsx` | page | request-response | `frontend/src/pages/HomePage.tsx` | role-match |
| `frontend/src/pages/ElectionDetailPage.tsx` | page | request-response | `frontend/src/pages/HomePage.tsx` | role-match |
| `frontend/src/types/index.ts` (modify) | utility | transform | `frontend/src/types/index.ts` | exact |

---

## Pattern Assignments

### `backend/app/routers/politicians.py` (router, request-response)

**Analog:** `backend/app/routers/health.py`

**Imports pattern** (health.py lines 1-3 — extend this with DB imports):
```python
from fastapi import APIRouter

router = APIRouter()
```

Extend to:
```python
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
```

**Core router pattern** (health.py lines 6-8 — replicate with async + db dep):
```python
@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

Replicate as:
```python
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

@router.get("/{slug}/promises", response_model=PaginatedResponse[PromiseStubOut])
async def get_politician_promises(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    pol_result = await db.execute(select(Politician).where(Politician.slug == slug))
    politician = pol_result.scalars().first()
    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")

    stmt = select(Promise).where(
        Promise.politician_id == politician.id,
        Promise.moderation_status == ModerationStatus.approved,
    )
    total = (await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )).scalar() or 0
    items = (await db.execute(
        stmt.order_by(Promise.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return PaginatedResponse(
        items=items, total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )
```

**Error handling pattern** — use `HTTPException` directly (no AppError wrapper exists in this project):
```python
raise HTTPException(status_code=404, detail="Politician not found")
```

**DB session pattern** from `backend/app/database.py` lines 25-32:
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```
The `get_db` dependency is already wired — import and use as-is with `Depends(get_db)`.

---

### `backend/app/routers/parties.py` (router, request-response)

**Analog:** `backend/app/routers/health.py`

Follow the exact same structure as `politicians.py` above, adapted for the `Party` model.

**Imports:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models.parties import Party
from app.models.politicians import Politician
from app.models.promises import Promise, ModerationStatus
from app.schemas.parties import PartyOut, PartyListItemOut
from app.schemas.politicians import PoliticianOut
from app.schemas.promises import PromiseStubOut
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/parties", tags=["parties"])
```

**Endpoints:**
- `GET /parties` — list all parties (used for the Party filter dropdown on PersonsPage; no pagination needed, small dataset)
- `GET /parties/{slug}` — party detail (after slug migration)
- `GET /parties/{slug}/politicians` — members list (no pagination needed initially, small count)
- `GET /parties/{slug}/promises` — paginated promises with `moderation_status=approved` filter

**Key constraint (Pitfall 1):** `Party` model (`backend/app/models/parties.py` lines 9-18) has no `slug` field. The migration `*_add_party_slug.py` must run first. Until then the route parameter must use `id` (UUID). After migration, switch to slug.

---

### `backend/app/routers/elections.py` (router, request-response)

**Analog:** `backend/app/routers/health.py`

**Imports:**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.elections import Election
from app.models.promises import Promise, PromiseElectionLink, ModerationStatus
from app.schemas.elections import ElectionOut, ElectionWithCountOut
from app.schemas.promises import PromiseStubOut
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/elections", tags=["elections"])
```

**Promise-count subquery** (Election already has `slug` — `backend/app/models/elections.py` lines 22-23):
```python
promise_count = (
    select(func.count())
    .where(PromiseElectionLink.election_id == Election.id)
    .correlate(Election)
    .scalar_subquery()
    .label("promise_count")
)

stmt = select(Election, promise_count).order_by(Election.election_date.desc())
```

**Election detail with linked promises:**
```python
@router.get("/{slug}/promises", response_model=PaginatedResponse[PromiseStubOut])
async def get_election_promises(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    election_result = await db.execute(select(Election).where(Election.slug == slug))
    election = election_result.scalars().first()
    if not election:
        raise HTTPException(status_code=404, detail="Election not found")

    stmt = (
        select(Promise)
        .join(PromiseElectionLink, PromiseElectionLink.promise_id == Promise.id)
        .where(
            PromiseElectionLink.election_id == election.id,
            Promise.moderation_status == ModerationStatus.approved,
        )
    )
    total = (await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )).scalar() or 0
    items = (await db.execute(
        stmt.order_by(Promise.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )).scalars().all()
    return PaginatedResponse(
        items=items, total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )
```

---

### `backend/app/schemas/common.py` (schema, transform)

**Analog:** `backend/app/schemas/health.py` (lines 1-4)

`health.py` establishes the minimal Pydantic pattern: `from pydantic import BaseModel` + simple class. Extend with Generic:

```python
from pydantic import BaseModel
```

New file (`common.py`) adds Generic:
```python
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

Note: No `model_config = ConfigDict(from_attributes=True)` needed here — `PaginatedResponse` is constructed manually from Python dicts/lists, not from an ORM object directly.

---

### `backend/app/schemas/politicians.py` (schema, transform)

**Analog:** `backend/app/schemas/health.py` (lines 1-4)

`health.py` shows the baseline:
```python
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
```

Extend with ORM mapping — **critical difference**: `health.py` does NOT use `from_attributes=True` because it returns a plain dict. Every schema wrapping an ORM model MUST add `model_config`:

```python
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

Fields sourced from `backend/app/models/politicians.py` lines 20-38.

---

### `backend/app/schemas/parties.py` (schema, transform)

**Analog:** `backend/app/schemas/health.py`

Fields sourced from `backend/app/models/parties.py` lines 9-18. After slug migration, add `slug: str` field.

```python
from pydantic import BaseModel, ConfigDict
import uuid

class PartyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    short_name_hy: str | None
    logo_url: str | None
    founded_year: int | None
    is_active: bool
    slug: str  # added by migration — include after migration runs
```

`PartyListItemOut` (for the filter dropdown, minimal fields):
```python
class PartyListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    short_name_hy: str | None
```

---

### `backend/app/schemas/elections.py` (schema, transform)

**Analog:** `backend/app/schemas/health.py`

Fields sourced from `backend/app/models/elections.py` lines 17-31. Election already has `slug`.

```python
from pydantic import BaseModel, ConfigDict
import uuid
from datetime import date
from app.models.elections import ElectionLevel

class ElectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    slug: str
    election_date: date
    level: ElectionLevel
    description_hy: str | None

class ElectionWithCountOut(ElectionOut):
    promise_count: int  # from correlated subquery label
```

Note: `ElectionWithCountOut` will be constructed from a `Row` tuple `(Election, int)`, not a plain ORM object. The router will unpack the row and pass fields explicitly, or use `model_validate`.

---

### `backend/app/schemas/promises.py` (schema, transform)

**Analog:** `backend/app/schemas/health.py`

Minimal stub for public display (truncated quote + status). Fields from `backend/app/models/promises.py` lines 34-49.

```python
from pydantic import BaseModel, ConfigDict
import uuid
from app.models.promises import ResolvedStatus

class PromiseStubOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title_hy: str
    quote_hy: str  # frontend truncates to ~120 chars
    resolved_status: ResolvedStatus
```

---

### `backend/app/main.py` (modify, config)

**Analog:** `backend/app/main.py` itself (lines 1-33 — exact match)

The `include_router` call pattern is at line 33:
```python
app.include_router(health.router)
```

Add the three new routers after the health import. The new routers use a `/api` prefix set on the router itself (via `prefix="/politicians"` etc.) so `include_router` wraps them with the `/api` prefix:
```python
from app.routers import health, politicians, parties, elections

app.include_router(health.router)
app.include_router(politicians.router, prefix="/api")
app.include_router(parties.router, prefix="/api")
app.include_router(elections.router, prefix="/api")
```

Also update the CORS `allow_origins` to read from settings (Pitfall 6):
```python
# Replace hardcoded line 27:
allow_origins=["http://localhost:5173"],
# With env-driven:
allow_origins=settings.CORS_ORIGINS,  # add CORS_ORIGINS list to app/config.py
```

---

### `backend/alembic/versions/*_add_party_slug.py` (migration, CRUD)

**Analog:** `backend/alembic/versions/20260521_000001_initial_schema.py`

Naming convention from existing migration (line 16): `revision: str = "20260521_000001"`. Use timestamp-based ID. Copy the file header:

```python
"""add_party_slug

Revision ID: 20260522_000001
Revises: 20260521_000001
Create Date: 2026-05-22 00:00:01.000000
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "20260522_000001"
down_revision: Union[str, None] = "20260521_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add slug column to parties (nullable first so existing rows don't violate NOT NULL)
    op.add_column("parties", sa.Column("slug", sa.String(length=200), nullable=True))
    # Populate slugs for existing seed rows via SQL UPDATE (slugs are ASCII transliterations)
    op.execute("""
        UPDATE parties SET slug = lower(regexp_replace(name_hy, '[^a-zA-Z0-9]+', '-', 'g'))
        WHERE slug IS NULL
    """)
    # Add unique constraint and make non-nullable
    op.alter_column("parties", "slug", nullable=False)
    op.create_unique_constraint(op.f("uq__parties__slug"), "parties", ["slug"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq__parties__slug"), "parties", type_="unique")
    op.drop_column("parties", "slug")
```

Note: The `regexp_replace` UPDATE is a fallback for seed rows only. Production slugs must be set explicitly. The seed script (`backend/app/seeds/`) should set slugs directly in seed data — check if seed script needs updating too.

---

### `backend/tests/test_politicians.py` (test, request-response)

**Analog:** `backend/tests/test_health.py` (lines 1-14)

Copy the full `test_health.py` pattern — `AsyncClient` + `ASGITransport` + `@pytest.mark.asyncio`:

```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_list_politicians():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/politicians")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "per_page" in body
    assert "pages" in body


@pytest.mark.asyncio
async def test_filter_by_party():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/politicians?party=<valid_uuid>")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_politician_not_found():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/politicians/does-not-exist")
    assert response.status_code == 404
```

Note: `conftest.py` (`backend/tests/conftest.py` lines 1-9) has a reusable `client` fixture — prefer using the fixture in new tests:
```python
@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
```

New test files should use `async def test_xxx(client)` with the shared fixture rather than repeating the `AsyncClient` setup inline.

---

### `frontend/src/App.tsx` (modify, config)

**Analog:** `frontend/src/App.tsx` itself (lines 1-12 — exact match)

Current structure (lines 1-12):
```tsx
import { Routes, Route } from "react-router-dom"
import HomePage from "@/pages/HomePage"
import NotFoundPage from "@/pages/NotFoundPage"

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
```

Add Layout wrapper and Phase 2 routes — keep `<Route path="*">` last:
```tsx
import { Routes, Route } from "react-router-dom"
import Layout from "@/components/Layout"
import HomePage from "@/pages/HomePage"
import NotFoundPage from "@/pages/NotFoundPage"
import PersonsPage from "@/pages/PersonsPage"
import PoliticianProfilePage from "@/pages/PoliticianProfilePage"
import PartyPage from "@/pages/PartyPage"
import ElectionsListPage from "@/pages/ElectionsListPage"
import ElectionDetailPage from "@/pages/ElectionDetailPage"

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/persons" element={<PersonsPage />} />
        <Route path="/persons/:slug" element={<PoliticianProfilePage />} />
        <Route path="/parties/:slug" element={<PartyPage />} />
        <Route path="/elections" element={<ElectionsListPage />} />
        <Route path="/elections/:slug" element={<ElectionDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
```

Note: Using React Router v7 outlet pattern — `Layout` renders `<Outlet />` instead of `{children}`. See Layout section below.

---

### `frontend/src/components/Layout.tsx` (component, request-response)

**Analog:** `frontend/src/pages/NotFoundPage.tsx` (lines 1-8) — closest existing component using Tailwind + `<main>` wrapper.

`NotFoundPage.tsx` structure:
```tsx
export default function NotFoundPage() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
      <p className="text-xl text-gray-600">Էջը չի գտնվել</p>
    </main>
  )
}
```

`Layout.tsx` extends this with React Router `<Outlet />` (v7 pattern) and nav (D-01, D-02, D-03):
```tsx
import { Link, Outlet } from "react-router-dom"

export default function Layout() {
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
        <Outlet />
      </main>
    </div>
  )
}
```

`/fulfilled` and `/unfulfilled` links hit `<NotFoundPage>` until Phase 3. That is intentional per D-02.

---

### `frontend/src/hooks/usePoliticians.ts` (hook, request-response)

**Analog:** `frontend/src/hooks/useHealth.ts` (lines 1-17 — full file)

`useHealth.ts` is the canonical hook pattern:
```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { HealthResponse } from "@/types"

export function useHealth() {
  const { data, isLoading, isError } = useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: () => apiClient.get<HealthResponse>("/health"),
    retry: 3,
  })

  return {
    status: data?.status ?? null,
    isLoading,
    isError,
  }
}
```

Replicate for paginated list — key differences: `queryKey` includes filter params, add `placeholderData: keepPreviousData` (TanStack v5 API — Pitfall 5), build query string from `URLSearchParams`:

```typescript
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

---

### `frontend/src/hooks/usePolitician.ts` (hook, request-response)

**Analog:** `frontend/src/hooks/useHealth.ts` (lines 1-17)

Detail hook — no pagination, but may 404. Use same `useQuery` pattern, `queryKey: ["politician", slug]`:

```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PoliticianOut } from "@/types"

export function usePolitician(slug: string) {
  return useQuery<PoliticianOut>({
    queryKey: ["politician", slug],
    queryFn: () => apiClient.get<PoliticianOut>(`/api/politicians/${slug}`),
    enabled: Boolean(slug),
  })
}
```

---

### `frontend/src/hooks/useParty.ts` (hook, request-response)

**Analog:** `frontend/src/hooks/useHealth.ts` (lines 1-17)

```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PartyOut } from "@/types"

export function useParty(slug: string) {
  return useQuery<PartyOut>({
    queryKey: ["party", slug],
    queryFn: () => apiClient.get<PartyOut>(`/api/parties/${slug}`),
    enabled: Boolean(slug),
  })
}
```

---

### `frontend/src/hooks/useElections.ts` (hook, request-response)

**Analog:** `frontend/src/hooks/useHealth.ts` (lines 1-17)

```typescript
import { useQuery, keepPreviousData } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PaginatedResponse, ElectionWithCountOut } from "@/types"

export function useElections(page: number = 1) {
  return useQuery<PaginatedResponse<ElectionWithCountOut>>({
    queryKey: ["elections", { page }],
    queryFn: () => apiClient.get<PaginatedResponse<ElectionWithCountOut>>(`/api/elections?page=${page}`),
    placeholderData: keepPreviousData,
  })
}
```

---

### `frontend/src/hooks/useElection.ts` (hook, request-response)

**Analog:** `frontend/src/hooks/useHealth.ts` (lines 1-17)

```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { ElectionOut } from "@/types"

export function useElection(slug: string) {
  return useQuery<ElectionOut>({
    queryKey: ["election", slug],
    queryFn: () => apiClient.get<ElectionOut>(`/api/elections/${slug}`),
    enabled: Boolean(slug),
  })
}
```

---

### `frontend/src/pages/PersonsPage.tsx` (page, request-response)

**Analog:** `frontend/src/pages/HomePage.tsx` (lines 1-24)

`HomePage.tsx` establishes the page component pattern: import hook, destructure `{ data, isLoading, isError }`, render loading/error/data states with Tailwind classes.

`HomePage.tsx` core pattern (lines 1-24):
```tsx
import { useHealth } from "@/hooks/useHealth"

export default function HomePage() {
  const { status, isLoading, isError } = useHealth()

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      {isLoading && <p className="text-gray-600">Բեռնվում է...</p>}
      {isError && <p className="text-red-600 font-medium">Սխալ</p>}
      {!isLoading && !isError && status !== null && (
        <p className="text-green-600 font-medium">{status}</p>
      )}
    </main>
  )
}
```

`PersonsPage.tsx` extends with filter state from `useSearchParams` (D-04, D-05), card grid (Claude's Discretion), and `PaginationControls`:
```tsx
import { useSearchParams } from "react-router-dom"
import { usePoliticians } from "@/hooks/usePoliticians"
import { useParties } from "@/hooks/useParties"
import { PoliticianCard } from "@/components/PoliticianCard"
import { PaginationControls } from "@/components/PaginationControls"

export default function PersonsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const page = Number(searchParams.get("page") ?? "1")
  const party = searchParams.get("party")
  const level = searchParams.get("level")

  const { data, isLoading, isError } = usePoliticians({ page, party, level })
  const { data: partiesData } = useParties()

  return (
    <div>
      {/* Filter dropdowns (D-05) */}
      <div className="flex gap-4 mb-6">
        <select value={party ?? ""} onChange={e => {
          setSearchParams(p => {
            const n = new URLSearchParams(p)
            e.target.value ? n.set("party", e.target.value) : n.delete("party")
            n.set("page", "1")
            return n
          })
        }}>
          <option value="">Բոլոր կուսակցությունները</option>
          {partiesData?.map(p => (
            <option key={p.id} value={p.id}>{p.short_name_hy ?? p.name_hy}</option>
          ))}
        </select>
        <select value={level ?? ""} onChange={e => {
          setSearchParams(p => {
            const n = new URLSearchParams(p)
            e.target.value ? n.set("level", e.target.value) : n.delete("level")
            n.set("page", "1")
            return n
          })
        }}>
          <option value="">Բոլոր մակարդակները</option>
          <option value="national">Ազգային</option>
          <option value="local">Տեղական</option>
          <option value="party">Կուսակցական</option>
        </select>
      </div>

      {isLoading && <p className="text-gray-600">Բեռնվում է...</p>}
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

### `frontend/src/pages/PoliticianProfilePage.tsx` (page, request-response)

**Analog:** `frontend/src/pages/HomePage.tsx` (lines 1-24)

Add `useParams` to extract `:slug`, then `usePolitician(slug)` + `usePoliticianPromises(slug, page)`:

```tsx
import { useParams } from "react-router-dom"
import { usePolitician } from "@/hooks/usePolitician"
import { PromiseStub } from "@/components/PromiseStub"
import { Avatar } from "@/components/Avatar"
import { PaginationControls } from "@/components/PaginationControls"

export default function PoliticianProfilePage() {
  const { slug } = useParams<{ slug: string }>()
  const { data, isLoading, isError } = usePolitician(slug!)

  if (isLoading) return <p className="text-gray-600">Բեռնվում է...</p>
  if (isError || !data) return <p className="text-red-600">Չի գտնվել</p>

  return (
    <div>
      <div className="flex items-center gap-4 mb-8">
        <Avatar photoUrl={data.photo_url} nameHy={data.name_hy} size="lg" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{data.name_hy}</h1>
          {data.position && <p className="text-gray-600">{data.position}</p>}
        </div>
      </div>
      {/* Promise list — use separate usePoliticianPromises hook */}
    </div>
  )
}
```

---

### `frontend/src/pages/PartyPage.tsx` (page, request-response)

**Analog:** `frontend/src/pages/HomePage.tsx` (lines 1-24)

Same pattern: `useParams` → `useParty(slug)`. Displays party detail + member politicians + paginated promises.

---

### `frontend/src/pages/ElectionsListPage.tsx` (page, request-response)

**Analog:** `frontend/src/pages/HomePage.tsx` (lines 1-24)

Uses `useElections(page)` with `useSearchParams` for page state. Displays election rows with `promise_count` badge.

---

### `frontend/src/pages/ElectionDetailPage.tsx` (page, request-response)

**Analog:** `frontend/src/pages/HomePage.tsx` (lines 1-24)

Uses `useParams` → `useElection(slug)` + `useElectionPromises(slug, page)`. Displays election header + paginated promise stubs.

---

### `frontend/src/types/index.ts` (modify, transform)

**Analog:** `frontend/src/types/index.ts` (lines 1-3 — exact match)

Current content:
```typescript
export interface HealthResponse {
  status: string
}
```

Add new types below without removing `HealthResponse`:
```typescript
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
```

---

## Shared Patterns

### Async DB Session Dependency
**Source:** `backend/app/database.py` lines 25-32
**Apply to:** All router files (`politicians.py`, `parties.py`, `elections.py`)

```python
from app.database import get_db
# In every handler:
db: AsyncSession = Depends(get_db)
```

The `get_db` generator handles commit on success and rollback on exception. Read-only handlers in Phase 2 do not need explicit transaction control — the auto-commit on exit is harmless.

---

### HTTP Error Pattern
**Source:** FastAPI convention (no custom AppError class exists in this project)
**Apply to:** All router detail endpoints (`/{slug}` handlers)

```python
raise HTTPException(status_code=404, detail="<Entity> not found")
```

No custom error wrapper — use FastAPI's `HTTPException` directly. This matches the simplicity of `health.py`.

---

### `moderation_status=approved` Filter
**Source:** `backend/app/models/promises.py` lines 52-55 (ModerationStatus enum) + RESEARCH.md Pitfall 4
**Apply to:** Every router that queries promises for public display

```python
from app.models.promises import ModerationStatus

stmt = stmt.where(Promise.moderation_status == ModerationStatus.approved)
```

This filter MUST appear in every promise query. Forgetting it exposes pending/rejected promises.

---

### Test Client Pattern
**Source:** `backend/tests/conftest.py` lines 1-9 + `backend/tests/test_health.py` lines 1-14
**Apply to:** `test_politicians.py`, `test_parties.py`, `test_elections.py`

```python
# Use shared fixture from conftest.py:
async def test_list_xxx(client):
    response = await client.get("/api/xxx")
    assert response.status_code == 200
```

---

### TanStack Query v5 `placeholderData` (not `keepPreviousData: true`)
**Source:** `frontend/src/hooks/useHealth.ts` uses `useQuery` — note it does NOT use `keepPreviousData` because health is not paginated. For paginated hooks only:
**Apply to:** `usePoliticians.ts`, `useElections.ts`, any other paginated list hook

```typescript
import { keepPreviousData } from "@tanstack/react-query"
// In useQuery options:
placeholderData: keepPreviousData,
```

Do NOT write `keepPreviousData: true` (v4 syntax) — will cause TypeScript error.

---

### URL-based Pagination State
**Source:** React Router `useSearchParams` (no existing analog — established from RESEARCH.md Pattern 4)
**Apply to:** `PersonsPage.tsx`, `ElectionsListPage.tsx`, `PoliticianProfilePage.tsx` (promise sub-list), `PartyPage.tsx` (promise sub-list), `ElectionDetailPage.tsx`

```typescript
const [searchParams, setSearchParams] = useSearchParams()
const page = Number(searchParams.get("page") ?? "1")

// Navigate to page:
setSearchParams(prev => {
  const next = new URLSearchParams(prev)
  next.set("page", String(p))
  return next
})
```

Page state lives in the URL — not `useState`. This makes pages shareable (D-04).

---

### Loading/Error State Pattern
**Source:** `frontend/src/pages/HomePage.tsx` lines 11-22
**Apply to:** All 5 page components

```tsx
{isLoading && <p className="text-gray-600">Բեռնվում է...</p>}
{isError && <p className="text-red-600">Սխալ</p>}
```

Armenian text for loading/error messages (`Բեռնվում է...` = "Loading...", `Սխալ` = "Error") — established in `HomePage.tsx`.

---

## No Analog Found

Files with no close match in the codebase (planner should use RESEARCH.md patterns instead):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `frontend/src/components/PaginationControls.tsx` | component | request-response | No pagination UI exists in project yet; use RESEARCH.md Pattern 4 + shadcn/ui Pagination |
| `frontend/src/components/Avatar.tsx` | component | transform | No avatar/image component exists; use RESEARCH.md Pattern 5 (initials fallback) |
| `frontend/src/components/PoliticianCard.tsx` | component | request-response | No card component exists; use shadcn/ui `Card` + RESEARCH.md architecture diagram |
| `frontend/src/components/PromiseStub.tsx` | component | transform | No promise display component exists; use RESEARCH.md Pattern 6 (ResolvedStatus badge) |

---

## Metadata

**Analog search scope:** `backend/app/routers/`, `backend/app/schemas/`, `backend/app/models/`, `backend/app/database.py`, `backend/app/main.py`, `backend/alembic/versions/`, `backend/tests/`, `frontend/src/hooks/`, `frontend/src/pages/`, `frontend/src/api/`, `frontend/src/types/`
**Files scanned:** 22
**Pattern extraction date:** 2026-05-22
