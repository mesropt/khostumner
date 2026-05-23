# Phase 4: Authentication - Research

**Researched:** 2026-05-23
**Domain:** FastAPI-Users + SQLAlchemy async + httpOnly JWT cookies + OAuth2 + React Context auth state
**Confidence:** HIGH (core stack verified via PyPI + official docs + source code inspection)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Use `fastapi-users[sqlalchemy]` — the opinionated library with built-in registration, verification, password reset, and OAuth. Connects to the existing SQLAlchemy 2.x async setup.
- **D-02:** The existing `User` model in `backend/app/models/users.py` must be adapted to inherit from FastAPI-Users' `SQLAlchemyBaseUserTableUUID` mixin. `UserRole` enum stays intact; existing columns (display_name, role, is_active, account_age_days) are preserved as extensions.
- **D-03:** Store JWT in **httpOnly cookies** — protects against XSS. FastAPI-Users `CookieTransport` is the transport layer.
- **D-04:** Use **access + refresh token pair**: access token expires in 1 hour, refresh token is sliding with 30-day expiry. FastAPI-Users `JWTStrategy` + `CookieTransport` supports this pattern.
- **D-05:** CSRF double-submit cookie pattern is required because we use httpOnly cookies with a browser SPA. FastAPI-Users does NOT auto-handle CSRF — must implement manually using `starlette-csrf` middleware.
- **D-06:** Support **Google + Facebook** OAuth in v1 (not GitHub). `httpx-oauth` (FastAPI-Users dependency) has `GoogleOAuth2` and `FacebookOAuth2` clients out of the box.
- **D-07:** OAuth users without an existing account get a new account created automatically. If the OAuth email matches an existing email/password account, link the OAuth identity to it (`associate_by_email=True`).
- **D-08:** Dev/test email delivery via **Mailhog** — add `mailhog` service to `docker-compose.yml` (image: `mailhog/mailhog`, ports: 1025 SMTP + 8025 web UI).
- **D-09:** Use **fastapi-mail** as the SMTP client for async email sending. FastAPI-Users exposes hooks: `on_after_register`, `on_after_forgot_password`, `on_after_request_verify` — send emails from these hooks.
- **D-10:** Email templates are plain HTML (Armenian text). No Jinja2 templating engine required for v1 — inline HTML strings are acceptable.

### Claude's Discretion

- Router structure: add `auth` router to `main.py` alphabetically first (before `elections`).
- CORS update for credentials: `allow_credentials=True` already set; `allow_origins=["http://localhost:5173"]` is explicit — no change needed.
- Frontend auth state management: use React Context + `useReducer` (no external state library needed for v1).
- Protected routes: use a `<RequireAuth>` wrapper component that redirects to `/login` if no session.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTH-01 | User can register an account with email and password | FastAPI-Users `get_register_router` + `UserCreate` schema + `on_after_register` hook |
| AUTH-02 | User receives email verification link after registration | FastAPI-Users `get_verify_router` + `on_after_request_verify` hook + fastapi-mail SMTP |
| AUTH-03 | User can reset password via email link | FastAPI-Users `get_reset_password_router` + `on_after_forgot_password` hook + fastapi-mail |
| AUTH-04 | User can log in via Google or Facebook OAuth | FastAPI-Users `get_oauth_router` + `httpx-oauth` GoogleOAuth2/FacebookOAuth2 clients |
| AUTH-05 | Authenticated user session persists across browser refresh (JWT) | CookieTransport with `cookie_max_age` + `/auth/me` endpoint called on mount |
</phase_requirements>

---

## Summary

Phase 4 integrates `fastapi-users[sqlalchemy]` 15.0.5 (current stable, maintenance mode) with the existing SQLAlchemy 2.x async setup. The library provides complete endpoints for registration, email verification, password reset, OAuth login, and user management — no hand-rolling.

The single most important discovery is a **schema conflict between the existing User model and FastAPI-Users' expected field names**. The existing `users` table has columns named `password_hash` and `email_verified`, while FastAPI-Users requires `hashed_password` and `is_verified`. An Alembic migration must rename both columns and add the missing `is_superuser` column. The existing `is_active` column name is already correct.

FastAPI-Users has no built-in refresh token rotation — the recommended pattern for this project is to use two `AuthenticationBackend` instances (one for access token cookie, one for refresh token cookie) with different `JWTStrategy` lifetimes. The refresh endpoint simply validates the refresh cookie and issues a new access token cookie. This is a deliberate limitation by design: the library leaves rotation strategy to the developer.

**Primary recommendation:** Follow the official SQLAlchemy async setup exactly; the column rename migration is the highest-risk task and should be Wave 0. Frontend auth state uses React Context + `useReducer` with a `/auth/me` call on app mount to rehydrate from httpOnly cookie.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Registration / verification / password reset | API / Backend | — | FastAPI-Users routers own all auth logic server-side |
| JWT token issuance and storage | API / Backend | Browser (cookie) | Server sets httpOnly cookie; browser stores passively |
| CSRF protection | API / Backend (middleware) | Browser (reads CSRF cookie) | starlette-csrf sets readable CSRF cookie; JS reads and sends as header |
| OAuth2 authorize + callback | API / Backend | — | httpx-oauth handles provider exchange; callback on backend |
| Auth state (logged in / out) | Frontend (React Context) | — | Frontend tracks login state in memory; rehydrates from /auth/me on mount |
| Protected route enforcement | Frontend (React Router) | — | RequireAuth component redirects before page renders |
| Email delivery (dev) | Docker (Mailhog) | — | SMTP relay; Mailhog catches and displays in web UI |

