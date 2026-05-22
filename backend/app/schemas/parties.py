import uuid

from pydantic import BaseModel, ConfigDict


class PartyListItemOut(BaseModel):
    """Minimal party representation for filter dropdowns and list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    short_name_hy: str | None
