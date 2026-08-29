"""
voice_assistant_service.py
===========================
Stage 16 — AI Voice-Assisted Field Dictation Assistant Service

Parses spoken voice memos in English and Hindi recorded during physical
field inspections, extracts structured findings (prices, batch numbers, violations),
and auto-populates the official inspection docket.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class VoiceNoteResult:
    """Structured result parsed from officer voice dictation."""
    raw_transcript: str
    language_detected: str  # "en", "hi", "hinglish"
    detected_mrp: Optional[float]
    detected_charged_price: Optional[float]
    detected_batch: Optional[str]
    detected_infractions: List[str]
    formatted_officer_note: str


class VoiceAssistantService:
    """Extracts structured legal metrology observations from speech transcripts."""

    def process_transcript(self, transcript: str) -> VoiceNoteResult:
        """
        Extracts structured values and statutory violations from officer dictation.
        Handles English, Hindi, and Hinglish dictation patterns.
        """
        text = transcript.strip()
        lang = "en"
        if any(c >= '\u0900' and c <= '\u097f' for c in text):
            lang = "hi"
        elif any(w in text.lower() for w in ("rupaye", "mrp se jyada", "sticker lagaya", "kimat")):
            lang = "hinglish"

        # Extract MRP / Prices
        detected_mrp = None
        detected_charged = None

        mrp_match = re.search(r'(?:mrp|printed|original)(?:\s+(?:mrp|price|rate|value))?\s*(?:is|of|was|hai|₹|rs\.?|rupees|:)?\s*([0-9]+(?:\.[0-9]{1,2})?)', text, re.IGNORECASE)
        if mrp_match:
            try:
                detected_mrp = float(mrp_match.group(1))
            except ValueError:
                pass

        charged_match = re.search(r'(?:charged|selling|sold at|shelf price|bech raha|liya|sale price)(?:\s+(?:at|for|is|rate|price))?\s*(?:₹|rs\.?|rupees|:)?\s*([0-9]+(?:\.[0-9]{1,2})?)', text, re.IGNORECASE)
        if charged_match:
            try:
                detected_charged = float(charged_match.group(1))
            except ValueError:
                pass

        # Extract Batch Number
        detected_batch = None
        batch_match = re.search(r'batch(?:\s+(?:no\.?|number|code|#))?\s*(?:is|was|:|#|-)?\s*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
        if batch_match:
            candidate = batch_match.group(1)
            if candidate.lower() not in ("is", "was", "the", "a", "an"):
                detected_batch = candidate

        # Detect Infractions mentioned (English + Hindi/Devanagari)
        infractions = []
        text_lower = text.lower()
        if (detected_mrp and detected_charged and detected_charged > detected_mrp) or any(w in text_lower for w in ("overcharge", "above mrp", "extra", "jyada", "adhik", "ज्यादा", "अधिक", "ओवरचार्ज")):
            infractions.append("OVERCHARGING_ABOVE_MRP")
        if any(w in text_lower for w in ("sticker", "pasted", "dual mrp", "chipkaya", "overprint", "स्टीकर", "चिपकाया", "ड्युअल")):
            infractions.append("DUAL_MRP_STICKER_TAMPERING")
        if any(w in text_lower for w in ("expired", "date smudged", "best before past", "tarikh", "एक्सपायरी", "तारीख")):
            infractions.append("EXPIRED_COMMODITY_SALE")
        if any(w in text_lower for w in ("customer care", "address missing", "missing declaration", "missing", "pata nahi", "कस्टमर केयर", "लापता")):
            infractions.append("MISSING_STATUTORY_DECLARATIONS")

        formatted_note = (
            f"[Voice Memo Transcription] {text}\n"
            f"• Extracted MRP: {f'₹{detected_mrp}' if detected_mrp else 'Not explicitly stated'}\n"
            f"• Extracted Charged Price: {f'₹{detected_charged}' if detected_charged else 'Not explicitly stated'}\n"
            f"• Batch Reference: {detected_batch or 'N/A'}\n"
            f"• Detected Infractions: {', '.join(infractions) if infractions else 'None identified'}"
        )

        return VoiceNoteResult(
            raw_transcript=text,
            language_detected=lang,
            detected_mrp=detected_mrp,
            detected_charged_price=detected_charged,
            detected_batch=detected_batch,
            detected_infractions=infractions,
            formatted_officer_note=formatted_note,
        )


voice_assistant_service = VoiceAssistantService()
