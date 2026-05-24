---
phase: 04-authentication
fixed_at: 2026-05-24T00:00:00Z
review_path: .planning/phases/04-authentication/04-REVIEW.md
iteration: 1
findings_in_scope: 16
fixed: 16
skipped: 0
status: all_fixed
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-05-24T00:00:00Z
**Source review:** .planning/phases/04-authentication/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 16 (9 Critical + 7 Warning; Info skipped per fix scope)
- Fixed: 16
- Skipped: 0

---

## Fixed Issues

### CR-01: Refresh endpoint now authenticates via refresh cookie backend

**Files modified:** `backend/app/routers/auth.py`
**Commits:** `219fd63`, `c084fd1`
**Applied fix:** Replaced `fastapi_users.current_user(active=True)` with `fastapi_users.current_user(active=True, get_enabled_backends=_only_refresh_backend)` where `_only_refresh_backend` is a dependency callable returning `[auth_backend_refresh]`. The `login` call is now `auth_backend_access.login(strategy, user, response)` matching the v15 API signature (2-arg, no response param). Also imported `auth_backend_refresh` in the router.

---

### CR-02: cookie_secure now reads from settings

**Files modified:** `backend/app/auth/backends.py`, `backend/app/config.py`
**Commit:** `4beb63a`
**Applied fix:** Added `COOKIE_SECURE: bool = True` to `Settings` in `config.py` (defaults secure; override to `false` in local dev via `.env`). Both `cookie_transport_access` and `cookie_transport_refresh` now pass `cookie_secure=settings.COOKIE_SECURE` instead of the hardcoded `False`.

---

### CR-03: Separate secrets for reset-password and verification tokens

**Files modified:** `backend/app/config.py`, `backend/app/auth/users.py`
**Commit:** `3b5afdc` (users.py), `4beb63a` (config.py)
**Applied fix:** Added `RESET_PASSWORD_SECRET` and `VERIFICATION_SECRET` fields to `Settings`. `UserManager.reset_password_token_secret` and `UserManager.verification_token_secret` now reference these distinct settings instead of both using `JWT_SECRET`.

---

### CR-04: HTML email href attributes use html.escape()

**Files modified:** `backend/app/auth/email.py`
**Commit:** `8870d3d`
**Applied fix:** Added `import html as html_module`. Both `send_verification_email` and `send_password_reset_email` now call `html_module.escape(url)` before embedding the URL in the `href` attribute. Attribute delimiters changed from single-quotes to double-quotes for consistency.

---

### CR-05: pytest-asyncio version corrected

**Files modified:** `backend/requirements-dev.txt`
**Commit:** `897e55e`
**Applied fix:** Changed `pytest-asyncio==1.3.0` (non-existent) to `pytest-asyncio==0.24.0` (latest stable 0.x release).

---

### CR-06: pydantic-settings pinned to exact version

**Files modified:** `backend/requirements.txt`
**Commit:** `b616a45`
**Applied fix:** Changed unpinned `pydantic-settings` to `pydantic-settings==2.7.0` for reproducible builds.

---

### CR-07: on_after_register uses user_db.update instead of new session

**Files modified:** `backend/app/auth/users.py`
**Commit:** `b2edb00`
**Applied fix:** Removed the `async with AsyncSessionLocal() as session:` block and the `sqlalchemy.update` import. Replaced with `await self.user_db.update(user, {"display_name": ...})` which operates within the existing session/transaction scope rather than opening a second independent transaction.

---

### CR-08: datetime.utcnow replaced with datetime.now(timezone.utc)

**Files modified:** `backend/app/models/users.py`
**Commit:** `049b454`
**Applied fix:** Added `timezone` to the `datetime` import. Changed `default=datetime.utcnow` to `default=lambda: datetime.now(timezone.utc)` producing a timezone-aware datetime compatible with the `DateTime(timezone=True)` / TIMESTAMPTZ column type.

---

### CR-09: CORS allowed origins read from settings

**Files modified:** `backend/app/main.py`, `backend/app/config.py`
**Commit:** `138e2c9` (main.py), `4beb63a` (config.py)
**Applied fix:** Added `ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]` to `Settings`. `CORSMiddleware` now passes `allow_origins=settings.ALLOWED_ORIGINS` so production deployments can override via environment variable without code changes.

---

### WR-01: Refresh backend login router registered in main.py

**Files modified:** `backend/app/main.py`
**Commit:** `f210a3e`
**Applied fix:** Added `app.include_router(fastapi_users.get_auth_router(auth_backend_refresh), prefix="/api/auth/refresh-backend", ...)` so the 30-day `khostumner_refresh` cookie is actually issued at login time.

---

### WR-02: get_access_strategy() called as factory (consistency fix bundled with CR-01)

**Files modified:** `backend/app/routers/auth.py`
**Commit:** `c084fd1`
**Applied fix:** The strategy is now assigned to a local variable (`strategy = get_access_strategy()`) before being passed to `auth_backend_access.login`. This was addressed as part of the CR-01 fix.

---

### WR-03: VerifyEmailPage useEffect dependency array fixed

**Files modified:** `frontend/src/pages/VerifyEmailPage.tsx`
**Commit:** `af7dcb0`
**Applied fix:** Extracted `const token = searchParams.get("token")` before the `useEffect`. The effect now declares `[token]` as its dependency array. The `// eslint-disable-line react-hooks/exhaustive-deps` comment was removed.

---

### WR-04: LoginPage checks /api/users/me response status

**Files modified:** `frontend/src/pages/LoginPage.tsx`
**Commit:** `851c186`
**Applied fix:** Changed the `/api/users/me` call to capture the `Response` object first, check `meRes.ok`, and only call `meRes.json()` and `dispatch` when the response is successful. Non-2xx responses now display an Armenian error message instead of polluting `state.user` with an error JSON object.

---

### WR-05: POSTGRES_PASSWORD added to docker-compose postgres service

**Files modified:** `docker-compose.yml`
**Commit:** `aa08f2b`
**Applied fix:** Added `POSTGRES_PASSWORD: khostumner` to the postgres service environment block. Also added `RESET_PASSWORD_SECRET`, `VERIFICATION_SECRET`, and `COOKIE_SECURE: "false"` to the backend service environment to wire the new config settings for local development.

---

### WR-06: on_after_login hook recomputes account_age_days

**Files modified:** `backend/app/auth/users.py`
**Commit:** `3843558`
**Applied fix:** Added `on_after_login` hook to `UserManager` that computes `(datetime.now(timezone.utc) - user.created_at).days` and persists the result via `self.user_db.update`. Phase 7 vote eligibility checks will now read a fresh value rather than always seeing `0`.

---

### WR-07: PaginationControls ellipsis uses current-page window algorithm

**Files modified:** `frontend/src/components/PaginationControls.tsx`
**Commit:** `5ac671c`
**Applied fix:** Replaced the fixed `[1, 2, 3, ellipsis, N-2, N-1, N]` pattern with a window-based algorithm. For `totalPages <= 5` all pages are shown. For larger totals, a `±1` window around `currentPage` is computed and ellipses are inserted only when gaps exist between `1`, the window, and `totalPages`. This ensures all pages are reachable for any value of `totalPages`.

---

## Skipped Issues

None — all 16 in-scope findings were fixed.

---

_Fixed: 2026-05-24T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
