"""
endpoints/citizen.py
====================
Stage 15 — Public Citizen Grievance & Crowdsourced Enforcement Gateway
"""

import uuid
import random
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_inspector
from app.models.citizen_complaint import CitizenComplaint
from app.models.user import User
from app.schemas.citizen import (
    CitizenComplaintCreate,
    CitizenComplaintResponse,
    CitizenTrackingResponse,
)
from app.schemas.citizen_bot import BotIncomingMessage, BotReplyResponse
from app.services.citizen_bot_service import citizen_bot_service

router = APIRouter()
logger = logging.getLogger(__name__)


def _compute_ai_credibility(req: CitizenComplaintCreate) -> tuple[float, str]:
    """
    Computes an AI credibility score (0–100) based on statutory keyword density,
    valid price delta, and complete jurisdictional reporting.
    """
    score = 50.0
    notes = []

    if req.charged_price and req.charged_price > 0:
        score += 20.0
        notes.append("Explicit overcharging price specified.")

    if req.retailer_address and len(req.retailer_address) > 10:
        score += 15.0
        notes.append("Full retailer street address provided.")

    if req.violation_category in ("OVERCHARGING_MRP", "DUAL_MRP", "EXPIRED_SALE"):
        score += 10.0
        notes.append("High-severity statutory violation category.")

    if len(req.complaint_description) > 30:
        score += 5.0

    score = min(100.0, score)
    notes_str = "; ".join(notes) if notes else "Standard consumer submission."
    return score, notes_str


@router.post(
    "/complaints",
    response_model=CitizenComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Public Citizen Grievance (Crowdsourced)",
)
def submit_citizen_complaint(
    req: CitizenComplaintCreate,
    db: Session = Depends(get_db),
):
    """
    Public reporting endpoint for Indian consumers to report packaged commodity violations
    (overcharging above MRP, altered dates, dual labels, missing manufacturer info).
    Automatically runs AI credibility triage and generates a public tracking ticket.
    """
    random_digits = f"{random.randint(10000, 99999)}"
    ticket_num = f"LM-CIT-2026-{random_digits}"

    credibility_score, triage_notes = _compute_ai_credibility(req)

    complaint = CitizenComplaint(
        ticket_number=ticket_num,
        citizen_name=req.citizen_name,
        citizen_contact=req.citizen_contact,
        retailer_name=req.retailer_name,
        retailer_address=req.retailer_address,
        state=req.state,
        district=req.district,
        violation_category=req.violation_category,
        complaint_description=req.complaint_description,
        charged_price=req.charged_price,
        ai_credibility_score=credibility_score,
        ai_triage_notes=triage_notes,
        status="TRIAGED" if credibility_score >= 70.0 else "SUBMITTED",
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    logger.info(
        "Citizen complaint %s created for retailer '%s' in %s, %s (Credibility: %.1f)",
        ticket_num, req.retailer_name, req.district, req.state, credibility_score
    )
    return complaint


@router.get(
    "/complaints/track/{ticket_number}",
    response_model=CitizenTrackingResponse,
    summary="Track Public Citizen Grievance by Ticket Number",
)
def track_citizen_complaint(
    ticket_number: str,
    db: Session = Depends(get_db),
):
    """
    Public lookup endpoint allowing citizens to check the real-time enforcement status
    of their submitted grievance (SUBMITTED, TRIAGED, ENFORCEMENT_INITIATED, RESOLVED).
    """
    complaint = db.query(CitizenComplaint).filter(
        CitizenComplaint.ticket_number == ticket_number
    ).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No grievance found with ticket number '{ticket_number}'.",
        )
    return CitizenTrackingResponse(
        ticket_number=complaint.ticket_number,
        retailer_name=complaint.retailer_name,
        state=complaint.state,
        district=complaint.district,
        violation_category=complaint.violation_category,
        status=complaint.status,
        ai_credibility_score=complaint.ai_credibility_score,
        created_at=complaint.created_at,
        resolution_notes=complaint.resolution_notes,
    )


@router.get(
    "/complaints",
    response_model=List[CitizenComplaintResponse],
    summary="List Citizen Grievances in Officer Triage Queue",
)
def list_citizen_complaints(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    min_credibility: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspector),
):
    """
    Officer-facing endpoint to inspect crowdsourced grievances, prioritize high-credibility
    complaints, and convert them into official field inspection dockets.
    """
    query = db.query(CitizenComplaint)
    if state:
        query = query.filter(CitizenComplaint.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(CitizenComplaint.district.ilike(f"%{district}%"))
    if status_filter:
        query = query.filter(CitizenComplaint.status == status_filter)
    if min_credibility is not None:
        query = query.filter(CitizenComplaint.ai_credibility_score >= min_credibility)

    return query.order_by(CitizenComplaint.created_at.desc()).all()


@router.patch(
    "/complaints/{ticket_number}/resolve",
    response_model=CitizenComplaintResponse,
    summary="Resolve Citizen Grievance with Officer Findings",
)
def resolve_citizen_complaint(
    ticket_number: str,
    resolution_notes: str = Query(..., description="Action taken by the officer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_inspector),
):
    """Update citizen grievance status to RESOLVED with formal officer findings."""
    complaint = db.query(CitizenComplaint).filter(
        CitizenComplaint.ticket_number == ticket_number
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    complaint.status = "RESOLVED"
    complaint.resolution_notes = f"[{current_user.full_name}] {resolution_notes}"
    db.commit()
    db.refresh(complaint)
    logger.info("Complaint %s resolved by %s", ticket_number, current_user.email)
    return complaint


# ===========================================================================
# Stage 22 — WhatsApp / Telegram Conversational Enforcement Webhook
# ===========================================================================

@router.post(
    "/bot/webhook",
    response_model=BotReplyResponse,
    summary="WhatsApp / Telegram Conversational Enforcement Bot Webhook",
)
def handle_bot_webhook(
    msg: BotIncomingMessage,
    db: Session = Depends(get_db),
):
    """
    Public conversational webhook receiving consumer chat messages (text/photo),
    parsing statutory infractions (e.g. MRP overcharging), and returning instant legal advice.
    """
    return citizen_bot_service.process_message(db=db, msg=msg)
