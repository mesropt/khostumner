---
phase: 05-promise-submission
verified: 2026-05-25T00:00:00Z
status: gaps_found
score: 3/4 roadmap success criteria verified
overrides_applied: 0
gaps:
  - truth: "POST /api/promises completes successfully without 500 error when politician_id is valid"
    status: failed
    reason: "politician_id FK is not validated before INSERT — PostgreSQL FK violation surfaces as unhandled IntegrityError → 500. The existing IntegrityError handler on the retry path does not discriminate by constraint name, so it will silently retry a non-slug violation and fail again with an unhandled exception."
    artifacts:
      - path: "backend/app/routers/promises.py"
        issue: "Lines 213-226: payload.politician_id written to Promise without SELECT-to-verify; lines 242-254: IntegrityError handler catches all violations without constraint discrimination"
    missing:
      - "Add politician existence check: SELECT Politician.id WHERE Politician.id == payload.politician_id LIMIT 1; raise 422 if None"
      - "Narrow IntegrityError catch to slug-uniqueness constraint only (check constraint name before retrying)"

  - truth: "Slug collision retry path produces correct promise row without data corruption"
    status: failed
    reason: "After rollback(), the Promise ORM object's state is expired. The retry block calls db.add(promise) on the stale expired object and adds PromiseElectionLink rows referencing the stale promise.id. In async-SQLAlchemy, accessing promise.id after rollback() may trigger a lazy-load that fails because the row no longer exists. Correct fix requires rebuilding the Promise object entirely after rollback."
    artifacts:
      - path: "backend/app/routers/promises.py"
        issue: "Lines 242-254: retry path reuses stale Promise object after db.rollback() instead of constructing a fresh one"
    missing:
      - "After db.rollback(), create a new Promise(...) object with the updated slug, add it, flush, then add fresh PromiseElectionLink rows"

  - truth: "account_age_days eligibility check cannot be bypassed by stale cached value"
    status: failed
    reason: "account_age_days is a cached integer column (CLAUDE.md Critical Pitfalls: vote brigading risk). A user who registers, waits 7 days without logging in again, retains account_age_days=0 and is incorrectly blocked. Conversely, an admin or bug can set account_age_days to any value, bypassing the gate entirely. CLAUDE.md explicitly flags this as a security concern."
    artifacts:
      - path: "backend/app/routers/promises.py"
        issue: "Lines 182-186 and 281-285: eligibility check reads user.account_age_days (cached) instead of computing from user.created_at"
      - path: "backend/app/auth/schemas.py"
        issue: "Line 11: account_age_days: int = 0 — documented as 'cached; recomputed on login'"
    missing:
      - "Replace user.account_age_days < 7 with: (datetime.now(timezone.utc) - user.created_at).days < 7 in both create_promise and edit_promise"

  - truth: "Core Phase 5 tests (PROM-03, PROM-04, ELEC-03) pass in the test suite"
    status: failed
    reason: "6 of the Phase 5 tests are permanently skipped via pytest.skip() calls. The verified_user_client fixture IS defined in the same test file (lines 21-76 per review), so the skip reason ('fixture needed') is no longer accurate. The primary deliverable tests are not being executed."
    artifacts:
      - path: "backend/tests/test_promises.py"
        issue: "test_create_promise, test_create_promise_unverified, test_create_promise_invalid_election, test_create_promise_with_elections, test_edit_promise_creates_edit_row — all unconditionally skipped with pytest.skip()"
    missing:
      - "Remove pytest.skip() calls from the 6 tests and wire them to use verified_user_client fixture"
      - "Ensure tests pass once CR-01, CR-04 are fixed"

  - truth: "PromiseEdit ORM model does not attempt to CREATE the moderation_status ENUM type when metadata.create_all() is called (test/CI paths)"
    status: failed
    reason: "PromiseEdit.moderation_status uses SAEnum(ModerationStatus, name='moderation_status') without create_type=False. SQLAlchemy will attempt CREATE TYPE moderation_status on metadata.create_all() paths, producing a DuplicateObject error in test environments that bypass Alembic. The migration correctly passes create_type=False via pgENUM, but the ORM model does not match."
    artifacts:
      - path: "backend/app/models/promise_edits.py"
        issue: "Line 39: SAEnum(ModerationStatus, name='moderation_status') missing create_type=False"
    missing:
      - "Change to SAEnum(ModerationStatus, name='moderation_status', create_type=False) matching evidence.py pattern"
