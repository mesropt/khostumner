---
phase: 05-promise-submission
reviewed: 2026-05-25T00:00:00Z
depth: standard
files_reviewed: 24
files_reviewed_list:
  - backend/alembic/versions/20260524_000001_add_promise_edits.py
  - backend/app/auth/schemas.py
  - backend/app/models/promise_edits.py
  - backend/app/routers/promises.py
  - backend/app/schemas/promises.py
  - backend/tests/test_promises.py
  - backend/Dockerfile
  - backend/requirements.txt
  - frontend/src/api/client.ts
  - frontend/src/contexts/AuthContext.tsx
  - frontend/src/hooks/useElectionsAll.ts
  - frontend/src/hooks/usePoliticianSearch.ts
  - frontend/src/components/ui/combobox.tsx
  - frontend/src/components/ui/checkbox.tsx
  - frontend/src/components/ui/command.tsx
  - frontend/src/components/ui/label.tsx
  - frontend/src/components/ui/radio-group.tsx
  - frontend/src/components/ui/popover.tsx
  - frontend/src/pages/PromiseSubmitPage.tsx
  - frontend/src/pages/PromiseEditPage.tsx
  - frontend/src/pages/PromiseDetailPage.tsx
  - frontend/src/pages/PromisesListPage.tsx
  - frontend/src/App.tsx
  - frontend/src/components/Layout.tsx
findings:
  critical: 6
  warning: 7
  info: 4
  total: 17
status: issues_found
---

# Phase 05: Code Review Report

**Reviewed:** 2026-05-25T00:00:00Z
**Depth:** standard
**Files Reviewed:** 24
**Status:** issues_found

## Summary

Phase 5 delivers the promise submission flow: `POST /api/promises`, `PUT /api/promises/{slug}` (append-only edit), the `promise_edits` table, and the corresponding React pages. The architecture is generally sound — the append-only edit pattern is correctly implemented and the two-status-field invariant from CLAUDE.md is respected.

However, six critical defects were found that either produce incorrect behaviour in production or introduce a security gap: an unvalidated politician_id FK, a missing `credentials: "include"` on `GET` requests in the API client, the `SAEnum` re-declaration issue that will attempt to create the already-existing `moderation_status` ENUM type on ORM metadata sync, a slug collision retry that re-adds already-flushed election links (data duplication), a React Router v6 route-ordering problem that makes `/promises/new` unreachable, and stale `account_age_days` allowing eligibility bypass. Seven warnings address robustness and correctness gaps.

---

## Critical Issues

### CR-01: `politician_id` not validated before INSERT — FK error surfaced as 500

**File:** `backend/app/routers/promises.py:213-226`
**Issue:** `create_promise` accepts `payload.politician_id` and writes it directly to the `Promise` row without first checking whether that UUID exists in the `politicians` table. If a client sends a fabricated UUID, PostgreSQL raises a foreign-key constraint violation. SQLAlchemy will re-raise this as an unhandled `IntegrityError` (the `IntegrityError` handler on lines 242-254 only catches slug collisions; it does not distinguish which constraint fired and does not produce a user-facing 422). The result is an unhandled exception → 500 response in production.

**Fix:**
```python
# After the election_ids validation block, before creating the Promise row:
pol_result = await db.execute(
    select(Politician.id).where(Politician.id == payload.politician_id).limit(1)
)
if pol_result.scalar_one_or_none() is None:
    raise HTTPException(status_code=422, detail="Invalid politician_id")
```

---

### CR-02: `apiClient.get()` omits `credentials: "include"` — authenticated GET requests fail silently

**File:** `frontend/src/api/client.ts:13-19`
**Issue:** The `get<T>()` method calls `fetch(API_BASE + path)` with no `credentials` option. The default is `"same-origin"`, which will not send the httpOnly auth cookie on cross-origin requests (the backend runs on `localhost:8000`, the frontend on a different port). Any hook that uses `apiClient.get` — including `usePoliticianSearch`, `useElectionsAll`, and the `usePromise` hook used by `PromiseEditPage` — will make unauthenticated requests. Currently the list/detail endpoints don't require auth, but this pattern will silently fail for any future GET that does require authentication. More immediately, it creates an inconsistency that is difficult to debug: `post`/`put` send cookies; `get` does not.

**Fix:**
```typescript
async get<T>(path: string): Promise<T> {
  const response = await fetch(API_BASE + path, {
    credentials: "include",
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw { status: response.status, detail: (err as { detail?: string }).detail ?? "Unknown error" }
  }
  return response.json() as Promise<T>
},
```
The error-throw shape is also inconsistent with `post`/`put` (line 16 throws `new Error(...)` while the others throw a plain object) — fix both together so callers handle the same shape.

---

