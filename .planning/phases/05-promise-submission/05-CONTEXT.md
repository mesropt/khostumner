# Phase 5: Promise Submission - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 5 delivers the promise submission pipeline for registered users:
- Authenticated and eligible users (email verified, account ≥7 days old) can submit new promises with verbatim quote, source URL, politician link, dates, and optional election links
- Authenticated eligible users can submit edits to existing approved promises — edits are stored as a full snapshot in a separate `promise_edits` table and await admin review
- Submitted promises enter the admin moderation queue (moderation_status=pending) and are NOT immediately visible site-wide
- A nav-accessible submission form at `/promises/new` with two visual sections and an eligibility gate

No admin review UI, no voting, no promise approval — those are Phases 6 and 7.
</domain>

<decisions>
## Implementation Decisions

### Submission Eligibility Guard
- **D-01:** Submitting a new promise requires: authenticated + email verified (`is_verified=True`) + account age ≥ 7 days (`account_age_days >= 7`). This matches CLAUDE.md's referenced "7 days" threshold for vote brigading protection, applied equally to submissions to prevent coordinated fake entries.
- **D-02:** When a logged-in user opens the form but is not yet eligible, the form renders normally (all fields visible) but the submit button is replaced with an inline explanation message: "Ձեր հաշիվը պետք է ունենա նվազագույնը 7 օրվա վաղեմություն և հաստատված էլ. հասցե՝ խոստում ներկայացնելու համար" (Your account must be at least 7 days old and email-verified to submit a promise). No redirect; no hiding the form.
- **D-03:** Unauthenticated visitors who click the nav link are redirected to `/login` via the existing `RequireAuth` component.

### Promise Edit Model
- **D-04:** Promise edits are stored in a new **`promise_edits` table** — a full snapshot of all editable fields, not a delta/patch. The live approved promise is NEVER touched until an admin approves the edit in Phase 6.
- **D-05:** Editable fields (all content fields): `title_hy`, `quote_hy`, `description_hy`, `source_url`, `made_date`, `expected_date`, and election links. Each edit row stores: `promise_id` (FK to the original), `submitted_by`, `moderation_status` (pending/approved/rejected), snapshot of all editable fields, `created_at`.
- **D-06:** The `promise_edits` table is **append-only** — rows are never deleted. Admin approval in Phase 6 marks the edit row `approved` and applies the snapshot to the live promise. All prior edit rows remain, giving a full audit trail (fulfills PROM-06 in Phase 6).
- **D-07:** Edit submission requires the same eligibility as new submission: logged in + verified + ≥7 days.

### Form Design
- **D-08:** The submission form lives at `/promises/new` as a dedicated page (not a modal). Protected by `RequireAuth` — unauthenticated users are redirected to `/login`.
- **D-09:** The form has **two visual sections on one scrollable page** (no stepper, no Back/Next navigation):
  - **Section 1 — Ով (Who):** Politician searchable autocomplete (required) + optional election toggle
  - **Section 2 — Ինչ (What) + Երբ (When):** Title, verbatim quote, source URL (all required), made_date, expected_date (optional), description_hy (optional)
  - One submit button at the bottom; if ineligible, it is replaced with the eligibility gate message (D-02).
- **D-10:** A **"Ներկայացնել խոստում" (Submit a promise)** nav link is added to the Layout header, always visible to all visitors. Clicking while logged out → redirected to `/login`; logged in but ineligible → form with inline message; eligible → full form with submit button.

### Politician Picker
- **D-11:** Politician selection uses a **searchable autocomplete combobox** — the existing shadcn Combobox component (built on Popover + Command). Typing triggers a debounced call to `GET /api/politicians?search=<query>` (or client-side filter if the full list is loaded on mount). Returns politician name_hy + id.
- **D-12:** Politician field is required — form cannot be submitted without selecting a politician.

### Election Picker (ELEC-03)
- **D-13:** Election linking is **optional**, hidden behind a checkbox toggle: "Կապել ընտրություններին" (Link to elections). When unchecked, no elections are linked.
- **D-14:** When the toggle is checked, a **cascading picker** appears:
  - **Level selection:** Radio buttons for election level (Ազգային / Տեղական / Հանրաքվե — maps to `ElectionLevel.national`, `local`, `referendum`). Default: no level selected.
  - **Election selection:** After a level is chosen, a checkbox list of elections filtered by that level appears. Multiple elections can be checked.
- **D-15:** The election level and elections data is fetched from the existing `GET /api/elections` endpoint, client-side filtered by level after fetch (election list is small, ≤20 items in v1).

