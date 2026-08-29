"""
test_regulatory_copilot.py
==========================
Stage 25 — Unit & API Tests for National AI Regulatory Copilot & Statutory Legal Chat
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.copilot import CopilotQueryRequest
from app.services.regulatory_copilot_service import regulatory_copilot_service

client = TestClient(app)


# ── AI Regulatory Copilot Unit Tests ─────────────────────────────────────────

def test_copilot_service_usp_exemption_query():
    req = CopilotQueryRequest(query="Is Unit Sale Price mandatory for packages under 10 grams?")
    res = regulatory_copilot_service.query(req)
    assert res.detected_intent == "USP_EXEMPTION_RULES"
    assert "Rule 6(11)" in res.legal_opinion
    assert len(res.citations) >= 1
    assert any(c.section_or_rule_no == "Rule 6(11)" for c in res.citations)
    assert res.is_compoundable is True


def test_copilot_service_ecommerce_rule_6_10():
    req = CopilotQueryRequest(query="What are the rules for e-commerce platforms like Amazon or Blinkit under Rule 6(10)?")
    res = regulatory_copilot_service.query(req)
    assert res.detected_intent == "ECOMMERCE_RULE_6_10"
    assert "Rule 6(10)" in res.legal_opinion
    assert "digital marketplace" in res.legal_opinion.lower()
    assert len(res.recommended_officer_actions) >= 2


def test_copilot_service_font_height_schedule():
    req = CopilotQueryRequest(query="What is the minimum font height required on the principal display panel under First Schedule?")
    res = regulatory_copilot_service.query(req)
    assert res.detected_intent == "FONT_HEIGHT_SCHEDULE"
    assert "First Schedule" in res.legal_opinion
    assert "1.0 mm" in res.legal_opinion
    assert "4.0 mm" in res.legal_opinion


def test_copilot_service_overcharging_and_recidivism():
    req = CopilotQueryRequest(query="What is the fine for retail overcharging above MRP for a second offence under Section 36?")
    res = regulatory_copilot_service.query(req)
    assert res.detected_intent == "OVERCHARGING_AND_DUAL_MRP"
    assert "Section 18" in res.legal_opinion
    assert "Section 36(2)" in res.penalty_implications or "imprisonment" in res.penalty_implications.lower()


def test_copilot_service_general_guidance():
    req = CopilotQueryRequest(query="Tell me about packaging standards in India")
    res = regulatory_copilot_service.query(req)
    assert res.detected_intent == "GENERAL_STATUTORY_GUIDANCE"
    assert "7 mandatory declarations" in res.legal_opinion
    assert len(res.citations) >= 1


# ── AI Regulatory Copilot API Endpoints Tests ────────────────────────────────

def test_copilot_query_api_200_usp():
    payload = {
        "query": "Is USP required on small 5g shampoo sachet?",
        "jurisdiction_state": "Maharashtra",
        "target_audience": "OFFICER",
    }
    resp = client.post("/api/v1/copilot/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_intent"] == "USP_EXEMPTION_RULES"
    assert "Rule 6(11)" in data["legal_opinion"]
    assert "citations" in data
    assert len(data["citations"]) >= 1


def test_copilot_query_api_200_ecommerce():
    payload = {
        "query": "Who is liable for missing MRP on quick commerce marketplace?",
        "jurisdiction_state": "Delhi",
    }
    resp = client.post("/api/v1/copilot/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_intent"] == "ECOMMERCE_RULE_6_10"
    assert "Rule 6(10)" in data["legal_opinion"]


def test_copilot_query_api_response_structure():
    payload = {
        "query": "What are the rules regarding dual mrp stickers?",
    }
    resp = client.post("/api/v1/copilot/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "query" in data
    assert "legal_opinion" in data
    assert "citations" in data
    assert "penalty_implications" in data
    assert "recommended_officer_actions" in data
    assert "is_compoundable" in data
    assert "created_at" in data


def test_copilot_suggested_prompts_api_200():
    resp = client.get("/api/v1/copilot/suggested-prompts")
    assert resp.status_code == 200
    prompts = resp.json()
    assert isinstance(prompts, list)
    assert len(prompts) >= 4
    assert any("Unit Sale Price" in p for p in prompts)


def test_copilot_compoundable_flag_set_appropriately():
    req = CopilotQueryRequest(query="Can I compound a Rule 6 infraction under Section 48?")
    res = regulatory_copilot_service.query(req)
    assert res.is_compoundable is True
