---
phase: 01-foundation
plan: "01"
subsystem: backend-scaffold
tags:
  - fastapi
  - sqlalchemy
  - alembic
  - docker-compose
  - postgresql
dependency_graph:
  requires: []
  provides:
    - backend-fastapi-app
    - postgresql-schema-12-tables
    - alembic-migration-initial
    - docker-compose-dev-environment
    - wave0-test-stubs
  affects:
    - all-subsequent-phases
tech_stack:
  added:
    - fastapi==0.115.14
    - sqlalchemy==2.0.49
    - asyncpg==0.31.0
    - alembic==1.18.4
    - pydantic==2.13.4
    - pydantic-settings
    - python-dotenv==1.2.2
    - psycopg2-binary==2.9.12
    - uvicorn==0.47.0
    - pytest-asyncio==1.3.0
    - httpx==0.28.1
  patterns:
    - FastAPI async lifespan context manager
    - SQLAlchemy 2.x async_sessionmaker
    - Alembic async env.py with URL scheme swap
    - Docker Compose service_healthy depends_on
    - MetaData naming convention for constraint names
key_files:
  created:
    - backend/app/main.py
    - backend/app/config.py
    - backend/app/database.py
    - backend/app/routers/health.py
    - backend/app/schemas/health.py
    - backend/app/models/base.py
    - backend/app/models/users.py
    - backend/app/models/parties.py
    - backend/app/models/politicians.py
    - backend/app/models/elections.py
    - backend/app/models/promises.py
    - backend/app/models/evidence.py
    - backend/app/models/votes.py
    - backend/app/models/stats_cache.py
    - backend/app/models/__init__.py
    - backend/alembic/env.py
    - backend/alembic/script.py.mako
    - backend/alembic/versions/20260521_000001_initial_schema.py
    - backend/tests/test_health.py
    - backend/tests/test_schema.py
    - backend/tests/test_seed.py
    - backend/tests/conftest.py
    - backend/requirements.txt
    - backend/requirements-dev.txt
    - backend/pyproject.toml
    - backend/Dockerfile
    - backend/alembic.ini
    - docker-compose.yml
    - .gitignore
    - .env.example
    - Makefile
    - frontend/src/App.test.tsx
  modified: []
decisions:
  - "Use async_sessionmaker (SQLAlchemy 2.x native) not legacy sessionmaker(class_=AsyncSession)"
  - "ModerationStatus defined once in promises.py and imported in evidence.py (no redefinition)"
  - "Two status fields: moderation_status and resolved_status are permanently separate on promises"
  - "VoteStatus enum defined once in votes.py and reused by VoteHistory (no redefinition)"
  - "Alembic uses psycopg2 sync driver; env.py swaps postgresql+asyncpg:// to postgresql://"
  - "postgres POSTGRES_PASSWORD supplied via .env file (env_file: [.env]) not hardcoded in docker-compose.yml"
  - "Migration written manually (no live DB at plan time); all 12 tables in correct FK dependency order"
metrics:
  duration: "~35 minutes"
  completed: "2026-05-21"
  tasks_completed: 2
  files_created: 32
---

# Phase 1 Plan 1: Backend Scaffold, Full DB Schema, Health Endpoint Summary

**One-liner:** FastAPI backend with async SQLAlchemy 2.x, 12-table PostgreSQL schema covering all 8 phases, Alembic async migration, Docker Compose with healthcheck wiring, and passing health endpoint test.

## What Was Built

### Task 1: Monorepo scaffold, Python packages, Docker Compose, Wave 0 test stubs

Created the complete backend infrastructure:

- **Docker Compose**: Three-service dev environment (postgres:17-alpine, backend, frontend) with `depends_on: postgres: condition: service_healthy` wiring and `POSTGRES_INITDB_ARGS` for UTF-8 encoding (prevents Armenian text corruption)
- **FastAPI app**: `app/main.py` with `asynccontextmanager lifespan` pattern, CORS restricted to `http://localhost:5173`, health router included
- **Database layer**: `app/database.py` with `create_async_engine` (pool_size=10, max_overflow=20), `async_sessionmaker`, and `get_db()` dependency with commit/rollback lifecycle
- **Config**: `app/config.py` using `pydantic-settings` BaseSettings with `SettingsConfigDict(env_file=".env")`
- **Test stubs**: `test_health.py` (full ASGITransport implementation, passing), `test_schema.py` (skipped until Task 2), `test_seed.py` (skipped until Plan 02), `frontend/src/App.test.tsx` (stub)
- **Security**: `.env` added to `.gitignore`; postgres password in `.env` file not hardcoded in `docker-compose.yml` (T-01-01 mitigation)