---

## Standard Stack

### Core (Backend)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastapi-users[sqlalchemy]` | 15.0.5 | Registration, verification, password reset, OAuth, user CRUD | Opinionated library; reduces auth surface area from weeks to days; ASVS-aligned |
| `httpx-oauth` | 0.17.0 | Google + Facebook OAuth2 client | Bundled dependency of fastapi-users; pure-async; official client classes for major providers |
| `python-multipart` | 0.0.29 | Form parsing required by FastAPI for login endpoint | Required by FastAPI when using OAuth2 form-based login |
| `bcrypt` | 5.0.0 | Password hashing (used by fastapi-users internally) | Industry-standard adaptive hashing; fastapi-users uses it by default |
| `fastapi-mail` | 1.6.4 | Async SMTP email sending | async-native; works with Mailhog/SMTP; simple ConnectionConfig API |
| `starlette-csrf` | 3.0.0 | Double-submit cookie CSRF protection for SPA + httpOnly cookies | Authored by same developer as fastapi-users; integrates cleanly |

All 6 packages verified on PyPI and cleared by slopcheck [OK]. [VERIFIED: npm registry equivalent — PyPI]

### Supporting (Frontend — no new packages required)

The existing frontend dependencies already cover auth UI needs:

| Existing Package | Auth Use |
|-----------------|---------|
| `react-router-dom` ^7.0.0 (resolved 7.15.1) | Protected routes via `<RequireAuth>` wrapper, navigate to /login |
| `@tanstack/react-query` ^5.0.0 (resolved 5.100.14) | `useQuery` for /auth/me session check; mutation for login/register |
| shadcn `Button`, `Input`, `Card` | Auth form UI components (already installed) |

No new npm packages are required for Phase 4 frontend work.

**Installation (backend additions):**
```bash
pip install "fastapi-users[sqlalchemy]==15.0.5" "fastapi-mail==1.6.4" "starlette-csrf==3.0.0" "python-multipart==0.0.29"
```

Note: `httpx-oauth` and `bcrypt` are pulled as transitive dependencies of `fastapi-users[sqlalchemy]`, but pinning them in requirements.txt is still recommended for reproducibility.

**Version verification (confirmed):**
```
fastapi-users: 15.0.5 (2026-03-27)
fastapi-mail:  1.6.4
starlette-csrf: 3.0.0
httpx-oauth:   0.17.0
python-multipart: 0.0.29
bcrypt:        5.0.0
```

---

## Package Legitimacy Audit

| Package | Registry | slopcheck | Disposition |
|---------|----------|-----------|-------------|
| `fastapi-users` | PyPI | [OK] | Approved |
| `httpx-oauth` | PyPI | [OK] | Approved |
| `python-multipart` | PyPI | [OK] — flagged as "classic LLM naming pattern but established" | Approved — well-known, required by FastAPI itself |
| `bcrypt` | PyPI | [OK] | Approved |
| `fastapi-mail` | PyPI | [OK] — flagged "no source repo linked" | Approved — widely used, 1.6.4 with long release history |
| `starlette-csrf` | PyPI | [OK] | Approved |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none (all [OK])

---

## Architecture Patterns

### System Architecture Diagram

```
Browser (SPA)
    |
    |-- POST /api/auth/login     (email+password form)  --.
    |-- GET  /api/auth/google/authorize                  --|--> FastAPI-Users Auth Router
    |-- GET  /api/auth/google/callback                   --'      |
    |                                                             |-- JWTStrategy (access, 1h)
    |  [Server sets httpOnly cookies]                            |-- JWTStrategy (refresh, 30d)
    |                                                             |-- CookieTransport (access)
    |  [Browser reads csrftoken cookie]                          |-- CookieTransport (refresh)
    |-- All POST/PUT/DELETE: header x-csrftoken                  |
    |                                                             v
    |-- GET /api/auth/me         (rehydrate on mount)    starlette-csrf middleware
    |-- POST /api/auth/refresh   (slide refresh token)   validates x-csrftoken header
    |-- POST /api/auth/logout    (clear cookies)
    |
    |-- POST /api/auth/register  (UserCreate)  --> on_after_register --> fastapi-mail --> Mailhog (dev)
    |-- POST /api/auth/verify    (token)       --> on_after_request_verify --> fastapi-mail
    |-- POST /api/auth/forgot-password         --> on_after_forgot_password --> fastapi-mail
    |-- POST /api/auth/reset-password          (token + new password)
    |
    React Context (AuthContext)
        useReducer: { user: User | null, isLoading: boolean }
        actions: SET_USER | CLEAR_USER | SET_LOADING
        on mount: GET /api/auth/me --> dispatch SET_USER or CLEAR_USER
```

### Recommended Project Structure (new files only)