human_verification:
  - test: "Navigate to /promises/new while unauthenticated"
    expected: "Redirected to /login page"
    why_human: "RequireAuth redirect behavior depends on runtime router state"
  - test: "Log in as eligible user (is_verified=true, account age >= 7 days), fill all required fields in /promises/new, submit"
    expected: "Redirected to /promises?submitted=1 with green success banner; promise row in DB with moderation_status=pending"
    why_human: "End-to-end form submit with real DB requires running application"
  - test: "Open a promise detail page while authenticated; verify edit link appears"
    expected: "Link labeled 'Խmbragrurel' appears below source buttons only for logged-in users"
    why_human: "Conditional rendering requires browser session state"
  - test: "Navigate to /promises/:slug/edit as eligible user; verify fields pre-fill from existing promise"
    expected: "title_hy, quote_hy, source_url, made_date, expected_date all pre-filled; politician shown as read-only text"
    why_human: "Pre-fill from usePromise data requires real API response"
  - test: "Submit edit on /promises/:slug/edit and verify original promise is unchanged"
    expected: "PUT returns 201; new row in promise_edits; live promise row title/quote unchanged"
    why_human: "Append-only behavior requires DB inspection"
  - test: "Verify Ներkayacnel nav link appears between Ընtrootsel and Mer massin in the header"
    expected: "Link present in correct position, visible to all users including unauthenticated"
    why_human: "Visual layout verification"
  - test: "Election toggle on submit form: check the checkbox, select a level, verify election checkboxes appear filtered by level"
    expected: "Only elections matching the selected level shown; unchecking toggle hides the picker"
    why_human: "Cascading UI state requires browser interaction"
---

# Phase 5: Promise Submission Verification Report

**Phase Goal:** Registered and verified users can submit new promises with required fields and source links, submit edits to existing promises, and link promises to elections — all entering an admin review queue.
**Verified:** 2026-05-25T00:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| SC1 | Logged-in user can submit a new promise with verbatim quote, source URL, promised date, and optional expected fulfillment date | ? UNCERTAIN | POST /api/promises endpoint exists and is substantive (lines 168-264, promises.py); PromiseSubmitPage.tsx has all required fields. BUT politician_id not validated (CR-01) and slug retry path is broken (CR-04) — happy-path works only if politician_id is valid and no slug collision occurs |
| SC2 | Submitted promise appears in the admin moderation queue rather than going live immediately | VERIFIED | Promise always created with moderation_status=ModerationStatus.pending (line 224); PromiseCreateIn has no moderation_status field (cannot be client-overridden) |
| SC3 | Logged-in user can submit an edit to an existing promise that enters the admin review queue | VERIFIED | PUT /api/promises/{slug} at lines 267-346 inserts PromiseEdit row with moderation_status=pending; live Promise row is never touched; PromiseEditPage.tsx calls apiClient.put() |
| SC4 | When submitting a promise, user can link it to one or more elections from a picker | VERIFIED | election_ids field in PromiseCreateIn and PromiseEditIn; cascading election picker (toggle → level RadioGroup → filtered Checkbox list) implemented in both PromiseSubmitPage.tsx and PromiseEditPage.tsx; PromiseElectionLink rows created in both endpoints |

