"""
schemas/challan.py
==================
Stage 23 — Section 48 Statutory e-Challan & Instant Compounding Settlement Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ChallanGenerateRequest(BaseModel):
    """Request payload to generate a Section 48 e-Challan for compounding."""
    compounding_fee: float = Field(..., gt=0, example=25000.0, description="Compounding amount in INR under Section 48")
    offence_description: str = Field(..., example="Non-declaration of Unit Sale Price and MRP overcharging under Rule 6(1)")
    violator_entity_name: str = Field(..., example="ABC Retail Mart Pvt Ltd")
    violator_gstin: Optional[str] = Field(None, example="27AAACA1234A1Z5")
    due_days: int = Field(30, ge=7, le=90, description="Days permitted to settle before court filing")


class ChallanSettlementRequest(BaseModel):
    """Payment settlement payload for e-Challan."""
    payment_mode: str = Field("UPI", example="UPI")  # "UPI", "NETBANKING", "RTGS_NEFT", "TREASURY_CHALLAN"
    transaction_reference: str = Field(..., example="UPI-IND-2026-9876543210")
    payer_name: str = Field(..., example="ABC Retail Mart Pvt Ltd")
    payer_bank: Optional[str] = Field("State Bank of India", example="State Bank of India")


class ChallanResponse(BaseModel):
    """Full statutory e-Challan details."""
    challan_id: uuid.UUID
    challan_number: str
    inspection_id: uuid.UUID
    violator_entity_name: str
    violator_gstin: Optional[str]
    state: str
    district: str
    offence_description: str
    compounding_amount: float
    status: str  # "ISSUED", "SETTLED", "OVERDUE", "COURT_ESCALATED"
    payment_upi_intent: str
    statutory_deadline: datetime
    issued_at: datetime
    settled_at: Optional[datetime] = None
    transaction_reference: Optional[str] = None
    discharge_certificate_seal: Optional[str] = None
    official_legal_notice: str
