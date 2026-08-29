"""
test_notice_and_export.py
=========================
Stage 14 — Unit & API Tests for Notice Dispatcher, State Overrides & Data Export
"""

import pytest
import uuid
import random
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.notice import NoticeDispatchRequest
from app.services.notice_dispatcher_service import notice_dispatcher_service

client = TestClient(app)

INSPECTOR_TOKEN = None
ADMIN_TOKEN = None


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


# ── Notice Dispatcher Tests ──────────────────────────────────────────────────

def test_notice_dispatch_service_logic():
    req = NoticeDispatchRequest(
        recipient_name="Grievance Officer",
        recipient_email="grievance@packagedfoods.com",
        recipient_phone="+919876543210",
        compliance_deadline_days=7,
        officer_remarks="Mandatory MRP with tax declaration required.",
    )
    # Mock inspection object
    class MockInspection:
        id = uuid.uuid4()
        inspection_number = "INS-TEST-001"
        product = None
        extracted_declarations = {}
        violations = []
        report = None

    resp = notice_dispatcher_service.dispatch(MockInspection(), req, "officer@gov.in")
    assert resp.delivery_status == "DISPATCHED"
    assert resp.recipient_email == "grievance@packagedfoods.com"
    assert resp.tracking_token.startswith("NT-")
    assert resp.compliance_deadline is not None


def test_notice_dispatch_custom_deadline():
    req = NoticeDispatchRequest(
        compliance_deadline_days=15,
        recipient_email="compliance@fmcg.com",
    )
    class MockInspection:
        id = uuid.uuid4()
        inspection_number = "INS-TEST-002"
        product = None
        extracted_declarations = {}
        violations = []
        report = None

    resp = notice_dispatcher_service.dispatch(MockInspection(), req, "officer@gov.in")
    days_delta = (resp.compliance_deadline - resp.dispatched_at.date()).days
    assert days_delta in (14, 15)  # depending on timezone transition


def test_notice_dispatch_nonexistent_inspection_404():
    token = get_inspector_token()
    random_id = str(uuid.uuid4())
    resp = client.post(
        f"/api/v1/inspections/{random_id}/dispatch-notice",
        json={"recipient_email": "test@mfg.com", "compliance_deadline_days": 7},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_notice_dispatch_api_success():
    token = get_inspector_token()
    # Fetch list of existing inspections
    resp = client.get(
        "/api/v1/inspections/?limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    inspections = resp.json().get("inspections", [])
    if inspections:
        insp_id = inspections[0]["id"]
        dispatch_resp = client.post(
            f"/api/v1/inspections/{insp_id}/dispatch-notice",
            json={"recipient_email": "manufacturer.grievance@packagedgoods.in", "compliance_deadline_days": 7},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert dispatch_resp.status_code == 200
        data = dispatch_resp.json()
        assert data["delivery_status"] == "DISPATCHED"
        assert data["tracking_token"].startswith("NT-")


# ── State Rule Override Tests ────────────────────────────────────────────────

def test_create_state_override_api_201():
    token = get_admin_token()
    state_code = f"S{random.randint(10, 99)}"
    payload = {
        "state_code": state_code,
        "state_name": "Test State",
        "rule_code": "RULE_6_1_E_MRP",
        "override_type": "MANDATORY_LOCAL_LANG",
        "description": "Mandatory local language script for retail price declarations",
        "gazette_notification_ref": "State Gazette Ref 2026/01",
        "is_active": True,
    }
    resp = client.post(
        "/api/v1/rules/state-overrides",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["state_code"] == state_code
    assert data["override_type"] == "MANDATORY_LOCAL_LANG"


def test_list_state_overrides_api_200():
    token = get_inspector_token()
    resp = client.get(
        "/api/v1/rules/state-overrides",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_filter_state_overrides_by_state_code():
    token = get_admin_token()
    unique_code = f"MH{random.randint(100, 999)}"
    payload = {
        "state_code": unique_code,
        "state_name": "Maharashtra",
        "rule_code": "RULE_6_1_C_NET_QTY",
        "override_type": "EXEMPTION",
        "description": "Small artisan packaging exemption under 10g",
    }
    client.post(
        "/api/v1/rules/state-overrides",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    # Query filtered
    resp = client.get(
        f"/api/v1/rules/state-overrides?state_code={unique_code}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    assert data[0]["state_code"] == unique_code


# ── Data Export Tests ────────────────────────────────────────────────────────

def test_export_inspections_csv_200():
    token = get_inspector_token()
    resp = client.get(
        "/api/v1/dashboard/export/csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "Inspection ID" in resp.text
    assert "Compliance Status" in resp.text


def test_export_inspections_json_200():
    token = get_inspector_token()
    resp = client.get(
        "/api/v1/dashboard/export/json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_records" in data
    assert "records" in data
    assert isinstance(data["records"], list)


def test_export_requires_auth():
    resp_csv = client.get("/api/v1/dashboard/export/csv")
    assert resp_csv.status_code == 401

    resp_json = client.get("/api/v1/dashboard/export/json")
    assert resp_json.status_code == 401
