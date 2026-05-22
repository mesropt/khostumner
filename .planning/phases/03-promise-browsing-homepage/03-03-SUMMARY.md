---
phase: 03-promise-browsing-homepage
plan: "03"
subsystem: backend-router + frontend-components + frontend-pages
tags: [promises-router, pagination, multi-filter, promise-card, list-pages, prom-01, disc-02, disc-03]
dependency_graph:
  requires:
    - 03-01 (PromiseListOut + PromiseDetailOut schemas, frontend type interfaces)
  provides:
    - GET /api/promises with 9 query params + PaginatedResponse[PromiseListOut]
    - GET /api/promises/{slug} returning PromiseDetailOut
    - PromiseCard component (frontend/src/components/PromiseCard.tsx)
    - usePromises hook (frontend/src/hooks/usePromises.ts)
    - PromisesListPage at /promises with full filter UI
    - FulfilledPage at /fulfilled (status=kept, no filters)
    - UnfulfilledPage at /unfulfilled (status=broken,stalled, no filters)
  affects:
    - 03-04 (wires promises router into main.py + adds routes to App.tsx)
tech_stack:
  added: []
  patterns:
    - Multi-value query param via comma-split (status=broken,stalled → ResolvedStatus list)
    - Conditional election_id JOIN (only added when param provided)
    - D-07b: date WHERE clauses only added when param is not None (null-date promises never filtered by default)
    - moderation_status=approved base condition on all public promise queries (T-03-07)
    - Plain BaseModel (no from_attributes) for JOIN Row tuple results
    - useSearchParams for all filter state — no React useState for filter values
key_files:
  created:
    - backend/app/routers/promises.py
    - frontend/src/components/PromiseCard.tsx
    - frontend/src/hooks/usePromises.ts
    - frontend/src/pages/PromisesListPage.tsx
    - frontend/src/pages/FulfilledPage.tsx
    - frontend/src/pages/UnfulfilledPage.tsx
  modified: []
decisions:
  - election_id filter joins PromiseElectionLink only when election_id is provided (avoids unnecessary JOIN in base query)
  - D-07b enforced: date filter WHERE clauses added only when params are not None — null-date promises appear in all unfiltered queries
  - PromiseCard meta line: politician name always shown; date appended conditionally with "·" separator
  - FulfilledPage and UnfulfilledPage have no filter UI (D-05) — clean focused pages per plan spec
metrics:
  duration: ~15 minutes
  completed_date: "2026-05-23"
  tasks: 3
  files_changed: 6
---

# Phase 3 Plan 3: Promises List Vertical Slice Summary

Promises list vertical slice: GET /api/promises router with 9 optional filter params (including comma-split multi-value status), PromiseCard component, usePromises hook, and three list pages (PromisesListPage with full filter UI, FulfilledPage filtered to kept, UnfulfilledPage filtered to broken+stalled).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement GET /api/promises router with multi-filter support | e28d93f | backend/app/routers/promises.py |
| 2 | PromiseCard component + usePromises hook | 53f899b | frontend/src/components/PromiseCard.tsx, frontend/src/hooks/usePromises.ts |
| 3 | PromisesListPage + FulfilledPage + UnfulfilledPage | e88046f | frontend/src/pages/PromisesListPage.tsx, frontend/src/pages/FulfilledPage.tsx, frontend/src/pages/UnfulfilledPage.tsx |

## What Was Built

### Backend

**`backend/app/routers/promises.py`** — Full promises router with two endpoints:

- `GET /api/promises` — paginated list with 9 query params:
  - page, per_page (pagination)
  - status (comma-separated multi-value; each value validated via `ResolvedStatus(s.strip())` → 422 on invalid — T-03-04)
  - politician_id, election_id (UUID params; FastAPI rejects invalid UUIDs with 422 — T-03-05)
  - made_date_from, made_date_to, expected_date_from, expected_date_to (ISO date params — T-03-06)
  - moderation_status=approved always applied as base WHERE condition (T-03-07)
  - D-07b: date WHERE clauses only added when param is not None
  - election_id triggers PromiseElectionLink JOIN only when provided
  - quote_hy truncated to 120 chars + "…" in router (PromiseListOut receives pre-truncated string)
  - count-via-subquery pattern for total count
  - Explicit row unpacking (promise, politician_name, politician_slug) from JOIN tuples

