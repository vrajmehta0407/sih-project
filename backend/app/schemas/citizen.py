"""
schemas/citizen.py
==================
Stage 15 — Public Citizen Grievance & AI Triage Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class CitizenComplaintCreate(BaseModel):
    """Payload submitted by a citizen via public reporting gateway."""
    citizen_name: Optional[str] = Field(None, example="Rahul Sharma")
    citizen_contact: str = Field(..., example="rahul.sharma@example.com", description="Email or phone for ticket tracking updates")
    retailer_name: str = Field(..., example="City Supermarket Store #4")
    retailer_address: Optional[str] = Field(None, example="MG Road, Fort, Mumbai 400001")
    state: str = Field(..., example="Maharashtra")
    district: str = Field(..., example="Mumbai")
    violation_category: str = Field(..., example="OVERCHARGING_MRP")  # "OVERCHARGING_MRP", "DUAL_MRP", "MISSING_DECLARATIONS", "EXPIRED_SALE"
    complaint_description: str = Field(..., example="Retailer charged ₹120 for product having printed MRP of ₹100.")
    charged_price: Optional[float] = Field(None, gt=0, example=120.0)


class CitizenComplaintResponse(BaseModel):
    """Response returned after complaint submission or for officer triage."""
    id: uuid.UUID
    ticket_number: str
    citizen_name: Optional[str]
    citizen_contact: str
    retailer_name: str
    retailer_address: Optional[str]
    state: str
    district: str
    violation_category: str
    complaint_description: str
    charged_price: Optional[float]
    ai_detected_mrp: Optional[float]
    ai_credibility_score: float
    ai_triage_notes: Optional[str]
    status: str
    assigned_inspection_id: Optional[str]
    resolution_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CitizenTrackingResponse(BaseModel):
    """Public tracking status for citizen lookup."""
    ticket_number: str
    retailer_name: str
    state: str
    district: str
    violation_category: str
    status: str
    ai_credibility_score: float
    created_at: datetime
    resolution_notes: Optional[str]
