"""
Pydantic schemas for Audit Log models in QuantumVault.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    """Schema for returning audit log events."""
    id: str
    user_id: Optional[str] = None
    file_id: Optional[str] = None
    event_type: str
    event_category: str
    status: str
    message: str
    metadata_json: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list."""
    total: int
    items: list[AuditLogResponse]
