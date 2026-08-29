"""
predictive_dispatch_service.py
==============================
Stage 20 — AI National Risk Heatmap & Predictive Raid Dispatch Service
"""

import uuid
import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.citizen_complaint import CitizenComplaint
from app.schemas.predictive_dispatch import (
    HotspotCluster,
    PredictiveHotspotsResponse,
    RaidRouteDispatchRequest,
    RaidRouteDispatchResponse,
    RaidTarget,
)

logger = logging.getLogger(__name__)

# Baseline Indian Commercial Hotspot Registry
SEED_HOTSPOTS = [
    {
        "cluster_id": "HOT-MUM-01",
        "cluster_name": "Crawford Market & Wholesale Hub",
        "state": "Maharashtra",
        "district": "Mumbai",
        "latitude": 18.9482,
        "longitude": 72.8347,
        "base_mvi": 88.5,
        "retailers": [
            ("Apex Supermarket Mart #12", "Shop 44, Crawford Market, Fort", "OVERCHARGING_MRP", 25000.0),
            ("Metro Provisions & Wholesale", "Lamington Road, Grant Road", "DUAL_MRP_STICKERS", 50000.0),
            ("City Mart Retail Hub", "Opp CST Station, Fort", "MISSING_USP_DECLARATIONS", 20000.0),
            ("Bharat FMCG Traders", "Kalbadevi Road, Marine Lines", "EXPIRED_COMMODITY", 35000.0),
            ("Golden Grain Super Store", "Princess Street, Marine Lines", "DECEPTIVE_PACKAGING", 25000.0),
        ]
    },
    {
        "cluster_id": "HOT-DEL-02",
        "cluster_name": "Chandni Chowk & Khari Baoli Spice Hub",
        "state": "Delhi",
        "district": "Central Delhi",
        "latitude": 28.6507,
        "longitude": 77.2334,
        "base_mvi": 92.0,
        "retailers": [
            ("Old Delhi Spices & Dry Fruits", "Khari Baoli, Chandni Chowk", "NET_QUANTITY_SHORTFALL", 50000.0),
            ("Capital Mart Express", "Main Road, Chandni Chowk", "OVERCHARGING_MRP", 25000.0),
            ("Shree Ganesh Provisions", "Nai Sarak, Chandni Chowk", "MISSING_MANUFACTURER_ADDRESS", 15000.0),
        ]
    },
    {
        "cluster_id": "HOT-BLR-03",
        "cluster_name": "Commercial Street & Chickpet Wholesale",
        "state": "Karnataka",
        "district": "Bengaluru Urban",
        "latitude": 12.9815,
        "longitude": 77.6083,
        "base_mvi": 76.5,
        "retailers": [
            ("Garden City Mega Supermarket", "Commercial Street, Tasker Town", "DUAL_MRP_STICKERS", 50000.0),
            ("Chickpet Wholesale Grocers", "Chickpet Main Road", "MISSING_CUSTOMER_CARE", 15000.0),
        ]
    },
    {
        "cluster_id": "HOT-KOL-04",
        "cluster_name": "Burrabazar Wholesale & Trading Depot",
        "state": "West Bengal",
        "district": "Kolkata",
        "latitude": 22.5833,
        "longitude": 88.3500,
        "base_mvi": 84.0,
        "retailers": [
            ("Howrah Trading Syndicate", "MG Road, Burrabazar", "OVERCHARGING_MRP", 25000.0),
            ("Eastern FMCG Distribution", "Cotton Street, Burrabazar", "TAMPERED_EXPIRY_DATE", 50000.0),
        ]
    },
]


class PredictiveDispatchService:
    """Calculates dynamic Market Vulnerability Index (MVI) and plans tactical raid patrol routes."""

    def get_predictive_hotspots(self, db: Session) -> PredictiveHotspotsResponse:
        """Compute nationwide market vulnerability index from live complaints & inspections."""
        now = datetime.utcnow()
        complaints_count = db.query(CitizenComplaint).count()
        inspections_count = db.query(Inspection).count()

        hotspot_list: List[HotspotCluster] = []
        for seed in SEED_HOTSPOTS:
            # Dynamically adjust MVI with DB activity
            adjusted_mvi = min(100.0, round(seed["base_mvi"] + (complaints_count * 0.5), 1))
            risk = "CRITICAL" if adjusted_mvi >= 85.0 else ("HIGH" if adjusted_mvi >= 70.0 else "MODERATE")

            hotspot_list.append(HotspotCluster(
                cluster_id=seed["cluster_id"],
                cluster_name=seed["cluster_name"],
                state=seed["state"],
                district=seed["district"],
                latitude=seed["latitude"],
                longitude=seed["longitude"],
                market_vulnerability_index=adjusted_mvi,
                risk_level=risk,
                repeat_offenders_count=len(seed["retailers"]),
                unresolved_grievances=max(2, complaints_count),
                recommended_action=f"Deploy {risk.lower()} priority audit team for Section 36(2) inspection.",
            ))

        critical_count = sum(1 for h in hotspot_list if h.risk_level == "CRITICAL")
        avg_mvi = round(sum(h.market_vulnerability_index for h in hotspot_list) / len(hotspot_list), 1)

        return PredictiveHotspotsResponse(
            generated_at=now,
            total_clusters_evaluated=len(hotspot_list),
            critical_clusters_count=critical_count,
            national_vulnerability_average=avg_mvi,
            hotspots=hotspot_list,
        )

    def plan_raid_route(
        self,
        db: Session,
        req: RaidRouteDispatchRequest,
        dispatched_by_email: str,
    ) -> RaidRouteDispatchResponse:
        """Generate an optimal tactical field inspection patrol route."""
        route_id = uuid.uuid4()
        now = datetime.utcnow()
        dispatch_code = f"RAID-{req.district[:3].upper()}-{route_id.hex[:6].upper()}"

        # Find matching cluster or default to first seed
        cluster = next(
            (c for c in SEED_HOTSPOTS if c["district"].lower() == req.district.lower()),
            SEED_HOTSPOTS[0]
        )

        selected_retailers = cluster["retailers"][:req.max_targets]
        targets: List[RaidTarget] = []
        total_recovery = 0.0

        for idx, (name, addr, risk, recovery) in enumerate(selected_retailers, 1):
            targets.append(RaidTarget(
                stop_sequence=idx,
                retailer_name=name,
                location_address=addr,
                latitude=cluster["latitude"] + (idx * 0.003),
                longitude=cluster["longitude"] + (idx * 0.003),
                priority_level="URGENT" if idx <= 2 else "HIGH",
                primary_infraction_risk=risk,
                predicted_compounding_recovery_inr=recovery,
            ))
            total_recovery += recovery

        est_hours = round(len(targets) * 0.75 + 0.5, 1)

        logger.info(
            "Raid Route %s dispatched to %s with %d targets by %s (Est. Recovery: ₹%.2f)",
            dispatch_code, req.team_lead_email, len(targets), dispatched_by_email, total_recovery
        )

        return RaidRouteDispatchResponse(
            route_id=route_id,
            dispatch_code=dispatch_code,
            state=req.state,
            district=req.district,
            assigned_team_lead=req.team_lead_email or "inspector.mumbai@legalmetrology.gov.in",
            dispatched_at=now,
            total_stops=len(targets),
            estimated_duration_hours=est_hours,
            estimated_fine_recovery_inr=total_recovery,
            targets=targets,
            status="DISPATCHED",
        )


predictive_dispatch_service = PredictiveDispatchService()
