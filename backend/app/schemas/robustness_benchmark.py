"""
schemas/robustness_benchmark.py
===============================
Stage 24 — Automated OCR Synthetic Stress-Testing & Adversarial Benchmark Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class DegradationProfileResult(BaseModel):
    """Result for a single adversarial perturbation profile."""
    profile_name: str  # "GAUSSIAN_BLUR", "PERSPECTIVE_SKEW", "SPECULAR_GLARE", "SENSOR_NOISE", "POLYBAG_CRINKLE", "INK_FADING"
    description: str
    severity_level: str  # "MILD", "MODERATE", "SEVERE"
    pre_restoration_ocr_conf: float
    post_restoration_ocr_conf: float
    character_recovery_rate: float  # Percentage (0-100%)
    fields_extracted_count: int
    is_rule6_parsable: bool


class RobustnessBenchmarkResponse(BaseModel):
    """Full benchmark report evaluating OCR pipeline robustness under adversarial stress."""
    benchmark_id: str
    test_timestamp: datetime
    overall_robustness_score: float  # (0 - 100%)
    robustness_grade: str  # "MIL-SPEC A+", "HIGHLY ROBUST A", "MODERATE B", "FRAGILE C"
    total_profiles_evaluated: int
    profiles_passed_count: int
    average_character_recovery_rate: float
    degradation_results: List[DegradationProfileResult]
    pipeline_resilience_summary: str
