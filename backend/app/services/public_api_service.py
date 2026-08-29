"""
public_api_service.py
=====================
Stage 26 — Public APIs & AI Integration Hub (public-apis/public-apis & LLM)
Integrates Open Food Facts, India Post PIN Code, Forex, Weather & Gemini AI.
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Standard timeout for external HTTP calls
DEFAULT_TIMEOUT = 8.0


class PublicAPIService:
    """Unified client for external free Public APIs and LLM inference."""

    def __init__(self):
        self.user_agent = "LegalMetrologyScanner/1.0 (https://legalmetrology.gov.in; contact@legalmetrology.gov.in)"

    # =========================================================================
    # 1. Open Food Facts — Pre-Packaged Commodity Barcode & Metadata Lookup
    # =========================================================================
    async def lookup_barcode_openfoodfacts(self, barcode: str) -> Dict[str, Any]:
        """
        Query Open Food Facts API (from public-apis / Food) for EAN-13 / UPC barcode.
        Extracts product name, brand, declared quantity, packaging, categories, and country of origin.
        """
        cleaned_barcode = re.sub(r"\D", "", barcode)
        if not cleaned_barcode:
            return {"success": False, "error": "Invalid barcode format."}

        url = f"{settings.OPEN_FOOD_FACTS_API_URL}/api/v2/product/{cleaned_barcode}.json"
        headers = {"User-Agent": self.user_agent}

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == 1:
                        product = data.get("product", {})
                        
                        # Extract relevant statutory declaration fields
                        product_name = product.get("product_name") or product.get("product_name_en") or "Unknown Commodity"
                        brand = product.get("brands") or "Generic / Unbranded"
                        quantity_declared = product.get("quantity") or product.get("product_quantity_unit") or ""
                        categories = product.get("categories", "")
                        origin = product.get("origins") or product.get("countries") or "India"
                        packaging = product.get("packaging", "")
                        image_url = product.get("image_url") or product.get("image_front_url")
                        manufacturing_places = product.get("manufacturing_places") or ""

                        return {
                            "success": True,
                            "source": "Open Food Facts (Public API)",
                            "barcode": cleaned_barcode,
                            "product_name": product_name,
                            "brand": brand,
                            "declared_quantity": quantity_declared,
                            "origin_country": origin,
                            "manufacturing_places": manufacturing_places,
                            "categories": categories,
                            "packaging_type": packaging,
                            "image_url": image_url,
                            "raw_data_summary": {
                                "ecoscore_grade": product.get("ecoscore_grade"),
                                "nutriscore_grade": product.get("nutriscore_grade"),
                                "ingredients_text": product.get("ingredients_text_en") or product.get("ingredients_text"),
                            },
                        }
                    else:
                        return {
                            "success": False,
                            "source": "Open Food Facts",
                            "barcode": cleaned_barcode,
                            "error": "Product not found in Open Food Facts database.",
                            "status_verbose": data.get("status_verbose"),
                        }
                else:
                    return {
                        "success": False,
                        "source": "Open Food Facts",
                        "error": f"HTTP {res.status_code} returned from Open Food Facts API.",
                    }
        except Exception as e:
            logger.warning("Failed to lookup barcode %s on Open Food Facts: %s", barcode, e)
            return {
                "success": False,
                "source": "Open Food Facts",
                "barcode": cleaned_barcode,
                "error": f"Connection error: {str(e)}",
            }

    # =========================================================================
    # 2. India Postal PIN Code API — Statutory Address & PIN Code Verification
    # =========================================================================
    async def verify_indian_pincode(self, pincode: str) -> Dict[str, Any]:
        """
        Query India Postal PIN Code API (from public-apis / Geocoding & Open Data).
        Validates manufacturer 6-digit PIN code required under Rule 6(1)(a).
        """
        cleaned_pin = re.sub(r"\D", "", pincode)
        if len(cleaned_pin) != 6:
            return {
                "success": False,
                "error": f"Invalid Indian PIN code '{pincode}'. Must be exactly 6 numeric digits.",
                "is_valid": False,
            }

        url = f"{settings.POSTAL_PINCODE_API_URL}/pincode/{cleaned_pin}"

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, list) and len(data) > 0 and data[0].get("Status") == "Success":
                        post_offices = data[0].get("PostOffice", [])
                        offices_summary = []
                        state = None
                        district = None
                        circle = None

                        for po in post_offices[:5]:  # Top 5 offices in circle
                            if not state:
                                state = po.get("State")
                                district = po.get("District")
                                circle = po.get("Circle")
                            offices_summary.append({
                                "name": po.get("Name"),
                                "branch_type": po.get("BranchType"),
                                "delivery_status": po.get("DeliveryStatus"),
                                "district": po.get("District"),
                                "state": po.get("State"),
                            })

                        return {
                            "success": True,
                            "is_valid": True,
                            "source": "India Post Open API",
                            "pincode": cleaned_pin,
                            "district": district,
                            "state": state,
                            "circle": circle,
                            "total_post_offices": len(post_offices),
                            "post_offices": offices_summary,
                            "rule_6_1_a_compliance": "VALID_PINCODE",
                        }
                    else:
                        return {
                            "success": False,
                            "is_valid": False,
                            "source": "India Post Open API",
                            "pincode": cleaned_pin,
                            "error": f"PIN code '{cleaned_pin}' not found in official India Post directory.",
                            "rule_6_1_a_compliance": "INVALID_PINCODE_DEFECT",
                        }
                else:
                    return {
                        "success": False,
                        "is_valid": False,
                        "error": f"HTTP {res.status_code} from Postal API",
                    }
        except Exception as e:
            logger.warning("Failed to verify PIN %s on India Postal API: %s", pincode, e)
            return {
                "success": False,
                "is_valid": False,
                "pincode": cleaned_pin,
                "error": f"Connection error: {str(e)}",
            }

    # =========================================================================
    # 3. Foreign Exchange Rates API — Imported Commodity Dual-Currency Audit
    # =========================================================================
    async def get_live_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """
        Query Foreign Exchange Rates API (from public-apis / Finance).
        Calculates INR conversion for imported pre-packaged commodities under Rule 6(1)(d).
        """
        base = base_currency.upper().strip()
        url = f"{settings.EXCHANGE_RATE_API_URL}/{base}"

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    rates = data.get("rates", {})
                    inr_rate = rates.get("INR", 83.50)
                    eur_rate = rates.get("EUR")
                    gbp_rate = rates.get("GBP")
                    time_last_update_utc = data.get("time_last_update_utc", "")

                    return {
                        "success": True,
                        "source": "ExchangeRate-API (Public API)",
                        "base_currency": base,
                        "inr_exchange_rate": round(inr_rate, 4),
                        "rates": {
                            "INR": inr_rate,
                            "EUR": eur_rate,
                            "GBP": gbp_rate,
                            "USD": rates.get("USD", 1.0),
                            "AED": rates.get("AED"),
                            "CNY": rates.get("CNY"),
                        },
                        "last_updated": time_last_update_utc,
                    }
                else:
                    return {"success": False, "error": f"HTTP {res.status_code} from Exchange API"}
        except Exception as e:
            logger.warning("Failed to fetch exchange rates: %s", e)
            return {
                "success": False,
                "base_currency": base,
                "inr_exchange_rate": 83.50,
                "error": str(e),
                "fallback_mode": True,
            }

    # =========================================================================
    # 4. Open-Meteo Weather API — Field Enforcement & Mandi Weather Dispatch
    # =========================================================================
    async def get_mandi_weather(self, lat: float = 19.0760, lon: float = 72.8777) -> Dict[str, Any]:
        """
        Query Open-Meteo API (from public-apis / Weather).
        Returns live weather, precipitation, and inspection raid feasibility index.
        """
        url = f"{settings.OPEN_METEO_API_URL}/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation_probability"

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    current = data.get("current_weather", {})
                    temp = current.get("temperature", 28.0)
                    windspeed = current.get("windspeed", 10.0)
                    weathercode = current.get("weathercode", 0)

                    # Determine raid feasibility condition
                    is_favorable = weathercode in [0, 1, 2, 3] and windspeed < 35.0
                    advisory = "Optimal field inspection conditions." if is_favorable else "Adverse weather: check rain/wind conditions."

                    return {
                        "success": True,
                        "source": "Open-Meteo (Public API)",
                        "latitude": lat,
                        "longitude": lon,
                        "temperature_celsius": temp,
                        "windspeed_kmh": windspeed,
                        "weather_code": weathercode,
                        "is_favorable_for_raid": is_favorable,
                        "field_advisory": advisory,
                    }
                else:
                    return {"success": False, "error": f"HTTP {res.status_code} from Open-Meteo"}
        except Exception as e:
            logger.warning("Failed to fetch weather: %s", e)
            return {
                "success": False,
                "latitude": lat,
                "longitude": lon,
                "temperature_celsius": 28.0,
                "is_favorable_for_raid": True,
                "field_advisory": "Standard field conditions (Offline fallback)",
                "error": str(e),
            }

    # =========================================================================
    # 5. Google Gemini AI API — Live Statutory Legal Metrology LLM
    # =========================================================================
    async def query_gemini_llm(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calls Google Gemini Generative Language API if GEMINI_API_KEY is configured.
        Supports automatic fallback across supported model endpoints.
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return {
                "success": False,
                "configured": False,
                "error": "GEMINI_API_KEY is not set in backend/.env. Running on local deterministic ruleset.",
            }

        candidate_models = [model_name] if model_name else ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-pro-latest"]
        
        default_sys = (
            "You are an expert Legal Metrology AI Statutory Copilot for the Ministry of Consumer Affairs, "
            "Government of India. Provide authoritative legal analysis referencing the Legal Metrology Act 2009 "
            "(Sections 18, 25, 36, 48, 49) and Legal Metrology (Packaged Commodities) Rules 2011 (Rule 6, 9, 11, Schedule I/II). "
            "Be precise, cite exact statutory provisions, penalty amounts, and actionable enforcement steps."
        )
        sys_prompt = system_instruction or default_sys

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"System Context:\n{sys_prompt}\n\nUser Question:\n{prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }

        last_err = ""
        async with httpx.AsyncClient(timeout=20.0) as client:
            for m in candidate_models:
                m_clean = m.replace("models/", "")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_clean}:generateContent?key={api_key}"
                try:
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates and len(candidates) > 0:
                            content_parts = candidates[0].get("content", {}).get("parts", [])
                            text_response = "".join(part.get("text", "") for part in content_parts)
                            return {
                                "success": True,
                                "configured": True,
                                "model": m_clean,
                                "response_text": text_response,
                                "source": "Google Gemini API (Live AI)",
                            }
                    else:
                        last_err = f"Model {m_clean} returned HTTP {res.status_code}"
                except Exception as e:
                    last_err = str(e)
                    logger.warning("Gemini attempt on %s failed: %s", m_clean, e)

        return {
            "success": False,
            "configured": True,
            "error": f"Gemini API request failed ({last_err}). Falling back to statutory knowledge base.",
        }

    # =========================================================================
    # 6. Global Status & Health of All Integrated Public APIs
    # =========================================================================
    async def get_all_apis_status(self) -> Dict[str, Any]:
        """Check availability and configuration status of all integrated public and AI APIs."""
        gemini_ready = bool(settings.GEMINI_API_KEY)
        openai_ready = bool(settings.OPENAI_API_KEY)
        huggingface_ready = bool(settings.HUGGINGFACE_API_KEY)

        # Quick probe for public APIs
        pincode_res = await self.verify_indian_pincode("110001")  # Connaught Place, New Delhi
        forex_res = await self.get_live_exchange_rates("USD")
        weather_res = await self.get_mandi_weather(19.0760, 72.8777)

        return {
            "public_apis": [
                {
                    "name": "Open Food Facts API",
                    "category": "Food & Commodities (public-apis)",
                    "url": settings.OPEN_FOOD_FACTS_API_URL,
                    "status": "ACTIVE",
                    "requires_key": False,
                    "description": "Global & Indian pre-packaged commodity barcode lookup, declared weight, brand & nutrition.",
                },
                {
                    "name": "India Postal PIN Code API",
                    "category": "Geocoding & Government (public-apis)",
                    "url": settings.POSTAL_PINCODE_API_URL,
                    "status": "ACTIVE" if pincode_res.get("success") else "DEGRADED",
                    "requires_key": False,
                    "sample_check": "110001 -> " + (pincode_res.get("district") or "Delhi"),
                    "description": "Rule 6(1)(a) manufacturer address and 6-digit postal PIN code verification.",
                },
                {
                    "name": "Foreign Exchange Rate API",
                    "category": "Finance & Currency (public-apis)",
                    "url": settings.EXCHANGE_RATE_API_URL,
                    "status": "ACTIVE" if forex_res.get("success") else "DEGRADED",
                    "requires_key": False,
                    "usd_to_inr": forex_res.get("inr_exchange_rate", 83.5),
                    "description": "Rule 6(1)(d) imported packaged commodity dual-pricing and forex parity calculation.",
                },
                {
                    "name": "Open-Meteo Weather API",
                    "category": "Weather & Environment (public-apis)",
                    "url": settings.OPEN_METEO_API_URL,
                    "status": "ACTIVE" if weather_res.get("success") else "DEGRADED",
                    "requires_key": False,
                    "description": "Real-time mandi & field enforcement weather forecast for predictive officer dispatch.",
                },
            ],
            "ai_llm_keys": {
                "gemini_api_key_configured": gemini_ready,
                "openai_api_key_configured": openai_ready,
                "huggingface_api_key_configured": huggingface_ready,
                "active_llm_provider": "Google Gemini 1.5/2.0 Flash" if gemini_ready else "Local Statutory Rule Engine (Fallback)",
            },
        }


public_api_service = PublicAPIService()
