"""
test_citizen_complaints.py
==========================
Stage 15 — Unit & API Tests for Citizen Grievance Gateway & AI Triage
"""

import pytest
import uuid
import random
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.citizen import _compute_ai_credibility
from app.schemas.citizen import CitizenComplaintCreate

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


# ── Unit Tests (Triage Logic) ────────────────────────────────────────────────

def test_high_credibility_score_calculation():
    req = CitizenComplaintCreate(
        citizen_name="Amitabh Verma",
        citizen_contact="amitabh@example.com",
        retailer_name="Metro Retail Mart",
        retailer_address="Plot 55, Nariman Point, Mumbai 400021",
        state="Maharashtra",
        district="Mumbai",
        violation_category="OVERCHARGING_MRP",
        complaint_description="The cashier charged Rs 250 for cooking oil with printed MRP of Rs 210.",
        charged_price=250.0,
    )
    score, notes = _compute_ai_credibility(req)
    assert score >= 80.0
    assert "Explicit overcharging" in notes
    assert "Full retailer street address" in notes


def test_minimal_credibility_score():
    req = CitizenComplaintCreate(
        citizen_contact="citizen@gmail.com",
        retailer_name="Small Kiosk",
        state="Delhi",
        district="Central Delhi",
        violation_category="MISSING_DECLARATIONS",
        complaint_description="Missing details.",
    )
    score, _ = _compute_ai_credibility(req)
    assert score <= 70.0


# ── API Tests ────────────────────────────────────────────────────────────────

def test_submit_citizen_complaint_201():
    payload = {
        "citizen_name": "Pooja Sharma",
        "citizen_contact": "pooja.sharma@example.com",
        "retailer_name": "Quick Supermart",
        "retailer_address": "Shop 4, Linking Road, Bandra, Mumbai 400050",
        "state": "Maharashtra",
        "district": "Mumbai",
        "violation_category": "DUAL_MRP",
        "complaint_description": "Found two conflicting MRP stickers on imported chocolates.",
        "charged_price": 350.0,
    }
    resp = client.post("/api/v1/citizen/complaints", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["ticket_number"].startswith("LM-CIT-2026-")
    assert data["status"] in ("TRIAGED", "SUBMITTED")
    assert data["ai_credibility_score"] > 50.0


def test_track_citizen_complaint_public_200():
    # Submit first
    payload = {
        "citizen_contact": "pooja@example.com",
        "retailer_name": "Test Bakery",
        "state": "Maharashtra",
        "district": "Pune",
        "violation_category": "EXPIRED_SALE",
        "complaint_description": "Bread was sold 3 days past the expiry date.",
        "charged_price": 45.0,
    }
    sub_resp = client.post("/api/v1/citizen/complaints", json=payload)
    assert sub_resp.status_code == 201
    ticket_num = sub_resp.json()["ticket_number"]

    # Public tracking (no auth header needed)
    track_resp = client.get(f"/api/v1/citizen/complaints/track/{ticket_num}")
    assert track_resp.status_code == 200
    data = track_resp.json()
    assert data["ticket_number"] == ticket_num
    assert data["retailer_name"] == "Test Bakery"
    assert data["status"] in ("SUBMITTED", "TRIAGED")


def test_track_nonexistent_ticket_404():
    resp = client.get("/api/v1/citizen/complaints/track/LM-CIT-2026-99999999")
    assert resp.status_code == 404


def test_officer_can_list_citizen_complaints_200():
    token = get_inspector_token()
    resp = client.get(
        "/api/v1/citizen/complaints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_filter_complaints_by_state_and_district():
    token = get_inspector_token()
    resp = client.get(
        "/api/v1/citizen/complaints?state=Maharashtra&district=Mumbai",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert "Maharashtra" in item["state"]


def test_officer_can_resolve_citizen_complaint_200():
    token = get_inspector_token()
    # Submit a complaint
    payload = {
        "citizen_contact": "complaint@user.com",
        "retailer_name": "Corner Store",
        "state": "Maharashtra",
        "district": "Mumbai",
        "violation_category": "OVERCHARGING_MRP",
        "complaint_description": "Charged 150 for 120 MRP juice.",
    }
    sub_resp = client.post("/api/v1/citizen/complaints", json=payload)
    ticket_num = sub_resp.json()["ticket_number"]

    # Resolve complaint
    resolve_resp = client.patch(
        f"/api/v1/citizen/complaints/{ticket_num}/resolve?resolution_notes=Issued formal statutory warning and seized overcharged stock.",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resolve_resp.status_code == 200
    data = resolve_resp.json()
    assert data["status"] == "RESOLVED"
    assert "formal statutory warning" in data["resolution_notes"]


def test_unauthenticated_cannot_list_officer_queue_401():
    resp = client.get("/api/v1/citizen/complaints")
    assert resp.status_code == 401


def test_invalid_resolution_on_missing_ticket_404():
    token = get_inspector_token()
    resp = client.patch(
        "/api/v1/citizen/complaints/LM-CIT-NONEXISTENT/resolve?resolution_notes=Test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
