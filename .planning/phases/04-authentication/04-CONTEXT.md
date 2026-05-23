# Phase 4: Authentication - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 delivers a complete user account system:
- Email + password registration with email verification
- Password reset via email link
- OAuth login via Google and Facebook
- Persistent JWT sessions via httpOnly cookies (access + refresh token pair)
- User model integration with FastAPI-Users[sqlalchemy]

No promise submission, no moderation, no voting — those are Phases 5-7.
</domain>

<decisions>
## Implementation Decisions

### Auth Library
- **D-01:** Use **fastapi-users[sqlalchemy]** — the opinionated library with built-in registration, verification, password reset, and OAuth. It connects to the existing SQLAlchemy 2.x async setup.
- **D-02:** The existing `User` model in `backend/app/models/users.py` must be adapted to inherit from FastAPI-Users' `SQLAlchemyBaseUserTableUUID` mixin. `UserRole` enum stays intact; existing columns (display_name, role, is_active, account_age_days) are preserved as extensions.

### JWT Storage
- **D-03:** Store JWT in **httpOnly cookies** — protects against XSS. FastAPI-Users `CookieTransport` is the transport layer.
- **D-04:** Use **access + refresh token pair**: access token expires in 1 hour, refresh token is sliding with 30-day expiry. FastAPI-Users `JWTStrategy` + `BearerTransport`/`CookieTransport` supports this pattern.
- **D-05:** CSRF double-submit cookie pattern is required because we use httpOnly cookies with a browser SPA. FastAPI-Users does NOT auto-handle CSRF — must implement manually or use a middleware (e.g., `starlette-csrf`).

### OAuth Providers
- **D-06:** Support **Google + Facebook** OAuth in v1 (not GitHub). `httpx-oauth` (FastAPI-Users dependency) has `GoogleOAuth2` and `FacebookOAuth2` clients out of the box.
- **D-07:** OAuth users who don't have an existing email/password account get a new account created automatically. If the OAuth email matches an existing email/password account, link the OAuth identity to it.

### Email Delivery
- **D-08:** Dev/test email delivery via **Mailhog** — add `mailhog` service to `docker-compose.yml` (image: `mailhog/mailhog`, ports: 1025 SMTP + 8025 web UI).
- **D-09:** Use **fastapi-mail** as the SMTP client for async email sending. FastAPI-Users exposes hooks: `on_after_register`, `on_after_forgot_password`, `on_after_request_verify` — send emails from these hooks.
- **D-10:** Email templates are plain HTML (Armenian text). No Jinja2 templating engine required for v1 — inline HTML strings are acceptable.

### Claude's Discretion
- Router structure: add `auth` router to `main.py` following the existing alphabetical order (after `elections`, before `health` — i.e., at index 0). Actually alphabetical: `auth` comes first.
- CORS update for credentials: `allow_credentials=True` already set in `main.py` — but `allow_origins` must be an explicit list (not `*`) when using credentials cookies. Already `["http://localhost:5173"]` — no change needed.
- Frontend auth state management: use React Context + `useReducer` (no external state library needed for v1).
- Protected routes: use a `<RequireAuth>` wrapper component that redirects to `/login` if no session.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Authentication — AUTH-01 through AUTH-05 (5 requirements)
- `.planning/ROADMAP.md` §Phase 4 — success criteria and phase goal

### Existing Code
- `backend/app/models/users.py` — existing User model; must be extended, not replaced
- `backend/app/main.py` — router registration pattern (alphabetical order)
- `backend/app/config.py` — settings pattern for adding JWT_SECRET, SMTP config, OAuth client IDs/secrets
- `docker-compose.yml` — add mailhog service here
- `frontend/src/App.tsx` — add /login, /register, /verify-email, /reset-password routes
- `frontend/src/components/Layout.tsx` — add Login/Logout nav link (right-aligned)

### Phase context
- `.planning/STATE.md` — current project state

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/ui/button.tsx` — use for form submit buttons (Login, Register)
- `frontend/src/components/ui/input.tsx` — use for email/password form fields
- `frontend/src/components/ui/card.tsx` — wrap login/register forms in Card

### Established Patterns
- All routers registered in `main.py` with `app.include_router(X.router, prefix="/api")` — auth router follows same pattern
- Plain `BaseModel` schemas (no `from_attributes`) for request/response where no ORM row mapping needed
- `app/config.py` holds all env-driven settings — add `JWT_SECRET`, `SMTP_HOST`, `SMTP_PORT`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET` there
- Frontend pages live in `frontend/src/pages/` — add `LoginPage.tsx`, `RegisterPage.tsx`, `VerifyEmailPage.tsx`, `ResetPasswordPage.tsx`

### Integration Points
- `backend/app/models/users.py` — existing User model must become FastAPI-Users compatible (UUID mixin)
- `frontend/src/App.tsx` — add new routes inside existing `<Route element={<Layout />}>` block
- `frontend/src/components/Layout.tsx` — add auth nav items (Login / user display name + Logout)
- `docker-compose.yml` — add mailhog service

</code_context>

<specifics>
## Specific Ideas

- The Armenian political nature of the site means user privacy matters — httpOnly cookies over localStorage was an explicit security choice.
- Google + Facebook chosen over GitHub because the target audience is Armenian general public, not developers.
- Mailhog in Docker gives a visual UI at localhost:8025 to inspect verification/reset emails during development.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 4-Authentication*
*Context gathered: 2026-05-23*