### CR-03: `SAEnum(ModerationStatus, name="moderation_status")` in `PromiseEdit` will attempt to CREATE the ENUM type again

**File:** `backend/app/models/promise_edits.py:38-42`
**Issue:** The `PromiseEdit.moderation_status` column is declared as:
```python
SAEnum(ModerationStatus, name="moderation_status")
```
SQLAlchemy's `SAEnum` with `create_type=True` (the default) will issue `CREATE TYPE moderation_status AS ENUM (...)` when the ORM creates/migrates the schema. Because this ENUM already exists in PostgreSQL (created by the initial `promises` migration), this causes a `DuplicateObject` error when running `alembic upgrade` on a fresh database that applies both migrations. The Alembic migration itself correctly passes `create_type=False`, but the ORM metadata does not match — any code path that calls `metadata.create_all()` (e.g., test setup that bypasses Alembic) will fail.

**Fix:**
```python
moderation_status: Mapped[ModerationStatus] = mapped_column(
    SAEnum(ModerationStatus, name="moderation_status", create_type=False),
    default=ModerationStatus.pending,
    nullable=False,
)
```

---

### CR-04: Slug-collision retry re-adds election links that were already flushed — duplicate rows

**File:** `backend/app/routers/promises.py:242-254`
**Issue:** When `IntegrityError` is caught after the first `commit()` attempt, the code does `rollback()`, assigns a new slug, and then re-adds election links in a second loop (lines 248-253). However, after the rollback the `promise` object and all `PromiseElectionLink` objects added before the first `commit()` are in a rolled-back state. The code then calls `db.add(promise)` (line 247) and adds fresh `PromiseElectionLink` rows. This is the correct intent, but the promise's `id` was set during `flush()` before the rollback. After the rollback the `promise.id` may be stale (the flush was rolled back). In many async-SQLAlchemy configurations, the object state after `rollback()` is expired, meaning `promise.id` will trigger a lazy load that fails because the row no longer exists in the DB. The safe fix is to rebuild the Promise object entirely after rollback.

**Fix:**
```python
except IntegrityError:
    await db.rollback()
    slug = f"{base_slug}-{_uuid.uuid4().hex[:6]}"
    promise = Promise(
        title_hy=payload.title_hy,
        quote_hy=payload.quote_hy,
        description_hy=payload.description_hy,
        politician_id=payload.politician_id,
        made_date=payload.made_date,
        expected_date=payload.expected_date,
        source_url=payload.source_url,
        slug=slug,
        moderation_status=ModerationStatus.pending,
        created_by=user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(promise)
    await db.flush()
    for election_id in payload.election_ids:
        db.add(PromiseElectionLink(promise_id=promise.id, election_id=election_id))
    await db.commit()
```

---

### CR-05: React Router v6 route ordering — `/promises/new` is shadowed by `/promises/:slug`

**File:** `frontend/src/App.tsx:33,44-46`
**Issue:** In React Router v6, routes are matched in the order they are declared within the same sibling group. The route `<Route path="/promises/:slug" ...>` (line 33) is declared before the `<RequireAuth>` wrapper that contains `/promises/new` (lines 44-46). React Router v6's matching algorithm will evaluate `/promises/new` against `/promises/:slug` first; because `new` is a valid slug string, it matches `:slug` and renders `PromiseDetailPage` instead of `PromiseSubmitPage`. The submit page is effectively unreachable via the URL `/promises/new`.

**Fix:** Move the `/promises/new` route (and the `RequireAuth` wrapper it lives in) above the `:slug` catch-all:
```tsx
<Route path="/promises" element={<PromisesListPage />} />
<Route element={<RequireAuth />}>
  <Route path="/promises/new" element={<PromiseSubmitPage />} />
  <Route path="/promises/:slug/edit" element={<PromiseEditPage />} />
</Route>
<Route path="/promises/:slug" element={<PromiseDetailPage />} />
```

---

### CR-06: `account_age_days` is a stale cached integer — eligibility check can be bypassed

**File:** `backend/app/routers/promises.py:182-186` and `backend/app/auth/schemas.py:12`
**Issue:** The account-age check at lines 182-186 reads `user.account_age_days`, which is a column in the `users` table described as "cached; recomputed on login" (auth/schemas.py line 12). A user who registers and is 0 days old can wait 7 real days without logging in again; their stored `account_age_days` remains 0, so they are incorrectly blocked. Conversely, a user who logs in once on day 7, has `account_age_days` set to 7, and then immediately logs in again on day 6 from a different clock (NTP skew, time zone confusion during sign-up, etc.) could have an inflated value. More critically, if an admin or a bug sets `account_age_days` to an arbitrary large value, there is no ground-truth check. The eligibility gate is security-relevant (CLAUDE.md Critical Pitfalls: "vote brigading").

