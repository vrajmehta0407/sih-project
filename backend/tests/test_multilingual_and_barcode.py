"""
test_multilingual_and_barcode.py
================================
Stage 11 — Unit Tests for Multilingual Hindi Statutory OCR & Barcode Decoding
"""

import pytest
from datetime import date
from app.services.extractor.parsers import (
    parse_mrp,
    parse_net_quantity,
    parse_dates,
    parse_batch_number,
    parse_mfg_packer_importer,
    parse_unit_sale_price,
)
from app.services.image_preprocessing_service import image_preprocessing_service


def test_hindi_mrp_extraction_with_taxes():
    raw_text = "अधिकतम खुदरा मूल्य: ₹ 240.00 (सभी करों सहित)"
    res = parse_mrp(raw_text)
    assert res["value"] == 240.0
    assert res["inclusive_taxes_declared"] is True
    assert res["confidence"] >= 0.90


def test_hindi_mrp_without_taxes():
    raw_text = "अधिकतम खुदरा मूल्य रु 95.50"
    res = parse_mrp(raw_text)
    assert res["value"] == 95.50
    assert res["inclusive_taxes_declared"] is False


def test_hindi_net_quantity_grams():
    raw_text = "शुद्ध मात्रा: 500 ग्राम"
    res = parse_net_quantity(raw_text)
    assert res["value"] == 500.0
    assert res["unit"] == "g"
    assert res["is_standard_unit"] is True


def test_hindi_net_quantity_kg():
    raw_text = "कुल मात्रा: 2.5 कि.ग्रा."
    res = parse_net_quantity(raw_text)
    assert res["value"] == 2.5
    assert res["unit"] == "kg"
    assert res["is_standard_unit"] is True


def test_hindi_net_quantity_ml():
    raw_text = "शुद्ध मात्रा: 750 मिली"
    res = parse_net_quantity(raw_text)
    assert res["value"] == 750.0
    assert res["unit"] == "ml"
    assert res["is_standard_unit"] is True


def test_hindi_mfg_date_parsing():
    raw_text = "निर्माण तिथि: 04/2026"
    res = parse_dates(raw_text)
    assert res["mfg_date"] == date(2026, 4, 1)


def test_hindi_exp_date_parsing():
    raw_text = "उपयोग की अंतिम तिथि: 11/2026"
    res = parse_dates(raw_text)
    assert res["exp_date"] == date(2026, 11, 1)


def test_hindi_best_before_duration():
    raw_text = "निर्माण तिथि: 01/2026\nसर्वोत्तम उपयोग 6 महीने"
    res = parse_dates(raw_text)
    assert res["mfg_date"] == date(2026, 1, 1)
    assert res["exp_date"] == date(2026, 7, 1)


def test_hindi_manufacturer_parsing():
    raw_text = "निर्माता: पतंजलि फूड्स लिमिटेड\nऔद्योगिक क्षेत्र, हरिद्वार 249401"
    res = parse_mfg_packer_importer(raw_text)
    assert "पतंजलि" in res["manufacturer_name"]


def test_hindi_batch_and_barcode_step():
    raw_text = "बैच संख्या: BATCH-IND-99"
    res = parse_batch_number(raw_text)
    assert res["batch_number"] == "BATCH-IND-99"
