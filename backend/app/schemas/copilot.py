"""
schemas/copilot.py
==================
Stage 25 — National Legal Metrology AI Regulatory Copilot Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CopilotQueryRequest(BaseModel):
    """User query submitted to the AI Regulatory Copilot."""
    query: str = Field(..., example="Is Unit Sale Price mandatory for packages under 10 grams?")
    jurisdiction_state: Optional[str] = Field("National", example="National")
    target_audience: Optional[str] = Field("OFFICER", example="OFFICER")  # "OFFICER", "RETAILER", "CONSUMER"


class StatutoryCitation(BaseModel):
    """Specific statutory citation backing the legal opinion."""
    act_or_rule: str  # "Legal Metrology Act, 2009" or "LM (Packaged Commodities) Rules, 2011"
    section_or_rule_no: str  # "Rule 6(1)(e)", "Section 36(1)", etc.
    title: str
    statutory_text_excerpt: str


class CopilotQueryResponse(BaseModel):
    """Authoritative legal opinion returned by the AI Regulatory Copilot."""
    query: str
    legal_opinion: str
    detected_intent: str
    citations: List[StatutoryCitation]
    penalty_implications: str
    recommended_officer_actions: List[str]
    is_compoundable: bool
    created_at: datetime