**Fix:** Compute the age from `user.created_at` at request time rather than trusting the cached column:
```python
from datetime import datetime, timezone

account_age = (datetime.now(timezone.utc) - user.created_at).days
if account_age < 7:
    raise HTTPException(
        status_code=403,
        detail="Account must be at least 7 days old to submit promises",
    )
```
This requires that `User.created_at` is stored with timezone info (confirm in the model). Remove the `account_age_days` column from the eligibility path; leave it only for display if needed.

---

## Warnings

### WR-01: `PUT /api/promises/{slug}` returns HTTP 201 — incorrect semantics for a resource update

**File:** `backend/app/routers/promises.py:267`
**Issue:** `@router.put("/{slug}", status_code=201, ...)` returns 201 Created on a successful edit submission. 201 is correct for resource creation; for an operation that inserts a subordinate edit record in response to updating an existing resource, the conventional status is 202 Accepted (edit is pending approval) or 200 OK. Returning 201 to a PUT is non-standard and will confuse API clients and documentation tooling.

**Fix:** Change to `status_code=202` (Accepted — edit queued for moderation) and update any frontend code that checks for `201` on this endpoint.

---

### WR-02: `datetime.utcnow` used as SQLAlchemy column default — produces naive (timezone-unaware) datetimes

**File:** `backend/app/models/promise_edits.py:50`
**Issue:** The column default `default=datetime.utcnow` stores a naive datetime (no tzinfo). The column is declared `DateTime(timezone=True)`, which means PostgreSQL expects a timezone-aware value. SQLAlchemy will store it but will not attach UTC info, so when the value is read back it may be interpreted incorrectly by the application layer or display layer. Python 3.12 deprecates `datetime.utcnow()`.

**Fix:**
```python
from datetime import datetime, timezone

created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
)
```
The same pattern recurs across many other model files (elections.py, politicians.py, promises.py, votes.py, evidence.py, stats_cache.py) — fix globally.

---

### WR-03: `PromiseEditPage` hard-codes `description_hy: null` instead of populating from existing promise data

**File:** `frontend/src/pages/PromiseEditPage.tsx:396`
**Issue:** When building `initialData` for `EditForm`, `description_hy` is always `null`:
```tsx
description_hy: null,
```
The `PromiseDetailOut` schema does not include `description_hy`, so it cannot be hydrated from the API response. This means if a promise has a description, the edit form initialises that field empty. If the user submits without noticing, the edit snapshot will overwrite the description with `null`. Because the append-only design means the approved edit replaces live data (in Phase 6), this will silently erase existing descriptions once an edit is approved.

**Fix:** Either add `description_hy` to `PromiseDetailOut` and propagate it through the `usePromise` hook, or document clearly that description is always cleared on edit. The former is correct.

---

### WR-04: `PromiseSubmitPage` `isEligible` check is purely client-side — form submit button hidden but form is not actually blocked

**File:** `frontend/src/pages/PromiseSubmitPage.tsx:56,340-353`
**Issue:** `isEligible` hides the submit button when the user is ineligible. However, `handleSubmit` is attached to the `<form onSubmit={...}>` element directly. A user can still submit the form programmatically (via JS console or keyboard Enter in a focused input) even when the submit button is hidden, because there is no guard in `handleSubmit` itself. This is a defence-in-depth failure: the backend will correctly block ineligible users with 403, but an ineligible user who bypasses the UI gets a confusing flow where a submit appears to happen, shows an error, and may confuse them about what went wrong.

**Fix:** Add an eligibility guard at the top of `handleSubmit`:
```typescript
async function handleSubmit(e: React.FormEvent) {
  e.preventDefault()
  if (!isEligible) return
  // ...
}
```

---

### WR-05: `usePoliticianSearch` and `useElectionsAll` fetch at most 100 items — silently truncates if database grows

**File:** `frontend/src/hooks/usePoliticianSearch.ts:16`, `frontend/src/hooks/useElectionsAll.ts:14`
**Issue:** Both hooks request `per_page=100` and rely on client-side filtering. If the politician or election count exceeds 100, the combobox/picker will silently omit records. There is no indication to the user that the list is incomplete, and no error is thrown. The current comment references "D-15: election list is ≤20 items in v1" for elections, but no equivalent bound is documented for politicians. This is a latent data-integrity bug as the site scales.

**Fix:** At minimum, check whether `data.total > data.items.length` and log a warning or surface a UI message. For politicians, where the count is unbounded, implement server-side search (debounced query param) rather than client-side filtering.

---

### WR-06: `Dockerfile` uses `--use-deprecated=legacy-resolver` — signals unresolved dependency conflicts

