"""
test_scorecard_and_certificates.py
==================================
Stage 17 — Unit & API Tests for Brand Scorecard & Model Certificates
"""

import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.scorecard import CertificateGenerateRequest
from app.services.brand_scorecard_service import brand_scorecard_service
from app.db.session import SessionLocal

client = TestClient(app)

ADMIN_TOKEN = None
INSPECTOR_TOKEN = None


def get_admin_token():
    global ADMIN_TOKEN
    if ADMIN_TOKEN:
        return ADMIN_TOKEN
    resp = client.post("/api/v1/auth/login", data={
        "username": "admin@legalmetrology.gov.in",
        "password": "AdminPassword@123",
    })
    assert resp.status_code == 200
    ADMIN_TOKEN = resp.json()["access_token"]
    return ADMIN_TOKEN


def get_inspector_token():
    global INSPECTOR_TOKEN
    if INSPECTOR_TOKEN:
        return INSPECTOR_TOKEN
    resp = client.post("/api/v1/auth/login", data={
        "username": "inspector.mumbai@legalmetrology.gov.in",
        "password": "InspectorPassword@123",
    })
    assert resp.status_code == 200
    INSPECTOR_TOKEN = resp.json()["access_token"]
    return INSPECTOR_TOKEN


# ── Brand Scorecard Unit & API Tests ─────────────────────────────────────────

def test_brand_scorecard_clean_brand_tier_a():
    db = SessionLocal()
    try:
        scorecard = brand_scorecard_service.compute_scorecard(db, "Amul Dairy")
        assert scorecard.compliance_rate >= 80.0
        assert scorecard.trust_tier in ("PLATINUM_GREEN", "GOLD_COMPLIANT")
        assert "Seal" in scorecard.trust_seal_badge
    finally:
        db.close()


def test_brand_scorecard_public_api_200():
    # Public endpoint without auth
    resp = client.get("/api/v1/registry/brands/Dabur/scorecard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["brand_name"] == "Dabur"
    assert "compliance_rate" in data
    assert "trust_tier" in data
    assert "active_registered_models" in data


def test_brand_scorecard_contains_risk_summary():
    resp = client.get("/api/v1/registry/brands/Patanjali/scorecard")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["risk_assessment_summary"]) > 10


# ── Certificate Generation Tests ─────────────────────────────────────────────

def test_certificate_generation_service_logic():
    req = CertificateGenerateRequest(
        brand_name="Tata Consumer Products",
        manufacturer_name="Tata Consumer Products Ltd",
        model_registration_number="LM-IND-2026-9901",
        commodity_category="Tea & Packaged Beverages",
        valid_until_years=3,
    )
    cert = brand_scorecard_service.generate_certificate(req, "admin@legalmetrology.gov.in")
    assert cert.certificate_number.startswith("LM-CERT-2026-")
    assert cert.qr_verification_token.startswith("QR-CERT-")
    assert len(cert.sha256_seal) == 64
    assert cert.certificate_status == "ACTIVE"


def test_certificate_sha256_seal_integrity():
    req = CertificateGenerateRequest(
        brand_name="Britannia Industries",
        manufacturer_name="Britannia Ltd",
        commodity_category="Biscuits & Bakery",
        valid_until_years=2,
    )
    cert1 = brand_scorecard_service.generate_certificate(req, "admin@gov.in")
    assert cert1.sha256_seal is not None
    assert len(cert1.sha256_seal) == 64


def test_certificate_valid_until_duration():
    req = CertificateGenerateRequest(
        brand_name="Nestle India",
        manufacturer_name="Nestle India Ltd",
        commodity_category="Packaged Foods",
        valid_until_years=5,
    )
    cert = brand_scorecard_service.generate_certificate(req, "admin@gov.in")
    days_delta = (cert.valid_until - cert.issued_at).days
    assert days_delta >= 365 * 4  # ~5 years


def test_certificate_generate_api_201():
    token = get_admin_token()
    payload = {
        "brand_name": "Haldiram Snacks",
        "manufacturer_name": "Haldiram Foods International Pvt Ltd",
        "commodity_category": "Traditional Indian Savouries",
        "valid_until_years": 3,
    }
    resp = client.post(
        "/api/v1/registry/certificates/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["certificate_number"].startswith("LM-CERT-2026-")
    assert data["brand_name"] == "Haldiram Snacks"
    assert data["certificate_status"] == "ACTIVE"


def test_certificate_generate_requires_admin_403():
    # Regular inspector cannot generate model certificate
    inspector_token = get_inspector_token()
    payload = {
        "brand_name": "Unauthorized Brand",
        "manufacturer_name": "Unauthorized Ltd",
        "commodity_category": "Snacks",
        "valid_until_years": 1,
    }
    resp = client.post(
        "/api/v1/registry/certificates/generate",
        json=payload,
        headers={"Authorization": f"Bearer {inspector_token}"},
    )
    assert resp.status_code == 403


def test_unauthenticated_cannot_generate_certificate_401():
    payload = {
        "brand_name": "Test Brand",
        "manufacturer_name": "Test Mfg",
        "commodity_category": "Food",
        "valid_until_years": 1,
    }
    resp = client.post("/api/v1/registry/certificates/generate", json=payload)
    assert resp.status_code == 401


def test_brand_scorecard_nonexistent_brand_fallback():
    resp = client.get("/api/v1/registry/brands/UnknownBrandXYZ123/scorecard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["brand_name"] == "UnknownBrandXYZ123"
    assert data["total_inspections"] == 0
    assert data["compliance_rate"] >= 90.0
