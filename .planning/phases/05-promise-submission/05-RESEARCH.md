# Phase 5: Promise Submission - Research

**Researched:** 2026-05-24
**Domain:** FastAPI authenticated mutation endpoints + React form with shadcn Combobox/Checkbox/RadioGroup + Alembic migration for `promise_edits` table
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01:** Submitting a new promise requires: authenticated + email verified (`is_verified=True`) + account age ≥ 7 days (`account_age_days >= 7`).

**D-02:** When a logged-in user opens the form but is not yet eligible, the form renders normally (all fields visible) but the submit button is replaced with an inline explanation message: "Ձեր հաշիվը պետք է ունենա նվազագույնը 7 օրվա վաղեմություն և հաստատված էլ. հասցե՝ խոստում ներկայացնելու համար"

**D-03:** Unauthenticated visitors who click the nav link are redirected to `/login` via the existing `RequireAuth` component.

**D-04:** Promise edits are stored in a new `promise_edits` table — a full snapshot of all editable fields, not a delta/patch. The live approved promise is NEVER touched until an admin approves the edit in Phase 6.

**D-05:** Editable fields: `title_hy`, `quote_hy`, `description_hy`, `source_url`, `made_date`, `expected_date`, and election links. Each edit row stores: `promise_id` (FK to the original), `submitted_by`, `moderation_status` (pending/approved/rejected), snapshot of all editable fields, `created_at`.

**D-06:** The `promise_edits` table is append-only — rows are never deleted. Admin approval in Phase 6 marks the edit row `approved` and applies the snapshot to the live promise. All prior edit rows remain, giving a full audit trail.

**D-07:** Edit submission requires the same eligibility as new submission: logged in + verified + ≥7 days.

**D-08:** The submission form lives at `/promises/new` as a dedicated page (not a modal). Protected by `RequireAuth`.

**D-09:** The form has two visual sections on one scrollable page (no stepper, no Back/Next navigation):
  - Section 1 — Ով (Who): Politician searchable autocomplete (required) + optional election toggle
  - Section 2 — Ինչ (What) + Երբ (When): Title, verbatim quote, source URL (all required), made_date, expected_date (optional), description_hy (optional)
  - One submit button at the bottom; if ineligible it is replaced with the eligibility gate message (D-02).

**D-10:** A "Ներկայացնել խոստում" nav link is added to the Layout header, always visible to all visitors. Clicking while logged out → redirected to `/login`; logged in but ineligible → form with inline message; eligible → full form with submit button.

**D-11:** Politician selection uses a searchable autocomplete combobox — the existing shadcn Combobox component (built on Popover + Command). Typing triggers a debounced call to `GET /api/politicians?search=<query>` (or client-side filter if the full list is loaded on mount). Returns politician name_hy + id.

**D-12:** Politician field is required — form cannot be submitted without selecting a politician.

**D-13:** Election linking is optional, hidden behind a checkbox toggle: "Կապել ընտրություններին".

**D-14:** When the toggle is checked, a cascading picker appears — radio buttons for election level (Ազգային / Տեղական / Հանրաքվե), then a checkbox list of elections filtered by that level. Multiple elections can be checked.

**D-15:** Election level and elections data fetched from existing `GET /api/elections`, client-side filtered by level after fetch (≤20 items in v1).

### Claude's Discretion

- Slug generation for new promises: backend auto-generates from `title_hy` using Armenian-to-ASCII transliteration (python-slugify library). The user never sees or edits the slug in the form.
- Form validation: client-side validation (required fields highlighted) + server-side 422 errors displayed inline below affected fields.
- After successful submission: redirect to `/promises` list with a success toast: "Ձեր խոստումը ներկայացված է: Այն կհրապարակվի ստուգումից հետո"
- The `promise_edits` table needs a new Alembic migration — it does not yet exist in the schema.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROM-03 | Registered user can submit a new promise (verbatim quote + source URL required + promised date + optional expected fulfillment date) | POST /api/promises endpoint with eligibility guard; `PromiseCreateIn` schema; frontend `/promises/new` page |
| PROM-04 | Registered user can submit an edit to an existing promise (edit enters admin review queue) | PUT /api/promises/{slug} endpoint; `promise_edits` table migration + model + `PromiseEditIn`/`PromiseEditOut` schemas; frontend `/promises/:slug/edit` page |
| ELEC-03 | When submitting a promise, user can link it to one or more elections | Election IDs included in `PromiseCreateIn`/`PromiseEditIn`; frontend cascading election picker; backend creates `PromiseElectionLink` rows |
</phase_requirements>

---

## Summary

