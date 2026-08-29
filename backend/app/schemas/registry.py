"""
schemas/registry.py
===================
Stage 13 — National Product Reference Registry Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class RegisteredProductCreate(BaseModel):
    """Request body for manufacturer product registration."""
    barcode_ean13: Optional[str] = Field(None, max_length=13, description="EAN-13 barcode (13 digits)")
    product_name: str
    manufacturer_name: str
    manufacturer_address: str
    declared_mrp: float = Field(..., gt=0)
    declared_net_quantity: str = Field(..., example="500 g")
    product_category: Optional[str] = None
    country_of_origin: Optional[str] = "India"
    authorized_batch_prefix: Optional[str] = None
    valid_until: Optional[datetime] = None
    registration_notes: Optional[str] = None


class RegisteredProductResponse(BaseModel):
    """Response for a registered product entry."""
    id: uuid.UUID
    barcode_ean13: Optional[str]
    product_name: str
    manufacturer_name: str
    manufacturer_address: str
    declared_mrp: float
    declared_net_quantity: str
    product_category: Optional[str]
    country_of_origin: Optional[str]
    authorized_batch_prefix: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    is_active: bool
    registered_by_email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CounterfeitCheckResponse(BaseModel):
    """Response from the counterfeit similarity check endpoint."""
    inspection_id: uuid.UUID
    similarity_score: float
    good_matches: int
    total_keypoints_query: int
    total_keypoints_reference: int
    is_suspected_counterfeit: bool
    confidence: str
    explanation: str
    reference_product_name: Optional[str] = None
