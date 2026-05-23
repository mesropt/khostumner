# Phase 4: Authentication - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-23
**Phase:** 4-Authentication
**Areas discussed:** Auth library, JWT storage, OAuth providers, Dev email setup

---

## Auth Library

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI-Users (fastapi-users[sqlalchemy]) | Ready-made library: registration, verification, reset, OAuth out of the box. Less code, faster phase. | ✓ |
| Custom JWT | python-jose/PyJWT by hand. Full control, good for learning FastAPI internals. More code. | |

**User's choice:** FastAPI-Users with SQLAlchemy integration
**Notes:** User confirmed `fastapi-users[sqlalchemy]` specifically (not Beanie/MongoDB variant).

---

## JWT Storage

| Option | Description | Selected |
|--------|-------------|----------|
| httpOnly cookie | JS cannot read — protects against XSS. Needs CSRF handling. FastAPI-Users CookieTransport. | ✓ |
| localStorage / Bearer header | Simpler implementation, but XSS-vulnerable. Standard SPA+API pattern. | |

**Token lifetime:** Access + refresh pair (1h access, 30d sliding refresh)

**User's choice:** httpOnly cookie with access + refresh tokens
**Notes:** Political site — explicit security priority over implementation simplicity.

---

## OAuth Providers

| Option | Description | Selected |
|--------|-------------|----------|
| Google only | Large Armenian audience. Add Facebook/GitHub later. | |
| GitHub only | Developer audience — wrong fit for political site. | |
| Both Google + GitHub | Per AUTH-04 wording. | |
| Google + Facebook | Armenian general public skews Google + Facebook, not GitHub. | ✓ |

**User's choice:** Google + Facebook (free-text override — not in pre-defined options)
**Notes:** User proactively corrected the requirement to Facebook instead of GitHub. AUTH-04 says "Google or GitHub" but Facebook is more appropriate for the Armenian audience.

---

## Dev Email Setup

| Option | Description | Selected |
|--------|-------------|----------|
| Mailhog | Docker SMTP catcher, visual web UI at localhost:8025. | ✓ |
| Console logging | Print emails to stdout. Zero dependencies. | |
| Mailtrap / Resend | Real SMTP service with free tier. Needs registration + API key. | |

**SMTP client:** fastapi-mail (async, integrates with Jinja2 templates)
**Docker Compose:** Add mailhog service (ports 1025 SMTP + 8025 UI)

**User's choice:** Mailhog + fastapi-mail

---

## Claude's Discretion

- Router registration order in main.py (alphabetical — `auth` goes first)
- Frontend auth state: React Context + useReducer
- Protected routes: `<RequireAuth>` wrapper component
- Email template format: plain HTML strings (no Jinja2 needed for v1)

## Deferred Ideas

None mentioned during discussion.
