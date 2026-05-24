---
phase: 04-authentication
reviewed: 2026-05-24T00:00:00Z
depth: standard
files_reviewed: 30
files_reviewed_list:
  - .gitignore
  - backend/.env.example
  - backend/alembic/versions/20260523_000001_auth_schema.py
  - backend/app/auth/__init__.py
  - backend/app/auth/backends.py
  - backend/app/auth/email.py
  - backend/app/auth/oauth.py
  - backend/app/auth/schemas.py
  - backend/app/auth/users.py
  - backend/app/config.py
  - backend/app/main.py
  - backend/app/models/__init__.py
  - backend/app/models/users.py
  - backend/app/routers/auth.py
  - backend/requirements.txt
  - backend/tests/test_auth.py
  - docker-compose.yml
  - frontend/src/App.tsx
  - frontend/src/components/Layout.tsx
  - frontend/src/components/PaginationControls.tsx
  - frontend/src/components/RequireAuth.test.tsx
  - frontend/src/components/RequireAuth.tsx
  - frontend/src/contexts/AuthContext.test.tsx
  - frontend/src/contexts/AuthContext.tsx
  - frontend/src/hooks/useAuth.ts
  - frontend/src/pages/LoginPage.test.tsx
  - frontend/src/pages/LoginPage.tsx
  - frontend/src/pages/RegisterPage.tsx
  - frontend/src/pages/ResetPasswordPage.tsx
  - frontend/src/pages/VerifyEmailPage.tsx
  - frontend/src/vite-env.d.ts
findings:
  critical: 9
  warning: 7
  info: 3
  total: 19
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-05-24T00:00:00Z
**Depth:** standard
**Files Reviewed:** 30
**Status:** issues_found

## Summary

Phase 4 delivers email + OAuth registration, JWT cookie sessions, CSRF protection, email verification, and password reset. The overall architecture is sound — FastAPI-Users is wired correctly, the dual-cookie access/refresh design is reasonable, and CSRF middleware is in place.

However, nine blockers were found. The most serious are: (1) the `/api/auth/refresh` endpoint reads the access cookie but never reads the refresh cookie, so the endpoint will 401 any user whose access token is already expired — defeating its entire purpose; (2) `cookie_secure=False` is hardcoded unconditionally, transmitting auth cookies over plain HTTP in every environment; (3) the shared `JWT_SECRET` is used for both reset-password tokens and verification tokens, so a leaked reset token can be reused for email verification and vice versa; (4) the email HTML body embeds the token URL inside an unquoted HTML attribute (`href='...'`), meaning a crafted `FRONTEND_URL` value can inject arbitrary HTML; (5) `pytest-asyncio==1.3.0` does not exist (latest stable is 0.x series) — the test suite will not install; (6) `pydantic-settings` is pinned without a version, making the backend build non-reproducible. Several additional security and correctness issues are documented below.

---

## Critical Issues

### CR-01: Refresh endpoint reads access cookie, not refresh cookie — token refresh never works for expired access tokens

**File:** `backend/app/routers/auth.py:10-14`

**Issue:** The `/api/auth/refresh` endpoint depends on `fastapi_users.current_user(active=True)`, which resolves against `auth_backend_access` (the 1-hour access cookie). When the access token is expired the dependency raises 401, so the endpoint never executes. The 30-day refresh cookie (`khostumner_refresh`) is never consulted. The entire silent re-auth flow in `AuthContext.tsx` (lines 62-75) therefore always fails when the access token has expired — the only scenario where refresh is needed.

**Fix:** Authenticate via the refresh backend in this endpoint:
```python
from app.auth.backends import auth_backend_access, auth_backend_refresh, get_access_strategy
from app.auth.users import fastapi_users

@router.post("/auth/refresh")
async def refresh_access_token(
    response: Response,
    user=Depends(fastapi_users.current_user(active=True, get_enabled_backends=[auth_backend_refresh])),
):
    return await auth_backend_access.login(get_access_strategy(), user, response)
```
If `get_enabled_backends` is not available in the installed version, inject the `SQLAlchemyUserDatabase` directly and validate the refresh JWT manually before issuing a new access token.

