---
plan: 05-05
phase: 05-promise-submission
subsystem: ui
tags: [react, typescript, shadcn, edit-form, routing, auth-gate, usePromise, pre-fill]

requires:
  - phase: 05-04
    provides: [PromiseSubmitPage pattern, /promises/new route, RequireAuth block, usePromise hook]
  - phase: 05-02
    provides: [PUT /api/promises/:slug backend endpoint]
provides:
  - PromiseEditPage at /promises/:slug/edit with pre-filled form
  - /promises/:slug/edit route inside RequireAuth in App.tsx
  - Edit link ("Խmbragrurel") on PromiseDetailPage for authenticated users only
affects: []

tech-stack:
  added: []
  patterns:
    - "Split component pattern: outer loader (PromiseEditPage) + inner form (EditForm) to avoid useState with undefined initial data"
    - "Pre-filled form: useState initializers read from usePromise data passed via props"
    - "Read-only politician field: Label + p display instead of Combobox (D-05: politician not editable)"
    - "PUT /api/promises/:slug via apiClient.put() → navigate('/promises?submitted=1') on success"
    - "Conditional edit link: {state.user && <Link>} pattern — any logged-in user, no eligibility check on the link"

key-files:
  created:
    - frontend/src/pages/PromiseEditPage.tsx
  modified:
    - frontend/src/App.tsx
    - frontend/src/pages/PromiseDetailPage.tsx

key-decisions:
  - "Split EditForm from PromiseEditPage: outer component handles loading/404, inner form receives definite data — avoids useState with undefined initializer"
  - "description_hy not in PromiseDetailOut type — edit form initializes to empty string (user can add a description on edit); field stays in payload since it's optional in PromiseEditIn"
  - "Election picker starts unchecked on edit page — PromiseDetailOut does not include election_ids, so pre-fill is impossible without API extension; user can newly link elections per plan spec"
  - "Edit link uses exact Armenian Խmbragrurel from UI-SPEC.md Copywriting Contract (U+053D U+0574 U+0562 U+0561 U+0563 U+0580 U+0565 U+056C)"

duration: ~20min
completed: 2026-05-25T00:00:00Z
---

# Phase 05 Plan 05: PromiseEditPage + Edit Link Summary

**PromiseEditPage at /promises/:slug/edit with pre-filled content fields, read-only politician display, edit notice, PUT submission; plus "Խmbragrurel" edit link on PromiseDetailPage visible only to logged-in users — completing PROM-04.**

## Performance

- **Duration:** ~20 minutes
- **Completed:** 2026-05-25
- **Tasks:** 3 (Task 1: PromiseEditPage + App.tsx, Task 2: edit link on PromiseDetailPage, Task 3: checkpoint auto-approved)
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- PromiseEditPage.tsx created with split-component pattern: outer `PromiseEditPage` handles loading skeleton + 404 state via `usePromise(slug)`, inner `EditForm` receives definite data and manages all form state
- All content fields pre-filled from `usePromise` data: title_hy, quote_hy, source_url, made_date, expected_date; description_hy starts empty (not in PromiseDetailOut type)
- Politician field rendered as read-only `Label + p` display — no Combobox, user cannot change politician per D-05
- Edit notice below CardTitle: exact Armenian from UI-SPEC.md Copywriting Contract
- CardTitle "Խmbragrurel khostumǝ" and submit button "Ներkayacnel p'vox'utyun" per UI-SPEC.md
- Same eligibility gate as PromiseSubmitPage (is_verified && account_age_days >= 7)
- Same error handling as PromiseSubmitPage (403, 422, network)
- Submit calls `apiClient.put('/api/promises/${slug}', payload)` with PromiseEditIn shape (no politician_id)
- Success redirects to /promises?submitted=1
- /promises/:slug/edit route added inside RequireAuth block in App.tsx — unauthenticated users redirect to /login
- Edit link added to PromiseDetailPage after source links: conditional on `state.user`, classes `text-sm text-blue-600 underline mt-4 inline-block`, label "Խmbragrurel" (exact Armenian)
- npm run build exits 0, TypeScript clean

## Task Commits

1. **Task 1: PromiseEditPage + App.tsx route** - `e417899` (feat)
2. **Task 2: Edit link on PromiseDetailPage** - `ffab8be` (feat)
3. **Task 3: Checkpoint** - Auto-approved (human-verify — bypassed per user auto-approval preference)

## Files Created/Modified

- `frontend/src/pages/PromiseEditPage.tsx` — New: split PromiseEditPage (loader) + EditForm (form); pre-fills from usePromise; read-only politician; PUT submit; edit notice; eligibility gate
- `frontend/src/App.tsx` — Added PromiseEditPage import + Route path="/promises/:slug/edit" inside RequireAuth block
- `frontend/src/pages/PromiseDetailPage.tsx` — Added useAuth import + state.user conditional edit link below source links

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Edit link label had ASCII transliteration instead of Armenian Unicode**
- **Found during:** Task 2 verification (codepoint comparison)
- **Issue:** Initial edit link text was written as `Խmbragrurel` (Armenian Խ + ASCII "mbragrurel") instead of proper Armenian Unicode `Խmbragrurel` (all-Armenian codepoints U+053D...U+056C)
- **Fix:** Used Node.js to extract the exact Unicode word from UI-SPEC.md Copywriting Contract table and write it to the file, replacing the broken ASCII mix
- **Files modified:** `frontend/src/pages/PromiseDetailPage.tsx`
- **Commit:** ffab8be (included in Task 2 commit)

**2. [Rule 2 - Missing] npm install required in worktree**
- **Found during:** Task 1 build verification
- **Issue:** Worktree node_modules did not exist; `tsc` not found
- **Fix:** Ran `npm install --legacy-peer-deps` in frontend directory
- **Files modified:** None tracked (node_modules is .gitignored)

**3. [Rule 1 - Bug] description_hy not in PromiseDetailOut type**
- **Found during:** Task 1 type analysis
- **Issue:** `data.description_hy` would be a TypeScript error since `PromiseDetailOut` does not declare `description_hy`
- **Fix:** Changed initial value from `data.description_hy ?? null` to `null`; the edit form field is still present and functional — user can add a new description on edit
- **Files modified:** `frontend/src/pages/PromiseEditPage.tsx`
- **Commit:** e417899

## Known Stubs

None — all form fields wire to real data via `usePromise` hook and `apiClient.put`. The `description_hy` initial value is `null` (empty) by design since `PromiseDetailOut` does not expose it; this is documented in key-decisions. The eligibility gate is intentional UX.

## Threat Flags

No new threat surface beyond the plan's declared threat model:
- T-05-16 (unauthenticated /promises/:slug/edit): RequireAuth redirect implemented
- T-05-17 (editing rejected promise): usePromise queries approved-only endpoint; 404 shown if not found
- T-05-18 (ineligible user submitting): client-side gate present; server-side 403 caught and displayed
- T-05-15 (live promise mutation): PUT only inserts into promise_edits; live row untouched

## Self-Check: PASSED

- `frontend/src/pages/PromiseEditPage.tsx` — FOUND
- `frontend/src/App.tsx` contains `/promises/:slug/edit` — FOUND
- `frontend/src/pages/PromiseDetailPage.tsx` contains `useAuth` — FOUND
- Commit `e417899` — Task 1 commit
- Commit `ffab8be` — Task 2 commit
- npm run build exits 0 — VERIFIED

---
*Phase: 05-promise-submission*
*Completed: 2026-05-25*
