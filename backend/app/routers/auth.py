from fastapi import APIRouter, Depends, Response

from app.auth.backends import get_access_strategy
from app.auth.users import auth_backend_access, fastapi_users

router = APIRouter(tags=["auth"])


@router.post("/auth/refresh")
async def refresh_access_token(
    response: Response,
    user=Depends(fastapi_users.current_user(active=True)),
):
    return await auth_backend_access.login(get_access_strategy(), user, response)
