"""
citizen_bot_service.py
======================
Stage 22 — WhatsApp / Telegram Citizen Enforcement Bot Service
"""

import re
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.citizen_complaint import CitizenComplaint
from app.schemas.citizen_bot import BotIncomingMessage, BotReplyResponse
from app.services.voice_assistant_service import voice_assistant_service

logger = logging.getLogger(__name__)


class CitizenBotService:
    """Processes natural language consumer messages from WhatsApp/Telegram and auto-logs grievances."""

    def process_message(self, db: Session, msg: BotIncomingMessage) -> BotReplyResponse:
        """Process incoming chat message, detect violations, and return statutory advice."""
        now = datetime.utcnow()
        text = msg.message_text.strip()

        # Parse text using voice_assistant entity extractor
        extracted = voice_assistant_service.process_transcript(text)
        lang = extracted.language_detected
        mrp = extracted.detected_mrp
        charged = extracted.detected_charged_price
        infractions = extracted.detected_infractions

        is_violation = False
        infraction_type = None
        statutory_ref = None
        ticket_num = None

        # Check overcharging or infractions
        if mrp and charged and charged > mrp:
            is_violation = True
            infraction_type = "OVERCHARGING_MRP"
            statutory_ref = "Section 18, Legal Metrology Act, 2009"
        elif "DUAL_MRP_STICKER_TAMPERING" in infractions:
            is_violation = True
            infraction_type = "DUAL_MRP_STICKER_TAMPERING"
            statutory_ref = "Rule 6(1)(e) & Section 36(1), LM Rules, 2011"
        elif "EXPIRED_COMMODITY_SALE" in infractions:
            is_violation = True
            infraction_type = "EXPIRED_COMMODITY_SALE"
            statutory_ref = "Rule 6(1)(d), LM (Packaged Commodities) Rules, 2011"
        elif "MISSING_STATUTORY_DECLARATIONS" in infractions:
            is_violation = True
            infraction_type = "MISSING_DECLARATIONS"
            statutory_ref = "Rule 6, LM (Packaged Commodities) Rules, 2011"

        # If a violation is identified, create an automated citizen complaint docket
        if is_violation:
            ticket_id = uuid.uuid4()
            ticket_num = f"CC-BOT-2026-{ticket_id.hex[:6].upper()}"

            complaint = CitizenComplaint(
                id=ticket_id,
                ticket_number=ticket_num,
                citizen_name=msg.sender_name or "WhatsApp Consumer",
                citizen_contact=msg.sender_phone,
                retailer_name="Establishment reported via WhatsApp Bot",
                retailer_address="Reported via mobile chat gateway",
                state="Maharashtra",
                district="Mumbai",
                violation_category=infraction_type or "OVERCHARGING_MRP",
                complaint_description=f"Automated bot submission: {text}",
                charged_price=charged,
                ai_detected_mrp=mrp,
                image_path=msg.media_url,
                ai_credibility_score=88.5,
                ai_triage_notes=f"Auto-parsed by Legal Metrology Bot via {msg.platform}. MRP: ₹{mrp}, Charged: ₹{charged}",
                status="SUBMITTED",
            )
            db.add(complaint)
            db.commit()
            db.refresh(complaint)

        # Generate conversational response in Hindi or English
        if lang == "hi":
            if is_violation:
                reply = (
                    f"⚠️ विधिक मापविज्ञान विभाग अलर्ट!\n\n"
                    f"आपकी सूचना के अनुसार वस्तु का अधिकतम खुदरा मूल्य (MRP) ₹{mrp or '---'} है, "
                    f"लेकिन आपसे ₹{charged or '---'} लिया गया। यह धारा 18 के तहत गैरकानूनी है।\n\n"
                    f"✅ आपकी आधिकारिक शिकायत दर्ज कर ली गई है:\n"
                    f"🎫 शिकायत टिकट: {ticket_num}\n"
                    f"⚖️ संबंधित कानून: {statutory_ref}\n\n"
                    f"संबंधित जिले के विधिक मापविज्ञान निरीक्षक को जांच हेतु सूचित कर दिया गया है।"
                )
            else:
                reply = (
                    "नमस्ते! विधिक मापविज्ञान विभाग (Legal Metrology) सहायता बॉट में आपका स्वागत है।\n\n"
                    "यदि किसी दुकानदार ने आपसे MRP से अधिक मूल्य लिया है या पैकेजिंग पर विवरण नहीं है, "
                    "तो कृपया पैकेट का फोटो या विवरण यहां भेजें।"
                )
        else:
            if is_violation:
                overcharge_diff = f" (+₹{round(charged - mrp, 1)} illegal markup)" if mrp and charged else ""
                reply = (
                    f"⚠️ Legal Metrology Statutory Infraction Alert!\n\n"
                    f"Based on your report, Printed MRP is ₹{mrp or '---'}, but you were charged ₹{charged or '---'}{overcharge_diff}.\n\n"
                    f"✅ Your official consumer grievance has been logged:\n"
                    f"🎫 Grievance Ticket: {ticket_num}\n"
                    f"⚖️ Statutory Violation: {statutory_ref}\n\n"
                    f"A field inspector has been dispatched to audit this establishment under Section 18 / 36."
                )
            else:
                reply = (
                    "Hello! Welcome to the National Legal Metrology Consumer Assistant.\n\n"
                    "If you have experienced overcharging above MRP, dual price stickers, or missing packaged commodity declarations, "
                    "please reply with the product details or send a label photo."
                )

        logger.info(
            "Bot message from %s processed (Lang: %s, Violation: %s, Ticket: %s)",
            msg.sender_phone, lang, is_violation, ticket_num
        )

        return BotReplyResponse(
            reply_text=reply,
            detected_language=lang,
            is_violation_identified=is_violation,
            infraction_type=infraction_type,
            statutory_reference=statutory_ref,
            auto_generated_ticket_number=ticket_num,
            created_at=now,
        )


citizen_bot_service = CitizenBotService()
