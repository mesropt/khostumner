# Technology Stack

**Project:** Khostumner (Խոստումներ) — Armenian Political Promise Tracker
**Researched:** 2026-05-20
**Overall confidence:** HIGH for core stack, MEDIUM for search layer

---

## Recommended Stack

### Core Framework
Спроси меня насчёт технологий - поговорим
---

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PostgreSQL | 17 (use 17.x, not 18 — 18 released Sep 2025 is very new) | Primary data store | Relational model fits promise→politician→election hierarchy perfectly; full-text search via `tsvector` defers the need for a dedicated search service in early phases; JSONB for flexible evidence metadata |
| Neon (hosted) | current | Managed serverless PostgreSQL | Native Vercel/serverless integration; Copy-on-Write branching for safe migrations; scales to zero on free tier; acquired by Databricks (May 2025) signals long-term investment. Alternative: Railway PostgreSQL if self-hosting is preferred |

**Why PostgreSQL over MySQL:**
JSONB column type for evidence/source metadata, full-text search with `tsvector`/`tsquery`, better support for complex queries (window functions for promise statistics), and superior ORM support in the Node.js ecosystem.

**Why not SQLite:**
Concurrent writes from crowdsourced voting will hit SQLite's write lock immediately. PostgreSQL handles it correctly.

---

### ORM / Database Access

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Drizzle ORM | 0.45.x (stable; v1.0 beta available but not recommended for new projects yet) | Type-safe database queries and migrations | ~7kb bundle with zero native binaries — critical for Vercel serverless functions; SQL-first API means no magic, schema defined in TypeScript; 90% smaller cold start vs Prisma; migrations via `drizzle-kit` are explicit and reviewable |

**Why Drizzle over Prisma:**
Prisma 7 (late 2025) eliminated the Rust binary which was its main disadvantage, but Drizzle's smaller footprint and more explicit SQL-like API remain advantages. For a civic platform with complex voting aggregation queries, Drizzle's raw SQL escape hatch is cleaner. However, if the team finds Drizzle's API unfamiliar, Prisma 7 is an acceptable alternative — the architectural difference is not critical for this project size.

**Why not TypeORM:**
Decorator-based approach, poor Tree-shaking, slower development relative to Drizzle/Prisma.

---

### Authentication

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Better Auth | 1.6.x (latest stable) | User registration, login, session management, RBAC | MIT licensed, self-hosted (no vendor lock-in or per-MAU cost), built-in RBAC for admin/moderator/user roles, plugin architecture, TypeScript-first, actively maintained with v1.4+ stable APIs |

**Why Better Auth over alternatives:**
- Auth.js (NextAuth v5): Still in beta after years; the lead contributor quit in Jan 2025; missing built-in RBAC which this project needs for admin moderation
- Clerk: $0.02/MAU becomes costly as civic platforms grow; vendor lock-in is unacceptable for a public-interest project; the pre-built UI components have limited customization for Armenian language
- Custom auth: Bcrypt, session tokens, CSRF — too much undifferentiated work

**RBAC roles needed:**
- `user`: can submit promises, vote on status
- `moderator`: can approve/reject submitted promises, resolve disputed votes
- `admin`: full access including politician profile management

---

### Search

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PostgreSQL full-text search (Phase 1) | built-in | Politician and promise search | `tsvector` with Armenian language configuration handles the initial use case with zero additional infrastructure; Armenian uses Unicode so standard unaccented text search works |
| Meilisearch (Phase 2, when needed) | 1.x engine (v1.38 latest), SDK 0.58.x | Advanced typo-tolerant search | When Postgres FTS becomes limiting; sub-50ms search, easy Docker deployment, built-in admin UI for tuning; simpler operational model than Elasticsearch |

**Phase 1 strategy:** Build with `tsvector` columns on `promises.text`, `politicians.name`, and `politicians.party`. Add GIN index. This handles the dataset size (hundreds to low thousands of records) without operational overhead.

**Phase 2 trigger:** Migrate to Meilisearch when: search quality complaints increase, OR dataset exceeds ~10k records, OR faceted filtering by election/party/status becomes complex.

**Why not Elasticsearch:** Operational overhead unjustifiable for a civic site at this scale; JVM memory requirements; complex tuning.
**Why not Algolia:** Pricing per-search becomes unpredictable for a public site; no self-hosting.

---

