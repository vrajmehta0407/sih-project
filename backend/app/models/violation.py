import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(36), ForeignKey("rules.id", ondelete="SET NULL"), nullable=True)
    rule_code = Column(String(100), nullable=False, index=True)
    field_affected = Column(String(100), nullable=False)

    # Statutory Grounding
    section_violated = Column(String(255), nullable=False)  # e.g., "Rule 6(1)(e) r/w Section 18"
    statute_title = Column(String(255), nullable=False, default="Legal Metrology (Packaged Commodities) Rules, 2011")
    penalty_provision = Column(String(255), nullable=False, default="Section 36, Legal Metrology Act, 2009")
    estimated_fine = Column(Text, nullable=True)

    violation_title = Column(String(255), nullable=False)
    violation_description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False, default="critical", index=True)  # critical, major, minor
    is_repeat_offender_alert = Column(Boolean, default=False)
    evidence_crop_url = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    inspection = relationship("Inspection", back_populates="violations")
    rule = relationship("Rule", back_populates="violations")
