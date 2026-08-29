import io
import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient
from app.core.config import settings

def _make_jpeg_bytes(width: int = 400, height: int = 300) -> bytes:
    img = np.full((height, width, 3), (240, 240, 240), dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (380, 80), (20, 20, 20), -1)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()

def _create_test_inspection(client: TestClient, headers: dict) -> str:
    """Helper to create an inspection docket and return its ID."""
    jpeg_bytes = _make_jpeg_bytes()
    files = [("images", ("test_pkg.jpg", jpeg_bytes, "image/jpeg"))]
    data = {
        "district": "Pune",
        "state": "Maharashtra",
        "store_name": "Adjudication Test Store",
        "sides": ["front"]
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/", data=data, files=files, headers=headers)
    assert resp.status_code == 201, f"Create inspection failed: {resp.text}"
    return resp.json()["id"]


def test_adjudicate_compound_offence_success(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "COMPOUND_OFFENCE",
        "compounding_amount": 25000.0,
        "receipt_number": "TR-MH-2026-9901",
        "order_number": "CMP-ORD-2026-0842",
        "adjudication_notes": "First offence compounded under Section 48 upon full payment."
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["adjudication_status"] == "compounded"
    assert data["compounding_amount"] == 25000.0
    assert data["receipt_number"] == "TR-MH-2026-9901"
    assert data["compounding_order_number"] == "CMP-ORD-2026-0842"


def test_adjudicate_refer_to_court_success(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "REFER_TO_COURT",
        "court_jurisdiction": "Chief Judicial Magistrate Court, Pune",
        "order_number": "CRT-REF-2026-0104",
        "adjudication_notes": "Refused to compound; prosecution initiated under Section 36(2)."
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["adjudication_status"] == "court_referred"
    assert data["court_jurisdiction"] == "Chief Judicial Magistrate Court, Pune"


def test_adjudicate_issue_show_cause_success(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "ISSUE_SHOW_CAUSE",
        "order_number": "SCN-2026-0881",
        "adjudication_notes": "15-day statutory Show Cause notice dispatched to manufacturer."
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["adjudication_status"] == "notice_issued"


def test_adjudicate_close_with_warning_success(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "CLOSE_WITH_WARNING",
        "adjudication_notes": "Minor clerical omission corrected on the spot. Warning issued."
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["adjudication_status"] == "closed_warning"


def test_adjudicate_compounding_amount_persistence(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "COMPOUND_OFFENCE",
        "compounding_amount": 50000.0,
        "receipt_number": "CHALLAN-9921"
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    assert resp.json()["compounding_amount"] == 50000.0


def test_adjudicate_treasury_receipt_tracking(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "COMPOUND_OFFENCE",
        "receipt_number": "SBI-EPAY-2026-883921"
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    assert resp.json()["receipt_number"] == "SBI-EPAY-2026-883921"


def test_adjudicate_court_jurisdiction_recording(client: TestClient, inspector_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "REFER_TO_COURT",
        "court_jurisdiction": "Metropolitan Magistrate Court 5, Mumbai"
    }
    resp = client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 200
    assert resp.json()["court_jurisdiction"] == "Metropolitan Magistrate Court 5, Mumbai"


def test_adjudicate_audit_log_created(client: TestClient, inspector_token_headers: dict, admin_token_headers: dict):
    insp_id = _create_test_inspection(client, inspector_token_headers)
    payload = {
        "action": "COMPOUND_OFFENCE",
        "compounding_amount": 10000.0
    }
    client.post(f"{settings.API_V1_STR}/inspections/{insp_id}/adjudicate", json=payload, headers=inspector_token_headers)

    # Check audit log via admin API
    audit_resp = client.get(f"{settings.API_V1_STR}/audit-logs?action=ADJUDICATION_ACTION", headers=admin_token_headers)
    assert audit_resp.status_code == 200
    items = audit_resp.json()["items"]
    assert any(item["entity_id"] == insp_id for item in items)


def test_adjudicate_unauthorized_access_401(client: TestClient):
    payload = {"action": "COMPOUND_OFFENCE", "compounding_amount": 5000.0}
    resp = client.post(f"{settings.API_V1_STR}/inspections/fake-uuid-123/adjudicate", json=payload)
    assert resp.status_code == 401


def test_adjudicate_nonexistent_inspection_404(client: TestClient, inspector_token_headers: dict):
    payload = {"action": "COMPOUND_OFFENCE", "compounding_amount": 5000.0}
    resp = client.post(f"{settings.API_V1_STR}/inspections/00000000-0000-0000-0000-000000000000/adjudicate", json=payload, headers=inspector_token_headers)
    assert resp.status_code == 404
