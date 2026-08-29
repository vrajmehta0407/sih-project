"""
consensus_engine.py
====================
Stage 3 — Dual OCR Consensus & Alignment Engine

Implements:
  1. Spatial bounding box matching (Intersection over Union).
  2. Character/Token level Levenshtein similarity analysis.
  3. Numerical & statutory symbol integrity verification (MRP, dates, weight).
  4. Confidence-weighted token selection.
  5. Disagreement matrix generation & manual review flagging.
"""

import re
import difflib
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

from app.core.config import settings
from app.services.ocr.ocr_engine import OCREngineResult, OCRTextBox


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------
@dataclass
class ConsensusToken:
    """A unified token resulting from dual-engine consensus arbitration."""
    text: str
    confidence: float
    box: List[List[int]]
    chosen_engine: str                              # 'consensus_agreed' | 'paddleocr' | 'tesseract' | 'fallback'
    paddle_text: Optional[str] = None
    tesseract_text: Optional[str] = None
    paddle_confidence: Optional[float] = None
    tesseract_confidence: Optional[float] = None
    similarity_ratio: float = 1.0
    is_disagreement: bool = False
    disagreement_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": round(self.confidence, 4),
            "box": self.box,
            "chosen_engine": self.chosen_engine,
            "paddle_text": self.paddle_text,
            "tesseract_text": self.tesseract_text,
            "paddle_confidence": round(self.paddle_confidence, 4) if self.paddle_confidence is not None else None,
            "tesseract_confidence": round(self.tesseract_confidence, 4) if self.tesseract_confidence is not None else None,
            "similarity_ratio": round(self.similarity_ratio, 4),
            "is_disagreement": self.is_disagreement,
            "disagreement_reason": self.disagreement_reason,
        }


@dataclass
class ConsensusResult:
    """Consolidated outcome of the dual OCR consensus pipeline for an image."""
    consensus_text: str
    tokens: List[ConsensusToken] = field(default_factory=list)
    paddle_raw_text: str = ""
    tesseract_raw_text: str = ""
    total_tokens: int = 0
    disagreement_count: int = 0
    overall_confidence: float = 0.0
    has_ocr_disagreement: bool = False
    manual_review_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consensus_text": self.consensus_text,
            "total_tokens": self.total_tokens,
            "disagreement_count": self.disagreement_count,
            "overall_confidence": round(self.overall_confidence, 4),
            "has_ocr_disagreement": self.has_ocr_disagreement,
            "manual_review_required": self.manual_review_required,
            "paddle_raw_text": self.paddle_raw_text,
            "tesseract_raw_text": self.tesseract_raw_text,
            "tokens": [t.to_dict() for t in self.tokens],
        }


