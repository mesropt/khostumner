from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy

from app.config import settings

cookie_transport_access = CookieTransport(
    cookie_name="khostumner_access",
    cookie_max_age=3600,
    cookie_httponly=True,
    cookie_secure=False,  # True in production
    cookie_samesite="lax",
)

cookie_transport_refresh = CookieTransport(
    cookie_name="khostumner_refresh",
    cookie_max_age=2592000,  # 60*60*24*30 = 30 days
    cookie_httponly=True,
    cookie_secure=False,  # True in production
    cookie_samesite="lax",
)


def get_access_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=3600)


def get_refresh_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=2592000)


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
