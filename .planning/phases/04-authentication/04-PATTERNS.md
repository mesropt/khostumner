# Phase 4: Authentication - Pattern Map

**Mapped:** 2026-05-23
**Files analyzed:** 14
**Analogs found:** 12 / 14

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `backend/app/models/users.py` | model | CRUD | `backend/app/models/politicians.py` | role-match |
| `backend/alembic/versions/20260523_000001_auth_schema.py` | migration | CRUD | `backend/alembic/versions/20260522_000001_add_party_slug.py` | exact |
| `backend/app/config.py` | config | — | `backend/app/config.py` (self — extend) | exact |
| `backend/app/main.py` | config | request-response | `backend/app/main.py` (self — extend) | exact |
| `backend/app/auth/__init__.py` | utility | — | `backend/app/routers/__init__.py` | partial |
| `backend/app/auth/users.py` | service | request-response | `backend/app/database.py` | partial |
| `backend/app/auth/backends.py` | config | request-response | `backend/app/config.py` | partial |
| `backend/app/auth/schemas.py` | model | request-response | `backend/app/schemas/politicians.py` | role-match |
| `backend/app/auth/email.py` | service | event-driven | none | no analog |
| `backend/app/routers/auth.py` | route | request-response | `backend/app/routers/health.py` | role-match |
| `docker-compose.yml` | config | — | `docker-compose.yml` (self — extend) | exact |
| `frontend/src/App.tsx` | config | request-response | `frontend/src/App.tsx` (self — extend) | exact |
| `frontend/src/components/Layout.tsx` | component | request-response | `frontend/src/components/Layout.tsx` (self — extend) | exact |
| `frontend/src/contexts/AuthContext.tsx` | provider | event-driven | none | no analog |
| `frontend/src/hooks/useAuth.ts` | hook | request-response | `frontend/src/hooks/usePolitician.ts` | role-match |
| `frontend/src/pages/LoginPage.tsx` | component | request-response | `frontend/src/pages/PromisesListPage.tsx` | role-match |
| `frontend/src/pages/RegisterPage.tsx` | component | request-response | `frontend/src/pages/PromisesListPage.tsx` | role-match |
| `frontend/src/pages/VerifyEmailPage.tsx` | component | request-response | `frontend/src/pages/AboutPage.tsx` | role-match |
| `frontend/src/pages/ResetPasswordPage.tsx` | component | request-response | `frontend/src/pages/PromisesListPage.tsx` | role-match |
| `frontend/src/components/RequireAuth.tsx` | middleware | request-response | none | no analog |

---

## Pattern Assignments

### `backend/app/models/users.py` (model, CRUD — modify existing)

**Analog:** `backend/app/models/politicians.py`

**Existing file** (`backend/app/models/users.py` lines 1-33):
```python
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserRole(str, enum.Enum):
    registered = "registered"
    moderator = "moderator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), default=UserRole.registered
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    account_age_days: Mapped[int] = mapped_column(Integer, default=0)
```

**What must change:**
- Replace `class User(Base):` with `class User(SQLAlchemyBaseUserTableUUID, Base):`
- Remove the explicit `id`, `email`, `is_active` columns (provided by base mixin)
- Rename `password_hash` -> `hashed_password` (done via Alembic; model attribute name must match)
- Rename `email_verified` -> `is_verified` (done via Alembic; model attribute name must match)
- Add `is_superuser` (provided by base mixin after migration adds the column)
- Add `OAuthAccount` class using `SQLAlchemyBaseOAuthAccountTableUUID`
- Add `oauth_accounts` relationship on `User`

**Analog pattern** — how base model class + custom columns coexist (`backend/app/models/politicians.py` lines 17-38):
```python
class Politician(Base):
    __tablename__ = "politicians"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_hy: Mapped[str] = mapped_column(String(200), nullable=False)
    ...
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
```

