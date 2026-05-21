# Phase 2: Politicians, Parties & Elections Browsing - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver read-only public browsing pages for politicians, parties, and elections — served with real data from the FastAPI API. Any visitor (unauthenticated) can browse the Persons list, open politician profiles and party pages, and browse the elections list and detail pages. This phase also establishes the shared site layout (header + navigation) that all subsequent phases inherit.

No user authentication, no write operations, no promise submission. Promise detail pages are Phase 3. Admin CRUD for politicians/parties is Phase 6.

</domain>

<decisions>
## Implementation Decisions

### Site Navigation & Layout

- **D-01:** Phase 2 builds a shared `<Layout>` component that wraps all pages with a persistent site header. All Phase 2 and future browsing pages use this layout.
- **D-02:** Full planned nav link set is rendered in the header as stubs from day one: logo (Խոստումներ → `/`), Կատարված (`/fulfilled`), Չկատարված (`/unfulfilled`), Պերսոններ (`/persons`), Ընտրություններ (`/elections`). Links for phases not yet built still render — they route to NotFoundPage until those phases deliver the pages.
- **D-03:** Logo links to `/` (homepage). No mobile hamburger menu in Phase 2 — mobile nav deferred to Phase 3 when the homepage is built.

### Persons List (POLS-02)

- **D-04:** Filter strategy is **server-side query params** — `?party=<uuid>&level=<national|local|party>`. Filters are sent to the API as query parameters. TanStack Query's `queryKey` includes the active filters so queries re-run on filter change. URLs are shareable with active filters.
- **D-05:** Filter UI is two `<select>` dropdowns: **Party** (all parties from API) and **Level** (national / local / party). Both default to "All".

### Promise Preview on Entity Pages (POLS-01, POLS-03, ELEC-01, ELEC-02)

- **D-06:** Promise items shown on politician profiles, party pages, and election detail pages are **minimal stubs**: truncated `quote_hy` (first ~120 characters, ellipsis if longer) + `resolved_status` badge (color-coded: kept=green, broken=red, in_progress=yellow, stalled=gray, not_rated=neutral).
- **D-07:** Each promise stub links to `/promises/{slug}`. In Phase 2 these links hit NotFoundPage — Phase 3 adds the promise detail page. This wires the final URL structure from day one.
- **D-08:** Promise lists on party pages and election detail pages are **paginated** using the same offset+limit approach as the Persons list. Politician profile promise list is also paginated.

### Pagination

- **D-09:** All list APIs use **offset+limit pagination**: `?page=1&per_page=20`. Query params `page` and `per_page` with defaults `page=1`, `per_page=20`, max `per_page=100`.
- **D-10:** API response envelope includes pagination metadata: `{ items: [...], total: N, page: N, per_page: N, pages: N }`.
- **D-11:** Frontend uses the **shadcn/ui Pagination component** (page number links + prev/next) — consistent with the shadcn stack already chosen.

### Claude's Discretion

- **Persons list layout** — user deferred to Claude. Card grid (photo/avatar, name, role, party badge) using shadcn/ui `Card` is the natural choice for a profile-heavy list. Use a 3-column grid on desktop, 1-column on mobile.
- **Photo fallback** — when `photo_url` is null (most seed politicians), show an initials-based avatar or a neutral silhouette placeholder. Claude decides the exact implementation.
- **Status badge colors** — exact Tailwind/shadcn color tokens for each resolved_status value are Claude's discretion within the constraint that each status is visually distinct.
- **API router file naming** — follow `backend/app/routers/health.py` pattern; one file per domain (politicians.py, parties.py, elections.py).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Foundation
- `.planning/PROJECT.md` — Project overview, constraints (Armenian-only UI, anonymous operation, FastAPI + React + PostgreSQL stack), key decisions table
- `.planning/REQUIREMENTS.md` — Phase 2 requirements: POLS-01, POLS-02, POLS-03, ELEC-01, ELEC-02 (lines 35–46); also DISC-01–DISC-03 for nav link targets that need to exist as routes even if unimplemented
- `.planning/ROADMAP.md` — Phase 2 goal, success criteria (5 items), and dependency chain

### Phase 1 Decisions (carry forward)
- `.planning/phases/01-foundation/01-CONTEXT.md` — All D-01–D-18 decisions; specifically D-02 (backend structure), D-03 (frontend structure), D-04 (full schema built upfront), D-06 (party affiliation time-bounded), D-07 (two status fields), D-15 (CI jobs)

### Data Model
- `backend/app/models/politicians.py` — `Politician` model (fields: id, name_hy, slug, photo_url, position, level, party_id, bio_hy, is_active) + `PoliticianPartyMembership` (time-bounded affiliation)
- `backend/app/models/parties.py` — `Party` model (fields: id, name_hy, short_name_hy, logo_url, founded_year, is_active)
- `backend/app/models/elections.py` — `Election` model (fields: id, name_hy, slug, election_date, level, description_hy)
- `backend/app/models/promises.py` — `Promise` model (fields include quote_hy, slug, resolved_status, moderation_status, promised_date)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/App.tsx` — Route registry; Phase 2 adds `/persons`, `/persons/:slug`, `/parties/:slug`, `/elections`, `/elections/:slug` here
- `frontend/src/pages/NotFoundPage.tsx` — Catches `/promises/:slug` links that Phase 2 wires up but Phase 3 hasn't implemented yet
- `backend/app/routers/health.py` — Template router pattern: `APIRouter()` + `@router.get(path)` async def; replicate for politicians, parties, elections routers
- `backend/app/main.py` — `include_router()` call site; Phase 2 adds politician, party, election routers here (also needs CORS origins update for prod)

### Established Patterns
- **TanStack Query hook pattern**: `useHealth` hook in `frontend/src/hooks/useHealth.ts` — follow this pattern for `usePoliticians`, `usePolitician`, `useParty`, `useElections` etc. (`useQuery` with typed response, error/loading states)
- **FastAPI async router**: `async def` endpoint handlers, dependency-injected `db: AsyncSession = Depends(get_db)` — follow `health.py` shape
- **SQLAlchemy async select**: models are already defined; Phase 2 uses `select(Model).where(...).offset(...).limit(...)` via `async with db` sessions

### Integration Points
- `frontend/src/App.tsx` — add new Route entries for Phase 2 pages
- `backend/app/main.py` — add `include_router(politicians.router, prefix="/api")` etc.
- `backend/app/database.py` — `get_db` dependency already wired; use as-is

</code_context>

<specifics>
## Specific Ideas

- Nav links present from day one even for unbuilt phases — routes resolve to NotFoundPage until the phase delivers the page. This prevents needing to retrofit nav in every phase.
- Promise stubs on entity pages link to `/promises/{slug}` from Phase 2 — final URL structure locked early.
- Pagination response envelope should be consistent across all list endpoints (same shape: `items`, `total`, `page`, `per_page`, `pages`) so the frontend can use a single generic hook.

</specifics>

<deferred>
## Deferred Ideas

- Mobile hamburger/responsive nav menu — deferred to Phase 3 (when homepage is built and full nav context is clear)
- Promise detail page (`/promises/{slug}`) — Phase 3
- Fulfillment percentage on politician profiles — Phase 8 (reads from stats_cache)
- Admin create/edit politician and party profiles — Phase 6

</deferred>

---

*Phase: 2-Politicians-Parties-Elections-Browsing*
*Context gathered: 2026-05-21*
