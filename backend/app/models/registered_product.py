"""
models/registered_product.py
=============================
Stage 13 — National Product Reference Registry Database Model
"""

from sqlalchemy import Column, String, Float, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.base import Base


class RegisteredProduct(Base):
    """
    Manufacturer-registered product record for counterfeit detection baseline.
    Stores the golden reference label image path, declared statutory values,
    and authorized batch range for cross-verification during field inspection.
    """
    __tablename__ = "registered_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    barcode_ean13 = Column(String(13), unique=True, index=True, nullable=True)
    product_name = Column(String(255), nullable=False)
    manufacturer_name = Column(String(255), nullable=False)
    manufacturer_address = Column(Text, nullable=False)
    declared_mrp = Column(Float, nullable=False)
    declared_net_quantity = Column(String(50), nullable=False)
    product_category = Column(String(100), nullable=True)
    country_of_origin = Column(String(100), nullable=True, default="India")
    golden_reference_image_path = Column(String(512), nullable=True)
    authorized_batch_prefix = Column(String(50), nullable=True)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    registered_by_email = Column(String(255), nullable=False)
    registration_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
