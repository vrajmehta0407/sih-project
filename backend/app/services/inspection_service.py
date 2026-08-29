"""
inspection_service.py
======================
Stage 2 — Inspection Upload & Preprocessing Orchestrator

Handles:
  - MIME validation (JPEG/PNG/WEBP/BMP only, max 15 MB)
  - Unique inspection number generation (INS-YYYYMMDD-XXXXXXXX)
  - Raw file persistence under uploads/raw/{inspection_id}/
  - Calls ImagePreprocessingService for each uploaded image side
  - Preprocessed file persistence under uploads/preprocessed/{inspection_id}/
  - Inspection + Product DB row creation
  - AuditLog entry via audit_service
"""

import os
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.inspection import Inspection
from app.models.product import Product
from app.services.audit_service import audit_service
from app.services.image_preprocessing_service import (
    image_preprocessing_service,
    PreprocessingResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/heic",
    "image/heif",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic", ".heif"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
VALID_SIDES = {"front", "back", "left", "right", "top"}


# ---------------------------------------------------------------------------
# Helper: Generate Inspection Number
# ---------------------------------------------------------------------------
def _generate_inspection_number() -> str:
    """Generate a unique inspection number: INS-YYYYMMDD-XXXXXXXX."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:8].upper()
    return f"INS-{date_str}-{suffix}"


# ---------------------------------------------------------------------------
# Helper: Compute SHA-256 of file bytes
# ---------------------------------------------------------------------------
def _sha256_of_file(path: str) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


# ---------------------------------------------------------------------------
# Main Service
# ---------------------------------------------------------------------------
class InspectionService:

    # ------------------------------------------------------------------
    # Validate a single UploadFile
    # ------------------------------------------------------------------
    async def validate_upload(self, file: UploadFile, side: str) -> bytes:
        """
        Validate MIME type, extension, file size, and side name.
        Returns raw bytes on success; raises HTTPException on failure.
        """
        # Validate side label
        side_lower = side.lower()
        if side_lower not in VALID_SIDES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid image side '{side}'. Must be one of: {sorted(VALID_SIDES)}",
            )

        # Validate extension
        if file.filename:
            _, ext = os.path.splitext(file.filename.lower())
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=(
                        f"File '{file.filename}' has unsupported extension '{ext}'. "
                        f"Allowed: {sorted(ALLOWED_EXTENSIONS)}"
                    ),
                )

        # Read content (enforces size limit)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"File exceeds maximum size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB. "
                    f"Received: {len(content) / (1024*1024):.1f} MB."
                ),
            )
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty.",
            )

        # Validate MIME by checking magic bytes (first 12 bytes)
        if not self._is_valid_image_magic(content):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    "File content is not a recognised image format. "
                    "Only JPEG, PNG, WEBP, BMP, HEIC are accepted."
                ),
            )

        return content

    def _is_valid_image_magic(self, content: bytes) -> bool:
        """Check magic bytes for known image formats."""
        if len(content) < 12:
            return False
        # JPEG: FF D8 FF
        if content[:3] == b"\xff\xd8\xff":
            return True
        # PNG: 89 50 4E 47 0D 0A 1A 0A
        if content[:8] == b"\x89PNG\r\n\x1a\n":
            return True
        # WEBP: RIFF....WEBP
        if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
            return True
        # BMP: BM
        if content[:2] == b"BM":
            return True
        # HEIC/HEIF: ftyp box (at offset 4)
        if content[4:8] in (b"ftyp", b"ftypheic", b"ftypheix"):
            return True
        return False

    # ------------------------------------------------------------------
    # Save raw file to disk
    # ------------------------------------------------------------------
    def _save_raw_file(
        self,
        content: bytes,
        inspection_id: str,
        side: str,
        original_filename: str,
    ) -> str:
        """Save raw bytes to uploads/raw/{inspection_id}/{side}{ext}."""
        _, ext = os.path.splitext(original_filename.lower())
        if not ext or ext not in ALLOWED_EXTENSIONS:
            ext = ".jpg"  # Default to JPEG

        raw_dir = os.path.join(settings.UPLOAD_DIR, "raw", inspection_id)
        os.makedirs(raw_dir, exist_ok=True)

        raw_path = os.path.join(raw_dir, f"{side}{ext}")
        with open(raw_path, "wb") as f:
            f.write(content)
        return raw_path

    # ------------------------------------------------------------------
    # Core: Create Inspection with Images
    # ------------------------------------------------------------------
    async def create_inspection_with_images(
        self,
        db: Session,
        inspector_id: str,
        district: str,
        state: str,
        image_files: List[UploadFile],
        image_sides: List[str],
        store_name: Optional[str] = None,
        store_address: Optional[str] = None,
        gps_latitude: Optional[float] = None,
        gps_longitude: Optional[float] = None,
        gps_accuracy_meters: Optional[float] = None,
        inspector_notes: Optional[str] = None,
        rule_version_id: Optional[str] = None,
        request=None,
    ) -> Dict[str, Any]:
        """
        Full pipeline:
          1. Validate all images
          2. Create Inspection DB record
          3. For each image: save raw → preprocess → update DB
          4. Create empty Product record
          5. Log to AuditLog
          6. Return structured response dict
        """
        if len(image_files) != len(image_sides):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Number of image files must match number of side labels.",
            )
        if len(image_files) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one image file is required.",
            )
        if len(image_files) > 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Maximum 5 images per inspection.",
            )

        # ── Validate all uploads first (fail-fast before DB writes) ────
        validated: List[tuple[str, bytes, str]] = []  # (side, content, filename)
        for file, side in zip(image_files, image_sides):
            content = await self.validate_upload(file, side)
            validated.append((side.lower(), content, file.filename or f"{side}.jpg"))

        # ── Create Inspection DB record ─────────────────────────────────
        inspection_id = str(uuid.uuid4())
        inspection_number = _generate_inspection_number()

        inspection = Inspection(
            id=inspection_id,
            inspection_number=inspection_number,
            inspector_id=inspector_id,
            rule_version_id=rule_version_id,
            store_name=store_name,
            store_address=store_address,
            district=district,
            state=state,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            gps_accuracy_meters=gps_accuracy_meters,
            inspector_notes=inspector_notes,
            status="draft",
            compliance_status="pending",
            raw_images=[],
            preprocessed_images=[],
        )
        db.add(inspection)
        db.flush()  # Get the ID without committing

        # ── Create empty Product record ──────────────────────────────────
        product = Product(inspection_id=inspection_id)
        db.add(product)

        # ── Process each image ───────────────────────────────────────────
        raw_images_meta = []
        preprocessed_images_meta = []
        preprocessing_details = []
        preprocessing_metadata_store = {}

        for side, content, original_filename in validated:
            # Save raw file
            raw_path = self._save_raw_file(content, inspection_id, side, original_filename)
            raw_url = f"/uploads/raw/{inspection_id}/{os.path.basename(raw_path)}"

            raw_images_meta.append({"side": side, "file_path": raw_path, "url": raw_url})

            # Run preprocessing pipeline
            preprocessed_dir = os.path.join(
                settings.UPLOAD_DIR, "preprocessed", inspection_id
            )
            preprocess_result: PreprocessingResult = image_preprocessing_service.preprocess(
                input_path=raw_path,
                output_dir=preprocessed_dir,
                filename_stem=side,
            )

            if preprocess_result.success:
                proc_basename = os.path.basename(preprocess_result.processed_image_path)
                gray_basename = os.path.basename(preprocess_result.grayscale_image_path)
                processed_url = f"/uploads/preprocessed/{inspection_id}/{proc_basename}"
                grayscale_url = f"/uploads/preprocessed/{inspection_id}/{gray_basename}"

                preprocessed_images_meta.append({
                    "side": side,
                    "file_path": preprocess_result.processed_image_path,
                    "grayscale_path": preprocess_result.grayscale_image_path,
                    "url": processed_url,
                    "grayscale_url": grayscale_url,
                })

                preprocessing_metadata_store[side] = {
                    "skew_angle_degrees": preprocess_result.skew_angle_degrees,
                    "perspective_corrected": preprocess_result.perspective_corrected,
                    "glare_regions_detected": preprocess_result.glare_regions_detected,
                    "contrast_enhanced": preprocess_result.contrast_enhanced,
                    "quality_score": preprocess_result.quality_score,
                    "processing_time_ms": preprocess_result.processing_time_ms,
                    "original_size": f"{preprocess_result.original_width}x{preprocess_result.original_height}",
                    "processed_size": f"{preprocess_result.processed_width}x{preprocess_result.processed_height}",
                    "pipeline_steps": preprocess_result.pipeline_steps,
                }

                preprocessing_details.append({
                    "side": side,
                    "raw_url": raw_url,
                    "processed_url": processed_url,
                    "grayscale_url": grayscale_url,
                    "preprocessing": preprocessing_metadata_store[side],
                    "success": True,
                })
                logger.info(
                    "Preprocessed '%s' side for inspection %s — quality=%.1f, time=%.0fms",
                    side, inspection_number, preprocess_result.quality_score, preprocess_result.processing_time_ms,
                )
            else:
                logger.warning(
                    "Preprocessing failed for '%s' side: %s", side, preprocess_result.error_message
                )
                preprocessing_details.append({
                    "side": side,
                    "raw_url": raw_url,
                    "processed_url": None,
                    "grayscale_url": None,
                    "preprocessing": None,
                    "success": False,
                    "error": preprocess_result.error_message,
                })

        # Update inspection with image metadata & transition status
        inspection.raw_images = raw_images_meta
        inspection.preprocessed_images = preprocessed_images_meta
        inspection.preprocessing_metadata = preprocessing_metadata_store
        inspection.status = "preprocessed" if preprocessed_images_meta else "draft"

        db.commit()
        db.refresh(inspection)

        # ── Audit Log ────────────────────────────────────────────────────
        audit_service.log(
            db=db,
            action="CREATE_INSPECTION",
            entity_name="Inspection",
            entity_id=inspection_id,
            user_id=inspector_id,
            request=request,
            details={
                "inspection_number": inspection_number,
                "district": district,
                "state": state,
                "sides_uploaded": [s for s, _, _ in validated],
                "total_images": len(validated),
                "preprocessed_count": len(preprocessed_images_meta),
            },
        )

        return {
            "id": inspection_id,
            "inspection_number": inspection_number,
            "status": inspection.status,
            "compliance_status": inspection.compliance_status,
            "district": district,
            "state": state,
            "store_name": store_name,
            "store_address": store_address,
            "gps_latitude": gps_latitude,
            "gps_longitude": gps_longitude,
            "gps_accuracy_meters": gps_accuracy_meters,
            "inspector_notes": inspector_notes,
            "images": preprocessing_details,
            "created_at": inspection.created_at.isoformat(),
            "updated_at": inspection.updated_at.isoformat(),
        }

    # ------------------------------------------------------------------
    # Add images to an existing inspection
    # ------------------------------------------------------------------
    async def add_images_to_inspection(
        self,
        db: Session,
        inspection_id: str,
        inspector_id: str,
        image_files: List[UploadFile],
        image_sides: List[str],
        request=None,
    ) -> Dict[str, Any]:
        """Append additional image sides to an existing inspection."""
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection '{inspection_id}' not found.",
            )
        if str(inspection.inspector_id) != str(inspector_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add images to your own inspections.",
            )

        if len(image_files) != len(image_sides):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Number of image files must match number of side labels.",
            )

        # Validate
        validated = []
        for file, side in zip(image_files, image_sides):
            content = await self.validate_upload(file, side)
            validated.append((side.lower(), content, file.filename or f"{side}.jpg"))

        current_raw = list(inspection.raw_images or [])
        current_preprocessed = list(inspection.preprocessed_images or [])
        current_meta = dict(inspection.preprocessing_metadata or {})
        new_details = []

        for side, content, original_filename in validated:
            raw_path = self._save_raw_file(content, inspection_id, side, original_filename)
            raw_url = f"/uploads/raw/{inspection_id}/{os.path.basename(raw_path)}"

            # Remove existing entry for this side if re-uploading
            current_raw = [r for r in current_raw if r.get("side") != side]
            current_raw.append({"side": side, "file_path": raw_path, "url": raw_url})

            preprocessed_dir = os.path.join(settings.UPLOAD_DIR, "preprocessed", inspection_id)
            preprocess_result = image_preprocessing_service.preprocess(
                input_path=raw_path,
                output_dir=preprocessed_dir,
                filename_stem=side,
            )

            if preprocess_result.success:
                proc_basename = os.path.basename(preprocess_result.processed_image_path)
                gray_basename = os.path.basename(preprocess_result.grayscale_image_path)
                processed_url = f"/uploads/preprocessed/{inspection_id}/{proc_basename}"
                grayscale_url = f"/uploads/preprocessed/{inspection_id}/{gray_basename}"

                current_preprocessed = [p for p in current_preprocessed if p.get("side") != side]
                current_preprocessed.append({
                    "side": side,
                    "file_path": preprocess_result.processed_image_path,
                    "grayscale_path": preprocess_result.grayscale_image_path,
                    "url": processed_url,
                    "grayscale_url": grayscale_url,
                })

                current_meta[side] = {
                    "skew_angle_degrees": preprocess_result.skew_angle_degrees,
                    "perspective_corrected": preprocess_result.perspective_corrected,
                    "glare_regions_detected": preprocess_result.glare_regions_detected,
                    "contrast_enhanced": preprocess_result.contrast_enhanced,
                    "quality_score": preprocess_result.quality_score,
                    "processing_time_ms": preprocess_result.processing_time_ms,
                    "pipeline_steps": preprocess_result.pipeline_steps,
                }
                new_details.append({
                    "side": side,
                    "raw_url": raw_url,
                    "processed_url": processed_url,
                    "grayscale_url": grayscale_url,
                    "preprocessing": current_meta[side],
                    "success": True,
                })

        inspection.raw_images = current_raw
        inspection.preprocessed_images = current_preprocessed
        inspection.preprocessing_metadata = current_meta
        inspection.status = "preprocessed"
        db.commit()
        db.refresh(inspection)

        audit_service.log(
            db=db,
            action="ADD_IMAGES_TO_INSPECTION",
            entity_name="Inspection",
            entity_id=inspection_id,
            user_id=inspector_id,
            request=request,
            details={"sides_added": [s for s, _, _ in validated]},
        )

        return {"inspection_id": inspection_id, "added_images": new_details}


# Module-level singleton
inspection_service = InspectionService()
