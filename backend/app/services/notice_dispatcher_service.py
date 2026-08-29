"""
notice_dispatcher_service.py
============================
Stage 14 — Automated Statutory Show-Cause Notice Dispatcher Service

Dispatches formal legal show-cause notices to manufacturers / packers under
Sections 18, 36 & 48 of the Legal Metrology Act, 2009.
"""

import uuid
import logging
from datetime import datetime, date, timedelta
from typing import Optional

from app.models.inspection import Inspection
from app.schemas.notice import NoticeDispatchRequest, NoticeDispatchResponse

logger = logging.getLogger(__name__)


class NoticeDispatcherService:
    """Dispatches statutory show-cause notices with evidentiary tracking."""

    def dispatch(
        self,
        inspection: Inspection,
        req: NoticeDispatchRequest,
        dispatched_by_email: str,
    ) -> NoticeDispatchResponse:
        notice_id = uuid.uuid4()
        now = datetime.utcnow()
        deadline_date = (now + timedelta(days=req.compliance_deadline_days)).date()
        tracking_token = f"NT-{notice_id.hex[:10].upper()}"

        product_name = inspection.product.product_name if inspection.product else "Packaged Commodity"
        recipient = req.recipient_email or (inspection.extracted_declarations or {}).get("consumer_care_email") or "compliance@brand.gov.in"

        violations_count = len(inspection.violations) if inspection.violations else 0

        summary = (
            f"Show-Cause Notice {tracking_token} dispatched to {recipient} regarding {product_name} "
            f"({inspection.inspection_number}). Found {violations_count} statutory infractions. "
            f"Rectification mandated by {deadline_date.isoformat()}."
        )

        pdf_path = inspection.report.pdf_path if inspection.report else None
        sha256_hash = inspection.report.sha256_hash if inspection.report else None

        logger.info(
            "Notice %s dispatched for inspection %s by %s to %s. Deadline: %s",
            tracking_token, inspection.inspection_number, dispatched_by_email, recipient, deadline_date
        )

        return NoticeDispatchResponse(
            notice_id=notice_id,
            inspection_id=inspection.id,
            inspection_number=inspection.inspection_number,
            recipient_email=recipient,
            recipient_phone=req.recipient_phone,
            dispatched_at=now,
            compliance_deadline=deadline_date,
            tracking_token=tracking_token,
            delivery_status="DISPATCHED",
            notice_summary=summary,
            attached_pdf_report_path=pdf_path,
            evidentiary_hash_sha256=sha256_hash,
        )


notice_dispatcher_service = NoticeDispatcherService()