**Target form for users.py:**
```python
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyBaseOAuthAccountTableUUID
from sqlalchemy.orm import relationship

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    __tablename__ = "oauth_accounts"
    # Override access_token to String(4096) — Google RS256 tokens exceed 1024 chars (Pitfall 3)
    access_token: Mapped[str] = mapped_column(String(4096), nullable=False)

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    # Fields provided by SQLAlchemyBaseUserTableUUID (DO NOT redeclare):
    #   id, email, hashed_password, is_active, is_superuser, is_verified
    
    # Custom extensions (keep from existing model):
    display_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), default=UserRole.registered
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    account_age_days: Mapped[int] = mapped_column(Integer, default=0)
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship("OAuthAccount", lazy="joined")
```

---

### `backend/alembic/versions/20260523_000001_auth_schema.py` (migration, CRUD — new)

**Analog:** `backend/alembic/versions/20260522_000001_add_party_slug.py`

**Revision header pattern** (lines 1-18 of analog):
```python
"""add_party_slug

Revision ID: 20260522_000001
Revises: 20260521_000001
Create Date: 2026-05-22 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260522_000001"
down_revision: Union[str, None] = "20260521_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
```

**Alter column pattern** (lines 43-47 of analog — nullable enforcement after data backfill):
```python
op.alter_column("parties", "slug", nullable=False)
op.create_unique_constraint("uq__parties__slug", "parties", ["slug"])
```

**Naming convention for constraints:** All existing migrations use `op.f("pk__TABLE")`, `op.f("uq__TABLE__COL")`, `op.f("fk__TABLE__COL__REFTABLE")` pattern — follow exactly.

**Target upgrade() for this migration:**
```python
def upgrade() -> None:
    # 1. Rename password_hash -> hashed_password
    op.alter_column("users", "password_hash", new_column_name="hashed_password")
    # 2. Rename email_verified -> is_verified
    op.alter_column("users", "email_verified", new_column_name="is_verified")
    # 3. Add is_superuser (missing column required by FastAPI-Users)
    op.add_column("users", sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"))
    # 4. Create oauth_accounts table
    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("oauth_name", sa.String(length=100), nullable=False),
        sa.Column("access_token", sa.String(length=4096), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("refresh_token", sa.String(length=4096), nullable=True),
        sa.Column("account_id", sa.String(length=320), nullable=False),
        sa.Column("account_email", sa.String(length=320), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],
            name=op.f("fk__oauth_accounts__user_id__users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__oauth_accounts")),
    )
    op.create_index(op.f("ix__oauth_accounts__oauth_name"), "oauth_accounts", ["oauth_name"])
    op.create_index(op.f("ix__oauth_accounts__account_id"), "oauth_accounts", ["account_id"])
    op.create_index(op.f("ix__oauth_accounts__account_email"), "oauth_accounts", ["account_email"])
```

**downgrade() pattern** — reverse operations in reverse order (drop constraints before columns):
```python
def downgrade() -> None:
    op.drop_table("oauth_accounts")
    op.drop_column("users", "is_superuser")
    op.alter_column("users", "is_verified", new_column_name="email_verified")
    op.alter_column("users", "hashed_password", new_column_name="password_hash")
```

---

### `backend/app/config.py` (config — modify existing)

**Existing file** (`backend/app/config.py` lines 1-13):
```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://khostumner:khostumner@localhost:5432/khostumner"
    DB_ECHO: bool = False
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
```

**Pattern — add fields to the same `Settings` class, preserve existing fields:**
```python
class Settings(BaseSettings):
    # ... existing fields unchanged ...

    # Phase 4: Auth
    JWT_SECRET: str = "change-me-in-production"
    CSRF_SECRET: str = "change-me-in-production-csrf"
    SMTP_HOST: str = "mailhog"
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

### `backend/app/main.py` (config — modify existing)

**Existing router registration pattern** (`backend/app/main.py` lines 1-40):
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.routers import elections, health, og, parties, politicians, promises, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Khostumner API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(politicians.router, prefix="/api")
app.include_router(parties.router, prefix="/api")
app.include_router(elections.router, prefix="/api")
app.include_router(promises.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(og.router, prefix="/api")
```