---

### CR-02: `cookie_secure=False` hardcoded — auth cookies transmitted over plain HTTP in all environments

**File:** `backend/app/auth/backends.py:9,17`

**Issue:** Both `cookie_transport_access` and `cookie_transport_refresh` set `cookie_secure=False` unconditionally with a comment "True in production." `cookie_secure=False` means browsers will send the `khostumner_access` and `khostumner_refresh` cookies over unencrypted HTTP. If this code is ever deployed to a non-local environment before that comment is acted on (e.g., a staging server reachable over HTTP), session tokens are transmitted in plaintext. The comment is not enforced by any runtime check.

**Fix:** Read the value from settings so it cannot be forgotten:
```python
# in config.py
COOKIE_SECURE: bool = True  # default True; override to False only in local dev via .env

# in backends.py
cookie_transport_access = CookieTransport(
    cookie_name="khostumner_access",
    cookie_max_age=3600,
    cookie_httponly=True,
    cookie_secure=settings.COOKIE_SECURE,
    cookie_samesite="lax",
)
```

---

### CR-03: Shared `JWT_SECRET` for access tokens, reset-password tokens, and verification tokens — cross-purpose token reuse

**File:** `backend/app/auth/users.py:25-26` and `backend/app/auth/backends.py:23,27`

**Issue:** `UserManager.reset_password_token_secret` and `UserManager.verification_token_secret` are both set to `settings.JWT_SECRET`, which is also the secret used by `JWTStrategy` to sign session access/refresh JWTs. A JWT signed for one purpose is valid for all three. Concretely: a stolen or leaked password-reset token can be submitted to the `/api/auth/verify` endpoint to verify an email address without the user's consent (and vice versa). FastAPI-Users embeds an `aud` claim only when the caller passes `audiences=`, but by default these tokens share the same signing key and have no audience restriction.

**Fix:** Use distinct secrets for each purpose:
```python
# config.py
JWT_SECRET: str = "change-me"
RESET_PASSWORD_SECRET: str = "change-me-reset"
VERIFICATION_SECRET: str = "change-me-verify"

# users.py
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.RESET_PASSWORD_SECRET
    verification_token_secret = settings.VERIFICATION_SECRET
```

---

### CR-04: HTML email body uses unquoted single-quoted `href` attribute — HTML injection via `FRONTEND_URL`

**File:** `backend/app/auth/email.py:30,48`

**Issue:** The email HTML is built with an f-string:
```python
f"<p><a href='{verify_url}'>{verify_url}</a></p>"
```
The `href` attribute uses single quotes. `verify_url` is formed as `f"{settings.FRONTEND_URL}/verify-email?token={token}"`. If `FRONTEND_URL` contains a single quote (e.g., a misconfigured value like `http://x'><script>`) the HTML attribute breaks and arbitrary HTML/JS can be injected into the email body. Tokens are signed and not user-controlled, but `FRONTEND_URL` is an admin-controlled setting that could be misconfigured or set via environment variable injection. Defence in depth requires escaping.

**Fix:** Use `html.escape()` or a templating library:
```python
import html

safe_url = html.escape(verify_url)
body = f"<html><body><p><a href=\"{safe_url}\">{safe_url}</a></p></body></html>"
```

---

### CR-05: `pytest-asyncio==1.3.0` does not exist — test suite cannot be installed

**File:** `backend/requirements-dev.txt:2`

**Issue:** The published `pytest-asyncio` package uses `0.x` versioning (e.g., `0.23.x`, `0.24.x`). Version `1.3.0` does not exist on PyPI. Any `pip install -r requirements-dev.txt` will fail with a "No matching distribution found" error, making it impossible to run the test suite in CI or locally.

**Fix:** Pin to the latest stable 0.x release:
```
pytest-asyncio==0.24.0
```

---

### CR-06: `pydantic-settings` unpinned — non-reproducible backend build

**File:** `backend/requirements.txt:7`

**Issue:** `pydantic-settings` is listed without a version constraint. Every `pip install` will silently pull the latest release, which may introduce breaking changes between deployments (e.g., `pydantic-settings` 2.x changed the `env_file` handling). All other dependencies are pinned to exact versions; this is the only exception. This directly affects `app/config.py` which imports from it.

