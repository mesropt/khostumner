---
phase: 05-promise-submission
plan: 03
subsystem: ui
tags: [react, typescript, shadcn, tanstack-query, combobox, csrf, radix-ui, cmdk]

requires:
  - phase: 05-01
    provides: [Radix/cmdk packages in package.json, PromiseCreateIn/PromiseEditIn schemas]
provides:
  - apiClient.post() and apiClient.put() with credentials:include and CSRF header
  - getCsrfToken() exported from frontend/src/api/client.ts
  - UserRead.account_age_days field in AuthContext.tsx
  - usePoliticianSearch hook (loads all politicians for client-side filter)
  - useElectionsAll hook (loads all elections for client-side level filter)
  - combobox.tsx (Popover + Command controlled generic combobox)
  - command.tsx, checkbox.tsx, radio-group.tsx, label.tsx, dialog.tsx, popover.tsx (shadcn)
affects: [05-04, 05-05]

tech-stack:
  added: []
  patterns:
    - "apiClient.post/put with credentials:include + x-csrftoken header via getCsrfToken()"
    - "usePoliticianSearch: staleTime=5min, per_page=100, client-side filter"
    - "useElectionsAll: strips promise_count from ElectionWithCountOut, returns plain ElectionOut[]"
    - "Combobox: generic controlled component with items/value/onChange props using Popover+Command"

key-files:
  created:
    - frontend/src/components/ui/combobox.tsx
    - frontend/src/components/ui/command.tsx
    - frontend/src/components/ui/checkbox.tsx
    - frontend/src/components/ui/radio-group.tsx
    - frontend/src/components/ui/label.tsx
    - frontend/src/components/ui/dialog.tsx
    - frontend/src/components/ui/popover.tsx
    - frontend/src/hooks/usePoliticianSearch.ts
    - frontend/src/hooks/useElectionsAll.ts
  modified:
    - frontend/src/api/client.ts
    - frontend/src/contexts/AuthContext.tsx
    - frontend/src/components/RequireAuth.test.tsx
    - frontend/src/contexts/AuthContext.test.tsx
    - frontend/package.json
    - frontend/package-lock.json

key-decisions:
  - "getCsrfToken() exported from client.ts (not moved from LoginPage.tsx — both files have it; plan says keeping in both is acceptable)"
  - "Combobox uses items.value for identity but CommandItem value=label for cmdk search filtering"
  - "useElectionsAll strips promise_count via destructuring — consumers only get ElectionOut fields"
  - "popover.tsx added via shadcn CLI (dependency of combobox.tsx); not in original plan task list but necessary"
  - "dialog.tsx generated as shadcn dependency of command.tsx; committed alongside command.tsx"
  - "npm install run in worktree to materialize packages from package.json added in plan 05-01"

patterns-established:
  - "Post/put mutation pattern: apiClient.post(path, body) throws { status, detail } object on non-ok"
  - "Combobox selection toggle: clicking selected item deselects (value === item.value ? '' : item.value)"
  - "staleTime: 5min on all-items hooks (politician/election lists change rarely)"

requirements-completed: [PROM-03, PROM-04, ELEC-03]

duration: ~18min
completed: 2026-05-24
---

# Phase 05 Plan 03: Wave 1b Frontend Infrastructure Summary

**Extended apiClient with post/put+CSRF methods, added account_age_days to UserRead, created usePoliticianSearch/useElectionsAll hooks, and generated 7 shadcn UI components (combobox, command, checkbox, radio-group, label, dialog, popover) required by Phase 5 form pages.**

## Performance

- **Duration:** ~18 minutes
- **Started:** 2026-05-24T10:30:00Z
- **Completed:** 2026-05-24T10:48:13Z
- **Tasks:** 2
- **Files modified:** 16 (9 created, 7 modified)

## Accomplishments

- apiClient now supports post() and put() methods with CSRF double-submit pattern and credentials:include — satisfying threat mitigations T-05-09 and T-05-10
- UserRead TypeScript type includes account_age_days: number, enabling client-side eligibility check (CONTEXT.md D-01/D-02)
- usePoliticianSearch and useElectionsAll hooks ready for PromiseSubmitPage consumption; both use staleTime=5min and load full list (per_page=100) for client-side filtering
- Combobox component built on shadcn Popover + Command with full keyboard navigation, Armenian placeholder text, and Check icon on selected item
- All 7 new UI component files in frontend/src/components/ui/ — TypeScript clean, npm run build exits 0

## Task Commits

1. **Task 1: Extend apiClient + update UserRead + generate shadcn components** - `7cbe1ee` (feat)
2. **Task 2: usePoliticianSearch + useElectionsAll + combobox.tsx** - `89497bf` (feat)

## Files Created/Modified

