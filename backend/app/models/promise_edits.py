import uuid
from datetime import date, datetime

from sqlalchemy import (
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

# Import ModerationStatus from promises.py — do NOT redefine it (same pattern as evidence.py)
from app.models.promises import ModerationStatus


class PromiseEdit(Base):
    """Full snapshot of all editable promise fields, stored as a pending edit row.

    Append-only — rows are never deleted (D-06).
    Admin approval in Phase 6 marks the edit `approved` and applies the snapshot
    to the live promise row.
    """

    __tablename__ = "promise_edits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        SAEnum(ModerationStatus, name="moderation_status"),
        default=ModerationStatus.pending,
        nullable=False,
    )
    title_hy: Mapped[str] = mapped_column(String(500), nullable=False)
    quote_hy: Mapped[str] = mapped_column(Text, nullable=False)
    description_hy: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    made_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


class PromiseEditElectionLink(Base):
    """Many-to-many: a promise edit can be linked to multiple elections.

    Mirrors the PromiseElectionLink pattern in promises.py.
    """

    __tablename__ = "promise_edit_election_links"
    __table_args__ = (
        UniqueConstraint(
            "edit_id",
            "election_id",
            name="uq__promise_edit_election_links__edit_id__election_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    edit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promise_edits.id", ondelete="CASCADE"), nullable=False
    )
    election_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("elections.id", ondelete="CASCADE"), nullable=False
    )
