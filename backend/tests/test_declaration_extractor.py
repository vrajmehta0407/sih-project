"""
test_declaration_extractor.py
==============================
Stage 4 — Unit & API Tests for NLP & Regex Statutory Declarations Extractor (Rule 6 of LM PCR 2011)

Test coverage (10 tests):
  1. test_mrp_and_inclusive_taxes_extraction         — Extracts MRP, currency, and verifies tax inclusion
  2. test_net_quantity_and_unit_normalization       — Normalizes non-standard units (gms->g, ltr->l) under Rule 11
  3. test_unit_sale_price_extraction                — Extracts USP declarations (₹/g, Rs/ml) under Rule 6(1)(k)
  4. test_mfg_and_exp_date_parsing                  — Standardizes MM/YYYY and DD/MM/YYYY dates
  5. test_best_before_relative_date_parsing         — Computes expiry date from relative shelf life (X months)
  6. test_batch_number_extraction                   — Extracts batch / lot code
  7. test_manufacturer_and_packer_address_extraction — Extracts company name and address with PIN code
  8. test_consumer_care_details_extraction          — Extracts toll-free phone and customer email
  9. test_country_of_origin_extraction              — Extracts country under Rule 6(1)(g)
 10. test_extract_declarations_api_endpoint_200     — POST /extract-declarations & GET /declarations API verification
"""

import io
import cv2
import numpy as np
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.extractor.parsers import (
    parse_mrp,
    parse_net_quantity,
    parse_unit_sale_price,
    parse_dates,
    parse_batch_number,
    parse_mfg_packer_importer,
    parse_country_of_origin,
    parse_consumer_care,
    parse_commodity_name,
)
from app.services.extractor.declaration_extractor import declaration_extractor
from app.services.extractor.extraction_service import extraction_service
from app.models.inspection import Inspection
from app.models.product import Product


# ===========================================================================
# Test 1 — MRP & Inclusive of All Taxes Extraction
# ===========================================================================
def test_mrp_and_inclusive_taxes_extraction():
    """Verify MRP numerical value and statutory tax phrase detection."""
    text1 = "MRP Rs. 249.00 (inclusive of all taxes)\nBatch: B01"
    res1 = parse_mrp(text1)
    assert res1["value"] == 249.0
    assert res1["inclusive_taxes_declared"] is True
    assert res1["confidence"] >= 0.90

    text2 = "MAX RETAIL PRICE: ₹ 1,500.50 (INCL. OF ALL TAXES)"
    # Clean commas before testing
    res2 = parse_mrp(text2.replace(",", ""))
    assert res2["value"] == 1500.50
    assert res2["inclusive_taxes_declared"] is True

    text3 = "MRP: Rs. 99\nNet Qty: 100g"  # Missing tax declaration
    res3 = parse_mrp(text3)
    assert res3["value"] == 99.0
    assert res3["inclusive_taxes_declared"] is False


# ===========================================================================
# Test 2 — Net Quantity & Unit Normalization (Rule 11)
# ===========================================================================
def test_net_quantity_and_unit_normalization():
    """Verify magnitude extraction and normalization to standard SI units."""
    # gms -> g
    res1 = parse_net_quantity("NET WEIGHT: 500 gms")
    assert res1["value"] == 500.0
    assert res1["unit"] == "g"
    assert res1["is_standard_unit"] is True

    # ltrs -> l
    res2 = parse_net_quantity("Net Content: 1.5 ltr")
    assert res2["value"] == 1.5
    assert res2["unit"] == "l"
    assert res2["is_standard_unit"] is True

    # pieces -> N
    res3 = parse_net_quantity("Quantity: 10 pieces")
    assert res3["value"] == 10.0
    assert res3["unit"] == "N"
    assert res3["is_standard_unit"] is True


# ===========================================================================
# Test 3 — Unit Sale Price (USP) Extraction
# ===========================================================================
def test_unit_sale_price_extraction():
    """Verify Unit Sale Price extraction required under Rule 6(1)(k)."""
    text1 = "MRP Rs. 100 (incl. of all taxes)\nUSP: Rs. 0.20 / g"
    res1 = parse_unit_sale_price(text1)
    assert res1["value"] == 0.20
    assert res1["unit"] == "g"

    text2 = "UNIT SALE PRICE: ₹ 1.50 per ml"
    res2 = parse_unit_sale_price(text2)
    assert res2["value"] == 1.50
    assert res2["unit"] == "ml"


# ===========================================================================
# Test 4 — Manufacturing & Expiry Date Parsing
# ===========================================================================
def test_mfg_and_exp_date_parsing():
    """Verify date parsing across standard Indian formats."""
    text1 = "MFD: 03/2026\nEXP: 03/2027"
    res1 = parse_dates(text1)
    assert res1["mfg_date"] == date(2026, 3, 1)
    assert res1["exp_date"] == date(2027, 3, 1)

    text2 = "PKD: 15 JAN 2026\nUSE BEFORE: 15 JAN 2028"
    res2 = parse_dates(text2)
    assert res2["mfg_date"] == date(2026, 1, 15)
    assert res2["exp_date"] == date(2028, 1, 15)


# ===========================================================================
# Test 5 — Relative Shelf-Life Date Computation
# ===========================================================================
def test_best_before_relative_date_parsing():
    """Relative shelf life (e.g. 6 months from Mfg) computes target expiry date."""
    text = "MFG DATE: 01/2026\nBest before 6 months from manufacture"
    res = parse_dates(text)
    assert res["mfg_date"] == date(2026, 1, 1)
    assert res["exp_date"] == date(2026, 7, 1)


