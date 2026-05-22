# Roadmap: Khostumner (Խոստումներ)

## Overview

Khostumner is built in 8 focused phases. Phase 1 lays the technical foundation (FastAPI + React/Vite + PostgreSQL + CI). Phases 2-3 deliver read-only public browsing of politicians, parties, elections, and promises so the site is useful immediately with seed data. Phase 4 adds authentication. Phases 5-6 add the full promise submission and admin moderation pipeline. Phase 7 introduces community voting and the dual-status model. Phase 8 completes the product with site-wide search and computed fulfillment statistics.

Every v1 requirement maps to exactly one phase. The first user-facing capability ships at the end of Phase 2.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - FastAPI + React/Vite + PostgreSQL scaffold, full DB schema, CI pipeline, seed data loader
- [x] **Phase 2: Politicians, Parties & Elections Browsing** - Read-only public pages for politicians, parties, and elections (completed 2026-05-22)
- [ ] **Phase 3: Promise Browsing & Homepage** - Read-only promise list, detail pages, homepage stats, section pages, OG tags
- [ ] **Phase 4: Authentication** - Email/password registration, email verification, password reset, OAuth, persistent JWT sessions
- [ ] **Phase 5: Promise Submission** - Registered users submit and edit promises; election linking
- [ ] **Phase 6: Admin Moderation** - Admin manages moderation queue, edit history, and politician/party profiles
- [ ] **Phase 7: Community Voting & Status System** - Registered users vote on promise status; admin override; vote distribution display
- [ ] **Phase 8: Search & Statistics** - Site-wide full-text search; fulfillment percentage computed via stats_cache

## Phase Details

### Phase 1: Foundation
**Goal**: The project runs end-to-end locally and in CI — FastAPI serves a health endpoint, React/Vite renders a shell, PostgreSQL holds the full schema with seed data, and the test/lint pipeline is green.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: *(infrastructure only — no user-facing requirement IDs; enables all subsequent phases)*
**Success Criteria** (what must be TRUE):
  1. `GET /health` returns 200 from the FastAPI backend
  2. React/Vite dev server renders the app shell without errors
  3. PostgreSQL database is reachable and all schema migrations run cleanly from a fresh state
  4. Seed data loader populates at least 3 politicians, 2 elections, and 5 promises for development use
  5. CI pipeline runs lint and tests and reports pass/fail on every push
**Plans**: 2 plans

Plans:

**Wave 1**
- [x] 01-01-PLAN.md — Project scaffold, full DB schema (12 tables), FastAPI health endpoint, Docker Compose, Wave 0 test stubs

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-02-PLAN.md — Seed data (10 politicians / 4 parties / 4 elections / 20 promises), React/Vite shell wired to health endpoint, GitHub Actions CI

**Cross-cutting constraints:**
- Two-status fields (`moderation_status` + `resolved_status`) must never be merged — enforced in both plans
- Alembic URL swap: `postgresql+asyncpg://` (runtime) ↔ `postgresql://` (migrations) — enforced in 01-01

### Phase 2: Politicians, Parties & Elections Browsing
**Goal**: Any visitor can browse politician profiles, the full persons list, party/bloc pages, and the elections list and detail pages — with real data served from the API.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: POLS-01, POLS-02, POLS-03, ELEC-01, ELEC-02
**Success Criteria** (what must be TRUE):
  1. Visitor can open a politician profile page and see photo, full name, current role, party affiliation, and a list of linked promises
  2. Visitor can browse the "Persons" section — paginated list of politicians — and filter by party or role
  3. Visitor can open a party or bloc page and see linked promises and member politicians
  4. Visitor can open the elections list page and see all elections with their promise counts
  5. Visitor can open an election detail page and see all promises linked to that election across all politicians
**Plans**: 4 plans
**UI hint**: yes

Plans:

