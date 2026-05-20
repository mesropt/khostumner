# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 01-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 1-Foundation
**Areas discussed:** Repo structure, DB schema scope, Local dev setup, Seed data

---

## Repo Structure

### Root layout

| Option | Description | Selected |
|--------|-------------|----------|
| backend/ + frontend/ at root | Standard monorepo: /backend (FastAPI), /frontend (React/Vite), docker-compose.yml and Makefile at root | ✓ |
| src/ with sub-dirs | /src/backend and /src/frontend nested under src/ | |
| Separate repos | backend and frontend in separate git repositories | |

**User's choice:** backend/ + frontend/ at root

### Backend internal structure

| Option | Description | Selected |
|--------|-------------|----------|
| По модулям | routers/, models/, schemas/, services/ — one file per entity | ✓ |
| По фичам (Feature-based) | politicians/, promises/ — each feature has its own router/model/schema | |

**User's choice:** По модулям (by type/layer)

### Frontend internal structure

| Option | Description | Selected |
|--------|-------------|----------|
| По типам | components/, pages/, api/, hooks/, types/ | ✓ |
| По фичам | features/promises/, features/politicians/ | |

**User's choice:** По типам (by type)

---

## DB Schema Scope

### How much schema to build in Phase 1

| Option | Description | Selected |
|--------|-------------|----------|
| Полная схема сразу | All tables for all 8 phases now | ✓ |
| Только Phase 2–3 | Only politicians/parties/elections/promises tables now | |

**User's choice:** Full schema upfront

### Party affiliation modelling

| Option | Description | Selected |
|--------|-------------|----------|
| Связь со временем | politician_party_memberships(politician_id, party_id, start_date, end_date) | ✓ |
| Простой FK | politicians.party_id — static foreign key | |

**User's choice:** Time-bounded membership table

### Politician vs Party entity

| Option | Description | Selected |
|--------|-------------|----------|
| Отдельные таблицы | politicians and parties — separate tables with separate attributes | ✓ |
| entities (полиморфная) | Single entities(type=politician\|party) table | |

**User's choice:** Separate tables

---

## Local Dev Setup

### How to run locally

| Option | Description | Selected |
|--------|-------------|----------|
| Docker Compose | docker-compose up — starts PostgreSQL + FastAPI + Vite in one command | ✓ |
| Вручную | uvicorn + npm run dev + local PostgreSQL manually | |
| Docker Compose для DB, вручную для приложений | PostgreSQL in Docker, FastAPI + Vite run directly | |

**User's choice:** Full Docker Compose

### CI pipeline

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Actions | On push/PR: ruff + pytest (backend), eslint + tsc (frontend) | ✓ |
| Пока вручную | Only pre-commit hooks locally, CI later | |

**User's choice:** GitHub Actions from Phase 1

---

## Seed Data

### Real vs fictional politicians

| Option | Description | Selected |
|--------|-------------|----------|
| Реальные политики | Real Armenian names, marked [TEST DATA] in promise text | ✓ |
| Вымышленные имена | Armenian names but fictional | |

**User's choice:** Real politicians (marked as test data)

### Seed data volume

| Option | Description | Selected |
|--------|-------------|----------|
| Минимально | 3 politicians, 2 parties, 2 elections, 5 promises | |
| Больше | 10 politicians, 4 parties, 4 elections, 20 promises | ✓ |

**User's choice:** Larger seed set for realistic UI testing

---

## Claude's Discretion

- Python package versions within FastAPI/SQLAlchemy/Alembic ecosystem
- Docker image base versions (python:3.12-slim, node:20-alpine)
- Alembic migration naming convention
- Pre-commit hooks configuration

## Deferred Ideas

None — discussion stayed within phase scope.
