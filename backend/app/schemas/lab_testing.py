"""
schemas/lab_testing.py
======================
Stage 27 — Central Laboratory Sample Verification & Net Quantity Gravimetric Tare Testing Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LabSampleSubmissionRequest(BaseModel):
    """Laboratory sample gravimetric tare test submission."""
    sample_id: Optional[str] = Field(None, example="SMPL-MUM-2026-0042")
    product_name: str = Field(..., example="Fortune Sunlite Refined Sunflower Oil 1L")
    brand_name: str = Field(..., example="Fortune")
    lot_or_batch_number: str = Field(..., example="LOT-2026-F981")
    declared_nominal_quantity: float = Field(..., gt=0, example=1000.0)  # e.g. 1000g or 1000ml
    unit: str = Field("g", example="g")  # "g" or "ml"
    gross_weight_grams: float = Field(..., gt=0, example=1025.4)
    tare_weight_grams: float = Field(..., gt=0, example=45.2)
    testing_lab_name: str = Field("National Metrology Testing Center, Mumbai", example="National Metrology Testing Center, Mumbai")
    technician_name: str = Field("Dr. S. K. Raman", example="Dr. S. K. Raman")
    temperature_celsius: Optional[float] = Field(23.5, example=23.5)
    relative_humidity_pct: Optional[float] = Field(55.0, example=55.0)


class LabTestReportResponse(BaseModel):
    """NABL-Accredited Laboratory Gravimetric Test Certificate."""
    certificate_number: str
    sample_id: str
    product_name: str
    brand_name: str
    lot_or_batch_number: str
    testing_lab_name: str
    technician_name: str
    tested_at: datetime
    declared_nominal_quantity: float
    unit: str
    gross_weight_grams: float
    tare_weight_grams: float
    actual_net_content_grams: float
    deficiency_or_excess_grams: float
    percentage_deviation: float
    max_permissible_error_grams: float
    max_permissible_error_pct: float
    is_compliant_with_mpe: bool
    statutory_verdict: str  # "COMPLIANT_WITHIN_MPE" or "SHORT_DELIVERY_OFFENCE"
    applicable_rule: str
    digital_signature_hash: str
    recommendation_to_officer: str
