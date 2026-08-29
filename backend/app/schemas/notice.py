"""
schemas/notice.py
=================
Stage 14 — Statutory Show-Cause Notice Dispatcher Schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
import uuid


class NoticeDispatchRequest(BaseModel):
    """Payload to dispatch a formal statutory show-cause notice."""
    recipient_name: Optional[str] = Field(None, description="Name of manufacturer / entity representative")
    recipient_email: Optional[str] = Field(None, description="Direct email for digital notice delivery")
    recipient_phone: Optional[str] = Field(None, description="Mobile / SMS contact for statutory alert")
    compliance_deadline_days: int = Field(7, ge=1, le=30, description="Statutory rectification window in days (default 7)")
    officer_remarks: Optional[str] = Field(None, description="Additional enforcement directives or remarks")
    cc_legal_cell: bool = Field(True, description="Whether to copy the Legal Metrology HQ Cell")


class NoticeDispatchResponse(BaseModel):
    """Response confirming statutory notice dispatch."""
    notice_id: uuid.UUID
    inspection_id: uuid.UUID
    inspection_number: str
    recipient_email: Optional[str]
    recipient_phone: Optional[str]
    dispatched_at: datetime
    compliance_deadline: date
    tracking_token: str
    delivery_status: str  # "DISPATCHED", "PENDING", "FAILED"
    notice_summary: str
    attached_pdf_report_path: Optional[str]
    evidentiary_hash_sha256: Optional[str]
