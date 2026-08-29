"""
test_dashboard_and_sync.py
==========================
Stage 7 — Unit & API Tests for Executive Analytics, Dashboard Metrics, Audit Logs, and Offline Batch Sync

Test coverage (10 tests):
  1. test_executive_metrics_aggregation          — Aggregates compliance rate, status counts, and violation tallies
  2. test_compliance_trends_time_series          — Computes time-series daily inspection velocity
  3. test_top_statutory_violations_breakdown     — Ranks most frequently violated rules under LM PCR 2011
  4. test_jurisdiction_heatmap_computation       — Groups inspections by district/state with compliance metrics
  5. test_repeat_offenders_leaderboard           — Aggregates recidivist manufacturers and violation counts
  6. test_get_dashboard_metrics_api_endpoint_200 — GET /dashboard/metrics returns 200
  7. test_get_dashboard_trends_api_endpoint_200  — GET /dashboard/trends returns 200
  8. test_get_dashboard_top_violations_api_endpoint_200 — GET /dashboard/top-violations returns 200
  9. test_get_audit_logs_paginated_api_endpoint_200 — GET /audit-logs returns paginated response
 10. test_post_batch_sync_api_endpoint_200       — POST /inspections/batch-sync syncs offline items
"""

import uuid
from datetime import datetime, timezone, date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation
from app.models.audit_log import AuditLog
from app.services.dashboard.analytics_service import analytics_service
from app.services.sync.batch_sync_service import batch_sync_service
from app.schemas.sync import BatchSyncRequest, BatchSyncInspectionItem


# ===========================================================================
# Test 1 — Executive Metrics Aggregation
# ===========================================================================
def test_executive_metrics_aggregation(db_session: Session):
    """Calculates overall compliance rate, breakdown, and violation summary."""
    insp1 = Inspection(
        inspection_number=f"INS-MET-001-{uuid.uuid4().hex[:4]}",
        inspector_id="mock-inspector-id",
        district="Mumbai",
        state="Maharashtra",
        status="completed",
        compliance_status="compliant",
    )
    insp2 = Inspection(
        inspection_number=f"INS-MET-002-{uuid.uuid4().hex[:4]}",
        inspector_id="mock-inspector-id",
        district="Mumbai",
        state="Maharashtra",
        status="completed",
        compliance_status="non_compliant",
    )
    db_session.add_all([insp1, insp2])
    db_session.flush()

    viol = Violation(
        inspection_id=str(insp2.id),
        rule_code="LM_RULE_6_1_E_MRP",
        field_affected="mrp",
        section_violated="Rule 6(1)(e)",
        violation_title="Missing MRP",
        violation_description="Missing MRP",
        severity="critical",
    )
    db_session.add(viol)
    db_session.flush()

    metrics = analytics_service.get_executive_metrics(db=db_session)
    assert metrics["total_inspections"] >= 2
    assert "compliance_rate_percentage" in metrics
    assert metrics["violations_summary"]["total_violations"] >= 1
    assert metrics["violations_summary"]["critical"] >= 1


# ===========================================================================
# Test 2 — Compliance Trends Time-Series
# ===========================================================================
def test_compliance_trends_time_series(db_session: Session):
    """Calculates daily time-series inspection counts."""
    trends = analytics_service.get_compliance_trends(db=db_session, days=30)
    assert isinstance(trends, list)
    if trends:
        assert "date" in trends[0]
        assert "total_inspections" in trends[0]
        assert "compliance_rate" in trends[0]


# ===========================================================================
# Test 3 — Top Statutory Violations Breakdown
# ===========================================================================
def test_top_statutory_violations_breakdown(db_session: Session):
    """Ranks and formats top breached statutory rules."""
    top_viols = analytics_service.get_top_statutory_violations(db=db_session, limit=5)
    assert isinstance(top_viols, list)
    if top_viols:
        assert "rule_code" in top_viols[0]
        assert "violation_count" in top_viols[0]
        assert "percentage_of_total" in top_viols[0]


# ===========================================================================
# Test 4 — Jurisdiction Heatmap Computation
# ===========================================================================
def test_jurisdiction_heatmap_computation(db_session: Session):
    """Groups inspections by district and computes compliance statistics."""
    heatmap = analytics_service.get_jurisdiction_heatmap(db=db_session)
    assert isinstance(heatmap, list)
    if heatmap:
        assert "district" in heatmap[0]
        assert "state" in heatmap[0]
        assert "compliance_rate" in heatmap[0]


