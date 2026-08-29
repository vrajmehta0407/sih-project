"""
test_lab_testing.py
===================
Stage 27 — Unit & API Tests for Central Laboratory Gravimetric Tare & MPE Verification
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.lab_testing import LabSampleSubmissionRequest
from app.services.lab_testing_service import lab_testing_service

client = TestClient(app)


# ── MPE Matrix Unit Tests ───────────────────────────────────────────────────

def test_lab_mpe_calculation_small_packages():
    # 50g package -> 9% MPE = 4.5g
    grams, pct = lab_testing_service.calculate_mpe(50.0)
    assert grams == 4.5
    assert pct == 9.0


def test_lab_mpe_calculation_medium_packages():
    # 500g package -> 3% MPE = 15.0g
    grams, pct = lab_testing_service.calculate_mpe(500.0)
    assert grams == 15.0
    assert pct == 3.0


def test_lab_mpe_calculation_large_packages():
    # 1000g (1kg) package -> 15.0g MPE
    grams, pct = lab_testing_service.calculate_mpe(1000.0)
    assert grams == 15.0


# ── Lab Testing Service Tests ───────────────────────────────────────────────

def test_lab_testing_service_compliant_sample():
    req = LabSampleSubmissionRequest(
        product_name="Amul Butter 500g",
        brand_name="Amul",
        lot_or_batch_number="LOT-2026-B1",
        declared_nominal_quantity=500.0,
        gross_weight_grams=510.0,
        tare_weight_grams=12.0,  # actual net = 498g -> diff -2g (well within MPE of 15g)
    )
    res = lab_testing_service.process_test(req)
    assert res.is_compliant_with_mpe is True
    assert res.statutory_verdict == "COMPLIANT_WITHIN_MPE"
    assert res.actual_net_content_grams == 498.0
    assert res.certificate_number.startswith("NABL-METROLOGY-2026-")


def test_lab_testing_service_short_delivery_offence():
    req = LabSampleSubmissionRequest(
        product_name="Deficient Sunflower Oil 1L",
        brand_name="Test Brand",
        lot_or_batch_number="LOT-2026-D9",
        declared_nominal_quantity=1000.0,
        gross_weight_grams=1010.0,
        tare_weight_grams=45.0,  # actual net = 965g -> deficit 35g (exceeds MPE of 15g)
    )
    res = lab_testing_service.process_test(req)
    assert res.is_compliant_with_mpe is False
    assert res.statutory_verdict == "SHORT_DELIVERY_OFFENCE"
    assert "Section 30" in res.applicable_rule or "Second Schedule" in res.applicable_rule


def test_lab_testing_service_digital_seal_integrity():
    req = LabSampleSubmissionRequest(
        product_name="Tata Salt 1kg",
        brand_name="Tata",
        lot_or_batch_number="LOT-2026-T1",
        declared_nominal_quantity=1000.0,
        gross_weight_grams=1030.0,
        tare_weight_grams=25.0,
    )
    res = lab_testing_service.process_test(req)
    assert len(res.digital_signature_hash) == 64  # SHA-256


# ── Lab Testing API Endpoints Tests ─────────────────────────────────────────

def test_lab_submit_api_200_compliant():
    payload = {
        "product_name": "API Compliant Salt 1kg",
        "brand_name": "Tata",
        "lot_or_batch_number": "LOT-2026-API-1",
        "declared_nominal_quantity": 1000.0,
        "gross_weight_grams": 1030.0,
        "tare_weight_grams": 25.0,
    }
    resp = client.post("/api/v1/lab-testing/submit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_compliant_with_mpe"] is True
    assert "certificate_number" in data


def test_lab_submit_api_200_short_delivery():
    payload = {
        "product_name": "API Short Oil 1L",
        "brand_name": "Offender Brand",
        "lot_or_batch_number": "LOT-2026-API-2",
        "declared_nominal_quantity": 1000.0,
        "gross_weight_grams": 980.0,
        "tare_weight_grams": 30.0,  # actual net = 950g
    }
    resp = client.post("/api/v1/lab-testing/submit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_compliant_with_mpe"] is False
    assert data["statutory_verdict"] == "SHORT_DELIVERY_OFFENCE"


def test_get_lab_report_api_200():
    # Submit first
    payload = {
        "sample_id": "SMPL-TEST-GET-01",
        "product_name": "Test Milk 500ml",
        "brand_name": "Amul",
        "lot_or_batch_number": "LOT-GET-1",
        "declared_nominal_quantity": 500.0,
        "gross_weight_grams": 520.0,
        "tare_weight_grams": 15.0,
    }
    client.post("/api/v1/lab-testing/submit", json=payload)

    # Retrieve
    resp = client.get("/api/v1/lab-testing/reports/SMPL-TEST-GET-01")
    assert resp.status_code == 200
    assert resp.json()["sample_id"] == "SMPL-TEST-GET-01"


def test_mpe_lookup_api_200():
    resp = client.get("/api/v1/lab-testing/mpe-lookup?nominal_quantity=500")
    assert resp.status_code == 200
    data = resp.json()
    assert data["nominal_quantity"] == 500.0
    assert data["max_permissible_error_grams"] == 15.0
    assert "Second Schedule" in data["schedule"]