**What to add:**
1. Import `CSRFMiddleware` and add it AFTER `CORSMiddleware` (CSRF must be registered after CORS)
2. Import `fastapi_users`, backends, schemas, OAuth clients from `app.auth.*`
3. Register auth routers alphabetically first (before `health.router`)

**Target additions:**
```python
# After CORSMiddleware registration:
from starlette_csrf import CSRFMiddleware
from app.config import settings

app.add_middleware(
    CSRFMiddleware,
    secret=settings.CSRF_SECRET,
    cookie_name="csrftoken",
    header_name="x-csrftoken",
    cookie_samesite="lax",
    safe_methods={"GET", "HEAD", "OPTIONS", "TRACE"},
)

# Router registration — auth routers before existing routers (alphabetical):
from app.auth.users import fastapi_users, auth_backend_access, auth_backend_refresh
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from app.auth.oauth import google_oauth_client, facebook_oauth_client

app.include_router(fastapi_users.get_auth_router(auth_backend_access), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/api/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/api/users", tags=["users"])
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend_access, settings.JWT_SECRET,
        associate_by_email=True, is_verified_by_default=True),
    prefix="/api/auth/google", tags=["auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(facebook_oauth_client, auth_backend_access, settings.JWT_SECRET,
        associate_by_email=True, is_verified_by_default=True),
    prefix="/api/auth/facebook", tags=["auth"],
)
# Then existing routers follow unchanged
app.include_router(health.router)
...
```

---

### `backend/app/auth/users.py` (service, request-response — new)

**Analog:** `backend/app/database.py` — the async session dependency generator pattern

**Session dependency pattern** (`backend/app/database.py` lines 25-33):
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Import pattern from `backend/app/database.py`** (lines 1-22):
```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings
```

**Target file structure:**
```python
import uuid
from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.models.users import User, OAuthAccount
from app.database import AsyncSessionLocal
from app.config import settings
# Import backends from backends.py (auth_backend_access, auth_backend_refresh)

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

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        # send reset email
        pass

    async def on_after_request_verify(self, user: User, token: str, request=None):
        # send verification email
        pass

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_access, auth_backend_refresh],
)
```

---

### `backend/app/auth/backends.py` (config — new)

**No direct analog** — new pattern; use RESEARCH.md Pattern 2 verbatim.

**Target file:**
```python
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy
from app.config import settings

cookie_transport_access = CookieTransport(
    cookie_name="khostumner_access",
    cookie_max_age=3600,
    cookie_httponly=True,
    cookie_secure=False,   # True in production
    cookie_samesite="lax",
)

cookie_transport_refresh = CookieTransport(
    cookie_name="khostumner_refresh",
    cookie_max_age=60 * 60 * 24 * 30,
    cookie_httponly=True,
    cookie_secure=False,
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

---

### `backend/app/auth/schemas.py` (model, request-response — new)

**Analog:** `backend/app/schemas/politicians.py`

**Schema pattern** (`backend/app/schemas/politicians.py` lines 1-20):
```python
import uuid

from pydantic import BaseModel, ConfigDict

from app.models.politicians import PoliticianLevel


class PoliticianOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    slug: str
    ...
```

**Target file — extend FastAPI-Users base schemas:**
```python
import uuid
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    display_name: str
    role: str  # UserRole enum serialized as string

class UserCreate(schemas.BaseUserCreate):
    display_name: str  # required — Pitfall 7: not in BaseUserCreate

class UserUpdate(schemas.BaseUserUpdate):
    display_name: str | None = None
```

**Note:** FastAPI-Users schemas use Pydantic v2 internally with `model_config = ConfigDict(from_attributes=True)` already set in base classes. Do NOT add `model_config` manually.

---

### `backend/app/auth/email.py` (service, event-driven — new)

**No close analog** — no email-sending code exists yet. Use RESEARCH.md Pattern 5 verbatim.

**Target file structure:**
```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="Խոստումներ",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,
)

