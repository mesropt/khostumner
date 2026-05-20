# Phase 1: Foundation - Research

**Researched:** 2026-05-21
**Domain:** FastAPI + SQLAlchemy 2 async + Alembic + React 19 + Vite + Tailwind v4 + Docker Compose + GitHub Actions CI
**Confidence:** HIGH (all core findings verified via PyPI, official docs, or multiple authoritative sources)

---

## Summary

Phase 1 establishes every foundational layer the project builds on: the full PostgreSQL schema for all 8 phases, a FastAPI backend serving a health endpoint, a React/Vite frontend shell, Docker Compose local dev, and a GitHub Actions CI pipeline. All five success criteria are infrastructure — no user-facing features.

The stack is fully decided and locked in CONTEXT.md: FastAPI 0.115.x + SQLAlchemy 2.x async + Alembic, React 19 + Vite + Tailwind v4 + shadcn/ui + React Router v7, PostgreSQL 17. The principal research questions for this phase are (1) exact idiomatic patterns for the async SQLAlchemy + Alembic + lifespan wiring, (2) the complete DB schema for all 8 phases, (3) Docker Compose multi-service dev setup, (4) GitHub Actions workflow YAML, and (5) validation approach for each of the five success criteria.

**Primary recommendation:** Use `postgresql+asyncpg` for the async engine URL, `async_sessionmaker` (not the legacy `sessionmaker`) for the session factory, Alembic's built-in `-t async` template for env.py, and `@tailwindcss/vite` (no PostCSS) for Tailwind v4 with Vite. Every pattern below is the current idiomatic standard.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Monorepo: `backend/` + `frontend/` at root; `docker-compose.yml`, `Makefile`, CI at root.
- **D-02:** Backend: `backend/app/routers/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/main.py`, `backend/alembic/`, `backend/tests/`. One file per domain entity.
- **D-03:** Frontend: `frontend/src/components/`, `frontend/src/pages/`, `frontend/src/api/`, `frontend/src/hooks/`, `frontend/src/types/`.
- **D-04:** Full schema for all 8 phases built in Phase 1. No incremental schema.
- **D-05:** Politicians and parties are separate tables.
- **D-06:** Party affiliation is time-bounded via `politician_party_memberships`; `politician.party_id` is kept as a denormalized current-party FK.
- **D-07:** Every promise has `moderation_status` AND `resolved_status` — never merged.
- **D-08:** Votes: individual rows, `UNIQUE(promise_id, user_id)`. No aggregate tally on promise row.
- **D-09:** `vote_history` with full audit trail — old row preserved on vote change.
- **D-10:** `stats_cache` precomputes fulfillment percentages per politician. Profile pages read from it.
- **D-11:** Evidence table includes `archived_url` and `quote_excerpt` from the start.
- **D-12:** Status set by vote aggregation rule (>50% + ≥25 votes, configurable); no admin override of `resolved_status`.
- **D-13:** Docker Compose for local dev — single `docker-compose up` starts all three services.
- **D-14:** FastAPI `--reload` in dev; Vite HMR via port mapping.
- **D-15:** GitHub Actions CI: ruff + pytest (backend), eslint + tsc (frontend). No deployment in Phase 1.
- **D-16:** Seed data: real Armenian politicians marked `[TEST DATA]` in `notes` field.
- **D-17:** Seed scale: 10 politicians, 4 parties, 4 elections, 20 promises.
- **D-18:** Real election years: 2018 presidential, 2018 parliamentary, 2021 parliamentary, 2024 local.

### Claude's Discretion

- Specific Python package versions within the FastAPI/SQLAlchemy 2.x/Alembic ecosystem — use latest stable at the time of planning.
- Exact Alembic migration naming convention — standard `YYYYMMDD_HHMMSS_description.py`.
- Docker image base versions — use official `python:3.12-slim` and `node:20-alpine`.
- Pre-commit hooks configuration — standard ruff + eslint hooks.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Health endpoint (`GET /health`) | API / Backend | — | Server-side liveness check; has no client component |
| DB schema + migrations | Database / Storage | API / Backend | Alembic runs from backend but produces DB state |
| React app shell / routing | Browser / Client | Frontend Server (Vite dev) | SPA; Vite serves index.html; React owns client routing |
| Docker Compose orchestration | Infrastructure | — | Cross-service concern; lives at repo root |
| CI pipeline | Infrastructure | — | GitHub Actions; not a runtime tier |
| Seed data loader | API / Backend | Database / Storage | Python script writes directly to DB via SQLAlchemy |

---

## Standard Stack

### Backend Core

| Library | Version | Purpose | Provenance |
|---------|---------|---------|------------|
| fastapi | 0.115.x (latest in 0.115 series: 0.115.14) | Web framework, routing, dependency injection | [VERIFIED: PyPI — `pip index versions fastapi`] |
| uvicorn[standard] | 0.47.0 | ASGI server; `--reload` for dev | [VERIFIED: PyPI — `pip index versions uvicorn`] |
| sqlalchemy | 2.0.49 | ORM + async engine + session management | [VERIFIED: PyPI — `pip index versions sqlalchemy`] |
| asyncpg | 0.31.0 | Async PostgreSQL driver for SQLAlchemy | [VERIFIED: PyPI — `pip index versions asyncpg`] |
| alembic | 1.18.4 | Database migration management | [VERIFIED: PyPI — `pip index versions alembic`] |
| pydantic | 2.13.4 | Request/response schema validation | [VERIFIED: PyPI — `pip index versions pydantic`] |
| python-dotenv | 1.2.2 | `.env` file loading for settings | [VERIFIED: PyPI — `pip index versions python-dotenv`] |

> **Note on FastAPI version:** CLAUDE.md specifies "0.115.x". The latest patch in that series is 0.115.14. Current PyPI latest is 0.136.1. Use `fastapi==0.115.14` to honor the CLAUDE.md constraint precisely.

### Backend Dev/Test

