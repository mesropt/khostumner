import uuid

from fastapi_users import schemas

from app.models.users import UserRole


class UserRead(schemas.BaseUser[uuid.UUID]):
    display_name: str
    role: str  # UserRole enum serialized as string


class UserCreate(schemas.BaseUserCreate):
    display_name: str  # required — Pitfall 7: not in BaseUserCreate


class UserUpdate(schemas.BaseUserUpdate):
    display_name: str | None = None
