---
phase: 03-promise-browsing-homepage
plan: "01"
subsystem: backend-schemas + frontend-types + test-stubs
tags: [schemas, pydantic, frontend-types, tdd-red, wave-0]
dependency_graph:
  requires: []
  provides:
    - PromiseListOut schema (backend/app/schemas/promises.py)
    - PromiseDetailOut schema (backend/app/schemas/promises.py)
    - StatsOut + StatsByStatus schemas (backend/app/schemas/stats.py)
    - RED test stubs for PROM-01, PROM-02, DISC-01, DISC-05
    - Frontend PromiseListOut, PromiseDetailOut, StatsByStatus, StatsOut interfaces
    - shadcn input + separator UI components
  affects:
    - backend/app/routers/promises.py (downstream — wired in 03-02)
    - backend/app/routers/stats.py (downstream — wired in 03-03)
    - backend/app/routers/og.py (downstream — wired in 03-05)
    - frontend/src/pages/PromisesListPage.tsx (downstream — 03-02)
    - frontend/src/pages/HomePage.tsx (downstream — 03-03)
tech_stack:
  added: []
  patterns:
    - Plain BaseModel (no from_attributes) for JOIN Row tuple schemas — established in 02-04, extended here
    - Wave 0 RED test stubs for all downstream promise endpoints
key_files:
  created:
    - backend/app/schemas/stats.py
    - backend/tests/test_promises.py
    - backend/tests/test_stats.py
    - backend/tests/test_og.py
    - frontend/src/components/ui/input.tsx
    - frontend/src/components/ui/separator.tsx
  modified:
    - backend/app/schemas/promises.py
    - frontend/src/types/index.ts
decisions:
  - PromiseListOut and PromiseDetailOut are plain BaseModel (no from_attributes) — same pattern as ElectionWithCountOut (02-04) because the promises router JOINs Promise + Politician and returns Row tuples
  - StatsOut and StatsByStatus are plain BaseModel — constructed from aggregate query results, not ORM objects
  - date fields use Python `date` type on the backend (from datetime import date); string | null on the frontend (JSON date serialization)
metrics:
  duration: ~2 minutes
  completed_date: "2026-05-22"
  tasks: 3
  files_changed: 8
---

# Phase 3 Plan 1: Wave 0 Schema Scaffold Summary

Wave 0 scaffolding: Pydantic schemas for promises + stats domains, RED test stubs for all Phase 3 promise endpoints, shadcn input/separator components, and frontend TypeScript type interfaces — establishing the full type contract for downstream plans 03-02 through 03-05.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add PromiseListOut + PromiseDetailOut + StatsOut schemas | 7636028 | backend/app/schemas/promises.py, backend/app/schemas/stats.py |
| 2 | Write RED test stubs for promises, stats, og | 7a5dfd4 | backend/tests/test_promises.py, backend/tests/test_stats.py, backend/tests/test_og.py |
| 3 | Install shadcn input/separator + extend frontend types | dacae70 | frontend/src/types/index.ts, frontend/src/components/ui/input.tsx, frontend/src/components/ui/separator.tsx |

## What Was Built

### Backend Schemas

**`backend/app/schemas/promises.py`** — Extended with two new schemas:
- `PromiseListOut` — plain BaseModel with 7 fields: id, slug, title_hy, quote_hy (truncated), resolved_status, politician_name_hy, made_date
- `PromiseDetailOut` — plain BaseModel with 11 fields: all PromiseListOut fields plus expected_date, source_url, archived_url, politician_slug
- Existing `PromiseStubOut` preserved unchanged (used by politician/party/election routers)

**`backend/app/schemas/stats.py`** — New file with:
- `StatsByStatus` — plain BaseModel: kept, broken, in_progress, stalled, not_rated (all int)
- `StatsOut` — plain BaseModel: total (int) + by_status (StatsByStatus)

### RED Test Stubs

All 9 test functions created across 3 files. All fail with 404 (routers not yet wired):
- `test_promises.py`: 6 tests covering PROM-01 (list, filter, multi-status, moderation guard) and PROM-02 (detail, not-found)
- `test_stats.py`: 1 test covering DISC-01 (stats response shape)
- `test_og.py`: 2 tests covering DISC-05 (og not-found, og html content)

### Frontend

**`frontend/src/types/index.ts`** — Appended 4 new exported interfaces: PromiseListOut, PromiseDetailOut, StatsByStatus, StatsOut. All existing interfaces preserved.

**shadcn components installed:**
- `frontend/src/components/ui/input.tsx` — official shadcn registry
- `frontend/src/components/ui/separator.tsx` — official shadcn registry

## Deviations from Plan

None — plan executed exactly as written.

## Verification Results

- `python -c "from app.schemas.promises import PromiseListOut, PromiseDetailOut"` — PASS
- `python -c "from app.schemas.stats import StatsOut, StatsByStatus"` — PASS
- `npx tsc --noEmit` — PASS (exit code 0, no errors)
- `pytest test_promises.py test_stats.py test_og.py` — 7 failed (404 RED), 1 passed (not_found test correctly gets 404), 1 skipped (og html skips when list returns 404)
- `frontend/src/components/ui/input.tsx` — EXISTS
- `frontend/src/components/ui/separator.tsx` — EXISTS

## Known Stubs

None. All schemas are fully defined with real field types. No placeholder values.

## Threat Flags

No new security surface introduced. This plan creates schema definitions and test stubs only. No network endpoints, auth paths, or file access patterns were added.

## Self-Check: PASSED

- [x] backend/app/schemas/promises.py — exists, contains PromiseListOut
- [x] backend/app/schemas/stats.py — exists, contains StatsOut
- [x] backend/tests/test_promises.py — exists, contains test_list_promises
- [x] backend/tests/test_stats.py — exists, contains test_get_stats
- [x] backend/tests/test_og.py — exists, contains test_og_promise
- [x] frontend/src/types/index.ts — contains PromiseListOut interface
- [x] frontend/src/components/ui/input.tsx — exists
- [x] frontend/src/components/ui/separator.tsx — exists
- [x] Commit 7636028 — feat(03-01): add PromiseListOut, PromiseDetailOut, StatsOut, StatsByStatus schemas
- [x] Commit 7a5dfd4 — test(03-01): add RED test stubs for PROM-01, PROM-02, DISC-01, DISC-05
- [x] Commit dacae70 — feat(03-01): install shadcn input/separator + add frontend type interfaces
