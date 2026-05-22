import uuid
from datetime import date

from pydantic import BaseModel

from app.models.elections import ElectionLevel


class ElectionOut(BaseModel):
    """Election detail schema — returned for single election lookups."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name_hy: str
    slug: str
    election_date: date
    level: ElectionLevel
    description_hy: str | None


class ElectionWithCountOut(BaseModel):
    """Election list schema — includes promise_count from correlated subquery.

    NOTE: NOT a subclass of ElectionOut. The list query returns Row(Election, int)
    tuples, not ORM objects, so from_attributes does not apply here.
    Instances are constructed explicitly in the router from (Election, int) rows.
    """

    id: uuid.UUID
    name_hy: str
    slug: str
    election_date: date
    level: ElectionLevel
    description_hy: str | None
    promise_count: int
