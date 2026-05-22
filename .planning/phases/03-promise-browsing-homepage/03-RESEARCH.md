# Phase 3: Promise Browsing & Homepage — Research

**Researched:** 2026-05-23
**Domain:** FastAPI list/detail endpoints with multi-field filtering; React SPA read-only browsing pages; Nginx/Docker Compose bot user-agent routing for Open Graph
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Homepage (DISC-01)**
- D-01: Homepage shows two sections: (1) stats block with counts per resolved_status (kept, broken, in_progress, stalled, not_rated) + total; (2) last 5–10 promises sorted by `created_at` desc.
- D-02: Stats fetched from `GET /api/stats`; promises from `GET /api/promises?per_page=10`.
- D-03: Homepage replaces the current health-check placeholder entirely.

**Section Pages (DISC-02, DISC-03)**
- D-04: Three separate routes: `/promises` (full filtered list), `/fulfilled` (kept), `/unfulfilled` (broken OR stalled).
- D-05: `/fulfilled` and `/unfulfilled` have no full filter UI — clean focused pages.
- D-06: `/promises` exposes full filter set: status, politician, election, made_date range, expected_date range. All filters are server-side query params, shareable via URL.
- D-07: Date filters use from/to date range. Promises without dates are not excluded when filter is not applied.
- D-07b: Open-ended promises (`expected_date=null`, no condition string) are valid; no "срок истёк" logic, no filtering out, no deadline badge. Show without deadline row on detail page.

**Promise List API (PROM-01)**
- D-08: `GET /api/promises` accepts: `?status=`, `?politician_id=`, `?election_id=`, `?made_date_from=`, `?made_date_to=`, `?expected_date_from=`, `?expected_date_to=`, `?page=`, `?per_page=`. All optional.
- D-09: Response uses `PaginatedResponse[T]` from `app/schemas/common.py`. `PromiseListOut` includes: id, slug, title_hy, quote_hy (first ~120 chars), resolved_status, politician name, made_date.
- D-10: Only `moderation_status=approved` promises on all public endpoints.

**Promise Detail Page (PROM-02)**
- D-11: `quote_hy` is visual hero — full text, no truncation. Below: status badge, politician name (linked), made_date, expected_date (if present; omit row if null).
- D-12: "Աղբյուր" source button + optional "Wayback Machine" (`archived_url`) fallback link.
- D-13: `title_hy` as page H1.
- D-14: `GET /api/promises/{slug}` returns `PromiseDetailOut` with all Promise fields + politician `name_hy` + politician `slug`.

**Open Graph Tags (DISC-05)**
- D-15: Nginx (Docker Compose routing) forwards bot user-agents to `GET /api/og/promises/{slug}` which returns minimal HTML with `<meta og:*>` tags. Browser requests go to SPA.
- D-16: `og:title` = `title_hy`, `og:description` = first 150 chars of `quote_hy` + " — " + politician `name_hy`, `og:image` = politician `photo_url` (fallback to site default), `og:url` = canonical promise URL.
- D-17: Bot detection in Docker Compose / reverse-proxy layer inspecting `User-Agent` — NOT in FastAPI application code.

**About Page**
- D-18: "Մեր մասին" nav link added last in Layout header, routing to `/about`.
- D-19: `/about` is a static page — no API calls. Content hardcoded in React component.
- D-20: Content from `Our Principles` file in project root. If not ready, component renders placeholder with TODO comments.
- D-21: No backend changes for `/about`. Frontend-only.

### Claude's Discretion

- Promise list card vs list layout on `/promises` — use a compact list (not card grid).
- Status badge colors — carry forward from Phase 2 (kept=green, broken=red, in_progress=yellow, stalled=gray, not_rated=neutral).
- Pagination on `/fulfilled` and `/unfulfilled` — same shadcn Pagination component as Phase 2.
- Date input component — use shadcn `<Input type="date">` (no date picker library).
- Mobile nav — may address if homepage layout creates the opportunity; not a hard requirement.

### Deferred Ideas (OUT OF SCOPE)