Phase 5 adds the write side of the promise pipeline. Two new backend endpoints (`POST /api/promises` and `PUT /api/promises/{slug}`) sit behind FastAPI-Users' `current_user` dependency. Both enforce eligibility (verified + ≥7 days) at the router level before touching the database. New promises start with `moderation_status=pending` and are invisible to the public until an admin approves them in Phase 6. Edits are stored as full snapshots in a new `promise_edits` table via a dedicated Alembic migration — the live promise row is never mutated.

On the frontend, the existing `RequireAuth` component already gates the `/promises/new` route. The primary new complexity is the politician searchable combobox (shadcn Combobox = Popover + Command + cmdk) and the cascading election picker (shadcn Checkbox + RadioGroup). Both require new shadcn component installations because the project currently only has card, input, button, badge, pagination, select, and separator installed. The `apiClient` in `frontend/src/api/client.ts` currently only handles GET requests — it needs a `post` method supporting `credentials: "include"` and the CSRF header before mutation calls can be made.

Slug generation uses `python-slugify` 8.0.4, which handles Armenian via `text-unidecode` transliteration. This library must be added to `requirements.txt` since it is not currently installed. The slug uniqueness collision case must be handled: if the transliterated slug already exists, append a short UUID suffix.

**Primary recommendation:** Wave 0 (migration + schemas + test stubs) is blocking. Wave 1 (backend endpoints) and Wave 2 (frontend form + election hook) can be parallelized. Wave 3 (edit submission page) builds on Wave 2's form component.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Eligibility enforcement (is_verified + account_age_days) | API / Backend | — | Must be server-side; client can only show helpful message, not gate access |
| promise_edits append-only storage | Database / Storage | API / Backend | Data integrity requires DB-level immutability pattern |
| Slug auto-generation | API / Backend | — | User never sees slug; derived server-side from title_hy |
| Election linking (PromiseElectionLink rows) | API / Backend | — | Relational integrity; frontend only sends election IDs |
| Politician autocomplete search | API / Backend + Browser | — | Server provides data; client debounces and filters |
| Election cascading picker | Browser / Client | API / Backend | Client-side filter on ≤20 items; server provides all elections |
| Eligibility gate UI message | Browser / Client | — | Display-only; actual gate is server-side |
| CSRF token header | Browser / Client | API / Backend | Double-submit cookie pattern established in Phase 4 |

---

## Standard Stack

### Core (Backend)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi-users | 15.0.5 | `current_user` dependency for protected endpoints | Already installed; provides `fastapi_users.current_user(active=True, verified=True)` |
| python-slugify | 8.0.4 | Armenian-to-ASCII transliteration for slug generation | Standard Python slug library; handles Unicode via text-unidecode [VERIFIED: npm registry via `pip index versions`] |
| sqlalchemy 2.x | 2.0.49 | `promise_edits` model; INSERT for new promise + edit rows | Already installed |
| alembic | 1.18.4 | New migration for `promise_edits` table | Already installed; prior migrations at `backend/alembic/versions/` |

### Core (Frontend)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @radix-ui/react-popover | 1.1.15 | Popover container for Combobox | shadcn Combobox pattern; not yet in package.json — needs install |
| cmdk | 1.1.1 | Command/search primitive inside Combobox | shadcn Command component depends on cmdk; not yet in package.json |
| @radix-ui/react-checkbox | 1.3.3 | Election checkbox selection + "link to elections" toggle | shadcn Checkbox component; not yet in package.json |
| @radix-ui/react-radio-group | 1.3.8 | Election level selector (Ազգային/Տեղական/Հանրաքվե) | shadcn RadioGroup component; not yet in package.json |
| @radix-ui/react-label | 2.1.8 | Labels for form fields | shadcn Label component; not yet in package.json |

### Already Installed (No New Install Required)

