---
phase: 2
slug: 02-politicians-parties-elections-browsing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (backend)** | pytest + pytest-asyncio + httpx |
| **Framework (frontend)** | vitest + @testing-library/react |
| **Config file (backend)** | `backend/pytest.ini` or `pyproject.toml` |
| **Quick run command** | `cd backend && pytest tests/test_politicians.py -x` |
| **Full suite command** | `cd backend && pytest && cd frontend && npm test -- --run` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command for the relevant test file
- **After every plan wave:** `cd backend && pytest && cd frontend && npm test -- --run`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| List politicians | backend | 1 | POLS-02 | — | N/A | integration | `pytest tests/test_politicians.py::test_list_politicians -x` | Wave 0 | ⬜ pending |
| Filter by party | backend | 1 | POLS-02 | — | N/A | integration | `pytest tests/test_politicians.py::test_filter_by_party -x` | Wave 0 | ⬜ pending |
| Filter by level | backend | 1 | POLS-02 | — | N/A | integration | `pytest tests/test_politicians.py::test_filter_by_level -x` | Wave 0 | ⬜ pending |
| Politician profile | backend | 1 | POLS-01 | — | N/A | integration | `pytest tests/test_politicians.py::test_get_politician_by_slug -x` | Wave 0 | ⬜ pending |
| Politician 404 | backend | 1 | POLS-01 | — | N/A | integration | `pytest tests/test_politicians.py::test_politician_not_found -x` | Wave 0 | ⬜ pending |
| Party detail | backend | 1 | POLS-03 | — | N/A | integration | `pytest tests/test_parties.py::test_get_party -x` | Wave 0 | ⬜ pending |
| Elections list | backend | 1 | ELEC-01 | — | N/A | integration | `pytest tests/test_elections.py::test_list_elections -x` | Wave 0 | ⬜ pending |
| Election detail | backend | 1 | ELEC-02 | — | N/A | integration | `pytest tests/test_elections.py::test_get_election -x` | Wave 0 | ⬜ pending |
| Election promises | backend | 1 | ELEC-02 | — | N/A | integration | `pytest tests/test_elections.py::test_election_promises -x` | Wave 0 | ⬜ pending |
| PersonsPage render | frontend | 2 | POLS-02 | — | N/A | component | `cd frontend && npm test -- --run` | Wave 0 | ⬜ pending |
| PoliticianProfilePage render | frontend | 2 | POLS-01 | — | N/A | component | `cd frontend && npm test -- --run` | Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_politicians.py` — stubs for POLS-01, POLS-02
- [ ] `backend/tests/test_parties.py` — stub for POLS-03
- [ ] `backend/tests/test_elections.py` — stubs for ELEC-01, ELEC-02
- [ ] `frontend/src/pages/PersonsPage.test.tsx` — smoke render test for POLS-02

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Nav links render stubs for unbuilt phases | D-02 | Visual inspection required | Open app, verify header shows all 5 nav links; click Կատարված/Չկատարված and confirm NotFoundPage renders |
| Photo fallback avatar shows initials | D-Claude | Visual inspection required | Open /persons page with seed politicians lacking photos; verify initials avatar displayed |
| Pagination works correctly at page boundaries | D-09 | Full seed data required | Navigate to last page, verify prev/next buttons disabled correctly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
