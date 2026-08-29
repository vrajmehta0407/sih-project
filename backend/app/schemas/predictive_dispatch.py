"""
schemas/predictive_dispatch.py
==============================
Stage 20 — AI National Risk Heatmap & Predictive Raid Dispatch Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class HotspotCluster(BaseModel):
    cluster_id: str
    cluster_name: str
    state: str
    district: str
    latitude: float
    longitude: float
    market_vulnerability_index: float  # 0.0 to 100.0
    risk_level: str  # "CRITICAL", "HIGH", "MODERATE", "LOW"
    repeat_offenders_count: int
    unresolved_grievances: int
    recommended_action: str


class PredictiveHotspotsResponse(BaseModel):
    generated_at: datetime
    total_clusters_evaluated: int
    critical_clusters_count: int
    national_vulnerability_average: float
    hotspots: List[HotspotCluster]


class RaidRouteDispatchRequest(BaseModel):
    state: str = Field("Maharashtra", example="Maharashtra")
    district: str = Field("Mumbai", example="Mumbai")
    team_lead_email: Optional[str] = Field("inspector.mumbai@legalmetrology.gov.in", example="inspector.mumbai@legalmetrology.gov.in")
    max_targets: int = Field(5, ge=1, le=15, description="Maximum number of establishments to inspect")
    focus_category: Optional[str] = Field("ALL", example="ALL")  # "ALL", "OVERCHARGING", "DUAL_MRP", "EXPIRED"


class RaidTarget(BaseModel):
    stop_sequence: int
    retailer_name: str
    location_address: str
    latitude: float
    longitude: float
    priority_level: str  # "URGENT", "HIGH", "MEDIUM"
    primary_infraction_risk: str
    predicted_compounding_recovery_inr: float


class RaidRouteDispatchResponse(BaseModel):
    route_id: uuid.UUID
    dispatch_code: str
    state: str
    district: str
    assigned_team_lead: str
    dispatched_at: datetime
    total_stops: int
    estimated_duration_hours: float
    estimated_fine_recovery_inr: float
    targets: List[RaidTarget]
    status: str  # "DISPATCHED", "IN_PROGRESS", "COMPLETED"
