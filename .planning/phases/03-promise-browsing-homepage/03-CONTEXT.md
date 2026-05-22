# Phase 3: Promise Browsing & Homepage - Context

**Gathered:** 2026-05-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the promise browsing experience: a real homepage with statistics, a general paginated promise list with full filters, focused Fulfilled/Unfulfilled section pages, promise detail pages (verbatim quote, source, status, dates), and OG-tag support for social sharing. Any visitor (unauthenticated) can access all of this.

No write operations, no voting, no user authentication. Tags, chronicle, "Верю/Не верю" polling, and politician-initiated promise updates are deferred to later phases.

The nav links Կatarвak (`/fulfilled`) and Չkatarвak (`/unfulfilled`) that currently 404 get real pages in this phase. A new nav section **Մեր մասին** (`/about`) is also added — a static informational page.

</domain>

<decisions>
## Implementation Decisions

### Homepage (DISC-01)

- **D-01:** Homepage shows two sections: (1) a stats block with counts per resolved_status (kept, broken, in_progress, stalled, not_rated) + total; (2) last 5–10 promises sorted by `created_at` desc.
- **D-02:** Stats are fetched from `GET /api/stats` — a dedicated endpoint returning `{ total: N, by_status: { kept, broken, in_progress, stalled, not_rated } }`. Promises are fetched via `GET /api/promises?per_page=10` (existing promises endpoint, once built).
- **D-03:** Homepage replaces the current health-check placeholder entirely.

### Section Pages (DISC-02, DISC-03)

- **D-04:** Three separate routes/pages for promise browsing:
  - `/promises` — full paginated list with all filters (PROM-01)
  - `/fulfilled` — filtered to `resolved_status=kept` only, paginated (DISC-02)
  - `/unfulfilled` — filtered to `resolved_status=broken` OR `resolved_status=stalled`, paginated (DISC-03)
- **D-05:** `/fulfilled` and `/unfulfilled` show focused views without the full filter UI — they are clean, titled pages ("Կatarвak" / "Չkatarвak") showing only their relevant promises.
- **D-06:** `/promises` exposes full filter set: status, politician, election, made_date range (from/to), expected_date range (from/to). All filters are server-side query params, shareable via URL (pattern from Phase 2 D-04).
- **D-07:** Date filters use from/to date range (two date inputs). Promises without dates (`made_date=null`, `expected_date=null`) are NOT excluded when a date filter is not applied; they simply don't match when a date filter IS applied.
- **D-07b:** **Бессрочные обещания** (open-ended, no deadline) — `expected_date=null` AND no condition string — are valid and must be handled gracefully throughout: no "срок истёк" logic, no filtering them out of `/unfulfilled` or `/fulfilled` based on date, no "active until date" badge. They simply show without any deadline row on the detail page.

### Promise List API (PROM-01)

- **D-08:** `GET /api/promises` accepts: `?status=`, `?politician_id=`, `?election_id=`, `?made_date_from=`, `?made_date_to=`, `?expected_date_from=`, `?expected_date_to=`, `?page=`, `?per_page=`. All optional.
- **D-09:** Response uses the existing `PaginatedResponse[T]` envelope (from `app/schemas/common.py`). Promise list item schema (`PromiseListOut`) includes: id, slug, title_hy, quote_hy (first ~120 chars for list), resolved_status, politician name, made_date.
- **D-10:** Only `moderation_status=approved` promises are returned on all public endpoints (carry-forward from Phase 2).

### Promise Detail Page (PROM-02)

- **D-11:** Layout hierarchy: verbatim quote (`quote_hy`) is the visual hero — displayed large, full text, no truncation. Below: status badge, politician name (linked to `/persons/{slug}`), made_date, expected_date (if present). If a date is null, that row is omitted entirely.
- **D-12:** Source link shown as a button/link labelled "Աղբյուր" opening in a new tab (`target=_blank`). If `archived_url` is also present, show a secondary link "Wayback Machine" as a fallback.
- **D-13:** `title_hy` shown as page heading above the quote.
- **D-14:** `GET /api/promises/{slug}` returns a `PromiseDetailOut` schema: all Promise fields + politician name_hy + politician slug (for linking).

