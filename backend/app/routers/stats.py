from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.promises import ModerationStatus, Promise, ResolvedStatus
from app.schemas.stats import StatsByStatus, StatsOut

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsOut:
    """Return aggregate promise counts broken down by resolved_status.

    Only counts approved promises — pending/rejected counts are never exposed (T-03-02).
    """
    # Phase 3: live GROUP BY is acceptable at seed-data volume. Will be migrated to stats_cache aggregate in Phase 8.
    stmt = (
        select(Promise.resolved_status, func.count().label("cnt"))
        .where(Promise.moderation_status == ModerationStatus.approved)
        .group_by(Promise.resolved_status)
    )
    result = await db.execute(stmt)
    rows = result.all()

    by_status_dict = {r.resolved_status: r.cnt for r in rows}
    total = sum(by_status_dict.values())

    return StatsOut(
        total=total,
        by_status=StatsByStatus(
            kept=by_status_dict.get(ResolvedStatus.kept, 0),
            broken=by_status_dict.get(ResolvedStatus.broken, 0),
            in_progress=by_status_dict.get(ResolvedStatus.in_progress, 0),
            stalled=by_status_dict.get(ResolvedStatus.stalled, 0),
            not_rated=by_status_dict.get(ResolvedStatus.not_rated, 0),
        ),
    )
