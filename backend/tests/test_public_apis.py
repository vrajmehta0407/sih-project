"""
test_public_apis.py
===================
Stage 26 — Unit & API Integration Tests for Public APIs & AI Services
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.services.public_api_service import public_api_service
from app.services.regulatory_copilot_service import regulatory_copilot_service
from app.schemas.copilot import CopilotQueryRequest

client = TestClient(app)


# ===========================================================================
# 1. Open Food Facts Service Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_lookup_barcode_openfoodfacts_invalid_barcode():
    res = await public_api_service.lookup_barcode_openfoodfacts("")
    assert res["success"] is False
    assert "Invalid barcode" in res["error"]


@pytest.mark.asyncio
async def test_lookup_barcode_openfoodfacts_mock_success():
    mock_payload = {
        "status": 1,
        "product": {
            "product_name": "Premium Basmati Rice",
            "brands": "India Gate",
            "quantity": "5 kg",
            "origins": "India",
            "categories": "Plant-based foods, Grains, Rice",
            "packaging": "Pouch, Plastic",
            "image_url": "https://images.openfoodfacts.org/rice.jpg",
        }
    }
    
    mock_resp = httpx.Response(200, json=mock_payload, request=httpx.Request("GET", "https://example.com"))
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await public_api_service.lookup_barcode_openfoodfacts("8901234567890")
        assert res["success"] is True
        assert res["product_name"] == "Premium Basmati Rice"
        assert res["brand"] == "India Gate"
        assert res["declared_quantity"] == "5 kg"
        assert res["origin_country"] == "India"


# ===========================================================================
# 2. India Postal PIN Code Service Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_verify_indian_pincode_invalid_length():
    res = await public_api_service.verify_indian_pincode("123")
    assert res["is_valid"] is False
    assert "Must be exactly 6 numeric digits" in res["error"]


@pytest.mark.asyncio
async def test_verify_indian_pincode_mock_success():
    mock_payload = [
        {
            "Status": "Success",
            "PostOffice": [
                {
                    "Name": "New Delhi G.P.O.",
                    "BranchType": "Head Post Office",
                    "DeliveryStatus": "Delivery",
                    "District": "Central Delhi",
                    "State": "Delhi",
                    "Circle": "Delhi Circle",
                }
            ]
        }
    ]

    mock_resp = httpx.Response(200, json=mock_payload, request=httpx.Request("GET", "https://example.com"))
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await public_api_service.verify_indian_pincode("110001")
        assert res["is_valid"] is True
        assert res["district"] == "Central Delhi"
        assert res["state"] == "Delhi"
        assert res["rule_6_1_a_compliance"] == "VALID_PINCODE"


# ===========================================================================
# 3. Foreign Exchange Rates Service Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_get_live_exchange_rates_mock_success():
    mock_payload = {
        "result": "success",
        "base_code": "USD",
        "rates": {
            "INR": 83.75,
            "EUR": 0.92,
            "GBP": 0.78,
            "USD": 1.0,
        },
        "time_last_update_utc": "Thu, 27 Aug 2026 10:00:00 +0000",
    }

    mock_resp = httpx.Response(200, json=mock_payload, request=httpx.Request("GET", "https://example.com"))
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await public_api_service.get_live_exchange_rates("USD")
        assert res["success"] is True
        assert res["inr_exchange_rate"] == 83.75
        assert res["rates"]["EUR"] == 0.92


# ===========================================================================
# 4. Open-Meteo Weather Service Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_get_mandi_weather_mock_success():
    mock_payload = {
        "current_weather": {
            "temperature": 29.5,
            "windspeed": 12.4,
            "weathercode": 1,
        }
    }

    mock_resp = httpx.Response(200, json=mock_payload, request=httpx.Request("GET", "https://example.com"))
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await public_api_service.get_mandi_weather(19.0760, 72.8777)
        assert res["success"] is True
        assert res["temperature_celsius"] == 29.5
        assert res["is_favorable_for_raid"] is True


# ===========================================================================
# 5. Gemini AI LLM & Copilot Fallback Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_query_gemini_without_api_key():
    with patch("app.core.config.settings.GEMINI_API_KEY", None):
        res = await public_api_service.query_gemini_llm("What is Rule 6?")
        assert res["success"] is False
        assert res["configured"] is False
        assert "GEMINI_API_KEY is not set" in res["error"]


@pytest.mark.asyncio
async def test_regulatory_copilot_async_query_with_gemini_fallback():
    req = CopilotQueryRequest(query="What is the unit sale price exemption for 10 grams?")
    res = await regulatory_copilot_service.async_query(req)
    assert res.detected_intent == "USP_EXEMPTION_RULES"
    assert len(res.citations) >= 1
    assert "Rule 6(11)" in res.citations[0].section_or_rule_no


# ===========================================================================
# 6. Public APIs Fast-API Endpoints Tests
# ===========================================================================

def test_api_public_apis_status():
    response = client.get("/api/v1/public-apis/status")
    assert response.status_code == 200
    data = response.json()
    assert "public_apis" in data
    assert "ai_llm_keys" in data
    assert len(data["public_apis"]) >= 4


def test_api_public_apis_pincode_endpoint():
    response = client.get("/api/v1/public-apis/pincode/110001")
    assert response.status_code == 200
    data = response.json()
    assert "pincode" in data or "success" in data


def test_api_public_apis_forex_endpoint():
    response = client.get("/api/v1/public-apis/forex?base=USD")
    assert response.status_code == 200
    data = response.json()
    assert "inr_exchange_rate" in data or "rates" in data


def test_api_public_apis_weather_endpoint():
    response = client.get("/api/v1/public-apis/weather?lat=19.0760&lon=72.8777")
    assert response.status_code == 200
    data = response.json()
    assert "temperature_celsius" in data or "latitude" in data


def test_api_public_apis_ai_chat_endpoint():
    response = client.post(
        "/api/v1/public-apis/ai-chat",
        json={"prompt": "Explain Section 36(1) penalty"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data or "success" in data
