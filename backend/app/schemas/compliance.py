"""
schemas/compliance.py
=====================
Pydantic v2 schemas for Statutory Compliance Validation & Violation Dockets API
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ViolationItemSchema(BaseModel):
    id: str
    rule_code: str
    field_affected: str
    section_violated: str
    statute_title: str
    penalty_provision: str
    estimated_fine: Optional[str] = None
    violation_title: str
    violation_description: str
    severity: str
    is_repeat_offender_alert: bool = False

    model_config = {"from_attributes": True}


class ComplianceValidationSummarySchema(BaseModel):
    total_violations: int = 0
    critical_violations: int = 0
    major_violations: int = 0
    minor_violations: int = 0
    is_repeat_offender: bool = False
    prior_offence_count: int = 0
    prior_inspections: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ValidationResponse(BaseModel):
    inspection_id: str
    inspection_number: str
    status: str
    compliance_status: str
    summary: ComplianceValidationSummarySchema
    violations: List[ViolationItemSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}
