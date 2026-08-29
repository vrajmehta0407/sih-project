"""
test_jurisdiction_transfer.py
=============================
Stage 21 — Unit & API Tests for Cross-State Case Transfer & Joint Officer Co-Signing
"""

import pytest
import uuid
import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.schemas.jurisdiction_transfer import (
    JurisdictionTransferRequest,
    OfficerCoSignRequest,
)
from app.services.jurisdiction_transfer_service import jurisdiction_transfer_service
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
    files = [("images", ("test_sample.jpg", buf.tobytes(), "image/jpeg"))]
    data = {
        "district": "Mumbai",
        "state": "Maharashtra",
        "store_name": "Jurisdiction Test Mart",
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


# ── Jurisdiction Transfer Tests ──────────────────────────────────────────────

def test_jurisdiction_transfer_service_logic():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        assert insp is not None
        req = JurisdictionTransferRequest(
            target_state="Gujarat",
            target_district="Anand",
            transfer_reason="Manufacturing unit located in Anand; Section 49 jurisdiction invoked.",
            transfer_urgency="HIGH",
        )
        res = jurisdiction_transfer_service.transfer_case(
            db=db,
            inspection=insp,
            req=req,
            transferring_officer_email="inspector.mumbai@legalmetrology.gov.in",
        )
        assert res.transfer_memo_number.startswith("LM-TRF-2026-")
        assert res.target_state == "Gujarat"
        assert res.target_district == "Anand"
        assert len(res.chain_of_custody_hash) == 64
        assert res.transfer_status == "TRANSFERRED"
    finally:
        db.close()


def test_jurisdiction_transfer_custody_hash_length():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req = JurisdictionTransferRequest(
            target_state="Delhi",
            target_district="Central Delhi",
            transfer_reason="Packer headquarters registered in Delhi.",
        )
        res = jurisdiction_transfer_service.transfer_case(
            db=db,
            inspection=insp,
            req=req,
            transferring_officer_email="inspector.mumbai@legalmetrology.gov.in",
        )
        assert len(res.chain_of_custody_hash) == 64
        assert "Section 49" in res.official_statutory_note
    finally:
        db.close()


def test_jurisdiction_transfer_updates_inspection_state():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        old_notes_len = len(insp.inspector_notes or "")
        req = JurisdictionTransferRequest(
            target_state="Karnataka",
            target_district="Bengaluru Urban",
            transfer_reason="Inter-state distribution audit.",
        )
        jurisdiction_transfer_service.transfer_case(
            db=db,
            inspection=insp,
            req=req,
            transferring_officer_email="officer@gov.in",
        )
        assert insp.state == "Karnataka"
        assert len(insp.inspector_notes) > old_notes_len
    finally:
        db.close()


def test_jurisdiction_transfer_api_200():
    insp_id = _create_test_inspection()
    token = get_inspector_token()
    payload = {
        "target_state": "Gujarat",
        "target_district": "Surat",
        "transfer_reason": "Factory origin violation under Section 49.",
        "transfer_urgency": "HIGH",
    }
    trf_resp = client.post(
        f"/api/v1/inspections/{insp_id}/transfer-jurisdiction",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert trf_resp.status_code == 200
    data = trf_resp.json()
    assert data["transfer_memo_number"].startswith("LM-TRF-2026-")
    assert data["target_state"] == "Gujarat"


def test_jurisdiction_transfer_nonexistent_inspection_404():
    token = get_inspector_token()
    payload = {
        "target_state": "Gujarat",
        "target_district": "Surat",
        "transfer_reason": "Test",
    }
    resp = client.post(
        "/api/v1/inspections/00000000-0000-0000-0000-000000000000/transfer-jurisdiction",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ── Joint Officer Co-Signature Tests ─────────────────────────────────────────

def test_officer_co_sign_service_logic():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req = OfficerCoSignRequest(
            co_investigator_name="Inspector Vikram Rathore",
            co_investigator_badge_number="MH-LM-INSP-4042",
            co_investigator_remarks="Corroborated physical label measurements on spot.",
        )
        res = jurisdiction_transfer_service.co_sign_docket(db, insp, req)
        assert res.co_investigator_name == "Inspector Vikram Rathore"
        assert res.co_investigator_badge_number == "MH-LM-INSP-4042"
        assert len(res.co_signature_seal) == 64
        assert res.total_co_signers >= 1
    finally:
        db.close()


def test_officer_co_sign_seal_integrity():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req = OfficerCoSignRequest(
            co_investigator_name="Deputy Controller Anita Roy",
            co_investigator_badge_number="DL-LM-DC-1090",
            co_investigator_remarks="Joint inspection confirmed non-declaration of USP.",
        )
        res = jurisdiction_transfer_service.co_sign_docket(db, insp, req)
        assert res.co_signature_seal is not None
        assert len(res.co_signature_seal) == 64
    finally:
        db.close()


def test_officer_co_sign_increments_count():
    insp_id = _create_test_inspection()
    db = SessionLocal()
    try:
        insp = db.query(Inspection).filter(Inspection.id == insp_id).first()
        req = OfficerCoSignRequest(
            co_investigator_name="Inspector R. K. Nair",
            co_investigator_badge_number="KA-LM-INSP-9081",
            co_investigator_remarks="Third corroborating witness on joint taskforce.",
        )
        res = jurisdiction_transfer_service.co_sign_docket(db, insp, req)
        assert res.total_co_signers >= 1
    finally:
        db.close()


def test_officer_co_sign_api_200():
    insp_id = _create_test_inspection()
    token = get_inspector_token()
    payload = {
        "co_investigator_name": "Inspector S. K. Deshmukh",
        "co_investigator_badge_number": "MH-LM-INSP-7712",
        "co_investigator_remarks": "Witnessed retail test purchase and overcharging evidence.",
    }
    cosign_resp = client.post(
        f"/api/v1/inspections/{insp_id}/co-sign",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cosign_resp.status_code == 200
    data = cosign_resp.json()
    assert data["co_investigator_name"] == "Inspector S. K. Deshmukh"
    assert len(data["co_signature_seal"]) == 64


def test_officer_co_sign_requires_inspector_auth_401():
    payload = {
        "co_investigator_name": "Test Officer",
        "co_investigator_badge_number": "TEST-01",
        "co_investigator_remarks": "Test remarks",
    }
    resp = client.post(
        "/api/v1/inspections/00000000-0000-0000-0000-000000000000/co-sign",
        json=payload,
    )
    assert resp.status_code == 401
