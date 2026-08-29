"""
endpoints/public_apis.py
========================
Stage 26 — Public APIs & AI Integration Hub Endpoints
Routes for Open Food Facts, India Post PIN Code, Forex, Weather & Gemini LLM.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field

from app.services.public_api_service import public_api_service

router = APIRouter()
logger = logging.getLogger(__name__)


# ===========================================================================
# Schemas for Public APIs Endpoints
# ===========================================================================

class AIChatRequest(BaseModel):
    prompt: str = Field(..., description="Query or legal question for the AI model")
    system_instruction: Optional[str] = Field(
        None, description="Optional custom system prompt instruction"
    )
    model_name: Optional[str] = Field(
        "gemini-1.5-flash", description="LLM model identifier"
    )


# ===========================================================================
# Endpoints
# ===========================================================================

@router.get(
    "/status",
    summary="Get status and health of all integrated Public APIs & AI keys",
)
async def get_public_apis_status():
    """
    Returns live connectivity and configuration status for:
    - Open Food Facts API (Food & Barcode data)
    - India Postal PIN Code API (Rule 6(1)(a) Address validation)
    - ExchangeRate-API / Frankfurter (Forex & Imported goods)
    - Open-Meteo API (GIS field weather forecast)
    - Google Gemini AI API (Statutory LLM Copilot)
    """
    return await public_api_service.get_all_apis_status()


@router.get(
    "/barcode/{barcode}",
    summary="Lookup commodity declarations by Barcode (Open Food Facts)",
)
async def lookup_barcode(barcode: str):
    """
    Query Open Food Facts public registry to retrieve declared product name,
    brand, net quantity, country of origin, packaging, and product photos.
    """
    result = await public_api_service.lookup_barcode_openfoodfacts(barcode)
    return result


@router.get(
    "/pincode/{pincode}",
    summary="Verify Indian Postal PIN Code (India Post Open API)",
)
async def verify_pincode(pincode: str):
    """
    Validates a 6-digit Indian PIN code against official India Post directory,
    returning District, State, Delivery Post Offices, and Rule 6(1)(a) compliance badge.
    """
    result = await public_api_service.verify_indian_pincode(pincode)
    return result


@router.get(
    "/forex",
    summary="Get live Foreign Exchange Rates for Imported Goods",
)
async def get_forex_rates(base: str = Query("USD", description="Base foreign currency code")):
    """
    Fetches real-time foreign currency exchange rates against INR for imported
    pre-packaged commodities compliance auditing under Rule 6(1)(d).
    """
    result = await public_api_service.get_live_exchange_rates(base)
    return result


@router.get(
    "/weather",
    summary="Get live Mandi & Market Weather Forecast (Open-Meteo)",
)
async def get_market_weather(
    lat: float = Query(19.0760, description="Latitude (e.g. Mumbai 19.0760)"),
    lon: float = Query(72.8777, description="Longitude (e.g. Mumbai 72.8777)"),
):
    """
    Retrieves live field inspection weather, precipitation probability, and
    inspection raid feasibility advisory for enforcement teams.
    """
    result = await public_api_service.get_mandi_weather(lat, lon)
    return result


@router.post(
    "/ai-chat",
    summary="Direct Chat with Gemini AI Legal Metrology Copilot",
)
async def direct_ai_chat(req: AIChatRequest):
    """
    Sends a query directly to Google Gemini AI API with Legal Metrology
    statutory context grounding.
    """
    result = await public_api_service.query_gemini_llm(
        prompt=req.prompt,
        system_instruction=req.system_instruction,
        model_name=req.model_name or "gemini-1.5-flash",
    )
    return result