```
backend/app/
├── auth/
│   ├── __init__.py
│   ├── users.py          # UserManager, get_user_manager, fastapi_users instance
│   ├── backends.py       # auth_backend_access, auth_backend_refresh definitions
│   ├── schemas.py        # UserRead, UserCreate, UserUpdate (extend base schemas)
│   └── email.py          # fastapi-mail ConnectionConfig + send functions
├── routers/
│   └── auth.py           # thin wrapper — includes fastapi-users routers + /me + /refresh

frontend/src/
├── contexts/
│   └── AuthContext.tsx   # React Context + useReducer + AuthProvider
├── hooks/
│   └── useAuth.ts        # convenience hook wrapping useContext(AuthContext)
├── components/
│   └── RequireAuth.tsx   # protected route wrapper
├── pages/
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── VerifyEmailPage.tsx
│   └── ResetPasswordPage.tsx
```

### Pattern 1: FastAPI-Users User Model Migration

**What:** The existing `User(Base)` model must swap its `Base` parent to also inherit `SQLAlchemyBaseUserTableUUID`. The field name collision must be resolved via Alembic migration before the library can be used.

**Critical field conflict table:**

| Existing column | FastAPI-Users expected column | Resolution |
|----------------|-------------------------------|------------|
| `password_hash` | `hashed_password` | Alembic: `op.alter_column("users", "password_hash", new_column_name="hashed_password")` |
| `email_verified` | `is_verified` | Alembic: `op.alter_column("users", "email_verified", new_column_name="is_verified")` |
| `is_active` | `is_active` | No change needed — already correct |
| *(missing)* | `is_superuser` | Alembic: `op.add_column("users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"))` |

**Existing fields to keep as extensions:**

```python
# Source: FastAPI-Users docs + existing model analysis
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    # Custom fields (not from base class)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), default=UserRole.registered)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    account_age_days: Mapped[int] = mapped_column(Integer, default=0)
    
    # OAuth accounts relationship
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship("OAuthAccount", lazy="joined")
```

**What `SQLAlchemyBaseUserTableUUID` provides (from source code):**
- `id: Mapped[uuid.UUID]` — primary key, `default=uuid.uuid4`
- `email: Mapped[str]` — `String(320)`, unique, indexed
- `hashed_password: Mapped[str]` — `String(1024)`
- `is_active: Mapped[bool]` — `default=True`
- `is_superuser: Mapped[bool]` — `default=False`
- `is_verified: Mapped[bool]` — `default=False`

