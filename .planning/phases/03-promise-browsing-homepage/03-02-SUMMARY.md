---
phase: 03-promise-browsing-homepage
plan: "02"
subsystem: api + ui
tags: [fastapi, sqlalchemy, react, tanstack-query, tailwind, homepage, stats]

dependency_graph:
  requires:
    - phase: 03-01
      provides: StatsOut + StatsByStatus pydantic schemas, StatsOut TypeScript interface, RED test stub for /api/stats
  provides:
    - GET /api/stats endpoint (backend/app/routers/stats.py) — GROUP BY resolved_status, approved-only filter
    - useStats TanStack Query hook (frontend/src/hooks/useStats.ts) — queryKey ["stats"], staleTime 5 min
    - New HomePage.tsx — stats block with total + 5 status counts, Armenian labels, semantic colors, recent-promises placeholder
  affects:
    - 03-04: must include_router(stats.router) in main.py to wire the endpoint
    - 03-03: promises hook once merged makes recent-promises section live

tech_stack:
  added: []
  patterns:
    - GROUP BY resolved_status with dict.get(key, 0) fallback ensures all 5 keys always present in stats response
    - useStats follows same destructuring pattern as useElections (single endpoint, no params, returns {data, isLoading, isError})
    - staleTime: 5 min on stats hook — homepage tolerate minor staleness, reduces server load

key_files:
  created:
    - backend/app/routers/stats.py
    - frontend/src/hooks/useStats.ts
  modified:
    - frontend/src/pages/HomePage.tsx

key_decisions:
  - "stats.py not wired to main.py in this plan — 03-04 handles all include_router calls to avoid main.py concurrent-edit conflicts"
  - "Recent promises section is a placeholder TODO in HomePage until 03-03 (usePromises) merges in Wave 2"
  - "Live GROUP BY query acceptable at seed-data volume; Phase 8 migrates to stats_cache aggregate (inline comment added)"

patterns-established:
  - "Stats endpoint pattern: GROUP BY enum column → dict.get(key, 0) for all enum values → plain StatsOut construction"
  - "Homepage stats block: bg-zinc-100 outer container, bg-zinc-50 stat cards, status-semantic text colors matching badge palette"

requirements-completed: [DISC-01]

duration: ~8min
completed: "2026-05-22"
---

# Phase 3 Plan 2: Stats Vertical Slice Summary

**GET /api/stats backend endpoint with GROUP BY query, useStats TanStack hook with 5-minute staleTime, and new HomePage replacing health-check placeholder with real stats block (5 resolved_status counts + total) and pending recent-promises section**

## Performance

- **Duration:** ~8 minutes
- **Started:** 2026-05-22T22:36:00Z
- **Completed:** 2026-05-22T22:44:15Z
- **Tasks:** 2
- **Files modified:** 3 (1 created backend, 1 created frontend hook, 1 replaced frontend page)

## Accomplishments

- `GET /api/stats` endpoint queries only `moderation_status=approved` promises, groups by `resolved_status`, defaults all 5 keys to 0 when absent — satisfies T-03-02 information disclosure mitigation
- `useStats()` hook wraps the stats endpoint with 5-minute staleTime and TanStack Query caching
- `HomePage` entirely replaces the health-check placeholder with a real stats block in zinc-100 container; 5 stat cards in zinc-50 with Armenian status labels in semantic colors (green-800/red-800/yellow-800/gray-600/zinc-500) matching Phase 2 badge palette
- Loading state uses animate-pulse skeleton for both stats block and 10-row promise list; error state uses exact Armenian copy from UI-SPEC Copywriting Contract

## Task Commits

1. **Task 1: Implement GET /api/stats endpoint** — `1be573a` (feat)
2. **Task 2: Create useStats hook + replace HomePage** — `0b52bbf` (feat)

## Files Created/Modified

- `backend/app/routers/stats.py` — APIRouter prefix="/stats"; get_stats() async function; GROUP BY resolved_status WHERE moderation_status=approved; all 5 ResolvedStatus keys defaulted to 0
- `frontend/src/hooks/useStats.ts` — useStats() hook; queryKey ["stats"]; staleTime 5 min; returns {data, isLoading, isError}
- `frontend/src/pages/HomePage.tsx` — replaces health-check placeholder; stats block with total count + 5 per-status cards; Armenian copy exact from UI-SPEC; recent promises TODO placeholder for 03-03

## Decisions Made

- `stats.py` not registered with `main.py` in this plan — 03-04 does all `include_router` calls to avoid concurrent file-edit conflicts across Wave 2 parallel plans.
- Recent promises section left as a descriptive placeholder with a `// TODO(03-03)` comment since `usePromises` is created in the parallel plan 03-03.
- Inline comment on the GROUP BY query: "Phase 3: live GROUP BY is acceptable at seed-data volume. Will be migrated to stats_cache aggregate in Phase 8." — satisfies the plan instruction.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

The recent promises section in `HomePage.tsx` (line ~72) renders a placeholder paragraph instead of a live promise list. This is intentional and documented: the `usePromises` hook is created in plan 03-03 (Wave 2), after which `HomePage.tsx` will be updated to use it. The stats block itself is fully wired — only the recent promises section is stubbed.

- **File:** `frontend/src/pages/HomePage.tsx`
- **Reason:** `usePromises` hook not yet available (created in 03-03)
- **Resolution plan:** 03-03 or a dedicated wiring step in 03-04 replaces the placeholder

## Threat Flags

No new security surface beyond what the plan's threat model covers:

- T-03-02 mitigated: `WHERE moderation_status == ModerationStatus.approved` present in stats query — pending/rejected counts never exposed.
- T-03-03 accepted: SQLAlchemy ORM parameterized query; no user input in stats query; no injection surface.

## Self-Check: PASSED

- [x] `backend/app/routers/stats.py` — exists, contains `get_stats`, `response_model=StatsOut`, `ModerationStatus.approved` WHERE clause, all 5 `ResolvedStatus` keys defaulted to 0
- [x] `python -c "from app.routers.stats import router; print('OK')"` — PASS (verified during execution)
- [x] `frontend/src/hooks/useStats.ts` — exists, exports `useStats`, queryKey `["stats"]`, staleTime 5 min, returns `{data, isLoading, isError}`
- [x] `frontend/src/pages/HomePage.tsx` — imports `useStats`, renders stats block with bg-zinc-100 container, 5 stat cards with Armenian labels, `Ընդամենը` total label
- [x] `npx tsc --noEmit` — PASS (exit code 0, no output)
- [x] Commit `1be573a` — feat(03-02): implement GET /api/stats endpoint
- [x] Commit `0b52bbf` — feat(03-02): create useStats hook + replace HomePage with stats block

---
*Phase: 03-promise-browsing-homepage*
*Completed: 2026-05-22*
