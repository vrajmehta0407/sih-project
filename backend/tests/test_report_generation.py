"""
test_report_generation.py
=========================
Stage 6 — Unit & API Tests for Statutory Inspection Report & QR Verification Service

Test coverage (10 tests):
  1. test_sha256_canonical_hash_generation       — Deterministic 64-character SHA-256 hex digest
  2. test_qr_code_image_generation               — Renders valid QR code PNG asset on disk
  3. test_pdf_report_rendering_creates_valid_pdf — ReportLab generates valid %PDF- header document
  4. test_pdf_report_with_violations_docket      — Generates PDF containing violations table & show-cause directive
  5. test_pdf_report_with_compliant_product      — Generates PDF containing compliance certification box
  6. test_generate_report_service_updates_db     — Report service persists Report row & completes Inspection
  7. test_post_generate_report_api_endpoint_200  — POST /inspections/{id}/report returns 200 with report details
  8. test_get_report_download_api_endpoint_200   — GET /inspections/{id}/report/download streams PDF file
  9. test_public_qr_verification_api_endpoint_200— GET /inspections/verify/{qr_token} verifies authenticity (public)
 10. test_invalid_qr_verification_token_404      — Unknown QR verification token returns 404
"""

import os
from datetime import date, datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation
from app.models.report import Report
from app.models.user import User
from app.services.report.crypto_service import crypto_service
from app.services.report.pdf_report_generator import pdf_report_generator
from app.services.report.report_service import report_service


# ===========================================================================
# Test 1 — SHA-256 Canonical Hash Generation
# ===========================================================================
def test_sha256_canonical_hash_generation():
    """Generates a deterministic 64-char SHA-256 digest regardless of dict key insertion order."""
    payload_a = {"b": 2, "a": 1, "nested": {"y": "val", "x": 10}}
    payload_b = {"a": 1, "nested": {"x": 10, "y": "val"}, "b": 2}

    hash_a = crypto_service.compute_canonical_hash(payload_a)
    hash_b = crypto_service.compute_canonical_hash(payload_b)

    assert len(hash_a) == 64
    assert hash_a == hash_b, "Canonical hash must be deterministic across key orderings."


# ===========================================================================
# Test 2 — QR Code Image Generation
# ===========================================================================
def test_qr_code_image_generation(tmp_path):
    """Renders a scannable QR code PNG image file."""
    qr_file = str(tmp_path / "test_qr.png")
    result_path = crypto_service.generate_qr_code_image(
        verification_url="http://localhost:8000/api/v1/inspections/verify/QR-LM-TEST-1234",
        output_path=qr_file,
    )
    assert os.path.isfile(result_path)
    assert os.path.getsize(result_path) > 100


