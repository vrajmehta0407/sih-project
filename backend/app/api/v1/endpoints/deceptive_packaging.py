"""
endpoints/deceptive_packaging.py
================================
Stage 29 — Multi-Platform Dark Pattern & Deceptive Packaging VDI Endpoints
"""

import logging
from fastapi import APIRouter

from app.schemas.deceptive_packaging import (
    DeceptivePackagingAuditRequest,
    DeceptivePackagingAuditResponse,
)
from app.services.deceptive_packaging_service import deceptive_packaging_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/audit",
    response_model=DeceptivePackagingAuditResponse,
    summary="Audit Packaging for Non-Functional Slack Fill & Deceptive Sizing",
)
def audit_deceptive_packaging(req: DeceptivePackagingAuditRequest):
    """
    Evaluates 3D container dimensions against product displacement volume, computes
    the Visual Deception Index (VDI 0-10 scale), flags non-functional slack fill,
    and returns statutory citations under Section 18 and Rule 5.
    """
    return deceptive_packaging_service.audit_package(req)


@router.get(
    "/reports/{audit_id}",
    response_model=DeceptivePackagingAuditResponse,
    summary="Get Deceptive Packaging Audit Report by ID",
)
def get_deceptive_packaging_audit(audit_id: str):
    """Retrieve certified deceptive packaging audit report and VDI verdict by audit ID."""
    return deceptive_packaging_service.get_audit(audit_id)
