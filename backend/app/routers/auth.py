from fastapi import APIRouter, Depends, Response

from app.auth.backends import auth_backend_refresh, get_access_strategy
from app.auth.users import auth_backend_access, fastapi_users

router = APIRouter(tags=["auth"])


@router.post("/auth/refresh")
async def refresh_access_token(
    response: Response,
    # Authenticate via the refresh cookie backend so this endpoint works even when
    # the access token is already expired (CR-01). The refresh cookie is a 30-day
    # httpOnly cookie named `khostumner_refresh`.
    user=Depends(
        fastapi_users.current_user(
            active=True, get_enabled_backends=[auth_backend_refresh]
        )
    ),
):
    strategy = get_access_strategy()
    return await auth_backend_access.login(strategy, user, response)
