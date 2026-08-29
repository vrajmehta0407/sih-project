"""
schemas/inspection.py
=====================
Pydantic v2 schemas for Inspection & Image Preprocessing endpoints.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class ImageSide(str, Enum):
    front = "front"
    back = "back"
    left = "left"
    right = "right"
    top = "top"


class InspectionStatus(str, Enum):
    draft = "draft"
    preprocessed = "preprocessed"
    extracted = "extracted"
    validated = "validated"
    completed = "completed"


class ComplianceStatus(str, Enum):
    pending = "pending"
    compliant = "compliant"
    non_compliant = "non_compliant"
    review_required = "review_required"


# ---------------------------------------------------------------------------
# Preprocessing Metadata (embedded per-image)
# ---------------------------------------------------------------------------
class PreprocessingMetadata(BaseModel):
    skew_angle_degrees: float = Field(..., description="Detected skew angle in degrees")
    perspective_corrected: bool = Field(..., description="Whether perspective warp was applied")
    glare_regions_detected: int = Field(..., ge=0, description="Number of glare blobs detected")
    contrast_enhanced: bool = Field(default=True, description="Whether CLAHE was applied")
    quality_score: float = Field(..., ge=0, le=100, description="IQA composite score 0-100")
    processing_time_ms: float = Field(..., ge=0, description="Pipeline runtime in milliseconds")
    original_size: Optional[str] = Field(None, description="WxH of input image, e.g. '3024x4032'")
    processed_size: Optional[str] = Field(None, description="WxH of processed image")
    pipeline_steps: Optional[List[str]] = Field(None, description="Ordered list of completed pipeline steps")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Per-Image Response (one per side uploaded)
# ---------------------------------------------------------------------------
class InspectionImageResponse(BaseModel):
    side: str = Field(..., description="Image side: front/back/left/right/top")
    raw_url: str = Field(..., description="URL to the original uploaded image")
    processed_url: Optional[str] = Field(None, description="URL to the color-processed JPEG")
    grayscale_url: Optional[str] = Field(None, description="URL to the grayscale PNG for OCR")
    preprocessing: Optional[PreprocessingMetadata] = Field(
        None, description="Preprocessing pipeline result metadata"
    )
    success: bool = Field(default=True, description="Whether preprocessing succeeded for this side")
    error: Optional[str] = Field(None, description="Error message if preprocessing failed")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
class InspectionCreate(BaseModel):
    """
    Metadata fields submitted alongside image files.
    Submitted as form fields in multipart/form-data.
    """
    district: str = Field(..., min_length=2, max_length=100, description="District of inspection")
    state: str = Field(..., min_length=2, max_length=100, description="State of inspection")
    store_name: Optional[str] = Field(None, max_length=255, description="Name of the shop/store")
    store_address: Optional[str] = Field(None, description="Address of the shop/store")
    gps_latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    gps_longitude: Optional[float] = Field(None, ge=-180, le=180, description="GPS longitude")
    gps_accuracy_meters: Optional[float] = Field(None, ge=0, description="GPS accuracy in metres")
    inspector_notes: Optional[str] = Field(None, description="Inspector free-text notes")
    rule_version_id: Optional[str] = Field(None, description="UUID of active rule version to apply")

    @field_validator("district", "state", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class InspectionFilter(BaseModel):
    """Query parameters for listing inspections."""
    district: Optional[str] = None
    state: Optional[str] = None
    status: Optional[InspectionStatus] = None
    compliance_status: Optional[ComplianceStatus] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------
class InspectionSummary(BaseModel):
    """Lightweight response for list endpoints."""
    id: str
    inspection_number: str
    status: str
    compliance_status: str
    district: str
    state: str
    store_name: Optional[str]
    total_images: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InspectionResponse(BaseModel):
    """Full inspection detail response."""
    id: str
    inspection_number: str
    status: str
    compliance_status: str
    district: str
    state: str
    store_name: Optional[str]
    store_address: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    gps_accuracy_meters: Optional[float]
    inspector_notes: Optional[str]
    images: List[InspectionImageResponse] = Field(default_factory=list)
    preprocessing_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Per-side preprocessing metadata keyed by side name"
    )
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InspectionListResponse(BaseModel):
    """Paginated list wrapper."""
    total: int
    skip: int
    limit: int
    items: List[InspectionSummary]


class AddImagesResponse(BaseModel):
    """Response when adding images to an existing inspection."""
    inspection_id: str
    added_images: List[InspectionImageResponse]


class DeleteResponse(BaseModel):
    """Confirmation of resource deletion."""
    message: str
    inspection_id: str
