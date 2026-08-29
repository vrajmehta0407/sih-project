"""
schemas/deceptive_packaging.py
==============================
Stage 29 — Multi-Platform Dark Pattern & Deceptive Packaging VDI Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class DeceptivePackagingAuditRequest(BaseModel):
    """Request payload to audit packaging for non-functional slack fill & deceptive sizing."""
    product_name: str = Field(..., example="Crunchy Cornflakes 500g Mega Pack")
    brand_name: str = Field(..., example="CrispyBites")
    packaging_type: str = Field("RIGID_BOX", example="RIGID_BOX")  # "RIGID_BOX", "FLEXIBLE_POUCH", "JAR_WITH_FALSE_BOTTOM", "BOTTLE"
    package_length_cm: float = Field(..., gt=0, example=24.0)
    package_width_cm: float = Field(..., gt=0, example=12.0)
    package_height_cm: float = Field(..., gt=0, example=36.0)
    declared_net_quantity_grams: float = Field(..., gt=0, example=500.0)
    product_bulk_density_g_per_cm3: Optional[float] = Field(0.18, example=0.18)  # g/cm3 for cornflakes
    functional_cushion_allowance_pct: Optional[float] = Field(15.0, example=15.0)  # Standard engineering allowance


class DeceptivePackagingAuditResponse(BaseModel):
    """Audit report quantifying Visual Deception Index (VDI) and non-functional slack fill."""
    audit_id: str
    product_name: str
    brand_name: str
    packaging_type: str
    audited_at: datetime
    container_outer_volume_cm3: float
    actual_product_volume_cm3: float
    total_slack_fill_volume_cm3: float
    total_slack_fill_pct: float
    functional_allowance_pct: float
    deceptive_non_functional_slack_fill_pct: float
    visual_deception_index: float  # 0.0 to 10.0 scale
    deception_risk_level: str  # "NEGLIGIBLE", "MODERATE_CAUTION", "HIGH_DECEPTIVE", "CRITICAL_FRAUD"
    is_compliant_with_rule_5: bool
    statutory_verdict: str  # "COMPLIANT_FUNCTIONAL_PACKAGING" or "DECEPTIVE_PACKAGING_VIOLATION"
    statutory_penalty_amount_inr: float
    statutory_citations: List[str]
    officer_action_recommendation: str
    digital_audit_seal: str