**Wave 1**
- [x] 02-01-PLAN.md — Wave 0 scaffolding: Party slug migration, shadcn/ui installs, shared backend schemas (PaginatedResponse, PromiseStubOut), Layout + App.tsx routing, frontend types, Wave 0 test stubs

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 02-02-PLAN.md — Politicians browsing slice: PoliticianOut schema + politicians router (list/detail/promises) + PersonsPage + PoliticianProfilePage (POLS-01, POLS-02)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 02-03-PLAN.md — Party page slice: PartyOut schema + expanded parties router (detail/members/promises) + PartyPage (POLS-03)

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 02-04-PLAN.md — Elections slice: ElectionOut/ElectionWithCountOut schemas + elections router (list with promise count/detail/promises) + ElectionsListPage + ElectionDetailPage + human verification checkpoint (ELEC-01, ELEC-02)

**Cross-cutting constraints:**
- All promise queries on public pages MUST filter `moderation_status=approved` — enforced in politicians, parties, elections routers
- `PaginatedResponse[T]` generic (from `app.schemas.common`) used for ALL list endpoints — no per-entity custom envelopes
- Party slug field added via Alembic migration in Wave 1 — all party URLs use `/parties/:slug`
- Page state stored in URL query params via `useSearchParams` — not React `useState`

### Phase 3: Promise Browsing & Homepage
**Goal**: Any visitor can see the homepage with overall stats, browse fulfilled and unfulfilled promises, view promise details with sources and status, and share links that render rich Open Graph previews.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: PROM-01, PROM-02, DISC-01, DISC-02, DISC-03, DISC-05
**Success Criteria** (what must be TRUE):
  1. Homepage displays total promise count and a fulfillment breakdown by status
  2. Visitor can browse a paginated promise list and filter by status, politician, or election
  3. Visitor can open a promise detail page showing the verbatim quote, source links, status badge, promised date, and a shareable slug URL
  4. "Կատարված" section shows all fulfilled promises, paginated
  5. "Չկատարված" section shows all broken or stalled promises, paginated
  6. Sharing a promise detail URL on social media renders an Open Graph card with title, status, and politician name
**Plans**: 5 plans
**UI hint**: yes

Plans:

**Wave 1**
- [ ] 03-01-PLAN.md — Wave 0 scaffolding: PromiseListOut/PromiseDetailOut/StatsOut schemas, RED test stubs (test_promises, test_stats, test_og), shadcn input/separator install, frontend PromiseListOut/PromiseDetailOut/StatsOut/StatsByStatus types

**Wave 2** *(blocked on Wave 1 completion — 03-02 and 03-03 run in parallel)*
- [ ] 03-02-PLAN.md — Stats slice: GET /api/stats router + useStats hook + HomePage replacement (stats block + recent promises) (DISC-01)
- [ ] 03-03-PLAN.md — Promises list slice: GET /api/promises router (7 filter params, comma-split status) + PromiseCard + usePromises hook + PromisesListPage + FulfilledPage + UnfulfilledPage (PROM-01, DISC-02, DISC-03)

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 03-04-PLAN.md — Promise detail + wiring: GET /api/promises/{slug} detail endpoint + main.py router registration + usePromise hook + PromiseDetailPage + AboutPage + Layout nav update + App.tsx routes (PROM-02)

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 03-05-PLAN.md — OG + Nginx: GET /api/og/promises/{slug} HTML endpoint + nginx/nginx.conf bot UA routing + docker-compose.yml nginx service + human verification checkpoint (DISC-05)

**Cross-cutting constraints:**
- All public promise endpoints MUST filter `moderation_status=approved` — never expose pending/rejected
- `PromiseListOut` and `PromiseDetailOut` are plain `BaseModel` (no `from_attributes`) — constructed from JOIN Row tuples
- Comma-separated `?status=broken,stalled` is the multi-value pattern for `/unfulfilled` (D-07b)
- Null-date promises (`expected_date=null`) MUST NOT be filtered out when no date filter is applied (D-07b)
- OG bot detection in Nginx/Docker Compose layer only — NOT in FastAPI application code (D-17)

