import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ElectionLevel(str, enum.Enum):
    national = "national"
    local = "local"
    referendum = "referendum"


class Election(Base):
    __tablename__ = "elections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name_hy: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    election_date: Mapped[date] = mapped_column(Date, nullable=False)
    level: Mapped[ElectionLevel] = mapped_column(
        SAEnum(ElectionLevel, name="election_level"), default=ElectionLevel.national
    )
    description_hy: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
