---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Phase 5 context gathered
last_updated: "2026-05-24T10:21:33.700Z"
last_activity: 2026-05-24 -- Phase 05 execution started
progress:
  total_phases: 8
  completed_phases: 4
  total_plans: 22
  completed_plans: 17
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-20)

**Core value:** Anyone can verify whether an Armenian politician kept their election promises — with evidence and sources.
**Current focus:** Phase 05 — promise-submission

## Current Position

Phase: 05 (promise-submission) — EXECUTING
Plan: 1 of 5
Next action: Human test email/OAuth flows, then execute Phase 5
Status: Executing Phase 05
Last activity: 2026-05-24 -- Phase 05 execution started

Progress: [███████░░░░░░░] 37%

## Performance Metrics

**Velocity:**

- Total plans completed: 11
- Average duration: ~21 minutes
- Total execution time: ~3.5 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation | 2/2 | ~41m | ~21m |
| 2. Politicians, Parties & Elections | 4/4 | ~1.5h | ~22m |
| 3. Promise Browsing & Homepage | 5/5 | ~1.5h | ~18m |

**Recent Trend:**

- Last 5 plans: 03-01 (~4m), 03-02 (~8m), 03-03 (~15m), 03-04 (~21m), 03-05 (~9m)
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
- [Phase ?]: 02-01: Party slug uses explicit ASCII transliterations in migration (no regexp_replace)
- [Phase ?]: 02-01: frontend/.npmrc sets legacy-peer-deps=true for shadcn CLI compatibility with pre-existing vite version conflict
- [Phase ?]: 02-01: PaginatedResponse[T] generic schema is the single source of truth for all paginated API responses
- 02-02: @vitejs/plugin-react pinned to ^4.0.0 — v6 requires vite ^8 which conflicts with project vite ^6
- 02-02: @testing-library/dom added as explicit dep — missing transitive dep exposed when plugin-react downgraded
- 02-02: PaginationControls pageParamKey prop allows /persons (?page) and /persons/:slug (?ppage) to coexist
- 02-02: GET /api/parties/{slug} stub included in plan 02 to satisfy Wave 0 test_parties.py::test_get_party
- 02-03: Party promises query uses JOIN approach (Promise JOIN Politician WHERE party_id == party.id) with ModerationStatus.approved filter (T-02-10)
- 02-04: ElectionWithCountOut is plain BaseModel (no from_attributes) — correlated subquery returns Row tuples; must unpack election_obj and count explicitly in router
- 02-04: Promise count subquery counts all linked promises (not approved-only); approved filter only applies to /promises endpoint
- 03-01: PromiseListOut and PromiseDetailOut are plain BaseModel (no from_attributes) — constructed from JOIN Row tuples (per 02-04 pattern)
- 03-02: Stats GROUP BY query is live at seed-data volume; will migrate to stats_cache in Phase 8
- 03-03: Comma-separated ?status=broken,stalled is the multi-value pattern; ResolvedStatus(s.strip()) raises 422 for invalid values
- 03-04: og.py created as minimal stub in 03-04; full OG endpoint implemented in 03-05
- 03-04: Router import order in main.py is alphabetical: elections, health, og, parties, politicians, promises, stats
- 03-05: OG bot detection via Nginx set+double-if pattern (avoids map-outside-http context issue in conf.d/default.conf)
- 03-05: default-og-image.png placeholder created in frontend/public/; replace before production
- 04-01: users table renamed columns hashed_password/is_verified/is_superuser; oauth_accounts table added
- 04-02: User inherits SQLAlchemyBaseUserTableUUID; OAuthAccount overrides user_id FK to "users.id" (base uses "user.id")
- 04-03: CSRFMiddleware registered AFTER CORSMiddleware (reverse order = CSRF inner, CORS outer)
- 04-03: /api/auth/refresh-backend registers separate 30-day cookie backend (not same as access backend)
- 04-04: AuthContext rehydrates via two-step: GET /me → 401 → POST /refresh → retry /me
- 04-05: LoginPage uses URLSearchParams (form data) not JSON for /api/auth/login (OAuth2PasswordRequestForm)
- 04-06: JWT_SECRET, RESET_PASSWORD_SECRET, VERIFICATION_SECRET are separate (no shared secret across token types)
- 04-06: COOKIE_SECURE=false in docker-compose.yml; true by default in production

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Content | AboutPage body text — replace TODO placeholder with "Our Principles" content (D-20) | Deferred | 03-04 |
| Asset | default-og-image.png — replace 1×1 placeholder with real OG image before launch | Deferred | 03-05 |

## Session Continuity

Last session: 2026-05-24T09:21:36.634Z
Stopped at: Phase 5 context gathered
Resume at: /gsd:execute-phase 4
