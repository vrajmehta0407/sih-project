"""
ocr_engine.py
==============
Stage 3 — Base OCR Abstractions, PaddleOCR (via RapidOCR-ONNX), and Tesseract OCR Engine Implementations
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any, Dict, Union

import numpy as np
import cv2
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------
@dataclass
class OCRTextBox:
    """A detected word or text line with spatial coordinates and confidence."""
    text: str
    confidence: float                                   # 0.0 to 1.0
    box: List[List[int]]                                # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    engine: str                                         # 'paddleocr' | 'tesseract'
    line_index: int = 0

    @property
    def bounding_rect(self) -> Tuple[int, int, int, int]:
        """Returns (x_min, y_min, width, height)."""
        xs = [p[0] for p in self.box]
        ys = [p[1] for p in self.box]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        return x_min, y_min, x_max - x_min, y_max - y_min

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "box": self.box,
            "engine": self.engine,
            "line_index": self.line_index,
            "bounding_rect": self.bounding_rect,
        }


@dataclass
class OCREngineResult:
    """Output from an OCR engine run on a single image."""
    engine_name: str
    success: bool
    raw_text: str = ""
    boxes: List[OCRTextBox] = field(default_factory=list)
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "success": self.success,
            "raw_text": self.raw_text,
            "box_count": len(self.boxes),
            "boxes": [b.to_dict() for b in self.boxes],
            "processing_time_ms": round(self.processing_time_ms, 2),
            "error_message": self.error_message,
        }


# ---------------------------------------------------------------------------
# Base Interface
# ---------------------------------------------------------------------------
class BaseOCREngine(ABC):
    """Abstract interface for all pluggable OCR engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name identifier of the OCR engine."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the OCR engine runtime / binary is available on the system."""
        pass

    @abstractmethod
    def extract(self, image_input: Union[str, np.ndarray]) -> OCREngineResult:
        """
        Run OCR extraction on image path or NumPy array.
        Returns OCREngineResult dataclass.
        """
        pass


# ---------------------------------------------------------------------------
# PaddleOCR Engine (RapidOCR-ONNX Implementation)
# ---------------------------------------------------------------------------
class PaddleOCREngine(BaseOCREngine):
    """
    PaddleOCR implementation powered by RapidOCR ONNX runtime.
    Provides sub-100ms inference with multi-oriented text detection (DBNet)
    and CRNN text recognition models.
    """

    def __init__(self):
        self._engine: Optional[Any] = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "paddleocr"

    def is_available(self) -> bool:
        try:
            import rapidocr_onnxruntime  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_engine(self):
        """Lazy load ONNX models into memory upon first use."""
        if not self._initialized:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._engine = RapidOCR()
                self._initialized = True
                logger.info("RapidOCR (PaddleOCR ONNX) engine initialized successfully.")
            except Exception as e:
                logger.error("Failed to initialize RapidOCR engine: %s", str(e))
                self._initialized = False
                self._engine = None
        return self._engine

    def extract(self, image_input: Union[str, np.ndarray]) -> OCREngineResult:
        t_start = time.monotonic()
        engine = self._get_engine()
        if engine is None:
            return OCREngineResult(
                engine_name=self.name,
                success=False,
                error_message="PaddleOCR (RapidOCR) engine is not initialized or rapidocr-onnxruntime is missing.",
            )

        try:
            # Handle string path vs NumPy array
            if isinstance(image_input, str):
                if not os.path.isfile(image_input):
                    return OCREngineResult(
                        engine_name=self.name,
                        success=False,
                        error_message=f"Image file not found: '{image_input}'",
                    )
                img = cv2.imread(image_input)
                if img is None:
                    return OCREngineResult(
                        engine_name=self.name,
                        success=False,
                        error_message=f"Failed to read image at '{image_input}'",
                    )
            else:
                img = image_input

            # Run inference: returns (ocr_result, elapse_list)
            # ocr_result is a list of [box_points, text, confidence]
            ocr_result, _ = engine(img)

            boxes: List[OCRTextBox] = []
            text_lines: List[str] = []

            if ocr_result:
                for idx, item in enumerate(ocr_result):
                    raw_box, text, score = item
                    # Format box points to integer coordinates [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                    formatted_box = [[int(pt[0]), int(pt[1])] for pt in raw_box]
                    clean_text = text.strip()
                    if clean_text:
                        boxes.append(
                            OCRTextBox(
                                text=clean_text,
                                confidence=float(score),
                                box=formatted_box,
                                engine=self.name,
                                line_index=idx,
                            )
                        )
                        text_lines.append(clean_text)

            raw_text = "\n".join(text_lines)
            elapsed_ms = (time.monotonic() - t_start) * 1000

            return OCREngineResult(
                engine_name=self.name,
                success=True,
                raw_text=raw_text,
                boxes=boxes,
                processing_time_ms=elapsed_ms,
            )

        except Exception as e:
            logger.exception("PaddleOCR extraction failed on input")
            elapsed_ms = (time.monotonic() - t_start) * 1000
            return OCREngineResult(
                engine_name=self.name,
                success=False,
                error_message=str(e),
                processing_time_ms=elapsed_ms,
            )