# ===========================================================================
# Test 3 — PDF Report Rendering Generates Valid PDF Document
# ===========================================================================
def test_pdf_report_rendering_creates_valid_pdf(tmp_path):
    """ReportLab compiles a valid PDF document with %PDF- header magic bytes."""
    output_pdf = str(tmp_path / "test_report.pdf")
    doc_data = {
        "docket_number": "DOCKET-MH-2026-TEST",
        "chain_of_custody_hash": "a" * 64,
        "qr_verification_token": "QR-LM-20260825-ABCD1234",
        "inspection": {
            "inspection_number": "INS-TEST-001",
            "created_at": "25-08-2026 10:00",
            "compliance_status": "compliant",
            "district": "Mumbai",
            "state": "Maharashtra",
            "store_name": "Super Mart",
            "gps_latitude": 19.0760,
            "gps_longitude": 72.8777,
        },
        "inspector": {"name": "Officer Sharma", "badge_number": "LM-MH-102"},
        "product": {
            "product_name": "Sunflower Oil 1L",
            "mrp_value": 140.0,
            "mrp_inclusive_taxes_declared": True,
            "net_quantity_value": 1.0,
            "net_quantity_unit": "l",
        },
        "violations": [],
    }

    result_pdf = pdf_report_generator.generate_report(
        output_pdf_path=output_pdf,
        inspection_data=doc_data,
    )
    assert os.path.isfile(result_pdf)

    # Validate PDF magic header bytes
    with open(result_pdf, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-"


# ===========================================================================
# Test 4 — PDF Report With Violations Docket & Show Cause Notice
# ===========================================================================
def test_pdf_report_with_violations_docket(tmp_path):
    """PDF generator renders structured violation dockets and statutory directive."""
    output_pdf = str(tmp_path / "violation_report.pdf")
    doc_data = {
        "docket_number": "DOCKET-MH-2026-VIOLATION",
        "chain_of_custody_hash": "b" * 64,
        "qr_verification_token": "QR-LM-20260825-VIOLATION",
        "inspection": {
            "inspection_number": "INS-VIOL-001",
            "created_at": "25-08-2026 11:00",
            "compliance_status": "non_compliant",
            "district": "Pune",
            "state": "Maharashtra",
            "store_name": "Corner Grocery",
            "gps_latitude": 18.5204,
            "gps_longitude": 73.8567,
        },
        "inspector": {"name": "Officer Patil", "badge_number": "LM-MH-105"},
        "product": {"product_name": "Biscuits 500g", "mrp_value": 30.0},
        "violations": [
            {
                "rule_code": "LM_RULE_6_1_E_MRP",
                "section_violated": "Rule 6(1)(e) r/w Section 18",
                "statute_title": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "violation_title": "Omission of Inclusive of All Taxes",
                "violation_description": "Taxes phrase missing on retail pack.",
                "severity": "major",
                "estimated_fine": "Fine up to ₹25,000",
            }
        ],
    }

    result_pdf = pdf_report_generator.generate_report(
        output_pdf_path=output_pdf,
        inspection_data=doc_data,
    )
    assert os.path.isfile(result_pdf)
    assert os.path.getsize(result_pdf) > 2000


# ===========================================================================
# Test 5 — PDF Report With Compliant Product
# ===========================================================================
def test_pdf_report_with_compliant_product(tmp_path):
    """PDF generator renders green compliance certification box when 0 violations exist."""
    output_pdf = str(tmp_path / "compliant_report.pdf")
    doc_data = {
        "docket_number": "DOCKET-MH-2026-COMPLIANT",
        "chain_of_custody_hash": "c" * 64,
        "qr_verification_token": "QR-LM-20260825-COMPLIANT",
        "inspection": {
            "inspection_number": "INS-COMP-001",
            "compliance_status": "compliant",
            "district": "Nagpur",
            "state": "Maharashtra",
        },
        "inspector": {"name": "Officer Deshmukh"},
        "product": {"product_name": "Basmati Rice 5kg"},
        "violations": [],
    }

    result_pdf = pdf_report_generator.generate_report(
        output_pdf_path=output_pdf,
        inspection_data=doc_data,
    )
    assert os.path.isfile(result_pdf)
    assert os.path.getsize(result_pdf) > 1500


# ===========================================================================
# Test 6 — Report Service Updates Database Records
# ===========================================================================
def test_generate_report_service_updates_db(db_session: Session):
    """ReportService persists Report model and sets Inspection status to 'completed'."""
    # Seed inspector
    insp_user = db_session.query(User).filter(User.role == "inspector").first()

    insp = Inspection(
        inspection_number="INS-SVC-TEST-001",
        inspector_id=insp_user.id if insp_user else "mock-user-id",
        district="Thane",
        state="Maharashtra",
        status="validated",
        compliance_status="compliant",
    )
    db_session.add(insp)
    db_session.commit()

    prod = Product(
        inspection_id=str(insp.id),
        product_name="Atta 1kg",
        mrp_value=50.0,
        mrp_inclusive_taxes_declared=True,
    )
    db_session.add(prod)
    db_session.commit()

    result = report_service.generate_inspection_report(
        db=db_session,
        inspection_id=str(insp.id),
        user_id=str(insp_user.id) if insp_user else "mock-user",
    )

    assert result["inspection_id"] == str(insp.id)
    assert "DOCKET-" in result["docket_number"]
    assert len(result["chain_of_custody_hash"]) == 64
    assert result["qr_verification_token"].startswith("QR-LM-")

    # Verify DB updates
    db_session.refresh(insp)
    assert insp.status == "completed"
    assert insp.record_sha256_hash == result["chain_of_custody_hash"]
    assert insp.qr_verification_token == result["qr_verification_token"]

    saved_report = db_session.query(Report).filter(Report.inspection_id == str(insp.id)).first()
    assert saved_report is not None
    assert saved_report.docket_number == result["docket_number"]


# ===========================================================================
# Test 7 — POST /api/v1/inspections/{id}/report Endpoint (200)
# ===========================================================================
def test_post_generate_report_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """POST /inspections/{id}/report generates PDF report and returns 200."""
    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    inspector_id = me_resp.json()["data"]["id"]

    insp = Inspection(
        inspection_number="INS-API-REP-001",
        inspector_id=inspector_id,
        district="Mumbai",
        state="Maharashtra",
        status="validated",
        compliance_status="compliant",
    )
    db_session.add(insp)
    db_session.commit()

    prod = Product(
        inspection_id=str(insp.id),
        product_name="Test Tea 250g",
        mrp_value=120.0,
        mrp_inclusive_taxes_declared=True,
    )
    db_session.add(prod)
    db_session.commit()

    resp = client.post(
        f"/api/v1/inspections/{insp.id}/report",
        headers=inspector_token_headers,
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()

    assert data["inspection_id"] == str(insp.id)
    assert "pdf_download_url" in data
    assert "chain_of_custody_hash" in data


# ===========================================================================
# Test 8 — GET /api/v1/inspections/{id}/report/download Endpoint (200)
# ===========================================================================
def test_get_report_download_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """GET /inspections/{id}/report/download streams the PDF file."""
    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    inspector_id = me_resp.json()["data"]["id"]

    insp = Inspection(
        inspection_number="INS-API-DL-001",
        inspector_id=inspector_id,
        district="Mumbai",
        state="Maharashtra",
        status="validated",
        compliance_status="compliant",
    )
    db_session.add(insp)
    db_session.commit()

    prod = Product(
        inspection_id=str(insp.id),
        product_name="Salt 1kg",
        mrp_value=25.0,
        mrp_inclusive_taxes_declared=True,
    )
    db_session.add(prod)
    db_session.commit()

    # Generate report first
    gen_resp = client.post(
        f"/api/v1/inspections/{insp.id}/report",
        headers=inspector_token_headers,
    )
    assert gen_resp.status_code == 200

    # Download report
    dl_resp = client.get(
        f"/api/v1/inspections/{insp.id}/report/download",
        headers=inspector_token_headers,
    )
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert dl_resp.content.startswith(b"%PDF-")


# ===========================================================================
# Test 9 — Public GET /api/v1/inspections/verify/{qr_token} Endpoint (200)
# ===========================================================================
def test_public_qr_verification_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """Public verification endpoint returns authentic record snapshot without auth."""
    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    inspector_id = me_resp.json()["data"]["id"]

    insp = Inspection(
        inspection_number="INS-QR-VERIFY-001",
        inspector_id=inspector_id,
        district="Nashik",
        state="Maharashtra",
        status="validated",
        compliance_status="compliant",
    )
    db_session.add(insp)
    db_session.commit()

    prod = Product(
        inspection_id=str(insp.id),
        product_name="Pure Ghee 500ml",
        mrp_value=350.0,
    )
    db_session.add(prod)
    db_session.commit()

    # Generate report to assign qr_verification_token
    gen_resp = client.post(
        f"/api/v1/inspections/{insp.id}/report",
        headers=inspector_token_headers,
    )
    assert gen_resp.status_code == 200
    qr_token = gen_resp.json()["qr_verification_token"]

    # Public verification request WITHOUT auth headers
    verify_resp = client.get(f"/api/v1/inspections/verify/{qr_token}")
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()

    assert v_data["verified"] is True
    assert v_data["tamper_evident_status"] == "AUTHENTIC_RECORD"
    assert v_data["inspection_number"] == "INS-QR-VERIFY-001"
    assert v_data["compliance_status"] == "compliant"


# ===========================================================================
# Test 10 — Invalid QR Verification Token Returns 404
# ===========================================================================
def test_invalid_qr_verification_token_404(client: TestClient):
    """Non-existent QR token returns 404 Not Found."""
    resp = client.get("/api/v1/inspections/verify/NON-EXISTENT-TOKEN-9999")
    assert resp.status_code == 404
