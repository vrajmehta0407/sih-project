"""
models/state_rule_override.py
=============================
Stage 14 — State-Specific Jurisdiction Rule Override Database Model
"""

from sqlalchemy import Column, String, Boolean, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base import Base


class StateRuleOverride(Base):
    """
    State-specific statutory amendments and local exemptions under Section 53
    of the Legal Metrology Act, 2009.
    Allows State Controllers to enforce local dual-language mandates or local threshold exemptions.
    """
    __tablename__ = "state_rule_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_code = Column(String(10), index=True, nullable=False)  # e.g., "MH", "TN", "DL", "KA"
    state_name = Column(String(100), nullable=False)
    rule_code = Column(String(50), nullable=False)  # e.g., "RULE_6_1_E_MRP"
    override_type = Column(String(50), nullable=False)  # "EXEMPTION", "MANDATORY_LOCAL_LANG", "PENALTY_MULTIPLIER"
    description = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=True)  # Custom configuration JSON
    is_active = Column(Boolean, default=True)
    gazette_notification_ref = Column(String(255), nullable=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    created_by_email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