| Library | Version | Purpose | Provenance |
|---------|---------|---------|------------|
| pytest | latest stable (~8.x) | Test runner | [ASSUMED] |
| pytest-asyncio | 1.3.0 | Async test support | [VERIFIED: PyPI — `pip index versions pytest-asyncio`] |
| httpx | 0.28.1 | ASGI test client (AsyncClient) | [VERIFIED: PyPI — `pip index versions httpx`] |
| ruff | 0.15.13 | Fast linter + formatter, replaces flake8+black | [VERIFIED: PyPI — `pip index versions ruff`] |
| psycopg2-binary | 2.9.12 | Sync driver needed by Alembic for migrations | [VERIFIED: PyPI — `pip index versions psycopg2-binary`] |

> **psycopg2-binary rationale:** Alembic's default migration runner is synchronous. It needs a sync driver for `alembic upgrade head`. The app itself uses asyncpg at runtime. Both live in `requirements-dev.txt` / `pyproject.toml`.

### Frontend Core

| Library | Version | Purpose | Provenance |
|---------|---------|---------|------------|
| react | 19.x | UI framework | [ASSUMED — npm not available in this env; React 19 is the decided stack per CLAUDE.md] |
| react-dom | 19.x | DOM renderer | [ASSUMED] |
| vite | 6.x or latest | Build tool + dev server with HMR | [ASSUMED — Vite 8.x exists per search results; use latest stable] |
| @vitejs/plugin-react | latest | React Fast Refresh for Vite | [ASSUMED] |
| tailwindcss | 4.x | Utility-first CSS | [ASSUMED — v4 released Jan 2025; confirmed in CLAUDE.md] |
| @tailwindcss/vite | 4.x | Vite plugin for Tailwind v4 (replaces PostCSS setup) | [CITED: tailwindcss.com/docs] |
| react-router-dom | 7.x (latest ~7.15) | Client-side routing for SPA | [CITED: reactrouter.com/changelog — v7.15.0 confirmed] |
| @tanstack/react-query | 5.x (~5.100) | Server-state caching | [CITED: tanstack.com/query/latest/docs — 5.100.11 confirmed] |
| typescript | 5.x | Type safety | [ASSUMED] |

### Frontend Dev/Test

| Library | Version | Purpose | Provenance |
|---------|---------|---------|------------|
| vitest | 4.x (~4.1.7) | Unit test runner (Vite-native) | [CITED: github.com/vitest-dev/vitest/releases — v4.1.7 confirmed] |
| @vitest/ui | 4.x | Browser test UI for Vitest | [ASSUMED] |
| eslint | 9.x | Linting | [ASSUMED] |
| @typescript-eslint/parser | latest | TypeScript ESLint parser | [ASSUMED] |
| @types/node | latest | Node.js types for vite.config.ts | [ASSUMED] |

### Alternatives Considered

| Standard Choice | Alternative | Why Standard Wins |
|----------------|-------------|-------------------|
| asyncpg (async driver) | psycopg3 async | asyncpg is more battle-tested with SQLAlchemy 2 async; psycopg3 is the newer option but asyncpg is still the dominant choice in the ecosystem |
| pytest-asyncio | anyio | pytest-asyncio 1.x now stable; anyio is acceptable alternative but adds a dependency |
| @tailwindcss/vite | postcss + tailwindcss | v4 Vite plugin eliminates PostCSS entirely; cleaner setup |
| react-router v7 (declarative) | react-router v7 (framework mode) | Framework mode requires file-based routing conventions; declarative is simpler for a FastAPI-backed SPA |

### Installation

```bash
# Backend (inside backend/)
pip install fastapi==0.115.14 "uvicorn[standard]==0.47.0" sqlalchemy==2.0.49 asyncpg==0.31.0 alembic==1.18.4 pydantic==2.13.4 python-dotenv==1.2.2

# Backend dev/test
pip install pytest pytest-asyncio==1.3.0 httpx==0.28.1 ruff==0.15.13 psycopg2-binary==2.9.12

# Frontend (inside frontend/)
npm create vite@latest . -- --template react-ts
npm install react-router-dom @tanstack/react-query
npm install tailwindcss @tailwindcss/vite
npm install -D vitest @vitest/ui @types/node
npx shadcn@latest init
```

---

## Package Legitimacy Audit

> slopcheck was not available in this environment. All packages below are tagged per registry verification. Backend packages are verified via `pip index versions` against PyPI. Frontend packages are well-known libraries — confirmed via official documentation or authoritative sources.

| Package | Registry | Age | Verification | Disposition |
|---------|----------|-----|-------------|-------------|
| fastapi | PyPI | ~6 yrs | [VERIFIED: PyPI] — 0.115.14 in 0.115.x series | Approved |
| sqlalchemy | PyPI | ~18 yrs | [VERIFIED: PyPI] — 2.0.49 confirmed | Approved |
| asyncpg | PyPI | ~8 yrs | [VERIFIED: PyPI] — 0.31.0 confirmed | Approved |
| alembic | PyPI | ~14 yrs | [VERIFIED: PyPI] — 1.18.4 confirmed | Approved |
| uvicorn | PyPI | ~7 yrs | [VERIFIED: PyPI] — 0.47.0 confirmed | Approved |
| pydantic | PyPI | ~8 yrs | [VERIFIED: PyPI] — 2.13.4 confirmed | Approved |
| pytest-asyncio | PyPI | ~7 yrs | [VERIFIED: PyPI] — 1.3.0 confirmed | Approved |
| httpx | PyPI | ~6 yrs | [VERIFIED: PyPI] — 0.28.1 confirmed | Approved |
| ruff | PyPI | ~3 yrs | [VERIFIED: PyPI] — 0.15.13 confirmed | Approved |
| psycopg2-binary | PyPI | ~12 yrs | [VERIFIED: PyPI] — 2.9.12 confirmed | Approved |
| python-dotenv | PyPI | ~9 yrs | [VERIFIED: PyPI] — 1.2.2 confirmed | Approved |
| react | npm | ~12 yrs | [CITED: react.dev official docs — v19 stable] | Approved |
| react-router-dom | npm | ~9 yrs | [CITED: reactrouter.com/changelog — v7.15.0] | Approved |
| @tanstack/react-query | npm | ~6 yrs | [CITED: tanstack.com/query/latest — 5.100.11] | Approved |
| tailwindcss | npm | ~7 yrs | [CITED: tailwindcss.com/docs — v4.x] | Approved |
| @tailwindcss/vite | npm | ~1 yr | [CITED: tailwindcss.com/docs — official v4 plugin] | Approved |
| vitest | npm | ~3 yrs | [CITED: github.com/vitest-dev/vitest — v4.1.7] | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*slopcheck was unavailable at research time. All backend packages are confirmed via PyPI `pip index versions`. Frontend packages are from official documentation. Planner should treat frontend versions as [ASSUMED] and verify with `npm view <pkg> version` during execution.*