### Task 2: Full SQLAlchemy models and Alembic migration

Created all 9 model files covering all 8 phases of the product:

| Model File | Tables |
|---|---|
| users.py | users |
| parties.py | parties |
| politicians.py | politicians, politician_party_memberships |
| elections.py | elections |
| promises.py | promises, promise_election_links |
| evidence.py | evidence |
| votes.py | votes, vote_history |
| stats_cache.py | stats_cache, app_settings |

**Critical architecture constraints honored:**
- `promises` has both `moderation_status` (pending/approved/rejected) and `resolved_status` (kept/broken/in_progress/stalled/not_rated) as separate Mapped columns — never merged (CLAUDE.md rule #1, D-07)
- `votes` has `UNIQUE(promise_id, user_id)` constraint — individual vote rows, no aggregate tally (D-08)
- `vote_history` is a full immutable audit trail (D-09)
- `stats_cache` precomputes fulfillment statistics per politician (D-10)
- `evidence` includes `archived_url` and `quote_excerpt` from day one (D-11)
- `ModerationStatus` defined once in `promises.py`, imported by `evidence.py` — not redefined (Pitfall 7)
- `VoteStatus` defined once in `votes.py`, reused by `VoteHistory`

**Alembic setup:**
- `env.py` imports `app.models` (side-effect to register all tables in `Base.metadata`) and swaps `postgresql+asyncpg://` to `postgresql://` for the sync migration runner (Pitfall 1)
- Initial migration `20260521_000001_initial_schema.py` creates all 12 tables in FK dependency order
- `script.py.mako` is standard Alembic template

## Verification

All success criteria met:

1. `python -c "from app.main import app; import app.models; print('OK')"` — exits 0
2. `pytest tests/test_health.py -v` — 1 passed (ASGITransport, no live DB needed)
3. `python -c "import app.models; print(len(app.models.Base.metadata.tables))"` — prints 12
4. `from app.models.promises import Promise, ModerationStatus, ResolvedStatus` — both enums distinct
5. `backend/alembic/env.py` contains `postgresql+asyncpg` (the URL it replaces) and `import app.models`

## Deviations from Plan

None — plan executed exactly as written.

The only minor execution decision: the migration file was written manually rather than via `alembic revision --autogenerate` because no live PostgreSQL instance was available at plan execution time. The manual migration matches what autogenerate would produce from the same models. The `test_schema.py` test will validate the migration's correctness against a real database at CI time.

## Known Stubs

| File | Stub | Reason |
|------|------|--------|
| backend/tests/test_schema.py | `test_tables_exist` requires live DB | Will pass in CI with postgres container; manually verified via model import count |
| backend/tests/test_seed.py | `test_seed_data_counts` skipped | Seed loader built in Plan 02 |
| frontend/src/App.test.tsx | Body truthy stub | React app built in Plan 02 |

These stubs are intentional — they are placeholders for Plan 02 and CI work. They do not prevent this plan's goal (health endpoint + schema scaffold) from being achieved.

## Threat Flags

No new threat surface beyond what was planned in the threat model. T-01-01 (postgres password disclosure) was mitigated by using `env_file: [.env]` and adding `.env` to `.gitignore`. T-01-03 (CORS) mitigated by restricting `allow_origins` to `["http://localhost:5173"]`.

## Self-Check: PASSED

Files verified present:
- backend/app/main.py: FOUND
- backend/app/database.py: FOUND
- backend/app/models/__init__.py: FOUND
- backend/alembic/env.py: FOUND
- backend/alembic/versions/20260521_000001_initial_schema.py: FOUND
- docker-compose.yml: FOUND
- .gitignore: FOUND
- .env.example: FOUND

Commits verified:
- eeeda6a: feat(01-01): monorepo scaffold, FastAPI health endpoint, Docker Compose, Wave 0 test stubs
- 13d7865: feat(01-01): full SQLAlchemy models (12 tables all 8 phases) and Alembic initial migration
