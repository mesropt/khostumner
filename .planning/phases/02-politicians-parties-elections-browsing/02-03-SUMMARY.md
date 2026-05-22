---
phase: 02-politicians-parties-elections-browsing
plan: 03
subsystem: api, ui
tags: [fastapi, pydantic, sqlalchemy, tanstack-query, react, pagination, party-page]

requires:
  - phase: 02-01
    provides: PaginatedResponse schema, PromiseStubOut schema, shadcn/ui components, Layout+routing
  - phase: 02-02
    provides: PartyListItemOut schema, parties router stub (GET / and GET /{slug}), Avatar, PromiseStub, PoliticianCard, PaginationControls components

provides:
  - PartyOut Pydantic schema (backend/app/schemas/parties.py)
  - GET /api/parties/{slug} — full party detail with PartyOut (T-02-09)
  - GET /api/parties/{slug}/politicians — active party member list (T-02-11)
  - GET /api/parties/{slug}/promises — paginated approved-only promises via JOIN (T-02-10)
  - useParty hook (frontend/src/hooks/useParty.ts)
  - usePartyPoliticians hook (frontend/src/hooks/usePartyPoliticians.ts)
  - usePartyPromises hook with placeholderData: keepPreviousData (frontend/src/hooks/usePartyPromises.ts)
  - PartyPage component with header, members section, paginated promises section

affects:
  - 02-04 (elections router): reuses PaginationControls, PromiseStub, PaginatedResponse patterns
  - all future phases: PartyPage delivers POLS-03 end-to-end

tech-stack:
  added: []
  patterns:
    - "JOIN approach for party promises: Promise JOIN Politician WHERE party_id == party.id"
    - "ModerationStatus.approved filter on all promise queries — T-02-10"
    - "Non-paginated party members endpoint — T-02-11 accept (< 100 members in v1)"
    - "useSearchParams for page state on PartyPage (not useState)"
    - "placeholderData: keepPreviousData (not keepPreviousData: true) — TanStack Query v5"

key-files:
  created:
    - "frontend/src/hooks/useParty.ts"
    - "frontend/src/hooks/usePartyPoliticians.ts"
    - "frontend/src/hooks/usePartyPromises.ts"
  modified:
    - "backend/app/schemas/parties.py — added PartyOut schema"
    - "backend/app/routers/parties.py — expanded from 2 to 4 endpoints"
    - "backend/tests/test_parties.py — updated from 2 stubs to 5 real assertions"
    - "frontend/src/pages/PartyPage.tsx — replaced stub with full implementation"

key-decisions:
  - "ModerationStatus.approved filter applied via JOIN not subquery — simpler and equivalent for approved-only requirement"
  - "Members section uses card grid for <=6 members, vertical list for >6 — matches UI-SPEC lines 206–209"
  - "Party promises use default pageParamKey='page' on PaginationControls — no collision since PartyPage has only one paginated section"

duration: ~4min
completed: 2026-05-22
---

# Phase 2, Plan 03: Party Page Vertical Slice Summary

**PartyOut Pydantic schema, 3 new API endpoints (party detail, members, promises with approved filter), 3 TanStack Query hooks, and full PartyPage implementation — POLS-03 end-to-end**

## Performance

- **Duration:** ~4 minutes
- **Completed:** 2026-05-22
- **Tasks:** 2
- **Files modified/created:** 7

## Accomplishments

- POLS-03 end-to-end: visitor can navigate to /parties/:slug and see party name, founding year, member politicians, and approved promises
- Backend: expanded parties router from 2 to 4 endpoints; PartyOut schema with full 7 fields; ModerationStatus.approved filter enforced on promises (T-02-10); SQLAlchemy ORM parameterized queries (T-02-09)
- Frontend: 3 TanStack Query hooks with proper queryKeys; PartyPage with hero (name, logo/initials avatar, founded year), members section (card grid or list based on count), paginated promises section
- TypeScript compiles clean (exit 0); vitest 3/3 tests pass

