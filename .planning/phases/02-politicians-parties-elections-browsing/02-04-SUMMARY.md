---
phase: 02-politicians-parties-elections-browsing
plan: 04
subsystem: api, ui
tags: [fastapi, pydantic, sqlalchemy, tanstack-query, react, pagination, elections, correlated-subquery]

requires:
  - phase: 02-01
    provides: PaginatedResponse schema, PromiseStubOut schema, shadcn/ui components, Layout+routing
  - phase: 02-02
    provides: PaginationControls, PromiseStub, PoliticianCard components
  - phase: 02-03
    provides: party router patterns, approved-only filter pattern

provides:
  - ElectionOut Pydantic schema (backend/app/schemas/elections.py)
  - ElectionWithCountOut Pydantic schema (backend/app/schemas/elections.py)
  - GET /api/elections — paginated list with promise_count via correlated subquery (ELEC-01)
  - GET /api/elections/{slug} — election detail (ELEC-01)
  - GET /api/elections/{slug}/promises — paginated approved-only linked promises (ELEC-02)
  - useElections hook with placeholderData: keepPreviousData (frontend/src/hooks/useElections.ts)
  - useElection hook with enabled guard (frontend/src/hooks/useElection.ts)
  - useElectionPromises hook with placeholderData: keepPreviousData (frontend/src/hooks/useElectionPromises.ts)
  - ElectionsListPage: cards with level badge + promise count + pagination
  - ElectionDetailPage: header + linked promises + 404 state with back link

affects:
  - Phase 3: promise browsing reuses elections context (linking promises to elections)
  - ELEC-01 and ELEC-02 requirements fully satisfied

tech-stack:
  added: []
  patterns:
    - "Correlated subquery for promise_count: select(func.count()).where(PromiseElectionLink.election_id == Election.id).correlate(Election).scalar_subquery()"
    - "Row tuple unpacking: election, count = row — required when select returns (ORM, scalar) pairs"
    - "ElectionWithCountOut as plain BaseModel (no from_attributes) — constructed explicitly from Row tuples"
    - "ModerationStatus.approved filter on all election promise queries — T-02-13"
    - "useElectionPromises uses keepPreviousData and enabled: Boolean(slug)"
    - "Armenian pluralization: N===1 ? 'N խոստում' : 'N խոստումներ'"

key-files:
  created:
    - "backend/app/schemas/elections.py — ElectionOut and ElectionWithCountOut schemas"
    - "backend/app/routers/elections.py — 3 async endpoints: list, detail, promises"
    - "frontend/src/hooks/useElections.ts — paginated elections list hook"
    - "frontend/src/hooks/useElection.ts — single election detail hook"
    - "frontend/src/hooks/useElectionPromises.ts — paginated election promises hook"
  modified:
    - "backend/app/main.py — added elections router import and include_router"
    - "backend/tests/test_elections.py — updated from stubs to real assertions"
    - "frontend/src/pages/ElectionsListPage.tsx — replaced stub with full implementation"
    - "frontend/src/pages/ElectionDetailPage.tsx — replaced stub with full implementation"

key-decisions:
  - "ElectionWithCountOut is NOT a subclass of ElectionOut — correlated subquery returns Row tuples, not ORM objects; model_config from_attributes would not help; explicit construction required"
  - "Promise count subquery counts ALL linked promises (not just approved) — count reflects election scope; approved filter only applies to the /promises endpoint"
  - "Election detail endpoint returns ElectionOut (no promise_count) — consistent with politicians/parties pattern where detail does not need the aggregate"

duration: ~12min
completed: 2026-05-22
---

# Phase 2, Plan 04: Elections Browsing Vertical Slice Summary

**ElectionOut/ElectionWithCountOut Pydantic schemas, 3 API endpoints with correlated subquery for promise counts, 3 TanStack Query hooks, and full ElectionsListPage + ElectionDetailPage — ELEC-01 and ELEC-02 end-to-end**

## Performance

- **Duration:** ~12 minutes
- **Completed:** 2026-05-22
- **Tasks:** 2 (+ 1 checkpoint pending human verification)
- **Files modified/created:** 9

## Accomplishments

- ELEC-01: GET /api/elections returns paginated ElectionWithCountOut with promise_count per election via correlated subquery; ElectionsListPage displays election cards with level badge and promise count
- ELEC-02: GET /api/elections/{slug}/promises returns paginated approved-only promises; ElectionDetailPage shows linked promises with PromiseStub components
- Backend: 3 async endpoints; ElectionOut schema for detail; ElectionWithCountOut for list (plain BaseModel, explicit construction from Row tuples); ModerationStatus.approved filter enforced (T-02-13); ORM parameterized queries (T-02-12)
- Frontend: 3 TanStack Query hooks with correct queryKeys; ElectionsListPage with skeleton/empty/error states; ElectionDetailPage with 404 state and back link; tsc --noEmit: exit 0

## Task Commits

1. **Task 1: Backend schemas + router + main.py + tests** — `a136066` (feat)
2. **Task 2: Hooks + ElectionsListPage + ElectionDetailPage** — `0f441f4` (feat)

