"""
test_ecommerce_and_ws.py
========================
Stage 12 — Unit & API Tests for E-Commerce Rule 6(10) Compliance Auditor & WebSocket
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.ecommerce import EcommerceAuditRequest
from app.api.v1.endpoints.ecommerce import _run_rule_6_10_audit

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


# ── Unit Tests (business logic) ──────────────────────────────────────────────

def test_compliant_listing_no_violations():
    req = EcommerceAuditRequest(
        platform="Amazon India",
        product_name="Amul Butter 500g",
        mrp_displayed=295.0,
        mrp_includes_taxes_declared=True,
        net_quantity_displayed="500 g",
        unit_sale_price_displayed="₹0.59/g",
        country_of_origin_displayed="India",
        manufacturer_details_displayed="Gujarat Cooperative Milk Marketing Federation Ltd, Anand 388001",
        customer_care_displayed="1800-599-4949",
        expiry_date_displayed="09/2026",
        is_imported=False,
        product_category="Food & Beverages",
    )
    result = _run_rule_6_10_audit(req)
    assert result.is_compliant is True
    assert result.total_violations == 0
    assert result.compliance_score == 100.0


def test_missing_mrp_violation_detected():
    req = EcommerceAuditRequest(
        platform="Flipkart",
        product_name="XYZ Biscuits",
        mrp_displayed=None,
        net_quantity_displayed="100 g",
        country_of_origin_displayed="India",
        manufacturer_details_displayed="XYZ Foods Pvt Ltd",
    )
    result = _run_rule_6_10_audit(req)
    codes = [v.code for v in result.violations]
    assert "MISSING_MRP" in [c.value for c in codes]
    assert result.is_compliant is False


def test_mrp_without_tax_clause_is_major_violation():
    req = EcommerceAuditRequest(
        platform="Blinkit",
        product_name="Tata Salt 1kg",
        mrp_displayed=20.0,
        mrp_includes_taxes_declared=False,
        net_quantity_displayed="1 kg",
        country_of_origin_displayed="India",
        manufacturer_details_displayed="Tata Consumer Products Ltd",
    )
    result = _run_rule_6_10_audit(req)
    major = [v for v in result.violations if v.code.value == "MRP_WITHOUT_TAX_DECLARATION"]
    assert len(major) == 1
    assert major[0].severity == "MAJOR"


def test_missing_country_of_origin_critical():
    req = EcommerceAuditRequest(
        platform="Amazon India",
        product_name="Imported Olive Oil 1L",
        mrp_displayed=450.0,
        mrp_includes_taxes_declared=True,
        net_quantity_displayed="1 L",
        country_of_origin_displayed=None,
        manufacturer_details_displayed="Oleificio SpA, Italy",
        is_imported=True,
        importer_details_displayed="ABC Imports, Mumbai 400001",
    )
    result = _run_rule_6_10_audit(req)
    codes = [v.code.value for v in result.violations]
    assert "MISSING_COUNTRY_OF_ORIGIN" in codes
    crit = [v for v in result.violations if v.code.value == "MISSING_COUNTRY_OF_ORIGIN"]
    assert crit[0].severity == "CRITICAL"


def test_imported_product_missing_importer_details():
    req = EcommerceAuditRequest(
        platform="Zepto",
        product_name="Greek Yogurt 200g",
        mrp_displayed=80.0,
        mrp_includes_taxes_declared=True,
        net_quantity_displayed="200 g",
        country_of_origin_displayed="Greece",
        manufacturer_details_displayed="Olympus Dairy, Athens",
        is_imported=True,
        importer_details_displayed=None,
    )
    result = _run_rule_6_10_audit(req)
    codes = [v.code.value for v in result.violations]
    assert "MISSING_IMPORTER_DETAILS" in codes


def test_food_product_missing_expiry_date():
    req = EcommerceAuditRequest(
        platform="Swiggy Instamart",
        product_name="Dabur Honey 500g",
        mrp_displayed=299.0,
        mrp_includes_taxes_declared=True,
        net_quantity_displayed="500 g",
        unit_sale_price_displayed="₹0.60/g",
        country_of_origin_displayed="India",
        manufacturer_details_displayed="Dabur India Ltd, Ghaziabad",
        customer_care_displayed="1800-103-1644",
        expiry_date_displayed=None,
        product_category="Food & Beverages",
    )
    result = _run_rule_6_10_audit(req)
    codes = [v.code.value for v in result.violations]
    assert "MISSING_EXPIRY_DATE" in codes


def test_non_compliant_listing_generates_show_cause_notice():
    req = EcommerceAuditRequest(
        platform="Amazon India",
        product_name="Unknown Product",
        mrp_displayed=None,
        net_quantity_displayed=None,
        country_of_origin_displayed=None,
        manufacturer_details_displayed=None,
    )
    result = _run_rule_6_10_audit(req)
    assert result.statutory_notice is not None
    assert "Section 36" in result.statutory_notice
    assert "Amazon India" in result.statutory_notice


# ── API Tests ────────────────────────────────────────────────────────────────

def test_ecommerce_audit_api_200():
    token = get_inspector_token()
    payload = {
        "platform": "Flipkart",
        "product_name": "Test Cookie 150g",
        "mrp_displayed": 25.0,
        "mrp_includes_taxes_declared": True,
        "net_quantity_displayed": "150 g",
        "unit_sale_price_displayed": "₹0.17/g",
        "country_of_origin_displayed": "India",
        "manufacturer_details_displayed": "Test Foods Ltd, Mumbai 400001",
        "customer_care_displayed": "1800-000-1234",
        "expiry_date_displayed": "06/2026",
        "is_imported": False,
        "product_category": "Food & Beverages",
    }
    resp = client.post(
        "/api/v1/ecommerce/audit",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "is_compliant" in data
    assert "violations" in data
    assert "compliance_score" in data


def test_ecommerce_audit_requires_auth():
    payload = {"platform": "Amazon", "product_name": "Test"}
    resp = client.post("/api/v1/ecommerce/audit", json=payload)
    assert resp.status_code == 401


def test_websocket_connection_and_ping():
    with client.websocket_connect("/api/v1/ws/inspections") as ws:
        # Should receive the connection handshake
        data = ws.receive_json()
        assert data["event"] == "CONNECTION_ESTABLISHED"
        # Send a PING
        ws.send_json({"action": "PING"})
        pong = ws.receive_json()
        assert pong["event"] == "PONG"
