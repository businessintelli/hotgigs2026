from pydantic import BaseModel, Field, field_validator
from typing import Generic, TypeVar, Optional, List
from datetime import datetime

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v > 100:
            return 100
        return v


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items returned")
    items: List[T] = Field(description="List of items")

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.limit - 1) // self.limit

    @property
    def current_page(self) -> int:
        """Calculate current page number (1-indexed)."""
        return (self.skip // self.limit) + 1


class TimestampMixin(BaseModel):
    """Mixin with timestamp fields."""

    created_at: datetime
    updated_at: datetime


class IdMixin(BaseModel):
    """Mixin with ID field."""

    id: int


class BaseResponse(IdMixin, TimestampMixin):
    """Base response model with ID and timestamps."""

    is_active: bool = True


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    checks: Optional[dict] = None
