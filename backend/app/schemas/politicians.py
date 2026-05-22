import uuid

from pydantic import BaseModel, ConfigDict

from app.models.politicians import PoliticianLevel


class PoliticianOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_hy: str
    slug: str
    photo_url: str | None
    position: str | None
    level: PoliticianLevel
    party_id: uuid.UUID | None
    bio_hy: str | None
    is_active: bool
