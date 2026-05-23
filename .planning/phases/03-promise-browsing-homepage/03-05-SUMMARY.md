---
phase: 03-promise-browsing-homepage
plan: 05
subsystem: api, infra
tags: [fastapi, nginx, docker-compose, og-tags, social-sharing]

requires:
  - phase: 03-04
    provides: og.py stub (replaced with full endpoint in this plan)

provides:
  - GET /api/og/promises/{slug} — OG tag HTML endpoint (fully implemented)
  - nginx/nginx.conf — bot user-agent routing (Facebookbot, Twitterbot, TelegramBot, LinkedInBot, Googlebot)
  - docker-compose.yml nginx service on port 80:80
  - frontend/public/default-og-image.png — fallback OG image placeholder

affects: [phase-04-auth, phase-05-submit]

tech-stack:
  added:
    - "nginx:1.25-alpine Docker service (bot UA routing sidecar)"
  patterns:
    - "OG endpoint: html.escape() on all string values inserted into HTML attributes (T-03-12)"
    - "Nginx: set + double-if pattern (safe for conf.d/ include context — avoids map-outside-http issue)"
    - "Nginx: proxy_set_header Upgrade + Connection for Vite HMR WebSocket pass-through"
    - "docker-compose: nginx service depends_on frontend + backend, restart unless-stopped"

key-files:
  created:
    - nginx/nginx.conf
    - frontend/public/default-og-image.png
  modified:
    - docker-compose.yml
    - frontend/src/App.tsx
    - frontend/src/components/Layout.tsx
    - frontend/src/pages/HomePage.tsx

key-decisions:
  - "og.py was already fully implemented in 03-04 (despite SUMMARY saying 'stub') — no re-implementation needed"
  - "Used set + double-if nginx pattern instead of top-level map directive (mount to conf.d/default.conf is inside http{} already)"
  - "WebSocket upgrade headers added to nginx proxy for Vite HMR compatibility in dev"
  - "Pending 03-04 Task 3 changes (App.tsx routes, Layout.tsx nav, HomePage wiring) committed here"

requirements-completed: [DISC-05]

duration: ~15min
completed: 2026-05-23
---

# Phase 03-05: OG Tags + Nginx Infrastructure Summary

**OG tag HTML endpoint complete; Nginx bot-routing config and docker-compose nginx service added; all Phase 3 backend + infra work delivered**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-05-23
- **Tasks:** 2/3 completed (Task 3 is a checkpoint:human-verify)
- **Files modified/created:** 6

## Accomplishments

- `GET /api/og/promises/{slug}` returns 200 HTML with og:title, og:description, og:image, og:url — tests GREEN
- `GET /api/og/promises/nonexistent-slug` returns 404 — test GREEN
- `html.escape()` applied to all string values (title_hy, quote_hy[:150]+name_hy, slug) — XSS prevention (T-03-12, T-03-13)
- `nginx/nginx.conf` routes Facebookbot, Twitterbot, TelegramBot, LinkedInBot, Googlebot to OG endpoint; all other UAs go to SPA
- `docker-compose.yml` nginx service: port 80:80, volume mount read-only, depends_on frontend+backend
- `frontend/public/default-og-image.png` 1x1 PNG placeholder created for og:image fallback (D-16)
- All 24 backend tests GREEN (excluding test_seed.py which requires ENVIRONMENT guard not set in local dev)

## Task Commits

1. **Task 1: OG endpoint + frontend wiring** - `5c0357c` (feat)
   - frontend/public/default-og-image.png (new)
   - frontend/src/App.tsx (routes: /promises, /fulfilled, /unfulfilled, /promises/:slug, /about)
   - frontend/src/components/Layout.tsx (Մeр масин nav link)
   - frontend/src/pages/HomePage.tsx (usePromises wired for recent section)
2. **Task 2: Nginx config + docker-compose** - `127cfb5` (feat)
   - nginx/nginx.conf (new)
   - docker-compose.yml (nginx service added)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 03-04 Task 3 changes were uncommitted**
- **Found during:** Task 1 pre-commit check
- **Issue:** App.tsx routes, Layout.tsx Մeр масин nav, and HomePage recent promises wiring were present as uncommitted changes (modified in working tree but not in any commit). The 03-04 SUMMARY incorrectly stated they were "included in ff4e8b5" — that commit only had usePromise.ts, PromiseDetailPage.tsx, AboutPage.tsx.
- **Fix:** Committed these 3 files as part of Task 1 (they are prerequisite to a working Phase 3 frontend).
- **Files modified:** frontend/src/App.tsx, frontend/src/components/Layout.tsx, frontend/src/pages/HomePage.tsx
- **Commit:** 5c0357c

**2. [Rule 3 - Blocking] og.py was already fully implemented**
- **Found during:** Task 1 read phase
- **Situation:** The plan says "Create (or replace stub) backend/app/routers/og.py" but git show abc86e3 confirms the full implementation was committed in 03-04 (not just a stub). No action needed — endpoint already satisfies all must_haves.
- **Files modified:** none (implementation already correct)

**3. [Rule 2 - Security] Added WebSocket upgrade headers to nginx proxy**
- **Found during:** Task 2 implementation
- **Issue:** Nginx proxy to Vite dev server needs WebSocket upgrade headers for HMR (Hot Module Replacement) to work. Without these, the browser would see failed WebSocket connections on port 80.
- **Fix:** Added `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";` to both location blocks.
- **Files modified:** nginx/nginx.conf
- **Commit:** 127cfb5

## Known Stubs

- `frontend/public/default-og-image.png` — 1x1 pixel PNG placeholder. The actual 1200x630px social-preview image must be created and replaced before public launch. The og:image fallback URL `https://khostumner.am/default-og-image.png` is correct but the image content is a placeholder.
- `frontend/src/pages/AboutPage.tsx` — static page renders TODO placeholder text pending content from "Our Principles" file in project root.

## Threat Flags

None — all security surfaces covered:
- T-03-12: html.escape() on all OG content strings (implemented in og.py)
- T-03-13: moderation_status == ModerationStatus.approved filter (implemented)
- T-03-14: nginx proxy targets are hardcoded Docker service names (implemented)
- T-03-15: bot UA spoofing returns OG HTML (benign, by design)
- T-03-SC: nginx:1.25-alpine from official Docker Hub (RESEARCH.md audit passed)

## Self-Check

### Files exist:
- [x] nginx/nginx.conf — FOUND
- [x] frontend/public/default-og-image.png — FOUND
- [x] docker-compose.yml (nginx service) — FOUND

### Commits exist:
- [x] 5c0357c — FOUND (feat(03-05): OG endpoint wiring + default-og-image.png placeholder)
- [x] 127cfb5 — FOUND (feat(03-05): Nginx bot-routing config + docker-compose nginx service)

## Self-Check: PASSED

---

## Checkpoint: Task 3 — Human Verification APPROVED

`checkpoint:human-verify` gate passed. Human verified the running stack and approved.
All Phase 3 plans (03-01 through 03-05) are complete.

## Next Phase Readiness
- Phase 3 fully complete: all 5 plans executed and human-approved
- All Phase 3 backend routes live: /api/stats, /api/promises, /api/promises/{slug}, /api/og/promises/{slug}
- All Phase 3 frontend routes accessible via Nginx on port 80
- Phase 4 (Authentication) can begin

*Phase: 03-promise-browsing-homepage*
*Completed: 2026-05-23*