**File:** `backend/Dockerfile:6`
**Issue:** `pip install --use-deprecated=legacy-resolver` suppresses pip's dependency resolver, which was deprecated in pip 22.x and removed in pip 25.x. Its presence means the dependency set has (or had) conflicts that the modern resolver would flag and refuse to install. This flag will cause build failures on pip ≥ 25, and it masks real conflicts in the current dependency set that may manifest at runtime.

**Fix:** Remove the flag and resolve the underlying dependency conflict. Run `pip install -r requirements.txt -r requirements-dev.txt` without the flag to surface the conflict, then pin the conflicting packages to compatible versions.

---

### WR-07: `create_promise` `IntegrityError` handler catches ALL `IntegrityError`s — non-slug constraint violations silently retried

**File:** `backend/app/routers/promises.py:242-254`
**Issue:** The `except IntegrityError:` block is intended to handle slug collisions, but it will also catch FK violations (wrong `politician_id`, wrong `election_id` if the earlier validation somehow passed a stale value), unique constraint violations on `PromiseElectionLink`, and any other integrity error. The retry will then attempt to commit the same invalid data again with a different slug, fail again, and this time propagate an unhandled exception → 500. The handler should discriminate by constraint name.

**Fix:**
```python
except IntegrityError as exc:
    await db.rollback()
    # Only retry for slug uniqueness violations
    if "uq__promises__slug" not in str(exc.orig):
        raise HTTPException(status_code=500, detail="Database constraint violation")
    # ... retry logic
```

---

## Info

### IN-01: `PromiseDetailPage` shows edit link to all authenticated users, including those with `account_age_days < 7`

**File:** `frontend/src/pages/PromiseDetailPage.tsx:107-113`
**Issue:** The "Խмбер" (Edit) link is shown to any `state.user` regardless of eligibility. Clicking it for an ineligible user navigates to the edit page, which renders the edit form, but the submit button is hidden. The UX is confusing — an ineligible user sees a functional-looking edit form with no way to submit.

**Fix:** Mirror the `isEligible` guard from `PromiseSubmitPage`:
```tsx
{state.user && state.user.is_verified && state.user.account_age_days >= 7 && (
  <Link to={`/promises/${data.slug}/edit`} ...>Խmbarate</Link>
)}
```

---

### IN-02: `PromisesListPage` success banner triggers on URL parameter but never clears the URL — banner reappears on refresh

**File:** `frontend/src/pages/PromisesListPage.tsx:28`
**Issue:** `showBanner` is initialised from `searchParams.get("submitted") === "1"`. The `submitted=1` param is never removed from the URL, so if the user refreshes the page the banner will reappear, suggesting a new submission occurred.

**Fix:** After setting `showBanner(true)`, remove the parameter from the URL:
```typescript
const [showBanner, setShowBanner] = useState(() => {
  const show = searchParams.get("submitted") === "1"
  if (show) {
    // Remove ?submitted=1 from URL without triggering navigation
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      next.delete("submitted")
      return next
    }, { replace: true })
  }
  return show
})
```

---

### IN-03: `combobox.tsx` `CommandItem` uses `value={item.label}` for cmdk filtering — items with identical labels become indistinguishable

**File:** `frontend/src/components/ui/combobox.tsx:76-83`
**Issue:** `<CommandItem value={item.label} ...>` passes the human-readable label as the cmdk filter key. If two politicians share the same display name (possible for Armenian politicians with identical names), cmdk will treat them as one item for filtering purposes and may deduplicate them visually. The selection logic (`onChange(item.value === value ? "" : item.value)`) uses `item.value` (the UUID) correctly, but filtering breaks.

**Fix:** Use `item.value` as the cmdk value and implement a custom `filter` prop on `<Command>` to search against `item.label` instead:
```tsx
<Command filter={(itemValue, search) => {
  const item = items.find(i => i.value === itemValue)
  return item?.label.toLowerCase().includes(search.toLowerCase()) ? 1 : 0
}}>
```

---

### IN-04: `backend/tests/test_promises.py` — six Phase 5 tests are permanently skipped with `pytest.skip`

**File:** `backend/tests/test_promises.py:210,235,282,291,300`
**Issue:** Six tests for the core Phase 5 requirements (PROM-03, PROM-04, ELEC-03) are unconditionally skipped with `pytest.skip(...)`. The `verified_user_client` fixture is actually defined in the same file (lines 21-76), so the stated reason for skipping ("fixture needed") is no longer accurate. These tests cover the primary deliverable of the phase and should be passing.

**Fix:** Remove the `pytest.skip(...)` calls from:
- `test_create_promise` (line 210)
- `test_create_promise_unverified` (line 235)
- `test_create_promise_invalid_election` (line 282)
- `test_create_promise_with_elections` (line 291)
- `test_edit_promise_creates_edit_row` (line 300)

Then wire up the test bodies using the `verified_user_client` fixture.

---

_Reviewed: 2026-05-25T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