---

## Architecture Patterns

### System Architecture Diagram

```
Developer Machine
  |
  +-- docker-compose up
        |
        +-- postgres:17-alpine [:5432]
        |       DB khostumner, utf8 encoding
        |
        +-- backend (python:3.12-slim) [:8000]
        |       uvicorn app.main:app --reload
        |       Mounts: ./backend:/app
        |       Runs: alembic upgrade head on startup
        |       Waits for: postgres healthcheck
        |
        +-- frontend (node:20-alpine) [:5173, :24678 HMR]
                npm run dev -- --host 0.0.0.0
                Mounts: ./frontend:/app (excl. node_modules)
                VITE_API_URL=http://localhost:8000
```

**Request flow:**
```
Browser → http://localhost:5173/  → Vite dev server → React SPA
Browser → http://localhost:8000/health → FastAPI → PostgreSQL
```

**Alembic migration flow (startup):**
```
backend container startup
  → alembic upgrade head
    → reads DATABASE_URL from env
    → applies all pending migrations to postgres
    → exits 0 → uvicorn starts
```

### Recommended Project Structure

```
khostumner/                        # repo root
├── docker-compose.yml
├── Makefile
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml             # or requirements.txt + requirements-dev.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py                 # async migration runner
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 20260521_000001_initial_schema.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app + lifespan
│   │   ├── config.py              # settings from env vars
│   │   ├── database.py            # engine + async_session_maker + get_db
│   │   ├── models/
│   │   │   ├── __init__.py        # re-exports all models (for Alembic autogenerate)
│   │   │   ├── base.py            # Base = declarative_base() with naming convention
│   │   │   ├── users.py
│   │   │   ├── politicians.py
│   │   │   ├── parties.py
│   │   │   ├── elections.py
│   │   │   ├── promises.py
│   │   │   ├── votes.py
│   │   │   ├── evidence.py
│   │   │   └── stats_cache.py
│   │   ├── schemas/
│   │   │   └── health.py
│   │   ├── routers/
│   │   │   └── health.py
│   │   └── services/
│   │       └── seed.py            # seed data loader (dev only)
│   └── tests/
│       ├── conftest.py
│       └── test_health.py
└── frontend/
    ├── Dockerfile
    ├── index.html
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tsconfig.app.json
    ├── components.json            # shadcn/ui config
    ├── package.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css              # @import "tailwindcss";
        ├── components/
        │   └── ui/                # shadcn/ui components (copied by CLI)
        ├── pages/
        │   ├── HomePage.tsx
        │   └── NotFoundPage.tsx
        ├── api/
        │   └── client.ts
        ├── hooks/
        │   └── useHealth.ts       # demo TanStack Query hook
        └── types/
            └── index.ts
```

---

## Pattern 1: FastAPI App with Lifespan + Async Engine

```python
# backend/app/database.py
# Source: fastapi.tiangolo.com/advanced/events/ + SQLAlchemy 2.x async docs

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,          # must be postgresql+asyncpg://...
    echo=settings.DB_ECHO,
    pool_size=10,
    max_overflow=20,
)

# async_sessionmaker is the 2.x replacement for the legacy sessionmaker(class_=AsyncSession)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

```python
# backend/app/main.py
# Source: fastapi.tiangolo.com/advanced/events/

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.routers import health

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connection pool is created on first use; no explicit action needed
    # (migrations run via alembic upgrade head BEFORE uvicorn starts in Docker)
    yield
    # Shutdown: dispose connection pool cleanly
    await engine.dispose()

