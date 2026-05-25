import uuid
from datetime import datetime, timezone

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.auth.backends import auth_backend_access, auth_backend_refresh
from app.auth.email import send_password_reset_email, send_verification_email
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.users import OAuthAccount, User


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.RESET_PASSWORD_SECRET
    verification_token_secret = settings.VERIFICATION_SECRET

    async def on_after_register(self, user: User, request=None):
        # If display_name is empty (e.g., after OAuth registration), default to email local part.
        # Use the injected user_db — do NOT open a second independent session, which would
        # UPDATE on a separate transaction and risk finding no row if the INSERT is not yet
        # visible (CR-07).
        if not user.display_name:
            await self.user_db.update(user, {"display_name": user.email.split("@")[0]})
        # Send verification email automatically on registration (OAuth users are pre-verified).
        if not user.is_verified:
            await self.request_verify(user, request)

    async def on_after_login(self, user: User, request=None, response=None):
        # Recompute and persist account_age_days on every login so Phase 7 vote
        # eligibility checks read a fresh value rather than always seeing 0 (WR-06).
        age = (datetime.now(timezone.utc) - user.created_at).days
        await self.user_db.update(user, {"account_age_days": age})

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        await send_password_reset_email(user.email, token)

    async def on_after_request_verify(self, user: User, token: str, request=None):
        await send_verification_email(user.email, token)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend_access, auth_backend_refresh],
)
