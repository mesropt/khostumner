---
plan: 05-04
phase: 05-promise-submission
subsystem: ui
tags: [react, typescript, shadcn, combobox, election-picker, eligibility-gate, form, routing]

requires:
  - phase: 05-02
    provides: [POST /api/promises backend endpoint, account_age_days in UserRead]
  - phase: 05-03
    provides: [apiClient.post(), usePoliticianSearch, useElectionsAll, combobox.tsx, checkbox.tsx, radio-group.tsx, label.tsx, separator.tsx]
provides:
  - PromiseSubmitPage at /promises/new with two-section form
  - /promises/new route inside RequireAuth in App.tsx
  - Ներկայացնել nav link in Layout.tsx
  - Success banner on PromisesListPage for ?submitted=1
affects: [05-05]

tech-stack:
  added: []
  patterns:
    - "Two-section scrollable form: Ով (politician + election picker) / Ինչ+Երբ (content fields)"
    - "Eligibility gate: isEligible replaces submit button with inline p message (D-02)"
    - "Cascading election picker: toggle checkbox → level RadioGroup → elections Checkbox list"
    - "Client-side validation with fieldErrors Record<string, string> + inline p.text-red-600"
    - "POST /api/promises via apiClient.post() → navigate('/promises?submitted=1') on success"
    - "Success banner: useState(searchParams.get('submitted') === '1') initialized on mount"

key-files:
  created:
    - frontend/src/pages/PromiseSubmitPage.tsx
  modified:
    - frontend/src/App.tsx
    - frontend/src/components/Layout.tsx
    - frontend/src/pages/PromisesListPage.tsx

key-decisions:
  - "Election picker uses 'hidden' class (not conditional render) when toggle unchecked — preserves scroll per UI-SPEC.md"
  - "selectedLevel typed as ElectionLevel | '' for clean RadioGroup value management"
  - "filteredElections derived inline from elections.filter(e => e.level === selectedLevel)"
  - "showBanner state initialized from searchParams.get('submitted') === '1' on mount (not reactive to URL changes)"
  - "aria-label added to dismiss button for accessibility; section headings use aria-labelledby pattern"

duration: ~25min
completed: 2026-05-24T17:12:00Z
---

# Phase 05 Plan 04: PromiseSubmitPage + Success Banner Summary

**Two-section promise submission form at /promises/new with politician combobox, cascading election picker, eligibility gate, nav link, and success banner on redirect — completing the primary user-facing deliverable for PROM-03 and ELEC-03.**

## Performance

- **Duration:** ~25 minutes
- **Completed:** 2026-05-24T17:12:00Z
- **Tasks:** 3 (Task 1: implementation, Task 2: checkpoint auto-approved, Task 3: success banner)
- **Files modified:** 4 (1 created, 3 modified)

## Accomplishments

- PromiseSubmitPage.tsx created with two-section form (Ով / Ինչ+Երբ) using Card layout per UI-SPEC.md
- Section 1 (Ով): politician Combobox (required, client-side filtered) + optional election toggle with cascading RadioGroup level selector and Checkbox election list
- Section 2 (Ինչ+Երբ): title, verbatim quote, source URL (required), made_date, expected_date, description_hy (optional)
- Eligibility gate: ineligible users (unverified or account < 7 days) see D-02 message instead of submit button
- Client-side validation with Armenian inline error messages; API error handling for 403/422/network
- /promises/new route added inside RequireAuth in App.tsx — unauthenticated users redirected to /login
- Ներկայացնել nav link inserted between Ընտրություններ and Մեր մասին in Layout.tsx
- Success banner in PromisesListPage reads ?submitted=1 and shows dismissible green banner
- npm run build exits 0 with TypeScript clean

## Task Commits

1. **Task 1: PromiseSubmitPage + App.tsx route + Layout nav link** - `4759d0d` (feat)
2. **Task 2: checkpoint** - Auto-approved (human-verify, gate=blocking — bypassed per user auto-approval preference)
3. **Task 3: PromisesListPage success banner** - `671cd28` (feat)

## Files Created/Modified

- `frontend/src/pages/PromiseSubmitPage.tsx` — New: full /promises/new form with two sections, combobox, election picker, eligibility gate, form validation, API submit
- `frontend/src/App.tsx` — Added PromiseSubmitPage import + Route path="/promises/new" inside RequireAuth block
- `frontend/src/components/Layout.tsx` — Added NavLink to="/promises/new" with label "Ներկայացնել" between Ընտրություններ and Մեր մասին
- `frontend/src/pages/PromisesListPage.tsx` — Added useState showBanner + dismissible green banner above filter row

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] npm install required in worktree**
- **Found during:** Task 1 build verification
- **Issue:** Worktree's node_modules did not exist after reset to main. Build tool `tsc` not found.
- **Fix:** Ran `npm install --legacy-peer-deps` in the frontend directory.
- **Files modified:** None tracked (node_modules is .gitignored)
- **Verification:** npm run build exits 0 after install

No other deviations — plan executed exactly as written for all functional tasks.

## Known Stubs

None — all form fields wire to real data hooks and POST /api/promises. The eligibility gate is intentional UX, not a stub.

## Threat Flags

No new threat surface beyond the plan's declared threat model. RequireAuth redirect (T-05-11) is implemented; eligibility gate client-UX (T-05-12 accepted) present; no new endpoints or auth paths introduced.

## Self-Check: PASSED

- `frontend/src/pages/PromiseSubmitPage.tsx` — FOUND
- `frontend/src/App.tsx` contains `/promises/new` — FOUND
- `frontend/src/components/Layout.tsx` contains `Ներկայացնել` — FOUND
- `frontend/src/pages/PromisesListPage.tsx` contains `submitted` — FOUND
- Commit `4759d0d` — FOUND
- Commit `671cd28` — FOUND
- npm run build exits 0 — VERIFIED

---
*Phase: 05-promise-submission*
*Completed: 2026-05-24*
