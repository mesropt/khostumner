from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware

from app.auth.oauth import facebook_oauth_client, google_oauth_client
from app.auth.schemas import UserCreate, UserRead, UserUpdate
from app.auth.users import auth_backend_access, auth_backend_refresh, fastapi_users
from app.config import settings
from app.database import engine
from app.routers import auth, elections, health, og, parties, politicians, promises, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connection pool created on first use;
    # migrations run via alembic upgrade head BEFORE uvicorn starts in Docker
    yield
    # Shutdown: dispose connection pool cleanly
    await engine.dispose()


app = FastAPI(
    title="Khostumner API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSRF middleware registered AFTER CORSMiddleware.
# FastAPI processes middleware in reverse registration order (last = outermost).
# Result: CORS outermost, CSRF innermost — per RESEARCH.md Pitfall 4.
app.add_middleware(
    CSRFMiddleware,
    secret=settings.CSRF_SECRET,
    cookie_name="csrftoken",
    header_name="x-csrftoken",
    cookie_samesite="lax",
    safe_methods={"GET", "HEAD", "OPTIONS", "TRACE"},
)

# Auth routers (registered before other routers — alphabetically first)
app.include_router(auth.router, prefix="/api")
app.include_router(
    fastapi_users.get_auth_router(auth_backend_access), prefix="/api/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/api/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/api/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/api/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/api/users", tags=["users"]
)
app.include_router(
    fastapi_users.get_oauth_router(
        google_oauth_client,
        auth_backend_access,
        settings.JWT_SECRET,
        associate_by_email=True,
        is_verified_by_default=True,
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

# Existing routers (unchanged)
app.include_router(health.router)
app.include_router(politicians.router, prefix="/api")
app.include_router(parties.router, prefix="/api")
app.include_router(elections.router, prefix="/api")
app.include_router(promises.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(og.router, prefix="/api")
