"""
test_counterfeit_and_registry.py
=================================
Stage 13 — Unit & API Tests for AI Counterfeit Detection & National Product Registry
"""

import os
import pytest
import tempfile
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app
from app.services.counterfeit_detection_service import (
    counterfeit_detection_service,
    CounterfeitDetectionService,
    COUNTERFEIT_THRESHOLD,
)

client = TestClient(app)

ADMIN_TOKEN = None


def get_admin_token():
    global ADMIN_TOKEN
    if ADMIN_TOKEN:
        return ADMIN_TOKEN
    resp = client.post("/api/v1/auth/login", data={
        "username": "admin@legalmetrology.gov.in",
        "password": "AdminPassword@123",
    })
    assert resp.status_code == 200
    ADMIN_TOKEN = resp.json()["access_token"]
    return ADMIN_TOKEN


# ── Helper to generate synthetic JPEG images ─────────────────────────────────
def _make_temp_jpeg(pattern: str = "random") -> str:
    """Generate a synthetic JPEG and return its path."""
    h, w = 300, 300
    if pattern == "checkerboard":
        img = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(0, h, 30):
            for j in range(0, w, 30):
                if (i // 30 + j // 30) % 2 == 0:
                    img[i:i+30, j:j+30] = (200, 200, 200)
    elif pattern == "edges":
        img = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(0, h, 20):
            img[i, :] = (180, 180, 180)
            img[:, i] = (180, 180, 180)
    else:
        img = (np.random.rand(h, w, 3) * 255).astype(np.uint8)

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(tmp.name, img)
    tmp.close()
    return tmp.name


# ── Unit Tests (service logic) ────────────────────────────────────────────────

def test_identical_images_high_similarity():
    path = _make_temp_jpeg("checkerboard")
    try:
        result = counterfeit_detection_service.compare(path, path)
        # Identical image should yield very high similarity
        assert result.similarity_score > 70.0
        assert result.is_suspected_counterfeit is False
    finally:
        os.unlink(path)


def test_different_random_images_low_similarity():
    path_a = _make_temp_jpeg("random")
    path_b = _make_temp_jpeg("random")
    try:
        result = counterfeit_detection_service.compare(path_a, path_b)
        # Two unrelated random images → low match → suspected counterfeit
        assert result.similarity_score < COUNTERFEIT_THRESHOLD or result.confidence in ("LOW", "INSUFFICIENT")
    finally:
        os.unlink(path_a)
        os.unlink(path_b)


def test_missing_reference_file_returns_insufficient():
    path = _make_temp_jpeg("checkerboard")
    try:
        result = counterfeit_detection_service.compare(path, "/nonexistent/reference.jpg")
        assert result.confidence == "INSUFFICIENT"
        assert result.is_suspected_counterfeit is True
    finally:
        os.unlink(path)


def test_missing_query_file_returns_insufficient():
    path = _make_temp_jpeg("checkerboard")
    try:
        result = counterfeit_detection_service.compare("/nonexistent/query.jpg", path)
        assert result.confidence == "INSUFFICIENT"
    finally:
        os.unlink(path)


def test_similarity_result_fields_present():
    path = _make_temp_jpeg("edges")
    try:
        result = counterfeit_detection_service.compare(path, path)
        assert hasattr(result, "similarity_score")
        assert hasattr(result, "good_matches")
        assert hasattr(result, "is_suspected_counterfeit")
        assert hasattr(result, "confidence")
        assert hasattr(result, "explanation")
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 10
    finally:
        os.unlink(path)


# ── API Tests ────────────────────────────────────────────────────────────────

def test_register_product_api_201():
    import random
    token = get_admin_token()
    unique_barcode = f"890{random.randint(1000000000, 9999999999)}"[:13]
    payload = {
        "barcode_ean13": unique_barcode,
        "product_name": "SIH Test Biscuit 100g",
        "manufacturer_name": "Test Foods Pvt Ltd",
        "manufacturer_address": "Plot 42, MIDC, Pune 411018",
        "declared_mrp": 15.0,
        "declared_net_quantity": "100 g",
        "product_category": "Food & Beverages",
        "country_of_origin": "India",
    }
    resp = client.post(
        "/api/v1/registry/products",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["product_name"] == "SIH Test Biscuit 100g"
    assert data["barcode_ean13"] == unique_barcode
    assert data["is_active"] is True


def test_register_duplicate_barcode_409():
    import random
    token = get_admin_token()
    unique_barcode = f"890{random.randint(1000000000, 9999999999)}"[:13]
    payload = {
        "barcode_ean13": unique_barcode,
        "product_name": "Product A",
        "manufacturer_name": "Test Foods Pvt Ltd",
        "manufacturer_address": "Test Address",
        "declared_mrp": 10.0,
        "declared_net_quantity": "50 g",
    }
    # Register first time
    resp1 = client.post(
        "/api/v1/registry/products",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 201

    # Register duplicate barcode second time
    resp2 = client.post(
        "/api/v1/registry/products",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 409


def test_list_registered_products_200():
    token = get_admin_token()
    resp = client.get(
        "/api/v1/registry/products",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_lookup_by_barcode_200():
    import random
    token = get_admin_token()
    unique_barcode = f"890{random.randint(1000000000, 9999999999)}"[:13]
    payload = {
        "barcode_ean13": unique_barcode,
        "product_name": "Lookup Test Product",
        "manufacturer_name": "Test Foods Pvt Ltd",
        "manufacturer_address": "Test Address",
        "declared_mrp": 50.0,
        "declared_net_quantity": "250 g",
    }
    # Register first
    resp1 = client.post(
        "/api/v1/registry/products",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 201

    # Lookup by barcode
    resp2 = client.get(
        f"/api/v1/registry/products/barcode/{unique_barcode}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["barcode_ean13"] == unique_barcode


def test_lookup_nonexistent_barcode_404():
    token = get_admin_token()
    resp = client.get(
        "/api/v1/registry/products/barcode/0000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