### UI Components and Styling

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Tailwind CSS | 4.x (released Jan 22, 2025) | Utility-first styling | CSS-first config (no tailwind.config.js), 5x faster builds via Lightning CSS, works seamlessly with shadcn/ui |
| shadcn/ui | latest CLI (copy-paste model, no version lock) | Accessible component primitives | Components are copied into the codebase (owned, not a dependency); built on Radix UI for accessibility; works natively with Next.js App Router and Tailwind v4; Armenian text renders without modification since it's Unicode |

**Why shadcn/ui over MUI or Chakra:**
shadcn/ui components live in your codebase — you can freely modify them for Armenian UI conventions (RTL is not needed; Armenian is LTR). MUI and Chakra carry heavy bundle weight and override friction. shadcn/ui is currently the dominant pattern in the Next.js 15 ecosystem.

---

### Form Handling and Validation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| React Hook Form | 7.76.x (latest stable) | Form state management | Uncontrolled components; minimal re-renders; works with Server Actions in Next.js App Router |
| Zod | 4.4.x (latest stable, v4 released 2025) | Schema validation | TypeScript-first; schemas are reusable between server (API validation) and client (form validation); integrates directly with React Hook Form via `@hookform/resolvers/zod` |

---

### State Management

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| TanStack Query (React Query) | 5.100.x (latest stable) | Client-side server-state caching | Handles vote count updates, politician profile data, and pagination without manual cache management; ~20% smaller than v4; Suspense-first in v5 aligns with Next.js App Router patterns |
| React Context (built-in) | — | Auth state, UI state (modals, toasts) | Sufficient for non-server state; no need for Zustand/Redux at this application scale |

---

### Deployment

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Vercel | current | Next.js hosting | Zero-config Next.js deployment, native Neon integration, preview deployments per PR (critical for reviewing promise submissions), free tier covers early traffic |
| Neon | current | PostgreSQL hosting | See Database section above |
| Cloudflare (optional) | — | CDN, DDoS protection | Armenian politics sites may face politically motivated attacks; Cloudflare free tier provides baseline protection |

**Why Vercel over Railway/Render for the frontend:**
Next.js was created by Vercel; ISR (Incremental Static Regeneration) and Edge middleware work best on Vercel's infrastructure. For a read-heavy public site (promise pages viewed by journalists and citizens), Vercel's CDN edge caching provides meaningful performance without configuration.