| Library | Version | Purpose |
|---------|---------|---------|
| @radix-ui/react-select | ^2.2.6 | Already present (not needed for this phase's new components) |
| @radix-ui/react-slot | ^1.2.4 | Already present |
| @tanstack/react-query | ^5.0.0 | Politician + election data hooks |
| lucide-react | ^1.16.0 | Icons (e.g., ChevronDown for combobox trigger) |

**Installation:**

Backend:
```bash
# Add to requirements.txt
python-slugify==8.0.4
```

Frontend:
```bash
cd frontend && npm install @radix-ui/react-popover@^1.1.15 cmdk@^1.1.1 @radix-ui/react-checkbox@^1.3.3 @radix-ui/react-radio-group@^1.3.8 @radix-ui/react-label@^2.1.8 --legacy-peer-deps
```

Note: `--legacy-peer-deps` is required per project decision 02-01 (`.npmrc` sets `legacy-peer-deps=true`).

---

## Package Legitimacy Audit

| Package | Registry | Age | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-------------|-----------|-------------|
| python-slugify | PyPI | ~10 yrs | github.com/un33k/python-slugify | [OK] | Approved |
| @radix-ui/react-popover | npm | ~5 yrs | github.com/radix-ui/primitives | [ASSUMED-OK] | Approved — established Radix UI primitive |
| cmdk | npm | ~3 yrs | github.com/pacocoursey/cmdk | [ASSUMED-OK] | Approved — shadcn/ui dependency, widely used |
| @radix-ui/react-checkbox | npm | ~5 yrs | github.com/radix-ui/primitives | [ASSUMED-OK] | Approved — established Radix UI primitive |
| @radix-ui/react-radio-group | npm | ~5 yrs | github.com/radix-ui/primitives | [ASSUMED-OK] | Approved — established Radix UI primitive |
| @radix-ui/react-label | npm | ~5 yrs | github.com/radix-ui/primitives | [ASSUMED-OK] | Approved — established Radix UI primitive |

**slopcheck result for python-slugify:** `[OK]` — confirmed via `slopcheck install python-slugify` [VERIFIED: PyPI registry].
**npm packages:** slopcheck does not support npm scan; all Radix UI packages confirmed to exist on npm registry via `npm view` and are part of the official Radix UI primitives monorepo at github.com/radix-ui/primitives [CITED: radix-ui.com]. cmdk confirmed at npm registry version 1.1.1 with official repo at github.com/pacocoursey/cmdk [CITED: npmjs.com/package/cmdk]. [ASSUMED] tags applied for npm packages since slopcheck could not run npm checks.

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
Browser
  |
  |-- GET /promises/new ──────────────────────────────────────────┐
  |   RequireAuth gate (redirect to /login if unauthenticated)    |
  |                                                               v
  |                                              PromiseSubmitPage
  |                                                  |
  |-- GET /api/politicians?search=... ──────────> usePoliticianSearch hook
  |-- GET /api/elections ─────────────────────> useElectionsAll hook
  |                                                  |
  |   [User fills form; eligibility check          ]|
  |   [from AuthContext: is_verified + account_age_days]        |
  |                                                  v
  |-- POST /api/promises (with CSRF header) ───> promises router
  |      credentials: "include"                      |
  |                                        current_user dependency
  |                                                  |
  |                                          Eligibility guard
  |                                        (is_verified + age ≥ 7)
  |                                                  |
  |                                    slug = slugify(title_hy) + dedup
  |                                                  |
  |                                    INSERT promises (pending)
  |                                    INSERT promise_election_links (0..n)
  |                                                  |
  |<── 201 Created PromiseOut ─────────────────────-+
  |   redirect to /promises + toast
  |
  |-- PUT /api/promises/{slug} ────────────────> promises router
  |      (edit flow — same eligibility)              |
  |                                    INSERT promise_edits (pending)
  |                                    INSERT promise_edit_election_links (0..n)
  |<── 201 Created PromiseEditOut ────────────────--+
```

### Recommended Project Structure

New files for Phase 5:

```
backend/
├── app/
│   ├── models/
│   │   └── promise_edits.py          # PromiseEdit model + PromiseEditElectionLink
│   ├── schemas/
│   │   └── promises.py               # ADD: PromiseCreateIn, PromiseEditIn, PromiseEditOut
│   └── routers/
│       └── promises.py               # ADD: POST /api/promises, PUT /api/promises/{slug}
└── alembic/versions/
    └── 20260524_000001_add_promise_edits.py

frontend/src/
├── components/ui/
│   ├── combobox.tsx                  # NEW: shadcn Combobox (Popover + Command)
│   ├── command.tsx                   # NEW: shadcn Command primitive (wraps cmdk)
│   ├── checkbox.tsx                  # NEW: shadcn Checkbox
│   ├── radio-group.tsx               # NEW: shadcn RadioGroup
│   └── label.tsx                     # NEW: shadcn Label
├── hooks/
│   ├── usePoliticianSearch.ts        # NEW: debounced politician search
│   └── useElectionsAll.ts            # NEW or reuse useElections with large per_page
├── pages/
│   ├── PromiseSubmitPage.tsx         # NEW: /promises/new
│   └── PromiseEditPage.tsx           # NEW: /promises/:slug/edit
└── api/
    └── client.ts                     # ADD: post() method with credentials + CSRF
```

### Pattern 1: FastAPI-Users current_user in a regular router

**What:** Inject the authenticated user into any FastAPI route using `fastapi_users.current_user(active=True, verified=True)`. Returns the `User` ORM object. Raises `401` if not authenticated, `403` if not verified.

**When to use:** Any endpoint that requires an authenticated, email-verified user.

**Example:**
```python
# Source: fastapi-users docs + existing app/routers/auth.py pattern
from app.auth.users import fastapi_users
from app.models.users import User

current_verified_user = fastapi_users.current_user(active=True, verified=True)

@router.post("", status_code=201, response_model=PromiseOut)
async def create_promise(
    payload: PromiseCreateIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_verified_user),
):
    # user.is_verified == True guaranteed by the dependency
    # Still need to manually check account_age_days
    if user.account_age_days < 7:
        raise HTTPException(status_code=403, detail="Account must be at least 7 days old")
    ...
