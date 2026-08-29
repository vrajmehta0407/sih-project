"""
endpoints/copilot.py
====================
Stage 25 — National Legal Metrology AI Regulatory Copilot API Endpoints
"""

import logging
from typing import List
from fastapi import APIRouter

from app.schemas.copilot import (
    CopilotQueryRequest,
    CopilotQueryResponse,
)
from app.services.regulatory_copilot_service import regulatory_copilot_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/query",
    response_model=CopilotQueryResponse,
    summary="Submit Query to AI Regulatory Copilot",
)
async def query_regulatory_copilot(req: CopilotQueryRequest):
    """
    Submits a natural language legal/statutory query to the AI Regulatory Copilot
    and returns authoritative statutory interpretation, exact Section citations,
    penalty clauses, and recommended officer enforcement actions.
    """
    return await regulatory_copilot_service.async_query(req)


@router.get(
    "/suggested-prompts",
    response_model=List[str],
    summary="Get Curated Legal & Statutory Prompt Suggestions",
)
def get_suggested_prompts():
    """Retrieve standard high-frequency statutory questions for 1-click legal research."""
    return [
        "Is Unit Sale Price mandatory for packages having net quantity under 10 grams?",
        "What are the digital display requirements for e-commerce platforms under Rule 6(10)?",
        "What are the mandatory font height rules for net quantity declarations under the First Schedule?",
        "What is the penalty range for a second offence of overcharging under Section 36(2)?",
        "Who is held liable for non-compliant packaging in a corporate entity under Section 49?",
        "Can a retail overcharging infraction be compounded under Section 48 without court filing?",
    ]