**Fix:**
```
pydantic-settings==2.7.0
```
(Pin to whatever version is already installed in the working environment.)

---

### CR-07: `on_after_register` opens a second database session to update `display_name` — breaks inside the original transaction / session scope

**File:** `backend/app/auth/users.py:31-37`

**Issue:** FastAPI-Users calls `on_after_register` with an already-open session. The hook opens a brand-new `AsyncSessionLocal()` context to issue an `UPDATE`, then commits it. This is a second independent transaction. If the first transaction (the `INSERT`) has not yet committed when this runs, the `UPDATE WHERE id = user.id` will find no row and silently do nothing, resulting in `display_name` staying as the empty-string default. Even when it works by coincidence of timing, the hook is violating the intended FastAPI-Users extension pattern: `on_after_register` receives the already-committed user row, but the correct approach is to pass `display_name` at create-time or use the FastAPI-Users `UserCreate` schema (which already has `display_name: str` defined in `schemas.py`).

**Fix:** Remove the secondary session. FastAPI-Users calls `create` with the `UserCreate` payload which contains `display_name`. Since `display_name` is in `UserCreate` and `User.display_name` is a mapped column, it should be set directly by the create path. If it genuinely needs a fallback for OAuth users (who have no `display_name`), override `on_after_register` and update via the injected `user_db` reference, not a fresh session:
```python
async def on_after_register(self, user: User, request=None):
    if not user.display_name:
        await self.user_db.update(user, {"display_name": user.email.split("@")[0]})
```

---

### CR-08: `datetime.utcnow` deprecated and produces naive datetime — stored in timezone-aware column

**File:** `backend/app/models/users.py:42`

**Issue:** `default=datetime.utcnow` passes the function object (not the result) as the SQLAlchemy column default. On each `INSERT`, SQLAlchemy calls `datetime.utcnow()` which returns a naive (timezone-unaware) `datetime`. The column is declared `DateTime(timezone=True)`, which in PostgreSQL maps to `TIMESTAMPTZ`. Python 3.12 emits a deprecation warning for `datetime.utcnow()`; in Python 3.14 it is removed. Additionally, mixing naive datetimes with a `TIMESTAMPTZ` column produces inconsistent behaviour across database drivers.

**Fix:**
```python
from datetime import datetime, timezone

created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
)
```

---

### CR-09: Hardcoded `allow_origins` with no environment-based override — CORS blocks production frontend

**File:** `backend/app/main.py:32-36`

**Issue:** `allow_origins=["http://localhost:5173"]` is hardcoded with no way to configure additional origins. When deployed to a staging or production domain (e.g., `https://khostumner.am`), browsers will block all cross-origin fetch requests because the origin does not match. Unlike `cookie_secure`, this value has no corresponding setting in `config.py` or `docker-compose.yml` environment block.

