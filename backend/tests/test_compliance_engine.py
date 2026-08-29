"""
test_compliance_engine.py
=========================
Stage 5 — Unit & API Tests for Statutory Compliance Validation Engine & Automated Violation Detection

Test coverage (10 tests):
  1. test_fully_compliant_product_validation               — Fully compliant product produces 0 violations & 'compliant' status
  2. test_missing_mrp_violation_detection                 — Missing MRP triggers Rule 6(1)(e) critical violation
  3. test_mrp_without_taxes_phrase_violation              — Omitting 'incl. of all taxes' triggers statutory violation
  4. test_non_standard_net_quantity_unit_violation        — Non-standard unit triggers Rule 6(1)(c) & Rule 11 violation
  5. test_missing_manufacturer_address_violation          — Incomplete address triggers Rule 6(1)(a) violation
  6. test_expired_product_on_shelf_violation              — Expired date triggers Rule 6(1)(h) critical violation
  7. test_missing_consumer_care_violation                 — Missing redressal contact triggers Rule 6(1)(f) violation
  8. test_repeat_offender_detection_and_penalty_escalation — Recidivism triggers alert and escalates penalty under Section 36(2)
  9. test_post_validate_api_endpoint_200                  — POST /inspections/{id}/validate returns 200 with summary
 10. test_get_violations_api_endpoint_200                 — GET /inspections/{id}/violations returns grounded violation list
"""

from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.rule import Rule, RuleVersion
from app.models.violation import Violation
from app.services.validator.rules_evaluator import rules_evaluator
from app.services.validator.repeat_offender_service import repeat_offender_service
from app.services.validator.compliance_service import compliance_service


# ---------------------------------------------------------------------------
# Helper — Create Compliant Product Model
# ---------------------------------------------------------------------------
def _create_mock_compliant_product(inspection_id: str) -> Product:
    today = date.today()
    return Product(
        inspection_id=inspection_id,
        product_name="Pure Wheat Flour 1kg",
        brand_name="National Mills",
        commodity_generic_name="Wheat Flour (Atta)",
        mrp_raw="MRP Rs. 55.00 (incl. of all taxes)",
        mrp_value=55.0,
        mrp_currency="INR",
        mrp_inclusive_taxes_declared=True,
        net_quantity_raw="1 kg",
        net_quantity_value=1.0,
        net_quantity_unit="kg",
        unit_sale_price_raw="Rs. 55.00 / kg",
        batch_number="WF-2026-08",
        mfg_date_raw="01/2026",
        mfg_date=date(2026, 1, 1),
        exp_date_raw="01/2027",
        exp_date=date(2027, 1, 1),
        manufacturer_name="National Flour Mills Pvt Ltd",
        manufacturer_address="Plot 10, Industrial Area, Sector 5, Navi Mumbai, Maharashtra 400705",
        country_of_origin="INDIA",
        consumer_care_email="care@nationalmills.in",
        consumer_care_phone="1800-200-1122",
        consumer_care_address="Customer Care Cell, National Mills, Navi Mumbai",
    )


# ===========================================================================
# Test 1 — Fully Compliant Product Validation
# ===========================================================================
def test_fully_compliant_product_validation(db_session: Session):
    """A product declaring all Rule 6 statutory disclosures should produce 0 violations."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-compliant-001")
    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    assert len(violations) == 0, f"Expected 0 violations, found: {[v.violation_title for v in violations]}"


# ===========================================================================
# Test 2 — Missing MRP Declaration Violation (Rule 6(1)(e))
# ===========================================================================
def test_missing_mrp_violation_detection(db_session: Session):
    """Omission of MRP must trigger a critical violation under Rule 6(1)(e)."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-no-mrp-001")
    product.mrp_value = None
    product.mrp_raw = None

    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    mrp_v = next((v for v in violations if v.field_affected == "mrp"), None)
    assert mrp_v is not None
    assert mrp_v.severity == "critical"
    assert "Rule 6(1)(e)" in mrp_v.section_violated


# ===========================================================================
# Test 3 — MRP Without Taxes Phrase Violation
# ===========================================================================
def test_mrp_without_taxes_phrase_violation(db_session: Session):
    """Declaring MRP without 'inclusive of all taxes' triggers a statutory violation."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-no-tax-001")
    product.mrp_inclusive_taxes_declared = False

    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    tax_v = next((v for v in violations if "Inclusive of All Taxes" in v.violation_title), None)
    assert tax_v is not None
    assert tax_v.severity in ("major", "critical")


# ===========================================================================
# Test 4 — Non-Standard Net Quantity Unit (Rule 11)
# ===========================================================================
def test_non_standard_net_quantity_unit_violation(db_session: Session):
    """Using non-standard units (e.g. 'box', 'pkt') triggers a Rule 11 violation."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-bad-unit-001")
    product.net_quantity_unit = "box"  # Non-standard

    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    unit_v = next((v for v in violations if v.field_affected == "net_quantity"), None)
    assert unit_v is not None
    assert "Non-Standard Unit" in unit_v.violation_title


# ===========================================================================
# Test 5 — Missing Manufacturer Address Violation (Rule 6(1)(a))
# ===========================================================================
def test_missing_manufacturer_address_violation(db_session: Session):
    """Omitting manufacturer physical address triggers Rule 6(1)(a) violation."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-no-addr-001")
    product.manufacturer_address = None
    product.packer_address = None

    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    mfg_v = next((v for v in violations if v.field_affected == "manufacturer_details"), None)
    assert mfg_v is not None
    assert "Address" in mfg_v.violation_title


# ===========================================================================
# Test 6 — Expired Product on Shelf (Rule 6(1)(h))
# ===========================================================================
def test_expired_product_on_shelf_violation(db_session: Session):
    """An expired product on store shelves triggers a critical violation."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-expired-001")
    product.exp_date = date(2026, 1, 1)  # Expired in Jan 2026

    # Inspection conducted in June 2026
    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    exp_v = next((v for v in violations if v.field_affected == "exp_date"), None)
    assert exp_v is not None
    assert exp_v.severity == "critical"
    assert "Expired Commodity" in exp_v.violation_title