- `frontend/src/api/client.ts` — Added getCsrfToken(), post<T>(), put<T>() with CSRF + credentials
- `frontend/src/contexts/AuthContext.tsx` — Added account_age_days: number to UserRead type
- `frontend/src/hooks/usePoliticianSearch.ts` — New hook: loads all politicians for client-side combobox filter
- `frontend/src/hooks/useElectionsAll.ts` — New hook: loads all elections, strips promise_count
- `frontend/src/components/ui/combobox.tsx` — Generic controlled Combobox (Popover + Command)
- `frontend/src/components/ui/command.tsx` — shadcn Command primitive (wraps cmdk)
- `frontend/src/components/ui/checkbox.tsx` — shadcn Checkbox
- `frontend/src/components/ui/radio-group.tsx` — shadcn RadioGroup
- `frontend/src/components/ui/label.tsx` — shadcn Label
- `frontend/src/components/ui/dialog.tsx` — shadcn Dialog (dependency of command.tsx)
- `frontend/src/components/ui/popover.tsx` — shadcn Popover (dependency of combobox.tsx; added via CLI)
- `frontend/src/components/RequireAuth.test.tsx` — Added account_age_days: 0 to mockUser
- `frontend/src/contexts/AuthContext.test.tsx` — Added account_age_days: 0 to mockUser
- `frontend/package.json` / `package-lock.json` — npm install run to materialize packages from 05-01

## Decisions Made

- getCsrfToken() is defined in both client.ts (exported) and LoginPage.tsx — plan explicitly said "keeping it in both is acceptable for Phase 5". No breakage.
- popover.tsx added via shadcn CLI as a necessity for combobox.tsx; not explicitly listed in plan Task 2 but required per the Combobox architecture.
- dialog.tsx was generated as a shadcn dependency of command.tsx (shadcn CLI included it automatically).
- Combobox uses `value={item.label}` on CommandItem so cmdk can filter by the displayed Armenian text; identity is tracked via the `value` prop comparing to `item.value`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed TypeScript build error in RequireAuth.test.tsx and AuthContext.test.tsx**
- **Found during:** Task 1 build verification
- **Issue:** Adding `account_age_days: number` (required field) to UserRead broke both test files that construct mock UserRead objects without the new field. TypeScript raised TS2741 errors.
- **Fix:** Added `account_age_days: 0` to both `mockUser` objects in the test files.
- **Files modified:** `frontend/src/components/RequireAuth.test.tsx`, `frontend/src/contexts/AuthContext.test.tsx`
- **Verification:** `npm run build` exits 0 after fix
- **Committed in:** 7cbe1ee (Task 1 commit)

**2. [Rule 3 - Blocking] npm install required in worktree**
- **Found during:** Task 1 shadcn CLI execution
- **Issue:** Worktree's node_modules did not have the Radix/cmdk packages that plan 05-01 added to package.json. The worktree was created from commit d74f2cd (before Wave 1) and its node_modules was not updated when the worktree was reset to 66d9e76.
- **Fix:** Ran `npm install --legacy-peer-deps` in the frontend directory to install all packages.
- **Files modified:** `frontend/package-lock.json` (already tracked)
- **Verification:** Shadcn CLI ran successfully after install
- **Committed in:** 7cbe1ee (Task 1 commit, package-lock.json included)

**3. [Rule 3 - Blocking] popover.tsx required for combobox.tsx but not listed in plan**
- **Found during:** Task 2 combobox.tsx creation
- **Issue:** combobox.tsx imports from `@/components/ui/popover` which did not exist (plan listed combobox but not popover as a deliverable).
- **Fix:** Added `popover.tsx` via `npx shadcn@latest add popover --yes`.
- **Files modified:** `frontend/src/components/ui/popover.tsx` (created)
- **Verification:** npm run build exits 0 after adding popover.tsx
- **Committed in:** 89497bf (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (1 Rule 1 bug, 2 Rule 3 blocking)
**Impact on plan:** All auto-fixes were necessary for correctness or build success. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- PromiseSubmitPage (plan 05-04) can import apiClient.post(), useAuth().state.user.account_age_days, usePoliticianSearch, useElectionsAll, and Combobox/Checkbox/RadioGroup/Label components
- PromiseEditPage (plan 05-05) can similarly import all needed primitives
- npm run build exits 0 with TypeScript clean

## Known Stubs

None — this plan creates infrastructure primitives only. No user-facing content or placeholder UI.

## Threat Flags

No new threat surface beyond what was already declared in the plan's threat model (T-05-09, T-05-10 — both mitigated by getCsrfToken() in post/put methods).

## Self-Check: PASSED

- `frontend/src/api/client.ts` exports getCsrfToken and apiClient.post/put — FOUND
- `frontend/src/contexts/AuthContext.tsx` contains account_age_days — FOUND
- `frontend/src/components/ui/combobox.tsx` — FOUND
- `frontend/src/components/ui/command.tsx` — FOUND
- `frontend/src/components/ui/checkbox.tsx` — FOUND
- `frontend/src/components/ui/radio-group.tsx` — FOUND
- `frontend/src/components/ui/label.tsx` — FOUND
- `frontend/src/hooks/usePoliticianSearch.ts` — FOUND
- `frontend/src/hooks/useElectionsAll.ts` — FOUND
- Commit 7cbe1ee — FOUND
- Commit 89497bf — FOUND

---
*Phase: 05-promise-submission*
*Completed: 2026-05-24*
