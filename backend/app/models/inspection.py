import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_number = Column(String(100), unique=True, index=True, nullable=False)
    inspector_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    rule_version_id = Column(String(36), ForeignKey("rule_versions.id", ondelete="SET NULL"), nullable=True)

    # Location Details
    store_name = Column(String(255), nullable=True)
    store_address = Column(Text, nullable=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    gps_accuracy_meters = Column(Float, nullable=True)

    # Status
    status = Column(String(50), nullable=False, default="completed")  # draft, preprocessed, extracted, validated, completed
    compliance_status = Column(String(50), nullable=False, default="pending", index=True)  # compliant, non_compliant, review_required

    # Image metadata
    raw_images = Column(JSON, default=list)  # [{"side": "front", "file_path": "...", "url": "..."}, ...]
    preprocessed_images = Column(JSON, default=list)
    preprocessing_metadata = Column(JSON, default=dict)  # {side: {skew_angle, quality_score, ...}}

    # Chain of Custody & Hash
    record_sha256_hash = Column(String(64), nullable=True)
    qr_verification_token = Column(String(255), unique=True, nullable=True)
    is_offline_synced = Column(Boolean, default=False)
    synced_at = Column(DateTime, nullable=True)
    inspector_notes = Column(Text, nullable=True)

    # Statutory Adjudication & Compounding Workflow (Section 48/49 LM Act)
    adjudication_status = Column(String(50), nullable=False, default="pending")  # pending, notice_issued, compounded, court_referred, closed_warning
    compounding_amount = Column(Float, nullable=True)
    compounding_order_number = Column(String(100), nullable=True)
    compounding_receipt_number = Column(String(100), nullable=True)
    court_jurisdiction = Column(String(255), nullable=True)
    adjudication_notes = Column(Text, nullable=True)
    adjudicated_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    inspector = relationship("User", back_populates="inspections")
    rule_version = relationship("RuleVersion", back_populates="inspections")
    product = relationship("Product", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="inspection", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
