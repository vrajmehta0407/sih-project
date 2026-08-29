"""
test_predictive_dispatch.py
===========================
Stage 20 — Unit & API Tests for Predictive Risk Heatmaps & Raid Route Dispatch
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.predictive_dispatch import RaidRouteDispatchRequest
from app.services.predictive_dispatch_service import predictive_dispatch_service
from app.db.session import SessionLocal

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


# ── Hotspot Analytics Tests ──────────────────────────────────────────────────

def test_predictive_hotspots_service_logic():
    db = SessionLocal()
    try:
        resp = predictive_dispatch_service.get_predictive_hotspots(db)
        assert resp.total_clusters_evaluated >= 4
        assert resp.national_vulnerability_average > 0.0
        assert len(resp.hotspots) >= 4
        assert resp.hotspots[0].market_vulnerability_index >= 50.0
    finally:
        db.close()


def test_predictive_hotspots_contains_mvi_and_clusters():
    db = SessionLocal()
    try:
        resp = predictive_dispatch_service.get_predictive_hotspots(db)
        mumbai_cluster = next((h for h in resp.hotspots if h.district == "Mumbai"), None)
        assert mumbai_cluster is not None
        assert mumbai_cluster.risk_level in ("CRITICAL", "HIGH")
        assert len(mumbai_cluster.recommended_action) > 10
    finally:
        db.close()


def test_predictive_hotspots_api_200():
    token = get_inspector_token()
    resp = client.get("/api/v1/dashboard/predictive-hotspots", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "hotspots" in data
    assert "national_vulnerability_average" in data
    assert len(data["hotspots"]) >= 4


def test_predictive_hotspots_requires_auth_401():
    resp = client.get("/api/v1/dashboard/predictive-hotspots")
    assert resp.status_code == 401


# ── Raid Route Dispatch Tests ────────────────────────────────────────────────

def test_raid_route_dispatch_service_logic():
    db = SessionLocal()
    try:
        req = RaidRouteDispatchRequest(
            state="Maharashtra",
            district="Mumbai",
            team_lead_email="inspector.mumbai@legalmetrology.gov.in",
            max_targets=4,
        )
        route = predictive_dispatch_service.plan_raid_route(db, req, "admin@legalmetrology.gov.in")
        assert route.dispatch_code.startswith("RAID-")
        assert route.total_stops == 4
        assert len(route.targets) == 4
        assert route.estimated_fine_recovery_inr > 0.0
        assert route.status == "DISPATCHED"
    finally:
        db.close()


def test_raid_route_dispatch_max_targets_enforced():
    db = SessionLocal()
    try:
        req = RaidRouteDispatchRequest(
            state="Delhi",
            district="Central Delhi",
            max_targets=2,
        )
        route = predictive_dispatch_service.plan_raid_route(db, req, "admin@gov.in")
        assert route.total_stops <= 2
        assert len(route.targets) <= 2
    finally:
        db.close()


def test_raid_route_dispatch_compounding_recovery_calculation():
    db = SessionLocal()
    try:
        req = RaidRouteDispatchRequest(
            state="Karnataka",
            district="Bengaluru Urban",
            max_targets=2,
        )
        route = predictive_dispatch_service.plan_raid_route(db, req, "admin@gov.in")
        expected_total = sum(t.predicted_compounding_recovery_inr for t in route.targets)
        assert route.estimated_fine_recovery_inr == expected_total
    finally:
        db.close()


def test_raid_route_dispatch_api_200():
    token = get_inspector_token()
    payload = {
        "state": "Maharashtra",
        "district": "Mumbai",
        "team_lead_email": "inspector.mumbai@legalmetrology.gov.in",
        "max_targets": 3,
        "focus_category": "ALL",
    }
    resp = client.post(
        "/api/v1/dashboard/dispatch-raid-route",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["dispatch_code"].startswith("RAID-")
    assert data["total_stops"] == 3
    assert len(data["targets"]) == 3
    assert data["estimated_duration_hours"] > 0.0


def test_raid_route_dispatch_custom_district():
    token = get_inspector_token()
    payload = {
        "state": "West Bengal",
        "district": "Kolkata",
        "max_targets": 2,
    }
    resp = client.post(
        "/api/v1/dashboard/dispatch-raid-route",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["district"] == "Kolkata"
    assert data["total_stops"] == 2


def test_raid_route_dispatch_requires_inspector_auth():
    payload = {
        "state": "Maharashtra",
        "district": "Mumbai",
        "max_targets": 3,
    }
    resp = client.post("/api/v1/dashboard/dispatch-raid-route", json=payload)
    assert resp.status_code == 401
