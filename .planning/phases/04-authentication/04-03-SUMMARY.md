---
phase: 04-authentication
plan: "03"
subsystem: backend/auth-wiring
tags:
  - fastapi-users
  - csrf
  - starlette-csrf
  - mailhog
  - docker-compose
  - main.py

dependency_graph:
  requires:
    - "04-02-SUMMARY.md (auth/ package — fastapi_users, auth_backend_access, backends, schemas, oauth clients)"
    - "backend/app/routers/health.py (thin router pattern)"
  provides:
    - "backend/app/routers/auth.py (POST /api/auth/refresh custom endpoint)"
    - "backend/app/main.py (all auth routers registered + CSRFMiddleware after CORSMiddleware)"
    - "docker-compose.yml (mailhog service + backend SMTP/JWT env vars)"
  affects:
    - "04-04 (frontend — backend auth endpoints now reachable)"
    - "04-05 (green tests — /api/auth/register, /api/auth/login, /api/users/me all routable)"

tech_stack:
  added: []
  patterns:
    - "CSRFMiddleware registered AFTER CORSMiddleware — FastAPI reverse order gives CORS outermost"
    - "FastAPI-Users router factory pattern — 8 routers registered in main.py with prefix=/api/auth or /api/users"
    - "Custom /auth/refresh endpoint via auth_backend_access.login() + fastapi_users.current_user()"
    - "Mailhog dev email service — Docker image mailhog/mailhog, SMTP port 1025, web UI port 8025"

key_files:
  created:
    - backend/app/routers/auth.py
  modified:
    - backend/app/main.py
    - docker-compose.yml

decisions:
  - "CSRFMiddleware added after CORSMiddleware per RESEARCH.md Pitfall 4 — CORS outermost, CSRF innermost in reverse-order middleware stack"
  - "auth.router imported from app.routers.auth (not app.auth) — keeps thin router pattern separate from auth/ package service layer"
  - "get_access_strategy imported from app.auth.backends (not app.auth.users) — correct source of truth"
  - "GOOGLE_CLIENT_ID and FACEBOOK_CLIENT_ID omitted from docker-compose.yml — requires real credentials (handled in 04-06 OAuth checkpoint)"

metrics:
  duration: "~3 minutes"
  completed_date: "2026-05-24"
  tasks_completed: 3
  files_changed: 3

requirements:
  - AUTH-01
  - AUTH-02
  - AUTH-03
  - AUTH-04
  - AUTH-05
---

# Phase 04 Plan 03: Auth Wiring — main.py + CSRFMiddleware + Mailhog Summary

**One-liner:** FastAPI-Users routers wired into main.py with CSRFMiddleware (after CORSMiddleware), custom /auth/refresh endpoint, and Mailhog dev email service added to docker-compose.yml.

## Tasks Completed

| # | Task | Commit | Key Output |
|---|------|--------|-----------|
| 1 | Create routers/auth.py with custom /auth/refresh | c6ae11a | backend/app/routers/auth.py |
| 2 | Wire auth into main.py and add CSRFMiddleware | 9263360 | backend/app/main.py (59 lines added) |
| 3 | Add Mailhog service to docker-compose.yml | 2a615ec | docker-compose.yml (15 lines added) |

## What Was Built

### Task 1: backend/app/routers/auth.py

Thin router following health.py pattern. Single endpoint:

- `POST /auth/refresh` — validates active user via `fastapi_users.current_user(active=True)` (browser sends refresh cookie), then calls `auth_backend_access.login(get_access_strategy(), user, response)` to issue a new access cookie.
- Final URL when registered with `prefix="/api"`: `POST /api/auth/refresh`
- `get_access_strategy` imported from `app.auth.backends` (correct module).

### Task 2: backend/app/main.py

Added to existing main.py:

