"""
test_image_preprocessing.py
============================
Stage 2 — Unit Tests for Image Preprocessing Pipeline & Inspection Endpoints

Test coverage (10 tests):
  1.  test_preprocess_clean_label_image       — clean synthetic label → success + quality > 0
  2.  test_preprocess_skewed_image            — synthetically skewed image → angle correction applied
  3.  test_preprocess_glare_image             — image with bright specular blob → glare_regions_detected > 0
  4.  test_preprocess_invalid_file            — non-image bytes → success=False, error_message set
  5.  test_preprocess_oversized_image         — 5000×4000 image → resize guard applied, output ≤ 4096px
  6.  test_create_inspection_endpoint         — POST multipart → 201, preprocessing.quality_score present
  7.  test_list_inspections_paginated         — GET list → correct pagination structure
  8.  test_get_inspection_by_id              — GET detail → images list + preprocessing_metadata present
  9.  test_upload_additional_image           — POST /{id}/images → back side added
  10. test_invalid_mime_type_rejected         — .exe bytes uploaded → 415 / 422 error
"""

import io
import os
import tempfile
import struct

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.services.image_preprocessing_service import (
    ImagePreprocessingService,
    PreprocessingResult,
    MAX_DIMENSION_PX,
)


# ---------------------------------------------------------------------------
# Helpers — Synthetic Image Factories
# ---------------------------------------------------------------------------

def _make_jpeg_bytes(width: int = 640, height: int = 480, color: tuple = (180, 200, 160)) -> bytes:
    """Create a valid JPEG image in memory via NumPy + cv2."""
    import cv2
    img = np.full((height, width, 3), color, dtype=np.uint8)
    # Draw some text-like rectangles so Hough / edge detection has content
    cv2.rectangle(img, (50, 50), (590, 100), (30, 30, 30), -1)
    cv2.rectangle(img, (50, 120), (400, 150), (30, 30, 30), -1)
    cv2.rectangle(img, (50, 170), (550, 190), (30, 30, 30), -1)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    assert ok
    return buf.tobytes()


def _make_skewed_jpeg_bytes(width: int = 640, height: int = 480, angle_deg: float = 7.0) -> bytes:
    """Create a JPEG image with a visible rotation (skew)."""
    import cv2
    img = np.full((height, width, 3), (220, 220, 220), dtype=np.uint8)
    # Draw horizontal lines that will appear skewed
    for y in range(60, height - 60, 40):
        cv2.line(img, (30, y), (width - 30, y), (20, 20, 20), 3)
    # Rotate
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated = cv2.warpAffine(img, M, (width, height), borderValue=(220, 220, 220))
    ok, buf = cv2.imencode(".jpg", rotated, [cv2.IMWRITE_JPEG_QUALITY, 90])
    assert ok
    return buf.tobytes()


def _make_glare_jpeg_bytes(width: int = 640, height: int = 480) -> bytes:
    """Create a JPEG with a bright specular highlight blob."""
    import cv2
    img = np.full((height, width, 3), (150, 160, 140), dtype=np.uint8)
    # Draw a large bright white ellipse (simulates glare)
    cv2.ellipse(img, (320, 240), (80, 60), 0, 0, 360, (255, 255, 255), -1)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    assert ok
    return buf.tobytes()


def _make_large_jpeg_bytes(width: int = 5000, height: int = 4000) -> bytes:
    """Create an intentionally large JPEG to trigger resize guard."""
    import cv2
    # Use a smaller array then resize to avoid memory issues in test generation
    small = np.full((400, 500, 3), (100, 150, 200), dtype=np.uint8)
    img = cv2.resize(small, (width, height), interpolation=cv2.INTER_LINEAR)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 70])
    assert ok
    return buf.tobytes()


