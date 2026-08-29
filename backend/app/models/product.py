import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    product_name = Column(String(255), nullable=True)
    brand_name = Column(String(255), nullable=True, index=True)
    category = Column(String(100), nullable=True)
    commodity_generic_name = Column(String(255), nullable=True)

    # Extracted Declarations
    mrp_raw = Column(String(100), nullable=True)
    mrp_value = Column(Float, nullable=True)
    mrp_currency = Column(String(10), default="INR")
    mrp_inclusive_taxes_declared = Column(Boolean, nullable=True)

    net_quantity_raw = Column(String(100), nullable=True)
    net_quantity_value = Column(Float, nullable=True)
    net_quantity_unit = Column(String(50), nullable=True)
    unit_sale_price_raw = Column(String(100), nullable=True)

    batch_number = Column(String(100), nullable=True, index=True)
    mfg_date_raw = Column(String(100), nullable=True)
    mfg_date = Column(Date, nullable=True)
    exp_date_raw = Column(String(100), nullable=True)
    exp_date = Column(Date, nullable=True)

    manufacturer_name = Column(Text, nullable=True, index=True)
    manufacturer_address = Column(Text, nullable=True)
    packer_name = Column(Text, nullable=True)
    packer_address = Column(Text, nullable=True)
    importer_name = Column(Text, nullable=True)
    importer_address = Column(Text, nullable=True)
    country_of_origin = Column(String(100), nullable=True)

    consumer_care_email = Column(String(255), nullable=True)
    consumer_care_phone = Column(String(50), nullable=True)
    consumer_care_address = Column(Text, nullable=True)

    # Dual OCR & NLP Consensus Info
    paddle_raw_text = Column(Text, nullable=True)
    tesseract_raw_text = Column(Text, nullable=True)
    extracted_fields_consensus = Column(JSON, default=dict)
    has_ocr_disagreement = Column(Boolean, default=False)
    manual_review_required = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    inspection = relationship("Inspection", back_populates="product")
