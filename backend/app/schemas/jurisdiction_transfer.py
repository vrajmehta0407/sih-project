"""
schemas/jurisdiction_transfer.py
================================
Stage 21 — Cross-State Jurisdictional Transfer & Multi-Officer Co-Signing Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class JurisdictionTransferRequest(BaseModel):
    """Payload to initiate a formal statutory Inter-State Enforcement Transfer."""
    target_state: str = Field(..., example="Gujarat", description="State of the manufacturer's packaging plant")
    target_district: str = Field(..., example="Anand", description="District of origin packaging unit")
    transfer_reason: str = Field(
        ...,
        example="Packaging origin violation under Section 49. Seized retail item in Mumbai manufactured in Anand plant.",
        description="Statutory justification under Section 49"
    )
    transfer_urgency: str = Field("HIGH", example="HIGH")  # "CRITICAL", "HIGH", "ROUTINE"


class JurisdictionTransferResponse(BaseModel):
    """Response returned upon formal statutory case transfer."""
    transfer_id: uuid.UUID
    transfer_memo_number: str
    inspection_id: uuid.UUID
    origin_state: str
    target_state: str
    target_district: str
    transfer_status: str  # "TRANSFERRED", "ACCEPTED", "IN_INVESTIGATION"
    transferred_at: datetime
    transferred_by_officer: str
    chain_of_custody_hash: str
    official_statutory_note: str


class OfficerCoSignRequest(BaseModel):
    """Payload for a secondary investigating officer to co-sign an inspection docket."""
    co_investigator_name: str = Field(..., example="Inspector Vikram Rathore")
    co_investigator_badge_number: str = Field(..., example="MH-LM-INSP-4042")
    co_investigator_remarks: str = Field(..., example="Corroborated physical label measurements and dual MRP sticker presence on spot.")


class OfficerCoSignResponse(BaseModel):
    """Response returned upon co-signature registration."""
    co_sign_id: uuid.UUID
    inspection_id: uuid.UUID
    co_investigator_name: str
    co_investigator_badge_number: str
    co_signed_at: datetime
    co_signature_seal: str
    total_co_signers: int
