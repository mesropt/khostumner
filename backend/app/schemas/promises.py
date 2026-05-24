import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.promises import ModerationStatus, ResolvedStatus


class PromiseStubOut(BaseModel):
    """Minimal promise stub for display in politician/party/election pages."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title_hy: str
    quote_hy: str
    resolved_status: ResolvedStatus


class PromiseListOut(BaseModel):
    """Promise list item — constructed from JOIN Row(Promise, politician_name, politician_slug).

    NO from_attributes: row tuples, not ORM objects. Constructed explicitly in the router.
    """

    id: uuid.UUID
    slug: str
    title_hy: str
    quote_hy: str  # first ~120 chars (truncated in router)
    resolved_status: ResolvedStatus
    politician_name_hy: str
    made_date: date | None


class PromiseDetailOut(BaseModel):
    """Promise detail — all fields + politician join data.

    NO from_attributes: constructed explicitly from JOIN row in the router.
    """

    id: uuid.UUID
    slug: str
    title_hy: str
    quote_hy: str  # full text, no truncation
    resolved_status: ResolvedStatus
    made_date: date | None
    expected_date: date | None
    source_url: str
    archived_url: str | None
    politician_name_hy: str
    politician_slug: str


# ──────────────────────────────────────────────────────────────────────────────
# Phase 5 — Promise Submission input/output schemas
# ──────────────────────────────────────────────────────────────────────────────


class PromiseCreateIn(BaseModel):
    """Input schema for POST /api/promises.

    NO from_attributes — this is a request body schema.
    Backend auto-generates the slug from title_hy; user never sets it.
    """

    title_hy: str
    quote_hy: str
    source_url: str
    politician_id: uuid.UUID
    made_date: date | None = None
    expected_date: date | None = None
    description_hy: str | None = None
    election_ids: list[uuid.UUID] = []


class PromiseOut(BaseModel):
    """Response schema for POST /api/promises.

    NO from_attributes — constructed explicitly in the router.
    """

    id: uuid.UUID
    slug: str
    title_hy: str
    moderation_status: ModerationStatus
    created_at: datetime


class PromiseEditIn(BaseModel):
    """Input schema for PUT /api/promises/{slug}.

    Full snapshot of all editable fields (D-05).
    NO from_attributes — this is a request body schema.
    """

    title_hy: str
    quote_hy: str
    source_url: str
    made_date: date | None = None
    expected_date: date | None = None
    description_hy: str | None = None
    election_ids: list[uuid.UUID] = []


class PromiseEditOut(BaseModel):
    """Response schema for PUT /api/promises/{slug}.

    NO from_attributes — constructed explicitly in the router.
    """

    id: uuid.UUID
    promise_id: uuid.UUID
    moderation_status: ModerationStatus
    created_at: datetime
