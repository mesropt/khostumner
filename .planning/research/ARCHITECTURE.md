# Architecture Patterns

**Domain:** Community-driven political promise tracking (wiki-style accountability platform)
**Project:** Khostumner (Խոստումներ)
**Researched:** 2026-05-20

---

## Recommended Architecture

A layered monolith with clear module boundaries. For v1 scale (Armenian civic audience, single-language, no mobile app), a well-structured monolith is simpler to deploy, debug, and iterate on than microservices. Module boundaries should be clean enough to extract services later if needed.

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Client                     │
│           (Server-rendered pages + thin JS)             │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────┐
│                    Web Application                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Auth &    │  │  Content     │  │  Moderation    │  │
│  │   Users     │  │  Module      │  │  Module        │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Voting &   │  │  Politician  │  │  Election      │  │
│  │  Evidence   │  │  Profiles    │  │  Grouping      │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Statistics Aggregation              │    │
│  └──────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   PostgreSQL Database                    │
└─────────────────────────────────────────────────────────┘
```

---

## Component Boundaries

| Component | Responsibility | Reads From | Writes To | Exposes |
|-----------|---------------|------------|-----------|---------|
| **Auth & Users** | Registration, login, session management, role assignment (visitor / registered / admin) | users, user_roles | users, sessions | Auth middleware, current_user context |
| **Content Module** | CRUD for promises; each promise starts as `pending` until approved | promises, politicians, elections | promises | Promise create/edit/delete endpoints |
| **Politician Profiles** | Aggregated view of a politician: photo, party, position, promise list, fulfillment %; read-heavy | politicians, promises, elections, stats_cache | stats_cache | Politician profile pages |
| **Election Grouping** | Organizes promises by election campaign; election is the anchor for a promise batch | elections, politicians, promises | elections | Election index + detail pages |
| **Voting & Evidence** | Records community votes on promise status; attaches evidence URLs; detects disputed threshold | votes, evidence, promises | votes, evidence | Vote endpoint, evidence CRUD |
| **Moderation Module** | Admin review queue; resolves disputed promises; approve/reject pending content | promises, votes | promises (status override) | Admin queue pages, approve/reject actions |
| **Statistics Aggregation** | Computes and caches per-politician and per-election fulfillment percentages | promises, votes | stats_cache | Computed stats used by Politician Profiles |

---

## Data Model

### Core Entities

#### `users`
```
id              UUID        PK
email           TEXT        UNIQUE NOT NULL
password_hash   TEXT        NOT NULL
display_name    TEXT        NOT NULL
role            ENUM        ('visitor_unregistered', 'registered', 'admin')
created_at      TIMESTAMPTZ
is_active       BOOLEAN     DEFAULT true
```
Note: `visitor_unregistered` is the implicit role for unauthenticated requests — no row is stored for visitors. Role stored in DB only for registered users. Admin flag is a role enum value, not a separate table, for v1 simplicity.

#### `politicians`
```
id              UUID        PK
name_hy         TEXT        NOT NULL     -- Armenian full name
slug            TEXT        UNIQUE       -- URL-friendly, e.g. "nikol-pashinyan"
photo_url       TEXT
position        TEXT                     -- e.g. "Վարչապետ", "Երեւանի քաղաքապետ"
level           ENUM        ('national', 'local', 'party')
party_id        UUID        FK → parties(id)  NULLABLE
bio_hy          TEXT
is_active       BOOLEAN     DEFAULT true
created_at      TIMESTAMPTZ
created_by      UUID        FK → users(id)
```

#### `parties`
```
id              UUID        PK
name_hy         TEXT        NOT NULL
short_name_hy   TEXT
logo_url        TEXT
founded_year    INTEGER
```

#### `elections`
```
id              UUID        PK
name_hy         TEXT        NOT NULL     -- e.g. "2021 Խ.Ժ. ընտրություններ"
slug            TEXT        UNIQUE
election_date   DATE        NOT NULL
level           ENUM        ('national', 'local', 'referendum')
description_hy  TEXT
created_at      TIMESTAMPTZ
created_by      UUID        FK → users(id)
```

#### `promises`
```
id              UUID        PK
title_hy        TEXT        NOT NULL
description_hy  TEXT
politician_id   UUID        FK → politicians(id)   NOT NULL
election_id     UUID        FK → elections(id)     NULLABLE
made_date       DATE
source_url      TEXT                               -- original source of the promise
moderation_status ENUM      ('pending', 'approved', 'rejected')   DEFAULT 'pending'
resolved_status   ENUM      ('unrated', 'kept', 'broken', 'in_progress', 'stalled', 'compromise')  DEFAULT 'unrated'
admin_override  BOOLEAN     DEFAULT false          -- true when admin forced resolved_status
created_by      UUID        FK → users(id)
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

