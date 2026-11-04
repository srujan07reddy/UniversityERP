from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base Pydantic schema with ORM mode enabled."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class APIResponse(BaseModel, Generic[T]):
    """
    Standard top-level envelope for successful single-object API responses.
    Ensures consistent API structure across all university ERP services.
    """
    success: bool = Field(default=True, description="Indicates operation success")
    data: Optional[T] = Field(default=None, description="Payload data")
    message: Optional[str] = Field(default=None, description="Human-readable informational message")
    request_id: Optional[str] = Field(default=None, description="Correlation identifier for distributed tracing")


class PaginationParams(BaseModel):
    """
    Standard query parameters for paginated collection endpoints.
    """
    page: int = Field(default=1, ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: Optional[str] = Field(default=None, description="Attribute name to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort direction: 'asc' or 'desc'")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginationMetadata(BaseModel):
    """
    Standard pagination metadata envelope.
    """
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page limit")
    total_items: int = Field(..., description="Total items matching filter")
    total_pages: int = Field(..., description="Total available pages")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_previous: bool = Field(..., description="Whether a previous page exists")

    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> "PaginationMetadata":
        total_pages = max(1, (total_items + page_size - 1) // page_size) if total_items > 0 else 1
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard top-level envelope for collection/list API responses.
    """
    success: bool = Field(default=True, description="Indicates operation success")
    data: List[T] = Field(default_factory=list, description="List of paginated items")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")
    request_id: Optional[str] = Field(default=None, description="Correlation identifier for distributed tracing")


class MessageResponse(BaseModel):
    """
    Standard response for simple acknowledgement operations (delete, ping, action triggers).
    """
    success: bool = Field(default=True, description="Indicates operation success")
    message: str = Field(..., description="Operation result description")
    request_id: Optional[str] = Field(default=None, description="Correlation identifier for distributed tracing")

