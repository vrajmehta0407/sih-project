"""
models/citizen_complaint.py
===========================
Stage 15 — Public Citizen Grievance & Consumer Packaging Complaint Database Model
"""

from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base import Base


class CitizenComplaint(Base):
    """
    Consumer grievance record submitted via public reporting gateway.
    Stores packaging photo, alleged overcharging details, AI credibility score,
    and linked jurisdictional inspection task.
    """
    __tablename__ = "citizen_complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    citizen_name = Column(String(255), nullable=True)
    citizen_contact = Column(String(255), nullable=False)  # email or phone
    retailer_name = Column(String(255), nullable=False)
    retailer_address = Column(Text, nullable=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    violation_category = Column(String(100), nullable=False)  # OVERCHARGING_MRP, DUAL_MRP, MISSING_DECLARATIONS, EXPIRED_SALE
    complaint_description = Column(Text, nullable=False)
    image_path = Column(String(512), nullable=True)
    charged_price = Column(Float, nullable=True)
    ai_detected_mrp = Column(Float, nullable=True)
    ai_credibility_score = Column(Float, nullable=False, default=0.0)
    ai_triage_notes = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="SUBMITTED", index=True)  # SUBMITTED, TRIAGED, ASSIGNED, RESOLVED
    assigned_inspection_id = Column(String(36), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