Key design decision: `moderation_status` and `resolved_status` are separate fields.
- `moderation_status` governs whether the promise is visible to the public (admin workflow).
- `resolved_status` reflects the community/admin judgment on fulfillment.

#### `votes`
```
id              UUID        PK
promise_id      UUID        FK → promises(id)   NOT NULL
user_id         UUID        FK → users(id)      NOT NULL
status_vote     ENUM        ('kept', 'broken', 'in_progress', 'stalled', 'compromise')
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ

UNIQUE (promise_id, user_id)   -- one active vote per user per promise
```

#### `evidence`
```
id              UUID        PK
promise_id      UUID        FK → promises(id)   NOT NULL
submitted_by    UUID        FK → users(id)      NOT NULL
url             TEXT        NOT NULL
title_hy        TEXT
description_hy  TEXT
evidence_type   ENUM        ('supports_kept', 'supports_broken', 'neutral')
moderation_status ENUM      ('pending', 'approved', 'rejected')  DEFAULT 'pending'
created_at      TIMESTAMPTZ
```

#### `stats_cache`
```
id              UUID        PK
entity_type     ENUM        ('politician', 'election')
entity_id       UUID        NOT NULL
total_promises  INTEGER
kept_count      INTEGER
broken_count    INTEGER
in_progress_count INTEGER
stalled_count   INTEGER
compromise_count INTEGER
unrated_count   INTEGER
fulfillment_pct NUMERIC(5,2)   -- (kept + compromise) / (total - unrated)
computed_at     TIMESTAMPTZ
```
This table is a write-through cache populated by a background job or post-vote hook. Politician profile pages read from here rather than re-aggregating on every request.

---

## Entity Relationships

```
parties ────────< politicians >────── elections
                      │                    │
                      └──────< promises >──┘
                                   │
                        ┌──────────┼──────────┐
                        │          │           │
                      votes    evidence   (moderation)
                        │
                      users ──> user_roles (via enum)
```

One politician may appear in many elections (many-to-many via promises; a promise links one politician + one election). Elections do not directly own politicians — the promise record is the junction.

---

## Data Flow

### 1. Promise Submission Flow
```
Registered User → POST /promises
    → ContentModule validates fields
    → Promise saved with moderation_status='pending'
    → NOT visible on public pages
    → Moderation queue entry appears in admin panel
Admin reviews → approve → moderation_status='approved', visible publicly
             → reject  → moderation_status='rejected', stored but hidden
```

### 2. Community Voting Flow
```
Registered User → POST /promises/:id/vote { status_vote }
    → VotingModule upserts vote row (one per user per promise)
    → Aggregate vote count recalculated
    → If no admin_override: resolved_status updated to plurality winner
    → If vote distribution is contested (e.g. <60% agreement): flag as 'disputed'
    → StatisticsAggregation updates stats_cache for the politician + election
```
Disputed threshold recommendation: if top vote choice has <60% of total votes AND >=10 votes cast, mark as disputed and surface in admin moderation queue.

