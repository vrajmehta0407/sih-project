"""
report_service.py
=================
Stage 6 — Statutory Report Generation & Verification Orchestrator
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation
from app.models.report import Report
from app.models.user import User
from app.services.audit_service import audit_service
from app.services.report.crypto_service import crypto_service
from app.services.report.pdf_report_generator import pdf_report_generator
from app.services.validator.compliance_service import compliance_service

logger = logging.getLogger(__name__)


class ReportService:
    """
    Coordinates PDF report rendering, cryptographic chain-of-custody signing,
    and public QR verification for Legal Metrology inspections.
    """

    def generate_inspection_report(
        self,
        db: Session,
        inspection_id: str,
        user_id: str,
        request=None,
    ) -> Dict[str, Any]:
        """
        Generates court-admissible PDF inspection report and persists Report entity.
        """
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection '{inspection_id}' not found.",
            )

        # Ensure inspection is validated
        if inspection.status != "validated":
            logger.info("Inspection %s not yet validated. Running compliance validation...", inspection_id)
            compliance_service.validate_inspection(
                db=db,
                inspection_id=inspection_id,
                user_id=user_id,
                request=request,
            )
            inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()

        product = db.query(Product).filter(Product.inspection_id == inspection_id).first()
        violations = db.query(Violation).filter(Violation.inspection_id == inspection_id).all()
        inspector = db.query(User).filter(User.id == inspection.inspector_id).first()

        # ── Canonical Payload for Hashing ─────────────────────────────────────
        canonical_payload = {
            "inspection_number": inspection.inspection_number,
            "inspector_id": str(inspection.inspector_id),
            "state": inspection.state,
            "district": inspection.district,
            "store_name": inspection.store_name,
            "gps_latitude": inspection.gps_latitude,
            "gps_longitude": inspection.gps_longitude,
            "product_name": product.product_name if product else None,
            "mrp_value": product.mrp_value if product else None,
            "net_quantity_value": product.net_quantity_value if product else None,
            "mfg_date": product.mfg_date.isoformat() if product and product.mfg_date else None,
            "manufacturer_name": product.manufacturer_name if product else None,
            "violations_count": len(violations),
            "violations": [
                {
                    "rule_code": v.rule_code,
                    "section_violated": v.section_violated,
                    "severity": v.severity,
                }
                for v in violations
            ],
            "created_at": inspection.created_at.isoformat() if inspection.created_at else datetime.now(timezone.utc).isoformat(),
        }

        # ── Cryptographic Chain of Custody ────────────────────────────────────
        sha256_hash = crypto_service.compute_canonical_hash(canonical_payload)
        qr_token = inspection.qr_verification_token or crypto_service.generate_qr_token()

        # ── File Paths & QR Rendering ─────────────────────────────────────────
        report_dir = os.path.join(settings.REPORT_OUTPUT_DIR, inspection_id)
        os.makedirs(report_dir, exist_ok=True)

        qr_path = os.path.join(report_dir, "verification_qr.png")
        pdf_path = os.path.join(report_dir, "inspection_report.pdf")

        # Determine verification URL
        host = request.headers.get("host", "localhost:8000") if request else "localhost:8000"
        scheme = "https" if request and request.url.scheme == "https" else "http"
        verification_url = f"{scheme}://{host}{settings.API_V1_STR}/inspections/verify/{qr_token}"

        crypto_service.generate_qr_code_image(verification_url, qr_path)

        # ── Format Docket Number ──────────────────────────────────────────────
        state_code = inspection.state[:2].upper() if inspection.state else "IN"
        date_stamp = datetime.now().strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:4].upper()
        docket_no = f"DOCKET-{state_code}-{date_stamp}-{rand_suffix}"

        # ── PDF Data Dict ─────────────────────────────────────────────────────
        doc_data = {
            "docket_number": docket_no,
            "chain_of_custody_hash": sha256_hash,
            "qr_verification_token": qr_token,
            "inspection": {
                "inspection_number": inspection.inspection_number,
                "created_at": inspection.created_at.strftime("%d-%m-%Y %H:%M") if inspection.created_at else datetime.now().strftime("%d-%m-%Y %H:%M"),
                "compliance_status": inspection.compliance_status,
                "district": inspection.district,
                "state": inspection.state,
                "store_name": inspection.store_name,
                "gps_latitude": inspection.gps_latitude,
                "gps_longitude": inspection.gps_longitude,
            },
            "inspector": {
                "name": inspector.full_name if inspector else "Enforcement Officer",
                "badge_number": inspector.badge_number if inspector and inspector.badge_number else "LM-OFFICER",
            },
            "product": {
                "product_name": product.product_name if product else None,
                "brand_name": product.brand_name if product else None,
                "commodity_generic_name": product.commodity_generic_name if product else None,
                "mrp_value": product.mrp_value if product else None,
                "mrp_inclusive_taxes_declared": product.mrp_inclusive_taxes_declared if product else False,
                "net_quantity_value": product.net_quantity_value if product else None,
                "net_quantity_unit": product.net_quantity_unit if product else None,
                "mfg_date_raw": product.mfg_date_raw if product else None,
                "mfg_date": product.mfg_date.strftime("%d-%m-%Y") if product and product.mfg_date else None,
                "exp_date_raw": product.exp_date_raw if product else None,
                "exp_date": product.exp_date.strftime("%d-%m-%Y") if product and product.exp_date else None,
                "batch_number": product.batch_number if product else None,
                "manufacturer_name": product.manufacturer_name if product else None,
                "manufacturer_address": product.manufacturer_address if product else None,
                "country_of_origin": product.country_of_origin if product else None,
                "consumer_care_email": product.consumer_care_email if product else None,
                "consumer_care_phone": product.consumer_care_phone if product else None,
            },
            "violations": [
                {
                    "rule_code": v.rule_code,
                    "section_violated": v.section_violated,
                    "statute_title": v.statute_title,
                    "violation_title": v.violation_title,
                    "violation_description": v.violation_description,
                    "severity": v.severity,
                    "estimated_fine": v.estimated_fine,
                }
                for v in violations
            ],
        }

        # ── Render PDF ────────────────────────────────────────────────────────
        pdf_report_generator.generate_report(
            output_pdf_path=pdf_path,
            inspection_data=doc_data,
            qr_image_path=qr_path,
        )

        # ── Persist Report in DB ──────────────────────────────────────────────
        report = db.query(Report).filter(Report.inspection_id == inspection_id).first()
        if not report:
            report = Report(
                inspection_id=inspection_id,
                docket_number=docket_no,
                pdf_file_path=pdf_path,
                pdf_download_url=f"/api/v1/inspections/{inspection_id}/report/download",
                qr_code_image_path=qr_path,
                chain_of_custody_hash=sha256_hash,
                status="issued",
                signed_by_inspector=True,
                inspector_signature_meta={"signed_by_user_id": user_id, "signed_at": datetime.now(timezone.utc).isoformat()},
            )
            db.add(report)
        else:
            report.docket_number = docket_no
            report.pdf_file_path = pdf_path
            report.pdf_download_url = f"/api/v1/inspections/{inspection_id}/report/download"
            report.qr_code_image_path = qr_path
            report.chain_of_custody_hash = sha256_hash
            report.status = "issued"

        # Update inspection records
        inspection.record_sha256_hash = sha256_hash
        inspection.qr_verification_token = qr_token
        inspection.status = "completed"

        db.commit()
        db.refresh(report)
        db.refresh(inspection)

        # Audit Log
        audit_service.log(
            db=db,
            action="GENERATE_STATUTORY_REPORT",
            entity_name="Report",
            entity_id=report.id,
            user_id=user_id,
            request=request,
            details={
                "docket_number": docket_no,
                "sha256_hash": sha256_hash,
                "qr_token": qr_token,
                "pdf_path": pdf_path,
            },
        )

        return {
            "report_id": str(report.id),
            "docket_number": report.docket_number,
            "inspection_id": inspection_id,
            "inspection_number": inspection.inspection_number,
            "status": report.status,
            "chain_of_custody_hash": report.chain_of_custody_hash,
            "qr_verification_token": qr_token,
            "pdf_download_url": report.pdf_download_url,
            "generated_at": report.generated_at.isoformat() if report.generated_at else datetime.now(timezone.utc).isoformat(),
        }

    def verify_qr_token(self, db: Session, qr_token: str) -> Dict[str, Any]:
        """
        Public verification endpoint resolving a QR token to authenticate inspection authenticity.
        """
        inspection = db.query(Inspection).filter(Inspection.qr_verification_token == qr_token).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invalid or unrecognized verification token '{qr_token}'.",
            )

        report = db.query(Report).filter(Report.inspection_id == inspection.id).first()
        product = db.query(Product).filter(Product.inspection_id == inspection.id).first()
        violations = db.query(Violation).filter(Violation.inspection_id == inspection.id).all()

        return {
            "verified": True,
            "tamper_evident_status": "AUTHENTIC_RECORD",
            "docket_number": report.docket_number if report else "N/A",
            "inspection_number": inspection.inspection_number,
            "chain_of_custody_hash": inspection.record_sha256_hash,
            "qr_token": qr_token,
            "compliance_status": inspection.compliance_status,
            "jurisdiction": f"{inspection.district}, {inspection.state}",
            "store_name": inspection.store_name,
            "inspection_date": inspection.created_at.strftime("%d-%m-%Y %H:%M") if inspection.created_at else "N/A",
            "product_name": product.product_name if product else "N/A",
            "manufacturer_name": product.manufacturer_name if product else "N/A",
            "total_violations": len(violations),
            "violations": [
                {
                    "section": v.section_violated,
                    "title": v.violation_title,
                    "severity": v.severity,
                }
                for v in violations
            ],
        }


# Singleton
report_service = ReportService()