- `GET /api/promises/{slug}` — single promise detail; 404 if not found or not approved

### Frontend

**`frontend/src/components/PromiseCard.tsx`** — Promise list row:
- Entire row is a `<Link>` to `/promises/:slug`
- Shows title_hy (semibold), truncated quote (line-clamp-2), politician name + conditional made_date meta
- ResolvedStatusBadge on right side

**`frontend/src/hooks/usePromises.ts`** — TanStack Query hook:
- 9-param interface (page required, all others optional with null defaults)
- URLSearchParams built conditionally — null/undefined params not added
- placeholderData: keepPreviousData to avoid flicker on filter/page change
- Returns `{ data, isLoading, isError }`

**`frontend/src/pages/PromisesListPage.tsx`** — Full filtered page at `/promises`:
- All 8 filter params read from URL via useSearchParams (no React useState for filter values)
- 3 selects (status, politician, election) + 4 date inputs
- Status options hard-coded with Armenian labels from UI-SPEC
- Politician options from `usePoliticians({ page: 1, perPage: 100 })`
- Election options from `useElections(1)`
- Loading skeleton (20 rows), error state (AlertCircle + Armenian copy), empty state, data list with PaginationControls

**`frontend/src/pages/FulfilledPage.tsx`** — Clean page at `/fulfilled`:
- No filter UI (D-05)
- status hard-coded to "kept"
- H1: "Կատարված խոստումներ"
- Loading/error/empty/data states

**`frontend/src/pages/UnfulfilledPage.tsx`** — Clean page at `/unfulfilled`:
- No filter UI (D-05)
- status hard-coded to "broken,stalled"
- H1: "Չկատարված խոստումներ"
- Loading/error/empty/data states

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

- `python -c "from app.routers.promises import router; print('OK')"` — PASS
- `list_promises` has 9 query params (page, per_page, status, politician_id, election_id, made_date_from, made_date_to, expected_date_from, expected_date_to, db) — PASS
- `npx tsc --noEmit` — PASS (exit code 0, no errors)
- moderation_status=approved always applied as base condition — PASS (verified by code review)
- comma-split status → ResolvedStatus validation — PASS (code review)
- FulfilledPage: no filter UI; status hard-coded to "kept" — PASS
- UnfulfilledPage: no filter UI; status hard-coded to "broken,stalled" — PASS
- All 6 files created and verified

## Threat Mitigations Applied

| Threat ID | Mitigation |
|-----------|------------|
| T-03-04 | status param: `ResolvedStatus(s.strip())` raises ValueError for invalid values → FastAPI returns 422; no raw string in SQL |
| T-03-05 | politician_id/election_id declared as `uuid.UUID | None` → Pydantic rejects invalid UUIDs with 422 before router executes |
| T-03-06 | date params declared as `date | None` → Pydantic validates ISO date format; rejects invalid strings with 422 |
| T-03-07 | `Promise.moderation_status == ModerationStatus.approved` always applied as first WHERE condition before any optional filters |

## Known Stubs

None. All components wire to real API endpoints via usePromises hook. No placeholder data.

## Threat Flags

No new security surface beyond what is in the threat model. The promises router is a read-only public endpoint with moderation guard always applied.

## Self-Check: PASSED

- [x] backend/app/routers/promises.py — exists, contains list_promises with 9 params
- [x] frontend/src/components/PromiseCard.tsx — exists, contains PromiseCard
- [x] frontend/src/hooks/usePromises.ts — exists, contains usePromises
- [x] frontend/src/pages/PromisesListPage.tsx — exists, contains PromisesListPage
- [x] frontend/src/pages/FulfilledPage.tsx — exists, contains FulfilledPage
- [x] frontend/src/pages/UnfulfilledPage.tsx — exists, contains UnfulfilledPage
- [x] Commit e28d93f — feat(03-03): implement GET /api/promises router with multi-filter support
- [x] Commit 53f899b — feat(03-03): PromiseCard component + usePromises hook
- [x] Commit e88046f — feat(03-03): PromisesListPage + FulfilledPage + UnfulfilledPage
- [x] TypeScript compiles with exit code 0
- [x] Backend router importable with exit code 0
