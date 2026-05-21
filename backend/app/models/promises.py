import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModerationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ResolvedStatus(str, enum.Enum):
    not_rated = "not_rated"
    kept = "kept"
    broken = "broken"
    in_progress = "in_progress"
    stalled = "stalled"


class Promise(Base):
    __tablename__ = "promises"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title_hy: Mapped[str] = mapped_column(String(500), nullable=False)  # display title
    quote_hy: Mapped[str] = mapped_column(Text, nullable=False)  # VERBATIM quote from source
    description_hy: Mapped[str | None] = mapped_column(Text)  # optional elaboration
    politician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("politicians.id", ondelete="RESTRICT"), nullable=False
    )
    made_date: Mapped[date | None] = mapped_column(Date)
    expected_date: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    archived_url: Mapped[str | None] = mapped_column(Text)  # Wayback Machine URL (D-11)
    quote_excerpt: Mapped[str | None] = mapped_column(Text)  # verbatim text backup (D-11)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)

    # TWO SEPARATE STATUS FIELDS — NEVER MERGE (D-07, CLAUDE.md rule #1)
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        SAEnum(ModerationStatus, name="moderation_status"),
        default=ModerationStatus.pending,
        nullable=False,
    )
    resolved_status: Mapped[ResolvedStatus] = mapped_column(
        SAEnum(ResolvedStatus, name="resolved_status"),
        default=ResolvedStatus.not_rated,
        nullable=False,
    )

    is_seed: Mapped[bool] = mapped_column(Boolean, default=False)  # marks dev seed data
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PromiseElectionLink(Base):
    """Many-to-many: a promise can be linked to multiple elections (reiterated promise)."""

    __tablename__ = "promise_election_links"
    __table_args__ = (
        UniqueConstraint(
            "promise_id", "election_id", name="uq__promise_election_links__promise_id__election_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id", ondelete="CASCADE"), nullable=False
    )
