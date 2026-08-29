"""
schemas/state_override.py
=========================
Stage 14 — State-Specific Jurisdiction Rule Override Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class StateRuleOverrideCreate(BaseModel):
    """Payload to create a state-specific rule override or exemption."""
    state_code: str = Field(..., max_length=10, example="MH")
    state_name: str = Field(..., example="Maharashtra")
    rule_code: str = Field(..., example="RULE_6_1_E_MRP")
    override_type: str = Field(..., example="MANDATORY_LOCAL_LANG")  # "EXEMPTION", "MANDATORY_LOCAL_LANG", "PENALTY_MULTIPLIER"
    description: str
    parameters: Optional[Dict[str, Any]] = None
    gazette_notification_ref: Optional[str] = Field(None, example="Govt. of Maharashtra Gazette No. LM-2026/412")
    is_active: bool = True


class StateRuleOverrideResponse(BaseModel):
    """Response representing a state rule override entry."""
    id: uuid.UUID
    state_code: str
    state_name: str
    rule_code: str
    override_type: str
    description: str
    parameters: Optional[Dict[str, Any]]
    is_active: bool
    gazette_notification_ref: Optional[str]
    effective_from: datetime
    created_by_email: str
    created_at: datetime

    model_config = {"from_attributes": True}