### Open Graph Tags (DISC-05)

- **D-15:** OG tags are served by FastAPI for bot user-agents. Architecture: Nginx (or Docker Compose routing) forwards requests to `/promises/{slug}` from known bot user-agents (Facebookbot, TelegramBot, Twitterbot, LinkedInBot) to a FastAPI endpoint `GET /api/og/promises/{slug}` which returns a minimal HTML page with `<meta og:*>` tags. Regular browser requests continue to the Vite SPA.
- **D-16:** OG preview content: `og:title` = `title_hy`, `og:description` = first 150 chars of `quote_hy` + " — " + politician `name_hy`, `og:image` = politician `photo_url` (if present; fall back to site default image), `og:url` = canonical promise URL.
- **D-17:** Bot detection is done in the Docker Compose / reverse-proxy layer by inspecting the `User-Agent` header — NOT in FastAPI application code. FastAPI's `/api/og/promises/{slug}` endpoint is a plain HTML-returning route, called only when the proxy routes to it.

### About Page (Մեր մասին)

- **D-18:** Add nav link **Մեր մասին** to the Layout header, routing to `/about`. Positioned last in the nav.
- **D-19:** `/about` is a **static page** — no API calls. Content is hardcoded in the React component (no CMS). Written in Armenian (հայերեն).
- **D-20:** Content covers two topics: (1) the principles by which promises are collected (verbatim quotes required, source links required, moderation process); (2) why this project exists (mission statement). The actual text will be provided by the user before Phase 3 execution — the file `Our Principles` in the project root is the intended source. If content is not ready at planning time, the component renders a placeholder with clear TODO comments.
- **D-21:** No backend changes needed for `/about`. Frontend-only: new route + new static page component.

### Claude's Discretion

- Promise list card vs list layout on `/promises` — use a compact list (not card grid) since promises are text-heavy; consistent with the election list in Phase 2.
- Status badge colors on promise list — follow Phase 2 established colors (kept=green, broken=red, in_progress=yellow, stalled=gray, not_rated=neutral).
- Pagination on `/fulfilled` and `/unfulfilled` — same shadcn Pagination component as Phase 2.
- Date input component for date range filter — use shadcn `<Input type="date">` (no date picker library needed for Phase 3).
- Mobile nav — deferred from Phase 2; Claude may address it in this phase if the homepage layout naturally creates the opportunity.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Foundation
- `.planning/PROJECT.md` — Core constraints: Armenian-only UI, anonymous browsing, FastAPI + React + PostgreSQL stack
- `.planning/REQUIREMENTS.md` — Phase 3 requirements: PROM-01, PROM-02, DISC-01, DISC-02, DISC-03, DISC-05 (lines 18–20, 48–53)
- `.planning/ROADMAP.md` — Phase 3 goal, 6 success criteria, dependency on Phase 2

### Phase 2 Decisions (carry forward)
- `.planning/phases/02-politicians-parties-elections-browsing/02-CONTEXT.md` — D-04 (server-side filter params), D-06 (promise stub format), D-07 (/promises/{slug} URL locked), D-09/D-10/D-11 (PaginatedResponse, pagination pattern)

### Data Model
- `backend/app/models/promises.py` — `Promise` model (fields: title_hy, quote_hy, slug, made_date, expected_date, source_url, archived_url, moderation_status, resolved_status, politician_id)
- `backend/app/models/politicians.py` — `Politician` model (name_hy, slug, photo_url — needed for OG image and detail page link)
- `backend/app/schemas/promises.py` — existing `PromiseStubOut` (reused on entity pages); Phase 3 adds `PromiseListOut` and `PromiseDetailOut`
- `backend/app/schemas/common.py` — `PaginatedResponse[T]` generic envelope — MUST be used for all list endpoints

