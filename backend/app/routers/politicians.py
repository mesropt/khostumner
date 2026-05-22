import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.politicians import Politician, PoliticianLevel
from app.models.promises import ModerationStatus, Promise
from app.schemas.common import PaginatedResponse
from app.schemas.politicians import PoliticianOut
from app.schemas.promises import PromiseStubOut

router = APIRouter(prefix="/politicians", tags=["politicians"])


@router.get("", response_model=PaginatedResponse[PoliticianOut])
async def list_politicians(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    party: uuid.UUID | None = Query(None),
    level: PoliticianLevel | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PoliticianOut]:
    """Return a paginated list of active politicians with optional filters."""
    stmt = select(Politician).where(Politician.is_active == True)  # noqa: E712

    if party is not None:
        stmt = stmt.where(Politician.party_id == party)
    if level is not None:
        stmt = stmt.where(Politician.level == level)

    # Count total matching rows via subquery
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    # Fetch paginated items
    stmt = stmt.order_by(Politician.name_hy).offset((page - 1) * per_page).limit(per_page)
    items_result = await db.execute(stmt)
    items = items_result.scalars().all()

    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return PaginatedResponse(
        items=list(items),
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{slug}", response_model=PoliticianOut)
async def get_politician(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> PoliticianOut:
    """Return a single politician by slug; 404 if not found."""
    stmt = select(Politician).where(Politician.slug == slug)
    result = await db.execute(stmt)
    politician = result.scalar_one_or_none()

    if politician is None:
        raise HTTPException(status_code=404, detail="Politician not found")

    return politician


@router.get("/{slug}/promises", response_model=PaginatedResponse[PromiseStubOut])
async def get_politician_promises(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PromiseStubOut]:
    """Return approved promises for a politician, paginated."""
    # Verify politician exists
    pol_stmt = select(Politician).where(Politician.slug == slug)
    pol_result = await db.execute(pol_stmt)
    politician = pol_result.scalar_one_or_none()

    if politician is None:
        raise HTTPException(status_code=404, detail="Politician not found")

    # Only approved promises — CRITICAL per CLAUDE.md and T-02-06
    stmt = select(Promise).where(
        Promise.politician_id == politician.id,
        Promise.moderation_status == ModerationStatus.approved,
    )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    stmt = stmt.order_by(Promise.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    items_result = await db.execute(stmt)
    items = items_result.scalars().all()

    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return PaginatedResponse(
        items=list(items),
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )
