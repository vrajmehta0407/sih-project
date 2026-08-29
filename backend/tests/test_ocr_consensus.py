"""
test_ocr_consensus.py
======================
Stage 3 — Unit & API Tests for Dual OCR Engine Integration & Consensus Pipeline

Test coverage (10 tests):
  1. test_paddle_ocr_engine_execution          — RapidOCR/PaddleOCR extracts text & boxes on synthetic image
  2. test_tesseract_ocr_engine_execution       — Tesseract engine runs / handles availability gracefully
  3. test_consensus_identical_strings          — High-agreement text produces consensus_agreed tokens
  4. test_consensus_minor_typo_resolution      — Fuzzy match resolves minor character variance
  5. test_consensus_disagreement_detection     — Conflicting digits (e.g. MRP 250 vs 350) flags disagreement
  6. test_spatial_bounding_box_iou             — IoU calculation across overlapping and disjoint geometries
  7. test_run_dual_ocr_service_on_inspection   — Service updates Product & advances status to 'extracted'
  8. test_post_ocr_endpoint_200                — POST /inspections/{id}/ocr returns 200 with consensus payload
  9. test_get_ocr_endpoint_200                 — GET /inspections/{id}/ocr returns structured consensus data
 10. test_ocr_on_inspection_without_images_400 — Rejects OCR on inspection with no image assets
"""

import io
import os
import tempfile
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.ocr.ocr_engine import (
    PaddleOCREngine,
    TesseractOCREngine,
    OCREngineResult,
    OCRTextBox,
)
from app.services.ocr.consensus_engine import (
    ConsensusEngine,
    compute_levenshtein_similarity,
    compute_iou,
    has_digit_mismatch,
)
from app.services.ocr.ocr_service import ocr_service
from app.models.inspection import Inspection
from app.models.product import Product


# ---------------------------------------------------------------------------
# Synthetic Image Factory
# ---------------------------------------------------------------------------
def _create_label_image(text_lines: list[str], width: int = 800, height: int = 400) -> np.ndarray:
    """Generates an image with rendered synthetic text lines for OCR testing."""
    img = np.full((height, width, 3), 255, dtype=np.uint8)
    y = 60
    for line in text_lines:
        cv2.putText(
            img,
            line,
            (40, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        y += 60
    return img


def _save_tmp_label_image(text_lines: list[str]) -> str:
    img = _create_label_image(text_lines)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    cv2.imwrite(path, img)
    return path


# ===========================================================================
# Test 1 — PaddleOCR Engine Execution
# ===========================================================================
def test_paddle_ocr_engine_execution():
    """PaddleOCR should successfully detect text lines and return valid bounding boxes."""
    engine = PaddleOCREngine()
    assert engine.is_available() is True

    test_lines = ["MRP Rs. 250.00", "NET WT: 500 g", "BATCH NO: B2026"]
    img_path = _save_tmp_label_image(test_lines)

    try:
        res = engine.extract(img_path)
        assert res.success is True, f"PaddleOCR failed: {res.error_message}"
        assert res.engine_name == "paddleocr"
        assert res.processing_time_ms > 0
        assert len(res.boxes) > 0

        extracted_upper = res.raw_text.upper()
        # Verify core keywords were captured
        assert "MRP" in extracted_upper or "250" in extracted_upper or "NET" in extracted_upper
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)


# ===========================================================================
# Test 2 — Tesseract OCR Engine Execution (or Resilient Fallback)
# ===========================================================================
def test_tesseract_ocr_engine_execution():
    """Tesseract engine extracts text if binary present, or falls back gracefully."""
    engine = TesseractOCREngine()
    test_lines = ["LEGAL METROLOGY SCANNER", "MFD: 01/2026"]
    img_path = _save_tmp_label_image(test_lines)

    try:
        res = engine.extract(img_path)
        assert res.engine_name == "tesseract"
        if engine.is_available():
            assert res.success is True
            assert len(res.boxes) >= 0
        else:
            # Clean fallback when binary not on PATH
            assert res.success is False
            assert "Tesseract binary is not installed" in (res.error_message or "")
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)