### Phase 4: Authentication
**Goal**: Users can create accounts, verify their email, log in with email/password or OAuth, reset forgotten passwords, and stay logged in across browser sessions via JWT.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05
**Success Criteria** (what must be TRUE):
  1. User can register with email and password and receives a verification email
  2. User can verify their email via the link in the verification email and gain full account access
  3. User can log in with email/password and remain logged in after a browser refresh (JWT persisted)
  4. User can log in via Google or GitHub OAuth without a separate password
  5. User can request a password reset email and set a new password via the link
**Plans**: TBD

### Phase 5: Promise Submission
**Goal**: Registered and verified users can submit new promises with required fields and source links, submit edits to existing promises, and link promises to elections — all entering an admin review queue.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: PROM-03, PROM-04, ELEC-03
**Success Criteria** (what must be TRUE):
  1. Logged-in user can submit a new promise with verbatim quote, source URL, promised date, and optional expected fulfillment date
  2. Submitted promise appears in the admin moderation queue rather than going live immediately
  3. Logged-in user can submit an edit to an existing promise that enters the admin review queue
  4. When submitting a promise, user can link it to one or more elections from a picker
**Plans**: TBD
**UI hint**: yes

### Phase 6: Admin Moderation
**Goal**: Admins can review and action every promise submission and edit in the moderation queue, view full edit history for any promise, and create or update politician and party profiles directly.
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: PROM-05, PROM-06, POLS-04, POLS-05
**Success Criteria** (what must be TRUE):
  1. Admin can open the moderation queue and see all pending promise submissions and edits
  2. Admin can approve or reject each item in the queue; approved items become visible site-wide
  3. Admin can view the full edit history of any promise with timestamps and submitter info
  4. Admin can create a new politician or party profile and edit any existing profile
  5. Registered user can submit a new or edited politician/party profile that enters the admin review queue
**Plans**: TBD
**UI hint**: yes

### Phase 7: Community Voting & Status System
**Goal**: Verified users (account ≥30 days) vote on promise status; resolved status is set automatically when >50% consensus is reached with ≥25 votes; full vote statistics are always public; admins can reset votes on proven brigading.
**Mode:** mvp
**Depends on**: Phase 6
**Requirements**: VOTE-01, VOTE-02, VOTE-03, VOTE-04, VOTE-05
**Success Criteria** (what must be TRUE):
  1. Logged-in user with account ≥30 days old and verified email can cast and change a vote on promise status
  2. Each user holds exactly one vote per promise at a time (UNIQUE constraint enforced)
  3. Resolved status updates automatically when leading option exceeds >50% of total votes AND total votes ≥ 25 (configurable); otherwise status stays Չգնահատված
  4. Promise detail page shows vote count per status, total votes, and current resolved status — always visible to all visitors
  5. Admin can reset all votes for a promise (with documented brigading reason); vote threshold minimum is configurable in admin settings
**Plans**: TBD

### Phase 8: Search & Statistics
**Goal**: Any visitor can search the site by keyword and find matching promises, politicians, and parties; politician profile pages display computed fulfillment percentages backed by the stats_cache table.
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: DISC-04
**Success Criteria** (what must be TRUE):
  1. Site-wide search input returns matching promises, politicians, and parties for a given keyword
  2. Search uses PostgreSQL full-text search (tsvector) and returns results in under 500 ms for typical queries
  3. Politician profile page displays a fulfillment percentage computed from the stats_cache table
  4. stats_cache is updated when a promise's resolved_status changes (via vote or admin override)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/2 | Complete | 2026-05-21 |
| 2. Politicians, Parties & Elections Browsing | 4/4 | Complete   | 2026-05-22 |
| 3. Promise Browsing & Homepage | 0/5 | In progress | - |
| 4. Authentication | 0/TBD | Not started | - |
| 5. Promise Submission | 0/TBD | Not started | - |
| 6. Admin Moderation | 0/TBD | Not started | - |
| 7. Community Voting & Status System | 0/TBD | Not started | - |
| 8. Search & Statistics | 0/TBD | Not started | - |
