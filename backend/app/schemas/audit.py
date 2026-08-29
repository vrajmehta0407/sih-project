from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    action: str
    entity_name: str
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = {}


class AuditLogCreate(AuditLogBase):
    user_id: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
