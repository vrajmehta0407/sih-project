"""
challan_service.py
==================
Stage 23 — Section 48 Statutory e-Challan & Compounding Settlement Service
"""

import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.schemas.challan import (
    ChallanGenerateRequest,
    ChallanSettlementRequest,
    ChallanResponse,
)

logger = logging.getLogger(__name__)


class ChallanService:
    """Generates Section 48 compounding e-challans and processes digital treasury settlements."""

    def generate_challan(
        self,
        db: Session,
        inspection: Inspection,
        req: ChallanGenerateRequest,
    ) -> ChallanResponse:
        """Issue an official Section 48 e-challan with Bharat QR UPI intent payload."""
        challan_id = uuid.uuid4()
        state_code = (inspection.state[:2] if inspection.state else "IN").upper()
        challan_number = f"CHALLAN-{state_code}-2026-{challan_id.hex[:6].upper()}"
        now = datetime.utcnow()
        deadline = now + timedelta(days=req.due_days)

        # Bharat QR / UPI payment intent URL
        encoded_note = f"LM+Section+48+Compounding+{challan_number}"
        upi_intent = (
            f"upi://pay?pa=legalmetrology.treasury@gov.in"
            f"&pn=Legal+Metrology+Department+{inspection.state}"
            f"&am={req.compounding_fee:.2f}"
            f"&cu=INR"
            f"&tn={encoded_note}"
        )

        statutory_notice = (
            f"Official Statutory Compounding Notice issued under Section 48 of the Legal Metrology Act, 2009. "
            f"Payable within {req.due_days} days to the Controller of Legal Metrology, {inspection.state}."
        )

        # Update inspection record
        inspection.compounding_order_number = challan_number
        inspection.compounding_amount = req.compounding_fee
        inspection.adjudication_status = "notice_issued"
        note_entry = (
            f"\n[e-Challan Generated: {challan_number} ({now.strftime('%d/%m/%Y %H:%M')})]\n"
            f"Violator: {req.violator_entity_name} (GSTIN: {req.violator_gstin or 'N/A'})\n"
            f"Compounding Sum: ₹{req.compounding_fee:,.2f} | Deadline: {deadline.strftime('%d/%m/%Y')}\n"
            f"Offence: {req.offence_description}"
        )
        inspection.inspector_notes = (inspection.inspector_notes or "") + note_entry
        db.commit()
        db.refresh(inspection)

        logger.info("e-Challan %s generated for Inspection %s (Amount: ₹%s)", challan_number, inspection.id, req.compounding_fee)

        return ChallanResponse(
            challan_id=challan_id,
            challan_number=challan_number,
            inspection_id=inspection.id,
            violator_entity_name=req.violator_entity_name,
            violator_gstin=req.violator_gstin,
            state=inspection.state or "National Jurisdiction",
            district=inspection.district or "District HQ",
            offence_description=req.offence_description,
            compounding_amount=req.compounding_fee,
            status="ISSUED",
            payment_upi_intent=upi_intent,
            statutory_deadline=deadline,
            issued_at=now,
            settled_at=None,
            transaction_reference=None,
            discharge_certificate_seal=None,
            official_legal_notice=statutory_notice,
        )

    def settle_challan(
        self,
        db: Session,
        inspection: Inspection,
        req: ChallanSettlementRequest,
    ) -> ChallanResponse:
        """Process online treasury payment and issue Section 48 Statutory Discharge Certificate."""
        now = datetime.utcnow()
        challan_number = inspection.compounding_order_number or f"CHALLAN-IN-2026-{uuid.uuid4().hex[:6].upper()}"
        amount = inspection.compounding_amount or 25000.0

        # Cryptographic Certificate of Discharge Seal
        seal_payload = (
            f"DISCHARGE:SEC48|CHALLAN:{challan_number}|INSP:{inspection.id}|"
            f"TXN:{req.transaction_reference}|PAYER:{req.payer_name}|"
            f"AMOUNT:{amount}|TIME:{now.isoformat()}"
        )
        discharge_seal = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()

        # Update inspection state
        inspection.adjudication_status = "compounded"
        inspection.compounding_receipt_number = req.transaction_reference
        inspection.adjudicated_at = now
        discharge_note = (
            f"\n[Section 48 Compounding Discharge ({now.strftime('%d/%m/%Y %H:%M')})]\n"
            f"Status: FULLY SETTLED via {req.payment_mode}\n"
            f"Transaction Ref (UTR): {req.transaction_reference}\n"
            f"Payer: {req.payer_name} ({req.payer_bank or 'Online Gateway'})\n"
            f"Discharge Certificate Seal: {discharge_seal}"
        )
        inspection.inspector_notes = (inspection.inspector_notes or "") + discharge_note
        db.commit()
        db.refresh(inspection)

        statutory_notice = (
            f"Section 48 Compounding Discharge Complete. The offence stands fully compounded. "
            f"No further criminal proceedings shall be instituted in court for this specific infraction."
        )

        logger.info("Challan %s settled via %s (Ref: %s)", challan_number, req.payment_mode, req.transaction_reference)

        return ChallanResponse(
            challan_id=uuid.uuid4(),
            challan_number=challan_number,
            inspection_id=inspection.id,
            violator_entity_name=req.payer_name,
            violator_gstin=None,
            state=inspection.state or "National Jurisdiction",
            district=inspection.district or "District HQ",
            offence_description="Section 48 Compounded Statutory Offence",
            compounding_amount=amount,
            status="SETTLED",
            payment_upi_intent="",
            statutory_deadline=now,
            issued_at=inspection.created_at or now,
            settled_at=now,
            transaction_reference=req.transaction_reference,
            discharge_certificate_seal=discharge_seal,
            official_legal_notice=statutory_notice,
        )


challan_service = ChallanService()
