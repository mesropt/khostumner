import enum
import uuid
from datetime import datetime, timezone

from fastapi_users.db import SQLAlchemyBaseOAuthAccountTableUUID, SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.models.base import Base


class UserRole(str, enum.Enum):
    registered = "registered"
    moderator = "moderator"
    admin = "admin"


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    __tablename__ = "oauth_accounts"
    # Override access_token to String(4096) -- Google RS256 tokens exceed 1024 chars (Pitfall 3)
    access_token: Mapped[str] = mapped_column(String(4096), nullable=False)

    # Override user_id FK -- base class uses "user.id" but our table is "users"
    @declared_attr
    def user_id(cls) -> Mapped[uuid.UUID]:
        from fastapi_users_db_sqlalchemy.generics import GUID
        return mapped_column(
            GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    # Fields provided by SQLAlchemyBaseUserTableUUID (DO NOT redeclare):
    #   id, email, hashed_password, is_active, is_superuser, is_verified

    # Custom extensions (keep from existing model):
    display_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), default=UserRole.registered
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    account_age_days: Mapped[int] = mapped_column(Integer, default=0)  # cached; computed on login
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship("OAuthAccount", lazy="joined")
