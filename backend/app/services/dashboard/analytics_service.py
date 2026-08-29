"""
analytics_service.py
====================
Stage 7 — Executive Analytics & Officer Dashboard Service

Provides high-performance aggregation queries for national/state legal metrology directors:
  1. Executive KPIs (Compliance rates, severity tally, repeat alerts, penalty liabilities)
  2. Time-series compliance trends
  3. Top statutory violated rules distribution
  4. Jurisdiction GIS enforcement heatmaps
  5. Repeat offender manufacturer leaderboard
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation


class AnalyticsService:
    """
    Computes real-time analytical metrics and enforcement KPIs.
    """

    def get_executive_metrics(
        self,
        db: Session,
        state: Optional[str] = None,
        district: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Aggregates high-level statutory compliance KPIs.
        """
        insp_q = db.query(Inspection)
        if state:
            insp_q = insp_q.filter(Inspection.state.ilike(f"%{state.strip()}%"))
        if district:
            insp_q = insp_q.filter(Inspection.district.ilike(f"%{district.strip()}%"))

        total_inspections = insp_q.count()
        compliant_count = insp_q.filter(Inspection.compliance_status == "compliant").count()
        non_compliant_count = insp_q.filter(Inspection.compliance_status == "non_compliant").count()
        review_required_count = insp_q.filter(Inspection.compliance_status == "review_required").count()
        pending_count = insp_q.filter(Inspection.compliance_status == "pending").count()

        compliance_rate = (
            round((compliant_count / total_inspections) * 100, 2)
            if total_inspections > 0
            else 100.0
        )

        # Status breakdown
        completed_count = insp_q.filter(Inspection.status == "completed").count()
        validated_count = insp_q.filter(Inspection.status == "validated").count()
        in_progress_count = total_inspections - completed_count - validated_count

        # Violations breakdown
        viol_q = db.query(Violation).join(Inspection, Inspection.id == Violation.inspection_id)
        if state:
            viol_q = viol_q.filter(Inspection.state.ilike(f"%{state.strip()}%"))
        if district:
            viol_q = viol_q.filter(Inspection.district.ilike(f"%{district.strip()}%"))

        total_violations = viol_q.count()
        critical_violations = viol_q.filter(Violation.severity == "critical").count()
        major_violations = viol_q.filter(Violation.severity == "major").count()
        minor_violations = viol_q.filter(Violation.severity == "minor").count()
        repeat_offender_alerts = viol_q.filter(Violation.is_repeat_offender_alert == True).count()

        return {
            "total_inspections": total_inspections,
            "compliance_rate_percentage": compliance_rate,
            "compliance_breakdown": {
                "compliant": compliant_count,
                "non_compliant": non_compliant_count,
                "review_required": review_required_count,
                "pending": pending_count,
            },
            "status_breakdown": {
                "completed": completed_count,
                "validated": validated_count,
                "in_progress": in_progress_count,
            },
            "violations_summary": {
                "total_violations": total_violations,
                "critical": critical_violations,
                "major": major_violations,
                "minor": minor_violations,
                "repeat_offender_alerts": repeat_offender_alerts,
            },
        }

    def get_compliance_trends(
        self,
        db: Session,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Calculates time-series daily inspection velocity and compliance rate.
        """
        since_date = datetime.now(timezone.utc) - timedelta(days=days)

        results = (
            db.query(
                func.date(Inspection.created_at).label("inspection_date"),
                func.count(Inspection.id).label("total"),
                func.sum(case((Inspection.compliance_status == "compliant", 1), else_=0)).label("compliant"),
                func.sum(case((Inspection.compliance_status == "non_compliant", 1), else_=0)).label("non_compliant"),
            )
            .filter(Inspection.created_at >= since_date)
            .group_by(func.date(Inspection.created_at))
            .order_by(func.date(Inspection.created_at).asc())
            .all()
        )

        trends = []
        for r in results:
            d_str = str(r.inspection_date)
            total = r.total or 0
            comp = r.compliant or 0
            non_comp = r.non_compliant or 0
            rate = round((comp / total) * 100, 2) if total > 0 else 100.0

            trends.append({
                "date": d_str,
                "total_inspections": total,
                "compliant_count": comp,
                "non_compliant_count": non_comp,
                "compliance_rate": rate,
            })

        return trends

    def get_top_statutory_violations(
        self,
        db: Session,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Identifies most frequently violated statutory rules and sections.
        """
        total_violations = db.query(Violation).count()

        results = (
            db.query(
                Violation.rule_code,
                Violation.section_violated,
                Violation.violation_title,
                Violation.severity,
                func.count(Violation.id).label("count"),
            )
            .group_by(
                Violation.rule_code,
                Violation.section_violated,
                Violation.violation_title,
                Violation.severity,
            )
            .order_by(desc("count"))
            .limit(limit)
            .all()
        )

        items = []
        for r in results:
            cnt = r.count
            pct = round((cnt / total_violations) * 100, 2) if total_violations > 0 else 0.0
            items.append({
                "rule_code": r.rule_code,
                "section_violated": r.section_violated,
                "violation_title": r.violation_title,
                "severity": r.severity,
                "violation_count": cnt,
                "percentage_of_total": pct,
            })

        return items

    def get_jurisdiction_heatmap(
        self,
        db: Session,
    ) -> List[Dict[str, Any]]:
        """
        Computes GIS district and state compliance statistics.
        """
        results = (
            db.query(
                Inspection.district,
                Inspection.state,
                func.count(Inspection.id).label("total"),
                func.sum(case((Inspection.compliance_status == "compliant", 1), else_=0)).label("compliant"),
                func.sum(case((Inspection.compliance_status == "non_compliant", 1), else_=0)).label("non_compliant"),
                func.avg(Inspection.gps_latitude).label("avg_lat"),
                func.avg(Inspection.gps_longitude).label("avg_lon"),
            )
            .filter(Inspection.district.isnot(None))
            .group_by(Inspection.district, Inspection.state)
            .order_by(desc("total"))
            .all()
        )

        heatmap = []
        for r in results:
            total = r.total or 0
            comp = r.compliant or 0
            rate = round((comp / total) * 100, 2) if total > 0 else 100.0

            heatmap.append({
                "district": r.district or "Unknown",
                "state": r.state or "Unknown",
                "total_inspections": total,
                "compliant_count": comp,
                "non_compliant_count": r.non_compliant or 0,
                "compliance_rate": rate,
                "centroid_latitude": float(r.avg_lat) if r.avg_lat is not None else None,
                "centroid_longitude": float(r.avg_lon) if r.avg_lon is not None else None,
            })

        return heatmap

    def get_repeat_offenders_leaderboard(
        self,
        db: Session,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Tracks manufacturers with highest recidivism rates across inspections.
        """
        results = (
            db.query(
                Product.manufacturer_name,
                Product.brand_name,
                func.count(Violation.id).label("violation_count"),
                func.count(func.distinct(Inspection.id)).label("inspection_count"),
                func.max(Inspection.created_at).label("last_inspection_date"),
            )
            .join(Inspection, Inspection.id == Product.inspection_id)
            .join(Violation, Violation.inspection_id == Inspection.id)
            .filter(Product.manufacturer_name.isnot(None))
            .group_by(Product.manufacturer_name, Product.brand_name)
            .order_by(desc("violation_count"))
            .limit(limit)
            .all()
        )

        leaderboard = []
        for r in results:
            leaderboard.append({
                "manufacturer_name": r.manufacturer_name,
                "brand_name": r.brand_name or "N/A",
                "total_violations": r.violation_count,
                "inspections_count": r.inspection_count,
                "last_inspection_date": r.last_inspection_date.strftime("%d-%m-%Y") if r.last_inspection_date else "N/A",
            })

        return leaderboard


# Singleton
analytics_service = AnalyticsService()
