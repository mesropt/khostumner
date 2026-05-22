import uuid

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
