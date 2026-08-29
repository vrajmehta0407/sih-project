"""
schemas/scorecard.py
====================
Stage 17 — Brand Compliance Scorecard & Trust Seal Certificate Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class BrandScorecardResponse(BaseModel):
    """Real-time Brand Compliance Scorecard and National Trust Tier Index."""
    brand_name: str
    total_inspections: int
    compliant_inspections: int
    violation_inspections: int
    compliance_rate: float  # 0.0 to 100.0%
    trust_tier: str  # "PLATINUM_GREEN", "GOLD_COMPLIANT", "AMBER_WATCHLIST", "RED_RECIDIVIST"
    trust_seal_badge: str  # "🟢 Tier-A Platinum Green Seal", etc.
    active_registered_models: int
    resolved_grievances_count: int
    risk_assessment_summary: str
    last_evaluated_at: datetime


class CertificateGenerateRequest(BaseModel):
    """Payload to generate an official Legal Metrology Model Verification Certificate."""
    brand_name: str = Field(..., example="Amul Dairy")
    manufacturer_name: str = Field(..., example="Gujarat Cooperative Milk Marketing Federation Ltd")
    model_registration_number: Optional[str] = Field(None, example="LM-IND-MOD-2026-8841")
    commodity_category: str = Field(..., example="Dairy & Food Packaging")
    valid_until_years: int = Field(3, ge=1, le=5, description="Validity period in years")


class CertificateGenerateResponse(BaseModel):
    """Response returned upon statutory certificate generation."""
    certificate_id: uuid.UUID
    certificate_number: str
    brand_name: str
    manufacturer_name: str
    commodity_category: str
    qr_verification_token: str
    sha256_seal: str
    issued_at: datetime
    valid_until: datetime
    certificate_status: str  # "ACTIVE", "EXPIRED", "REVOKED"
    verification_url: str
