"""
endpoints/audit.py
==================
Stage 7 — Immutable Audit Trail Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import require_inspector
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogResponse],
    summary="List Immutable Audit Logs",
    description="Retrieves filterable, paginated audit logs for legal scrutiny, supervisory monitoring, and court disclosure.",
)
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None, description="Filter by action name (e.g. VALIDATE_COMPLIANCE)"),
    entity_name: Optional[str] = Query(None, description="Filter by entity (e.g. Inspection, Report)"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action.strip()}%"))
    if entity_name:
        query = query.filter(AuditLog.entity_name == entity_name.strip())
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id.strip())
    if user_id:
        query = query.filter(AuditLog.user_id == user_id.strip())

    total = query.count()
    items = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
    pages = (total + limit - 1) // limit if limit > 0 and total > 0 else 1

    return PaginatedResponse(
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
        pages=pages,
        items=items,
    )
