"""
test_challan_settlement.py
==========================
Stage 23 — Unit & API Tests for Section 48 e-Challan & Compounding Settlement Portal
"""

import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.schemas.challan import ChallanGenerateRequest, ChallanSettlementRequest
from app.services.challan_service import challan_service
from app.db.session import SessionLocal
from app.models.inspection import Inspection

client = TestClient(app)

INSPECTOR_TOKEN = None


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


def _create_test_inspection() -> str:
    """Helper to create a fresh test inspection and return its ID."""
    token = get_inspector_token()
    img = np.full((300, 400, 3), (240, 240, 240), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    files = [("images", ("test_pkg.jpg", buf.tobytes(), "image/jpeg"))]
    data = {
        "district": "Mumbai",
        "state": "Maharashtra",
        "store_name": "Challan Settlement Test Supermarket",
        "sides": ["front"]
    }
    resp = client.post(
        f"{settings.API_V1_STR}/inspections/",
        data=data,
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── e-Challan Generation Tests ───────────────────────────────────────────────

def test_challan_generation_service_logic():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        assert insp is not None
        req = ChallanGenerateRequest(
            compounding_fee=25000.0,
            offence_description="Violation of Rule 6(1)(e) - Overcharging above printed MRP.",
            violator_entity_name="Metro Cash & Carry India",
            violator_gstin="27AABCM1234F1Z9",
            due_days=30,
        )
        res = challan_service.generate_challan(db, insp, req)
        assert res.challan_number.startswith("CHALLAN-")
        assert res.compounding_amount == 25000.0
        assert res.status == "ISSUED"
        assert res.violator_entity_name == "Metro Cash & Carry India"
    finally:
        db.close()


def test_challan_upi_intent_payload():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req = ChallanGenerateRequest(
            compounding_fee=50000.0,
            offence_description="Second offence under Section 36(1) for missing mandatory declarations.",
            violator_entity_name="Fresh Food Products Ltd",
            due_days=15,
        )
        res = challan_service.generate_challan(db, insp, req)
        assert "upi://pay" in res.payment_upi_intent
        assert "50000.00" in res.payment_upi_intent
        assert "legalmetrology.treasury@gov.in" in res.payment_upi_intent
    finally:
        db.close()


def test_challan_updates_inspection_record():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req = ChallanGenerateRequest(
            compounding_fee=20000.0,
            offence_description="Non-standard package size violation under Rule 5.",
            violator_entity_name="Quality Foods LLP",
        )
        res = challan_service.generate_challan(db, insp, req)
        assert insp.compounding_order_number == res.challan_number
        assert insp.compounding_amount == 20000.0
        assert insp.adjudication_status == "notice_issued"
    finally:
        db.close()


# ── e-Challan Settlement & Discharge Tests ───────────────────────────────────

def test_challan_settlement_service_logic():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req_gen = ChallanGenerateRequest(
            compounding_fee=25000.0,
            offence_description="Rule 6 MRP infraction.",
            violator_entity_name="Apex Supermarket",
        )
        challan_service.generate_challan(db, insp, req_gen)

        req_settle = ChallanSettlementRequest(
            payment_mode="UPI",
            transaction_reference="UPI-NPCI-2026-8819203910",
            payer_name="Apex Supermarket",
            payer_bank="HDFC Bank",
        )
        res = challan_service.settle_challan(db, insp, req_settle)
        assert res.status == "SETTLED"
        assert res.transaction_reference == "UPI-NPCI-2026-8819203910"
        assert res.discharge_certificate_seal is not None
        assert len(res.discharge_certificate_seal) == 64
    finally:
        db.close()


def test_challan_discharge_seal_integrity():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req_settle = ChallanSettlementRequest(
            payment_mode="NETBANKING",
            transaction_reference="NET-SBI-2026-772910",
            payer_name="City Stores",
        )
        res = challan_service.settle_challan(db, insp, req_settle)
        assert len(res.discharge_certificate_seal) == 64
        assert "Compounding Discharge Complete" in res.official_legal_notice
    finally:
        db.close()


def test_challan_settlement_updates_inspection_status():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req_settle = ChallanSettlementRequest(
            payment_mode="TREASURY_CHALLAN",
            transaction_reference="TR-MAH-2026-0091",
            payer_name="Global Trade Corp",
        )
        challan_service.settle_challan(db, insp, req_settle)
        assert insp.adjudication_status == "compounded"
        assert insp.compounding_receipt_number == "TR-MAH-2026-0091"
        assert insp.adjudicated_at is not None
    finally:
        db.close()


# ── e-Challan API Endpoints Tests ────────────────────────────────────────────

def test_challan_generate_api_200():
    insp_id = _create_test_inspection()
    token = get_inspector_token()
    payload = {
        "compounding_fee": 30000.0,
        "offence_description": "Absence of consumer care helpline and e-mail on pre-packaged goods.",
        "violator_entity_name": "Modern Packaging Ltd",
        "violator_gstin": "27AABCM9988A1Z1",
        "due_days": 30,
    }
    resp = client.post(
        f"/api/v1/inspections/{insp_id}/challan/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["challan_number"].startswith("CHALLAN-")
    assert data["compounding_amount"] == 30000.0
    assert data["status"] == "ISSUED"


def test_challan_settle_api_200():
    insp_id = _create_test_inspection()
    token = get_inspector_token()
    # First generate challan
    client.post(
        f"/api/v1/inspections/{insp_id}/challan/generate",
        json={
            "compounding_fee": 25000.0,
            "offence_description": "Test offence",
            "violator_entity_name": "Test Entity",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    # Settle
    settle_payload = {
        "payment_mode": "UPI",
        "transaction_reference": "UPI-SETTLE-TEST-9999",
        "payer_name": "Test Entity",
        "payer_bank": "ICICI Bank",
    }
    resp = client.post(
        f"/api/v1/inspections/{insp_id}/challan/settle",
        json=settle_payload,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SETTLED"
    assert data["transaction_reference"] == "UPI-SETTLE-TEST-9999"


def test_challan_get_status_api_200():
    insp_id = _create_test_inspection()
    resp = client.get(f"/api/v1/inspections/{insp_id}/challan")
    assert resp.status_code == 200
    data = resp.json()
    assert "challan_number" in data
    assert "compounding_amount" in data
    assert "status" in data


def test_challan_generate_requires_inspector_auth_401():
    payload = {
        "compounding_fee": 25000.0,
        "offence_description": "Unauthenticated attempt",
        "violator_entity_name": "Test",
    }
    resp = client.post(
        "/api/v1/inspections/00000000-0000-0000-0000-000000000000/challan/generate",
        json=payload,
    )
    assert resp.status_code == 401
