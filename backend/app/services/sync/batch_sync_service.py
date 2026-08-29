"""
batch_sync_service.py
=====================
Stage 7 — Offline Field Inspection Queue Batch Synchronizer
"""

import uuid
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation
from app.schemas.sync import BatchSyncRequest, BatchSyncResponse, BatchSyncResultItem
from app.services.audit_service import audit_service
from app.services.extractor.declaration_extractor import declaration_extractor
from app.services.validator.compliance_service import compliance_service

logger = logging.getLogger(__name__)


class BatchSyncService:
    """
    Processes queues of offline inspection packages collected on field devices.
    """

    def sync_offline_inspections(
        self,
        db: Session,
        payload: BatchSyncRequest,
        user_id: str,
        request=None,
    ) -> Dict[str, Any]:
        """
        Synchronizes a list of offline inspection records idempotently.
        """
        synced_results: List[Dict[str, Any]] = []
        success_count = 0
        failed_count = 0

        for item in payload.inspections:
            try:
                # Check for idempotent duplicate by matching offline ID prefix in inspection_number
                offline_prefix = f"INS-OFF-{item.client_offline_id[:8].upper()}"
                existing_insp = db.query(Inspection).filter(
                    Inspection.inspection_number.like(f"{offline_prefix}%")
                ).first()

                if existing_insp:
                    # Already synced
                    viol_count = db.query(Violation).filter(Violation.inspection_id == existing_insp.id).count()
                    synced_results.append({
                        "client_offline_id": item.client_offline_id,
                        "inspection_id": str(existing_insp.id),
                        "inspection_number": existing_insp.inspection_number,
                        "status": existing_insp.status,
                        "compliance_status": existing_insp.compliance_status,
                        "violations_count": viol_count,
                        "is_synced": True,
                        "message": "Already synchronized (idempotent match).",
                    })
                    success_count += 1
                    continue

                # Generate new inspection number
                insp_number = f"{offline_prefix}-{uuid.uuid4().hex[:4].upper()}"

                created_time = item.offline_captured_at or datetime.now(timezone.utc)
                if created_time.tzinfo is None:
                    created_time = created_time.replace(tzinfo=timezone.utc)

                inspection = Inspection(
                    inspection_number=insp_number,
                    inspector_id=user_id,
                    store_name=item.store_name,
                    store_address=item.store_address,
                    district=item.district,
                    state=item.state,
                    gps_latitude=item.gps_latitude,
                    gps_longitude=item.gps_longitude,
                    created_at=created_time,
                    status="pending",
                    compliance_status="pending",
                )
                db.add(inspection)
                db.flush()

                product = Product(
                    inspection_id=str(inspection.id),
                    product_name=item.product_name,
                    brand_name=item.brand_name,
                    paddle_raw_text=item.ocr_raw_text,
                    tesseract_raw_text=item.ocr_raw_text,
                )
                db.add(product)
                db.flush()

                # If offline device submitted OCR text, run extraction and validation pipeline
                if item.ocr_raw_text and len(item.ocr_raw_text.strip()) > 5:
                    decl = declaration_extractor.extract_from_text(item.ocr_raw_text)

                    product.mrp_raw = decl.mrp_raw
                    product.mrp_value = decl.mrp_value
                    product.mrp_currency = decl.mrp_currency
                    product.mrp_inclusive_taxes_declared = decl.mrp_inclusive_taxes_declared

                    product.net_quantity_raw = decl.net_quantity_raw
                    product.net_quantity_value = decl.net_quantity_value
                    product.net_quantity_unit = decl.net_quantity_unit

                    product.unit_sale_price_raw = decl.unit_sale_price_raw
                    product.unit_sale_price_value = decl.unit_sale_price_value

                    product.mfg_date_raw = decl.mfg_date_raw
                    product.mfg_date = decl.mfg_date
                    product.exp_date_raw = decl.exp_date_raw
                    product.exp_date = decl.exp_date

                    product.batch_number = decl.batch_number
                    product.manufacturer_name = decl.manufacturer_name or item.brand_name
                    product.manufacturer_address = decl.manufacturer_address
                    product.country_of_origin = decl.country_of_origin
                    product.consumer_care_email = decl.consumer_care_email
                    product.consumer_care_phone = decl.consumer_care_phone
                    product.consumer_care_address = decl.consumer_care_address

                    inspection.status = "extracted"
                    db.commit()

                    # Execute statutory compliance validation
                    val_res = compliance_service.validate_inspection(
                        db=db,
                        inspection_id=str(inspection.id),
                        user_id=user_id,
                        request=request,
                    )

                    synced_results.append({
                        "client_offline_id": item.client_offline_id,
                        "inspection_id": str(inspection.id),
                        "inspection_number": inspection.inspection_number,
                        "status": inspection.status,
                        "compliance_status": inspection.compliance_status,
                        "violations_count": val_res["summary"]["total_violations"],
                        "is_synced": True,
                        "message": "Successfully synchronized, extracted, and validated.",
                    })
                else:
                    db.commit()
                    synced_results.append({
                        "client_offline_id": item.client_offline_id,
                        "inspection_id": str(inspection.id),
                        "inspection_number": inspection.inspection_number,
                        "status": inspection.status,
                        "compliance_status": inspection.compliance_status,
                        "violations_count": 0,
                        "is_synced": True,
                        "message": "Synchronized without OCR text.",
                    })

                success_count += 1

            except Exception as exc:
                logger.error("Error syncing offline inspection %s: %s", item.client_offline_id, exc)
                db.rollback()
                failed_count += 1
                synced_results.append({
                    "client_offline_id": item.client_offline_id,
                    "inspection_id": "",
                    "inspection_number": "",
                    "status": "failed",
                    "compliance_status": "error",
                    "violations_count": 0,
                    "is_synced": False,
                    "message": str(exc),
                })

        # Audit Log
        audit_service.log(
            db=db,
            action="BATCH_SYNC_OFFLINE_INSPECTIONS",
            entity_name="Inspection",
            entity_id=user_id,
            user_id=user_id,
            request=request,
            details={
                "total_submitted": len(payload.inspections),
                "successfully_synced": success_count,
                "failed_count": failed_count,
            },
        )

        return {
            "total_submitted": len(payload.inspections),
            "successfully_synced": success_count,
            "failed_count": failed_count,
            "results": synced_results,
        }


# Singleton
batch_sync_service = BatchSyncService()
