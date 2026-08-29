"""
schemas/report.py
=================
Pydantic v2 schemas for Statutory Inspection Report & Public QR Verification API
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    report_id: str
    docket_number: str
    inspection_id: str
    inspection_number: str
    status: str
    chain_of_custody_hash: str
    qr_verification_token: str
    pdf_download_url: str
    generated_at: str

    model_config = {"from_attributes": True}


class QRVerificationViolationSchema(BaseModel):
    section: str
    title: str
    severity: str

    model_config = {"from_attributes": True}


class QRVerificationResponse(BaseModel):
    verified: bool
    tamper_evident_status: str
    docket_number: str
    inspection_number: str
    chain_of_custody_hash: str
    qr_token: str
    compliance_status: str
    jurisdiction: str
    store_name: Optional[str] = None
    inspection_date: str
    product_name: Optional[str] = None
    manufacturer_name: Optional[str] = None
    total_violations: int = 0
    violations: List[QRVerificationViolationSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}
