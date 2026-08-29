"""
endpoints/inspections.py
========================
Stage 2 — Inspection REST API (Image Upload & Preprocessing)

Routes:
  POST   /inspections/              Create inspection + upload images (multipart)
  GET    /inspections/              List inspections (paginated, filterable)
  GET    /inspections/{id}          Full inspection detail
  POST   /inspections/{id}/images   Add images to existing inspection
  GET    /inspections/{id}/images/{side}  Get image info for a specific side
  DELETE /inspections/{id}          Delete inspection + all associated files (admin only)
"""

import os
import shutil
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Query,
    Request,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import require_inspector, require_admin
from app.db.session import get_db
from app.models.inspection import Inspection
from app.models.product import Product
from app.models.violation import Violation
from app.models.report import Report
from app.services.inspection_service import inspection_service
from app.services.ocr.ocr_service import ocr_service
from app.services.extractor.extraction_service import extraction_service
from app.services.validator.compliance_service import compliance_service
from app.services.report.report_service import report_service
from app.services.sync.batch_sync_service import batch_sync_service
from app.services.audit_service import audit_service
from app.schemas.adjudication import AdjudicationRequest, AdjudicationResponse
from app.schemas.inspection import (
    InspectionResponse,
    InspectionListResponse,
    InspectionSummary,
    AddImagesResponse,
    DeleteResponse,
)
from app.schemas.ocr import OCRRunResponse
from app.schemas.extraction import ExtractedDeclarationsResponse
from app.schemas.compliance import ValidationResponse, ViolationItemSchema
from app.schemas.report import ReportResponse, QRVerificationResponse
from app.schemas.sync import BatchSyncRequest, BatchSyncResponse
from app.services.counterfeit_detection_service import counterfeit_detection_service
from app.schemas.registry import CounterfeitCheckResponse
from app.models.registered_product import RegisteredProduct
from app.schemas.notice import NoticeDispatchRequest, NoticeDispatchResponse
from app.services.notice_dispatcher_service import notice_dispatcher_service
from app.services.voice_assistant_service import voice_assistant_service
from app.services.forensic_tamper_service import forensic_tamper_service
from app.schemas.jurisdiction_transfer import (
    JurisdictionTransferRequest,
    JurisdictionTransferResponse,
    OfficerCoSignRequest,
    OfficerCoSignResponse,
)
from app.services.jurisdiction_transfer_service import jurisdiction_transfer_service
from app.schemas.challan import (
    ChallanGenerateRequest,
    ChallanSettlementRequest,
    ChallanResponse,
)
from app.services.challan_service import challan_service
from app.schemas.robustness_benchmark import (
    DegradationProfileResult,
    RobustnessBenchmarkResponse,
)
from app.services.robustness_benchmark_service import robustness_benchmark_service

router = APIRouter()
logger = logging.getLogger(__name__)