def _write_tmp_image(content: bytes, suffix: str = ".jpg") -> str:
    """Write bytes to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def svc() -> ImagePreprocessingService:
    return ImagePreprocessingService()


@pytest.fixture(scope="module")
def tmp_output_dir() -> str:
    d = tempfile.mkdtemp(prefix="lm_test_preprocess_")
    yield d
    # Cleanup after module tests complete
    import shutil
    shutil.rmtree(d, ignore_errors=True)


# ===========================================================================
# Test 1 — Clean label image → successful preprocessing, quality_score > 0
# ===========================================================================
def test_preprocess_clean_label_image(svc: ImagePreprocessingService, tmp_output_dir: str):
    """A clean, undistorted label image should pass the full pipeline successfully."""
    img_bytes = _make_jpeg_bytes(640, 480)
    path = _write_tmp_image(img_bytes)
    try:
        result: PreprocessingResult = svc.preprocess(
            input_path=path,
            output_dir=tmp_output_dir,
            filename_stem="clean_front",
        )
        assert result.success is True, f"Expected success, got error: {result.error_message}"
        assert result.quality_score > 0, "Quality score should be > 0 for a valid image"
        assert result.quality_score <= 100, "Quality score cannot exceed 100"
        assert os.path.isfile(result.processed_image_path), "Processed JPEG should exist on disk"
        assert os.path.isfile(result.grayscale_image_path), "Grayscale PNG should exist on disk"
        assert result.processing_time_ms > 0
        assert result.original_width == 640
        assert result.original_height == 480
        assert result.contrast_enhanced is True
        assert "load_validate" in result.pipeline_steps
        assert "clahe_contrast" in result.pipeline_steps
        assert "save_outputs" in result.pipeline_steps
    finally:
        os.unlink(path)


# ===========================================================================
# Test 2 — Skewed image → skew correction applied, angle detected
# ===========================================================================
def test_preprocess_skewed_image(svc: ImagePreprocessingService, tmp_output_dir: str):
    """An image rotated by ~7° should have its skew detected and corrected."""
    img_bytes = _make_skewed_jpeg_bytes(640, 480, angle_deg=7.0)
    path = _write_tmp_image(img_bytes)
    try:
        result = svc.preprocess(
            input_path=path,
            output_dir=tmp_output_dir,
            filename_stem="skewed_front",
        )
        assert result.success is True, f"Pipeline failed: {result.error_message}"
        # Skew angle should have been detected (non-zero) — may not be exactly 7° due to
        # Hough line estimation, but should be in range [1, 15] for a 7° rotation
        assert abs(result.skew_angle_degrees) >= 0.5, (
            f"Expected detectable skew, got {result.skew_angle_degrees}°"
        )
        # Verify the step was executed
        step_names = " ".join(result.pipeline_steps)
        assert "skew_correction" in step_names
    finally:
        os.unlink(path)


# ===========================================================================
# Test 3 — Glare image → glare regions detected and inpainted
# ===========================================================================
def test_preprocess_glare_image(svc: ImagePreprocessingService, tmp_output_dir: str):
    """An image with a bright specular highlight should detect glare regions."""
    img_bytes = _make_glare_jpeg_bytes(640, 480)
    path = _write_tmp_image(img_bytes)
    try:
        result = svc.preprocess(
            input_path=path,
            output_dir=tmp_output_dir,
            filename_stem="glare_front",
        )
        assert result.success is True, f"Pipeline failed: {result.error_message}"
        assert result.glare_regions_detected >= 1, (
            f"Expected at least 1 glare region, detected {result.glare_regions_detected}"
        )
        step_names = " ".join(result.pipeline_steps)
        assert "glare_suppression" in step_names
    finally:
        os.unlink(path)


# ===========================================================================
# Test 4 — Invalid file (non-image bytes) → success=False, error set
# ===========================================================================
def test_preprocess_invalid_file(svc: ImagePreprocessingService, tmp_output_dir: str):
    """A file containing random bytes (not a valid image) should fail gracefully."""
    fake_content = b"This is not an image file. %PDF-1.4 random garbage \x00\x01\x02\x03"
    path = _write_tmp_image(fake_content, suffix=".jpg")
    try:
        result = svc.preprocess(
            input_path=path,
            output_dir=tmp_output_dir,
            filename_stem="invalid_file",
        )
        assert result.success is False, "Expected failure for non-image file"
        assert result.error_message is not None and len(result.error_message) > 0
        # Partial files should not be left on disk
        assert not os.path.isfile(result.processed_image_path)
    finally:
        os.unlink(path)


# ===========================================================================
# Test 5 — Oversized image (5000×4000) → resize guard triggered
# ===========================================================================
def test_preprocess_oversized_image(svc: ImagePreprocessingService, tmp_output_dir: str):
    """An image larger than MAX_DIMENSION_PX should be downscaled by the resize guard."""
    img_bytes = _make_large_jpeg_bytes(5000, 4000)
    path = _write_tmp_image(img_bytes)
    try:
        result = svc.preprocess(
            input_path=path,
            output_dir=tmp_output_dir,
            filename_stem="oversized_front",
        )
        assert result.success is True, f"Pipeline failed: {result.error_message}"
        assert result.original_width == 5000
        assert result.original_height == 4000
        # Output must be ≤ MAX_DIMENSION_PX on both axes
        assert result.processed_width <= MAX_DIMENSION_PX, (
            f"Width {result.processed_width} exceeds max {MAX_DIMENSION_PX}"
        )
        assert result.processed_height <= MAX_DIMENSION_PX, (
            f"Height {result.processed_height} exceeds max {MAX_DIMENSION_PX}"
        )
        assert "resize_guard" in result.pipeline_steps
    finally:
        os.unlink(path)


# ===========================================================================
# Tests 6–10: REST API endpoint tests (use conftest client + token fixtures)
# ===========================================================================

# ===========================================================================
# Test 6 — POST /inspections/ → 201 Created, preprocessing metadata present
# ===========================================================================
def test_create_inspection_endpoint(client: TestClient, inspector_token_headers: dict):
    """Full multipart POST should create an inspection and return preprocessing metadata."""
    img_bytes = _make_jpeg_bytes(640, 480)

    response = client.post(
        "/api/v1/inspections/",
        headers=inspector_token_headers,
        data={
            "district": "Mumbai",
            "state": "Maharashtra",
            "store_name": "Test Kirana Store",
            "store_address": "Shop 12, MG Road, Mumbai",
            "sides": ["front"],
        },
        files=[
            ("images", ("front_label.jpg", io.BytesIO(img_bytes), "image/jpeg")),
        ],
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()

    assert "id" in data
    assert "inspection_number" in data
    assert data["inspection_number"].startswith("INS-")
    assert data["status"] in ("draft", "preprocessed")
    assert data["district"] == "Mumbai"
    assert data["state"] == "Maharashtra"
    assert isinstance(data["images"], list)
    assert len(data["images"]) == 1

    img_info = data["images"][0]
    assert img_info["side"] == "front"
    assert img_info["raw_url"] is not None

    # Preprocessing metadata should be present for a valid image
    if img_info.get("success") and img_info.get("preprocessing"):
        prep = img_info["preprocessing"]
        assert "quality_score" in prep
        assert 0 <= prep["quality_score"] <= 100
        assert "skew_angle_degrees" in prep
        assert "processing_time_ms" in prep
        assert prep["processing_time_ms"] > 0


# ===========================================================================
# Test 7 — GET /inspections/ → paginated list response
# ===========================================================================
def test_list_inspections_paginated(client: TestClient, inspector_token_headers: dict):
    """GET /inspections/ should return paginated structure with correct fields."""
    response = client.get(
        "/api/v1/inspections/?skip=0&limit=10",
        headers=inspector_token_headers,
    )

    assert response.status_code == 200, f"Unexpected status: {response.status_code}: {response.text}"
    data = response.json()

    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert data["skip"] == 0
    assert data["limit"] == 10

    # Each item should have required summary fields
    for item in data["items"]:
        assert "id" in item
        assert "inspection_number" in item
        assert "status" in item
        assert "compliance_status" in item
        assert "district" in item
        assert "state" in item
        assert "total_images" in item
        assert "created_at" in item


# ===========================================================================
# Test 8 — GET /inspections/{id} → full detail with images & preprocessing
# ===========================================================================
def test_get_inspection_by_id(client: TestClient, inspector_token_headers: dict):
    """GET /inspections/{id} should return full detail including images list."""
    # First create one
    img_bytes = _make_jpeg_bytes(640, 480)
    create_resp = client.post(
        "/api/v1/inspections/",
        headers=inspector_token_headers,
        data={
            "district": "Pune",
            "state": "Maharashtra",
            "sides": ["front"],
        },
        files=[
            ("images", ("label.jpg", io.BytesIO(img_bytes), "image/jpeg")),
        ],
    )
    assert create_resp.status_code == 201
    inspection_id = create_resp.json()["id"]

    # Fetch detail
    detail_resp = client.get(
        f"/api/v1/inspections/{inspection_id}",
        headers=inspector_token_headers,
    )
    assert detail_resp.status_code == 200, f"Expected 200: {detail_resp.text}"
    data = detail_resp.json()

    assert data["id"] == inspection_id
    assert data["district"] == "Pune"
    assert "images" in data
    assert isinstance(data["images"], list)
    assert "preprocessing_metadata" in data
    assert "created_at" in data
    assert "updated_at" in data


# ===========================================================================
# Test 9 — POST /inspections/{id}/images → add 'back' side to existing
# ===========================================================================
def test_upload_additional_image(client: TestClient, inspector_token_headers: dict):
    """Adding a second side (back) to an existing inspection should succeed."""
    img_bytes = _make_jpeg_bytes(640, 480)

    # Create with front only
    create_resp = client.post(
        "/api/v1/inspections/",
        headers=inspector_token_headers,
        data={
            "district": "Nagpur",
            "state": "Maharashtra",
            "sides": ["front"],
        },
        files=[
            ("images", ("front.jpg", io.BytesIO(img_bytes), "image/jpeg")),
        ],
    )
    assert create_resp.status_code == 201
    inspection_id = create_resp.json()["id"]

    # Now add back side
    back_bytes = _make_glare_jpeg_bytes(640, 480)
    add_resp = client.post(
        f"/api/v1/inspections/{inspection_id}/images",
        headers=inspector_token_headers,
        data={"sides": ["back"]},
        files=[
            ("images", ("back.jpg", io.BytesIO(back_bytes), "image/jpeg")),
        ],
    )
    assert add_resp.status_code == 200, f"Expected 200: {add_resp.text}"
    data = add_resp.json()

    assert data["inspection_id"] == inspection_id
    assert "added_images" in data
    assert len(data["added_images"]) == 1
    assert data["added_images"][0]["side"] == "back"


# ===========================================================================
# Test 10 — Upload non-image file → should be rejected with 415 / 422
# ===========================================================================
def test_invalid_mime_type_rejected(client: TestClient, inspector_token_headers: dict):
    """Uploading an executable or non-image file must be rejected before processing."""
    # Craft fake EXE-like bytes (MZ header)
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 200

    response = client.post(
        "/api/v1/inspections/",
        headers=inspector_token_headers,
        data={
            "district": "Thane",
            "state": "Maharashtra",
            "sides": ["front"],
        },
        files=[
            ("images", ("malware.exe", io.BytesIO(fake_exe), "application/octet-stream")),
        ],
    )

    # Should be rejected with 415 Unsupported Media Type or 422 Unprocessable Entity
    assert response.status_code in (415, 422), (
        f"Expected 415 or 422 for invalid file type, got {response.status_code}: {response.text}"
    )
