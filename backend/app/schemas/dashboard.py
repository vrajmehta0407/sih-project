"""
schemas/dashboard.py
====================
Pydantic v2 schemas for Executive Analytics & Officer Dashboard
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ComplianceBreakdownSchema(BaseModel):
    compliant: int = 0
    non_compliant: int = 0
    review_required: int = 0
    pending: int = 0


class StatusBreakdownSchema(BaseModel):
    completed: int = 0
    validated: int = 0
    in_progress: int = 0


class ViolationsSummarySchema(BaseModel):
    total_violations: int = 0
    critical: int = 0
    major: int = 0
    minor: int = 0
    repeat_offender_alerts: int = 0


class ExecutiveMetricsResponse(BaseModel):
    total_inspections: int
    compliance_rate_percentage: float
    compliance_breakdown: ComplianceBreakdownSchema
    status_breakdown: StatusBreakdownSchema
    violations_summary: ViolationsSummarySchema

    model_config = {"from_attributes": True}


class TrendItemSchema(BaseModel):
    date: str
    total_inspections: int
    compliant_count: int
    non_compliant_count: int
    compliance_rate: float


class TopViolationItemSchema(BaseModel):
    rule_code: str
    section_violated: str
    violation_title: str
    severity: str
    violation_count: int
    percentage_of_total: float


class JurisdictionHeatmapItemSchema(BaseModel):
    district: str
    state: str
    total_inspections: int
    compliant_count: int
    non_compliant_count: int
    compliance_rate: float
    centroid_latitude: Optional[float] = None
    centroid_longitude: Optional[float] = None


class RepeatOffenderLeaderboardItemSchema(BaseModel):
    manufacturer_name: str
    brand_name: str
    total_violations: int
    inspections_count: int
    last_inspection_date: str