# ===========================================================================
# Test 3 — Consensus on Identical Strings
# ===========================================================================
def test_consensus_identical_strings():
    """Identical outputs from both engines should produce consensus_agreed status."""
    consensus = ConsensusEngine()

    paddle_box = OCRTextBox(
        text="MRP Rs. 150.00",
        confidence=0.98,
        box=[[10, 10], [150, 10], [150, 40], [10, 40]],
        engine="paddleocr",
    )
    tess_box = OCRTextBox(
        text="MRP Rs. 150.00",
        confidence=0.95,
        box=[[12, 10], [152, 10], [152, 40], [12, 40]],
        engine="tesseract",
    )

    paddle_res = OCREngineResult("paddleocr", True, "MRP Rs. 150.00", [paddle_box])
    tess_res = OCREngineResult("tesseract", True, "MRP Rs. 150.00", [tess_box])

    result = consensus.reconcile(paddle_res, tess_res)

    assert result.has_ocr_disagreement is False
    assert result.disagreement_count == 0
    assert result.overall_confidence >= 0.95
    assert len(result.tokens) == 1
    assert result.tokens[0].chosen_engine == "consensus_agreed"
    assert result.tokens[0].text == "MRP Rs. 150.00"


# ===========================================================================
# Test 4 — Consensus Minor Typo Resolution
# ===========================================================================
def test_consensus_minor_typo_resolution():
    """Fuzzy Levenshtein matching resolves minor OCR character variance."""
    consensus = ConsensusEngine()

    paddle_box = OCRTextBox(
        text="Packed by ABC Foods",
        confidence=0.96,
        box=[[20, 50], [250, 50], [250, 80], [20, 80]],
        engine="paddleocr",
    )
    tess_box = OCRTextBox(
        text="Packed by ABC F00ds",  # Tesseract misread 'oo' as '00'
        confidence=0.72,
        box=[[22, 52], [248, 52], [248, 80], [22, 80]],
        engine="tesseract",
    )

    paddle_res = OCREngineResult("paddleocr", True, "Packed by ABC Foods", [paddle_box])
    tess_res = OCREngineResult("tesseract", True, "Packed by ABC F00ds", [tess_box])

    result = consensus.reconcile(paddle_res, tess_res)

    # Should select higher confidence PaddleOCR token
    assert result.tokens[0].text == "Packed by ABC Foods"
    assert result.tokens[0].chosen_engine == "paddleocr"


# ===========================================================================
# Test 5 — Consensus Disagreement Detection (Price Conflict)
# ===========================================================================
def test_consensus_disagreement_detection():
    """Conflicting numbers in statutory fields must trigger disagreement flags."""
    consensus = ConsensusEngine()

    paddle_box = OCRTextBox(
        text="MRP Rs. 250.00",
        confidence=0.88,
        box=[[30, 100], [200, 100], [200, 130], [30, 130]],
        engine="paddleocr",
    )
    tess_box = OCRTextBox(
        text="MRP Rs. 350.00",  # Conflicting price!
        confidence=0.85,
        box=[[32, 100], [198, 100], [198, 130], [32, 130]],
        engine="tesseract",
    )

    paddle_res = OCREngineResult("paddleocr", True, "MRP Rs. 250.00", [paddle_box])
    tess_res = OCREngineResult("tesseract", True, "MRP Rs. 350.00", [tess_box])

    result = consensus.reconcile(paddle_res, tess_res)

    assert result.has_ocr_disagreement is True
    assert result.disagreement_count >= 1
    assert result.manual_review_required is True
    assert result.tokens[0].is_disagreement is True
    assert "Numerical conflict" in (result.tokens[0].disagreement_reason or "")


# ===========================================================================
# Test 6 — Spatial Bounding Box IoU Calculation
# ===========================================================================
def test_spatial_bounding_box_iou():
    """Verify Intersection over Union algorithm."""
    # Complete overlap
    box_a = (10, 10, 100, 50)
    assert compute_iou(box_a, box_a) == 1.0

    # Disjoint boxes
    box_b = (200, 200, 100, 50)
    assert compute_iou(box_a, box_b) == 0.0

    # Partial overlap (50% horizontally)
    box_c = (60, 10, 100, 50)
    iou = compute_iou(box_a, box_c)
    assert 0.25 <= iou <= 0.40


# ===========================================================================
# Test 7 — OCR Service Integration on Inspection
# ===========================================================================
def test_run_dual_ocr_service_on_inspection(db_session: Session):
    """OCR service should process inspection image sides and update DB records."""
    img_path = _save_tmp_label_image(["BEST BEFORE 12 MONTHS", "NET QUANTITY: 1 kg"])

    try:
        insp = Inspection(
            inspection_number="INS-TEST-OCR-001",
            inspector_id="test-inspector-uuid",
            district="Mumbai",
            state="Maharashtra",
            status="preprocessed",
            preprocessed_images=[{"side": "front", "file_path": img_path}],
        )
        db_session.add(insp)
        db_session.commit()
        db_session.refresh(insp)

        result = ocr_service.process_inspection_ocr(
            db=db_session,
            inspection_id=str(insp.id),
            user_id="test-inspector-uuid",
        )

        assert result["status"] == "extracted"
        assert "ocr_consensus" in result
        assert "front" in result["ocr_consensus"]["per_side"]

        # Check Product row was populated
        prod = db_session.query(Product).filter(Product.inspection_id == str(insp.id)).first()
        assert prod is not None
        assert prod.extracted_fields_consensus is not None
        assert len(prod.extracted_fields_consensus["per_side"]) == 1
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)