```

Note: `fastapi_users.current_user(verified=True)` raises 403 for unverified users automatically. Account age must be checked manually since fastapi-users does not support custom eligibility fields in its dependency. [ASSUMED — based on fastapi-users 15.x docs; verified=True parameter behavior confirmed from auth.py usage pattern in this codebase]

### Pattern 2: Slug generation with collision handling

**What:** `python-slugify` with `text-unidecode=True` (Armenian → ASCII). Append a 6-char UUID fragment on collision.

**When to use:** Auto-generating the promise slug on POST /api/promises.

**Example:**
```python
# Source: python-slugify PyPI docs + codebase pattern from politicians.py (slug column)
from slugify import slugify
import uuid

def generate_unique_slug(title_hy: str, existing_slugs: set[str]) -> str:
    base = slugify(title_hy, allow_unicode=False)  # Armenian → ASCII via text-unidecode
    if not base:
        base = "promise"  # fallback for titles with only special chars
    slug = base
    if slug in existing_slugs:
        slug = f"{base}-{str(uuid.uuid4())[:6]}"
    return slug
```

For async DB check pattern, use `SELECT slug FROM promises WHERE slug = :base` and suffix if exists. [VERIFIED: PyPI registry — python-slugify 8.0.4 confirmed]

### Pattern 3: append-only promise_edits INSERT

**What:** Never UPDATE the live Promise row on edit submission. Always INSERT a new `promise_edits` row with `moderation_status=pending`.

**When to use:** PUT /api/promises/{slug} (Phase 5). UPDATE of live row only happens in Phase 6 (admin approval).

**Example:**
```python
# Source: CONTEXT.md D-04, D-06 locked decisions
edit = PromiseEdit(
    promise_id=existing_promise.id,
    submitted_by=user.id,
    moderation_status=ModerationStatus.pending,
    title_hy=payload.title_hy,
    quote_hy=payload.quote_hy,
    description_hy=payload.description_hy,
    source_url=payload.source_url,
    made_date=payload.made_date,
    expected_date=payload.expected_date,
)
db.add(edit)
await db.flush()  # get edit.id before adding election links

for election_id in payload.election_ids:
    db.add(PromiseEditElectionLink(edit_id=edit.id, election_id=election_id))

await db.commit()
```

### Pattern 4: Frontend form submit with CSRF + credentials

**What:** Extend `apiClient` with a `post` method that mirrors the existing auth pages' `fetch` pattern (credentials: "include" + x-csrftoken header).

**When to use:** All mutation calls from Phase 5+ form pages.

**Example:**
```typescript
// Source: frontend/src/pages/LoginPage.tsx getCsrfToken() pattern + existing apiClient
function getCsrfToken(): string {
  return document.cookie
    .split("; ")
    .find((r) => r.startsWith("csrftoken="))
    ?.split("=")[1] ?? ""
}

// Add to frontend/src/api/client.ts:
async post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(API_BASE + path, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "x-csrftoken": getCsrfToken(),
    },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw { status: response.status, detail: err.detail ?? "Unknown error" }
  }
  return response.json() as Promise<T>
},
```

### Pattern 5: Politician search combobox (shadcn Combobox)

**What:** shadcn Combobox = Popover + Command (cmdk). Input triggers debounced search. State: `open`, `selectedPoliticianId`, `searchQuery`.

**When to use:** Politician picker in the submission form (D-11).

**Example:**
```tsx
// Source: shadcn/ui docs Combobox pattern + existing usePoliticians hook
import { useState } from "react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandInput, CommandItem, CommandList } from "@/components/ui/command"

