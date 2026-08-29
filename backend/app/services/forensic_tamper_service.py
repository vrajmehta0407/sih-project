"""
forensic_tamper_service.py
===========================
Stage 16 — Forensic Error Level Analysis (ELA) & Sticker Tamper Detection

Detects physical price over-stickers, digital cloning, and label tampering
by analyzing compression artifact discrepancies across the packaging image.
"""

import os
import cv2
import numpy as np
import logging
from dataclasses import dataclass
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

ELA_JPEG_QUALITY = 90
ELA_SCALE_FACTOR = 15.0  # Amplification for pixel error difference


@dataclass
class TamperAnalysisResult:
    """Result from Error Level Analysis (ELA) tamper evaluation."""
    tamper_score: float  # 0.0 (uniform/clean) to 100.0 (high variance/tampered)
    is_tampering_suspected: bool
    max_error_differential: float
    suspicious_regions_count: int
    heatmap_image_path: Optional[str]
    forensic_summary: str


class ForensicTamperService:
    """Performs Error Level Analysis (ELA) on packaging images."""

    def analyze_tampering(
        self,
        image_path: str,
        output_heatmap_path: Optional[str] = None,
    ) -> TamperAnalysisResult:
        """
        Run ELA on the input packaging image to detect compression anomalies.
        """
        if not os.path.isfile(image_path):
            return TamperAnalysisResult(
                tamper_score=0.0,
                is_tampering_suspected=False,
                max_error_differential=0.0,
                suspicious_regions_count=0,
                heatmap_image_path=None,
                forensic_summary="Image file not found for forensic tamper analysis.",
            )

        original = cv2.imread(image_path)
        if original is None:
            return TamperAnalysisResult(
                tamper_score=0.0,
                is_tampering_suspected=False,
                max_error_differential=0.0,
                suspicious_regions_count=0,
                heatmap_image_path=None,
                forensic_summary="Could not decode image for tamper analysis.",
            )

        # 1. Re-encode at known quality
        temp_encoded_path = image_path + ".temp_ela.jpg"
        cv2.imwrite(temp_encoded_path, original, [cv2.IMWRITE_JPEG_QUALITY, ELA_JPEG_QUALITY])
        recompressed = cv2.imread(temp_encoded_path)
        try:
            if os.path.exists(temp_encoded_path):
                os.remove(temp_encoded_path)
        except Exception:
            pass

        # 2. Compute absolute difference and scale
        diff = cv2.absdiff(original, recompressed).astype(np.float32)
        diff_scaled = diff * ELA_SCALE_FACTOR
        diff_clipped = np.clip(diff_scaled, 0, 255).astype(np.uint8)

        # 3. Grayscale variance calculation
        gray_diff = cv2.cvtColor(diff_clipped, cv2.COLOR_BGR2GRAY)
        mean_val = float(np.mean(gray_diff))
        std_val = float(np.std(gray_diff))
        max_val = float(np.max(gray_diff))

        # 4. Generate false-color JET heatmap
        heatmap = cv2.applyColorMap(gray_diff, cv2.COLORMAP_JET)

        # 5. Detect local high-variance hotspots (pasted stickers)
        _, thresh = cv2.threshold(gray_diff, 120, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant_hotspots = [c for c in contours if cv2.contourArea(c) > 50]

        # Score computation: standard deviation + hotspots
        tamper_score = min(100.0, round((std_val * 1.5) + (len(significant_hotspots) * 8.0), 1))
        is_tampered = tamper_score >= 45.0

        # Save heatmap if path specified
        saved_path = None
        if output_heatmap_path:
            cv2.imwrite(output_heatmap_path, heatmap)
            saved_path = output_heatmap_path

        if is_tampered:
            summary = (
                f"SUSPECTED TAMPERING (Score: {tamper_score}/100) — Error Level Analysis detected "
                f"{len(significant_hotspots)} high-variance artifact clusters. "
                f"Physical over-stickering, dual price labelling, or date alteration is likely."
            )
        else:
            summary = (
                f"CLEAN / UNIFORM (Score: {tamper_score}/100) — Error Level Analysis shows "
                f"consistent compression artifacts across the label surface. No secondary pasted stickers detected."
            )

        return TamperAnalysisResult(
            tamper_score=tamper_score,
            is_tampering_suspected=is_tampered,
            max_error_differential=max_val,
            suspicious_regions_count=len(significant_hotspots),
            heatmap_image_path=saved_path,
            forensic_summary=summary,
        )


forensic_tamper_service = ForensicTamperService()
