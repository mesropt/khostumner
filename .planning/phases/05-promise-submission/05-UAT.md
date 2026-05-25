---
status: complete
phase: 05-promise-submission
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md, 05-03-SUMMARY.md, 05-04-SUMMARY.md, 05-05-SUMMARY.md]
started: 2026-05-25T00:00:00Z
updated: 2026-05-25T00:00:00Z
---

## Current Test

complete: true

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server. Start backend (docker compose up or uvicorn) and frontend (npm run dev) from scratch. Alembic migration 20260524_000001_add_promise_edits applies without errors ("type already exists" must NOT appear). The /api/promises endpoint returns a 200 JSON response with an "items" array. The frontend homepage loads without console errors.
result: pass

### 2. Nav Link "Ներкayacnel" Visible
expected: Open any page of the site (e.g. homepage). The top navigation bar contains the link "Ներкayacnel" between "Ընtrut'unn" (Elections) and "Mer mais" (About). Clicking it navigates to /promises/new.
result: pass

### 3. Unauthenticated Redirect for /promises/new
expected: While logged out, navigate directly to /promises/new (or click "Ներкayacnel" while logged out). You should be redirected to the /login page, not see the submit form.
result: pass

### 4. Eligibility Gate for Ineligible User
expected: Log in with a freshly registered account (less than 7 days old OR not yet email-verified). Navigate to /promises/new. You should see the form sections but instead of the submit button, an inline message states that account verification or age requirement is not met (no submit button visible).
result: pass

### 5. Promise Submit Form Structure
expected: Log in as an eligible user (verified + account ≥ 7 days). Navigate to /promises/new. The page shows two sections: Section 1 (Ով — "Who") contains a politician search combobox and an optional election toggle. Toggling the election checkbox reveals a level selector (RadioGroup) and a list of elections to check. Section 2 (Ինч+Erby — "What & When") contains: title field, verbatim quote textarea, source URL field, made date, expected date, and optional description. Required fields are marked.
result: pass

### 6. Submit a New Promise
expected: Fill in the promise form as an eligible authenticated user: pick any politician from the combobox, enter a title (≥5 chars), a quote (≥10 chars), a valid https:// source URL. Click submit. The request succeeds, and you are redirected to /promises where a green success banner appears at the top of the page.
result: pass

### 7. Success Banner on Promises List
expected: Immediately after submitting a promise (previous test) you land on /promises with a green dismissible banner saying the promise was submitted for review. Clicking the dismiss (×) button removes the banner. If you navigate away and come back to /promises (without ?submitted=1 in the URL) the banner is NOT shown.
result: pass

### 8. Edit Link Visibility on Promise Detail
expected: Find any approved promise and open its detail page. When you are NOT logged in: no edit link is visible anywhere on the page. When you log in and reload the same detail page: an edit link (Armenian text "Խmbragrurel") appears below the source link. Clicking it takes you to /promises/:slug/edit.
result: pass

### 9. Edit Form Pre-fills Content Fields
expected: Navigate to /promises/:slug/edit for any approved promise (logged in). The form loads with: title_hy pre-filled from the promise, quote_hy pre-filled, source_url pre-filled. The made_date and expected_date fields are pre-filled if the promise has them. The politician is shown in a read-only display (Label + text, no combobox). The form has an edit notice explaining that the edit will go to moderation.
result: pass

### 10. Submit a Promise Edit
expected: On the edit form (/promises/:slug/edit), modify the title or quote, then click the submit button. The request succeeds and you are redirected to /promises?submitted=1 where the green success banner appears. The original promise detail page still shows the original content (edit goes to moderation queue, live row is NOT changed).
result: pass

## Summary

total: 10
passed: 10
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