fm = FastMail(mail_config)

async def send_verification_email(email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    await fm.send_message(MessageSchema(
        subject="Հաստատեք Ձեր հաշիվը — Խոստումներ",
        recipients=[email],
        body=f"<html><body><p>Հետևեք հղմանը՝ <a href='{verify_url}'>{verify_url}</a></p></body></html>",
        subtype=MessageType.html,
    ))

async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    await fm.send_message(MessageSchema(
        subject="Գաղտնաբառի վերականգնում — Խոստումներ",
        recipients=[email],
        body=f"<html><body><p>Հետևեք հղմանը՝ <a href='{reset_url}'>{reset_url}</a></p></body></html>",
        subtype=MessageType.html,
    ))
```

---

### `backend/app/routers/auth.py` (route, request-response — new)

**Analog:** `backend/app/routers/health.py`

**Thin router pattern** (`backend/app/routers/health.py` lines 1-8):
```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Note:** Most auth routes are wired directly in `main.py` via FastAPI-Users. `auth.py` router provides only the custom `/auth/refresh` endpoint and `/auth/me` alias. The `router` object pattern uses `APIRouter(tags=["auth"])` following the `prefix` convention already in `main.py`.

**Target:**
```python
from fastapi import APIRouter, Depends, Response
from app.auth.users import fastapi_users, auth_backend_access, get_access_strategy

router = APIRouter(tags=["auth"])

@router.post("/auth/refresh")
async def refresh_access_token(
    response: Response,
    user=Depends(fastapi_users.current_user(active=True)),
):
    return await auth_backend_access.login(get_access_strategy(), user, response)
```

---

### `docker-compose.yml` (config — modify existing)

**Existing service block pattern** (lines 1-22 — postgres service):
```yaml
services:
  postgres:
    image: postgres:17
    env_file:
      - .env
    environment:
      POSTGRES_DB: khostumner
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U khostumner -d khostumner"]
      interval: 5s
      timeout: 5s
      retries: 10
    restart: unless-stopped
```

**Add mailhog service after postgres, before backend:**
```yaml
  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"   # SMTP
      - "8025:8025"   # Web UI
    restart: unless-stopped
```

**Add environment variables to `backend` service `environment:` block:**
```yaml
      SMTP_HOST: mailhog
      SMTP_PORT: "1025"
      SMTP_FROM: noreply@khostumner.am
      JWT_SECRET: dev-jwt-secret-change-in-production
      CSRF_SECRET: dev-csrf-secret-change-in-production
      FRONTEND_URL: http://localhost:5173
```

**Add `mailhog` to backend `depends_on` block.**

---

### `frontend/src/App.tsx` (config — modify existing)

**Existing route block** (`frontend/src/App.tsx` lines 16-35):
```tsx
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        ...
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
```

**Add auth routes inside existing `<Route element={<Layout />}>` block, and wrap protected routes with `<RequireAuth>`:**
```tsx
import LoginPage from "@/pages/LoginPage"
import RegisterPage from "@/pages/RegisterPage"
import VerifyEmailPage from "@/pages/VerifyEmailPage"
import ResetPasswordPage from "@/pages/ResetPasswordPage"
import RequireAuth from "@/components/RequireAuth"
import { AuthProvider } from "@/contexts/AuthContext"

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<Layout />}>
          {/* Existing public routes unchanged */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          {/* Protected routes (Phase 5+) wrapped in RequireAuth */}
          <Route element={<RequireAuth />}>
            {/* e.g. <Route path="/submit" element={<SubmitPromisePage />} /> */}
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
```

---

### `frontend/src/components/Layout.tsx` (component — modify existing)

**Existing nav pattern** (`frontend/src/components/Layout.tsx` lines 1-38):
```tsx
import { NavLink, Outlet } from "react-router-dom"

export default function Layout() {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? "text-sm font-semibold text-zinc-900"
      : "text-sm text-zinc-600 hover:text-zinc-900"

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="sticky top-0 z-10 bg-white border-b border-zinc-200">
        <nav className="max-w-7xl mx-auto px-4 flex items-center gap-6 h-14">
          <NavLink to="/" className={navLinkClass} end>
            <span className="font-bold text-lg text-zinc-900">Խոստումներ</span>
          </NavLink>
          ...
        </nav>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
```

**Pattern — add auth nav items right-aligned using `ml-auto` on a flex container:**
```tsx
import { useAuth } from "@/hooks/useAuth"

// Inside the nav, after existing NavLinks:
const { state, dispatch } = useAuth()

// Right-aligned auth section:
<div className="ml-auto flex items-center gap-4">
  {state.user ? (
    <>
      <span className="text-sm text-zinc-600">{state.user.display_name}</span>
      <button
        onClick={() => { /* call /api/auth/logout, dispatch CLEAR_USER */ }}
        className="text-sm text-zinc-600 hover:text-zinc-900"
      >
        Ելք
      </button>
    </>
  ) : (
    <NavLink to="/login" className={navLinkClass}>
      Մուտք
    </NavLink>
  )}
</div>
```

---

### `frontend/src/contexts/AuthContext.tsx` (provider, event-driven — new)

**No direct analog** — no context/provider exists in the codebase. Use RESEARCH.md Pattern 6.

**API client pattern to copy** (`frontend/src/api/client.ts` lines 1-13):
```typescript
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

const apiClient = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(API_BASE + path)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json() as Promise<T>
  },
}
```

**CRITICAL addition for auth:** All auth fetch calls must include `credentials: "include"` so the browser sends httpOnly cookies (Pitfall 6). The existing `apiClient.get` does NOT include this. The `AuthContext` must either use a new `authClient` wrapper or extend `apiClient`.

**Target file structure:**
```typescript
import { createContext, useContext, useReducer, useEffect, type Dispatch, type ReactNode } from "react"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

type UserRead = { id: string; email: string; display_name: string; is_active: boolean; is_verified: boolean; role: string }
type AuthState = { user: UserRead | null; isLoading: boolean }
type AuthAction =
  | { type: "SET_USER"; payload: UserRead }
  | { type: "CLEAR_USER" }
  | { type: "SET_LOADING"; payload: boolean }

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "SET_USER": return { ...state, user: action.payload, isLoading: false }
    case "CLEAR_USER": return { ...state, user: null, isLoading: false }
    case "SET_LOADING": return { ...state, isLoading: action.payload }
    default: return state
  }
}

export const AuthContext = createContext<{ state: AuthState; dispatch: Dispatch<AuthAction> } | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, { user: null, isLoading: true })

  useEffect(() => {
    // Rehydrate on mount — browser automatically sends httpOnly cookie
    fetch(`${API_BASE}/api/users/me`, { credentials: "include" })
      .then((r) => r.ok ? r.json() : Promise.reject(r.status))
      .then((user) => dispatch({ type: "SET_USER", payload: user }))
      .catch(() => dispatch({ type: "CLEAR_USER" }))
  }, [])

  return <AuthContext.Provider value={{ state, dispatch }}>{children}</AuthContext.Provider>
}
```

---

### `frontend/src/hooks/useAuth.ts` (hook, request-response — new)

**Analog:** `frontend/src/hooks/usePolitician.ts`

**Hook pattern** (`frontend/src/hooks/usePolitician.ts` lines 1-13):
```typescript
import { useQuery } from "@tanstack/react-query"
import { apiClient } from "@/api/client"
import type { PoliticianOut } from "@/types"

export function usePolitician(slug: string) {
  const { data, isLoading, isError } = useQuery<PoliticianOut>({
    queryKey: ["politician", slug],
    queryFn: () => apiClient.get<PoliticianOut>(`/api/politicians/${slug}`),
    enabled: Boolean(slug),
  })

  return { data, isLoading, isError }
}
```

**Target — convenience wrapper over AuthContext:**
```typescript
import { useContext } from "react"
import { AuthContext } from "@/contexts/AuthContext"

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
```

---

### `frontend/src/pages/LoginPage.tsx` (component, request-response — new)

**Analog:** `frontend/src/pages/PromisesListPage.tsx` — form with state, controlled inputs, error handling

**Input usage pattern** (`frontend/src/pages/PromisesListPage.tsx` lines 1-13 + Input usage):
```tsx
import { Input } from "@/components/ui/input"
// ...
<Input
  type="date"
  className="w-36"
  value={made_date_from ?? ""}
  onChange={(e) => handleDateChange("made_date_from", e.target.value)}
/>
```

**Error state pattern** (`frontend/src/pages/PromisesListPage.tsx` lines 215-221):
```tsx
{isError && (
  <div className="flex flex-col items-center gap-4 py-16 text-center">
    <AlertCircle className="w-8 h-8 text-red-500" />
    <p className="text-zinc-700">Տվյալները բեռնելու ժամանակ սխալ է տեղի ունեցել</p>
  </div>
)}
```

**Target structure:**
```tsx
import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/useAuth"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export default function LoginPage() {
  const { dispatch } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    // FastAPI-Users login uses application/x-www-form-urlencoded
    const formData = new URLSearchParams({ username: email, password })
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      credentials: "include",  // CRITICAL — receive httpOnly cookie
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString(),
    })
    if (res.ok) {
      // Fetch user profile after login
      const me = await fetch(`${API_BASE}/api/users/me`, { credentials: "include" }).then(r => r.json())
      dispatch({ type: "SET_USER", payload: me })
      navigate("/")
    } else {
      setError("Սխալ էլ. հասցե կամ գաղտնաբառ")
    }
    setIsLoading(false)
  }

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <Card>
        <CardHeader><CardTitle>Մուտք</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input type="email" placeholder="Էլ. հասցե" value={email} onChange={e => setEmail(e.target.value)} required />
            <Input type="password" placeholder="Գաղտնաբառ" value={password} onChange={e => setPassword(e.target.value)} required />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "..." : "Մուտք"}
            </Button>
          </form>
          <p className="text-sm text-zinc-500 mt-4 text-center">
            Հաշիվ չունե՞ք <Link to="/register" className="text-blue-600 underline">Գրանցվել</Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
```

---

### `frontend/src/pages/RegisterPage.tsx` (component, request-response — new)

**Analog:** Same as LoginPage — `frontend/src/pages/PromisesListPage.tsx` (form pattern) + Card/Input/Button components.

**Target structure:** Same shell as LoginPage but with fields: `display_name`, `email`, `password`, `confirm_password`. On success redirect to `/login` with a success message. POST to `/api/auth/register` with JSON body `{ email, password, display_name }`.

---

### `frontend/src/pages/VerifyEmailPage.tsx` (component, request-response — new)

**Analog:** `frontend/src/pages/AboutPage.tsx` — static-ish page, simple layout

**Static page pattern** (`frontend/src/pages/AboutPage.tsx` lines 1-10):
```tsx
import { Separator } from "@/components/ui/separator"

export default function AboutPage() {
  return (
    <main className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-semibold text-zinc-900 mb-6">Մեր մասին</h1>
      ...
    </main>
  )
}
```

**Target structure:** On mount, read `?token=` from query string. POST to `/api/auth/verify` with the token. Show loading, then success or error message. Uses `useEffect` + `useState` (no TanStack Query needed for one-shot POST).

---

### `frontend/src/pages/ResetPasswordPage.tsx` (component, request-response — new)

**Analog:** `frontend/src/pages/PromisesListPage.tsx` — form pattern

**Target structure:** Two-step page. Step 1: If no `?token=` in URL, show email input + POST to `/api/auth/forgot-password`. Step 2: If `?token=` present, show new password input + POST to `/api/auth/reset-password`. Uses `useState` for step tracking.

---

### `frontend/src/components/RequireAuth.tsx` (middleware, request-response — new)

**No analog** — no protected route wrappers exist. Use RESEARCH.md Pattern 7 verbatim.

**Target:**
```tsx
import { Navigate, Outlet, useLocation } from "react-router-dom"
import { useAuth } from "@/hooks/useAuth"

export default function RequireAuth() {
  const { state } = useAuth()
  const location = useLocation()

  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="h-8 w-8 bg-zinc-200 rounded-full animate-pulse" />
      </div>
    )
  }

  if (!state.user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
```

---

## Shared Patterns

### Tailwind + shadcn/ui Design Language
**Source:** All existing page components
**Apply to:** LoginPage, RegisterPage, VerifyEmailPage, ResetPasswordPage

- Page wrapper: `<main className="max-w-Xxl mx-auto px-4 py-8">`
- Headings: `className="text-2xl font-semibold text-zinc-900 mb-6"`
- Body text: `className="text-sm text-zinc-700"`
- Muted text: `className="text-sm text-zinc-500"`
- Error state: `<AlertCircle className="w-8 h-8 text-red-500" />`
- Loading skeleton: `className="h-X bg-zinc-200 rounded animate-pulse"`
- Form wrapper: `Card > CardHeader + CardContent`
- Auth forms are centered at `max-w-md mx-auto`

### Armenian UI Text Convention
**Source:** `frontend/src/components/Layout.tsx`, all page files
**Apply to:** All new frontend files

- All user-facing text in Armenian (հայերեն)
- Button labels: "Մուտք" (Login), "Ելք" (Logout), "Գրանցվել" (Register), "Ուղարկել" (Send)
- Error messages in Armenian
- Page titles: `<h1 className="text-2xl font-semibold text-zinc-900">`

### AsyncSession Dependency Pattern
**Source:** `backend/app/database.py` lines 25-33
**Apply to:** `backend/app/auth/users.py`

All database access uses `async with AsyncSessionLocal() as session: yield session` pattern. Do NOT create a new engine — reuse `AsyncSessionLocal` from `app.database`.

### Router Registration Pattern
**Source:** `backend/app/main.py` lines 33-39
**Apply to:** All new backend routers

```python
app.include_router(X.router, prefix="/api")
# OR for FastAPI-Users routers:
app.include_router(fastapi_users.get_X_router(...), prefix="/api/auth", tags=["auth"])
```

### fetch with credentials
**Source:** Pattern established in RESEARCH.md (Pitfall 6)
**Apply to:** ALL auth-related fetch calls in frontend (LoginPage, RegisterPage, VerifyEmailPage, ResetPasswordPage, AuthContext)

```typescript
await fetch(url, {
  method: "POST",
  credentials: "include",   // REQUIRED for httpOnly cookie delivery
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
})
```

### Pydantic Schema with from_attributes
**Source:** `backend/app/schemas/politicians.py`
**Apply to:** `backend/app/auth/schemas.py`

FastAPI-Users base schemas already include `model_config = ConfigDict(from_attributes=True)`. Do NOT add it manually to extension classes.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `backend/app/auth/email.py` | service | event-driven | No email-sending code exists; no async task/hook pattern to copy |
| `frontend/src/contexts/AuthContext.tsx` | provider | event-driven | No React Context providers exist; first context in codebase |
| `frontend/src/components/RequireAuth.tsx` | middleware | request-response | No protected route wrappers exist; first auth guard in codebase |

For these three files, RESEARCH.md Patterns 5, 6, and 7 (respectively) serve as the canonical reference.

---

## Metadata

**Analog search scope:** `backend/app/`, `frontend/src/`, `backend/alembic/versions/`
**Files scanned:** 28
**Pattern extraction date:** 2026-05-23