# ===========================================================================
# Test 8 — POST /api/v1/inspections/{id}/ocr Endpoint (200)
# ===========================================================================
def test_post_ocr_endpoint_200(client: TestClient, inspector_token_headers: dict):
    """POST /inspections/{id}/ocr triggers dual OCR and returns 200 OK."""
    # Create inspection first
    img_bytes = io.BytesIO()
    cv2_img = _create_label_image(["COUNTRY OF ORIGIN: INDIA", "MRP Rs. 99.00"])
    _, buf = cv2.imencode(".jpg", cv2_img)
    img_bytes.write(buf.tobytes())
    img_bytes.seek(0)

    create_resp = client.post(
        "/api/v1/inspections/",
        headers=inspector_token_headers,
        data={"district": "Mumbai", "state": "Maharashtra", "sides": ["front"]},
        files=[("images", ("label.jpg", img_bytes, "image/jpeg"))],
    )
    assert create_resp.status_code == 201
    inspection_id = create_resp.json()["id"]

    # Trigger OCR endpoint
    ocr_resp = client.post(
        f"/api/v1/inspections/{inspection_id}/ocr",
        headers=inspector_token_headers,
    )
    assert ocr_resp.status_code == 200, f"Expected 200: {ocr_resp.text}"
    data = ocr_resp.json()

    assert data["inspection_id"] == inspection_id
    assert data["status"] == "extracted"
    assert "ocr_consensus" in data
    assert "aggregated_consensus_text" in data["ocr_consensus"]


# ===========================================================================
# Test 9 — GET /api/v1/inspections/{id}/ocr Endpoint (200)
# ===========================================================================
def test_get_ocr_endpoint_200(client: TestClient, inspector_token_headers: dict):
    """GET /inspections/{id}/ocr retrieves existing consensus matrix."""
    # Create and run OCR
    img_bytes = io.BytesIO()
    cv2_img = _create_label_image(["MFG DATE: 05/2026", "EXP DATE: 05/2027"])
    _, buf = cv2.imencode(".jpg", cv2_img)
    img_bytes.write(buf.tobytes())
    img_bytes.seek(0)

    create_resp = client.post(
        "/api/v1/inspections/",
        headers=inspector_token_headers,
        data={"district": "Thane", "state": "Maharashtra", "sides": ["front"]},
        files=[("images", ("label.jpg", img_bytes, "image/jpeg"))],
    )
    inspection_id = create_resp.json()["id"]

    # Run OCR
    client.post(f"/api/v1/inspections/{inspection_id}/ocr", headers=inspector_token_headers)

    # Fetch OCR data
    get_resp = client.get(
        f"/api/v1/inspections/{inspection_id}/ocr",
        headers=inspector_token_headers,
    )
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["inspection_id"] == inspection_id
    assert "ocr_consensus" in data


# ===========================================================================
# Test 10 — OCR on Empty Inspection Returns 400 Bad Request
# ===========================================================================
def test_ocr_on_inspection_without_images_400(
    client: TestClient,
    inspector_token_headers: dict,
    db_session: Session,
):
    """Attempting OCR on an inspection record with no images returns 400."""
    insp = Inspection(
        inspection_number="INS-EMPTY-001",
        inspector_id="dummy-inspector",
        district="Mumbai",
        state="Maharashtra",
        status="draft",
        raw_images=[],
        preprocessed_images=[],
    )
    db_session.add(insp)
    db_session.commit()
    db_session.refresh(insp)

    # Make inspector the owner by fetching logged-in user profile
    me_resp = client.get("/api/v1/auth/me", headers=inspector_token_headers)
    inspector_user_id = me_resp.json()["data"]["id"]
    insp.inspector_id = inspector_user_id
    db_session.commit()

    resp = client.post(
        f"/api/v1/inspections/{insp.id}/ocr",
        headers=inspector_token_headers,
    )
    assert resp.status_code == 400
    assert "does not contain any images" in resp.json()["detail"]
