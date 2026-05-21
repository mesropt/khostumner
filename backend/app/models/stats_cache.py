import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StatsCache(Base):
    # D-10: precomputed per-politician fulfillment stats; never GROUP BY on request
    __tablename__ = "stats_cache"
    __table_args__ = (
        UniqueConstraint("politician_id", name="uq__stats_cache__politician_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    politician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("politicians.id", ondelete="CASCADE"), nullable=False
    )
    total_promises: Mapped[int] = mapped_column(Integer, default=0)
    kept_count: Mapped[int] = mapped_column(Integer, default=0)
    broken_count: Mapped[int] = mapped_column(Integer, default=0)
    in_progress_count: Mapped[int] = mapped_column(Integer, default=0)
    stalled_count: Mapped[int] = mapped_column(Integer, default=0)
    not_rated_count: Mapped[int] = mapped_column(Integer, default=0)
    fulfillment_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AppSettings(Base):
    """Admin-configurable settings. vote_threshold stored here per D-12/VOTE-04."""

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String, primary_key=True)  # e.g. "vote_threshold_minimum"
    value: Mapped[str] = mapped_column(String, nullable=False)  # always string; cast at read time
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
