---
phase: 04-authentication
plan: "04"
subsystem: frontend/auth-context
tags:
  - react-context
  - usereducer
  - jwt-cookies
  - protected-routes
  - tdd

dependency_graph:
  requires:
    - "04-02-SUMMARY.md (auth/ package — UserRead schema, JWT backends)"
    - "frontend/src/App.tsx (existing routes)"
    - "frontend/src/components/Layout.tsx (existing nav)"
  provides:
    - "frontend/src/contexts/AuthContext.tsx (AuthContext, AuthProvider, authReducer, UserRead)"
    - "frontend/src/hooks/useAuth.ts (useAuth hook)"
    - "frontend/src/components/RequireAuth.tsx (protected route wrapper)"
    - "frontend/src/App.tsx (AuthProvider + auth routes + RequireAuth group)"
    - "frontend/src/components/Layout.tsx (auth nav items)"
    - "frontend/src/pages/LoginPage.tsx (stub)"
    - "frontend/src/pages/RegisterPage.tsx (stub)"
    - "frontend/src/pages/VerifyEmailPage.tsx (stub)"
    - "frontend/src/pages/ResetPasswordPage.tsx (stub)"
  affects:
    - "04-05 (auth pages — LoginPage, RegisterPage, VerifyEmailPage, ResetPasswordPage real implementations)"

tech_stack:
  added: []
  patterns:
    - "React Context + useReducer for auth state — no external state library"
    - "Two-step rehydration: GET /me -> 401 -> POST /refresh -> retry /me (AUTH-05)"
    - "credentials: include on all auth fetch calls — browser sends httpOnly cookie"
    - "RequireAuth loading spinner prevents flash of redirect before auth state resolved"
    - "CSRF token extracted from document.cookie for logout POST (T-04-18)"

key_files:
  created:
    - frontend/src/contexts/AuthContext.tsx
    - frontend/src/contexts/AuthContext.test.tsx
    - frontend/src/hooks/useAuth.ts
    - frontend/src/components/RequireAuth.tsx
    - frontend/src/components/RequireAuth.test.tsx
    - frontend/src/pages/LoginPage.tsx
    - frontend/src/pages/RegisterPage.tsx
    - frontend/src/pages/VerifyEmailPage.tsx
    - frontend/src/pages/ResetPasswordPage.tsx
    - frontend/src/vite-env.d.ts
  modified:
    - frontend/src/App.tsx
    - frontend/src/components/Layout.tsx
    - frontend/src/components/PaginationControls.tsx

decisions:
  - "Two-step rehydration over single-step: GET /me first; on 401 attempt POST /refresh then retry /me — user with expired access but valid refresh token is silently rehydrated (AUTH-05)"
  - "authReducer exported from AuthContext.tsx for direct unit testing in test file"
  - "Loading spinner uses animate-pulse (zinc-200 rounded-full) instead of min-h-screen centering — plan specifies py-16 which is more appropriate than full viewport height"
  - "Stub page files (LoginPage, RegisterPage, etc.) use placeholder divs — real implementations in plan 04-05"

metrics:
  duration: "~5 minutes"
  completed_date: "2026-05-24"
  tasks_completed: 3
  files_changed: 13
---

# Phase 04 Plan 04: Frontend Auth Foundation Summary

**React Context + useReducer auth state with two-step JWT rehydration, RequireAuth protected route wrapper, and auth nav items wired into App.tsx and Layout.tsx.**

## Tasks Completed

| # | Task | Commit | Key Output |
|---|------|--------|-----------|
| 1 | Create AuthContext.tsx and useAuth.ts | c281a30 | AuthContext, authReducer, AuthProvider, useAuth — 7 tests pass |
| 2 | Create RequireAuth.tsx | f873221 | Protected route wrapper — 3 behavior tests pass |
| 3 | Update App.tsx and Layout.tsx | e08047f | AuthProvider wrapper, auth routes, nav auth items |

## What Was Built

### Task 1: AuthContext.tsx and useAuth.ts

`frontend/src/contexts/AuthContext.tsx` implements:
- `UserRead` type: `{ id, email, display_name, is_active, is_verified, role }`
- `AuthState`: `{ user: UserRead | null; isLoading: boolean }`
- `AuthAction` union: `SET_USER | CLEAR_USER | SET_LOADING`
- `authReducer`: pure function handling all three actions
- `AuthContext`: `createContext<{ state, dispatch } | null>(null)`
- `AuthProvider`: `useReducer` + `useEffect` for two-step rehydration on mount:
  - Step 1: `GET /api/users/me` with `credentials: "include"` — on 200 dispatch `SET_USER`
  - Step 2: On 401, `POST /api/auth/refresh` with `credentials: "include"` — if OK, retry `/me`; if retry OK, dispatch `SET_USER`
  - Step 3: Both fail → dispatch `CLEAR_USER`

`frontend/src/hooks/useAuth.ts` exports `useAuth()` which throws `"useAuth must be used within AuthProvider"` when used outside context.

Tests (7 passing): reducer unit tests (4) + AuthProvider mount behavior (3).

### Task 2: RequireAuth.tsx

