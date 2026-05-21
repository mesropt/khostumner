# Khostumner — Project Guide

Armenian political promise tracker. Wikipedia-style site where users and admins collect politicians' pre-election promises and track their fulfillment via crowdsourced voting with admin moderation.

## Stack

- **Backend**: FastAPI (Python 0.115.x) + SQLAlchemy 2.x (async) + Alembic
- **Database**: PostgreSQL 17 + pg_trgm for full-text search
- **Frontend**: React 19 + Vite + TanStack Query v5 + Tailwind CSS v4 + shadcn/ui
- **Auth**: JWT sessions; FastAPI-Users or custom JWT with RBAC (user / moderator / admin)
- **Language**: Armenian (հայերեն) — primary UI and content language

## Key Architecture Rules

1. **Two separate status fields** on every promise: `moderation_status` (is content visible?) and `resolved_status` (is promise kept/broken?). Never merge them.
2. **Individual vote rows** with `UNIQUE(promise_id, user_id)` — never store only an aggregate tally.
3. **stats_cache table** holds precomputed fulfillment percentages. Politician profile pages read from it. Never GROUP BY on every request.
4. **No admin status override** — `resolved_status` is set ONLY by community vote threshold (>50% with ≥25 votes). Admins can ONLY reset votes when proven brigading is documented (VOTE-04). Admins never set `resolved_status` directly.

## GSD Workflow

This project uses GSD for phased development. Planning artifacts live in `.planning/`.

### Workflow commands (run in order per phase)

```
/gsd:discuss-phase N    # Gather context before planning
/gsd:plan-phase N       # Create PLAN.md with tasks
/gsd:execute-phase N    # Execute all plans
/gsd:verify-work N      # Verify phase requirements met
```

### Current state

See `.planning/STATE.md` for current phase and progress.
See `.planning/ROADMAP.md` for all 8 phases.
See `.planning/REQUIREMENTS.md` for all 27 v1 requirements.

## Phase Overview

| Phase | Name | Key Deliverable |
|-------|------|-----------------|
| 1 | Foundation | FastAPI + React + PostgreSQL scaffold + CI |
| 2 | Politicians, Parties & Elections | Read-only browsing of entities |
| 3 | Promise Browsing & Homepage | Homepage stats, promise list/detail, OG tags |
| 4 | Authentication | Email + OAuth registration, JWT sessions |
| 5 | Promise Submission | Submit + edit promises with election linking |
| 6 | Admin Moderation | Moderation queue, edit history, profile CRUD |
| 7 | Community Voting | Vote system, admin override, vote distribution |
| 8 | Search & Statistics | Full-text search + fulfillment % stats |

## Critical Pitfalls (from research)

- **Armenian defamation law**: Fines up to 6M AMD. Require verbatim quotes + source links for every promise. Legal consultation before public launch.
- **Vote brigading**: Political factions can coordinate. Require account age ≥ 7 days + email verification before voting. Log IPs.
- **Source rot**: Armenian news URLs die. Archive evidence URLs at submission time (Wayback Machine API).
- **Schema inflexibility**: Politicians change parties. Use time-bounded party affiliation table, not a static FK.
- **Fulfillment rubric**: Define "Kept / Broken / In Progress / Stalled" in writing before building any voting UI.

## Next Step

```
/gsd:discuss-phase 1
```