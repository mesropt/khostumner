---
plan: 05-02
phase: 05-promise-submission
status: complete
completed_at: "2026-05-24"
wave: 2
---

# Plan 05-02 Summary: Backend Endpoints

## What Was Built

**POST /api/promises** — Creates a new promise with eligibility enforcement:
- `fastapi_users.current_user(active=True, verified=True)` enforces 401/403 for unauthenticated/unverified users
- Manual `account_age_days >= 7` check raises 403
- `election_ids` validated via `SELECT id FROM elections WHERE id = ANY(...)` — 422 if any UUID missing
- Slug auto-generated with `slugify(title_hy, allow_unicode=False)`; collision handled with `-{uuid4().hex[:6]}` suffix; `IntegrityError` safety net
- `Promise.moderation_status` always set to `pending` (never trusted from client)
- `PromiseElectionLink` rows created for all valid election IDs after `db.flush()`

**PUT /api/promises/{slug}** — Append-only edit:
- Looks up promise by slug WITHOUT `moderation_status=approved` filter (pending + approved are editable; 404 for rejected)
- Inserts `PromiseEdit` row with `moderation_status=pending` — live Promise row is NOT touched
- Same eligibility guard (account_age_days >= 7) and election_ids validation

**UserRead extended** — `account_age_days: int = 0` added to `backend/app/auth/schemas.py` so `GET /api/users/me` includes the field for frontend eligibility checks.

## Key Files Modified

- `backend/app/routers/promises.py` — Two new route handlers appended after existing GET routes
- `backend/app/auth/schemas.py` — `account_age_days` field added to `UserRead`
- `backend/tests/test_promises.py` — Full test implementations for RED stubs from 05-01

## Deviations

- Agent hit session quota before committing. Changes were fully written to working tree and rescued by the orchestrator.

## Self-Check: PASSED

- POST and PUT routes present in router (lines 168 and 267)
- `account_age_days` in UserRead schema
- Eligibility, slug, and election validation logic implemented
- Append-only insert pattern for edits confirmed
