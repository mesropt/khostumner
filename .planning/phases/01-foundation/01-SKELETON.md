---
phase: 01-foundation
type: walking-skeleton
created: 2026-05-21
status: planned
---

# Walking Skeleton: Khostumner

## Capability Proven

A developer clones the repository, runs `docker-compose up --build`, and within a few minutes:

1. `http://localhost:8000/health` returns `{"status": "ok"}` (FastAPI + PostgreSQL connected)
2. `http://localhost:5173` shows the React app shell displaying "API Status: ok" (React fetching from FastAPI)
3. The database holds all 12 tables populated by Alembic migrations, with seed data: 10 politicians, 4 parties, 4 elections, 20 promises
4. `pytest backend/tests/` passes (health check, schema verification, seed counts)
5. GitHub Actions CI runs `ruff + pytest` and `eslint + tsc + vitest` on every push

This proves the full stack is wired end-to-end: Browser → Vite → React → fetch → FastAPI → SQLAlchemy → PostgreSQL.

---

## Architectural Decisions

These decisions are established in Phase 1 and must NOT be renegotiated in subsequent phases.

### Language & Runtime
| Layer | Decision | Rationale |
|-------|----------|-----------|
| Backend language | Python 3.12 | LTS release; matches `python:3.12-slim` Docker image |
| Frontend language | TypeScript 5.x | Type safety for a maintainable SPA |
| Runtime | Docker Compose (dev) | Single `docker-compose up` — no local Python/Node required |

### Framework & Libraries
| Concern | Choice | Version | Locked Reason |
|---------|--------|---------|---------------|
| Web framework | FastAPI | 0.115.14 | CLAUDE.md + D-01 |
| ASGI server | Uvicorn[standard] | 0.47.0 | Standard ASGI server for FastAPI |
| ORM | SQLAlchemy async | 2.0.49 | Async-first; `async_sessionmaker` pattern |
| DB driver (runtime) | asyncpg | 0.31.0 | Async PostgreSQL for SQLAlchemy 2 |
| DB driver (migrations) | psycopg2-binary | 2.9.12 | Alembic migration runner is synchronous |
| Migrations | Alembic | 1.18.4 | Autogenerate + named constraints |
| Schema validation | Pydantic | 2.13.4 | Request/response validation; v2 native |
| Settings | pydantic-settings | latest | Separate package since pydantic v2 |
| UI framework | React | 19.x | CLAUDE.md + D-03 |
| Build tool | Vite | 6.x | Replaces CRA; Tailwind v4 compatible |
| CSS | Tailwind CSS | 4.x | CSS-first; `@import "tailwindcss"` syntax |
| Tailwind integration | @tailwindcss/vite | 4.x | Replaces PostCSS for Tailwind v4 |
| Routing (client) | React Router | 7.x | Declarative mode (not framework mode) |
| Server state | TanStack Query | 5.x | Caching + async data fetching |
| Component library | shadcn/ui | latest | Vite-compatible; components.json configured |
| Backend test client | httpx AsyncClient + ASGITransport | 0.28.1 | Zero network overhead; official pattern |
| Backend linter | ruff | 0.15.13 | Replaces flake8 + black |
| Frontend tests | Vitest | 4.x | Vite-native; replaces Jest |

### Database
| Concern | Decision | Locked Reason |
|---------|----------|---------------|
| Engine | PostgreSQL 17 | CLAUDE.md |
| Schema strategy | Full 8-phase schema in Phase 1 | D-04 — avoids costly future migrations |
| Promise status model | TWO separate fields: `moderation_status` + `resolved_status` | D-07, CLAUDE.md rule #1 — NEVER merge |
| Vote storage | Individual rows with UNIQUE(promise_id, user_id) | D-08, CLAUDE.md rule #2 |
| Vote history | Immutable audit log; old row preserved on change | D-09 |
| Stats | `stats_cache` table per politician; never GROUP BY on request | D-10, CLAUDE.md rule #3 |
| Evidence | Includes `archived_url` + `quote_excerpt` from Phase 1 | D-11 |
| Vote threshold | Configurable in `app_settings` table | D-12 |
| Party affiliation | Time-bounded via `politician_party_memberships` table | D-06 |
| Enum naming | Shared enums defined once, imported elsewhere | Pitfall 7 prevention |

