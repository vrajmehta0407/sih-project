"""
endpoints/dashboard.py
======================
Stage 7 — Executive Analytics & Officer Dashboard Endpoints
"""

import csv
import io
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session

from app.core.security import require_inspector
from app.db.session import get_db
from app.models.inspection import Inspection
from app.services.dashboard.analytics_service import analytics_service
from app.schemas.dashboard import (
    ExecutiveMetricsResponse,
    TrendItemSchema,
    TopViolationItemSchema,
    JurisdictionHeatmapItemSchema,
    RepeatOffenderLeaderboardItemSchema,
)
from app.schemas.predictive_dispatch import (
    PredictiveHotspotsResponse,
    RaidRouteDispatchRequest,
    RaidRouteDispatchResponse,
)
from app.services.predictive_dispatch_service import predictive_dispatch_service

router = APIRouter()


@router.get(
    "/metrics",
    response_model=ExecutiveMetricsResponse,
    summary="Get Executive Compliance KPIs",
    description="Retrieves aggregate compliance rates, severity breakdowns, and penalty estimates.",
)
def get_dashboard_metrics(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    return analytics_service.get_executive_metrics(db=db, state=state, district=district)


@router.get(
    "/trends",
    response_model=List[TrendItemSchema],
    summary="Get Time-Series Compliance Trends",
    description="Returns daily inspection volumes, compliant counts, and compliance rates.",
)
def get_dashboard_trends(
    days: int = Query(30, ge=1, le=365, description="Number of historical days to analyze"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    return analytics_service.get_compliance_trends(db=db, days=days)


@router.get(
    "/top-violations",
    response_model=List[TopViolationItemSchema],
    summary="Get Top Statutory Violations",
    description="Returns most frequently breached rules under Legal Metrology PCR 2011.",
)
def get_top_violations(
    limit: int = Query(5, ge=1, le=50, description="Max violations to return"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    return analytics_service.get_top_statutory_violations(db=db, limit=limit)


@router.get(
    "/jurisdiction-heatmap",
    response_model=List[JurisdictionHeatmapItemSchema],
    summary="Get GIS Jurisdiction Compliance Heatmap",
    description="Computes district and state-level compliance statistics and average GPS centroids for GIS mapping.",
)
def get_jurisdiction_heatmap(
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    return analytics_service.get_jurisdiction_heatmap(db=db)


@router.get(
    "/repeat-offenders",
    response_model=List[RepeatOffenderLeaderboardItemSchema],
    summary="Get Repeat Offenders Leaderboard",
    description="Tracks manufacturers and brands with highest repeat infraction frequency.",
)
def get_repeat_offenders(
    limit: int = Query(10, ge=1, le=100, description="Max offenders to list"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    return analytics_service.get_repeat_offenders_leaderboard(db=db, limit=limit)


# ===========================================================================
# Forensic Enforcement Data Export Endpoints (CSV & JSON)
# ===========================================================================

@router.get(
    "/export/csv",
    summary="Export Inspection Dockets & Enforcement Data to CSV",
)
def export_inspections_csv(
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Export all inspection dockets with compliance status, statutory violations count,
    adjudication details, and officer badge numbers as a downloadable CSV.
    """
    inspections = db.query(Inspection).order_by(Inspection.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Inspection ID",
        "Inspection Number",
        "Product Name",
        "Manufacturer Name",
        "Compliance Status",
        "Total Violations",
        "Adjudication Status",
        "Compounding Amount (INR)",
        "State",
        "District",
        "Created At (UTC)",
    ])

    for insp in inspections:
        prod_name = insp.product.product_name if insp.product else "N/A"
        mfg_name = insp.product.manufacturer_name if insp.product else "N/A"
        v_count = len(insp.violations) if insp.violations else 0
        writer.writerow([
            str(insp.id),
            insp.inspection_number,
            prod_name,
            mfg_name,
            insp.compliance_status,
            v_count,
            insp.adjudication_status or "OPEN",
            insp.compounding_amount or 0.0,
            insp.state or "N/A",
            insp.district or "N/A",
            insp.created_at.isoformat() if insp.created_at else "",
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=legal_metrology_inspections_export.csv"},
    )


@router.get(
    "/export/json",
    summary="Export Complete Enforcement Audit Trail to JSON",
)
def export_inspections_json(
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Export all inspection dossiers with detailed violation descriptions,
    statutory Rule 6 extractions, and adjudication records as structured JSON.
    """
    inspections = db.query(Inspection).order_by(Inspection.created_at.desc()).all()

    results = []
    for insp in inspections:
        prod_name = insp.product.product_name if insp.product else None
        mfg_name = insp.product.manufacturer_name if insp.product else None
        violations_data = [
            {
                "rule_code": v.rule_code,
                "violation_title": v.violation_title,
                "severity": v.severity,
                "description": v.violation_description,
                "section_violated": v.section_violated,
            }
            for v in (insp.violations or [])
        ]
        results.append({
            "inspection_id": str(insp.id),
            "inspection_number": insp.inspection_number,
            "product_name": prod_name,
            "manufacturer_name": mfg_name,
            "compliance_status": insp.compliance_status,
            "adjudication_status": insp.adjudication_status,
            "compounding_amount": insp.compounding_amount,
            "state": insp.state,
            "district": insp.district,
            "violations": violations_data,
            "created_at": insp.created_at.isoformat() if insp.created_at else None,
        })

    return JSONResponse(content={"total_records": len(results), "records": results})


# ===========================================================================
# Stage 20 — AI Predictive Risk Heatmaps & Automated Raid Dispatch
# ===========================================================================

@router.get(
    "/predictive-hotspots",
    response_model=PredictiveHotspotsResponse,
    summary="Get AI Market Vulnerability Index (MVI) Hotspots",
)
def get_predictive_hotspots(
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Compute dynamic Market Vulnerability Index (MVI) across commercial clusters in India
    by analyzing citizen grievances, repeat offenses, and past non-compliance.
    """
    return predictive_dispatch_service.get_predictive_hotspots(db=db)


@router.post(
    "/dispatch-raid-route",
    response_model=RaidRouteDispatchResponse,
    summary="Generate & Dispatch Tactical Inspection Patrol Itinerary",
)
def dispatch_raid_route(
    req: RaidRouteDispatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Automatically generate an optimal inspection patrol route sequencing high-risk retail
    targets for field teams with predicted statutory compounding recovery.
    """
    return predictive_dispatch_service.plan_raid_route(
        db=db,
        req=req,
        dispatched_by_email=current_user.email,
    )
