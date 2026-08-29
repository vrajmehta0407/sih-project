"""
counterfeit_detection_service.py
=================================
Stage 13 — AI Label Similarity & Counterfeit Detection Engine

Uses OpenCV ORB (Oriented FAST and Rotated BRIEF) keypoint descriptors
combined with a FLANN-based KNN matcher to compare an inspected label image
against a manufacturer-registered golden reference image.

Algorithm:
  1. Detect ORB keypoints & compute binary descriptors on both images.
  2. Run FLANN KNN match (k=2) for nearest-neighbour descriptor matching.
  3. Apply Lowe's ratio test (0.75) to filter high-quality matches.
  4. Compute similarity score = (good_matches / max_keypoints) * 100.
  5. Flag as SUSPECTED_COUNTERFEIT if score < COUNTERFEIT_THRESHOLD.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
ORB_MAX_FEATURES: int = 1000          # ORB keypoints to detect
FLANN_INDEX_LSH: int = 6             # FLANN index type for binary descriptors
LOWE_RATIO: float = 0.75             # Lowe's ratio test threshold
COUNTERFEIT_THRESHOLD: float = 35.0  # Similarity score below this = suspected counterfeit
MIN_GOOD_MATCHES: int = 10           # Minimum matches required for a meaningful comparison


# ── Result dataclass ─────────────────────────────────────────────────────────
@dataclass
class SimilarityResult:
    """Result from counterfeit label similarity check."""
    similarity_score: float          # 0 (no match) to 100 (identical)
    good_matches: int                # Lowe's ratio test survivors
    total_keypoints_query: int       # Keypoints found in inspected image
    total_keypoints_reference: int   # Keypoints found in reference image
    is_suspected_counterfeit: bool   # True if score < COUNTERFEIT_THRESHOLD
    confidence: str                  # "HIGH", "MEDIUM", "LOW", "INSUFFICIENT"
    explanation: str                 # Human-readable verdict


# ── Service ──────────────────────────────────────────────────────────────────
class CounterfeitDetectionService:
    """
    Compares an inspected label against a manufacturer-registered golden reference
    using ORB feature descriptors and FLANN-based KNN matching.
    """

    def __init__(self):
        self._orb = cv2.ORB_create(nfeatures=ORB_MAX_FEATURES)
        # FLANN parameters for binary (ORB) descriptors
        index_params = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
        search_params = dict(checks=50)
        self._flann = cv2.FlannBasedMatcher(index_params, search_params)

    def compare(
        self,
        inspected_image_path: str,
        reference_image_path: str,
    ) -> SimilarityResult:
        """
        Compare inspected label vs. registered golden reference image.

        Returns:
            SimilarityResult with similarity score and counterfeit flag.
        """
        try:
            img_query = self._load_gray(inspected_image_path)
            img_ref = self._load_gray(reference_image_path)
        except (FileNotFoundError, ValueError) as exc:
            return SimilarityResult(
                similarity_score=0.0,
                good_matches=0,
                total_keypoints_query=0,
                total_keypoints_reference=0,
                is_suspected_counterfeit=True,
                confidence="INSUFFICIENT",
                explanation=f"Could not load images for comparison: {exc}",
            )

        kp_q, desc_q = self._orb.detectAndCompute(img_query, None)
        kp_r, desc_r = self._orb.detectAndCompute(img_ref, None)

        n_kp_q = len(kp_q) if kp_q else 0
        n_kp_r = len(kp_r) if kp_r else 0

        # Insufficient keypoints — cannot determine similarity
        if (
            desc_q is None or desc_r is None
            or n_kp_q < MIN_GOOD_MATCHES
            or n_kp_r < MIN_GOOD_MATCHES
        ):
            return SimilarityResult(
                similarity_score=0.0,
                good_matches=0,
                total_keypoints_query=n_kp_q,
                total_keypoints_reference=n_kp_r,
                is_suspected_counterfeit=True,
                confidence="INSUFFICIENT",
                explanation="Insufficient keypoints detected — image quality too low for comparison.",
            )

        # Ensure descriptors are uint8 for FLANN LSH
        desc_q = desc_q.astype(np.uint8)
        desc_r = desc_r.astype(np.uint8)

        try:
            raw_matches = self._flann.knnMatch(desc_q, desc_r, k=2)
        except cv2.error as exc:
            logger.warning("FLANN matching failed, falling back to BF matcher: %s", exc)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            raw_matches = bf.knnMatch(desc_q, desc_r, k=2)

        # Lowe's ratio test
        good_matches = []
        for match_pair in raw_matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < LOWE_RATIO * n.distance:
                    good_matches.append(m)

        n_good = len(good_matches)
        max_possible = max(n_kp_q, n_kp_r)
        score = round(min(100.0, (n_good / max(1, max_possible)) * 100.0 * 3.0), 2)
        # ×3 amplification to scale ORB sparse matches to 0–100 range
        score = min(100.0, score)

        is_counterfeit = score < COUNTERFEIT_THRESHOLD

        if n_good < MIN_GOOD_MATCHES:
            confidence = "INSUFFICIENT"
        elif score >= 70:
            confidence = "HIGH"
        elif score >= 45:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        if is_counterfeit:
            explanation = (
                f"SUSPECTED COUNTERFEIT — Similarity score {score:.1f}% is below the "
                f"authenticity threshold of {COUNTERFEIT_THRESHOLD}%. "
                f"Only {n_good} feature correspondences found between the inspected label "
                f"and the manufacturer-registered golden reference."
            )
        else:
            explanation = (
                f"Label appears AUTHENTIC — Similarity score {score:.1f}% exceeds the "
                f"authenticity threshold. {n_good} strong feature correspondences matched "
                f"with the manufacturer-registered golden reference image."
            )

        return SimilarityResult(
            similarity_score=score,
            good_matches=n_good,
            total_keypoints_query=n_kp_q,
            total_keypoints_reference=n_kp_r,
            is_suspected_counterfeit=is_counterfeit,
            confidence=confidence,
            explanation=explanation,
        )

    def _load_gray(self, path: str) -> np.ndarray:
        """Load image as grayscale NumPy array."""
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image not found: {path}")
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not decode image: {path}")
        return img


# Module-level singleton
counterfeit_detection_service = CounterfeitDetectionService()