### Directory Layout
```
khostumner/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Makefile
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml          # pytest + ruff config
│   ├── requirements.txt        # production deps
│   ├── requirements-dev.txt    # test + lint deps
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py              # async runner + URL scheme swap
│   │   └── versions/           # generated migration files
│   └── app/
│       ├── main.py             # FastAPI + lifespan + CORS
│       ├── config.py           # pydantic-settings
│       ├── database.py         # async engine + sessionmaker
│       ├── models/             # one file per domain entity
│       ├── routers/            # one file per domain entity
│       ├── schemas/            # pydantic request/response models
│       └── services/           # business logic + seed loader
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts          # @tailwindcss/vite + HMR port 24678
    ├── components.json         # shadcn/ui config
    └── src/
        ├── main.tsx            # StrictMode + QueryClientProvider
        ├── App.tsx             # BrowserRouter + Routes
        ├── index.css           # @import "tailwindcss"
        ├── api/                # fetch wrapper + base URL
        ├── components/ui/      # shadcn/ui components
        ├── hooks/              # TanStack Query hooks
        ├── pages/              # route-level React components
        └── types/              # shared TypeScript interfaces
```

### Authentication
Not established in Phase 1. Phase 4 will add JWT sessions with email/password + OAuth. RBAC roles (registered/moderator/admin) are defined in the `users` table from Phase 1.

### Deployment
Not established in Phase 1. Docker Compose is for local dev only. Production deployment target TBD.

---

## Stack Touched

| Layer | Files Created | Key Pattern Established |
|-------|---------------|-------------------------|
| Database | `alembic/versions/<initial>.py` | All 12 tables in one migration; naming convention via MetaData |
| Backend models | `app/models/*.py` | SQLAlchemy 2 `mapped_column` syntax; shared enums imported not redefined |
| Backend routing | `app/routers/health.py` | APIRouter; include_router in main.py |
| Backend config | `app/config.py` | pydantic-settings; DATABASE_URL from env |
| Backend DB | `app/database.py` | `async_sessionmaker`; `get_db` dependency |
| Backend tests | `tests/test_health.py` | `ASGITransport(app=app)` — no live server needed |
| Seed data | `app/services/seed.py` | Idempotent; ENVIRONMENT guard; session.flush() for FK resolution |
| Frontend shell | `src/App.tsx` | BrowserRouter + declarative Routes |
| Frontend data | `src/hooks/useHealth.ts` | `useQuery` from TanStack Query v5 |
| Frontend config | `vite.config.ts` | `@tailwindcss/vite` plugin; `hmr.port = 24678` |
| CI | `.github/workflows/ci.yml` | Backend + frontend jobs; postgres service container |

---

## Out of Scope for Walking Skeleton

The following are explicitly deferred to later phases and must NOT be built in Phase 1:

- User authentication (Phase 4)
- Promise submission forms (Phase 5)
- Admin moderation queue (Phase 6)
- Community voting (Phase 7)
- Search (Phase 8)
- Production deployment / Dockerfile.prod (future)
- Email sending infrastructure (Phase 4)
- OAuth provider configuration (Phase 4)
- Wayback Machine API integration (Phase 5 — at submission time)
- stats_cache population triggers (Phase 7 — when votes are processed)
- pg_trgm extension and tsvector columns (Phase 8)

---

## Subsequent Slice Plan

Each subsequent phase builds a complete vertical slice (user-visible capability) on top of this skeleton:

| Phase | Slice | New Tables Used | New Endpoints |
|-------|-------|-----------------|---------------|
| 2 | Politician / party / election browsing | politicians, parties, elections, politician_party_memberships | GET /politicians, GET /politicians/{slug}, GET /parties, GET /elections |
| 3 | Promise list, detail, homepage stats | promises, promise_election_links | GET /promises, GET /promises/{slug}, GET /stats |
| 4 | Auth (register, login, verify) | users | POST /auth/register, POST /auth/login, POST /auth/verify |
| 5 | Promise submission | promises, evidence, promise_election_links | POST /promises, PATCH /promises/{id} |
| 6 | Admin moderation | promises (status updates), politicians, parties | GET /admin/queue, PATCH /admin/promises/{id} |
| 7 | Community voting + status resolution | votes, vote_history, stats_cache | POST /votes, GET /votes/{promise_id} |
| 8 | Search + fulfillment stats | stats_cache (read), tsvector columns | GET /search, GET /politicians/{slug}/stats |

The Walking Skeleton schema supports all phases without additional table creation. Only indexes, tsvector columns (Phase 8), and application logic change after Phase 1.

---

*Skeleton produced by: /gsd:plan-phase 1*
*Date: 2026-05-21*