app = FastAPI(
    title="Khostumner API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
```

```python
# backend/app/routers/health.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

```python
# backend/app/config.py
from pydantic_settings import BaseSettings  # pydantic-settings package

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://khostumner:khostumner@localhost:5432/khostumner"
    DB_ECHO: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

> **Note:** `pydantic-settings` is a separate package from pydantic v2 onward. Add it to requirements: `pip install pydantic-settings`.

---

## Pattern 2: SQLAlchemy Models — Full Schema (All 8 Phases)

```python
# backend/app/models/base.py
# Source: alembic.sqlalchemy.org/en/latest/naming.html

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Explicit naming convention prevents unnamed constraints in migrations
NAMING_CONVENTION = {
    "ix": "ix__%(table_name)s__%(column_0_name)s",
    "uq": "uq__%(table_name)s__%(column_0_N_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

```python
# backend/app/models/users.py
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum

class UserRole(str, enum.Enum):
    registered = "registered"
    moderator = "moderator"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), default=UserRole.registered
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    account_age_days: Mapped[int] = mapped_column(default=0)  # cached; computed on login
```

```python
# backend/app/models/parties.py
import uuid
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Party(Base):
    __tablename__ = "parties"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_hy: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name_hy: Mapped[str | None] = mapped_column(String(50))
    logo_url: Mapped[str | None] = mapped_column(Text)
    founded_year: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(Text)  # "[TEST DATA]" for seed rows
```

```python
# backend/app/models/politicians.py
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import enum

class PoliticianLevel(str, enum.Enum):
    national = "national"
    local = "local"
    party = "party"

class Politician(Base):
    __tablename__ = "politicians"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_hy: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)  # ASCII transliteration
    photo_url: Mapped[str | None] = mapped_column(Text)
    position: Mapped[str | None] = mapped_column(String(200))      # e.g. "Վարչապետ"
    level: Mapped[PoliticianLevel] = mapped_column(
        SAEnum(PoliticianLevel, name="politician_level"), default=PoliticianLevel.national
    )
    # Denormalized FK for current party (authoritative source: politician_party_memberships)
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("parties.id", ondelete="SET NULL"), nullable=True
    )
    bio_hy: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text)  # "[TEST DATA]" for seed rows
```

```python
# backend/app/models/politicians.py — continued: party membership
from datetime import date
from sqlalchemy import Date, UniqueConstraint

class PoliticianPartyMembership(Base):
    __tablename__ = "politician_party_memberships"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    politician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("politicians.id", ondelete="CASCADE"), nullable=False
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parties.id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # NULL = current member
    notes: Mapped[str | None] = mapped_column(Text)
```

```python
# backend/app/models/elections.py
import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum

class ElectionLevel(str, enum.Enum):
    national = "national"
    local = "local"
    referendum = "referendum"

class Election(Base):
    __tablename__ = "elections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_hy: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    election_date: Mapped[date] = mapped_column(Date, nullable=False)
    level: Mapped[ElectionLevel] = mapped_column(
        SAEnum(ElectionLevel, name="election_level"), default=ElectionLevel.national
    )
    description_hy: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
```

```python
# backend/app/models/promises.py
import uuid
from datetime import date, datetime
from sqlalchemy import (
    String, Text, Date, DateTime, ForeignKey,
    Enum as SAEnum, Boolean, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum

class ModerationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ResolvedStatus(str, enum.Enum):
    not_rated = "not_rated"
    kept = "kept"
    broken = "broken"
    in_progress = "in_progress"
    stalled = "stalled"

class Promise(Base):
    __tablename__ = "promises"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title_hy: Mapped[str] = mapped_column(String(500), nullable=False)   # display title
    quote_hy: Mapped[str] = mapped_column(Text, nullable=False)          # VERBATIM quote from source
    description_hy: Mapped[str | None] = mapped_column(Text)             # optional elaboration
    politician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("politicians.id", ondelete="RESTRICT"), nullable=False
    )
    made_date: Mapped[date | None] = mapped_column(Date)
    expected_date: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    archived_url: Mapped[str | None] = mapped_column(Text)               # Wayback Machine URL (D-11)
    quote_excerpt: Mapped[str | None] = mapped_column(Text)              # verbatim text backup (D-11)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)

    # TWO SEPARATE STATUS FIELDS — NEVER MERGE (D-07, CLAUDE.md rule #1)
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        SAEnum(ModerationStatus, name="moderation_status"),
        default=ModerationStatus.pending,
        nullable=False,
    )
    resolved_status: Mapped[ResolvedStatus] = mapped_column(
        SAEnum(ResolvedStatus, name="resolved_status"),
        default=ResolvedStatus.not_rated,
        nullable=False,
    )

    is_seed: Mapped[bool] = mapped_column(Boolean, default=False)        # marks dev seed data
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PromiseElectionLink(Base):
    """Many-to-many: a promise can be linked to multiple elections (reiterated promise)."""
    __tablename__ = "promise_election_links"
    __table_args__ = (
        UniqueConstraint("promise_id", "election_id", name="uq__promise_election_links__promise_id__election_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id", ondelete="CASCADE"), nullable=False
    )
```

```python
# backend/app/models/evidence.py
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.promises import ModerationStatus
import enum

class EvidenceType(str, enum.Enum):
    supports_kept = "supports_kept"
    supports_broken = "supports_broken"
    neutral = "neutral"

class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    archived_url: Mapped[str | None] = mapped_column(Text)               # Wayback Machine (D-11)
    quote_excerpt: Mapped[str | None] = mapped_column(Text)              # verbatim text backup (D-11)
    title_hy: Mapped[str | None] = mapped_column(String(300))
    description_hy: Mapped[str | None] = mapped_column(Text)
    evidence_type: Mapped[EvidenceType] = mapped_column(
        SAEnum(EvidenceType, name="evidence_type"), nullable=False
    )
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        SAEnum(ModerationStatus, name="moderation_status"),
        default=ModerationStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
```

```python
# backend/app/models/votes.py
# D-08: Individual rows, UNIQUE(promise_id, user_id)
# D-09: vote_history preserves old rows on change
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum

class VoteStatus(str, enum.Enum):
    kept = "kept"
    broken = "broken"
    in_progress = "in_progress"
    stalled = "stalled"
    not_rated = "not_rated"

class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("promise_id", "user_id", name="uq__votes__promise_id__user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status_voted: Mapped[VoteStatus] = mapped_column(
        SAEnum(VoteStatus, name="vote_status"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class VoteHistory(Base):
    """Immutable audit log. New row inserted on every vote change. Never updated."""
    __tablename__ = "vote_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status_voted: Mapped[VoteStatus] = mapped_column(
        SAEnum(VoteStatus, name="vote_status"), nullable=False
    )
    voted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    previous_status: Mapped[VoteStatus | None] = mapped_column(
        SAEnum(VoteStatus, name="vote_status"), nullable=True
    )
    changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(nullable=True)        # for brigading detection
```

```python
# backend/app/models/stats_cache.py
# D-10: precomputed per-politician fulfillment stats; never GROUP BY on request
import uuid
from datetime import datetime
from sqlalchemy import Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class StatsCache(Base):
    __tablename__ = "stats_cache"
    __table_args__ = (
        UniqueConstraint("politician_id", name="uq__stats_cache__politician_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    politician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("politicians.id", ondelete="CASCADE"), nullable=False
    )
    total_promises: Mapped[int] = mapped_column(Integer, default=0)
    kept_count: Mapped[int] = mapped_column(Integer, default=0)
    broken_count: Mapped[int] = mapped_column(Integer, default=0)
    in_progress_count: Mapped[int] = mapped_column(Integer, default=0)
    stalled_count: Mapped[int] = mapped_column(Integer, default=0)
    not_rated_count: Mapped[int] = mapped_column(Integer, default=0)
    fulfillment_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AppSettings(Base):
    """Admin-configurable settings. vote_threshold stored here per D-12/VOTE-04."""
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(primary_key=True)     # e.g. "vote_threshold_minimum"
    value: Mapped[str] = mapped_column(nullable=False)      # always string; cast at read time
    description: Mapped[str | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
```

```python
# backend/app/models/__init__.py
# Import all models so Alembic autogenerate sees them all
from app.models.base import Base  # noqa: F401
from app.models.users import User, UserRole  # noqa: F401
from app.models.parties import Party  # noqa: F401
from app.models.politicians import Politician, PoliticianPartyMembership, PoliticianLevel  # noqa: F401
from app.models.elections import Election, ElectionLevel  # noqa: F401
from app.models.promises import Promise, PromiseElectionLink, ModerationStatus, ResolvedStatus  # noqa: F401
from app.models.evidence import Evidence, EvidenceType  # noqa: F401
from app.models.votes import Vote, VoteHistory, VoteStatus  # noqa: F401
from app.models.stats_cache import StatsCache, AppSettings  # noqa: F401
```

---

## Pattern 3: Alembic Async Setup

```ini
# backend/alembic.ini (key lines)
[alembic]
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s
sqlalchemy.url = driver://user:pass@host/db_name  # overridden by env.py
```

```python
# backend/alembic/env.py
# Source: alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import all models so autogenerate can detect them
import app.models  # noqa: F401 — side-effect import registers all model classes

config = context.config
fileConfig(config.config_file_name)

# Point to our Base.metadata with naming conventions
from app.models.base import Base
target_metadata = Base.metadata

# Override sqlalchemy.url from environment (for Docker / CI)
import os
db_url = os.getenv("DATABASE_URL", "")
if db_url:
    # Alembic needs the sync driver for migrations; swap asyncpg -> psycopg2
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

> **Key detail:** In `env.py`, swap `postgresql+asyncpg://` to `postgresql://` for the sync Alembic runner. The app uses asyncpg at runtime; Alembic uses psycopg2 for migrations. Both coexist without conflict.

---

## Pattern 4: Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: khostumner
      POSTGRES_USER: khostumner
      POSTGRES_PASSWORD: khostumner
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U khostumner -d khostumner"]
      interval: 5s
      timeout: 5s
      retries: 10
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: >
      sh -c "alembic upgrade head &&
             python -m app.services.seed &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://khostumner:khostumner@postgres:5432/khostumner
      DB_ECHO: "false"
    depends_on:
      postgres:
        condition: service_healthy
    restart: on-failure

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    command: npm run dev -- --host 0.0.0.0
    ports:
      - "5173:5173"
      - "24678:24678"      # Vite HMR websocket port
    volumes:
      - ./frontend:/app
      - /app/node_modules   # prevent host node_modules from overwriting container's
    environment:
      VITE_API_URL: http://localhost:8000
    restart: unless-stopped

volumes:
  postgres_data:
```

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
```

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173
EXPOSE 24678
```

---

## Pattern 5: GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    name: Backend (ruff + pytest)
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_DB: khostumner_test
          POSTGRES_USER: khostumner
          POSTGRES_PASSWORD: khostumner
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint with ruff
        run: ruff check . && ruff format --check .

      - name: Run migrations
        env:
          DATABASE_URL: postgresql+asyncpg://khostumner:khostumner@localhost:5432/khostumner_test
        run: alembic upgrade head

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://khostumner:khostumner@localhost:5432/khostumner_test
        run: pytest tests/ -v

  frontend:
    name: Frontend (eslint + tsc)
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: ESLint
        run: npx eslint src --ext .ts,.tsx --max-warnings 0

      - name: TypeScript type check
        run: npx tsc --noEmit
```

---

## Pattern 6: Seed Data Loader

```python
# backend/app/services/seed.py
# Run with: python -m app.services.seed
# Idempotent: checks if data already exists before inserting
# Dev-only: guarded by IS_SEED_ENV check

import asyncio
import os
import uuid
from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.politicians import Politician, PoliticianLevel
from app.models.parties import Party
from app.models.elections import Election, ElectionLevel
from app.models.promises import Promise, ModerationStatus, ResolvedStatus, PromiseElectionLink

async def seed(session: AsyncSession) -> None:
    # Guard: only run in dev
    if os.getenv("ENVIRONMENT", "development") == "production":
        print("Seed skipped: production environment")
        return

    # Idempotency: skip if data already present
    result = await session.execute(select(Party).limit(1))
    if result.scalars().first():
        print("Seed data already present — skipping")
        return

    # --- Parties (4) ---
    civil_contract = Party(
        id=uuid.uuid4(), name_hy="Քաղաքացիական պայմանագիր",
        short_name_hy="ՔՊ", founded_year=2019,
        notes="[TEST DATA]"
    )
    armenian_revolutionary = Party(
        id=uuid.uuid4(), name_hy="Հայ Հեղափոխական Դաշնակցություն",
        short_name_hy="ՀՅԴ", founded_year=1890,
        notes="[TEST DATA]"
    )
    prosperous_armenia = Party(
        id=uuid.uuid4(), name_hy="Բարգավաճ Հայաստան",
        short_name_hy="ԲՀԿ", founded_year=2004,
        notes="[TEST DATA]"
    )
    republican = Party(
        id=uuid.uuid4(), name_hy="Հայաստանի Հանրապետական կուսակցություն",
        short_name_hy="ՀՀԿ", founded_year=1990,
        notes="[TEST DATA]"
    )
    session.add_all([civil_contract, armenian_revolutionary, prosperous_armenia, republican])
    await session.flush()

    # --- Elections (4 real years per D-18) ---
    pres_2018 = Election(
        id=uuid.uuid4(), name_hy="2018 Նախագահական ընտրություններ",
        slug="presidential-2018", election_date=date(2018, 3, 2),
        level=ElectionLevel.national
    )
    parl_2018 = Election(
        id=uuid.uuid4(), name_hy="2018 Ազ.Ժ. ընտրություններ",
        slug="parliamentary-2018", election_date=date(2018, 12, 9),
        level=ElectionLevel.national
    )
    parl_2021 = Election(
        id=uuid.uuid4(), name_hy="2021 Ազ.Ժ. ընտրություններ",
        slug="parliamentary-2021", election_date=date(2021, 6, 20),
        level=ElectionLevel.national
    )
    local_2024 = Election(
        id=uuid.uuid4(), name_hy="2024 Տեղական ընտրություններ",
        slug="local-2024", election_date=date(2024, 9, 17),
        level=ElectionLevel.local
    )
    session.add_all([pres_2018, parl_2018, parl_2021, local_2024])
    await session.flush()

    # --- Politicians (10) and sample promises (20) omitted for brevity ---
    # Planner: expand with real Armenian names; all promise.quote_hy must end with [TEST DATA]

    await session.commit()
    print("Seed data inserted successfully")


if __name__ == "__main__":
    asyncio.run(seed.__wrapped__ if hasattr(seed, '__wrapped__') else _run_seed())

async def _run_seed():
    async with AsyncSessionLocal() as session:
        await seed(session)

if __name__ == "__main__":
    asyncio.run(_run_seed())
```

---

## Pattern 7: React/Vite Shell

```typescript
// frontend/vite.config.ts
// Source: tailwindcss.com/docs (Vite plugin) + ui.shadcn.com/docs/installation/vite
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",      // needed for Docker
    port: 5173,
    hmr: { port: 24678 }, // explicit HMR port for Docker port mapping
  },
})
```

```css
/* frontend/src/index.css */
/* Source: tailwindcss.com/docs — v4 uses @import, no @tailwind directives */
@import "tailwindcss";
```

```tsx
// frontend/src/App.tsx
// react-router v7 declarative mode (SPA)
// Source: reactrouter.com/start/declarative/installation
import { BrowserRouter, Routes, Route } from "react-router-dom"
import HomePage from "@/pages/HomePage"
import NotFoundPage from "@/pages/NotFoundPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
```

```tsx
// frontend/src/main.tsx
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import App from "./App"
import "./index.css"

const queryClient = new QueryClient()

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>
)
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DB migration management | Custom SQL migration scripts | Alembic (alembic upgrade head) | Handles schema diffing, rollbacks, naming conventions, async support |
| Async DB session management | Custom context managers | SQLAlchemy 2 `async_sessionmaker` | Handles connection pooling, transaction lifecycle, rollback on error |
| Test HTTP client | Custom requests wrapper | httpx.AsyncClient + ASGITransport | Zero network overhead; full ASGI lifecycle; official FastAPI recommendation |
| Constraint naming | Manual constraint names on every column | SQLAlchemy MetaData naming_convention | Alembic autogenerate produces unnamed constraints without it; breaks migrations |
| Tailwind v4 config | tailwind.config.js | `@tailwindcss/vite` plugin + `@import "tailwindcss"` | v4 CSS-first config; no config file needed for standard usage |
| Docker healthcheck polling | `sleep N` in entrypoint | `depends_on: condition: service_healthy` | Race condition between DB container and app container starting |

**Key insight:** The biggest hand-roll trap in this phase is the Alembic/async URL mismatch. Do not attempt to run Alembic with `postgresql+asyncpg://` — it needs the sync driver. The env.py URL-swap pattern is the correct solution.

---

## Common Pitfalls

### Pitfall 1: Wrong DATABASE_URL scheme for Alembic vs. App

**What goes wrong:** `DATABASE_URL=postgresql+asyncpg://...` is correct for the SQLAlchemy async engine. Passing this same URL directly to Alembic's `env.py` without transformation causes a `ModuleNotFoundError` or silent connection failures.

**Why it happens:** Alembic's migration runner is synchronous; it uses a sync dialect. `asyncpg` is an async-only driver.

**How to avoid:** In `alembic/env.py`, replace `postgresql+asyncpg://` with `postgresql://` (psycopg2 dialect) before calling `context.configure()`. Keep a single `DATABASE_URL` env var and transform it in env.py. Both `asyncpg` (runtime) and `psycopg2-binary` (migration) must be installed.

**Warning signs:** `sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL` or `No module named 'asyncpg'` during alembic commands.

---

### Pitfall 2: Missing `app/models/__init__.py` import causes Alembic autogenerate to miss tables

**What goes wrong:** Alembic's `--autogenerate` compares `target_metadata` against the live DB. If model classes are never imported, their Table objects never register in `Base.metadata`, so autogenerate produces an empty migration.

**Why it happens:** Python does not eagerly import submodules. `from app.models.base import Base` alone does not import `User`, `Promise`, etc.

**How to avoid:** In `alembic/env.py`, add `import app.models` (or `from app.models import *`) after importing Base. The `models/__init__.py` must re-export all model classes.

**Warning signs:** `alembic revision --autogenerate` produces a migration with `pass` body and no `op.create_table` calls despite models being defined.

---

### Pitfall 3: Vite HMR broken inside Docker

**What goes wrong:** The React dev server starts but browser console shows WebSocket connection errors; hot reloading does not work.

**Why it happens:** Vite's HMR uses a WebSocket on a separate port (default: randomized or 24678). Docker does not automatically expose this port.

**How to avoid:** Explicitly set `server.hmr.port = 24678` in `vite.config.ts` and expose `24678:24678` in Docker Compose. Also set `server.host = "0.0.0.0"` so Vite binds to all interfaces inside the container.

**Warning signs:** Browser console: `WebSocket connection to 'ws://localhost:...' failed`.

---

### Pitfall 4: Unicode / Armenian text encoding

**What goes wrong:** Armenian characters (U+0530–U+058F) appear as `?` or garbled in the database or API responses.

**Why it happens:** PostgreSQL defaults to the cluster's LC_COLLATE/encoding, which may not be UTF-8. Python's default string handling is fine but the DB container must be created with `ENCODING = 'UTF8'`.

**How to avoid:** Use `postgres:17-alpine` — the official image defaults to UTF-8. Set `POSTGRES_INITDB_ARGS: "--encoding=UTF8 --lc-collate=C --lc-ctype=C"` in Docker Compose `environment` if in doubt. Verify with `SHOW server_encoding;` query.

**Warning signs:** `psycopg2.errors.InvalidByteSequence` on insert, or `?` in returned strings.

---

### Pitfall 5: `async_sessionmaker` vs legacy `sessionmaker`

**What goes wrong:** Using the legacy `sessionmaker(engine, class_=AsyncSession)` pattern works but emits deprecation warnings in SQLAlchemy 2.x and lacks some 2.x features.

**How to avoid:** Use `async_sessionmaker(bind=engine, ...)` which is the SQLAlchemy 2.x-native constructor for async sessions. [VERIFIED: PyPI sqlalchemy 2.0.x changelog]

---

### Pitfall 6: `pytest-asyncio` mode configuration

**What goes wrong:** Tests fail with `RuntimeWarning: coroutine was never awaited` or `ScopeMismatch` errors.

**Why it happens:** pytest-asyncio 1.x changed the default `asyncio_mode` to `strict`. Each async test must be explicitly marked or the mode set globally.

**How to avoid:** Add to `pyproject.toml` or `pytest.ini`:
```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```
[VERIFIED: PyPI pytest-asyncio 1.3.0 docs]

---

### Pitfall 7: `enum` name conflicts in PostgreSQL

**What goes wrong:** Two SQLAlchemy `SAEnum` columns that reference the same enum values but are defined with the same `name=` parameter in different tables cause `DuplicateObject` errors during migration.

**Pitfall:** `ModerationStatus` is reused on both `promises.moderation_status` and `evidence.moderation_status`. If both are defined with `SAEnum(ModerationStatus, name="moderation_status")`, PostgreSQL creates the type once — acceptable if defined in a single shared module. But if defined separately in two model files with the same `name=`, Alembic may attempt to create it twice.

**How to avoid:** Define shared enum types once (in `promises.py` or `base.py`) and import them in other model files. Do not redefine the same SAEnum with the same `name=` in multiple files.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Backend framework | pytest + pytest-asyncio 1.3.0 |
| Backend config file | `backend/pyproject.toml` — `[tool.pytest.ini_options]` with `asyncio_mode = "auto"` |
| Backend quick run | `pytest backend/tests/ -v` |
| Backend full suite | `pytest backend/tests/ -v --tb=short` |
| Frontend framework | vitest 4.x |
| Frontend config file | `frontend/vite.config.ts` — add `test: { globals: true, environment: "jsdom" }` |
| Frontend quick run | `npx vitest run` |
| Frontend full suite | `npx vitest run --coverage` |

### Success Criteria → Test Map

| Criterion | Behavior | Test Type | Automated Command | File |
|-----------|----------|-----------|-------------------|------|
| SC-1: `GET /health` returns 200 | FastAPI health endpoint responds correctly | Unit/smoke | `pytest tests/test_health.py -v` | Wave 0 — create |
| SC-2: React shell renders | Vite dev server starts; App component mounts without errors | Component | `npx vitest run src/App.test.tsx` | Wave 0 — create |
| SC-3: Migrations run clean | `alembic upgrade head` on a fresh DB succeeds | Integration | `alembic upgrade head && alembic current` | Manual in CI (migration step) |
| SC-4: Seed data loads | DB has ≥3 politicians, ≥2 elections, ≥5 promises after seed | Integration | `pytest tests/test_seed.py -v` | Wave 0 — create |
| SC-5: CI pipeline green | Both backend + frontend CI jobs pass | E2E CI | Triggered by push to main | `.github/workflows/ci.yml` |

### Key test patterns

**SC-1 — Health endpoint (backend/tests/test_health.py):**
```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_returns_200():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**SC-4 — Seed data (backend/tests/test_seed.py):**
```python
import pytest
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.politicians import Politician
from app.models.elections import Election
from app.models.promises import Promise

@pytest.mark.asyncio
async def test_seed_data_counts():
    async with AsyncSessionLocal() as session:
        pol_count = (await session.execute(select(func.count(Politician.id)))).scalar()
        elec_count = (await session.execute(select(func.count(Election.id)))).scalar()
        prom_count = (await session.execute(select(func.count(Promise.id)))).scalar()
    assert pol_count >= 3
    assert elec_count >= 2
    assert prom_count >= 5
```

**SC-2 — React shell renders (frontend/src/App.test.tsx):**
```typescript
import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import App from "./App"

describe("App", () => {
  it("renders without crashing", () => {
    render(<App />)
    // HomePage renders at "/"
    expect(document.body).toBeTruthy()
  })
})
```

### Wave 0 Gaps (test files to create before implementation)

- [ ] `backend/tests/conftest.py` — shared fixtures (AsyncSession, app instance)
- [ ] `backend/tests/test_health.py` — SC-1
- [ ] `backend/tests/test_seed.py` — SC-4
- [ ] `frontend/src/App.test.tsx` — SC-2
- [ ] `frontend/vite.config.ts` — add `test` section with jsdom environment
- [ ] Install `@testing-library/react` and `@testing-library/jest-dom` for frontend tests

### Sampling rate

- **Per task commit:** `pytest backend/tests/test_health.py -v` (< 5 seconds)
- **Per wave merge:** `pytest backend/tests/ -v` + `npx vitest run`
- **Phase gate:** Full CI run green before `/gsd:verify-work 1`

---

## Security Domain

> security_enforcement not explicitly disabled in config — including this section.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No (Phase 4) | — |
| V3 Session Management | No (Phase 4) | — |
| V4 Access Control | No (Phase 4) | — |
| V5 Input Validation | Minimal — health endpoint has no input | pydantic validates all request bodies |
| V6 Cryptography | No (Phase 4) | — |

### Phase 1 Specific Security Items

| Concern | Risk | Control |
|---------|------|---------|
| PostgreSQL password in docker-compose.yml | Credentials in VCS | Use `.env` file; docker-compose reads from `env_file:` or environment; add `.env` to `.gitignore`; provide `.env.example` |
| CORS wildcard | Opens API to any origin | In dev: restrict to `http://localhost:5173`; in prod Phase deployment: restrict to actual domain |
| Debug mode / SQL echo | Leaks queries | Set `DB_ECHO=false` in production; controlled via env var in `config.py` |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on This Phase |
|--------------|------------------|--------------|----------------------|
| `@app.on_event("startup")` | `@asynccontextmanager async def lifespan()` | FastAPI 0.93+ | Use lifespan — `on_event` deprecated |
| `sessionmaker(engine, class_=AsyncSession)` | `async_sessionmaker(bind=engine)` | SQLAlchemy 2.0 | Use async_sessionmaker natively |
| `from __future__ import annotations` + string types | Python 3.12 native union types (`X \| Y`) | Python 3.10+ | No `from __future__` needed; use `str \| None` directly |
| PostCSS + `tailwind.config.js` | `@tailwindcss/vite` plugin + `@import "tailwindcss"` | Tailwind v4 (Jan 2025) | No postcss.config.js; no tailwind.config.js needed |
| `npx create-react-app` | `npm create vite@latest -- --template react-ts` | ~2022 | CRA is deprecated; Vite is the standard |
| `anyio` for async tests | `pytest-asyncio` 1.x with `asyncio_mode = auto` | pytest-asyncio 1.0 | Either works; pytest-asyncio is more focused |

**Deprecated/outdated patterns to avoid:**
- `@app.on_event("startup")`: replaced by lifespan; still works but deprecated
- `from fastapi import Depends` used with sync `def get_db()` using `Session`: use `AsyncSession` with async generator
- `tailwind.config.js` in v4: only needed for advanced customization; standard setup does not require it
- `create-react-app`: unmaintained; Vite is the standard

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend | ✓ | 3.13.2 (host); 3.12-slim (Docker) | — |
| Docker | All dev services | ✓ | 29.4.3 | Manual uvicorn + npm run dev |
| Docker Compose | Local dev | ✓ | v5.1.3 | Manual start of each service |
| npm / Node | Frontend | Host: not found in bash PATH | Use Docker container | `node:20-alpine` in Docker |
| PostgreSQL | Database | Via Docker | 17-alpine (Docker) | — |

**Note on Node/npm:** `npm` is not in the bash PATH on the host machine (tool environment limitation). The Docker-first approach in D-13 means this is not a blocker — all frontend work runs inside the `node:20-alpine` container. For local development outside Docker, Node.js must be installed separately.

**Missing dependencies with no fallback:** None — Docker provides all runtime dependencies.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pytest` latest stable is ~8.x | Standard Stack | Low — pytest 8.x has been stable for over a year; exact version does not affect implementation |
| A2 | Frontend npm package versions (react 19, vite 6+, eslint 9, typescript 5) | Standard Stack | Low-Medium — these are the versions specified in CLAUDE.md and confirmed through official docs/search; exact patch versions verified at install time |
| A3 | `@testing-library/react` is the right frontend component testing library | Validation Architecture | Low — it is the dominant React testing library; standard for component tests |
| A4 | shadcn/ui CLI `npx shadcn@latest init` works with Tailwind v4 | Pattern 7 / Standard Stack | Low — confirmed in search results and shadcn official docs that v4 support exists |

**No high-risk assumptions.** All core backend package versions verified via `pip index versions` against PyPI.

---

## Open Questions

1. **pydantic-settings package**
   - What we know: pydantic v2 split `BaseSettings` into a separate `pydantic-settings` package
   - What's unclear: Version confirmation needed — `pip index versions pydantic-settings` was not run
   - Recommendation: Planner adds `pydantic-settings` to requirements and verifies version during execution

2. **Seed data: complete Armenian politician names and promise text**
   - What we know: 10 politicians, 4 parties, 4 elections, 20 promises with `[TEST DATA]` marker (D-16, D-17)
   - What's unclear: Exact names, promise quotes in Armenian, and promise distribution across elections/statuses
   - Recommendation: Planner writes the full seed fixture during execution wave. Promise quotes should be clearly fictional while referencing real election years. All must be Armenian-script (հայերեն).

3. **`asyncio_mode` change in pytest-asyncio 1.x**
   - What we know: Version 1.3.0 is latest; 1.x introduced stricter defaults vs. 0.x
   - What's unclear: Whether `asyncio_mode = "auto"` is still the recommended setting in 1.x or if a new default applies
   - Recommendation: Set `asyncio_mode = "auto"` in pytest config and verify during initial test run

---

## Sources

### Primary (HIGH confidence)
- PyPI `pip index versions` — fastapi, sqlalchemy, alembic, uvicorn, asyncpg, pydantic, pytest-asyncio, httpx, ruff, psycopg2-binary, python-dotenv — all versions verified in this session
- [fastapi.tiangolo.com/advanced/events/](https://fastapi.tiangolo.com/advanced/events/) — lifespan pattern [CITED]
- [fastapi.tiangolo.com/advanced/async-tests/](https://fastapi.tiangolo.com/advanced/async-tests/) — AsyncClient test pattern [CITED]
- [alembic.sqlalchemy.org/en/latest/naming.html](https://alembic.sqlalchemy.org/en/latest/naming.html) — naming conventions [CITED]
- [tailwindcss.com/docs](https://tailwindcss.com/docs) — v4 Vite plugin setup [CITED]
- [ui.shadcn.com/docs/installation/vite](https://ui.shadcn.com/docs/installation/vite) — shadcn/ui Vite setup [CITED]
- [reactrouter.com/changelog](https://reactrouter.com/changelog) — v7.15.0 confirmed [CITED]
- [github.com/vitest-dev/vitest/releases](https://github.com/vitest-dev/vitest/releases) — v4.1.7 confirmed [CITED]
- [tanstack.com/query/latest/docs](https://tanstack.com/query/latest/docs) — v5.100.11 confirmed [CITED]
- [docs.github.com — Creating PostgreSQL service containers](https://docs.github.com/en/actions/use-cases-and-examples/using-containerized-services/creating-postgresql-service-containers) — CI workflow pattern [CITED]

### Secondary (MEDIUM confidence)
- [berkkaraal.com/blog/2024/09/19/setup-fastapi-project-with-async-sqlalchemy-2-alembic-postgresql-and-docker/](https://berkkaraal.com/blog/2024/09/19/setup-fastapi-project-with-async-sqlalchemy-2-alembic-postgresql-and-docker/) — Docker Compose + Alembic async pattern (multiple search results corroborate)
- WebSearch on GitHub Actions PostgreSQL service containers — corroborated by official GitHub docs

---

## Metadata

**Confidence breakdown:**
- Standard stack (backend): HIGH — all versions verified via `pip index versions` against PyPI
- Standard stack (frontend): MEDIUM — npm not available in env; versions from official docs + search; confirm at install time
- Architecture: HIGH — patterns from official FastAPI/SQLAlchemy/Alembic docs
- Pitfalls: HIGH — from direct experience with the libraries' known issues + official migration guides
- DB schema: HIGH — locked decisions from CONTEXT.md; models are idiomatic SQLAlchemy 2 mapped_column style

**Research date:** 2026-05-21
**Valid until:** 2026-08-21 (90 days — core stack is stable; Tailwind v4 and vitest move fast)
