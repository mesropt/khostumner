---
phase: 4
slug: authentication
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-24
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio (backend), vitest (frontend) |
| **Config file** | `backend/pyproject.toml` — `asyncio_mode = "auto"` |
| **Quick run command** | `pytest tests/test_auth.py -x` |
| **Full suite command** | `pytest tests/ -x` |
| **Frontend quick run** | `npm run test -- --run src/contexts/AuthContext.test.tsx` |
| **Frontend full run** | `npm run test -- --run` |
| **Estimated runtime** | ~30 seconds (backend), ~10 seconds (frontend) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_auth.py -x`
- **After every plan wave:** Run `pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green; `npm run build` exits 0
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | AUTH-01,02,03,05 | T-04-01 | Schema conflict resolved before auth code loads | integration | `pytest tests/test_auth.py -x -k "test_me_unauthenticated"` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | AUTH-01,02,03,04,05 | — | All 6 new packages install without conflict | smoke | `pip install fastapi-users[sqlalchemy]==15.0.5 fastapi-mail==1.6.4 starlette-csrf==3.0.0; python -c "import fastapi_users"` | ❌ W0 | ⬜ pending |
| 04-01-03 | 01 | 1 | AUTH-01,02,03,05 | — | RED stubs collected without import errors | unit | `pytest tests/test_auth.py --co -q` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | AUTH-01,02,03,04,05 | T-04-01,02 | User model loads from SQLAlchemyBaseUserTableUUID | smoke | `python -c "from app.models.users import User, OAuthAccount; print('ok')"` | ✅ | ⬜ pending |
| 04-02-02 | 02 | 2 | AUTH-01,02,03 | T-04-09 | auth/ package importable; fastapi_users instance exported | smoke | `python -c "from app.auth.users import fastapi_users; print('ok')"` | ❌ W0 | ⬜ pending |
| 04-02-03 | 02 | 2 | AUTH-01,02 | T-04-12 | Email sending does not raise (mock SMTP) | unit | `pytest tests/test_auth.py -x -k "test_request_verify"` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 3 | AUTH-01,02,03,05 | T-04-01 | POST /api/auth/register returns 201 | integration | `pytest tests/test_auth.py -x -k "test_register_success"` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 3 | AUTH-05 | T-04-17 | GET /api/users/me returns 401 without cookie | integration | `pytest tests/test_auth.py -x -k "test_me_unauthenticated"` | ❌ W0 | ⬜ pending |
| 04-03-03 | 03 | 3 | AUTH-04 | T-04-14 | Mailhog container starts and accepts SMTP on port 1025 | smoke | `docker compose ps mailhog` | ✅ | ⬜ pending |
| 04-04-01 | 04 | 3 | AUTH-05 | T-04-17 | AuthContext initial state is { user: null, isLoading: true } | unit | `npm run test -- --run src/contexts/AuthContext.test.tsx` | ❌ W0 | ⬜ pending |
| 04-04-02 | 04 | 3 | AUTH-05 | T-04-19 | RequireAuth redirects to /login when user=null | unit | `npm run test -- --run src/components/RequireAuth.test.tsx` | ❌ W0 | ⬜ pending |
| 04-04-03 | 04 | 3 | AUTH-05 | — | App builds with AuthProvider wrapper | smoke | `npm run build` | ✅ | ⬜ pending |
| 04-05-01 | 05 | 4 | AUTH-01 | T-04-21 | Login form POSTs URLSearchParams with username field | unit | `npm run test -- --run src/pages/LoginPage.test.tsx` | ❌ W0 | ⬜ pending |
| 04-05-02 | 05 | 4 | AUTH-01,02,03,05 | T-04-20 | All backend AUTH tests pass (no xfail) | integration | `pytest tests/test_auth.py -x` | ❌ W0 | ⬜ pending |
| 04-06-01 | 06 | 5 | AUTH-04 | T-04-23,24,25 | OAuth authorize returns 302 to Google (manual verify) | manual | Visit http://localhost:8000/api/auth/google/authorize | N/A | ⬜ pending |
| 04-06-02 | 06 | 5 | AUTH-01..05 | — | Full test suite green | integration | `pytest tests/ -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_auth.py` — RED stubs for AUTH-01 through AUTH-05 (all 9 tests as xfail stubs)
- [ ] `frontend/src/contexts/AuthContext.test.tsx` — authReducer unit tests + AuthProvider mount behavior
- [ ] `frontend/src/components/RequireAuth.test.tsx` — placeholder (fleshed out in 04-04 Task 2)
- [ ] `frontend/src/pages/LoginPage.test.tsx` — 3 behavior tests for login form

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Google OAuth authorize redirect | AUTH-04 | Requires real Google OAuth credentials (dev console app) | After setting GOOGLE_CLIENT_ID in env: visit http://localhost:8000/api/auth/google/authorize — expect redirect to accounts.google.com |
| Facebook OAuth authorize redirect | AUTH-04 | Requires real Facebook OAuth credentials (dev console app) | After setting FACEBOOK_CLIENT_ID in env: visit http://localhost:8000/api/auth/facebook/authorize — expect redirect to facebook.com |
| Email verification email received | AUTH-02 | Requires visual inspection of Mailhog UI | Register user → open http://localhost:8025 → confirm verification email received with correct token URL |
| Password reset email received | AUTH-03 | Requires visual inspection of Mailhog UI | Request password reset → open http://localhost:8025 → confirm reset email with token URL |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING (❌) references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