### 3. Admin Override Flow
```
Admin → POST /admin/promises/:id/override { resolved_status }
    → admin_override = true on promise row
    → resolved_status set to admin's choice
    → Community votes still stored (audit trail), but no longer drive resolved_status
    → StatisticsAggregation updates stats_cache
```

### 4. Politician Profile Page Load (read path)
```
Browser → GET /politicians/:slug
    → PoliticianProfiles component
    → Read politicians row
    → Read stats_cache for politician_id (precomputed)
    → Read approved promises WHERE politician_id = :id
    → Each promise shows resolved_status + vote counts
    → Render: photo, position, fulfillment%, promise list grouped by election
```

### 5. Evidence Submission Flow
```
Registered User → POST /promises/:id/evidence { url, title, type }
    → VotingModule/Evidence creates evidence row with moderation_status='pending'
    → Admin approves → visible on promise detail page
    → Each approved evidence link displayed with support/oppose tag
```

---

## Status State Machine

### `moderation_status` (content visibility)
```
pending ──[admin approve]──> approved
pending ──[admin reject]───> rejected
approved ──[admin re-review]──> pending  (possible edge case)
```
All user-submitted promises and evidence begin as `pending`. Only approved content is publicly visible.

### `resolved_status` (fulfillment judgment)
```
unrated
  ├──[community votes reach threshold]──> kept / broken / in_progress / stalled / compromise
  └──[admin override]────────────────────> any status (admin_override=true)
kept / broken / etc.
  ├──[new votes shift plurality]──> different status (if not admin_override)
  └──[admin override changes]──────> any status
```

---

## Suggested Build Order (Phase Dependencies)

The following order respects hard dependencies — each layer requires the one above it.

### Layer 1 — Data Foundation
**Build first.** Everything else reads from these tables.
- Database schema: all core tables above
- Politicians CRUD (admin-only)
- Parties CRUD (admin-only)
- Elections CRUD (admin-only)
- Static public pages: politician list, politician profile (read-only, no promises yet)

No auth required to view; no voting yet. Validates data model before building workflows.

### Layer 2 — Auth & Roles
**Required for all user actions.**
- User registration + login (session or JWT)
- Role enforcement middleware (visitor / registered / admin)
- Protected routes

### Layer 3 — Promise Content Pipeline
**Requires Layer 1 + 2.**
- Promise submission form (registered users)
- Promise detail page (public, read-only)
- Admin moderation queue: approve / reject pending promises
- Evidence submission + moderation (same queue, same pattern)

This is the first full cycle: create → moderate → publish.

### Layer 4 — Community Voting
**Requires Layer 3** (votes attach to approved promises).
- Vote casting endpoint (one vote per user per promise)
- Vote aggregation → resolved_status derivation
- Dispute detection + surfacing in admin queue
- Admin override of resolved_status

### Layer 5 — Statistics & Aggregation
**Requires Layer 4** (stats depend on votes and resolved_status).
- stats_cache population (background job or post-vote hook)
- Politician profile: fulfillment percentage display
- Election summary page: aggregate stats per election
- "Kept" / "Broken" filtered listing pages

### Layer 6 — Navigation & Discovery
**Requires Layers 1–5** (links to everything).
- Top navigation: Kept, Broken, Politicians, Elections, Create Promise
- Search (basic text search over promise titles, politician names)
- Politician index page sorted by fulfillment rate

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mixing moderation_status and resolved_status
**What:** Using a single `status` field to mean both "is this content approved?" and "is this promise kept?"
**Why bad:** Forces content visibility to couple with fulfillment judgment. An approved promise can have an evolving resolved_status; a rejected promise should be hidden regardless of any vote.
**Instead:** Two separate fields as specified above.

### Anti-Pattern 2: Recomputing fulfillment stats on every page load
**What:** Running GROUP BY + COUNT aggregations at request time on the politician profile page.
**Why bad:** Every politician profile hit issues expensive aggregate queries. Under any real traffic this becomes a bottleneck.
**Instead:** Write-through stats_cache updated after each vote or admin action. Profile page reads precomputed values.

