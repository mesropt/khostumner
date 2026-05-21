import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# Import ModerationStatus from promises.py — do NOT redefine it (Pitfall 7)
from app.models.promises import ModerationStatus


class EvidenceType(str, enum.Enum):
    supports_kept = "supports_kept"
    supports_broken = "supports_broken"
    neutral = "neutral"


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    promise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("promises.id", ondelete="CASCADE"), nullable=False
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    archived_url: Mapped[str | None] = mapped_column(Text)  # Wayback Machine (D-11)
    quote_excerpt: Mapped[str | None] = mapped_column(Text)  # verbatim text backup (D-11)
    title_hy: Mapped[str | None] = mapped_column(String(300))
    description_hy: Mapped[str | None] = mapped_column(Text)
    evidence_type: Mapped[EvidenceType] = mapped_column(
        SAEnum(EvidenceType, name="evidence_type"), nullable=False
    )
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        SAEnum(ModerationStatus, name="moderation_status"),
        default=ModerationStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