**Fix:** Add an `ALLOWED_ORIGINS` setting:
```python
# config.py
ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Warnings

### WR-01: `auth_backend_refresh` imported but never registered as a login endpoint

**File:** `backend/app/main.py:9,53`

**Issue:** `auth_backend_refresh` is imported and passed to `FastAPIUsers([auth_backend_access, auth_backend_refresh])`, but `fastapi_users.get_auth_router(auth_backend_refresh)` is never called. FastAPI-Users only creates login/logout routes for backends whose `get_auth_router` is explicitly included. The refresh backend's cookie is therefore never set by a login response — the `khostumner_refresh` cookie is never issued to the client. The entire refresh token infrastructure (30-day cookie, `get_refresh_strategy`) is dead code.

**Fix:** Register the refresh login route:
```python
app.include_router(
    fastapi_users.get_auth_router(auth_backend_refresh),
    prefix="/api/auth/refresh-backend",
    tags=["auth"],
)
```
Or, if the intent is to have the access login also set the refresh cookie, handle that explicitly in the login response handler rather than registering a separate endpoint.

---

### WR-02: `get_access_strategy()` called as a plain function call (not passed as a callable) in the refresh router

**File:** `backend/app/routers/auth.py:14`

**Issue:** `auth_backend_access.login(get_access_strategy(), user, response)` calls `get_access_strategy()` eagerly and passes the resulting `JWTStrategy` instance directly. The `AuthenticationBackend.login` signature expects a `Strategy` instance, so this happens to work today. However `get_access_strategy` is designed as a factory meant to be called once per request (it reads `settings` at call time). If settings are ever mocked/overridden in tests, the already-instantiated strategy will retain the original settings. Consistency with the pattern used by FastAPI-Users internally (where `get_strategy` is a callable) is important.

**Fix:** This is a minor consistency issue, but to match the pattern:
```python
strategy = get_access_strategy()
return await auth_backend_access.login(strategy, user, response)
```
This is already what the code does; the real fix is to address CR-01 before this endpoint is usable.

---

### WR-03: `VerifyEmailPage` fires the verification POST in a `useEffect` with an empty dependency array while suppressing the `react-hooks/exhaustive-deps` lint rule

**File:** `frontend/src/pages/VerifyEmailPage.tsx:20-47`

**Issue:** `useEffect(() => { ... }, [])` reads `searchParams` from outside but does not include it in the dependency array. The `eslint-disable-line react-hooks/exhaustive-deps` comment suppresses the warning. If React ever re-renders with a different `searchParams` (e.g., navigating to the page with a different token), the effect does not re-run and the new token is never submitted. More concretely: in React 18 strict mode the effect runs twice in development; the second run fires a second POST to `/api/auth/verify` with the same (now-consumed) token, which returns an error, potentially flipping `status` back to `"error"` after a brief success.

**Fix:** Include `searchParams` in the dependency array, or extract the token before the effect and include it:
```tsx
const token = searchParams.get("token")

useEffect(() => {
  if (!token) {
    setStatus("error")
    return
  }
  // ... fetch with token
}, [token])
// Remove eslint-disable comment
```

---

### WR-04: `LoginPage` does not check `/api/users/me` response status before calling `dispatch`

**File:** `frontend/src/pages/LoginPage.tsx:48-51`

**Issue:**
```ts
const me = await fetch(`${API_BASE}/api/users/me`, {
  credentials: "include",
}).then((r) => r.json())
dispatch({ type: "SET_USER", payload: me })
```
If the `/api/users/me` request fails (network error, 401, 500), `.then((r) => r.json())` will either throw (on network error) or parse an error JSON object (on non-2xx). In the 401/500 case the error body is dispatched as the user payload, which will populate `state.user` with `{ detail: "Unauthorized" }` — a non-null object. Any component checking `state.user` truthy will believe the user is logged in. The `catch` block at line 56 catches network errors but not a successful HTTP response with a non-2xx status code.

**Fix:**
```ts
const meRes = await fetch(`${API_BASE}/api/users/me`, { credentials: "include" })
if (meRes.ok) {
  const me = await meRes.json()
  dispatch({ type: "SET_USER", payload: me })
  navigate("/")
} else {
  setError("Մուտքն ի վիճակ չէ հաստատել")
}
```

---

### WR-05: `POSTGRES_PASSWORD` missing from `docker-compose.yml` postgres service — password authentication may fail

**File:** `docker-compose.yml:7-12`

**Issue:** The `postgres` service defines `POSTGRES_DB` and `POSTGRES_USER` but not `POSTGRES_PASSWORD`. The `backend` service connects with `postgresql+asyncpg://khostumner:khostumner@postgres:5432/khostumner`, implying the password is `khostumner`. Without `POSTGRES_PASSWORD: khostumner` in the postgres service environment, PostgreSQL will set an empty password or rely on the `env_file` values. If `.env` does not define `POSTGRES_PASSWORD`, the database may start with peer/trust authentication and the backend may fail to connect with the supplied password on certain PostgreSQL configurations.

**Fix:** Add explicit password to the postgres service:
```yaml
environment:
  POSTGRES_DB: khostumner
  POSTGRES_USER: khostumner
  POSTGRES_PASSWORD: khostumner
```
For production, source this from a secret, not a hardcoded value.

---