- Tags / Labels — deferred to Phase 5 (Promise Submission).
- Chronicle / Topic grouping — deferred to Phase 6+.
- "Верю/Не верю" credibility poll — deferred to Phase 7.
- Politician-initiated promise update — deferred to Phase 6 or Phase 5.5.
- Mobile hamburger nav — deferred; may be incidental in Phase 3.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROM-01 | Anyone can view paginated promise list with filtering by status, politician, and election | Backend: `GET /api/promises` with 7 optional query params + `PaginatedResponse[PromiseListOut]`. Frontend: `PromisesListPage` with `useSearchParams` filter pattern from `PersonsPage.tsx`. |
| PROM-02 | Anyone can view promise detail page (verbatim quote, dates, status badge, source links, shareable slug URL) | Backend: `GET /api/promises/{slug}` returning `PromiseDetailOut`. Frontend: `PromiseDetailPage` with quote hero + metadata + source buttons. |
| DISC-01 | Homepage displays overall statistics (total promises, fulfillment breakdown by status) | Backend: `GET /api/stats` returning `{ total, by_status }`. Frontend: `HomePage` replacing health-check placeholder. |
| DISC-02 | "Կատարված" (Fulfilled) section shows all promises with fulfilled status, paginated | Frontend: `FulfilledPage` passing `?status=kept` to promises endpoint. No new backend needed beyond the promises list endpoint. |
| DISC-03 | "Չկատարված" (Not Fulfilled) section shows promises with broken or stalled status, paginated | Frontend: `UnfulfilledPage` — requires API to accept comma-separated or multi-value status param (`broken,stalled`). |
| DISC-05 | Promise detail pages include Open Graph meta tags for social sharing | Backend: `GET /api/og/promises/{slug}` returning minimal HTML. Docker Compose: Nginx bot-UA routing rule. No React SPA changes. |
</phase_requirements>

---

## Summary

Phase 3 is a read-only content delivery phase. The backend work is entirely new router work — a `promises` router (list + detail) and a `stats` router — both following the established pattern from `elections.py`. The frontend work replaces the health-check homepage and adds six new pages/routes.

The most technically novel piece is the Open Graph bot-routing requirement (DISC-05): no Nginx service currently exists in the Docker Compose stack. The dev compose runs a bare Vite dev server on port 5173 and the FastAPI backend on port 8000. Adding bot user-agent routing in dev requires either adding a new `nginx` service to `docker-compose.yml` or accepting that OG tag routing is a production-only concern with a stub endpoint in dev. The context decision (D-17) specifies Docker Compose / Nginx layer — so an Nginx sidecar is needed.

For the `/unfulfilled` route, the promises endpoint must accept multiple status values. The simplest approach: accept a comma-separated `?status=broken,stalled` string that the router splits and uses in a `WHERE resolved_status IN (...)` clause. This does not require a multi-value query param change to the FastAPI signature beyond splitting the string.

**Primary recommendation:** Build the promises router first (Wave 1 Wave 0 + schema), then homepage + section pages (Wave 2), then promise detail (Wave 3), then OG endpoint + Nginx routing (Wave 4).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Promise list with filters | API / Backend | Frontend Server (SPA fetch) | Filtering, pagination, and moderation gating belong in the database query layer |
| Promise detail data | API / Backend | Frontend Server (SPA fetch) | All data fields including politician join come from the database |
| Homepage stats aggregation | API / Backend | — | Counting promises by resolved_status is a database operation; never computed client-side |
| OG meta tag HTML | API / Backend | Nginx / Proxy | FastAPI returns the minimal HTML page; Nginx routes bot UAs to it |
| Bot user-agent detection | CDN / Nginx proxy | — | D-17: explicitly placed here, not in app code |
| Page rendering (all 6 pages) | Browser / Client (SPA) | — | React SPA fetches from API; no SSR |
| URL filter state | Browser / Client (SPA) | — | `useSearchParams` pattern from Phase 2 |
| About page content | Browser / Client (SPA) | — | Static component, no API tier involved |

---

## Standard Stack

### Core (carry-forward from Phase 1/2 — no new installs)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115.x | Promise list/detail/stats/OG routers | Project standard [ASSUMED] |
| SQLAlchemy 2.x async | 2.x | ORM queries with JOIN for detail endpoint | Project standard [ASSUMED] |
| Pydantic v2 | bundled with FastAPI | `PromiseListOut`, `PromiseDetailOut`, `StatsOut` schemas | Project standard [ASSUMED] |
| React 19 + Vite | 19/6 | SPA pages | Project standard [ASSUMED] |
| TanStack Query v5 | 5.x | `usePromises`, `usePromise`, `useStats` hooks | Project standard [ASSUMED] |
| React Router DOM v7 | 7.x | New routes: `/`, `/promises`, `/fulfilled`, `/unfulfilled`, `/promises/:slug`, `/about` | Project standard [ASSUMED] |
| Tailwind CSS v4 | 4.x | Styling per UI-SPEC | Project standard [ASSUMED] |
| shadcn/ui | latest | New: `input`, `separator` components; reuse: `badge`, `button`, `card`, `pagination`, `select` | Project standard [ASSUMED] |

### New shadcn components (Phase 3 additions)
```bash
npx shadcn@latest add input separator
```
Both are official shadcn registry — no third-party registries. [VERIFIED: ui.shadcn.com registry]

