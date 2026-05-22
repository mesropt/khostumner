---
status: testing
phase: 02-politicians-parties-elections-browsing
source: 02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md
started: 2026-05-22T19:00:00Z
updated: 2026-05-22T19:00:00Z
---

## Current Test

number: 1
name: Cold Start Smoke Test
expected: |
  Kill any running containers. Run `docker-compose up --build`.
  Postgres starts healthy, backend runs alembic migrations and seed without errors,
  uvicorn starts on port 8000. Opening http://localhost:8000/docs returns the Swagger UI.
  Opening http://localhost:5173 returns the React app.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running containers. Run `docker-compose up --build`. Postgres starts healthy, backend runs alembic migrations and seed without errors, uvicorn starts on port 8000. Opening http://localhost:8000/docs returns the Swagger UI. Opening http://localhost:5173 returns the React app.
result: [pending]

### 2. Navigation Header
expected: At http://localhost:5173, a sticky header shows 5 links: "Խոստumner" (logo/home), "Կatarvaç", "Çkatarvaç", "Անձinnq", "Yntrutyunner". Clicking "Անձinnq" highlights it (bold/dark). Clicking "Yntrutyunner" highlights it. Unvisited links are grey.
result: [pending]

### 3. Persons List Page (/persons)
expected: Navigating to /persons shows a grid of politician cards. Each card shows the politician's name, party badge, and avatar (photo or initials). Two filter dropdowns exist: "Կusaktsutyun" (party) and "Makardaq" (level). Selecting a filter updates the list. Pagination appears if more than one page exists.
result: [pending]

### 4. Politician Profile Page (/persons/:slug)
expected: Clicking a politician card navigates to /persons/{slug}. The page shows: politician's full name, avatar, bio text, list of their promises (if any exist in seed data), and a back link "Վeradarnał անżanqi ców'ak". If promises exist, each shows a truncated quote and a status badge.
result: [pending]

### 5. Politician 404 State
expected: Navigating to /persons/nonexistent-slug shows: "Անżн чи гтнвel" heading and a link "Վeradarnał անżanqi ców'ak" that goes back to /persons.
result: [pending]

### 6. Party Page (/parties/:slug)
expected: Navigating to /parties/{slug} (e.g. /parties/hhk) shows: party name, avatar (logo or initials), founded year. A members section shows politician cards for active members. A promises section shows approved promises with pagination. A back link returns to /persons.
result: [pending]

### 7. Party 404 State
expected: Navigating to /parties/nonexistent shows: "Կusaktsutyunnн чи гтнвel" heading and a back link to /persons.
result: [pending]

### 8. Elections List Page (/elections)
expected: Navigating to /elections shows election cards. Each card shows the election name, level badge (e.g. "ازгаyinnq"), and a promise count (e.g. "3 Honesty"). Pagination appears if more than one page. Skeleton loaders appear briefly while loading.
result: [pending]

### 9. Election Detail Page (/elections/:slug)
expected: Clicking an election card navigates to /elections/{slug}. The page shows: election name/date, a list of linked approved promises shown as PromiseStub components, and a back link "Վeradarnał Yntrutyunnneri ców'ak".
result: [pending]

### 10. Election 404 State
expected: Navigating to /elections/nonexistent shows a 404 message with a back link to /elections.
result: [pending]

## Summary

total: 10
passed: 0
issues: 0
pending: 10
skipped: 0
blocked: 0

## Gaps

[none yet]