**When to reconsider Vercel:**
If costs grow significantly (Vercel's function invocation pricing), migrate to a self-hosted solution on Railway or a VPS. The Next.js codebase is portable.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Framework | Next.js 15 | Nuxt 3 (Vue) | Smaller JS ecosystem; fewer Armenian-speaking developers; less mature App Router equivalent |
| Framework | Next.js 15 | Django + React SPA | Two runtimes, two deployments, split languages for one team; Django admin attractive but not worth the split |
| ORM | Drizzle | Prisma 7 | Both viable; Drizzle wins on bundle size and explicit SQL; Prisma 7 acceptable if team prefers it |
| Auth | Better Auth | Auth.js v5 | Auth.js still beta, no built-in RBAC |
| Auth | Better Auth | Clerk | Per-MAU pricing bad for public-interest civic app |
| Database | PostgreSQL | MySQL | Weaker JSONB, weaker FTS, weaker ecosystem in Node.js tooling |
| Search (Phase 1) | Postgres FTS | Meilisearch | Operational overhead unjustified until dataset grows |
| Search (Phase 2) | Meilisearch | Elasticsearch | JVM overhead, complex operations, overkill |
| Styling | Tailwind v4 + shadcn/ui | MUI | Heavy bundle, Armenian customization friction |
| Hosting | Vercel + Neon | Railway (all-in-one) | Railway is good alternative; Vercel-Neon integration is tighter for Next.js |

---

## Installation

```bash
# Create Next.js project
npx create-next-app@latest khostumner --typescript --tailwind --app --src-dir

# Database ORM
npm install drizzle-orm @neondatabase/serverless
npm install -D drizzle-kit

# Authentication
npm install better-auth

# Forms and Validation
npm install react-hook-form @hookform/resolvers zod

# Server state
npm install @tanstack/react-query @tanstack/react-query-devtools

# UI components (shadcn/ui is added via CLI, not npm)
npx shadcn@latest init

# Common shadcn components for this project
npx shadcn@latest add button card badge avatar input textarea
npx shadcn@latest add table dialog dropdown-menu
npx shadcn@latest add form label select
npx shadcn@latest add toast sonner
```

---

## Key Architectural Decisions This Stack Enables

1. **Server Components for public pages** — Promise detail pages, politician profiles, and election archives are rendered server-side by default. No client JS is shipped unless interaction is needed. This is critical for SEO (Armenian-language pages indexing in Google) and performance on lower-end devices.

2. **Server Actions for mutations** — Promise submissions, vote casting, and admin approvals go through Next.js Server Actions (not separate API routes). This keeps mutation logic colocated with the UI that triggers it, reducing boilerplate.

3. **Single deployment unit** — The entire application (UI + API + background jobs) deploys as one Next.js project. For a civic volunteer project, this dramatically reduces operational complexity.

4. **Postgres FTS as search v1** — Avoids running a separate search service until genuinely needed. The promise text and politician names are stored with `tsvector` columns from day one, making the Meilisearch migration mechanical rather than a data redesign.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Next.js 15 as framework | HIGH | Verified current stable version 15.5; official docs confirm App Router stability |
| PostgreSQL 17 | HIGH | Verified via endoflife.date; 17.x is current maintained release |
| Drizzle ORM 0.45.x | HIGH | Confirmed on npm; v1 beta exists but 0.45.x is production stable |
| Better Auth 1.6.x | HIGH | Confirmed on npm (1.6.11 published 7 days ago); stable v1 API |
| Tailwind CSS v4 | HIGH | Released Jan 22, 2025; widely adopted in Next.js ecosystem |
| Meilisearch as Phase 2 search | MEDIUM | v1.38 confirmed as current; Armenian language handling is Unicode-based and should work, but not specifically tested with Armenian — flag for phase-specific research |
| Neon for PostgreSQL hosting | HIGH | Databricks acquisition confirmed; Vercel-native integration well-documented |
| Vercel deployment | HIGH | Native Next.js platform; free tier confirmed available |
| shadcn/ui | HIGH | Copy-paste model means no version dependency; official Next.js docs reference it |

---

## Gaps Requiring Phase-Specific Research

- **Armenian full-text search configuration:** PostgreSQL's `unaccent` extension and Armenian stemming — the `hy` locale support in PostgreSQL needs verification before Phase 1 search implementation.
- **Meilisearch + Armenian Unicode:** Meilisearch's typo tolerance relies on language detection; Armenian script (Հ, ա, յ...) needs a proof-of-concept test before committing to it in Phase 2.
- **Image storage for politician photos:** Not decided. Options are Vercel Blob, Cloudflare R2, or a simple `public/` directory for v1. Decide at the politician profile phase.
- **Rate limiting for votes:** Next.js middleware + Upstash Redis is the standard pattern but adds a dependency. Needs evaluation before implementing the voting system.

---

## Sources

- [Next.js 15.5 Release Notes](https://nextjs.org/blog/next-15-5) — confirmed current stable version
- [Django 5.2 Released (LTS)](https://www.djangoproject.com/weblog/2025/apr/02/django-52-released/) — considered and rejected for v1
- [Drizzle ORM npm](https://www.npmjs.com/drizzle-orm) — version 0.45.x confirmed stable
- [Better Auth npm](https://www.npmjs.com/package/better-auth) — version 1.6.11 confirmed
- [Tailwind CSS v4.0](https://tailwindcss.com/blog/tailwindcss-v4) — stable January 22, 2025
- [Zod v4 npm](https://www.npmjs.com/package/zod) — version 4.4.3 confirmed
- [React Hook Form npm](https://www.npmjs.com/package/react-hook-form) — version 7.76.x confirmed
- [PostgreSQL endoflife.date](https://endoflife.date/postgresql) — v17 confirmed as maintained; v18 released Sep 2025
- [Neon vs Supabase for Next.js](https://infontic.com/supabase-vs-neon-best-serverless-postgres-for-nextjs/) — Neon as recommended for Vercel-based projects
- [Better Auth vs Clerk vs NextAuth comparison](https://supastarter.dev/blog/better-auth-vs-nextauth-vs-clerk) — Better Auth recommended for self-hosted RBAC
- [Meilisearch vs Typesense for community sites](https://blog.elest.io/meilisearch-vs-typesense-which-search-engine-for-your-app/) — Meilisearch for simpler ops
- [TanStack Query v5](https://tanstack.com/query/v5) — version 5.100.x confirmed stable
- [Vercel vs Railway vs Render](https://www.superfa.st/blog/vercel-vs-railway-vs-render) — Vercel for Next.js-first deployment