## Files Created/Modified

**Backend (4 files):**
- `backend/app/schemas/elections.py` — ElectionOut (from_attributes) and ElectionWithCountOut (plain BaseModel)
- `backend/app/routers/elections.py` — 3 async route handlers with ModerationStatus.approved filter
- `backend/app/main.py` — added elections import and include_router(elections.router, prefix="/api")
- `backend/tests/test_elections.py` — 3 tests: list pagination keys + promise_count; 404 for detail; 404 for promises

**Frontend (5 files):**
- `frontend/src/hooks/useElections.ts` — useQuery with placeholderData: keepPreviousData
- `frontend/src/hooks/useElection.ts` — useQuery with enabled: Boolean(slug)
- `frontend/src/hooks/useElectionPromises.ts` — paginated useQuery with keepPreviousData + enabled guard
- `frontend/src/pages/ElectionsListPage.tsx` — full page (heading, card list, badges, pagination)
- `frontend/src/pages/ElectionDetailPage.tsx` — full page (header, promises section, 404 state)

## Decisions Made

1. **ElectionWithCountOut as plain BaseModel**: The list query uses `select(Election, promise_count_subquery)` which returns `Row(Election, int)` tuples. Using `from_attributes=True` on a subclass of ElectionOut would not work because the Row object is not the ORM model — only `election_obj` inside it is. Explicit construction (`ElectionWithCountOut(id=row[0].id, ..., promise_count=row[1])`) is the correct and only approach.
2. **Promise count counts all linked promises**: The `promise_count` on election cards reflects the total linked promises (not approved-only). This shows the full promise scope for an election. The approved filter only applies to the `/promises` endpoint which returns actual content.
3. **No Armenian date formatting issues**: Using `toLocaleDateString("hy-AM")` is appropriate for the frontend. The ISO date string from the API (`YYYY-MM-DD`) parses correctly with `new Date(dateStr)`.

## Deviations from Plan

None — plan executed exactly as written. All must_haves satisfied:
- GET /api/elections returns PaginatedResponse with ElectionWithCountOut items
- GET /api/elections/{slug} returns election detail; nonexistent slug returns 404
- GET /api/elections/{slug}/promises returns paginated approved promises; nonexistent slug returns 404
- ElectionsListPage shows promise count per election card
- ElectionDetailPage shows 404 state with back link to /elections
- All 3 hooks have correct queryKeys including all params
- tsc --noEmit exits 0

## Checkpoint Status

Task 3 (human-verify checkpoint) is pending. The full Phase 2 browsing stack is implemented:
- POLS-01: GET /api/politicians/{slug} + PoliticianProfilePage
- POLS-02: GET /api/politicians?party=...&level=... + PersonsPage
- POLS-03: GET /api/parties/{slug} + PartyPage
- ELEC-01: GET /api/elections + ElectionsListPage
- ELEC-02: GET /api/elections/{slug}/promises + ElectionDetailPage

Human verification requires: Docker Compose stack running, seed data loaded, browser walkthrough of all 5 browsing flows.

## Known Stubs

- Promise links in PromiseStub.tsx (`/promises/{slug}`) resolve to NotFoundPage — Phase 3 adds promise detail page (inherited from plan 02-02).
- `/elections` nav link in Layout.tsx navigates to ElectionsListPage (no stub — implemented in plan 02-01 routing).

## Threat Flags

None — all endpoints are read-only GET within the plan's threat model. Threat mitigations applied:
- T-02-12: SQLAlchemy ORM parameterized: `Election.slug == slug` (no string interpolation)
- T-02-13: `ModerationStatus.approved` filter applied in `get_election_promises`
- T-02-14: per_page capped at 100 via `Query(..., le=100)` on all endpoints
- T-02-15: promise_count is an aggregate integer; no individual promise content exposed in list

## Self-Check: PASSED

- `backend/app/schemas/elections.py` — ElectionOut and ElectionWithCountOut both present
- `backend/app/routers/elections.py` — 3 route handlers: list_elections, get_election, get_election_promises
- `backend/app/routers/elections.py` — `ModerationStatus.approved` present at line 106
- `backend/app/main.py` — `elections.router` import and include_router present
- `frontend/src/hooks/useElections.ts` — queryKey: ["elections", { page }], placeholderData: keepPreviousData
- `frontend/src/hooks/useElection.ts` — queryKey: ["election", slug], enabled: Boolean(slug)
- `frontend/src/hooks/useElectionPromises.ts` — queryKey: ["election-promises", slug, { page, perPage }], keepPreviousData, enabled
- `frontend/src/pages/ElectionsListPage.tsx` — useElections hook, level badge, promise count
- `frontend/src/pages/ElectionDetailPage.tsx` — useElection + useElectionPromises, 404 back link to /elections
- Commits: a136066, 0f441f4 — both present in git log
- tsc --noEmit: exit 0

---
*Phase: 02-politicians-parties-elections-browsing*
*Completed: 2026-05-22*
