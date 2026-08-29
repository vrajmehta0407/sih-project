"""
schemas/citizen_bot.py
======================
Stage 22 — WhatsApp / Telegram Citizen Enforcement Bot Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BotIncomingMessage(BaseModel):
    """Incoming conversational message or webhook from WhatsApp/Telegram."""
    sender_phone: str = Field(..., example="+919876543210")
    sender_name: Optional[str] = Field(None, example="Rahul Sharma")
    message_text: str = Field(..., example="MRP was 150 but store charged 180 at Bandra")
    media_url: Optional[str] = Field(None, example="https://example.com/uploads/label.jpg")
    platform: str = Field("WHATSAPP", example="WHATSAPP")  # "WHATSAPP", "TELEGRAM", "SMS"


class BotReplyResponse(BaseModel):
    """Conversational reply returned to consumer with statutory advice and grievance ticket."""
    reply_text: str
    detected_language: str  # "en", "hi", "hinglish"
    is_violation_identified: bool
    infraction_type: Optional[str]
    statutory_reference: Optional[str]
    auto_generated_ticket_number: Optional[str]
    created_at: datetime
