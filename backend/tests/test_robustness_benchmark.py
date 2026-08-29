"""
test_robustness_benchmark.py
============================
Stage 24 — Unit & API Tests for OCR Synthetic Stress-Testing & Adversarial Benchmark
"""

import pytest
import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.robustness_benchmark_service import robustness_benchmark_service

client = TestClient(app)


# ── Robustness Benchmark Unit Tests ──────────────────────────────────────────

def test_robustness_benchmark_service_default_image():
    res = robustness_benchmark_service.run_stress_test()
    assert res.benchmark_id.startswith("BENCH-2026-")
    assert res.overall_robustness_score >= 80.0
    assert res.total_profiles_evaluated == 6
    assert res.profiles_passed_count >= 5
    assert len(res.degradation_results) == 6


def test_robustness_benchmark_contains_6_profiles():
    res = robustness_benchmark_service.run_stress_test()
    names = {p.profile_name for p in res.degradation_results}
    expected = {
        "GAUSSIAN_BLUR",
        "PERSPECTIVE_SKEW",
        "SPECULAR_GLARE",
        "SENSOR_NOISE",
        "POLYBAG_CRINKLE",
        "INK_FADING",
    }
    assert names == expected


def test_robustness_benchmark_gaussian_blur_profile():
    res = robustness_benchmark_service.run_stress_test()
    blur = next(p for p in res.degradation_results if p.profile_name == "GAUSSIAN_BLUR")
    assert blur.post_restoration_ocr_conf > blur.pre_restoration_ocr_conf
    assert blur.character_recovery_rate >= 90.0
    assert blur.is_rule6_parsable is True


def test_robustness_benchmark_perspective_skew_profile():
    res = robustness_benchmark_service.run_stress_test()
    skew = next(p for p in res.degradation_results if p.profile_name == "PERSPECTIVE_SKEW")
    assert skew.severity_level == "SEVERE"
    assert skew.character_recovery_rate >= 85.0


def test_robustness_benchmark_specular_glare_profile():
    res = robustness_benchmark_service.run_stress_test()
    glare = next(p for p in res.degradation_results if p.profile_name == "SPECULAR_GLARE")
    assert glare.fields_extracted_count >= 4


def test_robustness_benchmark_sensor_noise_profile():
    res = robustness_benchmark_service.run_stress_test()
    noise = next(p for p in res.degradation_results if p.profile_name == "SENSOR_NOISE")
    assert noise.post_restoration_ocr_conf >= 90.0
    assert noise.character_recovery_rate >= 90.0


def test_robustness_benchmark_polybag_crinkle_profile():
    res = robustness_benchmark_service.run_stress_test()
    crinkle = next(p for p in res.degradation_results if p.profile_name == "POLYBAG_CRINKLE")
    assert crinkle.is_rule6_parsable is True


def test_robustness_benchmark_ink_fading_profile():
    res = robustness_benchmark_service.run_stress_test()
    fading = next(p for p in res.degradation_results if p.profile_name == "INK_FADING")
    assert fading.character_recovery_rate >= 85.0
    assert "OpenCV Restoration" in res.pipeline_resilience_summary


# ── Robustness Benchmark API Tests ───────────────────────────────────────────

def test_robustness_benchmark_stress_test_api_200():
    img = np.full((300, 400, 3), 240, dtype=np.uint8)
    cv2.putText(img, "TEST LABEL MRP Rs. 200", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    _, buf = cv2.imencode(".jpg", img)

    files = {"image": ("test_label.jpg", buf.tobytes(), "image/jpeg")}
    resp = client.post("/api/v1/inspections/benchmark/stress-test", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["benchmark_id"].startswith("BENCH-2026-")
    assert data["overall_robustness_score"] >= 80.0
    assert data["total_profiles_evaluated"] == 6


def test_robustness_benchmark_latest_get_api_200():
    resp = client.get("/api/v1/inspections/benchmark/latest")
    assert resp.status_code == 200
    data = resp.json()
    assert "robustness_grade" in data
    assert "average_character_recovery_rate" in data
    assert len(data["degradation_results"]) == 6
