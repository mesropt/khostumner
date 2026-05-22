from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parties import Party
from app.schemas.parties import PartyListItemOut

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


@router.get("/{slug}", response_model=PartyListItemOut)
async def get_party(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> PartyListItemOut:
    """Return a single party by slug; 404 if not found. Full PartyOut added in plan 03."""
    stmt = select(Party).where(Party.slug == slug)
    result = await db.execute(stmt)
    party = result.scalar_one_or_none()

    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")

    return party