**Score:** 3/4 roadmap success criteria verified (SC1 uncertain due to CR-01/CR-04 defects; SC2, SC3, SC4 verified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `backend/alembic/versions/20260524_000001_add_promise_edits.py` | Migration creating promise_edits and promise_edit_election_links tables | VERIFIED | File exists; creates both tables; uses pgENUM create_type=False correctly; down_revision="20260523_000001" |
| `backend/app/models/promise_edits.py` | PromiseEdit and PromiseEditElectionLink ORM models | PARTIAL | File exists with both models; imports ModerationStatus from app.models.promises (correct); BUT SAEnum missing create_type=False (CR-03) |
| `backend/app/schemas/promises.py` | PromiseCreateIn, PromiseOut, PromiseEditIn, PromiseEditOut schemas | VERIFIED | All 4 schemas present; PromiseCreateIn includes election_ids; PromiseEditIn excludes politician_id (correct per D-05) |
| `backend/app/routers/promises.py` | POST /api/promises and PUT /api/promises/{slug} endpoints | PARTIAL | Both endpoints exist and are substantive; eligibility guard, slug generation, election validation all present; BUT politician_id not validated (CR-01) and retry path broken (CR-04) |
| `backend/app/auth/schemas.py` | UserRead schema with account_age_days | VERIFIED | account_age_days: int = 0 present at line 11 |
| `frontend/src/api/client.ts` | post() and put() with CSRF + credentials | VERIFIED | getCsrfToken() exported; post() and put() both include credentials:"include" and x-csrftoken header |
| `frontend/src/contexts/AuthContext.tsx` | UserRead type with account_age_days: number | VERIFIED | account_age_days: number at line 18 |
| `frontend/src/hooks/usePoliticianSearch.ts` | Hook loading all politicians for combobox | VERIFIED | Fetches /api/politicians?page=1&per_page=100; returns { politicians, isLoading } |
| `frontend/src/hooks/useElectionsAll.ts` | Hook loading all elections for picker | VERIFIED | File confirmed exists per SUMMARY; strips promise_count |
| `frontend/src/components/ui/combobox.tsx` | Combobox component | VERIFIED | Exists; uses Popover + Command; exported as Combobox; imported in PromiseSubmitPage.tsx |
| `frontend/src/components/ui/checkbox.tsx` | Checkbox component | VERIFIED | Listed in SUMMARY created files; used in both form pages |
| `frontend/src/components/ui/radio-group.tsx` | RadioGroup component | VERIFIED | Listed in SUMMARY; used in both form pages |
| `frontend/src/components/ui/label.tsx` | Label component | VERIFIED | Listed in SUMMARY; used in both form pages |
| `frontend/src/pages/PromiseSubmitPage.tsx` | Full /promises/new page | VERIFIED | Exists; substantive (359 lines); two-section form; politician combobox; election picker; eligibility gate; apiClient.post() call; navigate to /promises?submitted=1 on success |
| `frontend/src/pages/PromiseEditPage.tsx` | /promises/:slug/edit page with pre-filled form | VERIFIED | Exists; substantive (401 lines); split component pattern; pre-fills from usePromise; read-only politician; apiClient.put() call |
| `frontend/src/App.tsx` | /promises/new and /promises/:slug/edit routes inside RequireAuth | VERIFIED | Both routes present inside RequireAuth wrapper (lines 44-47) |
| `frontend/src/components/Layout.tsx` | Nav link "Ներkayacnel" | VERIFIED | NavLink to="/promises/new" with label "Ներkayacnel" between Ընtrootsel and Mer massin (lines 49-51) |
| `frontend/src/pages/PromisesListPage.tsx` | ?submitted=1 success banner | VERIFIED | showBanner state initialized from searchParams.get("submitted") === "1" (line 28); green banner div with dismiss button present |
| `frontend/src/pages/PromiseDetailPage.tsx` | Edit link for authenticated users | VERIFIED | {state.user && <Link to="/promises/${data.slug}/edit">} conditional (lines 107-114); label "Խmbagrel" (Armenian) |
| `backend/requirements.txt` | python-slugify==8.0.4 | VERIFIED | Present at line 17 |
| `frontend/package.json` | 5 Radix/cmdk packages | VERIFIED | @radix-ui/react-checkbox, @radix-ui/react-label, @radix-ui/react-popover, @radix-ui/react-radio-group, cmdk all present |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `backend/app/routers/promises.py` | `backend/app/auth/users.py` | fastapi_users.current_user(active=True, verified=True) | VERIFIED | current_verified_user defined at line 30; used as Depends in both POST and PUT handlers |
| `backend/app/routers/promises.py` | `backend/app/models/promise_edits.py` | PromiseEdit INSERT | VERIFIED | PromiseEdit imported at line 14; instantiated and db.add(edit) at lines 313-325 |
| `backend/app/models/promise_edits.py` | `backend/app/models/promises.py` | ModerationStatus import | VERIFIED | from app.models.promises import ModerationStatus at line 18 |
| `backend/alembic/versions/20260524_000001_add_promise_edits.py` | `backend/alembic/versions/20260523_000001_auth_schema.py` | down_revision chain | VERIFIED | down_revision = "20260523_000001" at line 17 |
| `frontend/src/pages/PromiseSubmitPage.tsx` | `frontend/src/api/client.ts` | apiClient.post('/api/promises', payload) | VERIFIED | apiClient.post("/api/promises", payload) at line 116; response triggers navigate("/promises?submitted=1") |
| `frontend/src/pages/PromiseSubmitPage.tsx` | `frontend/src/contexts/AuthContext.tsx` | useAuth().state.user.account_age_days | VERIFIED | isEligible = !!user && user.is_verified && user.account_age_days >= 7 at line 56 |
| `frontend/src/App.tsx` | `frontend/src/components/RequireAuth.tsx` | PromiseSubmitPage wrapped in RequireAuth | VERIFIED | Route element={<RequireAuth />} wraps both /promises/new and /promises/:slug/edit (lines 44-47) |
| `frontend/src/pages/PromiseEditPage.tsx` | `frontend/src/api/client.ts` | apiClient.put('/api/promises/:slug', payload) | VERIFIED | apiClient.put(\`/api/promises/${slug}\`, payload) at line 114 of PromiseEditPage.tsx |
| `frontend/src/pages/PromiseDetailPage.tsx` | `frontend/src/pages/PromiseEditPage.tsx` | Link to /promises/:slug/edit | VERIFIED | Link to={\`/promises/${data.slug}/edit\`} at line 109 of PromiseDetailPage.tsx |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|-------------------|--------|
| `PromiseSubmitPage.tsx` | politicians (combobox items) | usePoliticianSearch → apiClient.get("/api/politicians?...") → GET /api/politicians route (DB query) | Yes — fetches real politicians paginated from DB | FLOWING |
| `PromiseSubmitPage.tsx` | elections (picker items) | useElectionsAll → apiClient.get("/api/elections?...") → GET /api/elections route (DB query) | Yes — fetches real elections from DB | FLOWING |
| `PromiseEditPage.tsx` | initialData (pre-fill) | usePromise(slug) → apiClient.get("/api/promises/:slug") → GET /api/promises/{slug} route (DB query) | Yes — loads real promise from DB; description_hy always null (WR-03, tracked) | FLOWING with gap: description_hy not populated |
| `backend/app/routers/promises.py` POST | promise insert | payload from PromiseCreateIn; moderation_status forced to pending; slug from slugify | Yes — inserts real row into promises table | FLOWING but broken on invalid politician_id |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| POST endpoint registered | `grep "router.post" backend/app/routers/promises.py` | `@router.post("", status_code=201, response_model=PromiseOut)` at line 168 | PASS |
| PUT endpoint registered | `grep "router.put" backend/app/routers/promises.py` | `@router.put("/{slug}", status_code=201, response_model=PromiseEditOut)` at line 267 | PASS |
| Eligibility guard in POST | `grep "account_age_days" backend/app/routers/promises.py` | Lines 182-186 and 281-285; both endpoints have the guard | PASS (but uses stale cache — CR-06) |
| Append-only: no UPDATE on live promise in PUT | `grep -n "UPDATE\|promise\.\(title\|quote\|slug\)" backend/app/routers/promises.py` | No UPDATE of live promise in edit_promise function | PASS |
| moderation_status forced to pending | `grep "ModerationStatus.pending" backend/app/routers/promises.py` | Lines 224 (create) and 319 (edit) — both force pending | PASS |
| Election link rows created | `grep "PromiseElectionLink\|PromiseEditElectionLink" backend/app/routers/promises.py` | Lines 233-236 (create) and 331-335 (edit) | PASS |
| Frontend build with TypeScript | npm run build (confirmed in SUMMARY 05-04, 05-05) | Exits 0 | PASS (from SUMMARY — not re-executed) |

### Probe Execution

No probe scripts declared in any PLAN file. Step 7c skipped.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|---------|
| PROM-03 | 05-01, 05-02, 05-03, 05-04 | Registered user can submit a new promise (verbatim quote + source URL required + promised date + optional expected fulfillment date) | PARTIAL | POST /api/promises exists with all required fields; PromiseSubmitPage.tsx has full form; BUT politician_id validation missing (CR-01) and retry path broken (CR-04) — core use case is structurally present but has production defects |
| PROM-04 | 05-01, 05-02, 05-03, 05-05 | Registered user can submit an edit to an existing promise (edit enters admin review queue) | VERIFIED | PUT /api/promises/{slug} is append-only (inserts PromiseEdit, never touches live Promise); PromiseEditPage.tsx pre-fills and submits correctly; edit enters moderation queue with pending status |
| ELEC-03 | 05-01, 05-02, 05-03, 05-04 | When submitting a promise, user can link it to one or more elections | VERIFIED | election_ids in PromiseCreateIn/PromiseEditIn; cascading election picker in both frontend pages; PromiseElectionLink rows created in both backend endpoints; election_ids validated before INSERT |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `backend/app/routers/promises.py` | 213-226 | politician_id written to DB without SELECT-to-verify | BLOCKER | FK violation → unhandled 500 response |
| `backend/app/routers/promises.py` | 242-254 | IntegrityError handler reuses stale ORM object after rollback | BLOCKER | Data corruption / unhandled exception on slug collision retry |
| `backend/app/routers/promises.py` | 182-186, 281-285 | account_age_days eligibility check reads stale cached column | BLOCKER | Security bypass possible; CLAUDE.md explicitly flags brigading risk |
| `backend/app/models/promise_edits.py` | 39 | SAEnum without create_type=False | BLOCKER | CREATE TYPE error on metadata.create_all() paths (test/CI) |
| `backend/tests/test_promises.py` | 210, 235, 282, 291, 300 | 6 Phase 5 tests unconditionally pytest.skip() | BLOCKER | Core PROM-03/PROM-04/ELEC-03 tests never execute |
| `backend/app/models/promise_edits.py` | 50 | default=datetime.utcnow (naive datetime, deprecated in Python 3.12) | WARNING | Timezone-unaware datetimes stored in timezone=True column |
| `frontend/src/pages/PromiseEditPage.tsx` | 396 | description_hy: null hardcoded — cannot pre-fill existing description | WARNING | Approved edits will silently erase existing descriptions |
| `frontend/src/api/client.ts` | 13-19 | get() missing credentials:"include" and inconsistent error shape | WARNING | Future authenticated GET endpoints will fail silently; error handling inconsistent with post/put |
| `frontend/src/pages/PromisesListPage.tsx` | 28 | submitted=1 URL param never removed — banner re-appears on refresh | INFO | Minor UX issue |

No TBD/FIXME/XXX debt markers found in phase-modified files.

### Human Verification Required

Seven items require human testing. The most critical ones (required to confirm PROM-03/PROM-04 end-to-end) are:

**1. End-to-end promise submission**

**Test:** Log in as eligible user (account >= 7 days, is_verified=true), fill all fields in /promises/new including a valid politician and optional election links, submit.
**Expected:** Redirect to /promises?submitted=1; green banner shown; new promise row in DB with moderation_status=pending; PromiseElectionLink rows created.
**Why human:** Requires running application with real DB to verify round-trip.

**2. Unauthenticated redirect**

**Test:** Visit /promises/new without being logged in.
**Expected:** Redirect to /login (RequireAuth enforces this).
**Why human:** React Router RequireAuth client-side redirect requires browser runtime.

**3. Eligibility gate display**

**Test:** Log in as ineligible user (account_age_days=0 or is_verified=false), navigate to /promises/new.
**Expected:** Submit button replaced by the Armenian eligibility gate message ("Ձedr haschivǝ petq e..."); form is otherwise visible and fillable.
**Why human:** Client-side conditional rendering based on user session state.

**4. Edit pre-fill accuracy**

**Test:** Open an existing promise detail page, click the edit link, inspect all form fields.
**Expected:** title_hy, quote_hy, source_url, made_date, expected_date pre-filled from promise data; politician shown as read-only text; description field is empty (known limitation per WR-03).
**Why human:** Pre-fill depends on real usePromise API response.

**5. Edit link visibility**

**Test:** View a promise detail page (a) without auth and (b) with auth.
**Expected:** (a) No edit link visible; (b) "Խmbagrel" link visible below source buttons.
**Why human:** Conditional render based on auth state requires browser session.

**6. Election picker cascading behavior**

**Test:** On /promises/new, check "Կapel yntrootoghinnerin" checkbox, then select each radio level.
**Expected:** Only elections matching the selected level appear as checkboxes; selecting no level shows "Yntreq makarad" prompt; unchecking the toggle hides the picker.
**Why human:** Cascading state machine requires browser interaction.

**7. Append-only edit verification**

**Test:** Submit an edit via /promises/:slug/edit, then visit the original /promises/:slug detail page.
**Expected:** Original promise still shows its original content; edit is in promise_edits table with pending status.
**Why human:** Requires DB inspection and browser navigation.

---

## Gaps Summary

Five blockers prevent the phase from being certified complete:

**Root cause 1 — Backend validation gap (CR-01):** `politician_id` is never checked for existence before writing to the database. Any invalid UUID will cause PostgreSQL to raise an FK violation that SQLAlchemy surfaces as an unhandled `IntegrityError` → HTTP 500. This breaks the core PROM-03 use case whenever a client sends a politician_id that does not exist in the politicians table.

**Root cause 2 — Slug collision retry corruption (CR-04):** The `IntegrityError` safety net in `create_promise` reuses a stale ORM object after `db.rollback()`. In async-SQLAlchemy, accessing attributes of an expired object after rollback triggers a lazy-load that fails. This means the one-in-a-million slug collision retry path will produce either a 500 or corrupted data.

**Root cause 3 — Stale eligibility cache (CR-06):** The account age check reads `user.account_age_days`, a cached integer that is only updated on login. This is flagged in CLAUDE.md as a critical security concern (vote brigading). A user who registers and doesn't log in again will be incorrectly blocked; conversely, an admin-set value can bypass the gate entirely. The fix is to compute age from `user.created_at` at request time.

**Root cause 4 — ORM type declaration (CR-03):** `SAEnum(ModerationStatus, name="moderation_status")` in `PromiseEdit` lacks `create_type=False`. On any code path that calls `metadata.create_all()` (test database creation, fresh CI environment not using Alembic), this will attempt `CREATE TYPE moderation_status` and fail with `DuplicateObject`.

**Root cause 5 — Tests never execute (IN-04):** Six of the tests directly covering PROM-03/PROM-04/ELEC-03 are unconditionally skipped via `pytest.skip()`. The `verified_user_client` fixture exists in the same file. These tests were created as RED stubs in plan 05-01 but never transitioned to GREEN state despite the plan explicitly requiring them to pass. The phase cannot be considered test-verified without these tests running.

CR-01, CR-04, and CR-06 are grouped: all three are in `backend/app/routers/promises.py`. A single focused fix to the two route handlers addresses all three.

---

_Verified: 2026-05-25T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
