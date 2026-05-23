---
phase: 04-authentication
plan: "02"
subsystem: backend/auth
tags:
  - fastapi-users
  - jwt
  - sqlalchemy
  - oauth
  - fastapi-mail
  - smtp
  - pydantic

dependency_graph:
  requires:
    - "04-01-SUMMARY.md (auth schema migration + RED stubs + packages in requirements.txt)"
    - "backend/app/database.py (AsyncSessionLocal)"
    - "backend/app/config.py (Settings class)"
    - "backend/app/models/users.py (User model)"
  provides:
    - "backend/app/models/users.py (User(SQLAlchemyBaseUserTableUUID, Base) + OAuthAccount)"
    - "backend/app/config.py (12 Phase 4 settings: JWT_SECRET, CSRF_SECRET, SMTP_*, OAuth IDs, FRONTEND_URL)"
    - "backend/app/auth/__init__.py (package marker)"
    - "backend/app/auth/backends.py (auth_backend_access, auth_backend_refresh)"
    - "backend/app/auth/schemas.py (UserRead, UserCreate, UserUpdate)"
    - "backend/app/auth/email.py (send_verification_email, send_password_reset_email)"
    - "backend/app/auth/users.py (UserManager, fastapi_users, get_user_manager)"
    - "backend/app/auth/oauth.py (google_oauth_client, facebook_oauth_client)"
  affects:
    - "04-03 (auth router — imports fastapi_users, auth_backend_access, schemas, OAuth clients)"
    - "04-04 (frontend auth pages — login/register POSTs backend endpoints wired here)"
    - "04-05 (main.py wiring — fastapi_users routers, CSRFMiddleware)"

tech_stack:
  added:
    - "fastapi-users[sqlalchemy]==15.0.5 (installed from requirements.txt — was in requirements but not in env)"
    - "fastapi-mail==1.6.4"
    - "starlette-csrf==3.0.0"
    - "python-multipart==0.0.29"
    - "httpx-oauth==0.17.0"
    - "bcrypt==5.0.0"
  patterns:
    - "SQLAlchemyBaseUserTableUUID mixin — User class inherits, no duplicate column declarations"
    - "SQLAlchemyBaseOAuthAccountTableUUID mixin — OAuthAccount with String(4096) override"
    - "Two AuthenticationBackend instances (access 1hr, refresh 30d) with CookieTransport + JWTStrategy"
    - "fastapi-users base schemas extended: UserCreate adds display_name required field"
    - "UserManager hooks: on_after_request_verify -> send_verification_email; on_after_forgot_password -> send_password_reset_email"

key_files:
  created:
    - backend/app/auth/__init__.py
    - backend/app/auth/backends.py
    - backend/app/auth/schemas.py
    - backend/app/auth/email.py
    - backend/app/auth/users.py
    - backend/app/auth/oauth.py
  modified:
    - backend/app/models/users.py
    - backend/app/config.py
    - backend/app/models/__init__.py

key_decisions:
  - "OAuthAccount.access_token overridden to String(4096) — Google RS256 tokens exceed 1024 chars (Pitfall 3)"
  - "Two auth backends (access_cookie + refresh_cookie) with separate JWTStrategy lifetimes — no built-in refresh rotation in fastapi-users"
  - "display_name auto-populated from email local-part in on_after_register if empty (handles OAuth users)"
  - "UserRole imported in schemas.py but role field typed as str for UserRead serialization compatibility"
  - "fastapi-users packages installed to local Python env as part of this plan execution (packages were in requirements.txt from 04-01 but not installed)"

patterns_established:
  - "auth/ package: single source of truth for FastAPI-Users wiring — backends, schemas, email, UserManager, OAuth clients"
  - "UserManager inherits UUIDIDMixin + BaseUserManager[User, uuid.UUID] — standard fastapi-users pattern"
  - "get_async_session dependency reuses AsyncSessionLocal (not engine) per AsyncSession dependency pattern"

requirements_completed:
  - AUTH-01
  - AUTH-02
  - AUTH-03
  - AUTH-04
  - AUTH-05

duration: ~3min
completed: "2026-05-24"
---

# Phase 04 Plan 02: Auth Layer — User Model + auth/ Package Summary

**FastAPI-Users wired to SQLAlchemy User model with two-backend JWT cookie auth, email hooks via fastapi-mail, OAuth clients for Google/Facebook, and UserCreate extended with required display_name field.**

## Performance

- **Duration:** ~3 minutes
- **Started:** 2026-05-23T20:25:36Z
- **Completed:** 2026-05-23T20:29:00Z
- **Tasks:** 3
- **Files modified:** 9 (3 modified + 6 created)

## Accomplishments

