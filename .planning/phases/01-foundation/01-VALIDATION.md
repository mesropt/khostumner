---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-21
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend) + vitest (frontend) |
| **Config file** | `backend/pyproject.toml` (pytest section) + `frontend/vitest.config.ts` — Wave 0 creates both |
| **Quick run command** | `cd backend && pytest tests/ -x --tb=short -q` |
| **Full suite command** | `cd backend && pytest tests/ && cd ../frontend && npm run test -- --run` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd backend && pytest tests/ -x --tb=short -q`
- **After every plan wave:** Run `cd backend && pytest tests/ && cd ../frontend && npm run test -- --run`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| SC-1: health | 01 | 1 | Infrastructure | — | GET /health returns 200 with JSON body | integration | `pytest tests/test_health.py -v` | ❌ W0 | ⬜ pending |
| SC-2: React shell | 01 | 2 | Infrastructure | — | App.tsx renders without errors | unit | `npm run test -- --run src/App.test.tsx` | ❌ W0 | ⬜ pending |
| SC-3: migrations | 01 | 1 | Infrastructure | — | All Alembic migrations apply from scratch, all tables exist | integration | `pytest tests/test_schema.py -v` | ❌ W0 | ⬜ pending |
| SC-4: seed data | 01 | 2 | Infrastructure | — | ≥3 politicians, ≥2 elections, ≥5 promises in DB | integration | `pytest tests/test_seed.py -v` | ❌ W0 | ⬜ pending |
| SC-5: CI | 01 | 3 | Infrastructure | — | GitHub Actions pipeline passes | manual | CI green badge | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/__init__.py` — empty package marker
- [ ] `backend/tests/conftest.py` — async database fixture using `asyncpg` + test DB URL
- [ ] `backend/tests/test_health.py` — `GET /health` returns 200, stub for SC-1
- [ ] `backend/tests/test_schema.py` — migration run + table existence check, stub for SC-3
- [ ] `backend/tests/test_seed.py` — count assertions for politicians/elections/promises, stub for SC-4
- [ ] `frontend/src/App.test.tsx` — renders without crashing, stub for SC-2
- [ ] `backend/pyproject.toml` pytest section — `asyncio_mode = "auto"`, `testpaths = ["tests"]`
- [ ] `frontend/vitest.config.ts` — `jsdom` environment, `@testing-library/react` setup

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Vite HMR works inside Docker | Infrastructure | Requires live browser interaction | Edit `frontend/src/App.tsx`, confirm hot reload in browser at `localhost:5173` |
| `docker-compose up` cold start | Infrastructure | Requires Docker daemon and full build | `docker-compose up --build`, wait for all 3 services healthy, visit `localhost:8000/health` and `localhost:5173` |
| CI pipeline green on fresh push | Infrastructure | Requires GitHub repo + Actions runner | Push to `main`, check GitHub Actions tab shows all jobs passing |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
