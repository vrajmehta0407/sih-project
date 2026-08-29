"""
compliance_service.py
=====================
Stage 5 — Inspection Statutory Compliance Validation & Violation Dockets Orchestrator
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.rule import Rule, RuleVersion
from app.models.violation import Violation
from app.services.audit_service import audit_service
from app.services.validator.rules_evaluator import rules_evaluator, EvaluatedViolation
from app.services.validator.repeat_offender_service import repeat_offender_service
from app.services.extractor.extraction_service import extraction_service

logger = logging.getLogger(__name__)


class ComplianceService:
    """
    Coordinates compliance rule evaluation, repeat offender detection, and
    violation record persistence for field inspections.
    """

    def validate_inspection(
        self,
        db: Session,
        inspection_id: str,
        user_id: str,
        request=None,
    ) -> Dict[str, Any]:
        """
        Runs the full statutory validation lifecycle on an inspection.
        """
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection '{inspection_id}' not found.",
            )

        product = db.query(Product).filter(Product.inspection_id == inspection_id).first()

        # If product declarations have not been extracted, trigger extraction first
        if not product or (
            product.mrp_value is None
            and product.net_quantity_value is None
            and product.manufacturer_name is None
        ):
            logger.info("Product declarations not found for inspection %s. Triggering extractor...", inspection_id)
            extraction_service.extract_declarations_for_inspection(
                db=db,
                inspection_id=inspection_id,
                user_id=user_id,
                request=request,
            )
            product = db.query(Product).filter(Product.inspection_id == inspection_id).first()

        # Fetch active rule version and rules
        active_version = None
        if inspection.rule_version_id:
            active_version = db.query(RuleVersion).filter(RuleVersion.id == inspection.rule_version_id).first()
        if not active_version:
            active_version = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()

        rules = []
        if active_version:
            inspection.rule_version_id = active_version.id
            rules = db.query(Rule).filter(Rule.version_id == active_version.id, Rule.is_active == True).all()

        # Run statutory rules evaluator
        inspection_date = inspection.created_at.date() if inspection.created_at else datetime.now(timezone.utc).date()
        evaluated_violations: List[EvaluatedViolation] = rules_evaluator.evaluate_product(
            product=product,
            rules=rules,
            inspection_date=inspection_date,
        )

        # Check repeat offender history
        repeat_info = repeat_offender_service.check_repeat_offender_status(
            db=db,
            current_inspection_id=inspection_id,
            manufacturer_name=product.manufacturer_name,
            brand_name=product.brand_name,
            store_name=inspection.store_name,
        )

        # Clear any prior violation records for this inspection to maintain idempotency
        db.query(Violation).filter(Violation.inspection_id == inspection_id).delete()

        persisted_violations: List[Violation] = []
        critical_count = 0
        major_count = 0
        minor_count = 0

        for ev in evaluated_violations:
            fine_amount = (
                repeat_info["escalated_penalty"]
                if repeat_info["is_repeat_offender"]
                else ev.estimated_fine
            )

            violation = Violation(
                inspection_id=inspection_id,
                rule_id=ev.rule_id,
                rule_code=ev.rule_code,
                field_affected=ev.field_affected,
                section_violated=ev.section_violated,
                statute_title=ev.statute_title,
                penalty_provision=ev.penalty_provision,
                estimated_fine=fine_amount,
                violation_title=ev.violation_title,
                violation_description=ev.violation_description,
                severity=ev.severity,
                is_repeat_offender_alert=repeat_info["is_repeat_offender"],
            )
            db.add(violation)
            persisted_violations.append(violation)

            if ev.severity == "critical":
                critical_count += 1
            elif ev.severity == "major":
                major_count += 1
            else:
                minor_count += 1

        # Determine compliance status
        if product.has_ocr_disagreement or product.manual_review_required:
            inspection.compliance_status = "review_required"
        elif len(persisted_violations) == 0:
            inspection.compliance_status = "compliant"
        else:
            inspection.compliance_status = "non_compliant"

        inspection.status = "validated"

        db.commit()
        db.refresh(inspection)

        # Audit Log
        audit_service.log(
            db=db,
            action="VALIDATE_COMPLIANCE",
            entity_name="Inspection",
            entity_id=inspection_id,
            user_id=user_id,
            request=request,
            details={
                "inspection_number": inspection.inspection_number,
                "compliance_status": inspection.compliance_status,
                "violations_total": len(persisted_violations),
                "critical": critical_count,
                "major": major_count,
                "minor": minor_count,
                "is_repeat_offender": repeat_info["is_repeat_offender"],
            },
        )

        return {
            "inspection_id": inspection_id,
            "inspection_number": inspection.inspection_number,
            "status": inspection.status,
            "compliance_status": inspection.compliance_status,
            "summary": {
                "total_violations": len(persisted_violations),
                "critical_violations": critical_count,
                "major_violations": major_count,
                "minor_violations": minor_count,
                "is_repeat_offender": repeat_info["is_repeat_offender"],
                "prior_offence_count": repeat_info["prior_violations_count"],
                "prior_inspections": repeat_info["prior_inspection_numbers"],
            },
            "violations": [
                {
                    "id": str(v.id),
                    "rule_code": v.rule_code,
                    "field_affected": v.field_affected,
                    "section_violated": v.section_violated,
                    "statute_title": v.statute_title,
                    "penalty_provision": v.penalty_provision,
                    "estimated_fine": v.estimated_fine,
                    "violation_title": v.violation_title,
                    "violation_description": v.violation_description,
                    "severity": v.severity,
                    "is_repeat_offender_alert": v.is_repeat_offender_alert,
                }
                for v in persisted_violations
            ],
        }


# Singleton
compliance_service = ComplianceService()