# ===========================================================================
# Test 7 — Missing Consumer Care Redressal Violation (Rule 6(1)(f))
# ===========================================================================
def test_missing_consumer_care_violation(db_session: Session):
    """Missing consumer complaint mechanisms triggers Rule 6(1)(f) violation."""
    active_version = db_session.query(RuleVersion).filter(RuleVersion.is_active == True).first()
    rules = db_session.query(Rule).filter(Rule.version_id == active_version.id).all()

    product = _create_mock_compliant_product("insp-no-care-001")
    product.consumer_care_email = None
    product.consumer_care_phone = None
    product.consumer_care_address = None

    violations = rules_evaluator.evaluate_product(product, rules, inspection_date=date(2026, 6, 1))

    care_v = next((v for v in violations if v.field_affected == "consumer_care"), None)
    assert care_v is not None
    assert care_v.severity == "critical"


# ===========================================================================
# Test 8 — Repeat Offender Detection & Penalty Escalation (Section 36(2))
# ===========================================================================
def test_repeat_offender_detection_and_penalty_escalation(db_session: Session):
    """A manufacturer with historical non-compliance escalates to Section 36(2) penalties."""
    # Create past non-compliant inspection in DB
    past_insp = Inspection(
        inspection_number="INS-PAST-OFFENCE-001",
        inspector_id="test-inspector",
        district="Mumbai",
        state="Maharashtra",
        status="validated",
        compliance_status="non_compliant",
    )
    db_session.add(past_insp)
    db_session.commit()

    past_prod = Product(
        inspection_id=str(past_insp.id),
        manufacturer_name="Repeat Offender Foods Ltd",
        brand_name="RepeatBrand",
    )
    db_session.add(past_prod)

    past_violation = Violation(
        inspection_id=str(past_insp.id),
        rule_code="LM_RULE_6_1_E_MRP",
        field_affected="mrp",
        section_violated="Rule 6(1)(e)",
        violation_title="Missing MRP",
        violation_description="Missing MRP",
        severity="critical",
    )
    db_session.add(past_violation)
    db_session.commit()

    # Now check repeat offender status for new inspection of same manufacturer
    repeat_res = repeat_offender_service.check_repeat_offender_status(
        db=db_session,
        current_inspection_id="new-insp-id",
        manufacturer_name="Repeat Offender Foods Ltd",
    )

    assert repeat_res["is_repeat_offender"] is True
    assert repeat_res["prior_violations_count"] >= 1
    assert "Section 36(2)" in repeat_res["escalated_penalty"]
    assert "INS-PAST-OFFENCE-001" in repeat_res["prior_inspection_numbers"]


# ===========================================================================
# Test 9 — POST /api/v1/inspections/{id}/validate Endpoint (200)
# ===========================================================================
def test_post_validate_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """POST /inspections/{id}/validate executes validation engine and returns 200."""
    insp = Inspection(
        inspection_number="INS-VAL-TEST-001",
        inspector_id="test-inspector",
        district="Mumbai",
        state="Maharashtra",
        status="extracted",
    )
    db_session.add(insp)
    db_session.commit()

    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    insp.inspector_id = me_resp.json()["data"]["id"]
    db_session.commit()

    # Create product with missing MRP
    prod = _create_mock_compliant_product(str(insp.id))
    prod.mrp_value = None  # Introduce violation
    db_session.add(prod)
    db_session.commit()

    resp = client.post(
        f"/api/v1/inspections/{insp.id}/validate",
        headers=inspector_token_headers,
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()

    assert data["inspection_id"] == str(insp.id)
    assert data["compliance_status"] == "non_compliant"
    assert data["summary"]["total_violations"] >= 1
    assert data["summary"]["critical_violations"] >= 1


# ===========================================================================
# Test 10 — GET /api/v1/inspections/{id}/violations Endpoint (200)
# ===========================================================================
def test_get_violations_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """GET /inspections/{id}/violations retrieves persisted violation dockets."""
    insp = Inspection(
        inspection_number="INS-VIOLATIONS-GET-001",
        inspector_id="test-inspector",
        district="Pune",
        state="Maharashtra",
        status="validated",
        compliance_status="non_compliant",
    )
    db_session.add(insp)
    db_session.commit()

    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    insp.inspector_id = me_resp.json()["data"]["id"]
    db_session.commit()

    violation = Violation(
        inspection_id=str(insp.id),
        rule_code="LM_RULE_6_1_E_MRP",
        field_affected="mrp",
        section_violated="Rule 6(1)(e), LM PCR 2011",
        statute_title="Legal Metrology (Packaged Commodities) Rules, 2011",
        penalty_provision="Section 36, Legal Metrology Act, 2009",
        estimated_fine="Fine up to ₹25,000",
        violation_title="Missing MRP",
        violation_description="Package omits maximum retail price.",
        severity="critical",
    )
    db_session.add(violation)
    db_session.commit()

    get_resp = client.get(
        f"/api/v1/inspections/{insp.id}/violations",
        headers=inspector_token_headers,
    )
    assert get_resp.status_code == 200
    v_list = get_resp.json()
    assert len(v_list) == 1
    assert v_list[0]["rule_code"] == "LM_RULE_6_1_E_MRP"
    assert "Rule 6(1)(e)" in v_list[0]["section_violated"]