# ---------------------------------------------------------------------------
# Algorithmic Helpers
# ---------------------------------------------------------------------------
def compute_levenshtein_similarity(s1: str, s2: str) -> float:
    """Computes normalized similarity ratio between two strings (0.0 to 1.0)."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    matcher = difflib.SequenceMatcher(None, s1.strip().lower(), s2.strip().lower())
    return matcher.ratio()


def compute_iou(box1_rect: Tuple[int, int, int, int], box2_rect: Tuple[int, int, int, int]) -> float:
    """
    Computes Intersection over Union (IoU) of two bounding rectangles.
    Inputs are (x, y, w, h).
    """
    x1, y1, w1, h1 = box1_rect
    x2, y2, w2, h2 = box2_rect

    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)

    inter_width = max(0, xi2 - xi1)
    inter_height = max(0, yi2 - yi1)
    inter_area = inter_width * inter_height

    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def has_digit_mismatch(s1: str, s2: str) -> bool:
    """
    Detects if two strings have conflicting numeric digits.
    Critical for Legal Metrology price (MRP), date, and net quantity integrity.
    """
    digits1 = re.findall(r"\d+", s1)
    digits2 = re.findall(r"\d+", s2)
    if digits1 and digits2 and digits1 != digits2:
        return True
    return False


# ---------------------------------------------------------------------------
# Consensus Engine
# ---------------------------------------------------------------------------
class ConsensusEngine:
    """
    Reconciles outputs from PaddleOCR and Tesseract to generate a high-confidence,
    verified text consensus matrix.
    """

    def reconcile(
        self,
        paddle_result: OCREngineResult,
        tesseract_result: OCREngineResult,
    ) -> ConsensusResult:
        """
        Main entry point to reconcile two OCR engine results.
        """
        # Case 1: Both engines succeeded
        if paddle_result.success and tesseract_result.success and tesseract_result.boxes:
            return self._reconcile_dual(paddle_result, tesseract_result)

        # Case 2: Only PaddleOCR succeeded
        if paddle_result.success:
            return self._build_single_engine_result(paddle_result, "paddleocr", tesseract_result.raw_text)

        # Case 3: Only Tesseract succeeded
        if tesseract_result.success:
            return self._build_single_engine_result(tesseract_result, "tesseract", paddle_result.raw_text)

        # Case 4: Neither engine produced output
        return ConsensusResult(
            consensus_text="",
            paddle_raw_text=paddle_result.raw_text,
            tesseract_raw_text=tesseract_result.raw_text,
            has_ocr_disagreement=False,
            manual_review_required=True,
        )

    def _reconcile_dual(
        self,
        paddle_res: OCREngineResult,
        tesseract_res: OCREngineResult,
    ) -> ConsensusResult:
        """
        Spatial alignment and token arbitration between PaddleOCR and Tesseract.
        """
        consensus_tokens: List[ConsensusToken] = []
        tess_boxes_used = set()
        disagreement_count = 0

        # Iterate through primary detector boxes (PaddleOCR has superior scene text localization)
        for p_box in paddle_res.boxes:
            p_rect = p_box.bounding_rect
            best_tess_idx = -1
            best_iou = 0.0

            # Find matching spatial box in Tesseract outputs
            for t_idx, t_box in enumerate(tesseract_res.boxes):
                if t_idx in tess_boxes_used:
                    continue
                t_rect = t_box.bounding_rect
                iou = compute_iou(p_rect, t_rect)
                if iou > best_iou:
                    best_iou = iou
                    best_tess_idx = t_idx

            if best_tess_idx >= 0 and best_iou >= settings.OCR_IOU_MATCHING_THRESHOLD:
                # Spatial Match found!
                t_box = tesseract_res.boxes[best_tess_idx]
                tess_boxes_used.add(best_tess_idx)

                sim = compute_levenshtein_similarity(p_box.text, t_box.text)
                digit_conflict = has_digit_mismatch(p_box.text, t_box.text)

                if sim >= 0.95 and not digit_conflict:
                    # High agreement
                    chosen_text = p_box.text
                    confidence = max(p_box.confidence, t_box.confidence)
                    engine_choice = "consensus_agreed"
                    is_disagree = False
                    reason = None
                elif sim >= settings.OCR_DISAGREEMENT_SIMILARITY_THRESHOLD and not digit_conflict:
                    # Minor typographical variance — pick highest confidence engine
                    if p_box.confidence >= t_box.confidence:
                        chosen_text = p_box.text
                        confidence = p_box.confidence
                        engine_choice = "paddleocr"
                    else:
                        chosen_text = t_box.text
                        confidence = t_box.confidence
                        engine_choice = "tesseract"
                    is_disagree = False
                    reason = None
                else:
                    # Significant disagreement or numerical mismatch!
                    is_disagree = True
                    disagreement_count += 1
                    reason = (
                        f"Numerical conflict: '{p_box.text}' vs '{t_box.text}'"
                        if digit_conflict
                        else f"Low text similarity ({sim:.2f}): '{p_box.text}' vs '{t_box.text}'"
                    )
                    # PaddleOCR is generally preferred for packaging fonts, but flagged
                    chosen_text = p_box.text if p_box.confidence >= t_box.confidence else t_box.text
                    confidence = (p_box.confidence + t_box.confidence) / 2.0
                    engine_choice = "paddleocr" if p_box.confidence >= t_box.confidence else "tesseract"

                token = ConsensusToken(
                    text=chosen_text,
                    confidence=confidence,
                    box=p_box.box,
                    chosen_engine=engine_choice,
                    paddle_text=p_box.text,
                    tesseract_text=t_box.text,
                    paddle_confidence=p_box.confidence,
                    tesseract_confidence=t_box.confidence,
                    similarity_ratio=sim,
                    is_disagreement=is_disagree,
                    disagreement_reason=reason,
                )
                consensus_tokens.append(token)
            else:
                # No matching spatial box in Tesseract (PaddleOCR detected text that Tesseract missed)
                token = ConsensusToken(
                    text=p_box.text,
                    confidence=p_box.confidence,
                    box=p_box.box,
                    chosen_engine="paddleocr",
                    paddle_text=p_box.text,
                    tesseract_text=None,
                    paddle_confidence=p_box.confidence,
                    tesseract_confidence=None,
                    similarity_ratio=1.0,
                    is_disagreement=False,
                    disagreement_reason=None,
                )
                consensus_tokens.append(token)

        # Catch remaining Tesseract text that PaddleOCR might have missed
        for t_idx, t_box in enumerate(tesseract_res.boxes):
            if t_idx not in tess_boxes_used and t_box.confidence >= settings.OCR_CONFIDENCE_THRESHOLD:
                token = ConsensusToken(
                    text=t_box.text,
                    confidence=t_box.confidence,
                    box=t_box.box,
                    chosen_engine="tesseract",
                    paddle_text=None,
                    tesseract_text=t_box.text,
                    paddle_confidence=None,
                    tesseract_confidence=t_box.confidence,
                    similarity_ratio=1.0,
                    is_disagreement=False,
                    disagreement_reason=None,
                )
                consensus_tokens.append(token)

        # Assemble full consensus text
        # Group by vertical line index / box top position
        sorted_tokens = sorted(consensus_tokens, key=lambda t: (min(p[1] for p in t.box), min(p[0] for p in t.box)))
        consensus_text = " ".join([t.text for t in sorted_tokens])

        # Compute overall confidence
        total_tokens = len(sorted_tokens)
        overall_conf = (
            sum(t.confidence for t in sorted_tokens) / total_tokens if total_tokens > 0 else 0.0
        )

        has_disagreements = disagreement_count > 0
        manual_review = has_disagreements or overall_conf < settings.OCR_CONFIDENCE_THRESHOLD

        return ConsensusResult(
            consensus_text=consensus_text,
            tokens=sorted_tokens,
            paddle_raw_text=paddle_res.raw_text,
            tesseract_raw_text=tesseract_res.raw_text,
            total_tokens=total_tokens,
            disagreement_count=disagreement_count,
            overall_confidence=overall_conf,
            has_ocr_disagreement=has_disagreements,
            manual_review_required=manual_review,
        )

    def _build_single_engine_result(
        self,
        res: OCREngineResult,
        engine_name: str,
        other_raw_text: str,
    ) -> ConsensusResult:
        """Constructs a consensus result when only one OCR engine is active/available."""
        tokens: List[ConsensusToken] = []
        for box in res.boxes:
            p_text = box.text if engine_name == "paddleocr" else None
            t_text = box.text if engine_name == "tesseract" else None
            p_conf = box.confidence if engine_name == "paddleocr" else None
            t_conf = box.confidence if engine_name == "tesseract" else None

            tokens.append(
                ConsensusToken(
                    text=box.text,
                    confidence=box.confidence,
                    box=box.box,
                    chosen_engine=engine_name,
                    paddle_text=p_text,
                    tesseract_text=t_text,
                    paddle_confidence=p_conf,
                    tesseract_confidence=t_conf,
                    similarity_ratio=1.0,
                    is_disagreement=False,
                )
            )

        total_tokens = len(tokens)
        overall_conf = sum(t.confidence for t in tokens) / total_tokens if total_tokens > 0 else 0.0
        manual_review = overall_conf < settings.OCR_CONFIDENCE_THRESHOLD

        paddle_raw = res.raw_text if engine_name == "paddleocr" else other_raw_text
        tess_raw = res.raw_text if engine_name == "tesseract" else other_raw_text

        return ConsensusResult(
            consensus_text=res.raw_text,
            tokens=tokens,
            paddle_raw_text=paddle_raw,
            tesseract_raw_text=tess_raw,
            total_tokens=total_tokens,
            disagreement_count=0,
            overall_confidence=overall_conf,
            has_ocr_disagreement=False,
            manual_review_required=manual_review,
        )


# Singleton
consensus_engine = ConsensusEngine()