### New Infrastructure (Phase 3 addition)
| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| Nginx | 1.25-alpine (Docker) | Bot UA routing for OG tags | New service in docker-compose.yml |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Nginx bot-routing in Docker Compose | Next.js SSR for OG tags | Project uses React SPA + FastAPI; Next.js would require full stack replacement |
| Nginx bot-routing | UA detection in FastAPI middleware | D-17 explicitly prohibits UA detection in app code |
| Comma-separated `?status=` param | Multiple `?status[]=` params | Comma-separated is simpler for the existing `apiClient.get()` URL construction pattern |

---

## Package Legitimacy Audit

No new npm or PyPI packages are being installed in Phase 3 beyond official shadcn registry components (`input`, `separator` — both from `https://ui.shadcn.com/r/`, the official shadcn registry). The Nginx Docker image is the official `nginx:alpine` from Docker Hub.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| shadcn input | ui.shadcn.com/r/ | Official registry | N/A | github.com/shadcn-ui/ui | N/A — official | Approved |
| shadcn separator | ui.shadcn.com/r/ | Official registry | N/A | github.com/shadcn-ui/ui | N/A — official | Approved |
| nginx:alpine | Docker Hub official | Years | Millions | docker.com/r/library/nginx | N/A — official image | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
Browser (regular)              Browser (Googlebot / TelegramBot etc.)
      |                                        |
      v                                        v
  Nginx :80                              Nginx :80
      |                                        |
      | UA not a bot                           | UA matches bot pattern
      v                                        v
  Vite SPA :5173              FastAPI /api/og/promises/{slug} :8000
  (React Router)                    |
      |                             v
      | fetch /api/...        Returns minimal HTML
      v                       <meta og:title, og:description,
  FastAPI :8000                og:image, og:url>
      |
      v
  PostgreSQL :5432
```

Data flow for promise list:
```
GET /api/promises?status=kept&politician_id=X&page=2
  → promises router
  → SELECT promises JOIN politicians WHERE moderation_status=approved
    AND resolved_status=kept AND politician_id=X
    OFFSET 20 LIMIT 20
  → PaginatedResponse[PromiseListOut]
  → TanStack Query cache → PromisesListPage render
```

Data flow for stats:
```
GET /api/stats
  → stats router
  → SELECT resolved_status, COUNT(*) FROM promises
    WHERE moderation_status=approved GROUP BY resolved_status
  → { total: N, by_status: { kept: N, broken: N, ... } }
  → HomePage stats block render
```

### Recommended Project Structure — New Files

```
backend/app/
├── routers/
│   ├── promises.py          # GET /api/promises, GET /api/promises/{slug}
│   ├── stats.py             # GET /api/stats
│   └── og.py                # GET /api/og/promises/{slug}  (returns HTML)
├── schemas/
│   └── promises.py          # Add PromiseListOut, PromiseDetailOut (existing file)

frontend/src/
├── pages/
│   ├── HomePage.tsx         # Replace health-check placeholder (D-03)
│   ├── PromisesListPage.tsx # /promises — full filtered list (PROM-01)
│   ├── FulfilledPage.tsx    # /fulfilled — kept only (DISC-02)
│   ├── UnfulfilledPage.tsx  # /unfulfilled — broken,stalled (DISC-03)
│   ├── PromiseDetailPage.tsx # /promises/:slug (PROM-02)
│   └── AboutPage.tsx        # /about — static page (D-19)
├── components/
│   └── PromiseCard.tsx      # Promise list row: title + truncated quote + badge + meta
├── hooks/
│   ├── usePromises.ts       # TanStack Query hook for list endpoint
│   ├── usePromise.ts        # TanStack Query hook for detail endpoint
│   └── useStats.ts          # TanStack Query hook for stats endpoint
├── types/
│   └── index.ts             # Add PromiseListOut, PromiseDetailOut, StatsOut interfaces

nginx/
└── nginx.conf               # Bot UA routing configuration

