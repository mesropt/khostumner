import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import update

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
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(self, user: User, request=None):
        # If display_name is empty (e.g., after OAuth registration), default to email local part
        if not user.display_name:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(display_name=user.email.split("@")[0])
                )
                await session.commit()

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
