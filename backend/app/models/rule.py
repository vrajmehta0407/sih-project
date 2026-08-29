import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_tag = Column(String(50), unique=True, nullable=False)  # e.g., "LM-PCR-2011-V2.1-2024"
    statutory_act = Column(String(255), nullable=False, default="Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011")
    description = Column(Text, nullable=True)
    gazette_notification_ref = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    published_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    rules = relationship("Rule", back_populates="version", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="rule_version")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = Column(String(36), ForeignKey("rule_versions.id", ondelete="CASCADE"), nullable=False)
    rule_code = Column(String(100), nullable=False, index=True)  # e.g. "LM_RULE_6_MRP", "LM_RULE_6_NET_QTY"
    title = Column(String(255), nullable=False)
    statutory_source = Column(String(255), nullable=False)  # e.g. "Rule 6(1)(e), Legal Metrology (Packaged Commodities) Rules, 2011"
    statutory_penalty_source = Column(String(255), nullable=False, default="Section 36, Legal Metrology Act, 2009")
    penalty_first_offence = Column(String(100), default="Fine up to ₹25,000")
    penalty_repeat_offence = Column(String(255), default="Fine up to ₹50,000 or imprisonment up to 1 year")
    description = Column(Text, nullable=False)
    field_to_validate = Column(String(100), nullable=False, index=True)  # mrp, net_quantity, batch_no, mfg_date, exp_date, manufacturer, country_of_origin, consumer_care, unit_sale_price
    is_mandatory = Column(Boolean, default=True)
    validation_type = Column(String(50), nullable=False, default="presence_and_format")  # presence_and_format, regex, unit_check, numeric_range, date_validity
    validation_parameters = Column(JSON, default=dict)
    severity = Column(String(50), nullable=False, default="critical")  # critical, major, minor
    state_override = Column(String(100), nullable=True)  # NULL for Pan-India, or State name
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    version = relationship("RuleVersion", back_populates="rules")
    violations = relationship("Violation", back_populates="rule")