docker-compose.yml           # Add nginx service
```

### Pattern 1: Promise List Router with Multi-Field Filtering

Extends the established `elections.py` pattern. Key addition: optional filters each become an `.where()` clause added conditionally.

```python
# Source: backend/app/routers/elections.py — adapted pattern
@router.get("", response_model=PaginatedResponse[PromiseListOut])
async def list_promises(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),           # comma-separated for multi-value
    politician_id: uuid.UUID | None = Query(None),
    election_id: uuid.UUID | None = Query(None),
    made_date_from: date | None = Query(None),
    made_date_to: date | None = Query(None),
    expected_date_from: date | None = Query(None),
    expected_date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PromiseListOut]:
    stmt = (
        select(Promise, Politician.name_hy.label("politician_name"), Politician.slug.label("politician_slug"))
        .join(Politician, Politician.id == Promise.politician_id)
        .where(Promise.moderation_status == ModerationStatus.approved)
    )
    if status:
        status_values = [ResolvedStatus(s.strip()) for s in status.split(",")]
        stmt = stmt.where(Promise.resolved_status.in_(status_values))
    if politician_id:
        stmt = stmt.where(Promise.politician_id == politician_id)
    if election_id:
        stmt = stmt.join(PromiseElectionLink, PromiseElectionLink.promise_id == Promise.id) \
                   .where(PromiseElectionLink.election_id == election_id)
    if made_date_from:
        stmt = stmt.where(Promise.made_date >= made_date_from)
    if made_date_to:
        stmt = stmt.where(Promise.made_date <= made_date_to)
    if expected_date_from:
        stmt = stmt.where(Promise.expected_date >= expected_date_from)
    if expected_date_to:
        stmt = stmt.where(Promise.expected_date <= expected_date_to)
    # count + paginate follow same pattern as elections.py
