"""
extraction_service.py
=====================
Stage 4 — Statutory Declarations Extraction Service & DB Persistence
"""

import logging
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.product import Product
from app.services.audit_service import audit_service
from app.services.extractor.declaration_extractor import declaration_extractor, ExtractedDeclarations
from app.services.ocr.ocr_service import ocr_service

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Coordinates extraction of statutory declarations under Rule 6 of LM PCR 2011
    from OCR consensus text and populates the Product entity.
    """

    def extract_declarations_for_inspection(
        self,
        db: Session,
        inspection_id: str,
        user_id: str,
        request=None,
    ) -> Dict[str, Any]:
        """
        Extracts all statutory declarations for an inspection.
        If OCR has not yet been executed, automatically runs the dual OCR pipeline first.
        """
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection '{inspection_id}' not found.",
            )

        product = db.query(Product).filter(Product.inspection_id == inspection_id).first()

        # Check if OCR consensus text is available; if not, trigger OCR
        ocr_text = ""
        if product and product.extracted_fields_consensus:
            ocr_text = product.extracted_fields_consensus.get("aggregated_consensus_text", "")

        if not ocr_text:
            if product and (product.paddle_raw_text or product.tesseract_raw_text):
                ocr_text = product.paddle_raw_text or product.tesseract_raw_text
            else:
                # Trigger OCR
                logger.info("No existing OCR text found for inspection %s. Triggering OCR...", inspection_id)
                ocr_res = ocr_service.process_inspection_ocr(
                    db=db,
                    inspection_id=inspection_id,
                    user_id=user_id,
                    request=request,
                )
                ocr_text = ocr_res["ocr_consensus"]["aggregated_consensus_text"]
                # Refresh product
                product = db.query(Product).filter(Product.inspection_id == inspection_id).first()

        if not ocr_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OCR extraction produced no readable text for this inspection.",
            )

        # Run declaration extraction engine
        decl: ExtractedDeclarations = declaration_extractor.extract_from_text(ocr_text)

        # Ensure product record exists
        if not product:
            product = Product(inspection_id=inspection_id)
            db.add(product)

        # Populate Product fields
        product.mrp_raw = decl.mrp_raw
        product.mrp_value = decl.mrp_value
        product.mrp_currency = decl.mrp_currency
        product.mrp_inclusive_taxes_declared = decl.mrp_inclusive_taxes_declared

        product.net_quantity_raw = decl.net_quantity_raw
        product.net_quantity_value = decl.net_quantity_value
        product.net_quantity_unit = decl.net_quantity_unit
        product.unit_sale_price_raw = decl.unit_sale_price_raw

        product.batch_number = decl.batch_number
        product.mfg_date_raw = decl.mfg_date_raw
        product.mfg_date = decl.mfg_date
        product.exp_date_raw = decl.exp_date_raw
        product.exp_date = decl.exp_date

        product.manufacturer_name = decl.manufacturer_name
        product.manufacturer_address = decl.manufacturer_address
        product.packer_name = decl.packer_name
        product.packer_address = decl.packer_address
        product.importer_name = decl.importer_name
        product.importer_address = decl.importer_address
        product.country_of_origin = decl.country_of_origin

        product.consumer_care_email = decl.consumer_care_email
        product.consumer_care_phone = decl.consumer_care_phone
        product.consumer_care_address = decl.consumer_care_address

        product.commodity_generic_name = decl.commodity_generic_name
        if decl.brand_name:
            product.brand_name = decl.brand_name

        # Advance inspection state to extracted
        if inspection.status in ("draft", "preprocessed"):
            inspection.status = "extracted"

        db.commit()
        db.refresh(product)
        db.refresh(inspection)

        # Audit Log
        audit_service.log(
            db=db,
            action="EXTRACT_STATUTORY_DECLARATIONS",
            entity_name="Product",
            entity_id=product.id,
            user_id=user_id,
            request=request,
            details={
                "inspection_number": inspection.inspection_number,
                "declared_count": decl.declared_fields_count,
                "missing_fields": decl.missing_mandatory_fields,
                "overall_confidence": round(decl.overall_confidence, 4),
            },
        )

        return {
            "inspection_id": inspection_id,
            "inspection_number": inspection.inspection_number,
            "product_id": product.id,
            "status": inspection.status,
            "declarations": decl.to_dict(),
        }


# Singleton
extraction_service = ExtractionService()
