---
phase: 05-promise-submission
plan: 01
subsystem: backend-schema
tags: [migration, orm-models, pydantic-schemas, test-stubs, npm-deps]
dependency_graph:
  requires: [04-06]
  provides: [promise_edits-tables, PromiseEdit-model, PromiseEditElectionLink-model, PromiseCreateIn-schema, PromiseEditIn-schema, PromiseOut-schema, PromiseEditOut-schema, RED-test-stubs]
  affects: [05-02, 05-03, 05-04, 05-05]
tech_stack:
  added: [python-slugify==8.0.4, "@radix-ui/react-popover@1.1.15", "cmdk@1.1.1", "@radix-ui/react-checkbox@1.3.3", "@radix-ui/react-radio-group@1.3.8", "@radix-ui/react-label@2.1.8"]
  patterns: [pgENUM(create_type=False) for reusing existing PostgreSQL enum types in new migrations]
key_files:
  created:
    - backend/alembic/versions/20260524_000001_add_promise_edits.py
    - backend/app/models/promise_edits.py
  modified:
    - backend/app/schemas/promises.py
    - backend/tests/test_promises.py
    - backend/requirements.txt
    - backend/Dockerfile
    - frontend/package.json
    - frontend/package-lock.json
decisions:
  - "Use sqlalchemy.dialects.postgresql.ENUM(create_type=False) in Alembic migration for moderation_status reuse — sa.Enum does not expose create_type attribute in SQLAlchemy 2.x"
  - "RED test stubs use only existing `client` fixture (not future verified_user_client) to avoid pytest ERROR on missing fixtures; future fixtures added in Wave 1 (plan 02)"
  - "Dockerfile --use-deprecated=legacy-resolver: pre-existing fastapi-mail==1.6.4 / starlette<0.47.0 conflict requires legacy resolver; behavior unchanged"
metrics:
  duration: "~13 minutes"
  completed: "2026-05-24T10:36:30Z"
  tasks_completed: 2
  files_modified: 8
requirements: [PROM-03, PROM-04, ELEC-03]
---

# Phase 05 Plan 01: Wave 0 Scaffold — promise_edits migration, schemas, and test stubs

## One-liner

Alembic migration for `promise_edits`/`promise_edit_election_links` tables, PromiseEdit/PromiseEditElectionLink ORM models importing shared ModerationStatus enum, four new Pydantic schemas (PromiseCreateIn, PromiseOut, PromiseEditIn, PromiseEditOut), 8 RED-state test stubs, python-slugify==8.0.4 in requirements.txt, and 5 Radix/cmdk packages in frontend package.json.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Alembic migration + ORM models | 0b0a770 | 20260524_000001_add_promise_edits.py, app/models/promise_edits.py, requirements.txt, Dockerfile |
| 2 | Pydantic schemas + frontend npm deps + RED test stubs | 2d43f7e | app/schemas/promises.py, tests/test_promises.py, frontend/package.json, package-lock.json |

## Verification Results

- `alembic upgrade head` → applied 20260524_000001 without "type already exists" error
- `promise_edits` and `promise_edit_election_links` tables confirmed in PostgreSQL
- `from app.models.promise_edits import PromiseEdit, PromiseEditElectionLink` → OK
- `from app.schemas.promises import PromiseCreateIn, PromiseOut, PromiseEditIn, PromiseEditOut` → OK
- `pytest tests/test_promises.py` → 5 passed, 9 skipped (8 RED stubs + 1 no-seed skip), 0 errors
- `grep "python-slugify==8.0.4" requirements.txt` → exits 0
- `grep "@radix-ui/react-popover" frontend/package.json` → exits 0

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] pgENUM(create_type=False) instead of sa.Enum(create_type=False)**
- **Found during:** Task 1 migration verification
- **Issue:** `sa.Enum` in SQLAlchemy 2.x does not expose a `create_type` attribute. When used inside `op.create_table`, SQLAlchemy's `_on_table_create` event fires and issues `CREATE TYPE moderation_status` even when `create_type=False` is passed as a kwarg — the kwarg is silently ignored.
- **Fix:** Replaced with `sqlalchemy.dialects.postgresql.ENUM("pending","approved","rejected", name="moderation_status", create_type=False)` which correctly suppresses the `CREATE TYPE` call.
- **Files modified:** `backend/alembic/versions/20260524_000001_add_promise_edits.py`
- **Commit:** 0b0a770

**2. [Rule 1 - Bug] Dockerfile --use-deprecated=legacy-resolver for pre-existing pip conflict**
- **Found during:** Task 1 migration verification (backend image rebuild)
- **Issue:** `fastapi-mail==1.6.4` declares `starlette>=1.0.0` as a dependency but the project uses `starlette 0.46.2` (via `fastapi==0.115.14`). The new pip resolver rejects this as a conflict, breaking `docker build`. The pre-existing production image was built 40 hours ago with a cached pip layer before the conflict manifested.
- **Fix:** Added `--use-deprecated=legacy-resolver` to the Dockerfile RUN pip command. This matches how the original image was built (legacy resolver ignores the starlette version declaration mismatch).
- **Files modified:** `backend/Dockerfile`
- **Commit:** 0b0a770

**3. [Rule 1 - Bug] RED test stubs use only `client` fixture (not future authenticated fixtures)**
- **Found during:** Task 2 test run
- **Issue:** The plan specified `test_create_promise(client, verified_user_client)` but `verified_user_client`, `unverified_user_client`, and `young_user_client` fixtures don't exist in conftest.py yet (they're Wave 1 fixtures). Pytest raised `ERROR` on fixture lookup failure instead of `SKIP`.
- **Fix:** Changed stub signatures to use only `client` fixture (which exists); added docstrings noting the missing fixtures will be added in Wave 1 plan 02. All 8 stubs now SKIP cleanly.
- **Files modified:** `backend/tests/test_promises.py`
- **Commit:** 2d43f7e

## Known Stubs

None — this plan only creates infrastructure (migration, models, schemas, test stubs). No user-facing components or placeholder UI text.

## Self-Check: PASSED

- `backend/alembic/versions/20260524_000001_add_promise_edits.py` → FOUND
- `backend/app/models/promise_edits.py` → FOUND
- `backend/app/schemas/promises.py` → FOUND (modified)
- `backend/tests/test_promises.py` → FOUND (modified)
- `backend/requirements.txt` → contains python-slugify==8.0.4 FOUND
- `frontend/package.json` → contains @radix-ui/react-popover FOUND
- Commit 0b0a770 → FOUND
- Commit 2d43f7e → FOUND
