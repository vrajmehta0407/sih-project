"""
test_deceptive_packaging.py
===========================
Stage 29 — Unit & API Tests for Deceptive Packaging & Visual Deception Index (VDI)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.deceptive_packaging import DeceptivePackagingAuditRequest
from app.services.deceptive_packaging_service import deceptive_packaging_service

client = TestClient(app)


# ── Deceptive Packaging Service Unit Tests ───────────────────────────────────

def test_deceptive_packaging_oversized_box_violation():
    # Outer volume = 24 * 12 * 36 = 10,368 cm3
    # Product volume = 500 / 0.18 = 2,777 cm3 -> Slack = 73.2% -> Deceptive = 58.2% -> VDI ~ 9.7
    req = DeceptivePackagingAuditRequest(
        product_name="Oversized Cereal",
        brand_name="Test Brand",
        packaging_type="RIGID_BOX",
        package_length_cm=24.0,
        package_width_cm=12.0,
        package_height_cm=36.0,
        declared_net_quantity_grams=500.0,
        product_bulk_density_g_per_cm3=0.18,
        functional_cushion_allowance_pct=15.0,
    )
    res = deceptive_packaging_service.audit_package(req)
    assert res.is_compliant_with_rule_5 is False
    assert res.statutory_verdict == "DECEPTIVE_PACKAGING_VIOLATION"
    assert res.visual_deception_index >= 7.0
    assert res.deception_risk_level == "CRITICAL_FRAUD"
    assert res.statutory_penalty_amount_inr == 25000.0


def test_deceptive_packaging_chips_nitrogen_cushion_compliant():
    # Outer volume = 18 * 6 * 20 = 2,160 cm3
    # Product volume = 90 / 0.06 = 1,500 cm3 -> Slack = 30.5% -> Deceptive = 0.5% (allowance 30%)
    req = DeceptivePackagingAuditRequest(
        product_name="Compliant Potato Chips",
        brand_name="SnackCo",
        packaging_type="FLEXIBLE_POUCH",
        package_length_cm=18.0,
        package_width_cm=6.0,
        package_height_cm=20.0,
        declared_net_quantity_grams=90.0,
        product_bulk_density_g_per_cm3=0.06,
        functional_cushion_allowance_pct=30.0,
    )
    res = deceptive_packaging_service.audit_package(req)
    assert res.is_compliant_with_rule_5 is True
    assert res.statutory_verdict == "COMPLIANT_FUNCTIONAL_PACKAGING"
    assert res.visual_deception_index <= 1.0


def test_deceptive_packaging_cosmetic_false_bottom_fraud():
    # Outer volume = 8 * 8 * 8 = 512 cm3
    # Product volume = 50 / 0.95 = 52.6 cm3 -> Slack = 89.7% -> Deceptive = 79.7%
    req = DeceptivePackagingAuditRequest(
        product_name="False Bottom Face Cream",
        brand_name="LuxeCosmetics",
        packaging_type="JAR_WITH_FALSE_BOTTOM",
        package_length_cm=8.0,
        package_width_cm=8.0,
        package_height_cm=8.0,
        declared_net_quantity_grams=50.0,
        product_bulk_density_g_per_cm3=0.95,
        functional_cushion_allowance_pct=10.0,
    )
    res = deceptive_packaging_service.audit_package(req)
    assert res.is_compliant_with_rule_5 is False
    assert res.visual_deception_index == 10.0
    assert "Section 18" in res.statutory_citations[0]


def test_deceptive_packaging_vdi_scale_boundaries():
    req = DeceptivePackagingAuditRequest(
        product_name="Compact Salt Box",
        brand_name="Tata",
        packaging_type="RIGID_BOX",
        package_length_cm=10.0,
        package_width_cm=8.0,
        package_height_cm=12.0,
        declared_net_quantity_grams=1000.0,
        product_bulk_density_g_per_cm3=1.1,  # V = 909 cm3 vs outer 960 cm3 -> ~5% slack
    )
    res = deceptive_packaging_service.audit_package(req)
    assert 0.0 <= res.visual_deception_index <= 10.0
    assert res.deception_risk_level == "NEGLIGIBLE"


def test_deceptive_packaging_statutory_penalty_calculation():
    req = DeceptivePackagingAuditRequest(
        product_name="Deceptive Biscuits",
        brand_name="SweetBites",
        packaging_type="RIGID_BOX",
        package_length_cm=20.0,
        package_width_cm=10.0,
        package_height_cm=15.0,
        declared_net_quantity_grams=100.0,
        product_bulk_density_g_per_cm3=0.5,
    )
    res = deceptive_packaging_service.audit_package(req)
    assert res.statutory_penalty_amount_inr == 25000.0


# ── Deceptive Packaging API Tests ───────────────────────────────────────────

def test_deceptive_audit_api_200_violation():
    payload = {
        "product_name": "API Deceptive Cereal 500g",
        "brand_name": "CrunchMart",
        "packaging_type": "RIGID_BOX",
        "package_length_cm": 25.0,
        "package_width_cm": 12.0,
        "package_height_cm": 35.0,
        "declared_net_quantity_grams": 500.0,
        "product_bulk_density_g_per_cm3": 0.18,
        "functional_cushion_allowance_pct": 15.0,
    }
    resp = client.post("/api/v1/deceptive-packaging/audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_compliant_with_rule_5"] is False
    assert data["statutory_verdict"] == "DECEPTIVE_PACKAGING_VIOLATION"
    assert "audit_id" in data


def test_deceptive_audit_api_200_compliant():
    payload = {
        "product_name": "API Compliant Butter 500g",
        "brand_name": "Amul",
        "packaging_type": "RIGID_BOX",
        "package_length_cm": 12.0,
        "package_width_cm": 7.0,
        "package_height_cm": 6.5,
        "declared_net_quantity_grams": 500.0,
        "product_bulk_density_g_per_cm3": 0.96,
        "functional_cushion_allowance_pct": 10.0,
    }
    resp = client.post("/api/v1/deceptive-packaging/audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_compliant_with_rule_5"] is True
    assert data["statutory_verdict"] == "COMPLIANT_FUNCTIONAL_PACKAGING"


def test_deceptive_audit_api_response_schema():
    payload = {
        "product_name": "Schema Test Jar",
        "brand_name": "SkinCare",
        "packaging_type": "JAR_WITH_FALSE_BOTTOM",
        "package_length_cm": 6.0,
        "package_width_cm": 6.0,
        "package_height_cm": 6.0,
        "declared_net_quantity_grams": 50.0,
    }
    resp = client.post("/api/v1/deceptive-packaging/audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "visual_deception_index" in data
    assert "container_outer_volume_cm3" in data
    assert "actual_product_volume_cm3" in data
    assert "deceptive_non_functional_slack_fill_pct" in data
    assert "digital_audit_seal" in data


def test_get_deceptive_audit_api_200():
    # Audit first
    payload = {
        "product_name": "Lookup Test Box",
        "brand_name": "Lookup Brand",
        "package_length_cm": 15.0,
        "package_width_cm": 10.0,
        "package_height_cm": 20.0,
        "declared_net_quantity_grams": 400.0,
    }
    create_resp = client.post("/api/v1/deceptive-packaging/audit", json=payload)
    audit_id = create_resp.json()["audit_id"]

    # Query
    get_resp = client.get(f"/api/v1/deceptive-packaging/reports/{audit_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["audit_id"] == audit_id


def test_deceptive_audit_seal_integrity():
    req = DeceptivePackagingAuditRequest(
        product_name="Seal Test Pack",
        brand_name="SealCo",
        package_length_cm=10.0,
        package_width_cm=10.0,
        package_height_cm=10.0,
        declared_net_quantity_grams=200.0,
    )
    res = deceptive_packaging_service.audit_package(req)
    assert len(res.digital_audit_seal) == 64  # SHA-256
