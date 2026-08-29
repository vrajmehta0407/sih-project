"""
test_grand_finale.py
====================
Stage 30 — Unit & API Tests for SIH 2026 Grand Finale Demo Simulator
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.grand_finale import DemoScenarioRequest
from app.services.grand_finale_service import grand_finale_service

client = TestClient(app)


# ── Grand Finale Service Unit Tests ─────────────────────────────────────────

def test_grand_finale_simulation_runs_15_steps():
    req = DemoScenarioRequest(
        scenario_id="FULL_PIPELINE",
        officer_name="Inspector Test Kumar",
        target_shop="Test Supermarket, Mumbai",
        product_label_type="PACKAGED_CEREAL_OVERCHARGE",
    )
    res = grand_finale_service.run_simulation(req)
    assert res.total_steps == 15
    assert len(res.pipeline_steps) == 15


def test_grand_finale_simulation_id_format():
    req = DemoScenarioRequest()
    res = grand_finale_service.run_simulation(req)
    assert res.simulation_id.startswith("SIH2026-DEMO-")


def test_grand_finale_steps_passed_and_flagged_count():
    req = DemoScenarioRequest()
    res = grand_finale_service.run_simulation(req)
    assert res.steps_passed + res.steps_flagged == res.total_steps


def test_grand_finale_all_steps_have_sha256_seals():
    req = DemoScenarioRequest()
    res = grand_finale_service.run_simulation(req)
    for step in res.pipeline_steps:
        assert len(step.sha256_seal) == 64


def test_grand_finale_jury_scorecard_total_96():
    req = DemoScenarioRequest()
    res = grand_finale_service.run_simulation(req)
    assert res.jury_scorecard["total_score"] == 96.0
    assert res.jury_scorecard["grade"] == "S+"


def test_grand_finale_jury_commendations_count():
    req = DemoScenarioRequest()
    res = grand_finale_service.run_simulation(req)
    assert len(res.jury_scorecard["commendations"]) >= 5


def test_grand_finale_master_seal_sha256_length():
    req = DemoScenarioRequest()
    res = grand_finale_service.run_simulation(req)
    assert len(res.master_simulation_seal) == 64


def test_grand_finale_get_simulation_by_id():
    req = DemoScenarioRequest(officer_name="Inspector Cache Test")
    res = grand_finale_service.run_simulation(req)
    cached = grand_finale_service.get_simulation(res.simulation_id)
    assert cached is not None
    assert cached.simulation_id == res.simulation_id


# ── Grand Finale API Tests ───────────────────────────────────────────────────

def test_grand_finale_run_api_200():
    payload = {
        "scenario_id": "FULL_PIPELINE",
        "officer_name": "Inspector API Test",
        "target_shop": "API Test Supermarket, Mumbai",
        "product_label_type": "PACKAGED_CEREAL_OVERCHARGE",
    }
    resp = client.post("/api/v1/grand-finale/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "simulation_id" in data
    assert data["total_steps"] == 15
    assert data["jury_scorecard"]["total_score"] == 96.0


def test_grand_finale_jury_scorecard_api_200():
    resp = client.get("/api/v1/grand-finale/jury-scorecard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_score"] == 96.0
    assert data["grade"] == "S+"
    assert "commendations" in data
    assert "platform_stats" in data
    assert data["platform_stats"]["total_stages_built"] == 30