// Client-side filter on loaded list (≤100 politicians in v1):
// usePoliticians({ page: 1, perPage: 100 }) on mount, then filter by searchQuery
```

### Anti-Patterns to Avoid

- **Mutating the live Promise row on edit submission:** Phase 6 owns approval; Phase 5 only INSERTs into `promise_edits`.
- **Setting moderation_status from the frontend:** Backend always sets `moderation_status=pending` for new submissions; never trust a client-supplied value.
- **Skipping CSRF header on POST/PUT:** `starlette_csrf` is active on all non-safe methods; missing header → 403. Pattern already established in LoginPage.tsx.
- **Missing `await db.flush()` before linking election rows:** Election link FKs reference `promise.id` or `edit.id`; must flush to get the PK before inserting links.
- **slug uniqueness check race condition:** Check slug availability inside the same DB transaction and handle IntegrityError with a retry/suffix.
- **apiClient GET-only:** The current `apiClient` in `frontend/src/api/client.ts` only has a `get` method. A `post` method (and optionally `put`) must be added before the form can submit.
- **`from_attributes=True` on PromiseCreateIn/PromiseEditIn:** Input schemas are plain BaseModel — no ORM mapping needed. Only output schemas that are constructed from ORM objects need model_config.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Armenian text slugification | Custom regex transliterator | `python-slugify` + `text-unidecode` | Handles all Unicode Armenian correctly; battle-tested edge cases (apostrophes, hyphens, numbers) |
| Combobox with search | Custom autocomplete component | shadcn Combobox (Popover + Command + cmdk) | Keyboard nav, accessibility, focus trapping already built in |
| Authenticated route protection | Custom middleware | Existing `RequireAuth` component | Already works; just nest `/promises/new` inside it in App.tsx |
| Current user injection | Manual JWT decode in router | `fastapi_users.current_user()` dependency | Already integrated; handles token validation, expiry, 401/403 |
| CSRF protection | Custom middleware | `starlette_csrf` (already active) | Already in `main.py`; just include the header in fetch calls |

**Key insight:** The hardest parts (auth, CSRF, protected routes) are already built in Phases 1-4. Phase 5 is primarily schema + form work on top of a working foundation.

---

## Common Pitfalls

### Pitfall 1: `account_age_days` is login-snapshot, not real-time

**What goes wrong:** A user registers and immediately logs in, gets `account_age_days=0`. If they never log in again for 8 days and then go to submit, `account_age_days` is still 0 from the last login — the eligibility check fails even though the account is actually 8 days old.

**Why it happens:** `account_age_days` is computed in `UserManager.on_after_login` and persisted to the DB. It is NOT updated on every API request.

**How to avoid:** This is an accepted v1 limitation documented in CONTEXT.md (specifics section). The planner should note it in the plan but NOT change the approach — it is locked.

**Warning signs:** Users reporting "account says 0 days" despite having registered over a week ago. Fix in v2 via real-time computation from `user.created_at`.

### Pitfall 2: Slug collision for Armenian titles

**What goes wrong:** Two promises with similar titles transliterate to the same slug. The second INSERT raises `UniqueViolation` on `promises.slug`.

**Why it happens:** `python-slugify` maps many Armenian characters to the same ASCII output. Common words ("Արցախ" → "artsakh") will collide when the same word appears in multiple promise titles.

**How to avoid:** After generating `base_slug = slugify(title_hy)`, check `SELECT 1 FROM promises WHERE slug = :base_slug LIMIT 1`. If exists, append `-{uuid4()[:6]}`. Wrap the INSERT in a try/except for `asyncpg.UniqueViolationError` as a safety net.

### Pitfall 3: Missing election validation — invalid election_ids accepted silently

**What goes wrong:** If `election_ids` in the request payload contains a UUID that does not exist in the `elections` table, the FK insert fails with an IntegrityError (or silently succeeds if the FK is deferred).

**Why it happens:** Pydantic validates that election_ids are valid UUIDs but not that they exist in the DB.

**How to avoid:** After receiving `election_ids`, query `SELECT id FROM elections WHERE id = ANY(:ids)` and verify the count matches. Return 422 if any election_id is invalid.

### Pitfall 4: `PUT /api/promises/{slug}` 404 on non-approved promises

**What goes wrong:** A user tries to edit a promise that is in `pending` state (e.g., one they submitted 5 minutes ago). The existing GET endpoint only returns `moderation_status=approved` promises, so the edit endpoint would 404.

**Why it happens:** Phase 3 GET endpoint filters by `moderation_status=approved`. If the PUT endpoint uses the same filter, pending promises cannot be edited.

**How to avoid:** The PUT /api/promises/{slug} endpoint should look up the promise without the `moderation_status=approved` filter — it should find any non-rejected promise. Rejected promises should not be editable (return 404 or 403).

### Pitfall 5: Frontend `apiClient.post` missing `credentials: "include"`

**What goes wrong:** The CSRF cookie and auth cookie are not sent with the POST request. The backend returns 403 (CSRF) or 401 (no auth).

**Why it happens:** The current `apiClient.get` does NOT include `credentials: "include"`. A naively extended `post` method that follows the same pattern will fail.

**How to avoid:** Explicitly add `credentials: "include"` and `"x-csrftoken": getCsrfToken()` to the `post` (and `put`) methods. The `getCsrfToken()` helper exists in `LoginPage.tsx` and should be moved to `client.ts` or a shared `csrf.ts` utility.

### Pitfall 6: `PromiseEditIn` election_ids not creating `PromiseEditElectionLink` rows

**What goes wrong:** Edit submission captures all content fields in `promise_edits` but the election links are stored in a separate table. If the planner forgets to add a `promise_edit_election_links` table (or if the Phase 6 admin approval logic doesn't know to read from it), the election associations on an edited promise are lost.

**Why it happens:** The M2M relationship for edits is a different table from `promise_election_links`.

**How to avoid:** The `promise_edits` model needs either (a) a companion `promise_edit_election_links` table mirroring `promise_election_links`, or (b) a JSON column storing the election ID array as part of the snapshot. Recommendation: use a companion table for FK integrity and to match the existing `promise_election_links` pattern.

---

## Code Examples

### Backend: PromiseCreateIn schema

```python
# Source: existing app/schemas/promises.py patterns + CONTEXT.md D-09 field list
import uuid
from datetime import date
from pydantic import BaseModel, HttpUrl

