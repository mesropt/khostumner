import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# VoteStatus defined ONCE here — do not redefine in vote_history
class VoteStatus(str, enum.Enum):
    kept = "kept"
    broken = "broken"
    in_progress = "in_progress"
    stalled = "stalled"
    not_rated = "not_rated"


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("promise_id", "user_id", name="uq__votes__promise_id__user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status_voted: Mapped[VoteStatus] = mapped_column(
        SAEnum(VoteStatus, name="vote_status"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class VoteHistory(Base):
    """Immutable audit log. New row inserted on every vote change. Never updated."""

    __tablename__ = "vote_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status_voted: Mapped[VoteStatus] = mapped_column(
        SAEnum(VoteStatus, name="vote_status"), nullable=False
    )
    voted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    previous_status: Mapped[VoteStatus | None] = mapped_column(
        SAEnum(VoteStatus, name="vote_status"), nullable=True
    )
    changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)  # brigading detection
