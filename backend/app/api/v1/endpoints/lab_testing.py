"""
endpoints/lab_testing.py
========================
Stage 27 — Central Laboratory Gravimetric Tare Testing & NABL Certificate Endpoints
"""

import logging
from typing import Dict
from fastapi import APIRouter

from app.schemas.lab_testing import (
    LabSampleSubmissionRequest,
    LabTestReportResponse,
)
from app.services.lab_testing_service import lab_testing_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/submit",
    response_model=LabTestReportResponse,
    summary="Submit Laboratory Sample for Gravimetric Tare Verification",
)
def submit_lab_sample(req: LabSampleSubmissionRequest):
    """
    Computes net quantity from gross and tare weights, evaluates variance against
    statutory Maximum Permissible Error (MPE) thresholds under the Second Schedule,
    and returns an official NABL-Accredited Test Certificate with a cryptographic seal.
    """
    return lab_testing_service.process_test(req)


@router.get(
    "/reports/{sample_id}",
    response_model=LabTestReportResponse,
    summary="Get Laboratory Test Certificate by Sample ID",
)
def get_lab_test_report(sample_id: str):
    """Retrieve certified laboratory gravimetric test report by sample ID."""
    return lab_testing_service.get_report(sample_id)


@router.get(
    "/mpe-lookup",
    summary="Lookup Second Schedule Maximum Permissible Error (MPE)",
)
def lookup_mpe(nominal_quantity: float):
    """Lookup statutory MPE tolerance in grams/ml and percentage for any nominal package quantity."""
    grams, pct = lab_testing_service.calculate_mpe(nominal_quantity)
    return {
        "nominal_quantity": nominal_quantity,
        "max_permissible_error_grams": grams,
        "max_permissible_error_pct": pct,
        "schedule": "Second Schedule, Legal Metrology (Packaged Commodities) Rules 2011",
    }
