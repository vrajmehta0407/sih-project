from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_name: str,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
        audit_entry = AuditLog(
            action=action,
            entity_name=entity_name,
            entity_id=entity_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry


audit_service = AuditService()
