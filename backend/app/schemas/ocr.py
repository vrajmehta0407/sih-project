"""
schemas/ocr.py
==============
Pydantic v2 schemas for Dual OCR Extraction & Consensus Verification API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OCRTextBoxSchema(BaseModel):
    text: str
    confidence: float
    box: List[List[int]]
    engine: str
    line_index: int = 0
    bounding_rect: List[int]

    model_config = {"from_attributes": True}


class ConsensusTokenSchema(BaseModel):
    text: str
    confidence: float
    box: List[List[int]]
    chosen_engine: str
    paddle_text: Optional[str] = None
    tesseract_text: Optional[str] = None
    paddle_confidence: Optional[float] = None
    tesseract_confidence: Optional[float] = None
    similarity_ratio: float = 1.0
    is_disagreement: bool = False
    disagreement_reason: Optional[str] = None

    model_config = {"from_attributes": True}


class SideConsensusSchema(BaseModel):
    consensus_text: str
    total_tokens: int
    disagreement_count: int
    overall_confidence: float
    has_ocr_disagreement: bool
    manual_review_required: bool
    paddle_raw_text: str = ""
    tesseract_raw_text: str = ""
    tokens: List[ConsensusTokenSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SideOCRDetailSchema(BaseModel):
    image_path: str
    paddle_success: bool
    tesseract_success: bool
    paddle_time_ms: float
    tesseract_time_ms: float
    consensus: SideConsensusSchema

    model_config = {"from_attributes": True}


class OCRConsensusPayloadSchema(BaseModel):
    per_side: Dict[str, SideOCRDetailSchema]
    aggregated_consensus_text: str
    aggregated_paddle_text: str
    aggregated_tesseract_text: str
    total_tokens: int
    total_disagreements: int
    overall_confidence: float
    has_ocr_disagreement: bool
    manual_review_required: bool

    model_config = {"from_attributes": True}


class OCRRunResponse(BaseModel):
    inspection_id: str
    inspection_number: str
    status: str
    ocr_consensus: OCRConsensusPayloadSchema

    model_config = {"from_attributes": True}
