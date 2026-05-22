from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response envelope for all list endpoints."""

    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int