## Task Commits

1. **Task 1: Backend schemas + routers + tests** — `b93a2c4` (feat)
2. **Task 2: Hooks + PartyPage** — `481d256` (feat)

## Files Created/Modified

**Backend (3 files):**
- `backend/app/schemas/parties.py` — added PartyOut with 7 fields (id, name_hy, short_name_hy, logo_url, founded_year, is_active, slug)
- `backend/app/routers/parties.py` — expanded: GET /, GET /{slug}, GET /{slug}/politicians, GET /{slug}/promises
- `backend/tests/test_parties.py` — 5 tests covering list, 404 paths for all 3 slug endpoints

**Frontend (4 files):**
- `frontend/src/hooks/useParty.ts` — useQuery<PartyOut> with enabled guard
- `frontend/src/hooks/usePartyPoliticians.ts` — useQuery<PoliticianOut[]> with enabled guard
- `frontend/src/hooks/usePartyPromises.ts` — paginated useQuery with placeholderData: keepPreviousData
- `frontend/src/pages/PartyPage.tsx` — full page replacing stub

## Decisions Made

1. **JOIN approach for party promises**: Used `Promise JOIN Politician WHERE party_id == party.id` rather than subquery. Simpler, same correctness, standard SQLAlchemy pattern.
2. **Members section rendering**: Card grid for <=6 members (horizontal row per UI-SPEC), vertical link list for >6. Matches UI-SPEC lines 206–209 exactly.
3. **Default pageParamKey**: PartyPage promises use default `pageParamKey="page"` — no URL param collision since PartyPage has only one paginated list (unlike PoliticianProfilePage which has both persons page and promises page).

## Deviations from Plan

None — plan executed exactly as written. All must_haves satisfied:
- GET /api/parties/{slug} returns PartyOut with full fields; nonexistent slug returns 404
- GET /api/parties/{slug}/politicians returns list of active member politicians
- GET /api/parties/{slug}/promises returns PaginatedResponse[PromiseStubOut] with moderation_status=approved filter
- PartyPage renders header (name, avatar, founded year), members section, paginated promises
- usePartyPromises uses placeholderData: keepPreviousData (not keepPreviousData: true)
- useSearchParams for page state

## Known Stubs

- Promise links in PromiseStub.tsx (`/promises/{slug}`) resolve to NotFoundPage — Phase 3 adds the promise detail page (inherited from plan 02-02, not introduced here).

## Threat Flags

None — all endpoints are read-only GET within the plan's threat model. Threat mitigations applied:
- T-02-09: SQLAlchemy ORM parameterized: `Party.slug == slug` (no string interpolation)
- T-02-10: `ModerationStatus.approved` filter applied in every promise query in parties router
- T-02-11: Party members not paginated — party size < 100 in v1 seed data (accepted)

## Self-Check: PASSED

- `backend/app/schemas/parties.py` — exports PartyListItemOut and PartyOut; PartyOut has slug field
- `backend/app/routers/parties.py` — 4 route handlers: list, detail, members, promises
- `backend/app/routers/parties.py` — `ModerationStatus.approved` present (grep confirmed)
- `backend/app/routers/parties.py` — `Party.slug` present (grep confirmed)
- `frontend/src/hooks/useParty.ts` — exists with queryKey: ["party", slug]
- `frontend/src/hooks/usePartyPoliticians.ts` — exists with queryKey: ["party-politicians", slug]
- `frontend/src/hooks/usePartyPromises.ts` — exists with placeholderData: keepPreviousData
- `frontend/src/pages/PartyPage.tsx` — full implementation (header, members, promises)
- Commits: b93a2c4, 481d256 — both present in git log
- tsc --noEmit: exit 0
- vitest run: 3/3 tests passed

---
*Phase: 02-politicians-parties-elections-browsing*
*Completed: 2026-05-22*
