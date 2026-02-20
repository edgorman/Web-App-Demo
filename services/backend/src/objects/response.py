"""Generic API response model."""
from typing import Generic, TypeVar, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

DataT = TypeVar('DataT')


class APIResponse(BaseModel, Generic[DataT]):
    """Generic API response wrapper.

    This model wraps all API responses with consistent metadata.
    """

    data: DataT = Field(..., description="The response data")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp"
    )
    success: bool = Field(default=True, description="Whether the request was successful")
    message: Optional[str] = Field(default=None, description="Optional message about the response")
