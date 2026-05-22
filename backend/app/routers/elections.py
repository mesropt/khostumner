from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.elections import Election
from app.models.promises import ModerationStatus, Promise, PromiseElectionLink
from app.schemas.common import PaginatedResponse
from app.schemas.elections import ElectionOut, ElectionWithCountOut
from app.schemas.promises import PromiseStubOut

router = APIRouter(prefix="/elections", tags=["elections"])


@router.get("", response_model=PaginatedResponse[ElectionWithCountOut])
async def list_elections(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ElectionWithCountOut]:
    """Return a paginated list of elections with per-election promise counts."""
    # Correlated subquery: count approved promises linked to each election
    # Pattern 8 from RESEARCH.md — Row tuples (Election, int) must be unpacked
    promise_count_subquery = (
        select(func.count())
        .where(PromiseElectionLink.election_id == Election.id)
        .correlate(Election)
        .scalar_subquery()
        .label("promise_count")
    )

    stmt = select(Election, promise_count_subquery).order_by(Election.election_date.desc())

    # Count total elections
    count_stmt = select(func.count()).select_from(select(Election).subquery())
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    # Fetch paginated items
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    items_result = await db.execute(stmt)
    rows = items_result.all()

    items = [
        ElectionWithCountOut(
            id=election.id,
            name_hy=election.name_hy,
            slug=election.slug,
            election_date=election.election_date,
            level=election.level,
            description_hy=election.description_hy,
            promise_count=count,
        )
        for election, count in rows
    ]

    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{slug}", response_model=ElectionOut)
async def get_election(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ElectionOut:
    """Return a single election by slug; 404 if not found."""
    stmt = select(Election).where(Election.slug == slug)
    result = await db.execute(stmt)
    election = result.scalar_one_or_none()

    if election is None:
        raise HTTPException(status_code=404, detail="Election not found")

    return election  # type: ignore[return-value]


@router.get("/{slug}/promises", response_model=PaginatedResponse[PromiseStubOut])
async def get_election_promises(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PromiseStubOut]:
    """Return approved promises linked to an election, paginated. 404 if election not found."""
    # Verify election exists — T-02-12: parameterized ORM query, no string interpolation
    election_stmt = select(Election).where(Election.slug == slug)
    election_result = await db.execute(election_stmt)
    election = election_result.scalar_one_or_none()

    if election is None:
        raise HTTPException(status_code=404, detail="Election not found")

    # Only approved promises — T-02-13: moderation_status filter prevents non-approved leakage
    stmt = (
        select(Promise)
        .join(PromiseElectionLink, PromiseElectionLink.promise_id == Promise.id)
        .where(
            PromiseElectionLink.election_id == election.id,
            Promise.moderation_status == ModerationStatus.approved,
        )
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
