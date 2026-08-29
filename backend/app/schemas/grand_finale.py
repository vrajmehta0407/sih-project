"""
schemas/grand_finale.py
=======================
Stage 30 — Master SIH 2026 Grand Finale Demo Simulator Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DemoScenarioRequest(BaseModel):
    """Request to run a specific Grand Finale demo scenario."""
    scenario_id: str = Field("FULL_PIPELINE", example="FULL_PIPELINE")
    officer_name: str = Field("Inspector Rajesh Kumar", example="Inspector Rajesh Kumar")
    target_shop: str = Field("FastRetail Supermarkets, Bandra, Mumbai", example="FastRetail Supermarkets, Bandra, Mumbai")
    product_label_type: str = Field("PACKAGED_CEREAL_OVERCHARGE", example="PACKAGED_CEREAL_OVERCHARGE")


class DemoStepResult(BaseModel):
    """Result of a single automated demo pipeline step."""
    step_number: int
    step_name: str
    module_name: str
    status: str  # "PASS", "FLAGGED", "COMPLIANT"
    key_finding: str
    data_payload: Dict[str, Any]
    sha256_seal: str
    duration_ms: int


class GrandFinaleSimulatorResponse(BaseModel):
    """Master end-to-end demo pipeline result for SIH 2026 Grand Finale."""
    simulation_id: str
    scenario_title: str
    officer_name: str
    target_shop: str
    simulated_at: datetime
    total_steps: int
    steps_passed: int
    steps_flagged: int
    pipeline_steps: List[DemoStepResult]
    jury_scorecard: Dict[str, Any]
    master_simulation_seal: str


class JuryScorecard(BaseModel):
    """SIH 2026 Jury evaluation scorecard with per-dimension scores."""
    innovation_score: float
    statutory_accuracy_score: float
    ai_depth_score: float
    field_deployability_score: float
    courtroom_readiness_score: float
    citizen_impact_score: float
    total_score: float
    max_score: float
    grade: str
    commendations: List[str]