# ===========================================================================
# POST /inspections/batch-sync
# Synchronize offline inspection records collected on field tablets
# ===========================================================================
@router.post(
    "/batch-sync",
    response_model=BatchSyncResponse,
    summary="Batch Synchronize Offline Inspections",
    description=(
        "Processes a batch queue of inspections recorded offline by field officers in low-connectivity areas. "
        "Performs idempotent synchronization, text extraction, and statutory compliance validation."
    ),
)
def batch_sync_inspections(
    payload: BatchSyncRequest,
    request: Request,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    return batch_sync_service.sync_offline_inspections(
        db=db,
        payload=payload,
        user_id=str(current_user.id),
        request=request,
    )


# ===========================================================================
# POST /inspections/
# Create a new inspection with one or more product label images
# ===========================================================================
@router.post(
    "/",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Inspection & Upload Label Images",
    description=(
        "Upload 1–5 images of a product label (different sides: front/back/left/right/top). "
        "The OpenCV preprocessing pipeline will automatically run perspective correction, "
        "denoising, glare suppression, CLAHE contrast enhancement, and skew detection "
        "on each uploaded image. Returns full preprocessing metadata and image URLs."
    ),
)
async def create_inspection(
    request: Request,
    # ── Image files & sides ──────────────────────────────────────────────
    images: List[UploadFile] = File(
        ..., description="1 to 5 product label images (JPEG/PNG/WEBP/BMP, max 15 MB each)"
    ),
    sides: List[str] = Form(
        ..., description="Side labels matching each image: front | back | left | right | top"
    ),
    # ── Inspection metadata fields ────────────────────────────────────────
    district: str = Form(..., description="District where inspection is conducted"),
    state: str = Form(..., description="State where inspection is conducted"),
    store_name: Optional[str] = Form(None, description="Name of inspected shop/store"),
    store_address: Optional[str] = Form(None, description="Address of shop/store"),
    gps_latitude: Optional[float] = Form(None, description="GPS latitude (-90 to 90)"),
    gps_longitude: Optional[float] = Form(None, description="GPS longitude (-180 to 180)"),
    gps_accuracy_meters: Optional[float] = Form(None, description="GPS accuracy in metres"),
    inspector_notes: Optional[str] = Form(None, description="Inspector notes"),
    rule_version_id: Optional[str] = Form(None, description="Active rule version UUID"),
    # ── Auth & DB ─────────────────────────────────────────────────────────
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    result = await inspection_service.create_inspection_with_images(
        db=db,
        inspector_id=str(current_user.id),
        district=district.strip(),
        state=state.strip(),
        image_files=images,
        image_sides=sides,
        store_name=store_name,
        store_address=store_address,
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude,
        gps_accuracy_meters=gps_accuracy_meters,
        inspector_notes=inspector_notes,
        rule_version_id=rule_version_id,
        request=request,
    )
    return result


# ===========================================================================
# GET /inspections/
# List inspections (paginated) — inspectors see their own; admins see all
# ===========================================================================
@router.get(
    "/",
    response_model=InspectionListResponse,
    summary="List Inspections",
    description="Paginated list of inspections. Inspectors see only their own; admins see all.",
)
def list_inspections(
    district: Optional[str] = Query(None, description="Filter by district"),
    state: Optional[str] = Query(None, description="Filter by state"),
    insp_status: Optional[str] = Query(None, alias="status", description="Filter by pipeline status"),
    compliance_status: Optional[str] = Query(None, description="Filter by compliance outcome"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Results per page (max 100)"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    query = db.query(Inspection)

    # Role-based filter: inspectors see only their own inspections
    if current_user.role == "inspector":
        query = query.filter(Inspection.inspector_id == current_user.id)

    if district:
        query = query.filter(Inspection.district.ilike(f"%{district}%"))
    if state:
        query = query.filter(Inspection.state.ilike(f"%{state}%"))
    if insp_status:
        query = query.filter(Inspection.status == insp_status)
    if compliance_status:
        query = query.filter(Inspection.compliance_status == compliance_status)

    total = query.count()
    inspections = (
        query.order_by(Inspection.created_at.desc()).offset(skip).limit(limit).all()
    )

    items = []
    for insp in inspections:
        items.append(
            InspectionSummary(
                id=str(insp.id),
                inspection_number=insp.inspection_number,
                status=insp.status,
                compliance_status=insp.compliance_status,
                district=insp.district,
                state=insp.state,
                store_name=insp.store_name,
                total_images=len(insp.raw_images or []),
                created_at=insp.created_at,
            )
        )

    return InspectionListResponse(total=total, skip=skip, limit=limit, items=items)


# ===========================================================================
# GET /inspections/{inspection_id}
# Full inspection detail with preprocessing metadata
# ===========================================================================
@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
    summary="Get Inspection Detail",
    description="Full inspection record including per-side image URLs and preprocessing metadata.",
)
def get_inspection(
    inspection_id: str,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection '{inspection_id}' not found.",
        )

    # Inspectors can only view their own inspections
    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own inspections.",
        )

    # Build images list from DB metadata
    raw_map = {r["side"]: r for r in (inspection.raw_images or [])}
    pre_map = {p["side"]: p for p in (inspection.preprocessed_images or [])}
    meta_map = inspection.preprocessing_metadata or {}

    all_sides = set(raw_map.keys()) | set(pre_map.keys())
    images = []
    for side in sorted(all_sides):
        raw_entry = raw_map.get(side, {})
        pre_entry = pre_map.get(side, {})
        meta = meta_map.get(side)

        images.append({
            "side": side,
            "raw_url": raw_entry.get("url", ""),
            "processed_url": pre_entry.get("url"),
            "grayscale_url": pre_entry.get("grayscale_url"),
            "preprocessing": meta,
            "success": bool(pre_entry),
        })

    return {
        "id": str(inspection.id),
        "inspection_number": inspection.inspection_number,
        "status": inspection.status,
        "compliance_status": inspection.compliance_status,
        "district": inspection.district,
        "state": inspection.state,
        "store_name": inspection.store_name,
        "store_address": inspection.store_address,
        "gps_latitude": inspection.gps_latitude,
        "gps_longitude": inspection.gps_longitude,
        "gps_accuracy_meters": inspection.gps_accuracy_meters,
        "inspector_notes": inspection.inspector_notes,
        "images": images,
        "preprocessing_metadata": inspection.preprocessing_metadata,
        "created_at": inspection.created_at,
        "updated_at": inspection.updated_at,
    }


# ===========================================================================
# POST /inspections/{inspection_id}/images
# Add additional images to an existing inspection
# ===========================================================================
@router.post(
    "/{inspection_id}/images",
    response_model=AddImagesResponse,
    summary="Add Images to Existing Inspection",
    description=(
        "Upload additional side images (e.g., back, top) to a previously created inspection. "
        "Existing images for the same side will be replaced. Preprocessing runs automatically."
    ),
)
async def add_images(
    inspection_id: str,
    request: Request,
    images: List[UploadFile] = File(..., description="Additional images to add"),
    sides: List[str] = Form(..., description="Sides matching each image"),
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    result = await inspection_service.add_images_to_inspection(
        db=db,
        inspection_id=inspection_id,
        inspector_id=str(current_user.id),
        image_files=images,
        image_sides=sides,
        request=request,
    )
    return result


# ===========================================================================
# GET /inspections/{inspection_id}/images/{side}
# Get image file response for a specific side
# ===========================================================================
@router.get(
    "/{inspection_id}/images/{side}",
    summary="Get Processed Image for Side",
    description="Returns the preprocessed (color JPEG) image for the given side directly.",
)
def get_image_for_side(
    inspection_id: str,
    side: str,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    preprocessed = inspection.preprocessed_images or []
    entry = next((p for p in preprocessed if p.get("side") == side.lower()), None)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No preprocessed image found for side '{side}'. "
                   f"Available sides: {[p.get('side') for p in preprocessed]}",
        )

    file_path = entry.get("file_path")
    if not file_path or not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preprocessed file not found on disk: '{file_path}'.",
        )

    return FileResponse(file_path, media_type="image/jpeg")


# ===========================================================================
# DELETE /inspections/{inspection_id}
# Delete inspection record + all associated files (admin only)
# ===========================================================================
@router.delete(
    "/{inspection_id}",
    response_model=DeleteResponse,
    summary="Delete Inspection",
    description="Permanently deletes inspection record and all raw/preprocessed image files. Admin only.",
)
def delete_inspection(
    inspection_id: str,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection '{inspection_id}' not found.",
        )

    # Remove files from disk
    for folder in ("raw", "preprocessed"):
        folder_path = os.path.join(settings.UPLOAD_DIR, folder, inspection_id)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)
            logger.info("Deleted upload folder: %s", folder_path)

    db.delete(inspection)
    db.commit()

    logger.info(
        "Admin '%s' deleted inspection '%s'",
        current_user.email,
        inspection.inspection_number,
    )
    return DeleteResponse(
        message=f"Inspection '{inspection.inspection_number}' and all associated files deleted.",
        inspection_id=inspection_id,
    )


# ===========================================================================
# POST /inspections/{inspection_id}/ocr
# Trigger dual-engine OCR (PaddleOCR + Tesseract) & Consensus Pipeline
# ===========================================================================
@router.post(
    "/{inspection_id}/ocr",
    response_model=OCRRunResponse,
    summary="Run Dual OCR & Consensus Pipeline",
    description=(
        "Executes dual OCR extraction (PaddleOCR and Tesseract) on all preprocessed images "
        "associated with this inspection. Reconciles character/token level outputs using spatial "
        "IoU alignment, Levenshtein distance metrics, and digit mismatch verification. "
        "Updates the Product record and advances inspection status to 'extracted'."
    ),
)
def run_dual_ocr(
    inspection_id: str,
    request: Request,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    # Verify inspector owns inspection
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = ocr_service.process_inspection_ocr(
        db=db,
        inspection_id=inspection_id,
        user_id=str(current_user.id),
        request=request,
    )
    return result


# ===========================================================================
# GET /inspections/{inspection_id}/ocr
# Retrieve OCR results and consensus matrix
# ===========================================================================
@router.get(
    "/{inspection_id}/ocr",
    response_model=OCRRunResponse,
    summary="Get OCR Consensus Data",
    description="Retrieves existing raw PaddleOCR, Tesseract, and reconciled consensus matrix for the inspection.",
)
def get_ocr_consensus(
    inspection_id: str,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    product = db.query(Product).filter(Product.inspection_id == inspection_id).first()
    if not product or not product.extracted_fields_consensus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OCR consensus data not found for inspection '{inspection_id}'. Run POST /ocr first.",
        )

    return {
        "inspection_id": inspection_id,
        "inspection_number": inspection.inspection_number,
        "status": inspection.status,
        "ocr_consensus": product.extracted_fields_consensus,
    }


# ===========================================================================
# POST /inspections/{inspection_id}/extract-declarations
# Extract statutory declarations under Rule 6 of LM PCR 2011
# ===========================================================================
@router.post(
    "/{inspection_id}/extract-declarations",
    response_model=ExtractedDeclarationsResponse,
    summary="Extract Statutory Declarations (Rule 6)",
    description=(
        "Parses OCR consensus text using specialized regex and NLP rules to extract all mandatory "
        "declarations under Rule 6 of Legal Metrology (Packaged Commodities) Rules, 2011. "
        "Populates the Product record with MRP, Net Quantity, Dates, Batch No, Manufacturer, "
        "Origin, and Consumer Care details."
    ),
)
def extract_statutory_declarations(
    inspection_id: str,
    request: Request,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = extraction_service.extract_declarations_for_inspection(
        db=db,
        inspection_id=inspection_id,
        user_id=str(current_user.id),
        request=request,
    )
    return result


# ===========================================================================
# GET /inspections/{inspection_id}/declarations
# Retrieve structured statutory declarations for inspection
# ===========================================================================
@router.get(
    "/{inspection_id}/declarations",
    response_model=ExtractedDeclarationsResponse,
    summary="Get Extracted Declarations",
    description="Retrieves structured statutory declarations and confidence metrics extracted from the product packaging.",
)
def get_extracted_declarations(
    inspection_id: str,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    product = db.query(Product).filter(Product.inspection_id == inspection_id).first()
    if not product or product.mrp_value is None and product.net_quantity_value is None and product.manufacturer_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Declarations not yet extracted for inspection '{inspection_id}'. Run POST /extract-declarations first.",
        )

    from app.services.extractor.declaration_extractor import declaration_extractor
    # Reconstruct from OCR text or DB fields
    ocr_text = ""
    if product.extracted_fields_consensus:
        ocr_text = product.extracted_fields_consensus.get("aggregated_consensus_text", "")
    if not ocr_text:
        ocr_text = product.paddle_raw_text or product.tesseract_raw_text or ""

    decl = declaration_extractor.extract_from_text(ocr_text)

    return {
        "inspection_id": inspection_id,
        "inspection_number": inspection.inspection_number,
        "product_id": product.id,
        "status": inspection.status,
        "declarations": decl.to_dict(),
    }


# ===========================================================================
# POST /inspections/{inspection_id}/validate
# Execute statutory Legal Metrology compliance validation engine
# ===========================================================================
@router.post(
    "/{inspection_id}/validate",
    response_model=ValidationResponse,
    summary="Validate Statutory Compliance & Detect Violations",
    description=(
        "Evaluates the pre-packaged commodity's extracted declarations against active statutory rules "
        "(Rule 6 of LM PCR 2011, Section 18 & Section 36 of LM Act 2009). "
        "Performs repeat offender intelligence analysis, calculates fine liabilities, "
        "creates persistent Violation records, and updates inspection compliance status."
    ),
)
def validate_inspection_compliance(
    inspection_id: str,
    request: Request,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = compliance_service.validate_inspection(
        db=db,
        inspection_id=inspection_id,
        user_id=str(current_user.id),
        request=request,
    )
    return result


# ===========================================================================
# GET /inspections/{inspection_id}/violations
# Retrieve statutory violation records for inspection
# ===========================================================================
@router.get(
    "/{inspection_id}/violations",
    response_model=List[ViolationItemSchema],
    summary="Get Statutory Violations",
    description="Retrieves all grounded statutory violations and penalty assessments for the inspection.",
)
def get_inspection_violations(
    inspection_id: str,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    violations = db.query(Violation).filter(Violation.inspection_id == inspection_id).all()
    return violations


# ===========================================================================
# GET /inspections/verify/{qr_token}
# Public Verification Endpoint (No authentication required)
# ===========================================================================
@router.get(
    "/verify/{qr_token}",
    response_model=QRVerificationResponse,
    summary="Verify Inspection Authenticity via QR Token",
    description="Public endpoint to verify the authenticity and tamper-proof cryptographic audit trail of an inspection report.",
)
def verify_inspection_qr(
    qr_token: str,
    db: Session = Depends(get_db),
):
    result = report_service.verify_qr_token(db=db, qr_token=qr_token)
    return result


# ===========================================================================
# POST /inspections/{inspection_id}/report
# Generate statutory inspection report & notice PDF
# ===========================================================================
@router.post(
    "/{inspection_id}/report",
    response_model=ReportResponse,
    summary="Generate Statutory Inspection Report & Notice PDF",
    description=(
        "Generates a court-admissible PDF inspection report and statutory legal notice with "
        "ReportLab, embeds verification QR code, computes SHA-256 chain-of-custody hash, "
        "and sets inspection status to completed."
    ),
)
def generate_inspection_report(
    inspection_id: str,
    request: Request,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    result = report_service.generate_inspection_report(
        db=db,
        inspection_id=inspection_id,
        user_id=str(current_user.id),
        request=request,
    )
    return result


# ===========================================================================
# GET /inspections/{inspection_id}/report/download
# Download generated PDF inspection report
# ===========================================================================
@router.get(
    "/{inspection_id}/report/download",
    summary="Download Inspection Report PDF",
    description="Streams the generated court-admissible PDF inspection report.",
)
def download_inspection_report(
    inspection_id: str,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    report = db.query(Report).filter(Report.inspection_id == inspection_id).first()
    if not report or not report.pdf_file_path or not os.path.isfile(report.pdf_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report PDF for inspection '{inspection_id}' has not been generated yet. Call POST /report first.",
        )

    return FileResponse(
        path=report.pdf_file_path,
        media_type="application/pdf",
        filename=f"{report.docket_number}.pdf",
    )


# ===========================================================================
# POST /inspections/{inspection_id}/adjudicate
# Statutory Adjudication & Compounding Workflow (Section 48/49 LM Act 2009)
# ===========================================================================
@router.post(
    "/{inspection_id}/adjudicate",
    response_model=AdjudicationResponse,
    summary="Adjudicate Violation Docket & Compound Offence",
    description=(
        "Records post-inspection legal adjudication actions under Section 48/49 of the Legal Metrology Act, 2009. "
        "Allows compounding of offences, recording fee payments, or escalating to the Designated Magistrate Court."
    ),
)
def adjudicate_inspection(
    inspection_id: str,
    payload: AdjudicationRequest,
    request: Request,
    current_user=Depends(require_inspector),
    db: Session = Depends(get_db),
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inspection '{inspection_id}' not found.")

    if current_user.role == "inspector" and str(inspection.inspector_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    action_map = {
        "COMPOUND_OFFENCE": "compounded",
        "REFER_TO_COURT": "court_referred",
        "ISSUE_SHOW_CAUSE": "notice_issued",
        "CLOSE_WITH_WARNING": "closed_warning",
    }

    new_status = action_map.get(payload.action, "compounded")
    inspection.adjudication_status = new_status
    if payload.compounding_amount is not None:
        inspection.compounding_amount = payload.compounding_amount
    if payload.order_number:
        inspection.compounding_order_number = payload.order_number
    if payload.receipt_number:
        inspection.compounding_receipt_number = payload.receipt_number
    if payload.court_jurisdiction:
        inspection.court_jurisdiction = payload.court_jurisdiction
    if payload.adjudication_notes:
        inspection.adjudication_notes = payload.adjudication_notes

    from datetime import datetime, timezone
    now_utc = datetime.now(timezone.utc)
    inspection.adjudicated_at = now_utc

    # Audit log
    audit_service.log(
        db=db,
        action="ADJUDICATION_ACTION",
        entity_name="Inspection",
        entity_id=inspection.id,
        user_id=current_user.id,
        request=request,
        details={
            "action": payload.action,
            "adjudication_status": new_status,
            "compounding_amount": payload.compounding_amount,
            "order_number": payload.order_number
        }
    )

    db.commit()
    db.refresh(inspection)

    return AdjudicationResponse(
        inspection_id=inspection.id,
        inspection_number=inspection.inspection_number,
        compliance_status=inspection.compliance_status,
        adjudication_status=inspection.adjudication_status,
        compounding_amount=inspection.compounding_amount,
        compounding_order_number=inspection.compounding_order_number,
        receipt_number=inspection.compounding_receipt_number,
        court_jurisdiction=inspection.court_jurisdiction,
        adjudication_notes=inspection.adjudication_notes,
        adjudicated_by_user=current_user.full_name,
        updated_at=now_utc,
    )


# ===========================================================================
# POST /inspections/{id}/counterfeit-check
# AI ORB Feature Similarity vs. Manufacturer Golden Reference
# ===========================================================================
@router.post(
    "/{inspection_id}/counterfeit-check",
    response_model=CounterfeitCheckResponse,
    summary="AI Counterfeit Label Detection (ORB Feature Similarity)",
)
def counterfeit_check(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Compare the inspected label image against the manufacturer-registered golden
    reference image using OpenCV ORB feature descriptors + FLANN KNN matching.

    Returns a similarity score (0–100) and flags SUSPECTED_COUNTERFEIT when the
    score falls below the authenticity threshold (35%).

    If no golden reference image is registered for this product barcode,
    returns an INSUFFICIENT confidence result with explanation.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    # Resolve inspected image path (use first available processed image)
    inspected_path = None
    if inspection.images:
        for img in inspection.images:
            candidate = img.processed_image_path or img.original_image_path
            if candidate and os.path.isfile(candidate):
                inspected_path = candidate
                break

    if not inspected_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No processed image found on this inspection. Run preprocessing first.",
        )

    # Look up golden reference via barcode
    reference_path = None
    reference_product_name = None
    if inspection.product and inspection.product.barcode:
        registered = db.query(RegisteredProduct).filter(
            RegisteredProduct.barcode_ean13 == inspection.product.barcode,
            RegisteredProduct.is_active == True,
        ).first()
        if registered and registered.golden_reference_image_path:
            reference_path = registered.golden_reference_image_path
            reference_product_name = registered.product_name

    if not reference_path or not os.path.isfile(reference_path):
        return CounterfeitCheckResponse(
            inspection_id=inspection.id,
            similarity_score=0.0,
            good_matches=0,
            total_keypoints_query=0,
            total_keypoints_reference=0,
            is_suspected_counterfeit=False,
            confidence="INSUFFICIENT",
            explanation="No golden reference image is registered for this product barcode. "
                        "Register the product in the National Product Registry first.",
            reference_product_name=reference_product_name,
        )

    result = counterfeit_detection_service.compare(inspected_path, reference_path)

    return CounterfeitCheckResponse(
        inspection_id=inspection.id,
        similarity_score=result.similarity_score,
        good_matches=result.good_matches,
        total_keypoints_query=result.total_keypoints_query,
        total_keypoints_reference=result.total_keypoints_reference,
        is_suspected_counterfeit=result.is_suspected_counterfeit,
        confidence=result.confidence,
        explanation=result.explanation,
        reference_product_name=reference_product_name,
    )


# ===========================================================================
# POST /inspections/{id}/dispatch-notice
# Dispatch Formal Statutory Show-Cause Notice (Section 18/36/48)
# ===========================================================================
@router.post(
    "/{inspection_id}/dispatch-notice",
    response_model=NoticeDispatchResponse,
    summary="Dispatch Formal Statutory Show-Cause Notice",
)
def dispatch_statutory_notice(
    inspection_id: str,
    req: NoticeDispatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Generate and dispatch a formal legal Show-Cause Notice directly to the
    manufacturer/packer contact under Sections 18 & 36 of the Legal Metrology Act, 2009.
    Embeds statutory compliance rectification deadlines and logs delivery in the
    immutable audit trail under Section 65B of Bharatiya Sakshya Adhiniyam, 2023.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    response = notice_dispatcher_service.dispatch(inspection, req, current_user.email)

    # Log to immutable BSA 2023 audit trail
    audit_service.log_event(
        db=db,
        action="DISPATCH_STATUTORY_NOTICE",
        user_id=current_user.id,
        user_email=current_user.email,
        entity_type="INSPECTION",
        entity_id=str(inspection.id),
        details={
            "tracking_token": response.tracking_token,
            "recipient_email": response.recipient_email,
            "compliance_deadline": response.compliance_deadline.isoformat(),
            "inspection_number": inspection.inspection_number,
        },
    )

    return response


# ===========================================================================
# POST /inspections/{id}/voice-notes
# Process Spoken Voice Notes & Dictations for Field Inspection
# ===========================================================================
@router.post(
    "/{inspection_id}/voice-notes",
    summary="Process Spoken Voice Dictation into Inspection Docket",
)
def process_voice_notes(
    inspection_id: str,
    transcript: str = Query(..., description="Spoken voice note transcript from microphone"),
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Parses spoken voice memos in English and Hindi recorded during field raids,
    extracts structured values (MRP, charged prices, batch, observed violations),
    and appends them to the official inspection notes.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    result = voice_assistant_service.process_transcript(transcript)

    # Append to inspector notes
    existing_notes = inspection.inspector_notes or ""
    new_notes = (existing_notes + "\n\n" + result.formatted_officer_note).strip()
    inspection.inspector_notes = new_notes
    db.commit()
    db.refresh(inspection)

    return {
        "inspection_id": inspection.id,
        "raw_transcript": result.raw_transcript,
        "language_detected": result.language_detected,
        "detected_mrp": result.detected_mrp,
        "detected_charged_price": result.detected_charged_price,
        "detected_batch": result.detected_batch,
        "detected_infractions": result.detected_infractions,
        "updated_inspector_notes": inspection.inspector_notes,
    }


# ===========================================================================
# GET /inspections/{id}/tamper-heatmap
# Forensic Error Level Analysis (ELA) for Packaging Tamper & Sticker Detection
# ===========================================================================
@router.get(
    "/{inspection_id}/tamper-heatmap",
    summary="Forensic Error Level Analysis (ELA) Sticker Tamper Detection",
)
def get_tamper_heatmap(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Computes Error Level Analysis (ELA) on the inspected label image to detect
    dual MRP stickers, altered dates, and secondary overprinting.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    # Find first available image
    img_path = None
    if inspection.raw_images:
        for item in inspection.raw_images:
            p = item.get("file_path")
            if p and os.path.isfile(p):
                img_path = p
                break

    if not img_path:
        return {
            "inspection_id": inspection.id,
            "tamper_score": 0.0,
            "is_tampering_suspected": False,
            "forensic_summary": "No raw label image found on this docket for forensic analysis.",
        }

    out_heatmap = img_path + "_ela_heatmap.jpg"
    res = forensic_tamper_service.analyze_tampering(img_path, out_heatmap)

    return {
        "inspection_id": inspection.id,
        "tamper_score": res.tamper_score,
        "is_tampering_suspected": res.is_tampering_suspected,
        "max_error_differential": res.max_error_differential,
        "suspicious_regions_count": res.suspicious_regions_count,
        "forensic_summary": res.forensic_summary,
    }


# ===========================================================================
# Stage 21 — Cross-State Jurisdictional Transfer & Multi-Officer Co-Signing
# ===========================================================================

@router.post(
    "/{inspection_id}/transfer-jurisdiction",
    response_model=JurisdictionTransferResponse,
    summary="Formally Transfer Case to Origin Manufacturing State",
)
def transfer_case_jurisdiction(
    inspection_id: str,
    req: JurisdictionTransferRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Initiate a formal inter-state statutory enforcement transfer under Section 49
    of the Legal Metrology Act, 2009 to the Controller of Legal Metrology of the
    origin manufacturing state.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    return jurisdiction_transfer_service.transfer_case(
        db=db,
        inspection=inspection,
        req=req,
        transferring_officer_email=current_user.email,
    )


@router.post(
    "/{inspection_id}/co-sign",
    response_model=OfficerCoSignResponse,
    summary="Register Secondary Officer Joint Investigation Co-Signature",
)
def co_sign_inspection(
    inspection_id: str,
    req: OfficerCoSignRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Register a secondary investigating officer's digital co-signature on an inspection docket
    during joint market taskforce operations.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    return jurisdiction_transfer_service.co_sign_docket(
        db=db,
        inspection=inspection,
        req=req,
    )


# ===========================================================================
# Stage 23 — Section 48 e-Challan & Online Compounding Settlement
# ===========================================================================

@router.post(
    "/{inspection_id}/challan/generate",
    response_model=ChallanResponse,
    summary="Generate Official Section 48 Compounding e-Challan",
)
def generate_compounding_challan(
    inspection_id: str,
    req: ChallanGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_inspector),
):
    """
    Issue an official Section 48 e-Challan with dynamic UPI Bharat QR intent
    for compounding of Legal Metrology offences.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    return challan_service.generate_challan(db=db, inspection=inspection, req=req)


@router.post(
    "/{inspection_id}/challan/settle",
    response_model=ChallanResponse,
    summary="Settle e-Challan Online & Issue Section 48 Discharge Certificate",
)
def settle_compounding_challan(
    inspection_id: str,
    req: ChallanSettlementRequest,
    db: Session = Depends(get_db),
):
    """
    Process online treasury settlement of a Section 48 compounding fee,
    close the violation docket, and generate a Certificate of Compounding Discharge.
    """
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    return challan_service.settle_challan(db=db, inspection=inspection, req=req)


@router.get(
    "/{inspection_id}/challan",
    response_model=ChallanResponse,
    summary="Get e-Challan Status and Compounding Details",
)
def get_challan_status(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve the live Section 48 e-Challan status and discharge details for an inspection."""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    is_settled = inspection.adjudication_status == "compounded"
    challan_num = inspection.compounding_order_number or f"CHALLAN-IN-2026-{inspection.id[:6].upper()}"
    amount = inspection.compounding_amount or 25000.0

    return ChallanResponse(
        challan_id=uuid.UUID(str(inspection.id)),
        challan_number=challan_num,
        inspection_id=uuid.UUID(str(inspection.id)),
        violator_entity_name=inspection.store_name or "Commercial Establishment",
        violator_gstin=None,
        state=inspection.state or "National Jurisdiction",
        district=inspection.district or "District HQ",
        offence_description="Section 48 Statutory Compounding Offence",
        compounding_amount=amount,
        status="SETTLED" if is_settled else "ISSUED",
        payment_upi_intent=f"upi://pay?pa=legalmetrology.treasury@gov.in&am={amount:.2f}&cu=INR&tn=Compounding+{challan_num}",
        statutory_deadline=inspection.created_at or datetime.utcnow(),
        issued_at=inspection.created_at or datetime.utcnow(),
        settled_at=inspection.adjudicated_at if is_settled else None,
        transaction_reference=inspection.compounding_receipt_number,
        discharge_certificate_seal=None,
        official_legal_notice="Official Statutory Record under Section 48 of Legal Metrology Act, 2009.",
    )


# ===========================================================================
# Stage 24 — Automated OCR Synthetic Stress-Testing & Adversarial Benchmark
# ===========================================================================

@router.post(
    "/benchmark/stress-test",
    response_model=RobustnessBenchmarkResponse,
    summary="Execute Adversarial OCR Robustness Stress-Test",
)
async def run_ocr_robustness_stress_test(
    image: Optional[UploadFile] = File(None),
):
    """
    Apply 6 synthetic adversarial field distortions (Motion Blur, 45-Deg Skew,
    Flash Glare, Sensor Noise, Polybag Crinkle, and Ink Fading) and measure
    character recovery and Rule 6 extraction resilience.
    """
    image_bytes = None
    if image:
        image_bytes = await image.read()

    return robustness_benchmark_service.run_stress_test(image_bytes=image_bytes)


@router.get(
    "/benchmark/latest",
    response_model=RobustnessBenchmarkResponse,
    summary="Get Latest Synthetic Robustness Benchmark Report",
)
def get_latest_benchmark_report():
    """Retrieve pre-computed standard synthetic baseline robustness benchmark report."""
    return robustness_benchmark_service.run_stress_test()
