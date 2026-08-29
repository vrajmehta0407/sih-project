"""
test_citizen_bot.py
===================
Stage 22 — Unit & API Tests for WhatsApp/Telegram Citizen Enforcement Bot
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.citizen_bot import BotIncomingMessage
from app.services.citizen_bot_service import citizen_bot_service
from app.db.session import SessionLocal
from app.models.citizen_complaint import CitizenComplaint

client = TestClient(app)


# ── Citizen Bot Unit Tests ───────────────────────────────────────────────────

def test_citizen_bot_service_english_overcharging():
    db = SessionLocal()
    try:
        msg = BotIncomingMessage(
            sender_phone="+919876543210",
            sender_name="Amit Kumar",
            message_text="Printed MRP is 150 but store charged 180 rupees at Dadar West",
            platform="WHATSAPP",
        )
        res = citizen_bot_service.process_message(db, msg)
        assert res.is_violation_identified is True
        assert res.infraction_type == "OVERCHARGING_MRP"
        assert res.auto_generated_ticket_number.startswith("CC-BOT-2026-")
        assert "Section 18" in res.statutory_reference
        assert "150" in res.reply_text
        assert "180" in res.reply_text
    finally:
        db.close()


def test_citizen_bot_service_hindi_overcharging():
    db = SessionLocal()
    try:
        msg = BotIncomingMessage(
            sender_phone="+919811122233",
            sender_name="सुरेश शर्मा",
            message_text="दुकानदार ने एमआरपी 100 की जगह 140 रुपया ज्यादा लिया और स्टीकर चिपकाया है",
            platform="WHATSAPP",
        )
        res = citizen_bot_service.process_message(db, msg)
        assert res.detected_language == "hi"
        assert res.is_violation_identified is True
        assert "विधिक मापविज्ञान" in res.reply_text
        assert "शिकायत टिकट" in res.reply_text
    finally:
        db.close()


def test_citizen_bot_service_sticker_tampering():
    db = SessionLocal()
    try:
        msg = BotIncomingMessage(
            sender_phone="+919922334455",
            message_text="Dual sticker pasted over original price on cooking oil container",
            platform="TELEGRAM",
        )
        res = citizen_bot_service.process_message(db, msg)
        assert res.is_violation_identified is True
        assert res.infraction_type == "DUAL_MRP_STICKER_TAMPERING"
    finally:
        db.close()


def test_citizen_bot_service_general_greeting():
    db = SessionLocal()
    try:
        msg = BotIncomingMessage(
            sender_phone="+919900112233",
            message_text="Hello, how can I file a complaint?",
            platform="WHATSAPP",
        )
        res = citizen_bot_service.process_message(db, msg)
        assert res.is_violation_identified is False
        assert res.auto_generated_ticket_number is None
        assert "Welcome to the National Legal Metrology Consumer Assistant" in res.reply_text
    finally:
        db.close()


def test_citizen_bot_service_creates_db_complaint():
    db = SessionLocal()
    try:
        phone = "+919870001122"
        msg = BotIncomingMessage(
            sender_phone=phone,
            sender_name="Pooja Mehta",
            message_text="Retailer selling expired milk packet. Best before date expired last month.",
            platform="WHATSAPP",
        )
        res = citizen_bot_service.process_message(db, msg)
        assert res.is_violation_identified is True
        # Verify in DB
        complaint = db.query(CitizenComplaint).filter(CitizenComplaint.ticket_number == res.auto_generated_ticket_number).first()
        assert complaint is not None
        assert complaint.citizen_contact == phone
        assert complaint.status == "SUBMITTED"
        assert complaint.ai_credibility_score > 80.0
    finally:
        db.close()


# ── Webhook API Tests ────────────────────────────────────────────────────────

def test_citizen_bot_webhook_api_200_english():
    payload = {
        "sender_phone": "+919876543210",
        "sender_name": "Rohan Verma",
        "message_text": "MRP was 200, retailer charged 250 at market",
        "platform": "WHATSAPP",
    }
    resp = client.post("/api/v1/citizen/bot/webhook", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_violation_identified"] is True
    assert data["auto_generated_ticket_number"].startswith("CC-BOT-2026-")
    assert "Section 18" in data["statutory_reference"]


def test_citizen_bot_webhook_api_200_hindi():
    payload = {
        "sender_phone": "+919811223344",
        "message_text": "नमस्ते, मुझे शिकायत करनी है",
        "platform": "WHATSAPP",
    }
    resp = client.post("/api/v1/citizen/bot/webhook", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_language"] == "hi"
    assert data["is_violation_identified"] is False


def test_citizen_bot_webhook_response_fields():
    payload = {
        "sender_phone": "+919800000000",
        "message_text": "Missing customer care details and address on packet",
        "platform": "TELEGRAM",
    }
    resp = client.post("/api/v1/citizen/bot/webhook", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "reply_text" in data
    assert "detected_language" in data
    assert "created_at" in data


def test_citizen_bot_handles_empty_message_gracefully():
    payload = {
        "sender_phone": "+919800000000",
        "message_text": "hi",
        "platform": "WHATSAPP",
    }
    resp = client.post("/api/v1/citizen/bot/webhook", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_violation_identified"] is False


def test_citizen_bot_telegram_platform_parsing():
    payload = {
        "sender_phone": "@telegram_user_99",
        "sender_name": "Telegram User",
        "message_text": "MRP 300, charged 360",
        "platform": "TELEGRAM",
    }
    resp = client.post("/api/v1/citizen/bot/webhook", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_violation_identified"] is True
    assert data["infraction_type"] == "OVERCHARGING_MRP"
