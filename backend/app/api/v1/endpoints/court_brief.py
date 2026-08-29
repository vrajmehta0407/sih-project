"""
endpoints/court_brief.py
========================
Stage 28 — Pre-Trial Court Evidence Brief & Section 65B Certificate Endpoints
"""

import logging
from fastapi import APIRouter

from app.schemas.court_brief import (
    CourtBriefGenerateRequest,
    CourtBriefResponse,
)
from app.services.court_brief_service import court_brief_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/generate",
    response_model=CourtBriefResponse,
    summary="Generate Pre-Trial Judicial Prosecution Brief & Sec 65B Certificate",
)
def generate_court_brief(req: CourtBriefGenerateRequest):
    """
    Assembles a standardized judicial chargesheet (Form V) for filing before the Chief Judicial
    Magistrate (CJM), complete with chronological facts, Section 49 accused corporate roster,
    evidentiary exhibits inventory, and a sworn Section 63 BSA 2023 / Sec 65B Evidence affidavit.
    """
    return court_brief_service.generate_brief(req)


@router.get(
    "/{dossier_id}",
    response_model=CourtBriefResponse,
    summary="Get Court Prosecution Dossier by ID",
)
def get_court_brief(dossier_id: str):
    """Retrieve certified court prosecution brief and digital affidavit by dossier ID."""
    return court_brief_service.get_brief(dossier_id)