### Anti-Pattern 3: Storing only the final vote tally, discarding individual votes
**What:** Keeping only a single `vote_counts` JSON blob on the promise row.
**Why bad:** Can't audit who voted, can't prevent double-voting, can't recalculate on rule changes, can't detect sockpuppet patterns.
**Instead:** Individual vote rows with UNIQUE(promise_id, user_id) constraint. Tally derived from rows.

### Anti-Pattern 4: Flat admin role without moderation queue
**What:** Admin directly edits promise rows in a database admin panel.
**Why bad:** No audit trail, no workflow, no visibility into what needs attention, no accountability for moderation decisions.
**Instead:** Dedicated moderation queue showing `pending` items with explicit approve/reject actions. Every moderation action logged with admin user_id and timestamp.

### Anti-Pattern 5: Embedding election data inside politician rows
**What:** Storing election context as a string field on the promise (e.g., `election_name: "2021 elections"`).
**Why bad:** Breaks election-level grouping, prevents consistent display of "all promises from the 2021 elections" across multiple politicians, leads to typo inconsistencies.
**Instead:** Normalized `elections` table with FK from promises.

---

## Scalability Considerations

| Concern | At v1 (hundreds of promises) | At scale (thousands) |
|---------|------------------------------|----------------------|
| Profile stats | Compute on request acceptable | Switch to stats_cache write-through |
| Moderation queue | Simple DB query on pending rows | Add queue-type indexing, possibly dedicated admin tool |
| Vote storage | Full row per vote, fine | Add index on (promise_id, status_vote) for fast tally |
| Full-text search | ILIKE query or pg_trgm on promises.title_hy | PostgreSQL full-text search (Armenian tokenizer may be limited — flag for research) |
| Session storage | DB-backed sessions fine | Move to Redis if session volume grows |

Armenian full-text search is a known risk: PostgreSQL's built-in text search has no Armenian language dictionary. For v1, ILIKE or pg_trgm extension (trigram matching) is adequate for short Armenian strings. Deeper search is deferred per PROJECT.md.

---

## Component Communication Summary

```
Browser
  └── HTTP ──> Web Routes
                  ├── Auth Middleware (validates session, injects role)
                  ├── Content Module (promise CRUD, election/politician CRUD)
                  ├── Voting Module (votes, evidence)
                  ├── Moderation Module (admin queue, overrides)
                  ├── Profile Module (read-heavy, uses stats_cache)
                  └── Statistics Aggregator
                          └── writes to stats_cache after vote/override events
All modules ──> PostgreSQL (single database, schema-level separation)
```

No message queue or async worker needed in v1. Statistics can be recalculated synchronously in the same request as a vote (acceptable at small scale). Extract to background job when latency becomes measurable.

---

## Sources

- PromiseTracker by Code for Africa (architecture inferred from live site and GitHub): https://github.com/CodeForAfrica/PromiseTracker
- PolitiFact Promise Tracker (status taxonomy reference): https://www.politifact.com/truth-o-meter/promises/
- Polimeter (political science-backed promise tracking): https://www.polimeter.org/en
- MediaWiki database model (wiki-style content architecture reference): https://www.mediawiki.org/wiki/Manual:MediaWiki_architecture
- Drupal Workflows module (state machine pattern for content moderation): https://drupalize.me/tutorial/overview-workflows-and-content-moderation
- Optimizely Community API moderation workflows: https://docs.developers.optimizely.com/content-management-system/v1.4.0-community-api/docs/moderation-workflows
- Content moderation database architecture (SQL schema patterns): https://www.sqlservercentral.com/articles/database-architecture-considerations-for-implementing-content-moderation-services
- RBAC implementation guide: https://www.permit.io/blog/best-practices-to-implement-rbac-for-developers