### Claude's Discretion
- Slug generation for new promises: backend auto-generates from `title_hy` using Armenian-to-ASCII transliteration (e.g., unicode slugify library). The user never sees or edits the slug in the form.
- Form validation: client-side validation (required fields highlighted) + server-side 422 errors displayed inline below affected fields.
- After successful submission: redirect to `/promises` list with a success toast: "Ձեր խոստումը ներկայացված է: Այն կհրապարակվի ստուգումից հետո" (Your promise has been submitted. It will be published after review).
- The `promise_edits` table needs a new Alembic migration — it does not yet exist in the schema.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 5 requirements: PROM-03, PROM-04, ELEC-03
- `.planning/ROADMAP.md` §Phase 5 — goal, success criteria (4 items), phase dependencies

### Data Model
- `backend/app/models/promises.py` — `Promise` model (all fields), `PromiseElectionLink` M2M table, `ModerationStatus` and `ResolvedStatus` enums
- `backend/app/models/elections.py` — `Election` model with `ElectionLevel` enum (national/local/referendum) — used for cascading picker
- `backend/app/models/users.py` — `User` model with `is_verified`, `account_age_days` fields (eligibility check)
- `backend/app/schemas/promises.py` — existing `PromiseStubOut`, `PromiseListOut`, `PromiseDetailOut` — Phase 5 adds `PromiseCreateIn`, `PromiseEditIn`, `PromiseEditOut`
- `backend/app/schemas/common.py` — `PaginatedResponse[T]` — MUST be used for any new list endpoints

### Auth & Routing
- `.planning/phases/04-authentication/04-CONTEXT.md` — D-03 (httpOnly JWT cookies), D-04 (access + refresh pair), D-05 (CSRF double-submit), D-06 (Google + Facebook OAuth)
- `backend/app/auth/users.py` — `UserManager` with `on_after_login` hook (account_age_days updated on login)
- `frontend/src/App.tsx` — route registry; Phase 5 adds `/promises/new` and `/promises/:slug/edit` inside `<RequireAuth>`
- `frontend/src/components/RequireAuth.tsx` — existing auth guard component

### Existing Endpoints
- `backend/app/routers/promises.py` — existing `GET /api/promises` and `GET /api/promises/{slug}` — Phase 5 adds `POST /api/promises` and `PUT /api/promises/{slug}`
- `backend/app/routers/elections.py` — existing `GET /api/elections` — reused for election picker data fetch

### Frontend Patterns
- `frontend/src/pages/LoginPage.tsx` — form pattern: Card + Input + Button + error state + CSRF header
- `frontend/src/contexts/AuthContext.tsx` — `useAuth()` hook for current user + eligibility check

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/ui/card.tsx` — wrap the form in Card (established pattern from auth pages)
- `frontend/src/components/ui/input.tsx` — all text fields
- `frontend/src/components/ui/button.tsx` — submit button
- shadcn Combobox (Popover + Command) — politician searchable autocomplete (D-11); install needed if not present
- shadcn Checkbox + Label — election selection (D-14)
- shadcn RadioGroup + RadioGroupItem — election level selection (D-14)
- `frontend/src/components/PaginationControls.tsx` — not needed for submission form

### Established Patterns
- **Form submit pattern**: `useState` for each field + `handleSubmit` with `credentials: "include"` + CSRF header via `getCsrfToken()` — established in `LoginPage.tsx`
- **TanStack Query for data fetching**: `useElections` / `usePoliticians` hooks follow the pattern in `/src/hooks/`
- **Error display**: `setError(...)` state with inline `<p className="text-red-500">` — pattern from `LoginPage.tsx`
- **Backend response schemas**: plain `BaseModel` (no `from_attributes`) for request/response where no ORM row mapping needed (from CONTEXT 02-04, 03-01)
- **Router registration**: alphabetical order in `main.py` — `POST /api/promises` extends existing promises router
- **moderation_status=pending default**: new promises start as pending; only `moderation_status=approved` are shown publicly — established constraint from Phase 2 onward

### Integration Points
- `backend/app/main.py` — no new router needed; add POST route to existing promises router
- `frontend/src/App.tsx` — add `/promises/new` and `/promises/:slug/edit` inside the existing `<RequireAuth>` block
- `frontend/src/components/Layout.tsx` — add "Ներկայացնել խոստում" nav link (D-10)
- New Alembic migration required for `promise_edits` table (D-06)

</code_context>

<specifics>
## Specific Ideas

- The election picker uses a two-level cascade: radio buttons for level (Ազգային / Տեղական / Հանրաքվե), then checkboxes for specific elections within that level. This keeps the UI clean when there are many elections across different types.
- The "link to elections" section is hidden behind a checkbox toggle — most promises may not need to be tied to a specific election, so reducing noise in the default view is intentional.
- The politician picker is the searchable combobox because the list will grow beyond what a static dropdown handles well. Armenian names use Unicode so the search must match Armenian text properly.
- Account age is checked via `account_age_days` which is recomputed on every login by `UserManager.on_after_login` (established in Phase 4, WR-06 fix). This means the check is based on the last-login snapshot, not real-time — acceptable for v1.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 5-Promise-Submission*
*Context gathered: 2026-05-24*
