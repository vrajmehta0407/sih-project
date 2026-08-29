"""
ocr_service.py
==============
Stage 3 — Inspection Multi-Side Dual OCR & Consensus Orchestrator
"""

import os
import logging
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.services.audit_service import audit_service
from app.services.ocr.ocr_engine import paddle_ocr_engine, tesseract_ocr_engine
from app.services.ocr.consensus_engine import consensus_engine, ConsensusResult

logger = logging.getLogger(__name__)


class OCRService:
    """
    Coordinates dual-engine OCR extraction and consensus matrix generation across
    all sides of an inspected product packaging.
    """

    def process_inspection_ocr(
        self,
        db: Session,
        inspection_id: str,
        user_id: str,
        request=None,
    ) -> Dict[str, Any]:
        """
        Executes dual OCR on all available preprocessed side images for an inspection.
        Updates Product record and advances Inspection state to 'extracted'.
        """
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection '{inspection_id}' not found.",
            )

        # Inspect preprocessed image records
        images = inspection.preprocessed_images or inspection.raw_images or []
        if not images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inspection does not contain any images to process with OCR.",
            )

        per_side_results: Dict[str, Any] = {}
        all_paddle_texts = []
        all_tess_texts = []
        all_consensus_texts = []
        total_tokens_across_sides = 0
        total_disagreements_across_sides = 0
        confidence_sum = 0.0
        sides_processed_count = 0
        any_disagreement = False
        any_manual_review = False

        for img_entry in images:
            side = img_entry.get("side", "unknown")
            # Prefer grayscale preprocessed image for maximum OCR contrast
            img_path = (
                img_entry.get("grayscale_path")
                or img_entry.get("file_path")
            )

            if not img_path or not os.path.isfile(img_path):
                logger.warning("Image file path not found for side '%s': %s", side, img_path)
                continue

            # Run PaddleOCR
            paddle_res = paddle_ocr_engine.extract(img_path)
            # Run Tesseract OCR
            tesseract_res = tesseract_ocr_engine.extract(img_path)

            # Reconcile outputs
            consensus_res: ConsensusResult = consensus_engine.reconcile(paddle_res, tesseract_res)

            per_side_results[side] = {
                "image_path": img_path,
                "paddle_success": paddle_res.success,
                "tesseract_success": tesseract_res.success,
                "paddle_time_ms": round(paddle_res.processing_time_ms, 2),
                "tesseract_time_ms": round(tesseract_res.processing_time_ms, 2),
                "consensus": consensus_res.to_dict(),
            }

            if paddle_res.raw_text:
                all_paddle_texts.append(f"[{side.upper()}]\n{paddle_res.raw_text}")
            if tesseract_res.raw_text:
                all_tess_texts.append(f"[{side.upper()}]\n{tesseract_res.raw_text}")
            if consensus_res.consensus_text:
                all_consensus_texts.append(f"[{side.upper()}]\n{consensus_res.consensus_text}")

            total_tokens_across_sides += consensus_res.total_tokens
            total_disagreements_across_sides += consensus_res.disagreement_count
            confidence_sum += consensus_res.overall_confidence
            sides_processed_count += 1

            if consensus_res.has_ocr_disagreement:
                any_disagreement = True
            if consensus_res.manual_review_required:
                any_manual_review = True

        if sides_processed_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="None of the inspection image files were readable on disk.",
            )

        avg_confidence = confidence_sum / sides_processed_count

        aggregated_paddle_text = "\n\n".join(all_paddle_texts)
        aggregated_tess_text = "\n\n".join(all_tess_texts)
        aggregated_consensus_text = "\n\n".join(all_consensus_texts)

        consensus_payload = {
            "per_side": per_side_results,
            "aggregated_consensus_text": aggregated_consensus_text,
            "aggregated_paddle_text": aggregated_paddle_text,
            "aggregated_tesseract_text": aggregated_tess_text,
            "total_tokens": total_tokens_across_sides,
            "total_disagreements": total_disagreements_across_sides,
            "overall_confidence": round(avg_confidence, 4),
            "has_ocr_disagreement": any_disagreement,
            "manual_review_required": any_manual_review,
        }

        # Update or create Product record
        product = db.query(Product).filter(Product.inspection_id == inspection_id).first()
        if not product:
            product = Product(inspection_id=inspection_id)
            db.add(product)

        product.paddle_raw_text = aggregated_paddle_text
        product.tesseract_raw_text = aggregated_tess_text
        product.extracted_fields_consensus = consensus_payload
        product.has_ocr_disagreement = any_disagreement
        product.manual_review_required = any_manual_review

        # Advance inspection state
        inspection.status = "extracted"

        db.commit()
        db.refresh(product)
        db.refresh(inspection)

        # Audit Trail
        audit_service.log(
            db=db,
            action="RUN_DUAL_OCR",
            entity_name="Inspection",
            entity_id=inspection_id,
            user_id=user_id,
            request=request,
            details={
                "sides_processed": list(per_side_results.keys()),
                "total_tokens": total_tokens_across_sides,
                "disagreements": total_disagreements_across_sides,
                "has_disagreement": any_disagreement,
                "confidence": round(avg_confidence, 4),
            },
        )

        return {
            "inspection_id": inspection_id,
            "inspection_number": inspection.inspection_number,
            "status": inspection.status,
            "ocr_consensus": consensus_payload,
        }


# Singleton
ocr_service = OCRService()
