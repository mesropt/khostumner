# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-20)

**Core value:** Anyone can verify whether an Armenian politician kept their election promises — with evidence and sources.
**Current focus:** Phase 2 — Politicians, Parties & Elections Browsing

## Current Position

Phase: 2 of 8 (Politicians, Parties & Elections Browsing) — **READY TO EXECUTE**
Next phase: 2 of 8 (Politicians, Parties & Elections Browsing)
Status: Phase 2 planned — 4 plans in 4 waves (POLS-01,02,03 + ELEC-01,02 covered)
Last activity: 2026-05-22 — Phase 2 planning complete; 4 PLAN.md files verified

Progress: [██░░░░░░░░] 12%

## Performance Metrics

**Velocity:**
- Total plans completed: 2
- Average duration: ~21 minutes
- Total execution time: 0.9 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation | 2/2 | ~41m | ~21m |

**Recent Trend:**
- Last 5 plans: 01-01 (~35m), 01-02 (~6m)
- Trend: On track

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Roadmap: Two separate status fields — `moderation_status` (content visibility) and `resolved_status` (promise fulfillment) — established as core schema constraint
- Roadmap: Individual vote rows with UNIQUE(promise_id, user_id); stats_cache table for fulfillment percentages
- Roadmap: No admin override of resolved_status — community vote threshold only (>50%, ≥25 votes); admins can only reset votes on documented brigading
- Roadmap: Stack is FastAPI (Python) + React/Vite + PostgreSQL; no Next.js server actions
- 01-01: ModerationStatus defined once in promises.py; imported by evidence.py (no SAEnum redefinition)
- 01-01: Alembic env.py swaps postgresql+asyncpg:// → postgresql:// for sync migration runner
- 01-01: Initial migration written manually (no live DB at plan time); CI validates against real postgres
- 01-02: Tailwind v4 CSS-first: @import "tailwindcss" only; no postcss.config.js or tailwind.config.js
- 01-02: Vite HMR port 24678 explicitly set in vite.config.ts for Docker port mapping
- 01-02: Seed idempotency via Party.limit(1) check; ENVIRONMENT=production guard prevents production runs
- 01-02: App.test.tsx wraps App in MemoryRouter to avoid router nesting in test context
- 01-02: ENVIRONMENT=ci_no_seed skips test_seed_data_counts in CI (seed not run during CI pytest)

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-05-21
Stopped at: Phase 2 context gathered — 4 areas discussed (nav, persons list, promise preview, pagination)
Resume at: `/gsd:plan-phase 2` — Phase 2: Politicians, Parties & Elections Browsing