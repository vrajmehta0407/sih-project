"""
schemas/adjudication.py
=======================
Pydantic v2 schemas for Statutory Case Adjudication & Offence Compounding Workflow (Section 48/49 LM Act 2009)
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field


class AdjudicationRequest(BaseModel):
    action: str = Field(
        ...,
        description="Adjudication action: COMPOUND_OFFENCE | REFER_TO_COURT | ISSUE_SHOW_CAUSE | CLOSE_WITH_WARNING"
    )
    compounding_amount: Optional[float] = Field(
        None,
        description="Agreed compounding fine amount in INR under Section 48"
    )
    receipt_number: Optional[str] = Field(
        None,
        description="Treasury / Challan payment receipt number"
    )
    order_number: Optional[str] = Field(
        None,
        description="Statutory compounding or court referral order docket number"
    )
    court_jurisdiction: Optional[str] = Field(
        None,
        description="Designated Judicial Magistrate First Class (JMFC) Court if referred"
    )
    adjudication_notes: Optional[str] = Field(
        None,
        description="Official adjudication observations by the Controller / Deputy Controller"
    )
    hearing_date: Optional[date] = Field(
        None,
        description="Designated compliance hearing date"
    )


class AdjudicationResponse(BaseModel):
    inspection_id: str
    inspection_number: str
    compliance_status: str
    adjudication_status: str
    compounding_amount: Optional[float] = None
    compounding_order_number: Optional[str] = None
    receipt_number: Optional[str] = None
    court_jurisdiction: Optional[str] = None
    adjudication_notes: Optional[str] = None
    adjudicated_by_user: str
    updated_at: datetime

    model_config = {"from_attributes": True}