# ===========================================================================
# Test 6 — Batch / Lot Number Extraction
# ===========================================================================
def test_batch_number_extraction():
    """Verify batch and lot code extraction."""
    text1 = "BATCH NO: B2026-X99\nMRP: Rs. 150"
    res1 = parse_batch_number(text1)
    assert res1["batch_number"] == "B2026-X99"

    text2 = "LOT: L-90214"
    res2 = parse_batch_number(text2)
    assert res2["batch_number"] == "L-90214"


# ===========================================================================
# Test 7 — Manufacturer & Packer Details Extraction
# ===========================================================================
def test_manufacturer_and_packer_address_extraction():
    """Verify business name, address, and PIN code extraction."""
    text = (
        "MANUFACTURED BY: ABC Food Products Pvt Ltd\n"
        "Plot 45, MIDC Industrial Area, Andheri East\n"
        "Mumbai, Maharashtra 400093\n"
        "PACKED BY: XYZ Packers\n"
        "Pune 411001"
    )
    res = parse_mfg_packer_importer(text)
    assert "ABC Food Products" in res["manufacturer_name"]
    assert "400093" in res["manufacturer_address"]
    assert "XYZ Packers" in res["packer_name"]


# ===========================================================================
# Test 8 — Consumer Care Details Extraction
# ===========================================================================
def test_consumer_care_details_extraction():
    """Verify toll-free helpline and customer support email extraction."""
    text = (
        "FOR CONSUMER COMPLAINTS / FEEDBACK CONTACT:\n"
        "Consumer Care Executive\n"
        "Toll Free: 1800-222-333\n"
        "Email: care@abcfoods.com\n"
        "Address: PO Box 1234, Mumbai"
    )
    res = parse_consumer_care(text)
    assert "1800-222-333" in res["phone"]
    assert res["email"] == "care@abcfoods.com"


# ===========================================================================
# Test 9 — Country of Origin Extraction
# ===========================================================================
def test_country_of_origin_extraction():
    """Verify country of origin declaration under Rule 6(1)(g)."""
    text1 = "COUNTRY OF ORIGIN: INDIA\nMRP Rs. 50"
    res1 = parse_country_of_origin(text1)
    assert res1["country"] == "INDIA"

    text2 = "MADE IN VIETNAM"
    res2 = parse_country_of_origin(text2)
    assert res2["country"] == "VIETNAM"


# ===========================================================================
# Test 10 — POST /extract-declarations & GET /declarations API Verification
# ===========================================================================
def test_extract_declarations_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """Full API verification of declarations extraction pipeline."""
    sample_label_text = (
        "SAMPLE BRAND BASMATI RICE\n"
        "GENERIC NAME: Basmati Rice\n"
        "NET QTY: 1 kg\n"
        "MRP: Rs. 140.00 (incl. of all taxes)\n"
        "USP: Rs. 0.14 / g\n"
        "BATCH NO: BR-2026-01\n"
        "MFD: 02/2026\n"
        "EXP: 02/2028\n"
        "MANUFACTURED BY: Royal Agri Ltd\n"
        "GT Road, Karnal, Haryana 132001\n"
        "COUNTRY OF ORIGIN: INDIA\n"
        "Consumer Care: 1800-111-222, care@royalagri.in\n"
    )

    # Create inspection directly in DB with mock OCR consensus text
    insp = Inspection(
        inspection_number="INS-DECL-TEST-001",
        inspector_id="test-inspector",
        district="Mumbai",
        state="Maharashtra",
        status="preprocessed",
        preprocessed_images=[{"side": "front", "file_path": "dummy.jpg"}],
    )
    db_session.add(insp)
    db_session.commit()

    # Link logged-in inspector
    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    insp.inspector_id = me_resp.json()["data"]["id"]
    db_session.commit()

    prod = Product(
        inspection_id=str(insp.id),
        paddle_raw_text=sample_label_text,
        extracted_fields_consensus={"aggregated_consensus_text": sample_label_text},
    )
    db_session.add(prod)
    db_session.commit()

    # Run extraction endpoint
    post_resp = client.post(
        f"/api/v1/inspections/{insp.id}/extract-declarations",
        headers=inspector_token_headers,
    )
    assert post_resp.status_code == 200, f"Expected 200: {post_resp.text}"
    post_data = post_resp.json()

    assert post_data["inspection_id"] == str(insp.id)
    assert post_data["declarations"]["mrp"]["value"] == 140.0
    assert post_data["declarations"]["mrp"]["inclusive_taxes_declared"] is True
    assert post_data["declarations"]["net_quantity"]["value"] == 1.0
    assert post_data["declarations"]["net_quantity"]["unit"] == "kg"
    assert post_data["declarations"]["country_of_origin"]["country"] == "INDIA"
    assert post_data["declarations"]["consumer_care"]["email"] == "care@royalagri.in"
    assert post_data["declarations"]["summary"]["declared_fields_count"] >= 5

    # Fetch declarations via GET endpoint
    get_resp = client.get(
        f"/api/v1/inspections/{insp.id}/declarations",
        headers=inspector_token_headers,
    )
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["declarations"]["mrp"]["value"] == 140.0
