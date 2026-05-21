import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PoliticianLevel(str, enum.Enum):
    national = "national"
    local = "local"
    party = "party"


class Politician(Base):
    __tablename__ = "politicians"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_hy: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)  # ASCII transliteration
    photo_url: Mapped[str | None] = mapped_column(Text)
    position: Mapped[str | None] = mapped_column(String(200))  # e.g. "Վարչապետ"
    level: Mapped[PoliticianLevel] = mapped_column(
        SAEnum(PoliticianLevel, name="politician_level"), default=PoliticianLevel.national
    )
    # Denormalized FK for current party (authoritative source: politician_party_memberships)
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("parties.id", ondelete="SET NULL"), nullable=True
    )
    bio_hy: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text)  # "[TEST DATA]" for seed rows


class PoliticianPartyMembership(Base):
    __tablename__ = "politician_party_memberships"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    politician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("politicians.id", ondelete="CASCADE"), nullable=False
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("parties.id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # NULL = current member
    notes: Mapped[str | None] = mapped_column(Text)
