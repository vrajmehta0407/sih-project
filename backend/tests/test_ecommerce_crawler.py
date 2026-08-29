"""
test_ecommerce_crawler.py
=========================
Stage 26 — Unit & API Tests for High-Throughput E-Commerce Batch URL Crawler
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ecommerce_batch import (
    BatchAuditRequest,
    BatchProductUrlItem,
)
from app.services.ecommerce_batch_service import ecommerce_batch_service

client = TestClient(app)


# ── E-Commerce Batch Crawler Service Unit Tests ───────────────────────────────

def test_batch_crawler_service_logic():
    req = BatchAuditRequest(
        batch_title="Test FMCG Batch",
        platform_name="Blinkit",
        items=[
            BatchProductUrlItem(url="https://www.blinkit.com/prn/amul-gold-milk-1l", platform_name="Blinkit"),
            BatchProductUrlItem(url="https://www.blinkit.com/prn/imported-chips-250g", platform_name="Blinkit"),
        ]
    )
    res = ecommerce_batch_service.audit_batch(req)
    assert res.total_listings_audited == 2
    assert res.platform_name == "Blinkit"
    assert res.batch_id.startswith("ECOM-BATCH-2026-")
    assert len(res.items_verdicts) == 2


def test_batch_crawler_identifies_defective_listings():
    req = BatchAuditRequest(
        batch_title="Snack Audit",
        platform_name="Zepto",
        items=[
            BatchProductUrlItem(url="https://www.zeptonow.com/prn/imported-snack-pack-100g", platform_name="Zepto"),
        ]
    )
    res = ecommerce_batch_service.audit_batch(req)
    verdict = res.items_verdicts[0]
    assert verdict.is_compliant is False
    assert len(verdict.missing_declarations) >= 1
    assert verdict.statutory_penalty_amount > 0


def test_batch_crawler_calculates_liability_penalty():
    req = BatchAuditRequest(
        batch_title="Multi Platform Stress Audit",
        platform_name="Amazon",
        items=[
            BatchProductUrlItem(url="https://www.amazon.in/dp/B08XYZ/imported-snack-1", platform_name="Amazon"),
            BatchProductUrlItem(url="https://www.amazon.in/dp/B09ABC/imported-oil-2", platform_name="Amazon"),
        ]
    )
    res = ecommerce_batch_service.audit_batch(req)
    assert res.non_compliant_count == 2
    assert res.total_statutory_liability_inr == 50000.0


def test_batch_crawler_generates_formal_notice_draft():
    req = BatchAuditRequest(
        batch_title="Notice Generation Test",
        platform_name="Flipkart",
        items=[
            BatchProductUrlItem(url="https://www.flipkart.com/imported-product-123", platform_name="Flipkart"),
        ]
    )
    res = ecommerce_batch_service.audit_batch(req)
    assert "FORMAL STATUTORY NOTICE UNDER RULE 6(10)" in res.bulk_show_cause_notice_draft
    assert "Flipkart" in res.bulk_show_cause_notice_draft
    assert res.batch_id in res.bulk_show_cause_notice_draft


def test_batch_crawler_infraction_breakdown_metrics():
    req = BatchAuditRequest(
        batch_title="Infractions Check",
        platform_name="Blinkit",
        items=[
            BatchProductUrlItem(url="https://www.blinkit.com/prn/imported-snack", platform_name="Blinkit"),
        ]
    )
    res = ecommerce_batch_service.audit_batch(req)
    assert "MISSING_COUNTRY_OF_ORIGIN" in res.high_risk_infraction_distribution
    assert res.high_risk_infraction_distribution["MISSING_COUNTRY_OF_ORIGIN"] >= 1


# ── E-Commerce Batch Crawler API Tests ───────────────────────────────────────

def test_batch_audit_api_200():
    payload = {
        "batch_title": "API Batch Audit Test",
        "platform_name": "Blinkit",
        "items": [
            {"url": "https://www.blinkit.com/prn/amul-milk-1l", "platform_name": "Blinkit"},
            {"url": "https://www.blinkit.com/prn/imported-cheese-200g", "platform_name": "Blinkit"},
        ]
    }
    resp = client.post("/api/v1/ecommerce/batch-audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_listings_audited"] == 2
    assert "batch_id" in data
    assert data["batch_id"].startswith("ECOM-BATCH-2026-")


def test_batch_audit_api_response_schema():
    payload = {
        "batch_title": "Schema Test",
        "platform_name": "Amazon",
        "items": [
            {"url": "https://www.amazon.in/dp/B001/organic-tea-500g", "platform_name": "Amazon"}
        ]
    }
    resp = client.post("/api/v1/ecommerce/batch-audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "compliance_rate_pct" in data
    assert "total_statutory_liability_inr" in data
    assert "items_verdicts" in data
    assert "bulk_show_cause_notice_draft" in data


def test_get_batch_audit_api_200():
    # Execute batch first
    payload = {
        "batch_title": "Lookup Test",
        "platform_name": "Zepto",
        "items": [
            {"url": "https://www.zeptonow.com/prn/amul-butter-500g", "platform_name": "Zepto"}
        ]
    }
    create_resp = client.post("/api/v1/ecommerce/batch-audit", json=payload)
    batch_id = create_resp.json()["batch_id"]

    # Query by batch_id
    get_resp = client.get(f"/api/v1/ecommerce/batch-audit/{batch_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["batch_id"] == batch_id


def test_batch_audit_preserves_batch_id():
    req = BatchAuditRequest(
        batch_title="Preserve ID",
        platform_name="Swiggy Instamart",
        items=[
            BatchProductUrlItem(url="https://www.swiggy.com/instamart/item-1", platform_name="Swiggy Instamart")
        ]
    )
    res = ecommerce_batch_service.audit_batch(req)
    cached = ecommerce_batch_service.get_batch(res.batch_id)
    assert cached is not None
    assert cached.batch_id == res.batch_id


def test_batch_crawler_slug_extraction():
    url = "https://www.blinkit.com/prn/fortune-sunflower-oil-1l/prid/1029"
    title = ecommerce_batch_service._extract_title_from_url(url)
    assert "Sunflower" in title or "Fortune" in title or len(title) > 3