# ---------------------------------------------------------------------------
# Tesseract OCR Engine (pytesseract Implementation with Graceful Fallback)
# ---------------------------------------------------------------------------
class TesseractOCREngine(BaseOCREngine):
    """
    Tesseract OCR implementation using pytesseract.
    Extracts text line structures, word bounding boxes, and confidence levels.
    """

    def __init__(self):
        self._tesseract_available: Optional[bool] = None
        self._configure_cmd()

    @property
    def name(self) -> str:
        return "tesseract"

    def _configure_cmd(self):
        try:
            import pytesseract
            if settings.TESSERACT_CMD_PATH and os.path.exists(settings.TESSERACT_CMD_PATH):
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD_PATH
            elif os.name == "nt":
                # Check standard Windows paths if not configured
                default_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Users\vrajm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
                ]
                for p in default_paths:
                    if os.path.exists(p):
                        pytesseract.pytesseract.tesseract_cmd = p
                        break
        except Exception:
            pass

    def is_available(self) -> bool:
        if self._tesseract_available is None:
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
            except Exception:
                self._tesseract_available = False
        return self._tesseract_available

    def extract(self, image_input: Union[str, np.ndarray]) -> OCREngineResult:
        t_start = time.monotonic()
        try:
            import pytesseract
            from pytesseract import Output
        except ImportError:
            return OCREngineResult(
                engine_name=self.name,
                success=False,
                error_message="pytesseract is not installed.",
            )

        if not self.is_available():
            # Graceful degraded fallback for environments without Tesseract binary
            logger.warning("Tesseract binary not found on system path. Tesseract OCR skipped.")
            return OCREngineResult(
                engine_name=self.name,
                success=False,
                error_message="Tesseract binary is not installed or not found in system PATH.",
                processing_time_ms=(time.monotonic() - t_start) * 1000,
            )

        try:
            if isinstance(image_input, str):
                if not os.path.isfile(image_input):
                    return OCREngineResult(
                        engine_name=self.name,
                        success=False,
                        error_message=f"Image file not found: '{image_input}'",
                    )
                pil_img = Image.open(image_input)
            elif isinstance(image_input, np.ndarray):
                # Convert BGR/Gray numpy to PIL RGB
                if len(image_input.shape) == 2:
                    pil_img = Image.fromarray(image_input)
                else:
                    rgb = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb)
            else:
                pil_img = image_input

            # Run data extraction for bounding boxes + confidence
            data = pytesseract.image_to_data(pil_img, output_type=Output.DICT)
            raw_text = pytesseract.image_to_string(pil_img).strip()

            boxes: List[OCRTextBox] = []
            n_boxes = len(data["text"])
            line_idx = 0
            curr_line_num = -1

            for i in range(n_boxes):
                text = data["text"][i].strip()
                conf_val = float(data["conf"][i])
                if text and conf_val > 0:  # -1 is for layout blocks
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    line_num = data["line_num"][i]
                    if line_num != curr_line_num:
                        curr_line_num = line_num
                        line_idx += 1

                    box_pts = [
                        [x, y],
                        [x + w, y],
                        [x + w, y + h],
                        [x, y + h],
                    ]
                    boxes.append(
                        OCRTextBox(
                            text=text,
                            confidence=min(1.0, conf_val / 100.0),  # Tesseract returns 0-100
                            box=box_pts,
                            engine=self.name,
                            line_index=line_idx,
                        )
                    )

            elapsed_ms = (time.monotonic() - t_start) * 1000
            return OCREngineResult(
                engine_name=self.name,
                success=True,
                raw_text=raw_text,
                boxes=boxes,
                processing_time_ms=elapsed_ms,
            )

        except Exception as e:
            logger.exception("Tesseract extraction failed on input")
            elapsed_ms = (time.monotonic() - t_start) * 1000
            return OCREngineResult(
                engine_name=self.name,
                success=False,
                error_message=str(e),
                processing_time_ms=elapsed_ms,
            )


# Singleton instances
paddle_ocr_engine = PaddleOCREngine()
tesseract_ocr_engine = TesseractOCREngine()
