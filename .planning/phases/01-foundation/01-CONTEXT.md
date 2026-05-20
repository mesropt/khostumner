# Phase 1: Foundation - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up the complete project scaffold: monorepo structure, full PostgreSQL schema (all 8 phases), FastAPI health endpoint, React/Vite app shell, Docker Compose local dev, GitHub Actions CI, and seed data with real Armenian politicians. Phase ends when all 5 success criteria in ROADMAP.md are green and a developer can clone the repo and be running in one command.

No user-facing features are built in this phase — just the foundation everything else depends on.

</domain>

<decisions>
## Implementation Decisions

### Repository Structure
- **D-01:** Monorepo with `backend/` and `frontend/` at root level. `docker-compose.yml`, `Makefile`, and CI config at root.
- **D-02:** Backend internal structure — **по модулям**: `backend/app/routers/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/main.py`, `backend/alembic/`, `backend/tests/`. One file per domain entity (politicians.py, promises.py, votes.py, etc.).
- **D-03:** Frontend internal structure — **по типам**: `frontend/src/components/`, `frontend/src/pages/`, `frontend/src/api/`, `frontend/src/hooks/`, `frontend/src/types/`, `frontend/public/`, `frontend/index.html`, `frontend/vite.config.ts`.

### Database Schema
- **D-04:** Build the **full schema** for all 8 phases in Phase 1. No incremental schema — all tables created upfront. This avoids costly migrations later.
- **D-05:** `politicians` and `parties` are **separate tables**. Clear boundary: politicians have photos and personal attributes; parties have logos and membership.
- **D-06:** Party affiliation is **time-bounded** via a `politician_party_memberships` junction table: `(politician_id, party_id, start_date, end_date NULL = current)`. The `politician.party_id` FK is kept for the current party (denormalized for query convenience) but the membership table is authoritative.
- **D-07:** Every promise has TWO status fields — `moderation_status` (enum: pending/approved/rejected — is content visible?) and `resolved_status` (enum: kept/broken/in_progress/stalled/not_rated — is the promise fulfilled?). These MUST remain separate fields, never merged.
- **D-08:** Vote storage uses individual rows: `votes(id, promise_id, user_id, status_voted, created_at)` with `UNIQUE(promise_id, user_id)`. Tally is never stored on the promise row.
- **D-09:** `vote_history(id, promise_id, user_id, status_voted, voted_at, previous_status, changed_at)` — full audit trail. When a user changes their vote, the old row is preserved and a new row is inserted. Full history retained indefinitely (VOTE-05).
- **D-10:** `stats_cache(politician_id, total_promises, kept_count, broken_count, in_progress_count, stalled_count, not_rated_count, fulfillment_pct, updated_at)` — precomputed fulfillment statistics. Updated after each vote/status change. Politician profile pages read from this table.
- **D-11:** Evidence table includes `archived_url` and `quote_excerpt` fields from the start. `archived_url` is populated via Wayback Machine API at submission time. `quote_excerpt` stores the verbatim text from the source in case the link dies.
- **D-12:** Status is set automatically by vote aggregation rule: leading status wins if it holds **>50%** of total votes AND total votes **≥ 25** (configurable in settings table). Otherwise resolved_status stays `not_rated`. No admin override of resolved_status.

### Local Development
- **D-13:** **Docker Compose** for local dev — single `docker-compose up` starts PostgreSQL + FastAPI (Uvicorn) + React/Vite dev server. Developers do not need to install Python or Node locally.
- **D-14:** FastAPI runs with `--reload` in dev container. Vite HMR works via Docker port mapping.

### CI Pipeline
- **D-15:** **GitHub Actions** on push and pull request to main.
  - Backend job: `ruff` lint + `pytest` (against a test PostgreSQL container).
  - Frontend job: `eslint` + `tsc --noEmit` type check.
  - Both jobs must pass; no deployment in Phase 1.

### Seed Data
- **D-16:** Real Armenian politicians and parties, marked with `[TEST DATA]` in the `notes` field. Seed data is clearly development-only — not loaded in production.
- **D-17:** Seed scale: **10 politicians**, **4 parties**, **4 elections**, **20 promises** (mixed statuses: kept/broken/in_progress/stalled/not_rated). Enough to make UI realistic.
- **D-18:** Seed data includes real election years (e.g., 2018 parliamentary, 2021 parliamentary, 2018 presidential). Promise quotes should be clearly fictional (e.g., "Կբարձրացնեմ նվազագույն աշխատավարձը — [TEST DATA]").

### Claude's Discretion
- Specific Python package versions within the FastAPI/SQLAlchemy 2.x/Alembic ecosystem — use latest stable at the time of planning.
- Exact Alembic migration naming convention — standard `YYYYMMDD_HHMMSS_description.py`.
- Docker image base versions — use official `python:3.12-slim` and `node:20-alpine`.
- Pre-commit hooks configuration — standard ruff + eslint hooks.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Foundation
- `.planning/PROJECT.md` — Project overview, constraints (Armenian-only, anonymous operation, FastAPI stack), key decisions table
- `.planning/REQUIREMENTS.md` — All 29 v1 requirements with REQ-IDs; traceability table (Phase 1 has no direct REQ-IDs — it is infrastructure)
- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, and dependency chain

### Architecture Decisions
- `.planning/research/SUMMARY.md` — Synthesized research: recommended stack (FastAPI + React + PostgreSQL), top 5 pitfalls, suggested phase structure, key architecture constraints
- `.planning/research/ARCHITECTURE.md` — Component boundaries, data model, build order, two-status-field constraint, stats_cache pattern, anti-patterns to avoid
- `.planning/research/STACK.md` — Full technology stack with versions and rationale (note: Next.js full-stack recommendation overridden; use FastAPI + React/Vite instead)
- `.planning/research/PITFALLS.md` — Domain pitfalls with prevention strategies: Armenian defamation law, vote brigading, source rot, data model inflexibility

No external ADRs or design documents exist yet — all constraints are captured in planning artifacts above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project. No existing code to reuse.

### Established Patterns
- None yet — this phase establishes all patterns.

### Integration Points
- Phase 1 establishes ALL integration points: FastAPI ↔ PostgreSQL (SQLAlchemy async), React ↔ FastAPI (REST via fetch/TanStack Query), CI ↔ GitHub repo.

</code_context>

<specifics>
## Specific Ideas

- Frontend folder structure preview confirmed by user: `components/`, `pages/`, `api/`, `hooks/`, `types/` under `src/`.
- Backend folder structure confirmed: `routers/`, `models/`, `schemas/`, `services/` under `app/`.
- Seed data should use real election years: 2018 presidential, 2018 parliamentary, 2021 parliamentary, 2024 local.
- Promise seed data must be clearly marked — use `[TEST DATA]` suffix in the promise text or a boolean `is_seed` field on the promises table.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Foundation*
*Context gathered: 2026-05-21*