`frontend/src/components/RequireAuth.tsx`:
- `isLoading=true` → renders loading spinner (`animate-pulse`, `py-16` centered)
- `user=null, isLoading=false` → `<Navigate to="/login" state={{ from: location }} replace />`
- `user set` → `<Outlet />`

Tests (3 passing): loading spinner, redirect to login, Outlet rendering.

### Task 3: App.tsx and Layout.tsx wiring

`frontend/src/App.tsx`:
- Entire `<Routes>` tree wrapped in `<AuthProvider>`
- Auth routes added inside `<Route element={<Layout />}>`: `/login`, `/register`, `/verify-email`, `/reset-password`
- Empty `<Route element={<RequireAuth />}>` group for Phase 5+ protected routes

`frontend/src/components/Layout.tsx`:
- `useAuth()` called; `state` and `dispatch` destructured
- Auth nav section added with `ml-auto flex items-center gap-4`:
  - When logged in: display_name span + Ելք button (logout with CSRF header)
  - When logged out: Մուտք NavLink

Stub pages created: `LoginPage.tsx`, `RegisterPage.tsx`, `VerifyEmailPage.tsx`, `ResetPasswordPage.tsx` — each returns `<div>X placeholder</div>`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added missing vite-env.d.ts to fix import.meta.env TypeScript error**

- **Found during:** Task 3 build verification
- **Issue:** `frontend/src/api/client.ts` (and our new `AuthContext.tsx`, `Layout.tsx`) used `import.meta.env.VITE_API_URL` which TypeScript rejected with `TS2339: Property 'env' does not exist on type 'ImportMeta'`. The `vite-env.d.ts` file (standard in Vite projects) was missing.
- **Fix:** Created `frontend/src/vite-env.d.ts` with `/// <reference types="vite/client" />`
- **Files modified:** `frontend/src/vite-env.d.ts` (created)
- **Commit:** e08047f

**2. [Rule 1 - Bug] Fixed unused searchParams destructuring in PaginationControls.tsx**

- **Found during:** Task 3 build verification
- **Issue:** `const [searchParams, setSearchParams] = useSearchParams()` — `searchParams` was declared but never read, causing `TS6133` error with `"noUnusedLocals": true`
- **Fix:** Changed to `const [, setSearchParams] = useSearchParams()`
- **Files modified:** `frontend/src/components/PaginationControls.tsx`
- **Commit:** e08047f (included with Task 3)

**3. [Rule 1 - Bug] Removed unused Outlet import from RequireAuth.test.tsx**

- **Found during:** Task 3 build verification
- **Issue:** RequireAuth.test.tsx imported `Outlet` from react-router-dom but didn't use it directly — `noUnusedLocals` caused `TS6133`
- **Fix:** Removed `Outlet` from the import destructure
- **Files modified:** `frontend/src/components/RequireAuth.test.tsx`
- **Commit:** e08047f (included with Task 3)

## Known Stubs

The following page files are intentional stubs, tracking for plan 04-05:

| File | Stub Type | Resolution |
|------|-----------|-----------|
| `frontend/src/pages/LoginPage.tsx` | Returns `<div>LoginPage placeholder</div>` | Real implementation in plan 04-05 |
| `frontend/src/pages/RegisterPage.tsx` | Returns `<div>RegisterPage placeholder</div>` | Real implementation in plan 04-05 |
| `frontend/src/pages/VerifyEmailPage.tsx` | Returns `<div>VerifyEmailPage placeholder</div>` | Real implementation in plan 04-05 |
| `frontend/src/pages/ResetPasswordPage.tsx` | Returns `<div>ResetPasswordPage placeholder</div>` | Real implementation in plan 04-05 |

These stubs are intentional scaffolding required for `App.tsx` to compile. The plan explicitly states these are placeholders for 04-05 implementations.

## Threat Flags

No new security surface beyond what the plan's threat model covers:
- T-04-17 (httpOnly cookie — JS never reads token value): mitigated by `credentials: "include"` pattern without JS token access
- T-04-18 (CSRF token for logout): mitigated by `document.cookie` CSRF read + `x-csrftoken` header in logout
- T-04-19 (RequireAuth flash): mitigated by loading spinner while `isLoading=true`

## Self-Check

- [x] `frontend/src/contexts/AuthContext.tsx` exists
- [x] `frontend/src/hooks/useAuth.ts` exists
- [x] `frontend/src/components/RequireAuth.tsx` exists
- [x] `frontend/src/pages/LoginPage.tsx` exists
- [x] `frontend/src/pages/RegisterPage.tsx` exists
- [x] `frontend/src/pages/VerifyEmailPage.tsx` exists
- [x] `frontend/src/pages/ResetPasswordPage.tsx` exists
- [x] Commit c281a30 exists (Task 1)
- [x] Commit f873221 exists (Task 2)
- [x] Commit e08047f exists (Task 3)
- [x] 10 tests pass (7 AuthContext + 3 RequireAuth)
- [x] npm run build exits 0
- [x] AuthProvider present in App.tsx
- [x] RequireAuth present in App.tsx
- [x] useAuth present in Layout.tsx

## Self-Check: PASSED
