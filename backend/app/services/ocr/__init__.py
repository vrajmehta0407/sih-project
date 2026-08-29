"""
app.services.ocr
================
Stage 3 — Dual OCR & Consensus Pipeline Module
"""

from app.services.ocr.ocr_engine import (
    OCRTextBox,
    OCREngineResult,
    BaseOCREngine,
    PaddleOCREngine,
    TesseractOCREngine,
    paddle_ocr_engine,
    tesseract_ocr_engine,
)
from app.services.ocr.consensus_engine import (
    ConsensusToken,
    ConsensusResult,
    ConsensusEngine,
    consensus_engine,
)
from app.services.ocr.ocr_service import OCRService, ocr_service

__all__ = [
    "OCRTextBox",
    "OCREngineResult",
    "BaseOCREngine",
    "PaddleOCREngine",
    "TesseractOCREngine",
    "paddle_ocr_engine",
    "tesseract_ocr_engine",
    "ConsensusToken",
    "ConsensusResult",
    "ConsensusEngine",
    "consensus_engine",
    "OCRService",
    "ocr_service",
]
