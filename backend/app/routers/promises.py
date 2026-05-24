import uuid as _uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.users import fastapi_users
from app.database import get_db
from app.models.elections import Election
from app.models.politicians import Politician
from app.models.promise_edits import PromiseEdit, PromiseEditElectionLink
from app.models.promises import ModerationStatus, Promise, PromiseElectionLink, ResolvedStatus
from app.models.users import User
from app.schemas.common import PaginatedResponse
from app.schemas.promises import (
    PromiseCreateIn,
    PromiseDetailOut,
    PromiseEditIn,
    PromiseEditOut,
    PromiseListOut,
    PromiseOut,
)

router = APIRouter(prefix="/promises", tags=["promises"])

# FastAPI-Users dependency: raises 401 if not authenticated, 403 if not verified
current_verified_user = fastapi_users.current_user(active=True, verified=True)


def _generate_slug(title_hy: str) -> str:
    """Transliterate title_hy to an ASCII slug using python-slugify."""
    slug = slugify(title_hy, allow_unicode=False)
    return slug if slug else "promise"


@router.get("", response_model=PaginatedResponse[PromiseListOut])
async def list_promises(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),  # comma-separated: "broken,stalled" — T-03-04
    politician_id: _uuid.UUID | None = Query(None),  # T-03-05: FastAPI rejects invalid UUIDs with 422
    election_id: _uuid.UUID | None = Query(None),  # T-03-05: FastAPI rejects invalid UUIDs with 422
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


@router.post("", status_code=201, response_model=PromiseOut)
async def create_promise(
    payload: PromiseCreateIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_verified_user),
) -> PromiseOut:
    """Create a new promise.

    Eligibility: authenticated + email verified (fastapi_users enforces) + account_age_days >= 7.
    New promise always starts with moderation_status=pending (T-05-03).
    Slug auto-generated from title_hy via python-slugify (T-05-02).
    Election IDs validated before insert (T-05-04).
    """
    # D-01: Account must be at least 7 days old (manual check — fastapi_users only does active+verified)
    if user.account_age_days < 7:
        raise HTTPException(
            status_code=403,
            detail="Account must be at least 7 days old to submit promises",
        )

    # T-05-04: Validate all election_ids exist in elections table
    if payload.election_ids:
        result = await db.execute(
            select(Election.id).where(Election.id.in_(payload.election_ids))
        )
        found_ids = set(result.scalars().all())
        requested_ids = set(payload.election_ids)
        unknown_ids = requested_ids - found_ids
        if unknown_ids:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid election IDs: {[str(i) for i in unknown_ids]}",
            )

    # Generate slug: transliterate title_hy → ASCII slug; handle collision
    base_slug = _generate_slug(payload.title_hy)
    slug = base_slug

    # Check for slug collision
    collision_check = await db.execute(
        select(Promise.slug).where(Promise.slug == slug).limit(1)
    )
    if collision_check.scalar_one_or_none() is not None:
        slug = f"{base_slug}-{_uuid.uuid4().hex[:6]}"

    # Create the Promise row — moderation_status always forced to pending (T-05-03)
    promise = Promise(
        title_hy=payload.title_hy,
        quote_hy=payload.quote_hy,
        description_hy=payload.description_hy,
        politician_id=payload.politician_id,
        made_date=payload.made_date,
        expected_date=payload.expected_date,
        source_url=payload.source_url,
        slug=slug,
        moderation_status=ModerationStatus.pending,
        created_by=user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(promise)

    # Flush to get promise.id before creating election links
    await db.flush()

    # Create PromiseElectionLink rows for each validated election_id
    for election_id in payload.election_ids:
        link = PromiseElectionLink(
            promise_id=promise.id,
            election_id=election_id,
        )
        db.add(link)

    try:
        await db.commit()
    except IntegrityError:
        # Safety net: slug collision race (extremely rare) — retry with new suffix
        await db.rollback()
        slug = f"{base_slug}-{_uuid.uuid4().hex[:6]}"
        promise.slug = slug
        db.add(promise)
        for election_id in payload.election_ids:
            link = PromiseElectionLink(
                promise_id=promise.id,
                election_id=election_id,
            )
            db.add(link)
        await db.commit()

    await db.refresh(promise)

    return PromiseOut(
        id=promise.id,
        slug=promise.slug,
        title_hy=promise.title_hy,
        moderation_status=promise.moderation_status,
        created_at=promise.created_at,
    )


@router.put("/{slug}", status_code=201, response_model=PromiseEditOut)
async def edit_promise(
    slug: str,
    payload: PromiseEditIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_verified_user),
) -> PromiseEditOut:
    """Submit an edit to an existing promise.

    Append-only: inserts a row into promise_edits; NEVER modifies the live Promise row (D-04, T-05-05).
    Eligibility: same as create (D-07).
    Lookup: finds pending AND approved promises; rejected → 404 (RESEARCH Pitfall 4).
    """
    # D-07: Same eligibility as new submission
    if user.account_age_days < 7:
        raise HTTPException(
            status_code=403,
            detail="Account must be at least 7 days old to submit promise edits",
        )

    # Look up promise by slug — exclude rejected (pending + approved are editable)
    result = await db.execute(
        select(Promise).where(
            Promise.slug == slug,
            Promise.moderation_status != ModerationStatus.rejected,
        )
    )
    promise = result.scalar_one_or_none()
    if promise is None:
        raise HTTPException(status_code=404, detail="Promise not found")

    # T-05-04: Validate all election_ids exist
    if payload.election_ids:
        elec_result = await db.execute(
            select(Election.id).where(Election.id.in_(payload.election_ids))
        )
        found_ids = set(elec_result.scalars().all())
        requested_ids = set(payload.election_ids)
        unknown_ids = requested_ids - found_ids
        if unknown_ids:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid election IDs: {[str(i) for i in unknown_ids]}",
            )

    # Create PromiseEdit row — full snapshot, always pending (append-only, D-06)
    edit = PromiseEdit(
        promise_id=promise.id,
        submitted_by=user.id,
        moderation_status=ModerationStatus.pending,
        title_hy=payload.title_hy,
        quote_hy=payload.quote_hy,
        description_hy=payload.description_hy,
        source_url=payload.source_url,
        made_date=payload.made_date,
        expected_date=payload.expected_date,
        created_at=datetime.now(timezone.utc),
    )
    db.add(edit)

    # Flush to get edit.id before creating election links
    await db.flush()

    # Create PromiseEditElectionLink rows for each election_id
    for election_id in payload.election_ids:
        edit_link = PromiseEditElectionLink(
            edit_id=edit.id,
            election_id=election_id,
        )
        db.add(edit_link)

    await db.commit()
    await db.refresh(edit)

    return PromiseEditOut(
        id=edit.id,
        promise_id=edit.promise_id,
        moderation_status=edit.moderation_status,
        created_at=edit.created_at,
    )
