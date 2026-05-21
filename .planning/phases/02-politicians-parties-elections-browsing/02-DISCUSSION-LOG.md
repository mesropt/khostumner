# Phase 2: Politicians, Parties & Elections Browsing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-21
**Phase:** 2-Politicians-Parties-Elections-Browsing
**Areas discussed:** Site navigation, Persons list style, Promise preview depth, Pagination approach

---

## Site Navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — build in Phase 2 | Shared `<Layout>` with header wraps all pages. Cleaner UX from day one. | ✓ |
| No — defer to Phase 3 | Pages standalone in Phase 2. Nav added alongside homepage in Phase 3. | |

**User's choice:** Build site header in Phase 2.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Only Phase 2 sections | Nav shows only Persons + Elections links. | |
| All planned nav links as stubs | Full nav rendered from day one; unbuilt pages route to NotFoundPage. | ✓ |

**User's choice:** All planned nav links present as stubs (Կատarவad, Չկatarவad, Persons, Elections).

---

| Option | Description | Selected |
|--------|-------------|----------|
| Logo → / (homepage), no hamburger | Simple header. Mobile nav deferred to Phase 3. | ✓ |
| Logo → / + hamburger for mobile | Responsive from day one. Requires mobile menu component. | |

**User's choice:** Logo → `/`, no mobile hamburger yet.

---

## Persons List Style

| Option | Description | Selected |
|--------|-------------|----------|
| Card grid | Photo/avatar, name, role, party badge via shadcn/ui Card. | |
| List rows | Compact horizontal rows, table-like. | |
| You decide | Leave layout to Claude's discretion. | ✓ |

**User's choice:** Claude's discretion. (Card grid with shadcn Card chosen as logical implementation.)

---

| Option | Description | Selected |
|--------|-------------|----------|
| Server-side query params | ?party=uuid&level=national. URL-shareable, works with TanStack queryKey. | ✓ |
| Client-side filtering | Fetch all, filter in browser. Simpler but loses shareable URLs. | |

**User's choice:** Server-side query params.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Two dropdowns: Party + Level | Select elements mapping to ?party= and ?level= params. | ✓ |
| Filter chips / tag buttons | Clickable chip components. More visual, more components. | |

**User's choice:** Two select dropdowns (Party + Level).

---

## Promise Preview Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal stub: quote + status badge | First ~120 chars of quote_hy + resolved_status badge. | ✓ |
| Richer stub: quote + date + status | Adds promised_date and politician name. | |
| You decide | Leave to Claude's discretion. | |

**User's choice:** Minimal stub — truncated quote + status badge.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Not clickable in Phase 2 | Plain list items, no links. Phase 3 adds href. | |
| Clickable but goes to 404 | Links to /promises/{slug} → hits NotFoundPage. Final URL locked early. | ✓ |

**User's choice:** Clickable from Phase 2, routes to NotFoundPage until Phase 3.

---

| Option | Description | Selected |
|--------|-------------|----------|
| Paginated (same as Persons list) | Consistent pagination. Scales if many promises per entity. | ✓ |
| Show all (no pagination) | Simpler. Fine for seed data (20 promises). | |
| You decide | Leave to Claude's discretion. | |

**User's choice:** Paginated.

---

## Pagination Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Offset+limit | ?page=1&per_page=20. Simple, URL-friendly, TanStack-compatible. | ✓ |
| Cursor-based | ?cursor=token. Better for large sets, adds complexity. | |

**User's choice:** Offset+limit.

---

| Option | Description | Selected |
|--------|-------------|----------|
| 20 per page default, 100 max | Standard for content-heavy pages. | ✓ |
| 10 per page default, 50 max | Smaller pages. Better for mobile. | |
| You decide | Leave to Claude. | |

**User's choice:** 20 default, 100 max.

---

| Option | Description | Selected |
|--------|-------------|----------|
| shadcn/ui Pagination component | Page numbers + prev/next. Consistent with stack. | ✓ |
| Simple prev/next buttons | Minimal. No page numbers. Faster to build. | |
| You decide | Leave to Claude. | |

**User's choice:** shadcn/ui Pagination component.

---

## Claude's Discretion

- **Persons list layout**: Card grid (3-column desktop / 1-column mobile) using shadcn/ui Card
- **Photo fallback**: Initials avatar or silhouette when photo_url is null
- **Status badge colors**: Tailwind/shadcn tokens per resolved_status value (kept=green, broken=red, in_progress=yellow, stalled=gray, not_rated=neutral)
- **API router naming**: One file per domain following health.py pattern

## Deferred Ideas

- Mobile hamburger/responsive nav — deferred to Phase 3
- Promise detail page (/promises/{slug}) — Phase 3
- Fulfillment percentage on politician profiles — Phase 8
- Admin create/edit profiles — Phase 6
