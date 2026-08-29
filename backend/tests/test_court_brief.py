"""
test_court_brief.py
===================
Stage 28 — Unit & API Tests for Pre-Trial Court Evidence Brief & Sec 65B Certificate
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.court_brief import (
    CourtBriefGenerateRequest,
    AccusedEntityDetails,
)
from app.services.court_brief_service import court_brief_service

client = TestClient(app)


# ── Court Brief Service Unit Tests ──────────────────────────────────────────

def test_court_brief_service_logic():
    req = CourtBriefGenerateRequest(
        case_title="State vs. Test Retail Ltd.",
        court_name="Court of CJM, Mumbai",
        jurisdiction_district="Mumbai Suburban",
        complainant_officer_name="Inspector R. Kumar",
        accused=AccusedEntityDetails(
            company_name="Test Retail Ltd.",
            registered_address="Bandra, Mumbai",
            managing_director_name="Mr. A. Sharma",
        ),
        offence_summary="Overcharging under Section 18 read with Section 36(2).",
    )
    res = court_brief_service.generate_brief(req)
    assert res.dossier_id.startswith("COURT-BRIEF-2026-")
    assert res.case_title == "State vs. Test Retail Ltd."
    assert len(res.statement_of_facts) >= 5
    assert len(res.exhibits_inventory) >= 4


def test_court_brief_statement_of_facts():
    req = CourtBriefGenerateRequest(
        accused=AccusedEntityDetails(
            company_name="Alpha Corp",
            registered_address="Nariman Point, Mumbai",
            managing_director_name="John Doe",
        ),
        offence_summary="Tampered price stickers.",
    )
    res = court_brief_service.generate_brief(req)
    facts_text = " ".join(res.statement_of_facts)
    assert "Section 15" in facts_text
    assert "Section 48" in facts_text
    assert "Alpha Corp" in facts_text


def test_court_brief_exhibits_inventory_hashes():
    req = CourtBriefGenerateRequest(
        accused=AccusedEntityDetails(
            company_name="Beta Logistics",
            registered_address="Andheri, Mumbai",
            managing_director_name="Jane Doe",
        ),
        offence_summary="Missing country of origin.",
    )
    res = court_brief_service.generate_brief(req)
    assert any(ex.exhibit_number == "Exhibit P-1" for ex in res.exhibits_inventory)
    assert all(len(ex.sha256_hash) == 64 for ex in res.exhibits_inventory)


def test_court_brief_statutory_prayer():
    req = CourtBriefGenerateRequest(
        accused=AccusedEntityDetails(
            company_name="Gamma Foods",
            registered_address="Thane West",
            managing_director_name="V. K. Singh",
        ),
        offence_summary="Deficient net quantity.",
    )
    res = court_brief_service.generate_brief(req)
    assert "WHEREFORE" in res.statutory_prayer_to_magistrate
    assert "Section 36(2)" in res.statutory_prayer_to_magistrate


def test_court_brief_section_65b_affidavit():
    req = CourtBriefGenerateRequest(
        complainant_officer_name="Inspector S. Verma",
        accused=AccusedEntityDetails(
            company_name="Delta Stores",
            registered_address="Pune Station Rd",
            managing_director_name="R. Patil",
        ),
        offence_summary="Non-standard packaging.",
    )
    res = court_brief_service.generate_brief(req)
    assert "BHARATIYA SAKSHYA ADHINIYAM, 2023" in res.section_65b_bsa_affidavit_text
    assert "Inspector S. Verma" in res.section_65b_bsa_affidavit_text


def test_court_brief_master_seal_hash():
    req = CourtBriefGenerateRequest(
        accused=AccusedEntityDetails(
            company_name="Epsilon Mart",
            registered_address="Kurla, Mumbai",
            managing_director_name="M. Khan",
        ),
        offence_summary="Dual MRP.",
    )
    res = court_brief_service.generate_brief(req)
    assert len(res.master_court_seal_hash) == 64  # SHA-256


# ── Court Brief API Endpoints Tests ─────────────────────────────────────────

def test_generate_court_brief_api_200():
    payload = {
        "case_title": "State of Maharashtra vs. MegaMart Retail Ltd.",
        "court_name": "Court of Chief Judicial Magistrate, Mumbai",
        "jurisdiction_district": "Mumbai City",
        "complainant_officer_name": "Inspector Rajesh Kumar",
        "accused": {
            "company_name": "MegaMart Retail Ltd.",
            "registered_address": "Fort, Mumbai 400001",
            "managing_director_name": "Sunil Mittal",
            "cin_number": "U52100MH2020PTC123456",
        },
        "offence_summary": "Recidivist overcharging under Section 18 read with Section 36(2).",
    }
    resp = client.post("/api/v1/court-brief/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "dossier_id" in data
    assert data["dossier_id"].startswith("COURT-BRIEF-2026-")
    assert len(data["exhibits_inventory"]) >= 4


def test_generate_court_brief_api_schema():
    payload = {
        "case_title": "State of Gujarat vs. QuickBite Foods",
        "court_name": "Court of CJM, Ahmedabad",
        "jurisdiction_district": "Ahmedabad",
        "accused": {
            "company_name": "QuickBite Foods Pvt. Ltd.",
            "registered_address": "SG Highway, Ahmedabad",
            "managing_director_name": "P. Shah",
        },
        "offence_summary": "Short-delivery of packaged snacks under Section 30.",
    }
    resp = client.post("/api/v1/court-brief/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "statement_of_facts" in data
    assert "statutory_prayer_to_magistrate" in data
    assert "section_65b_bsa_affidavit_text" in data
    assert "master_court_seal_hash" in data


def test_get_court_brief_api_200():
    # Create first
    payload = {
        "case_title": "State of Karnataka vs. SuperGrocer",
        "court_name": "Court of CJM, Bengaluru",
        "jurisdiction_district": "Bengaluru Urban",
        "accused": {
            "company_name": "SuperGrocer India Ltd.",
            "registered_address": "MG Road, Bengaluru",
            "managing_director_name": "K. Rao",
        },
        "offence_summary": "Missing MRP declarations.",
    }
    create_resp = client.post("/api/v1/court-brief/generate", json=payload)
    dossier_id = create_resp.json()["dossier_id"]

    # Query
    get_resp = client.get(f"/api/v1/court-brief/{dossier_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["dossier_id"] == dossier_id


def test_court_brief_preserves_dossier_id():
    req = CourtBriefGenerateRequest(
        accused=AccusedEntityDetails(
            company_name="Zeta Logistics",
            registered_address="Kolkata Port",
            managing_director_name="A. Roy",
        ),
        offence_summary="Section 49 corporate non-compliance.",
    )
    res = court_brief_service.generate_brief(req)
    cached = court_brief_service.get_brief(res.dossier_id)
    assert cached is not None
    assert cached.dossier_id == res.dossier_id