class PromiseCreateIn(BaseModel):
    """Input for POST /api/promises. NO from_attributes — this is a request body schema."""
    title_hy: str          # required
    quote_hy: str          # required (verbatim)
    source_url: str        # required
    politician_id: uuid.UUID  # required
    made_date: date | None = None
    expected_date: date | None = None
    description_hy: str | None = None
    election_ids: list[uuid.UUID] = []  # optional, may be empty
```

### Backend: PromiseEditIn schema

```python
# Source: CONTEXT.md D-05 editable fields list
class PromiseEditIn(BaseModel):
    """Input for PUT /api/promises/{slug}. Full snapshot of all editable fields."""
    title_hy: str
    quote_hy: str
    source_url: str
    made_date: date | None = None
    expected_date: date | None = None
    description_hy: str | None = None
    election_ids: list[uuid.UUID] = []
```

### Backend: Alembic migration skeleton for `promise_edits`

```python
# Source: existing migrations at backend/alembic/versions/ as reference for naming/style
# File: 20260524_000001_add_promise_edits.py
revision = "20260524_000001"
down_revision = "20260523_000001"  # auth schema migration

def upgrade() -> None:
    op.create_table(
        "promise_edits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("promise_id", sa.UUID(), sa.ForeignKey("promises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submitted_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("moderation_status", sa.Enum("pending", "approved", "rejected", name="moderation_status"), nullable=False),
        sa.Column("title_hy", sa.String(500), nullable=False),
        sa.Column("quote_hy", sa.Text(), nullable=False),
        sa.Column("description_hy", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("made_date", sa.Date(), nullable=True),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__promise_edits")),
    )
    op.create_table(
        "promise_edit_election_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("edit_id", sa.UUID(), sa.ForeignKey("promise_edits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("election_id", sa.UUID(), sa.ForeignKey("elections.id", ondelete="CASCADE"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__promise_edit_election_links")),
        sa.UniqueConstraint("edit_id", "election_id", name=op.f("uq__promise_edit_election_links__edit_id__election_id")),
    )
```

Note: `moderation_status` SAEnum is already created in the DB by the initial migration. The migration must use `create_type=False` or reference the existing Enum to avoid "type already exists" error. [ASSUMED — based on SQLAlchemy/Alembic behavior with pre-existing enum types; this is the established pattern in the codebase]

### Frontend: eligibility gate component

```tsx
// Source: CONTEXT.md D-02 locked decision
function EligibilityGate({ children, user }: { children: React.ReactNode; user: UserRead & { account_age_days: number } }) {
  const isEligible = user.is_verified && user.account_age_days >= 7

  if (!isEligible) {
    return (
      <p className="text-sm text-zinc-500 mt-4">
        Ձեր հաշիվը պետք է ունենա նվազագույնը 7 օրվա վաղեմություն և հաստատված
        էլ. հասցե՝ խոստում ներկայացնելու համար
      </p>
    )
  }
  return <>{children}</>
}
```

Note: `account_age_days` is not currently in the `UserRead` TypeScript type in `frontend/src/types/index.ts` or `AuthContext.tsx`. It must be added to both. [VERIFIED: codebase grep — `account_age_days` is in `User` ORM model in `users.py` but absent from `AuthContext.tsx`'s `UserRead` type]

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Custom slug libraries with manual Armenian char maps | `python-slugify` with `text-unidecode` for full Unicode coverage | Use python-slugify; do not hand-roll |
| Stepper forms (multi-page) | Single scrollable page with two visual sections | Simpler UX; already decided (D-09) |
| Optimistic UI for pending submissions | Redirect + success toast; pending items shown to submitter in future phase | No optimistic UI needed in Phase 5 |

**Deprecated/outdated:**
- `text-unidecode` standalone: use via `python-slugify` which bundles it as a dependency.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `fastapi_users.current_user(verified=True)` automatically raises 403 for unverified users; account_age_days must still be checked manually | Pattern 1 | If verified=True doesn't auto-raise, need manual check for is_verified too |
| A2 | The existing `moderation_status` SAEnum type in PostgreSQL can be reused in the new `promise_edits` table migration using `create_type=False` in Alembic | Code Examples | If not, migration will fail with "type already exists"; fix: use `existing_type` pattern |
| A3 | Election list is ≤20 items in v1; client-side filtering after a single `/api/elections` fetch is acceptable (D-15) | Architecture Patterns | If election count grows before Phase 5 runs, server-side filtering may be needed |
| A4 | Radix UI npm packages (@radix-ui/react-popover, etc.) ages, download counts confirmed as established packages | Package Legitimacy | slopcheck npm scan not available; packages confirmed via npm view and official Radix UI docs |
| A5 | `account_age_days` field is missing from the `UserRead` TypeScript type in AuthContext.tsx | Code Examples / Pitfall 1 | If it is present under a different key, the frontend eligibility check logic differs |

---

## Open Questions

1. **`moderation_status` SAEnum reuse in `promise_edits` migration**
   - What we know: SQLAlchemy defines the `moderation_status` Enum type in PostgreSQL once (initial migration). Using `SAEnum(ModerationStatus, name="moderation_status")` again in a new model will cause `CREATE TYPE moderation_status` to be called a second time.
   - What's unclear: Does the existing codebase pattern (check `evidence.py` which also references ModerationStatus) already solve this via `create_type=False`?
   - Recommendation: The planner must inspect `backend/app/models/evidence.py` to confirm how the ModerationStatus import is handled there, then replicate that pattern in `promise_edits.py`.

2. **`per_page` limit for politician fetch in Combobox**
   - What we know: `GET /api/politicians` has `per_page` max of 100. Seed data has ~10 politicians.
   - What's unclear: Whether to use client-side filtering (load all 100 once) or server-side search (debounced per-keystroke). D-11 says "debounced call to GET /api/politicians?search=<query> OR client-side filter if the full list is loaded on mount."
   - Recommendation: Load all politicians once on mount (page=1, per_page=100) and filter client-side. The backend `GET /api/politicians` does not currently support a `search` query param — adding server-side search would require a new Phase 5 backend task. Client-side filter is simpler and sufficient for v1 politician counts.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | Running the full stack | ✓ | 29.4.3 | — |
| Node.js | Frontend build / npm installs | ✓ | 26.2.0 | — |
| Python | Backend / pip installs | ✓ | 3.13.2 | — |
| python-slugify | Slug generation | ✗ (not in requirements.txt) | 8.0.4 on PyPI | Must add to requirements.txt |
| @radix-ui/react-popover | Combobox component | ✗ (not in package.json) | 1.1.15 on npm | Must npm install |
| cmdk | Command primitive | ✗ (not in package.json) | 1.1.1 on npm | Must npm install |
| @radix-ui/react-checkbox | Election checkbox | ✗ (not in package.json) | 1.3.3 on npm | Must npm install |
| @radix-ui/react-radio-group | Election level radio | ✗ (not in package.json) | 1.3.8 on npm | Must npm install |
| @radix-ui/react-label | Form labels | ✗ (not in package.json) | 2.1.8 on npm | Must npm install |

**Missing dependencies with no fallback:**
- `python-slugify` must be added to `requirements.txt` and installed before the backend can generate slugs.
- All 5 frontend Radix/cmdk packages must be `npm install`-ed before shadcn components can be created.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (backend); Vitest (frontend) |
| Config file | `backend/pyproject.toml` (pytest config); `frontend/vite.config.ts` (vitest) |
| Quick run command | `docker compose exec backend pytest tests/test_promises.py -x` |
| Full suite command | `docker compose exec backend pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROM-03 | POST /api/promises creates pending promise with correct fields | integration | `pytest tests/test_promises.py::test_create_promise -x` | ❌ Wave 0 |
| PROM-03 | POST /api/promises returns 401 for unauthenticated request | integration | `pytest tests/test_promises.py::test_create_promise_unauthenticated -x` | ❌ Wave 0 |
| PROM-03 | POST /api/promises returns 403 for unverified user | integration | `pytest tests/test_promises.py::test_create_promise_unverified -x` | ❌ Wave 0 |
| PROM-03 | POST /api/promises returns 403 for account < 7 days | integration | `pytest tests/test_promises.py::test_create_promise_too_young -x` | ❌ Wave 0 |
| PROM-03 | POST /api/promises with invalid election_id returns 422 | integration | `pytest tests/test_promises.py::test_create_promise_invalid_election -x` | ❌ Wave 0 |
| PROM-04 | PUT /api/promises/{slug} inserts into promise_edits (not updating live row) | integration | `pytest tests/test_promises.py::test_edit_promise_creates_edit_row -x` | ❌ Wave 0 |
| PROM-04 | PUT /api/promises/{slug} returns 401 for unauthenticated | integration | `pytest tests/test_promises.py::test_edit_promise_unauthenticated -x` | ❌ Wave 0 |
| ELEC-03 | POST /api/promises with election_ids creates PromiseElectionLink rows | integration | `pytest tests/test_promises.py::test_create_promise_with_elections -x` | ❌ Wave 0 |
| Schema | promise_edits table exists with correct columns | unit | `pytest tests/test_schema.py::test_promise_edits_table -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `docker compose exec backend pytest tests/test_promises.py -x`
- **Per wave merge:** `docker compose exec backend pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_promises.py` — add PROM-03, PROM-04, ELEC-03 test stubs (RED state)
- [ ] `tests/test_schema.py` — add `test_promise_edits_table` assertion
- [ ] `backend/app/models/promise_edits.py` — PromiseEdit + PromiseEditElectionLink models
- [ ] `backend/alembic/versions/20260524_000001_add_promise_edits.py` — migration
- [ ] `backend/requirements.txt` — add `python-slugify==8.0.4`
- [ ] `frontend/package.json` — add Radix + cmdk packages

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | fastapi-users `current_user(active=True, verified=True)` dependency |
| V3 Session Management | yes | httpOnly cookies; CSRF double-submit (starlette_csrf already active) |
| V4 Access Control | yes | Server-side eligibility check (is_verified + account_age_days ≥ 7) |
| V5 Input Validation | yes | Pydantic PromiseCreateIn/PromiseEditIn schemas; server-side 422 for invalid fields |
| V6 Cryptography | no | No new crypto operations; JWT from Phase 4 handles auth tokens |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Submitting promises from unverified/new accounts (coordinated fake entries) | Spoofing | Server-side eligibility guard: is_verified=True + account_age_days ≥ 7 (D-01) |
| Defamatory content in promise submissions | Tampering / Repudiation | All submissions enter moderation queue (moderation_status=pending); never go live without admin review |
| Source URL manipulation (pointing to unrelated page) | Tampering | Phase 5 stores URL as-is; source validation is a human/admin moderation task (out of scope for Phase 5 automation) |
| Mass submission from freshly created accounts | Denial of Service | Account age requirement (7 days) limits blast radius from newly created bot accounts |
| CSRF on POST /api/promises | Tampering | starlette_csrf middleware active; x-csrftoken header required on all non-safe methods |
| Election ID injection (non-existent elections) | Tampering | Backend validates all election_ids against DB before INSERT |
| slug enumeration via edit endpoint | Information Disclosure | PUT /api/promises/{slug} should only return 200/201 or 403; never expose whether a pending promise exists to non-owner |

---

## Sources

### Primary (HIGH confidence)
- Codebase inspection: `backend/app/`, `frontend/src/` — all existing models, schemas, routers, hooks, components, and types read directly
- `backend/requirements.txt` — confirmed installed packages and versions
- `frontend/package.json` — confirmed installed npm packages and versions
- `backend/alembic/versions/` — confirmed existing migrations and naming conventions
- `pip index versions python-slugify` — confirmed latest version 8.0.4 [VERIFIED: PyPI registry]
- `slopcheck install python-slugify` — confirmed [OK] [VERIFIED: slopcheck 0.6.1]

### Secondary (MEDIUM confidence)
- `npm view @radix-ui/react-popover version` → 1.1.15; `npm view cmdk version` → 1.1.1; etc. [VERIFIED: npm registry for version existence]
- Radix UI official docs at radix-ui.com confirming these are the official primitive packages [CITED: radix-ui.com/primitives]
- CONTEXT.md locked decisions (D-01 through D-15) — user-confirmed design decisions

### Tertiary (LOW confidence)
- `fastapi_users.current_user(verified=True)` auto-raise behavior — [ASSUMED] from reading auth.py usage patterns in the codebase; not independently verified against fastapi-users 15.0.5 changelog
- SAEnum `create_type=False` pattern for reusing existing PostgreSQL enum types in new Alembic migrations — [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified against PyPI/npm registries; existing packages confirmed from requirements.txt and package.json
- Architecture: HIGH — derived entirely from existing codebase patterns (Phase 2-4 conventions) + locked CONTEXT.md decisions
- Pitfalls: MEDIUM — pitfalls 1-5 are verified against codebase; pitfall 6 (PromiseEditElectionLink) is architectural reasoning [ASSUMED] not tested

**Research date:** 2026-05-24
**Valid until:** 2026-06-24 (30 days — stable stack)