- User model refactored to inherit SQLAlchemyBaseUserTableUUID + Base with OAuthAccount relationship; duplicate columns removed
- Complete auth/ package (6 modules): backends, schemas, email, users, oauth, __init__
- config.py extended with 12 Phase 4 settings (JWT_SECRET, CSRF_SECRET, SMTP_*, OAuth client IDs, FRONTEND_URL)

## Task Commits

Each task was committed atomically:

1. **Task 1: Update User model and config.py** - `edb9475` (feat)
2. **Task 2: Create auth/ package — backends, schemas, email** - `a166447` (feat)
3. **Task 3: Create auth/users.py and auth/oauth.py** - `c301df7` (feat)

**Plan metadata:** to be added (docs: complete plan)

## Files Created/Modified

- `backend/app/models/users.py` - Refactored to SQLAlchemyBaseUserTableUUID, added OAuthAccount class, removed duplicate columns
- `backend/app/config.py` - Added 12 Phase 4 settings fields
- `backend/app/models/__init__.py` - Updated to export OAuthAccount (deferred from 04-01)
- `backend/app/auth/__init__.py` - Empty package marker
- `backend/app/auth/backends.py` - auth_backend_access (access_cookie, 3600s) and auth_backend_refresh (refresh_cookie, 2592000s)
- `backend/app/auth/schemas.py` - UserRead, UserCreate (display_name required), UserUpdate
- `backend/app/auth/email.py` - send_verification_email + send_password_reset_email with Armenian HTML bodies
- `backend/app/auth/users.py` - UserManager, fastapi_users instance, get_user_manager dependency
- `backend/app/auth/oauth.py` - google_oauth_client, facebook_oauth_client

## Decisions Made

- **Two-backend auth pattern:** access_cookie (1h) + refresh_cookie (30d) — fastapi-users has no built-in refresh rotation; this is the standard community pattern per Discussion #989
- **display_name auto-populated:** on_after_register sets display_name to email.split("@")[0] when empty, to handle OAuth registrations where provider doesn't supply a display name
- **String(4096) for OAuthAccount.access_token:** Google RS256 tokens can exceed 1024 chars; override prevents silent truncation (Pitfall 3)
- **role field as str in UserRead:** UserRole enum serialized as string for JSON compatibility with frontend

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed auth packages from requirements.txt into local Python environment**

- **Found during:** Task 1 verification
- **Issue:** `fastapi-users` and the other 5 packages added to requirements.txt in plan 04-01 were not installed in the local Python environment, causing `ModuleNotFoundError: No module named 'fastapi_users'`
- **Fix:** Ran `pip install "fastapi-users[sqlalchemy]==15.0.5" "fastapi-mail==1.6.4" "starlette-csrf==3.0.0" "python-multipart==0.0.29" "httpx-oauth==0.17.0" "bcrypt==5.0.0"` — these are the same packages already in requirements.txt, verified in RESEARCH.md Package Legitimacy Audit (all [OK])
- **Files modified:** none (pip install only, no file changes)
- **Verification:** `from app.models.users import User, OAuthAccount, UserRole` succeeds after install
- **Note:** Not a new package install decision — packages were already approved and in requirements.txt from 04-01

**2. [Rule 1 - Bug] Cleaned up on_after_register implementation**

- **Found during:** Task 3 (initial write)
- **Issue:** First draft used `__import__("sqlalchemy")` inline which is an anti-pattern
- **Fix:** Added proper `from sqlalchemy import update` at module top
- **Files modified:** `backend/app/auth/users.py`
- **Committed in:** c301df7 (included in Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking — env install, 1 bug — code cleanup)
**Impact on plan:** Both fixes necessary for correctness. No scope creep.

## Issues Encountered

None beyond the deviations documented above.

## Known Stubs

None — all modules are fully implemented. Email functions have real Armenian HTML bodies. OAuth clients are instantiated from settings (empty string defaults work for dev; real credentials needed for OAuth flows).

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: config_defaults | backend/app/config.py | JWT_SECRET defaults to "change-me-in-production" — acceptable for dev; docker-compose.yml must override; production requires real secret via env |

Note: T-04-12 (JWT_SECRET default) is already in the plan threat register with disposition "accept" — docker-compose.yml in 04-05 will set dev-jwt-secret override.

## Next Phase Readiness

- auth/ package complete and all modules importable without error
- Plan 04-03 can immediately import: `from app.auth.users import fastapi_users, get_user_manager, auth_backend_access, auth_backend_refresh`
- Plan 04-03 can immediately import: `from app.auth.schemas import UserRead, UserCreate, UserUpdate`
- Plan 04-03 can immediately import: `from app.auth.oauth import google_oauth_client, facebook_oauth_client`
- docker-compose.yml Mailhog + env vars wired in 04-05 (Wave 5)

---
*Phase: 04-authentication*
*Completed: 2026-05-24*
