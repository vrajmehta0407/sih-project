import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), unique=True, nullable=False)
    docket_number = Column(String(100), unique=True, index=True, nullable=False)  # e.g. "DOCKET-MH-2026-0045"
    
    pdf_file_path = Column(Text, nullable=False)
    pdf_download_url = Column(Text, nullable=True)
    qr_code_image_path = Column(Text, nullable=True)
    chain_of_custody_hash = Column(String(64), nullable=False)

    status = Column(String(50), default="issued")  # draft, issued, signed, served, archived
    notice_issued_to = Column(String(255), nullable=True)
    serving_date = Column(Date, nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    signed_by_inspector = Column(Boolean, default=True)
    inspector_signature_meta = Column(JSON, default=dict)

    # Relationships
    inspection = relationship("Inspection", back_populates="report")
