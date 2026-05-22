import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.politicians import Politician
from app.models.promises import ModerationStatus, Promise, PromiseElectionLink, ResolvedStatus
from app.schemas.common import PaginatedResponse
from app.schemas.promises import PromiseDetailOut, PromiseListOut

router = APIRouter(prefix="/promises", tags=["promises"])


@router.get("", response_model=PaginatedResponse[PromiseListOut])
async def list_promises(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),  # comma-separated: "broken,stalled" — T-03-04
    politician_id: uuid.UUID | None = Query(None),  # T-03-05: FastAPI rejects invalid UUIDs with 422
    election_id: uuid.UUID | None = Query(None),  # T-03-05: FastAPI rejects invalid UUIDs with 422
    made_date_from: date | None = Query(None),  # T-03-06: Pydantic validates ISO date format
    made_date_to: date | None = Query(None),  # T-03-06: Pydantic validates ISO date format
    expected_date_from: date | None = Query(None),  # T-03-06
    expected_date_to: date | None = Query(None),  # T-03-06
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PromiseListOut]:
    """Return a paginated list of approved promises with optional filters.

    Only moderation_status=approved promises are ever returned (T-03-07).
    D-07b: Promises without expected_date are valid; date filters only exclude them
    when the filter IS applied — they are NOT filtered out when no date param is given.
    """
    # Base query — T-03-07: moderation_status=approved WHERE clause always applied first
    stmt = (
        select(
            Promise,
            Politician.name_hy.label("politician_name"),
            Politician.slug.label("politician_slug"),
        )
        .join(Politician, Politician.id == Promise.politician_id)
        .where(Promise.moderation_status == ModerationStatus.approved)
    )

    # Optional filters — each added ONLY when param is not None
    if status is not None:
        # T-03-04: ResolvedStatus(s.strip()) raises ValueError for invalid values → FastAPI 422
        status_values = [ResolvedStatus(s.strip()) for s in status.split(",")]
        stmt = stmt.where(Promise.resolved_status.in_(status_values))

    if politician_id is not None:
        stmt = stmt.where(Promise.politician_id == politician_id)

    if election_id is not None:
        # Join only when election_id is provided to avoid unnecessary joins
        stmt = stmt.join(
            PromiseElectionLink, PromiseElectionLink.promise_id == Promise.id
        ).where(PromiseElectionLink.election_id == election_id)

    # D-07b: Date filters only added when param is not None — never exclude null-date promises
    if made_date_from is not None:
        stmt = stmt.where(Promise.made_date >= made_date_from)
    if made_date_to is not None:
        stmt = stmt.where(Promise.made_date <= made_date_to)
    if expected_date_from is not None:
        stmt = stmt.where(Promise.expected_date >= expected_date_from)
    if expected_date_to is not None:
        stmt = stmt.where(Promise.expected_date <= expected_date_to)

    # Count total matching rows via subquery (pattern from elections.py)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar_one()

    # Order and paginate
    stmt = stmt.order_by(Promise.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    rows = (await db.execute(stmt)).all()

    # Explicit row unpacking — PromiseListOut has no from_attributes (JOIN row tuples)
    items = [
        PromiseListOut(
            id=promise.id,
            slug=promise.slug,
            title_hy=promise.title_hy,
            quote_hy=promise.quote_hy[:120] + "…" if len(promise.quote_hy) > 120 else promise.quote_hy,
            resolved_status=promise.resolved_status,
            politician_name_hy=politician_name,
            made_date=promise.made_date,
        )
        for promise, politician_name, politician_slug in rows
    ]

    pages = (total + per_page - 1) // per_page if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{slug}", response_model=PromiseDetailOut)
async def get_promise(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> PromiseDetailOut:
    """Return a single approved promise by slug; 404 if not found or not approved."""
    stmt = (
        select(
            Promise,
            Politician.name_hy.label("politician_name"),
            Politician.slug.label("politician_slug"),
        )
        .join(Politician, Politician.id == Promise.politician_id)
        .where(
            Promise.slug == slug,
            Promise.moderation_status == ModerationStatus.approved,
        )
    )
    result = await db.execute(stmt)
    row = result.first()

    if row is None:
        raise HTTPException(status_code=404, detail="Promise not found")

    promise, politician_name, politician_slug = row

    return PromiseDetailOut(
        id=promise.id,
        slug=promise.slug,
        title_hy=promise.title_hy,
        quote_hy=promise.quote_hy,
        resolved_status=promise.resolved_status,
        made_date=promise.made_date,
        expected_date=promise.expected_date,
        source_url=promise.source_url,
        archived_url=promise.archived_url,
        politician_name_hy=politician_name,
        politician_slug=politician_slug,
    )
