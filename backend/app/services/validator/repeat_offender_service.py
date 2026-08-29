"""
repeat_offender_service.py
==========================
Stage 5 — Repeat Offender Intelligence & Cross-Inspection Tracker

Checks historical enforcement data across the database to detect repeat statutory infractions
by the same manufacturer, brand, or retail outlet, escalating penalties under Section 36(2) of
the Legal Metrology Act, 2009.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation


class RepeatOffenderService:
    """
    Analyzes historical violations across inspections for manufacturer / brand recidivism.
    """

    def check_repeat_offender_status(
        self,
        db: Session,
        current_inspection_id: str,
        manufacturer_name: Optional[str] = None,
        brand_name: Optional[str] = None,
        store_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Queries database for prior non-compliant inspections matching the manufacturer,
        brand, or store name.
        """
        if not manufacturer_name and not brand_name and not store_name:
            return {
                "is_repeat_offender": False,
                "prior_violations_count": 0,
                "prior_inspection_numbers": [],
                "escalated_penalty": None,
            }

        # Find previous inspection IDs matching manufacturer or brand
        query = (
            db.query(Inspection.inspection_number, Violation.rule_code)
            .join(Product, Product.inspection_id == Inspection.id)
            .join(Violation, Violation.inspection_id == Inspection.id)
            .filter(Inspection.id != current_inspection_id)
            .filter(Inspection.compliance_status == "non_compliant")
        )

        filters = []
        if manufacturer_name and len(manufacturer_name) >= 3:
            # Case-insensitive substring match
            filters.append(Product.manufacturer_name.ilike(f"%{manufacturer_name.strip()}%"))
        if brand_name and len(brand_name) >= 3:
            filters.append(Product.brand_name.ilike(f"%{brand_name.strip()}%"))
        if store_name and len(store_name) >= 3:
            filters.append(Inspection.store_name.ilike(f"%{store_name.strip()}%"))

        if not filters:
            return {
                "is_repeat_offender": False,
                "prior_violations_count": 0,
                "prior_inspection_numbers": [],
                "escalated_penalty": None,
            }

        from sqlalchemy import or_
        query = query.filter(or_(*filters))

        results = query.all()

        if results:
            prior_insp_numbers = list({r[0] for r in results})
            return {
                "is_repeat_offender": True,
                "prior_violations_count": len(results),
                "prior_inspection_numbers": prior_insp_numbers,
                "escalated_penalty": (
                    "Section 36(2), Legal Metrology Act 2009: Fine up to ₹50,000 "
                    "or imprisonment up to 1 year for second/subsequent offence"
                ),
            }

        return {
            "is_repeat_offender": False,
            "prior_violations_count": 0,
            "prior_inspection_numbers": [],
            "escalated_penalty": None,
        }


# Singleton
repeat_offender_service = RepeatOffenderService()