[VERIFIED: https://github.com/fastapi-users/fastapi-users-db-sqlalchemy/blob/main/fastapi_users_db_sqlalchemy/__init__.py]

### Pattern 2: Authentication Backend Setup (Access + Refresh Token Pair)

FastAPI-Users has **no built-in refresh token rotation**. The pattern is to create two separate `AuthenticationBackend` instances with different cookie names and JWT lifetimes.

```python
# Source: FastAPI-Users docs + Discussion #350 + Discussion #989
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy

# Access token: 1 hour, httpOnly cookie
cookie_transport_access = CookieTransport(
    cookie_name="khostumner_access",
    cookie_max_age=3600,          # 1 hour
    cookie_httponly=True,
    cookie_secure=False,          # set True in production
    cookie_samesite="lax",
)

# Refresh token: 30 days, httpOnly cookie
cookie_transport_refresh = CookieTransport(
    cookie_name="khostumner_refresh",
    cookie_max_age=60 * 60 * 24 * 30,  # 30 days
    cookie_httponly=True,
    cookie_secure=False,          # set True in production
    cookie_samesite="lax",
)

def get_access_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=3600)

def get_refresh_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=60 * 60 * 24 * 30)

auth_backend_access = AuthenticationBackend(
    name="access_cookie",
    transport=cookie_transport_access,
    get_strategy=get_access_strategy,
)

auth_backend_refresh = AuthenticationBackend(
    name="refresh_cookie",
    transport=cookie_transport_refresh,
    get_strategy=get_refresh_strategy,
)
```

**The refresh endpoint** is a custom route that calls `auth_backend_access.login()` after verifying the user via the refresh backend's `current_user` dependency:

```python
@router.post("/auth/refresh")
async def refresh_access_token(
    response: Response,
    user=Depends(fastapi_users.current_user(active=True)),  # authenticated via refresh backend
):
    return await auth_backend_access.login(get_access_strategy(), user, response)
```

[ASSUMED: The exact sliding refresh implementation — fastapi-users discussion confirms no built-in support; this custom route pattern is from the community. The two-backend approach is documented in Discussion #989.]

### Pattern 3: CSRF Protection with starlette-csrf

```python
# Source: https://github.com/frankie567/starlette-csrf
from starlette_csrf import CSRFMiddleware

app.add_middleware(
    CSRFMiddleware,
    secret=settings.CSRF_SECRET,
    cookie_name="csrftoken",    # readable by JavaScript (not httpOnly)
    header_name="x-csrftoken",  # frontend reads cookie, sends in this header
    cookie_samesite="lax",
    safe_methods={"GET", "HEAD", "OPTIONS", "TRACE"},
)
```

**Frontend responsibility:** On every POST/PUT/DELETE, the React app reads `document.cookie` for `csrftoken` and includes it as `x-csrftoken` header. TanStack Query's `defaultOptions` can inject this globally via a custom fetch wrapper.

**Middleware ordering in FastAPI:** CSRF middleware must be added AFTER CORSMiddleware. FastAPI processes middleware in reverse registration order (last added = outermost), so add CORS first, then CSRF.

[VERIFIED: https://github.com/frankie567/starlette-csrf]

### Pattern 4: OAuth2 Setup (Google + Facebook)

```python
# Source: FastAPI-Users OAuth2 docs
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.facebook import FacebookOAuth2

google_oauth_client = GoogleOAuth2(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
)

facebook_oauth_client = FacebookOAuth2(
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
)

# Router registration (in main.py or auth router)
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend_access,
        settings.JWT_SECRET,
        associate_by_email=True,     # D-07: links OAuth to existing email/password account
        is_verified_by_default=True, # Google verifies emails — mark user as verified automatically
    ),
    prefix="/api/auth/google",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_oauth_router(
        facebook_oauth_client,
        auth_backend_access,
        settings.JWT_SECRET,
        associate_by_email=True,
        is_verified_by_default=True,
    ),
    prefix="/api/auth/facebook",
    tags=["auth"],
)
```

**OAuth callback URLs** (must be registered in Google/Facebook developer consoles):
- Google: `http://localhost:8000/api/auth/google/callback`
- Facebook: `http://localhost:8000/api/auth/facebook/callback`

**OAuthAccount table** (required when using OAuth):
```python
from fastapi_users.db import SQLAlchemyBaseOAuthAccountTableUUID

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass
```

`SQLAlchemyBaseOAuthAccountTableUUID` provides: `id` (UUID PK), `oauth_name` (str), `access_token` (str, up to 1024 chars — see Pitfall 3), `expires_at` (int, nullable), `refresh_token` (str, nullable), `account_id` (str), `account_email` (str), `user_id` (UUID FK to users).

[VERIFIED: https://fastapi-users.github.io/fastapi-users/latest/configuration/oauth/]

### Pattern 5: fastapi-mail + Mailhog + UserManager Hooks

```python
# Source: fastapi-mail docs + fastapi-users UserManager hooks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=settings.SMTP_PORT,      # 1025 for Mailhog
    MAIL_SERVER=settings.SMTP_HOST,    # "mailhog" in Docker, "localhost" dev
    MAIL_FROM_NAME="Խոստումներ",
    MAIL_STARTTLS=False,               # Mailhog does not need TLS
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,             # Mailhog has no auth
)

fm = FastMail(mail_config)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(self, user: User, request=None):
        await fm.send_message(MessageSchema(
            subject="Հաստատեք Ձեր հաշիվը — Խոստումներ",
            recipients=[user.email],
            body=f"<html><body>...</body></html>",  # inline Armenian HTML (D-10)
            subtype=MessageType.html,
        ))

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        # send email with reset_url

    async def on_after_request_verify(self, user: User, token: str, request=None):
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        # send email with verify_url
```

[VERIFIED: https://pypi.org/project/fastapi-mail/ + FastAPI-Users UserManager docs]

### Pattern 6: Frontend Auth State (React Context + useReducer)

```typescript
// contexts/AuthContext.tsx
// Source: React Context + useReducer pattern — standard SPA auth
type AuthState = { user: UserRead | null; isLoading: boolean }
type AuthAction =
  | { type: "SET_USER"; payload: UserRead }
  | { type: "CLEAR_USER" }
  | { type: "SET_LOADING"; payload: boolean }

const AuthContext = createContext<{
  state: AuthState
  dispatch: Dispatch<AuthAction>
} | null>(null)

// On AuthProvider mount: call GET /api/users/me
// If 200 -> dispatch SET_USER; if 401 -> dispatch CLEAR_USER
// Browser automatically sends httpOnly access cookie with every same-origin request
```

**Key insight for httpOnly cookies:** The browser sends the cookie automatically. React does NOT read the token value. The `/api/users/me` endpoint validates the cookie and returns the user object (or 401). The frontend's "are we logged in?" question is answered entirely by calling this endpoint on mount.

**Page refresh persistence (AUTH-05):** The AuthProvider calls `/api/users/me` on every mount. If the access cookie is still valid, the user is rehydrated silently. If the access cookie is expired but the refresh cookie is valid, the frontend calls `/api/auth/refresh` first (sets a new access cookie), then retries `/api/users/me`.

### Pattern 7: Protected Route (React Router v7)

```typescript
// components/RequireAuth.tsx
import { Navigate, Outlet, useLocation } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"

export default function RequireAuth() {
  const { state } = useAuth()
  const location = useLocation()

  if (state.isLoading) return <div>...</div>  // avoid flash of redirect

  if (!state.user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
```

**Usage in App.tsx:**
```tsx
<Route element={<RequireAuth />}>
  <Route path="/submit" element={<SubmitPromisePage />} />
  {/* future protected routes */}
</Route>
```

[CITED: https://blog.logrocket.com/authentication-react-router-v7/]

### Anti-Patterns to Avoid

- **Storing JWT in localStorage:** XSS can steal it. Decision D-03 prohibits this.
- **Using `allow_origins=["*"]` with `allow_credentials=True`:** FastAPI/Starlette raises a runtime error. Always use explicit origin list.
- **Calling `is_superuser` as the admin check:** The project uses `UserRole.admin` in the `role` column. `is_superuser` in FastAPI-Users is a different concept. Use role-based guards, not `is_superuser`.
- **Adding starlette-csrf BEFORE CORSMiddleware:** Causes CORS preflight (OPTIONS) to be rejected as unsafe. Always add CSRF after CORS in registration order.
- **Not sending `credentials: "include"` from the frontend:** Without this flag on `fetch` calls, the browser omits cookies on cross-origin requests even if the server allows them.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Registration + email verification flow | Custom `/register` endpoint | `fastapi_users.get_register_router()` + `get_verify_router()` | Handles token generation, secure comparison, expiry |
| Password hashing | Custom bcrypt calls | FastAPI-Users' internal `PasswordHelper` | Automatically upgrades hash algorithm version |
| Password reset token flow | Custom token table | `fastapi_users.get_reset_password_router()` | Handles token signing, expiry, one-time use |
| OAuth2 PKCE flow | Custom OAuth state/code exchange | `httpx-oauth` GoogleOAuth2/FacebookOAuth2 | Handles CSRF token, state parameter, token exchange |
| JWT signing/verification | `pyjwt` calls directly | `JWTStrategy` from fastapi-users | Handles audience, expiry, secret rotation patterns |
| CSRF token generation | Custom HMAC token | `starlette-csrf` | Double-submit pattern, safe method exemption, URL-based exemptions |

**Key insight:** FastAPI-Users reduces the auth attack surface from ~15 custom endpoints to 0 — every route that handles credentials or tokens is library-managed and tested.

---

## Common Pitfalls

### Pitfall 1: Schema Conflict — password_hash vs hashed_password

**What goes wrong:** The existing `users` table has `password_hash` (String 255). FastAPI-Users reads and writes `hashed_password`. SQLAlchemy will map the ORM model attribute `hashed_password` to a column that does not exist, causing `UndefinedColumn` errors on any login attempt.

**Why it happens:** The existing Phase 1 schema was hand-designed before FastAPI-Users was chosen.

**How to avoid:** Alembic migration in Wave 0 must rename `password_hash` -> `hashed_password` AND `email_verified` -> `is_verified` AND add `is_superuser` column.

**Warning signs:** `sqlalchemy.exc.ProgrammingError: column users.hashed_password does not exist`

### Pitfall 2: Missing is_superuser Column

**What goes wrong:** FastAPI-Users always reads `is_superuser` from the user row. If the column is missing, every authenticated request fails.

**How to avoid:** Include `is_superuser BOOLEAN NOT NULL DEFAULT FALSE` in the same migration as the column renames (Wave 0).

### Pitfall 3: OAuthAccount Token Length

**What goes wrong:** Google RS256 access tokens can exceed 1024 characters. The default `SQLAlchemyBaseOAuthAccountTableUUID.access_token` is `String(1024)`. Token truncation causes silent login failures.

**How to avoid:** Override the column in the `OAuthAccount` model:

```python
class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    access_token: Mapped[str] = mapped_column(String(4096), nullable=False)
```

[CITED: https://github.com/fastapi-users/fastapi-users-db-sqlalchemy/issues/20]

### Pitfall 4: CSRF Middleware Order

**What goes wrong:** starlette-csrf added before CORSMiddleware blocks all OAuth redirects (which use GET, but the callback uses POST in some flows) and can block preflight OPTIONS requests.

**How to avoid:** `app.add_middleware(CORSMiddleware, ...)` first, then `app.add_middleware(CSRFMiddleware, ...)`. FastAPI processes middleware in reverse order of registration (last registered = outermost wrapper).

### Pitfall 5: Mailhog Image Status

**What goes wrong:** `mailhog/mailhog` Docker image has been unmaintained since 2020. The image still works but has no security patches. For a project that handles user emails (even in dev), this is a risk to be aware of.

**How to avoid:** D-08 locks this choice as Mailhog. For awareness: `axllent/mailpit` is the maintained replacement, is API-compatible, and is a one-line change if the decision is revisited. SMTP port 1025 + web UI port 8025 remain the same.

[CITED: https://sendpigeon.dev/blog/mailpit-vs-mailhog]

### Pitfall 6: Frontend Cookie Fetch Without credentials: include

**What goes wrong:** All auth API calls use `fetch` or TanStack Query's default fetcher. By default, `fetch` does NOT send cookies for cross-origin requests (localhost:5173 → localhost:8000). Login sets the cookie, but the next `GET /api/users/me` request omits it, returning 401.

**How to avoid:** Configure a global API client (or TanStack Query `defaultOptions`) that always sets `credentials: "include"`.

### Pitfall 7: display_name Required Field Not in FastAPI-Users BaseUserCreate

**What goes wrong:** FastAPI-Users' `BaseUserCreate` only requires `email` + `password`. The project requires `display_name`. If not extended, registrations succeed but `display_name` is left empty/null, causing NOT NULL constraint violations.

**How to avoid:** Extend `UserCreate` schema:
```python
class UserCreate(BaseUserCreate):
    display_name: str  # required
```

And handle in `UserManager.on_after_register` or override `create()` to set `display_name` from the request.

### Pitfall 8: FastAPI-Users Maintenance Mode

**What goes wrong:** The library is in maintenance mode as of 2025. No new features will be added. If a dependency (e.g., Pydantic v3, SQLAlchemy 3.0) introduces breaking changes, updates may be slow.

**Impact for this phase:** Low risk — the library is stable at 15.0.5 and the dependencies (FastAPI 0.115.x, SQLAlchemy 2.x, Pydantic 2.x) are all already pinned in the project.

[CITED: https://fastapi-users.github.io/fastapi-users/latest/]

---

## Code Examples

### Full UserManager with Hooks

```python
# backend/app/auth/users.py
import uuid
from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.models.users import User, OAuthAccount
from app.database import AsyncSessionLocal  # reuse existing session factory

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(self, user: User, request=None):
        # send verification email via fastapi-mail (D-09)
        pass

    async def on_after_forgot_password(self, user, token, request=None):
        # send reset email
        pass

    async def on_after_request_verify(self, user, token, request=None):
        # send verification email
        pass

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_access, auth_backend_refresh],
)
```

### Router Registration in main.py (alphabetical — auth first)

```python
# main.py additions
from app.auth.users import fastapi_users, auth_backend_access, auth_backend_refresh
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.facebook import FacebookOAuth2

# Auth routers (insert before existing routers, alphabetical)
app.include_router(fastapi_users.get_auth_router(auth_backend_access), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/api/users", tags=["users"])
app.include_router(fastapi_users.get_oauth_router(google_oauth_client, auth_backend_access, settings.JWT_SECRET, associate_by_email=True, is_verified_by_default=True), prefix="/api/auth/google", tags=["auth"])
app.include_router(fastapi_users.get_oauth_router(facebook_oauth_client, auth_backend_access, settings.JWT_SECRET, associate_by_email=True, is_verified_by_default=True), prefix="/api/auth/facebook", tags=["auth"])
```

### Alembic Migration for User Model Changes

```python
# alembic/versions/YYYYMMDD_auth_schema.py
def upgrade():
    # Rename password_hash -> hashed_password (D-02)
    op.alter_column("users", "password_hash", new_column_name="hashed_password")
    # Rename email_verified -> is_verified (D-02)
    op.alter_column("users", "email_verified", new_column_name="is_verified")
    # Add missing is_superuser column
    op.add_column("users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"))
    # Create oauth_accounts table
    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("oauth_name", sa.String(length=100), nullable=False, index=True),
        sa.Column("access_token", sa.String(length=4096), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("refresh_token", sa.String(length=4096), nullable=True),
        sa.Column("account_id", sa.String(length=320), nullable=False, index=True),
        sa.Column("account_email", sa.String(length=320), nullable=False, index=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk__oauth_accounts__user_id__users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__oauth_accounts")),
    )
```

### Settings Extensions (config.py)

```python
class Settings(BaseSettings):
    # ... existing fields ...
    JWT_SECRET: str = "change-me-in-production"
    CSRF_SECRET: str = "change-me-in-production-csrf"
    SMTP_HOST: str = "mailhog"       # Docker service name
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@khostumner.am"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FACEBOOK_CLIENT_ID: str = ""
    FACEBOOK_CLIENT_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:5173"
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| JWT in localStorage | JWT in httpOnly cookie | Eliminates XSS token theft; requires CSRF protection |
| Single long-lived JWT | Access + refresh token pair | Minimizes exposure window; refresh enables session extension |
| Mailhog for dev email | Mailpit (axllent/mailpit) | Mailpit is maintained; same API; decision D-08 keeps Mailhog |
| FastAPI-Users v10.x | FastAPI-Users v15.0.5 (latest) | Stable; maintenance mode since Oct 2025 |

**Deprecated/outdated:**
- `fastapi-users` v9.x and earlier: different import paths, `UserDB` class removed in v10 — all examples from pre-v10 tutorials are incompatible
- `email-validator` as standalone install: bundled in fastapi-users since v10

---

## Runtime State Inventory

> Greenfield auth additions — no rename/refactor. However, the Alembic column rename touches existing data.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `users` table — existing rows have `password_hash` and `email_verified` columns; seed data has ~10 rows | Alembic migration renames columns in-place (no data loss) |
| Stored data | No `oauth_accounts` table exists | Alembic creates new table |
| Live service config | No external services configured yet | None |
| OS-registered state | None | None |
| Secrets/env vars | No JWT_SECRET, SMTP_*, OAuth client IDs in .env | Add to .env and docker-compose.yml environment blocks |
| Build artifacts | None relevant | None |

---

## Open Questions (RESOLVED)

1. **Refresh token sliding window behavior** [RESOLVED]
   - What we know: fastapi-users has no built-in rotation; the two-backend pattern issues new access tokens when refresh is valid.
   - **Decision:** Use a fixed 30-day refresh cookie (non-sliding) for Phase 4 MVP. True sliding window requires a Redis token store — deferred to a future phase if needed. The custom `/api/auth/refresh` endpoint validates the refresh cookie and issues a new access token cookie without resetting the refresh cookie's expiry.

2. **OAuth dev credentials for Google/Facebook** [RESOLVED]
   - What we know: OAuth routes will be wired but require real client IDs/secrets.
   - **Decision:** Include a `checkpoint:human-verify` task (plan 04-06) for OAuth credential creation. Email/password registration, login, and verification are fully testable without OAuth credentials. `test_oauth_google_authorize` is marked `pytest.mark.skipif(not settings.GOOGLE_CLIENT_ID)` so CI passes without credentials.

3. **display_name population for OAuth users** [RESOLVED]
   - What we know: FastAPI-Users creates the user from the OAuth provider's data (email, account_id). It does NOT automatically set `display_name`.
   - **Decision:** Override `UserManager.on_after_oauth_register` to set `display_name` from the OAuth provider's name claim if available, else default to the email local part (everything before `@`). This ensures `display_name` is never empty/null (NOT NULL constraint) for OAuth registrations.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | Mailhog container | Yes | 29.4.3 | — |
| Python 3.12+ | Backend | Yes | 3.13.2 | — |
| Node.js 18+ | Frontend | Yes | 26.2.0 | — |
| PostgreSQL | DB | Available via Docker | 17 (in Docker) | — |
| fastapi-users 15.0.5 | Backend auth | Yes (PyPI) | 15.0.5 | — |
| fastapi-mail 1.6.4 | Email hooks | Yes (PyPI) | 1.6.4 | — |
| starlette-csrf 3.0.0 | CSRF middleware | Yes (PyPI) | 3.0.0 | — |
| httpx-oauth 0.17.0 | OAuth clients | Yes (PyPI, bundled) | 0.17.0 | — |
| Google OAuth credentials | AUTH-04 | No (needs setup) | — | Use email/password only during dev |
| Facebook OAuth credentials | AUTH-04 | No (needs setup) | — | Use email/password only during dev |

**Missing dependencies with no fallback:** none (all installable)

**Missing dependencies with fallback:**
- Google/Facebook OAuth credentials: email/password + email verification fully testable without them. OAuth routes exist but return errors without valid client IDs — functional for Phase 4.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 1.3.0 (pytest-asyncio) |
| Config file | `backend/pyproject.toml` — `asyncio_mode = "auto"` |
| Quick run command | `pytest tests/test_auth.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | POST /api/auth/register creates user, returns 201 | integration | `pytest tests/test_auth.py::test_register_success -x` | Wave 0 |
| AUTH-01 | Duplicate email registration returns 400 | integration | `pytest tests/test_auth.py::test_register_duplicate_email -x` | Wave 0 |
| AUTH-02 | POST /api/auth/request-verify-token sends verification email (mock SMTP) | integration | `pytest tests/test_auth.py::test_request_verify -x` | Wave 0 |
| AUTH-02 | POST /api/auth/verify with valid token sets is_verified=True | integration | `pytest tests/test_auth.py::test_verify_email -x` | Wave 0 |
| AUTH-03 | POST /api/auth/forgot-password triggers email hook (mock SMTP) | integration | `pytest tests/test_auth.py::test_forgot_password -x` | Wave 0 |
| AUTH-03 | POST /api/auth/reset-password with valid token changes password | integration | `pytest tests/test_auth.py::test_reset_password -x` | Wave 0 |
| AUTH-04 | GET /api/auth/google/authorize returns redirect URL | smoke | `pytest tests/test_auth.py::test_oauth_google_authorize -x` | Wave 0 |
| AUTH-05 | GET /api/users/me with valid access cookie returns 200 | integration | `pytest tests/test_auth.py::test_me_authenticated -x` | Wave 0 |
| AUTH-05 | GET /api/users/me without cookie returns 401 | integration | `pytest tests/test_auth.py::test_me_unauthenticated -x` | Wave 0 |

**Frontend tests (Vitest):**
| Component | Behavior | Test Type | Automated Command |
|-----------|----------|-----------|-------------------|
| `AuthContext` | Initial state is `isLoading=true`, resolves after /me | unit | `npm run test -- --run src/contexts/AuthContext.test.tsx` |
| `RequireAuth` | Redirects to /login when user is null | unit | `npm run test -- --run src/components/RequireAuth.test.tsx` |
| `LoginPage` | Form submission calls /api/auth/login | unit | `npm run test -- --run src/pages/LoginPage.test.tsx` |

### Sampling Rate

- **Per task commit:** `pytest tests/test_auth.py -x`
- **Per wave merge:** `pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_auth.py` — covers all AUTH-0x requirements (new file)
- [ ] `src/contexts/AuthContext.test.tsx` — covers context reducer logic
- [ ] `src/components/RequireAuth.test.tsx` — covers redirect behavior
- [ ] `src/pages/LoginPage.test.tsx` — covers form submission

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | fastapi-users (registration, verification, password reset, OAuth) |
| V3 Session Management | Yes | httpOnly CookieTransport + 1hr access / 30-day refresh token pair |
| V4 Access Control | Partial (Phase 4 scope is auth only; RBAC enforced in Phase 5+) | `UserRole` enum + `fastapi_users.current_user(active=True)` dependency |
| V5 Input Validation | Yes | Pydantic v2 schemas (UserCreate, UserUpdate) with email-validator |
| V6 Cryptography | Yes | bcrypt (password hashing via fastapi-users); JWT (HS256 via JWTStrategy) |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XSS token theft | Information Disclosure | httpOnly cookie — JS cannot read token |
| CSRF on state-changing requests | Tampering | starlette-csrf double-submit cookie; x-csrftoken header required |
| OAuth state forgery | Spoofing | httpx-oauth handles state parameter generation and validation |
| Brute-force registration/login | Denial of Service | FastAPI-Users rate limiting not built in — note for Phase 4: rely on Nginx rate limiting or accept for MVP |
| Token replay after logout | Elevation of Privilege | JWTs are not revocable; logout clears client cookie only. Acceptable for MVP; server-side revocation requires Redis (deferred) |
| Email enumeration via forgot-password | Information Disclosure | FastAPI-Users always returns 202 regardless of email existence — correct behavior built in |
| Account takeover via email association | Tampering | `associate_by_email=True` requires trusting provider's email validation; Google/Facebook both verify emails — acceptable risk |

---

## Project Constraints (from CLAUDE.md)

| Directive | Impact on Phase 4 |
|-----------|-------------------|
| FastAPI 0.115.x + SQLAlchemy 2.x (async) | fastapi-users 15.0.5 is compatible |
| JWT sessions, FastAPI-Users or custom JWT with RBAC | fastapi-users chosen (D-01); UserRole enum provides RBAC tiers |
| Two separate status fields (moderation_status + resolved_status) | No impact on Phase 4 |
| Individual vote rows with UNIQUE(promise_id, user_id) | No impact on Phase 4 |
| stats_cache table — never GROUP BY on every request | No impact on Phase 4 |
| No admin override of resolved_status | No impact on Phase 4 |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Two-backend pattern (access + refresh JWTStrategy) provides a functional sliding refresh via custom `/auth/refresh` endpoint | Architecture Patterns §2 | Refresh implementation may need adjustment; fallback is single long-lived access token (less ideal) |
| A2 | `is_verified_by_default=True` for Google/Facebook OAuth correctly marks new OAuth users as verified without requiring email verification | Pattern 4 — OAuth | If wrong, OAuth users would be stuck requiring email verification for an email the provider already verified |
| A3 | `display_name` can be populated during OAuth user creation via `UserManager` override or post-registration hook | Open Questions §3 | If fastapi-users does not expose the OAuth profile data in the hook, display_name would need to be set via a separate `/users/me` PATCH after OAuth login |
| A4 | `op.alter_column("users", "password_hash", new_column_name="hashed_password")` works as expected in Alembic with psycopg2-binary on PostgreSQL 17 | Code Examples — Alembic | PostgreSQL supports column rename via ALTER TABLE...RENAME COLUMN; low risk |

**If this table is empty:** All other claims in this research were verified or cited.

---

## Sources

### Primary (HIGH confidence)

- [FastAPI-Users official docs](https://fastapi-users.github.io/fastapi-users/latest/) — routers, transports, strategies, OAuth, UserManager hooks
- [fastapi-users-db-sqlalchemy source code](https://github.com/fastapi-users/fastapi-users-db-sqlalchemy/blob/main/fastapi_users_db_sqlalchemy/__init__.py) — exact column names in SQLAlchemyBaseUserTableUUID
- [PyPI: fastapi-users 15.0.5](https://pypi.org/project/fastapi-users/) — verified via `pip index versions`
- [PyPI: fastapi-mail 1.6.4](https://pypi.org/project/fastapi-mail/) — verified via `pip index versions`
- [PyPI: starlette-csrf 3.0.0](https://pypi.org/project/starlette-csrf/) — verified via `pip index versions`
- [PyPI: httpx-oauth 0.17.0](https://pypi.org/project/httpx-oauth/) — verified via `pip index versions`
- [starlette-csrf GitHub README](https://github.com/frankie567/starlette-csrf) — double-submit cookie pattern, configuration parameters
- [FastAPI-Users OAuth docs](https://fastapi-users.github.io/fastapi-users/latest/configuration/oauth/) — OAuthAccount table, associate_by_email, router setup
- Project codebase — existing `backend/app/models/users.py`, `backend/app/main.py`, `backend/app/config.py`, `docker-compose.yml`, `backend/alembic/versions/20260521_000001_initial_schema.py`

### Secondary (MEDIUM confidence)

- [FastAPI-Users Discussion #989](https://github.com/fastapi-users/fastapi-users/discussions/989) — two auth backends pattern
- [FastAPI-Users Discussion #350](https://github.com/fastapi-users/fastapi-users/discussions/350) — refresh token limitation confirmed by maintainer
- [fastapi-users-db-sqlalchemy Issue #20](https://github.com/fastapi-users/fastapi-users-db-sqlalchemy/issues/20) — OAuthAccount access_token length issue
- [React Router v7 authentication guide](https://blog.logrocket.com/authentication-react-router-v7/) — RequireAuth pattern

### Tertiary (LOW confidence)

- [Mailpit vs Mailhog 2025 comparison](https://sendpigeon.dev/blog/mailpit-vs-mailhog) — Mailhog unmaintained since 2020

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified on PyPI, slopcheck clean, official docs consulted
- Architecture: HIGH — based on official docs + source code inspection of base class columns
- Pitfalls: HIGH — column name conflict verified by reading both source code and existing migration; OAuth token length is a documented GitHub issue
- Refresh token pattern: MEDIUM — community-derived workaround; no official documentation

**Research date:** 2026-05-23
**Valid until:** 2026-08-23 (fastapi-users in maintenance mode — stable; 90 days reasonable)