**New imports:**
- `from starlette_csrf import CSRFMiddleware`
- `from app.config import settings`
- `from app.auth.oauth import facebook_oauth_client, google_oauth_client`
- `from app.auth.schemas import UserCreate, UserRead, UserUpdate`
- `from app.auth.users import auth_backend_access, auth_backend_refresh, fastapi_users`
- Added `auth` to existing routers import line

**Middleware (order preserved):**
1. `CORSMiddleware` — registered first (outermost in execution order)
2. `CSRFMiddleware` — registered second (innermost, runs before CORS due to reverse order)

**Router registrations added (9 total — before existing routes):**
1. `auth.router` → `POST /api/auth/refresh`
2. `get_auth_router(auth_backend_access)` → `POST /api/auth/login`, `POST /api/auth/logout`
3. `get_register_router(UserRead, UserCreate)` → `POST /api/auth/register`
4. `get_verify_router(UserRead)` → `POST /api/auth/request-verify-token`, `POST /api/auth/verify`
5. `get_reset_password_router()` → `POST /api/auth/forgot-password`, `POST /api/auth/reset-password`
6. `get_users_router(UserRead, UserUpdate)` → `GET/PATCH /api/users/me`, `GET/PATCH/DELETE /api/users/{id}`
7. `get_oauth_router(google_oauth_client, ...)` → `GET /api/auth/google/authorize`, `GET /api/auth/google/callback`
8. `get_oauth_router(facebook_oauth_client, ...)` → `GET /api/auth/facebook/authorize`, `GET /api/auth/facebook/callback`

**All existing routes preserved:** `/health`, `/api/politicians/*`, `/api/parties/*`, `/api/elections/*`, `/api/promises/*`, `/api/stats`, `/api/og/*`

Total routes: 36 (including docs, openapi.json, redoc).

### Task 3: docker-compose.yml

**Added mailhog service block** (between postgres and backend services):
```yaml
mailhog:
  image: mailhog/mailhog
  ports:
    - "1025:1025"   # SMTP
    - "8025:8025"   # Web UI
  restart: unless-stopped
```

**Backend service additions:**
- Environment: `SMTP_HOST: mailhog`, `SMTP_PORT: "1025"`, `SMTP_FROM: noreply@khostumner.am`, `JWT_SECRET: dev-jwt-secret-change-in-production`, `CSRF_SECRET: dev-csrf-secret-change-in-production`, `FRONTEND_URL: http://localhost:5173`
- `depends_on`: Added `mailhog: condition: service_started` alongside existing postgres healthcheck dependency

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None in this plan's scope. All auth endpoints are fully routed through FastAPI-Users library (not stubs). The custom `/auth/refresh` endpoint is fully implemented. Mailhog service uses a real Docker image.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: plaintext_secret_in_compose | docker-compose.yml | `JWT_SECRET: dev-jwt-secret-change-in-production` and `CSRF_SECRET: dev-csrf-secret-change-in-production` are plaintext dev placeholders in version-controlled file — acceptable for dev; production must use env-injected secrets (T-04-16 in plan threat register, disposition: accept for dev) |

## Self-Check

- [x] `backend/app/routers/auth.py` exists
- [x] `backend/app/main.py` contains `CSRFMiddleware`
- [x] `docker-compose.yml` contains `mailhog/mailhog`
- [x] Commit c6ae11a exists (Task 1)
- [x] Commit 9263360 exists (Task 2)
- [x] Commit 2a615ec exists (Task 3)
- [x] `python -c "from app.main import app; routes=[r.path for r in app.routes]; assert any('login' in r for r in routes)"` passes
- [x] `python -c "from app.main import app; routes=[r.path for r in app.routes]; assert '/health' in routes"` passes
- [x] 36 routes registered (auth + existing)
- [x] CSRFMiddleware registered after CORSMiddleware (line 42 vs line 31)
- [x] SMTP_HOST, JWT_SECRET, CSRF_SECRET present in docker-compose.yml

## Self-Check: PASSED
