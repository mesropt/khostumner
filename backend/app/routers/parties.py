from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parties import Party
from app.models.politicians import Politician
from app.models.promises import ModerationStatus, Promise
from app.schemas.common import PaginatedResponse
from app.schemas.parties import PartyListItemOut, PartyOut
from app.schemas.politicians import PoliticianOut
from app.schemas.promises import PromiseStubOut

router = APIRouter(prefix="/parties", tags=["parties"])


@router.get("", response_model=list[PartyListItemOut])
async def list_parties(
    db: AsyncSession = Depends(get_db),
) -> list[PartyListItemOut]:
    """Return all active parties — non-paginated list for filter dropdown."""
    stmt = select(Party).where(Party.is_active == True).order_by(Party.name_hy)  # noqa: E712
    result = await db.execute(stmt)
    parties = result.scalars().all()
    return list(parties)


@router.get("/{slug}", response_model=PartyOut)
async def get_party(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> PartyOut:
    """Return a single party by slug; 404 if not found."""
    stmt = select(Party).where(Party.slug == slug, Party.is_active == True)  # noqa: E712
    result = await db.execute(stmt)
    party = result.scalar_one_or_none()

    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")

    return party


@router.get("/{slug}/politicians", response_model=list[PoliticianOut])
async def get_party_politicians(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[PoliticianOut]:
    """Return all active politicians who are current members of this party; 404 if party not found.

    Not paginated — party membership count is small (< 100 in v1 seed data); see T-02-11.
    """
    # Find party by slug
    party_stmt = select(Party).where(Party.slug == slug, Party.is_active == True)  # noqa: E712
    party_result = await db.execute(party_stmt)
    party = party_result.scalar_one_or_none()

    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")

    # Fetch active politicians in this party, ordered by name
    pol_stmt = (
        select(Politician)
        .where(Politician.party_id == party.id, Politician.is_active == True)  # noqa: E712
        .order_by(Politician.name_hy)
    )
    pol_result = await db.execute(pol_stmt)
    politicians = pol_result.scalars().all()

    return list(politicians)


@router.get("/{slug}/promises", response_model=PaginatedResponse[PromiseStubOut])
async def get_party_promises(
    slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PromiseStubOut]:
    """Return paginated approved promises for politicians in this party; 404 if party not found.

    Filters moderation_status == ModerationStatus.approved — CRITICAL per T-02-10.
    Uses JOIN approach: Promise JOIN Politician WHERE party_id == party.id.
    """
    # Find party by slug
    party_stmt = select(Party).where(Party.slug == slug, Party.is_active == True)  # noqa: E712
    party_result = await db.execute(party_stmt)
    party = party_result.scalar_one_or_none()

    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")

    # Only approved promises — filter moderation_status=approved per T-02-10
    stmt = (
        select(Promise)
        .join(Politician, Politician.id == Promise.politician_id)
        .where(
            Politician.party_id == party.id,
            Promise.moderation_status == ModerationStatus.approved,  # T-02-10: never skip
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
