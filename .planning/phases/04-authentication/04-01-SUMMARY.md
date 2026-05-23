---
phase: 04-authentication
plan: "01"
subsystem: backend/auth-schema
tags:
  - alembic
  - migration
  - fastapi-users
  - postgresql
  - tdd-red
dependency_graph:
  requires:
    - "03-05-SUMMARY.md (promise browsing complete)"
    - "backend/alembic/versions/20260522_000001_add_party_slug.py (down_revision)"
  provides:
    - "backend/alembic/versions/20260523_000001_auth_schema.py (auth schema migration)"
    - "backend/requirements.txt (6 auth packages added)"
    - "backend/tests/test_auth.py (9 RED xfail stubs)"
  affects:
    - "04-02 (User model refactor + FastAPI-Users wiring)"
    - "04-03 (email/OAuth backend)"
tech_stack:
  added:
    - "fastapi-users[sqlalchemy]==15.0.5"
    - "fastapi-mail==1.6.4"
    - "starlette-csrf==3.0.0"
    - "python-multipart==0.0.29"
    - "httpx-oauth==0.17.0"
    - "bcrypt==5.0.0"
  patterns:
    - "Alembic ALTER COLUMN rename (password_hash -> hashed_password, email_verified -> is_verified)"
    - "op.f() naming convention for FK and index constraints"
    - "String(4096) override for OAuth access_token (Pitfall 3)"
    - "pytest.mark.xfail(strict=False) RED stubs with NotImplementedError"
key_files:
  created:
    - backend/alembic/versions/20260523_000001_auth_schema.py
    - backend/tests/test_auth.py
  modified:
    - backend/requirements.txt
    - backend/app/models/__init__.py
decisions:
  - "OAuthAccount import deferred to 04-02 — premature import in __init__.py caused ImportError breaking test collection (Rule 1 fix)"
  - "String(4096) for oauth_accounts.access_token and refresh_token — Google RS256 tokens exceed 1024 chars"
  - "downgrade() includes index drops before table drop for clean rollback"
metrics:
  duration: "~8 minutes"
  completed_date: "2026-05-24"
  tasks_completed: 3
  files_changed: 4
requirements:
  - AUTH-01
  - AUTH-02
  - AUTH-03
  - AUTH-04
  - AUTH-05
---

# Phase 04 Plan 01: Auth Schema Migration and RED Test Stubs Summary

**One-liner:** Alembic migration renames users columns to FastAPI-Users names, creates oauth_accounts table, installs 6 auth packages, and stubs 9 xfail tests covering all AUTH-0x requirements.

## Tasks Completed

| # | Task | Commit | Key Output |
|---|------|--------|-----------|
| 1 | Alembic auth schema migration | d2939a0 | 20260523_000001_auth_schema.py |
| 2 | Auth packages + models/__init__.py update | fa00d63 | requirements.txt (6 new pkgs) |
| 3 | RED test stubs for AUTH-01 through AUTH-05 | 84983dc | test_auth.py (9 xfail tests) |

## What Was Built

### Task 1: Alembic Migration (20260523_000001_auth_schema.py)

Migration with `down_revision = "20260522_000001"` performing four operations in upgrade():

1. `op.alter_column("users", "password_hash", new_column_name="hashed_password")` — FastAPI-Users expects this name
2. `op.alter_column("users", "email_verified", new_column_name="is_verified")` — FastAPI-Users expects this name
3. `op.add_column("users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"))` — missing required column
4. `op.create_table("oauth_accounts", ...)` with String(4096) access_token and refresh_token, FK to users.id with CASCADE DELETE, indexes on oauth_name/account_id/account_email

downgrade() reverses all four operations in reverse order (index drops before table drop, alter_column reverses).

### Task 2: Auth Package Dependencies

Added to `backend/requirements.txt`:
- `fastapi-users[sqlalchemy]==15.0.5` — opinionated auth library (maintenance mode, stable)
- `fastapi-mail==1.6.4` — async SMTP for verification/reset emails
- `starlette-csrf==3.0.0` — double-submit cookie CSRF (required for httpOnly JWT + SPA)
- `python-multipart==0.0.29` — form parsing required by FastAPI for OAuth2 login form
- `httpx-oauth==0.17.0` — Google/Facebook OAuth2 clients
- `bcrypt==5.0.0` — password hashing backend

All 6 packages slopcheck [OK] per RESEARCH.md Package Legitimacy Audit.

`backend/app/models/__init__.py` retains `User, UserRole` import (OAuthAccount import deferred — see Deviations).

### Task 3: RED Test Stubs

`backend/tests/test_auth.py` with 9 `pytest.mark.xfail(reason="auth not implemented yet", strict=False)` stubs:

- `test_register_success` — AUTH-01
- `test_register_duplicate_email` — AUTH-01
- `test_request_verify` — AUTH-02
- `test_verify_email` — AUTH-02
- `test_forgot_password` — AUTH-03
- `test_reset_password` — AUTH-03
- `test_oauth_google_authorize` — AUTH-04
- `test_me_authenticated` — AUTH-05
- `test_me_unauthenticated` — AUTH-05

Each stub raises `NotImplementedError("implement in 04-02/04-03")` to ensure proper XFAIL state.
Fixture uses `ASGITransport(app=app)` pattern matching `test_health.py`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reverted premature OAuthAccount import in models/__init__.py**

- **Found during:** Task 3 verification
- **Issue:** Task 2 added `from app.models.users import User, UserRole, OAuthAccount` to `__init__.py`, but `OAuthAccount` class does not exist in `users.py` yet (it will be created in plan 04-02). This caused `ImportError` when pytest attempted to collect `test_auth.py`, as all imports chain through `app.main -> app.models`. Task 3 done criteria requires "file runs without import errors."
- **Fix:** Changed `__init__.py` import back to `from app.models.users import User, UserRole  # noqa: F401  # OAuthAccount added in 04-02`. The OAuthAccount import will be restored in 04-02 when the class is defined.
- **Files modified:** `backend/app/models/__init__.py`
- **Commit:** 84983dc (included with Task 3 commit)
- **Plan note reconciled:** Plan Task 2 note says "The import will fail until 04-02 completes; that is expected." However, plan Task 3 done criteria requires tests to collect without errors. The fix aligns with Task 3 done criteria while tracking the TODO in a comment.

## Known Stubs

None in the scope of deliverables — `test_auth.py` stubs are intentional RED stubs, not data stubs. All raise `NotImplementedError` explicitly; no hardcoded empty values or placeholder data flow to any UI.

## Threat Flags

No new security surface introduced. Migration runs in the Alembic offline context (psycopg2 sync). No new network endpoints, auth paths, or trust boundaries opened in this plan.

## Self-Check

- [x] `backend/alembic/versions/20260523_000001_auth_schema.py` exists
- [x] `backend/tests/test_auth.py` exists
- [x] Commit d2939a0 exists (Task 1)
- [x] Commit fa00d63 exists (Task 2)
- [x] Commit 84983dc exists (Task 3)
- [x] Alembic HEAD is 20260523_000001
- [x] All 9 tests collected: `pytest --co -q` shows 9 items
- [x] All 9 tests XFAIL: `pytest tests/test_auth.py` shows `9 xfailed`

## Self-Check: PASSED
