import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.promises import ResolvedStatus


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