### WR-06: `account_age_days` is a cached integer updated "on login" — but no login hook updates it

**File:** `backend/app/models/users.py:43`

**Issue:** The field comment says "cached; computed on login," but there is no `on_after_login` hook in `UserManager` and no code anywhere updates this field. It will always remain `0`. The CLAUDE.md anti-brigading requirement states "Require account age ≥ 7 days + email verification before voting." If voting logic in Phase 7 reads `account_age_days` it will always see `0` and either always block or always allow, depending on how the check is written.

**Fix:** Either implement the `on_after_login` hook to recompute and persist `account_age_days`, or compute account age dynamically from `created_at` at check-time and remove the cached column (it provides no useful optimisation for a single comparison):
```python
from datetime import datetime, timezone

def account_age_days(user: User) -> int:
    return (datetime.now(timezone.utc) - user.created_at).days
```

---

### WR-07: `PaginationControls` ellipsis logic produces wrong page numbers when `totalPages` is between 7 and 9

**File:** `frontend/src/components/PaginationControls.tsx:40`

**Issue:** When `totalPages > 7`, the page numbers shown are always `[1, 2, 3, "ellipsis", totalPages-2, totalPages-1, totalPages]`. For `totalPages = 8`, this gives `[1, 2, 3, "ellipsis", 6, 7, 8]` — pages 4 and 5 are silently unreachable. For `totalPages = 7`, the early branch takes over and all pages show correctly. The bug window is `totalPages` in the range 8–9: with 8 total pages pages 4–5 are missing, with 9 total pages page 4 and 5 are missing. This is a pagination correctness bug where users cannot navigate to certain pages.

**Fix:** Use a proper windowing algorithm that adjusts the window around the current page, or for a simple fix change the threshold:
```ts
if (totalPages <= 5) {
  pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1)
} else {
  const near = [currentPage - 1, currentPage, currentPage + 1].filter(
    (p) => p > 1 && p < totalPages
  )
  pageNumbers = [1, ...(near[0] > 2 ? ["ellipsis" as const] : []), ...near,
    ...(near[near.length - 1] < totalPages - 1 ? ["ellipsis" as const] : []), totalPages]
}
```

---

## Info

### IN-01: `backend/.env.example` inaccessible — file-permission error during review

**File:** `backend/.env.example`

**Issue:** The file could not be read due to OS permission settings on this machine. This means its contents have not been reviewed. Verify manually that it does not contain real secrets (it should contain only placeholder values) and that it is committed to version control so new contributors know what environment variables are required.

---

### IN-02: `display_name` column has `nullable=False, default=""` — silently stores empty strings for OAuth users

**File:** `backend/app/models/users.py:38`

**Issue:** The column default is an empty string `""`. For OAuth registrations where `display_name` is not set by the caller, `on_after_register` is supposed to set it from the email. However because `on_after_register` has the second-session bug (CR-07), this fallback may silently fail, leaving a blank display name. The `nullable=False` constraint does not prevent empty strings at the database level. Any UI rendering `user.display_name` will show nothing for these accounts with no error.

**Fix:** Add a database-level CHECK constraint and/or an application-level validator:
```python
# models/users.py — add a CheckConstraint
from sqlalchemy import CheckConstraint
# in __table_args__:
CheckConstraint("length(display_name) > 0", name="ck_users_display_name_nonempty")
```

---

### IN-03: `docker-compose.yml` backend service uses `--reload` in production command

**File:** `docker-compose.yml:36-37`

**Issue:** The uvicorn startup command includes `--reload`, which watches the filesystem for changes and restarts on modification. This is a development convenience that should not be in a Docker Compose service that could be used for staging or production. `--reload` also disables preloading optimisations and causes uvicorn to fork a reloader process. The flag is acceptable if this file is exclusively for local development, but there is no separate production compose file, and the comment says nothing to that effect.

**Fix:** Remove `--reload` from the uvicorn command, or extract it to a separate `docker-compose.override.yml` that is only used in development:
```yaml
command: >
  sh -c "alembic upgrade head &&
         python -m app.services.seed &&
         uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

---

_Reviewed: 2026-05-24T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