# ===========================================================================
# Test 5 — Repeat Offenders Leaderboard
# ===========================================================================
def test_repeat_offenders_leaderboard(db_session: Session):
    """Ranks repeat offending manufacturers."""
    leaderboard = analytics_service.get_repeat_offenders_leaderboard(db=db_session, limit=10)
    assert isinstance(leaderboard, list)


# ===========================================================================
# Test 6 — GET /api/v1/dashboard/metrics Endpoint (200)
# ===========================================================================
def test_get_dashboard_metrics_api_endpoint_200(client: TestClient, inspector_token_headers: dict):
    """GET /dashboard/metrics returns 200 with executive KPIs."""
    resp = client.get("/api/v1/dashboard/metrics", headers=inspector_token_headers)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()
    assert "total_inspections" in data
    assert "compliance_rate_percentage" in data
    assert "violations_summary" in data


# ===========================================================================
# Test 7 — GET /api/v1/dashboard/trends Endpoint (200)
# ===========================================================================
def test_get_dashboard_trends_api_endpoint_200(client: TestClient, inspector_token_headers: dict):
    """GET /dashboard/trends returns 200 with time-series array."""
    resp = client.get("/api/v1/dashboard/trends?days=14", headers=inspector_token_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ===========================================================================
# Test 8 — GET /api/v1/dashboard/top-violations Endpoint (200)
# ===========================================================================
def test_get_dashboard_top_violations_api_endpoint_200(client: TestClient, inspector_token_headers: dict):
    """GET /dashboard/top-violations returns 200."""
    resp = client.get("/api/v1/dashboard/top-violations?limit=5", headers=inspector_token_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ===========================================================================
# Test 9 — GET /api/v1/audit-logs Endpoint (200)
# ===========================================================================
def test_get_audit_logs_paginated_api_endpoint_200(client: TestClient, inspector_token_headers: dict, db_session: Session):
    """GET /audit-logs returns paginated list of immutable audit entries."""
    log = AuditLog(
        action="TEST_ACTION",
        entity_name="TestEntity",
        entity_id="test-id",
        details={"test": "data"},
    )
    db_session.add(log)
    db_session.commit()

    resp = client.get("/api/v1/audit-logs?limit=10", headers=inspector_token_headers)
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1


# ===========================================================================
# Test 10 — POST /api/v1/inspections/batch-sync Endpoint (200)
# ===========================================================================
def test_post_batch_sync_api_endpoint_200(client: TestClient, inspector_token_headers: dict):
    """POST /inspections/batch-sync synchronizes offline field inspection queue."""
    offline_uuid = str(uuid.uuid4())
    sync_payload = {
        "inspections": [
            {
                "client_offline_id": offline_uuid,
                "store_name": "Rural Grocery Mart",
                "store_address": "Village Square, Post Khed",
                "district": "Ratnagiri",
                "state": "Maharashtra",
                "gps_latitude": 17.7478,
                "gps_longitude": 73.3934,
                "product_name": "Gram Flour 500g",
                "brand_name": "Khed Mills",
                "ocr_raw_text": (
                    "KHED MILLS GRAM FLOUR 500g\n"
                    "MRP Rs. 45.00 (incl. of all taxes)\n"
                    "NET WT: 500 g\n"
                    "MFD: 02/2026\n"
                    "EXP: 12/2026\n"
                    "BATCH: KM-2026\n"
                    "MFG BY: Khed Mills Pvt Ltd, Ratnagiri, Maharashtra 415612\n"
                    "CONSUMER CARE: 1800-444-2222 care@khedmills.in\n"
                ),
            }
        ]
    }

    resp = client.post(
        "/api/v1/inspections/batch-sync",
        json=sync_payload,
        headers=inspector_token_headers,
    )
    assert resp.status_code == 200, f"Expected 200: {resp.text}"
    data = resp.json()

    assert data["total_submitted"] == 1
    assert data["successfully_synced"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["client_offline_id"] == offline_uuid
    assert data["results"][0]["is_synced"] is True
    assert data["results"][0]["compliance_status"] == "compliant"
