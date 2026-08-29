"""
schemas/sync.py
===============
Pydantic v2 schemas for Offline Field Batch Inspection Synchronization
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BatchSyncInspectionItem(BaseModel):
    client_offline_id: str = Field(..., description="Unique UUID generated on offline mobile tablet")
    store_name: str
    store_address: Optional[str] = None
    district: str
    state: str
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    offline_captured_at: Optional[datetime] = None
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    ocr_raw_text: Optional[str] = Field(None, description="Consensus OCR text captured offline")


class BatchSyncRequest(BaseModel):
    inspections: List[BatchSyncInspectionItem] = Field(..., min_length=1)


class BatchSyncResultItem(BaseModel):
    client_offline_id: str
    inspection_id: str
    inspection_number: str
    status: str
    compliance_status: str
    violations_count: int
    is_synced: bool = True
    message: Optional[str] = None


class BatchSyncResponse(BaseModel):
    total_submitted: int
    successfully_synced: int
    failed_count: int = 0
    results: List[BatchSyncResultItem] = Field(default_factory=list)