### Frontend Patterns
- `frontend/src/App.tsx` — route registry; Phase 3 adds `/`, `/promises`, `/fulfilled`, `/unfulfilled`, `/promises/:slug`, `/about`
- `frontend/src/pages/ElectionsListPage.tsx` — template for a clean filtered list page (card layout, loading/error states)
- `frontend/src/components/Layout.tsx` — existing nav; `/fulfilled` and `/unfulfilled` already linked (currently 404); `/about` (Մեր մասին) is a new nav link added in Phase 3

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/PromiseStub.tsx` — promise stub component (truncated quote + status badge) — reused on `/promises` list and homepage recent promises
- `frontend/src/components/PaginationControls.tsx` — pagination UI — reused on `/promises`, `/fulfilled`, `/unfulfilled`
- `backend/app/routers/elections.py` — template for a list + detail router pattern (query filtering, PaginatedResponse, JOINs) — replicate for promises router
- `backend/app/schemas/elections.py` — template schema structure for a list item vs detail item

### Established Patterns
- **TanStack Query hook**: `useElections` / `useParty` hooks — follow same pattern for `usePromises`, `usePromise`, `useStats`
- **Server-side filters via useSearchParams**: established in `PersonsPage.tsx` — follow exactly for `/promises` filters
- **PaginatedResponse**: mandatory envelope for all list endpoints — already in `app/schemas/common.py`
- **moderation_status=approved filter**: MUST be applied on all public promise queries — established in Phase 2 routers

### Integration Points
- `backend/app/main.py` — add `include_router(promises.router, prefix="/api")` and `include_router(stats.router, prefix="/api")`
- `frontend/src/App.tsx` — add routes: `/` (replace HomePage), `/promises`, `/fulfilled`, `/unfulfilled`, `/promises/:slug`
- Docker Compose / Nginx — add bot user-agent routing rule for OG endpoint (D-17)

</code_context>

<specifics>
## Specific Ideas

- The homepage "last 5–10 promises" should show promises from different politicians — not 10 promises from the same person. Consider `ORDER BY created_at DESC LIMIT 10` which naturally gives recent ones; seed data is diverse enough.
- OG image falls back to a site default image if `photo_url` is null — define a static default image asset in Phase 3.
- The "Wayback Machine" fallback link (D-12) uses `archived_url` which the Promise model already has — no schema change needed.
- **Бессрочные обещания** (D-07b): пример — "Мы реализуем идею подарить каждой семье флаг". Никакого `expected_date`, никакого условия. Отображать без строки срока; фильтры по дате их не задевают.
- **Файл `Our Principles`** в корне проекта — будущий источник текста для страницы `/about`. Пустой на момент контекста — исполнитель ставит TODO-placeholder и ждёт текста от пользователя перед деплоем.

</specifics>

<deferred>
## Deferred Ideas

- **Tags / Labels** (теги: транспорт, сельское хозяйство и т.д.) — Requires `tags` table + M2M + tag selection UI on promise submission. Belongs in Phase 5 (Promise Submission) when the submission form is built. Tag filtering on `/promises` can be added in Phase 5 as well.
- **Chronicle / Topic grouping** (хроника по теме — напр. все обещания по аэропорту) — New entity "topic/campaign" grouping related promises. Significant feature; defer to Phase 6+ after core content model is stable.
- **«Верю/Не верю» credibility poll** — Per-promise user poll ("I believe" / "I don't believe") with vote count display; active until `expected_date`, shows frozen results after. Different from Phase 7 resolved_status voting. Requires auth (Phase 4). Suggest implementing in Phase 7 alongside the main voting system.
- **Politician-initiated promise update** (перенос даты / обновление условий) — Politician extends deadline or adds conditions. Requires verified politician account + edit history + moderation. Belongs in Phase 6 (Admin Moderation) or a dedicated Phase 5.5.
- **Mobile hamburger nav** — Deferred from Phase 2. May be addressed in Phase 3 if layout work creates the natural opportunity, but not a hard requirement.

</deferred>

---

*Phase: 3-Promise-Browsing-Homepage*
*Context gathered: 2026-05-22*
