"""
jurisdiction_transfer_service.py
================================
Stage 21 — Cross-State Jurisdictional Transfer & Multi-Officer Co-Signing Service
"""

import uuid
import hashlib
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.schemas.jurisdiction_transfer import (
    JurisdictionTransferRequest,
    JurisdictionTransferResponse,
    OfficerCoSignRequest,
    OfficerCoSignResponse,
)

logger = logging.getLogger(__name__)


class JurisdictionTransferService:
    """Handles Section 49 Inter-State Case Transfers and Multi-Officer Joint Taskforce Co-Signatures."""

    def transfer_case(
        self,
        db: Session,
        inspection: Inspection,
        req: JurisdictionTransferRequest,
        transferring_officer_email: str,
    ) -> JurisdictionTransferResponse:
        """Formally transfer an inspection docket to origin manufacturing state."""
        transfer_id = uuid.uuid4()
        now = datetime.utcnow()
        memo_num = f"LM-TRF-2026-{transfer_id.hex[:8].upper()}"

        origin_state = inspection.state or "Maharashtra"

        # Update inspection state/district and append audit note
        note_entry = (
            f"\n[Inter-State Transfer Memo: {memo_num} ({now.strftime('%d/%m/%Y %H:%M')})]\n"
            f"Transferred from {origin_state} to {req.target_state} ({req.target_district}) under Section 49 LM Act, 2009.\n"
            f"Reason: {req.transfer_reason}\nTransferred by Officer: {transferring_officer_email}"
        )
        inspection.inspector_notes = (inspection.inspector_notes or "") + note_entry
        inspection.state = req.target_state
        inspection.district = req.target_district
        db.commit()
        db.refresh(inspection)

        # Cryptographic chain-of-custody hash
        payload = f"TRF:{memo_num}|INSP:{inspection.id}|ORIGIN:{origin_state}|TARGET:{req.target_state}|BY:{transferring_officer_email}|TIME:{now.isoformat()}"
        custody_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        statutory_note = (
            f"Official Transfer Memo dispatched under Section 49 (Offences by Companies). "
            f"Custody handed over to Controller of Legal Metrology, {req.target_state}."
        )

        logger.info(
            "Inspection %s transferred from %s to %s by %s (Memo: %s)",
            inspection.id, origin_state, req.target_state, transferring_officer_email, memo_num
        )

        return JurisdictionTransferResponse(
            transfer_id=transfer_id,
            transfer_memo_number=memo_num,
            inspection_id=inspection.id,
            origin_state=origin_state,
            target_state=req.target_state,
            target_district=req.target_district,
            transfer_status="TRANSFERRED",
            transferred_at=now,
            transferred_by_officer=transferring_officer_email,
            chain_of_custody_hash=custody_hash,
            official_statutory_note=statutory_note,
        )

    def co_sign_docket(
        self,
        db: Session,
        inspection: Inspection,
        req: OfficerCoSignRequest,
    ) -> OfficerCoSignResponse:
        """Register a secondary joint-investigating officer's co-signature on an inspection."""
        co_sign_id = uuid.uuid4()
        now = datetime.utcnow()

        seal_payload = (
            f"COSIGN:{co_sign_id}|INSP:{inspection.id}|OFFICER:{req.co_investigator_name}|"
            f"BADGE:{req.co_investigator_badge_number}|TIME:{now.isoformat()}"
        )
        sig_seal = hashlib.sha256(seal_payload.encode("utf-8")).hexdigest()

        cosign_note = (
            f"\n[Joint Officer Co-Signature ({now.strftime('%d/%m/%Y %H:%M')})]\n"
            f"Co-Signed by: {req.co_investigator_name} (Badge #{req.co_investigator_badge_number})\n"
            f"Remarks: {req.co_investigator_remarks}\nDigital Seal: {sig_seal[:16]}..."
        )
        inspection.inspector_notes = (inspection.inspector_notes or "") + cosign_note
        db.commit()
        db.refresh(inspection)

        # Count total co-signers from notes
        total_co_signers = inspection.inspector_notes.count("[Joint Officer Co-Signature")

        logger.info(
            "Inspection %s co-signed by %s (Badge: %s, Seal: %s)",
            inspection.id, req.co_investigator_name, req.co_investigator_badge_number, sig_seal[:12]
        )

        return OfficerCoSignResponse(
            co_sign_id=co_sign_id,
            inspection_id=inspection.id,
            co_investigator_name=req.co_investigator_name,
            co_investigator_badge_number=req.co_investigator_badge_number,
            co_signed_at=now,
            co_signature_seal=sig_seal,
            total_co_signers=total_co_signers,
        )


jurisdiction_transfer_service = JurisdictionTransferService()
