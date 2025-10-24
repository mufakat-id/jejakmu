import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.auditlogs.models import AuditAction


class AuditLogBase(BaseModel):
    table_name: str
    record_id: str
    action: AuditAction
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    changed_fields: list[str] | None = None
    user_id: uuid.UUID | None = None
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    session_id: str | None = None
    additional_info: dict[str, Any] | None = None


class AuditLogResponse(AuditLogBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    data: list[AuditLogResponse]
    count: int
    limit: int
    offset: int
