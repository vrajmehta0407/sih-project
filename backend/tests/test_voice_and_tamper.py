"""
test_voice_and_tamper.py
========================
Stage 16 — Unit & API Tests for AI Voice Dictation & Forensic ELA Tamper Analysis
"""

import os
import cv2
import pytest
import tempfile
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.voice_assistant_service import voice_assistant_service
from app.services.forensic_tamper_service import forensic_tamper_service

client = TestClient(app)

INSPECTOR_TOKEN = None


def get_inspector_token():
    global INSPECTOR_TOKEN
    if INSPECTOR_TOKEN:
        return INSPECTOR_TOKEN
    resp = client.post("/api/v1/auth/login", data={
        "username": "inspector.mumbai@legalmetrology.gov.in",
        "password": "InspectorPassword@123",
    })
    assert resp.status_code == 200
    INSPECTOR_TOKEN = resp.json()["access_token"]
    return INSPECTOR_TOKEN


def _create_synthetic_jpeg(tampered: bool = False) -> str:
    """Create a temporary JPEG image for ELA testing."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 128
    if tampered:
        # Paste a high-frequency noisy patch simulating an altered sticker
        noise = (np.random.rand(50, 50, 3) * 255).astype(np.uint8)
        img[50:100, 50:100] = noise

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(tmp.name, img)
    tmp.close()
    return tmp.name


# ── Voice Dictation Unit Tests ───────────────────────────────────────────────

def test_voice_dictation_english_mrp_extraction():
    transcript = "Inspected Amul butter at store. The printed MRP is 250 and retailer was selling at 280 rupees. Batch number is B442."
    result = voice_assistant_service.process_transcript(transcript)
    assert result.detected_mrp == 250.0
    assert result.detected_charged_price == 280.0
    assert result.detected_batch == "B442"
    assert "OVERCHARGING_ABOVE_MRP" in result.detected_infractions
    assert result.language_detected == "en"


def test_voice_dictation_hindi_infractions():
    transcript = "दुकानदार ने एमआरपी से ज्यादा रुपया लिया और ड्युअल स्टीकर चिपकाया है।"
    result = voice_assistant_service.process_transcript(transcript)
    assert result.language_detected == "hi"
    assert "OVERCHARGING_ABOVE_MRP" in result.detected_infractions
    assert "DUAL_MRP_STICKER_TAMPERING" in result.detected_infractions


def test_voice_dictation_hinglish_detection():
    transcript = "Retailer ne MRP se jyada price liya and expiry date was expired."
    result = voice_assistant_service.process_transcript(transcript)
    assert result.language_detected == "hinglish"
    assert "EXPIRED_COMMODITY_SALE" in result.detected_infractions


def test_voice_dictation_formatted_note():
    transcript = "Missing customer care details on packaged rice."
    result = voice_assistant_service.process_transcript(transcript)
    assert "MISSING_STATUTORY_DECLARATIONS" in result.detected_infractions
    assert "[Voice Memo Transcription]" in result.formatted_officer_note


# ── Forensic Tamper ELA Unit Tests ──────────────────────────────────────────

def test_forensic_ela_clean_image():
    path = _create_synthetic_jpeg(tampered=False)
    try:
        res = forensic_tamper_service.analyze_tampering(path)
        assert res.tamper_score >= 0.0
        assert isinstance(res.forensic_summary, str)
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_forensic_ela_tampered_hotspot():
    path = _create_synthetic_jpeg(tampered=True)
    try:
        out_heatmap = path + "_heatmap.jpg"
        res = forensic_tamper_service.analyze_tampering(path, out_heatmap)
        assert res.max_error_differential >= 0.0
        assert os.path.exists(out_heatmap)
        os.remove(out_heatmap)
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_forensic_ela_nonexistent_file():
    res = forensic_tamper_service.analyze_tampering("/invalid/image/path.jpg")
    assert res.tamper_score == 0.0
    assert res.is_tampering_suspected is False


# ── API Endpoints Tests ──────────────────────────────────────────────────────

def test_voice_notes_api_endpoint_200():
    token = get_inspector_token()
    # Fetch an existing inspection
    resp = client.get("/api/v1/inspections/?limit=1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    inspections = resp.json().get("inspections", [])
    if inspections:
        insp_id = inspections[0]["id"]
        voice_resp = client.post(
            f"/api/v1/inspections/{insp_id}/voice-notes?transcript=MRP was 100 but retailer charged 130 rupees due to dual sticker",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert voice_resp.status_code == 200
        data = voice_resp.json()
        assert data["detected_mrp"] == 100.0
        assert data["detected_charged_price"] == 130.0
        assert "DUAL_MRP_STICKER_TAMPERING" in data["detected_infractions"]


def test_tamper_heatmap_api_endpoint_200():
    token = get_inspector_token()
    resp = client.get("/api/v1/inspections/?limit=1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    inspections = resp.json().get("inspections", [])
    if inspections:
        insp_id = inspections[0]["id"]
        tamper_resp = client.get(
            f"/api/v1/inspections/{insp_id}/tamper-heatmap",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tamper_resp.status_code == 200
        data = tamper_resp.json()
        assert "tamper_score" in data
        assert "forensic_summary" in data


def test_voice_notes_api_nonexistent_inspection_404():
    token = get_inspector_token()
    resp = client.post(
        "/api/v1/inspections/00000000-0000-0000-0000-000000000000/voice-notes?transcript=test",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