```

**Important:** The JOIN with `Politician` required for `PromiseListOut.politician_name` means rows are `(Promise, politician_name, politician_slug)` tuples — same Row-tuple unpacking pattern as `ElectionWithCountOut` in `02-04`. `PromiseListOut` must be a plain `BaseModel` (no `from_attributes`) if constructed from Row tuples.

### Pattern 2: Stats Endpoint (Aggregate Query)

```python
# Source: [ASSUMED] — SQLAlchemy func.count with GROUP BY pattern
@router.get("", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsOut:
    stmt = (
        select(Promise.resolved_status, func.count().label("cnt"))
        .where(Promise.moderation_status == ModerationStatus.approved)
        .group_by(Promise.resolved_status)
    )
    result = await db.execute(stmt)
    rows = result.all()
    by_status = {r.resolved_status: r.cnt for r in rows}
    total = sum(by_status.values())
    return StatsOut(
        total=total,
        by_status=StatsByStatus(
            kept=by_status.get(ResolvedStatus.kept, 0),
            broken=by_status.get(ResolvedStatus.broken, 0),
            in_progress=by_status.get(ResolvedStatus.in_progress, 0),
            stalled=by_status.get(ResolvedStatus.stalled, 0),
            not_rated=by_status.get(ResolvedStatus.not_rated, 0),
        ),
    )
```

### Pattern 3: OG Endpoint Returning Raw HTML

```python
# Source: [ASSUMED] — FastAPI HTMLResponse pattern
from fastapi.responses import HTMLResponse

@router.get("/promises/{slug}", response_class=HTMLResponse)
async def og_promise(slug: str, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    # fetch promise + politician
    # build og:* meta tags
    html = f"""<!DOCTYPE html><html><head>
    <meta property="og:title" content="{title_hy}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{image_url}" />
    <meta property="og:url" content="{canonical_url}" />
    </head><body></body></html>"""
    return HTMLResponse(content=html)
```

### Pattern 4: Nginx Bot User-Agent Routing

```nginx
# nginx.conf — [ASSUMED] pattern for bot UA routing
map $http_user_agent $is_bot {
    default 0;
    "~*Facebookbot"   1;
    "~*Twitterbot"    1;
    "~*TelegramBot"   1;
    "~*LinkedInBot"   1;
    "~*Googlebot"     1;
}

server {
    listen 80;

    location ~* ^/promises/(.+)$ {
        if ($is_bot) {
            proxy_pass http://backend:8000/api/og/promises/$1;
        }
        proxy_pass http://frontend:5173;
    }

    location / {
        proxy_pass http://frontend:5173;
    }
}
```

**Note:** The `if` inside `location` in Nginx has known quirks ("if is evil" in nginx lore). The safer pattern uses two separate `location` blocks with `map` variable to avoid nested `if` — but for this specific case (single header check, simple proxy_pass) the `if ($is_bot)` pattern is standard practice. [ASSUMED]

### Pattern 5: TanStack Query hook with multi-param filter

Following existing `usePoliticians` pattern exactly:

```typescript
// Source: frontend/src/hooks/usePoliticians.ts — adapted pattern
export function usePromises(params: UsePromisesParams) {
  return useQuery<PaginatedResponse<PromiseListOut>>({
    queryKey: ["promises", params],
    queryFn: () => {
      const p = new URLSearchParams()
      p.set("page", String(params.page))
      if (params.status) p.set("status", params.status)
      if (params.politician_id) p.set("politician_id", params.politician_id)
      if (params.election_id) p.set("election_id", params.election_id)
      if (params.made_date_from) p.set("made_date_from", params.made_date_from)
      if (params.made_date_to) p.set("made_date_to", params.made_date_to)
      if (params.expected_date_from) p.set("expected_date_from", params.expected_date_from)
      if (params.expected_date_to) p.set("expected_date_to", params.expected_date_to)
      return apiClient.get<PaginatedResponse<PromiseListOut>>(`/api/promises?${p}`)
    },
    placeholderData: keepPreviousData,
  })
}
```

### Anti-Patterns to Avoid

- **Merging moderation_status + resolved_status**: The two status fields MUST remain separate. `moderation_status=approved` is always the public visibility filter. `resolved_status` is the filterable content field. Never check one instead of the other.
- **GROUP BY on every request for stats**: The stats endpoint for homepage (D-02) does a live GROUP BY — this is acceptable for Phase 3 (seed data, low traffic). The `stats_cache` table exists for Phase 8 per-politician stats. Global stats aggregation with `COUNT(*) GROUP BY resolved_status` on a few thousand rows is fast enough in Phase 3.
- **Computing OG tags in React**: D-17 is explicit — no OG-related code in the SPA. Bots don't execute JavaScript anyway.
- **Building custom date pickers**: UI-SPEC mandates `<Input type="date">` from shadcn. The native date input is sufficient for Phase 3.
- **Filtering out null-date promises**: D-07b — promises with `expected_date=null` are valid. When a date filter param is not provided, do NOT add any WHERE clause for that date field. Null dates are not excluded.
- **Using `from_attributes=True` on PromiseListOut**: Because the router JOINs Promise + Politician and returns Row tuples, `PromiseListOut` must be a plain `BaseModel` constructed explicitly (same pattern as `ElectionWithCountOut` in the 02-04 codebase note).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Paginated response envelope | Custom per-entity pagination schema | `PaginatedResponse[T]` from `app/schemas/common.py` | Already established in Phase 1; all list endpoints must use it |
| Filter state persistence in URL | React `useState` for filter values | `useSearchParams` + `setSearchParams` | Established pattern in `PersonsPage.tsx`; makes filters shareable by URL |
| Status badge rendering | Inline conditional CSS in each page | `ResolvedStatusBadge` component (already built) | Already handles all 5 statuses with correct Armenian labels and colors |
| Pagination UI | Custom pagination component | `PaginationControls` component (already built) | Already handles page URL param, ellipsis, disabled states |
| Promise truncation for list | Manual JS slice in each component | `PromiseCard` component (new in Phase 3) OR the existing `PromiseStub` for homepage | Centralizes the 120-char truncation logic |
| HTML escaping in OG endpoint | Manual string sanitization | Python `html.escape()` from stdlib | Prevents XSS via politician names or promise titles containing `"` or `<` |

**Key insight:** The Phase 2 component library (`ResolvedStatusBadge`, `PaginationControls`, `PromiseStub`) was built precisely to avoid per-page re-implementation in Phase 3.

---

## Common Pitfalls

### Pitfall 1: Row Tuple vs ORM Object from JOIN Queries

**What goes wrong:** The `list_promises` endpoint JOINs `Promise` and `Politician`. SQLAlchemy returns `Row` objects (tuples), not plain `Promise` ORM objects. If `PromiseListOut` uses `from_attributes=True` and you pass the row directly, you get a Pydantic validation error because `Row` doesn't have `politician_name` as an attribute on the Promise model.

**Why it happens:** `select(Promise, Politician.name_hy)` returns `Row(Promise, str)`, not `Promise`. The `02-04` codebase note explicitly documents this: "ElectionWithCountOut is plain BaseModel (no from_attributes) — correlated subquery returns Row tuples; must unpack election_obj and count explicitly in router."

**How to avoid:** Make `PromiseListOut` a plain `BaseModel` (no `from_attributes`). Construct it explicitly in the router from the unpacked row. Follow the `ElectionWithCountOut` construction pattern exactly.

**Warning signs:** `pydantic.ValidationError: value is not a valid dict` at runtime when calling the endpoint.

### Pitfall 2: Multi-Value Status Filter for /unfulfilled

**What goes wrong:** `/unfulfilled` needs promises with `resolved_status IN ('broken', 'stalled')`. If the API only accepts a single `?status=` value, `/unfulfilled` cannot be implemented without a separate endpoint.

**Why it happens:** Simple filter endpoints often only accept one value per parameter.

**How to avoid:** Accept comma-separated values in the `?status=` query param. In the router, split on comma: `status_values = [ResolvedStatus(s.strip()) for s in status.split(",")]`. The `FulfilledPage` passes `?status=kept`; `UnfulfilledPage` passes `?status=broken,stalled`.

**Warning signs:** `FulfilledPage` works but `UnfulfilledPage` silently returns empty results or only one status.

### Pitfall 3: Nginx "if is evil" with proxy_pass

**What goes wrong:** Nginx's `if` directive inside `location` blocks can produce unexpected behavior when `proxy_pass` is the action — it may reset upstream variables or fail silently for some requests.

**Why it happens:** Nginx's `if` is not a general-purpose conditional; it has documented edge cases with `proxy_pass`.

**How to avoid:** Use the `map` directive to set a variable based on `$http_user_agent`, then use a single `if ($is_bot)` per location block. Alternatively, split into named locations using `@bot_proxy` and `@spa_proxy` patterns. Test with `curl -A "Facebookbot/2.1"` to verify routing.

**Warning signs:** Bot requests falling through to the SPA (which returns a blank HTML shell with no OG tags).

### Pitfall 4: OG Image XSS / HTML Injection

**What goes wrong:** `og:content` attributes contain politician `name_hy` or `title_hy` which may contain Armenian apostrophes, quotation marks, or other characters that break the HTML attribute string.

**Why it happens:** Template string construction without escaping: `content="{title_hy}"` where `title_hy` contains `"` breaks the attribute.

**How to avoid:** Use Python's `html.escape()` on every string inserted into HTML attributes in the OG endpoint. Always use double-quote delimiters in HTML attributes.

**Warning signs:** OG preview shows garbled title or no preview image.

### Pitfall 5: Nginx Service Not Wired to Frontend/Backend Networks in Docker Compose

**What goes wrong:** The Nginx container cannot reach `frontend:5173` or `backend:8000` because Docker Compose services are on separate networks or the Nginx config references the wrong hostnames.

**Why it happens:** Docker Compose service hostnames are the service names (e.g., `backend`, `frontend`). A new Nginx service added to compose must be on the same default network.

**How to avoid:** In `docker-compose.yml`, the Nginx service must have `depends_on: [frontend, backend]`. The nginx.conf must proxy to `http://backend:8000` and `http://frontend:5173` (service names, not `localhost`).

**Warning signs:** Nginx returns 502 Bad Gateway.

### Pitfall 6: date Filter Excluding null-date Promises

**What goes wrong:** A WHERE clause like `WHERE made_date >= :from OR made_date IS NULL` when no filter is applied accidentally filters out null-date promises if the condition is written incorrectly.

**Why it happens:** D-07b specifies: "Promises without dates are NOT excluded when a date filter is not applied." The correct behavior is: when `made_date_from` is None, add no WHERE clause for `made_date`. Only add the filter when the param is provided.

**How to avoid:** Use conditional filter addition — only `.where(Promise.made_date >= made_date_from)` when `made_date_from is not None`. Never add a default date filter.

**Warning signs:** Open-ended promises disappear from the default promise list.

---

## Code Examples

### Frontend: PromisesListPage filter pattern (adapted from PersonsPage.tsx)

```typescript
// Source: frontend/src/pages/PersonsPage.tsx — established useSearchParams filter pattern
export default function PromisesListPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const page = parseInt(searchParams.get("page") ?? "1", 10) || 1
  const status = searchParams.get("status") || null
  const politician_id = searchParams.get("politician_id") || null
  const election_id = searchParams.get("election_id") || null
  const made_date_from = searchParams.get("made_date_from") || null
  const made_date_to = searchParams.get("made_date_to") || null
  const expected_date_from = searchParams.get("expected_date_from") || null
  const expected_date_to = searchParams.get("expected_date_to") || null

  function handleStatusChange(value: string) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === "__all__") { next.delete("status") }
      else { next.set("status", value) }
      next.set("page", "1")
      return next
    })
  }
  // Same pattern for other filters
}
```

### Backend: Existing pagination count pattern

```python
# Source: backend/app/routers/elections.py — count_stmt pattern
count_stmt = select(func.count()).select_from(stmt.subquery())
total_result = await db.execute(count_stmt)
total: int = total_result.scalar_one()
```

This pattern works for filtered queries too — wrap the filtered base `stmt` in a subquery for the count, so the count reflects the applied filters.

### Backend: PromiseDetailOut join pattern

```python
# Source: [ASSUMED] — adapted from politicians router pattern
@router.get("/{slug}", response_model=PromiseDetailOut)
async def get_promise(slug: str, db: AsyncSession = Depends(get_db)) -> PromiseDetailOut:
    stmt = (
        select(Promise, Politician.name_hy.label("politician_name"),
               Politician.slug.label("politician_slug"))
        .join(Politician, Politician.id == Promise.politician_id)
        .where(
            Promise.slug == slug,
            Promise.moderation_status == ModerationStatus.approved,
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")
    promise, politician_name, politician_slug = row
    return PromiseDetailOut(
        id=promise.id,
        slug=promise.slug,
        title_hy=promise.title_hy,
        quote_hy=promise.quote_hy,
        resolved_status=promise.resolved_status,
        made_date=promise.made_date,
        expected_date=promise.expected_date,
        source_url=promise.source_url,
        archived_url=promise.archived_url,
        politician_name_hy=politician_name,
        politician_slug=politician_slug,
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SSR for OG tags (Next.js) | FastAPI OG endpoint + Nginx UA routing | Project decision Phase 3 | No Next.js; keep FastAPI/SPA architecture; slightly more infra (Nginx sidecar) |
| React `useState` for filter state | `useSearchParams` for filter state | Established Phase 2 | Filters are shareable, bookmarkable, browser-back navigable |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `PromiseListOut` must be a plain `BaseModel` (no `from_attributes`) when JOIN returns Row tuples | Architecture Patterns / Pitfalls | Pydantic validation errors at runtime on the list endpoint |
| A2 | Comma-separated `?status=broken,stalled` is the right multi-value approach | Architecture Patterns | `/unfulfilled` silently broken; alternative is multi-value `?status[]=` FastAPI pattern |
| A3 | Nginx `map + if` pattern for bot UA routing works with `proxy_pass` to both backend and frontend | Architecture Patterns | Bot routing fails silently; OG tags not served |
| A4 | Stats endpoint does a live `GROUP BY` on every request (not reading from `stats_cache`) | Architecture Patterns | Fine for Phase 3 data volume; `stats_cache` is for per-politician stats in Phase 8 |
| A5 | `html.escape()` from Python stdlib is sufficient for OG attribute injection prevention | Don't Hand-Roll | XSS in OG preview if politician names contain `"` or `<` |
| A6 | Docker Compose Nginx sidecar approach — no external Nginx install needed | Environment Availability | Dev environment OG routing requires container Nginx, not a local install |

---

## Open Questions

1. **Multiple status values: comma-separated vs repeated param**
   - What we know: FastAPI supports both `?status=broken,stalled` (string split in router) and `?status=broken&status=stalled` (List[ResolvedStatus] param type)
   - What's unclear: which pattern the future Phase 5 submission form and Phase 8 search will expect
   - Recommendation: Use comma-separated string for Phase 3 (matches the existing `apiClient.get()` URL construction pattern with `URLSearchParams`); document in API comments for future phases

2. **OG default image asset**
   - What we know: D-16 specifies fallback to "site default image" when `photo_url` is null
   - What's unclear: no default image asset currently exists in the project
   - Recommendation: Create a minimal `default-og-image.png` (1200x630px) in `frontend/public/` during Phase 3 Wave 0; the OG endpoint references it via the site's canonical URL

3. **Nginx in dev vs production only**
   - What we know: D-17 says Docker Compose / Nginx handles bot routing; the current compose has no Nginx service
   - What's unclear: whether the Nginx sidecar should be dev-only, prod-only, or both
   - Recommendation: Add Nginx to the main `docker-compose.yml` for full parity; use a simple upstream proxy config that also handles the dev Vite server (Vite's `--host 0.0.0.0` already works behind a proxy). Bot UAs rarely hit dev, but the routing config should work in both environments.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker (Nginx via container) | OG bot routing (DISC-05) | ✓ | docker-compose.yml already in use | — |
| PostgreSQL 17 | All backend endpoints | ✓ | 17 (docker-compose.yml) | — |
| Node.js 24 | Frontend shadcn install | ✓ | 24-slim (frontend/Dockerfile) | — |
| `npx shadcn@latest` | `input`, `separator` install | ✓ | available via existing frontend/.npmrc (legacy-peer-deps=true) | — |

**Missing dependencies with no fallback:** none

**Missing dependencies with fallback:** none

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (established in Phase 1/2) |
| Config file | `backend/pytest.ini` or `pyproject.toml` (check existing) |
| Quick run command | `pytest backend/tests/test_promises.py -x` |
| Full suite command | `pytest backend/tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROM-01 | `GET /api/promises` returns 200 with PaginatedResponse envelope | integration | `pytest backend/tests/test_promises.py::test_list_promises -x` | ❌ Wave 0 |
| PROM-01 | `GET /api/promises?status=kept` returns only kept promises | integration | `pytest backend/tests/test_promises.py::test_list_promises_filter_status -x` | ❌ Wave 0 |
| PROM-01 | `GET /api/promises?status=broken,stalled` returns broken+stalled promises | integration | `pytest backend/tests/test_promises.py::test_list_promises_multi_status -x` | ❌ Wave 0 |
| PROM-01 | `GET /api/promises` never returns non-approved promises | integration | `pytest backend/tests/test_promises.py::test_list_promises_moderation_filter -x` | ❌ Wave 0 |
| PROM-02 | `GET /api/promises/{slug}` returns full detail with politician info | integration | `pytest backend/tests/test_promises.py::test_get_promise -x` | ❌ Wave 0 |
| PROM-02 | `GET /api/promises/nonexistent-slug` returns 404 | integration | `pytest backend/tests/test_promises.py::test_get_promise_not_found -x` | ❌ Wave 0 |
| DISC-01 | `GET /api/stats` returns `{ total, by_status }` with all 5 statuses | integration | `pytest backend/tests/test_stats.py::test_get_stats -x` | ❌ Wave 0 |
| DISC-05 | `GET /api/og/promises/{slug}` returns HTML with og:title, og:description | integration | `pytest backend/tests/test_og.py::test_og_promise -x` | ❌ Wave 0 |
| DISC-05 | `GET /api/og/promises/nonexistent` returns 404 | integration | `pytest backend/tests/test_og.py::test_og_promise_not_found -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/test_promises.py -x`
- **Per wave merge:** `pytest backend/tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `backend/tests/test_promises.py` — covers PROM-01, PROM-02 (list, detail, filter, moderation guard, 404)
- [ ] `backend/tests/test_stats.py` — covers DISC-01 (stats endpoint structure)
- [ ] `backend/tests/test_og.py` — covers DISC-05 (OG endpoint returns HTML with og: tags, 404 for missing slug)

*(Existing `conftest.py` with `client` fixture reused as-is — no new fixtures needed)*

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 3 is read-only public browsing; no auth |
| V3 Session Management | no | No sessions in Phase 3 |
| V4 Access Control | yes | `moderation_status=approved` filter on ALL public promise queries — never expose pending/rejected |
| V5 Input Validation | yes | Query params validated by FastAPI/Pydantic (date types, UUID types, int bounds); status enum validation |
| V6 Cryptography | no | No crypto in Phase 3 |

### Known Threat Patterns for this Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Non-approved promise leakage | Information Disclosure | Always filter `moderation_status == ModerationStatus.approved` — established Phase 2 pattern |
| OG HTML injection | Tampering | `html.escape()` all string values inserted into OG HTML attributes |
| Date filter SQL injection | Tampering | FastAPI declares params as `date | None` — Pydantic validates before ORM; SQLAlchemy ORM uses parameterized queries (never string interpolation) |
| UUID param injection | Tampering | FastAPI declares `politician_id: uuid.UUID | None` — invalid UUIDs rejected with 422 before reaching the router |
| Nginx proxy to wrong upstream | Elevation of Privilege | Nginx `proxy_pass` targets are service names in Docker Compose network — not user-controlled |

---

## Sources

### Primary (HIGH confidence)
- Codebase: `backend/app/routers/elections.py` — exact pattern for list + detail + promises subrouter
- Codebase: `frontend/src/pages/PersonsPage.tsx` — exact pattern for `useSearchParams` filter state
- Codebase: `frontend/src/components/PaginationControls.tsx` — exact pagination component API
- Codebase: `backend/app/models/promises.py` — exact Promise model fields (confirmed all fields exist: title_hy, quote_hy, slug, made_date, expected_date, source_url, archived_url, moderation_status, resolved_status, politician_id, created_at)
- Codebase: `backend/app/schemas/common.py` — `PaginatedResponse[T]` exact definition
- Codebase: `frontend/src/types/index.ts` — existing type definitions to extend
- Context: `03-CONTEXT.md` — all D-XX decisions
- Context: `03-UI-SPEC.md` — all visual/component/copy contracts

### Secondary (MEDIUM confidence)
- `backend/app/models/stats_cache.py` — confirms stats_cache is per-politician (Phase 8 concern); global stats in Phase 3 use live GROUP BY
- Codebase pattern note in STATE.md: "02-04: ElectionWithCountOut is plain BaseModel (no from_attributes)" — confirms Row tuple unpacking is needed for JOIN queries

### Tertiary (LOW confidence / ASSUMED)
- Nginx `map` + `if ($is_bot)` routing pattern — [ASSUMED] from general Nginx knowledge; needs validation during implementation
- `html.escape()` sufficiency for OG attribute injection — [ASSUMED]; Python stdlib, well-established

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries confirmed in existing codebase
- Architecture: HIGH — backend patterns read directly from existing routers; frontend patterns from existing pages
- Pitfalls: HIGH — Row tuple pitfall confirmed from STATE.md codebase note; Nginx pitfall is MEDIUM (based on general knowledge)
- OG/Nginx routing: MEDIUM — no existing Nginx config to reference; pattern is standard but needs implementation validation

**Research date:** 2026-05-23
**Valid until:** 2026-06-23 (stable stack — 30 days)
