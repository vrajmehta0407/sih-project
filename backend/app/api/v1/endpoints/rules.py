from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, require_admin
from app.db.session import get_db
from app.models.rule import Rule, RuleVersion
from app.models.user import User
from app.schemas.rule import (
    RuleResponse, RuleCreate, RuleUpdate,
    RuleVersionResponse, RuleVersionCreate
)
from app.models.state_rule_override import StateRuleOverride
from app.schemas.state_override import StateRuleOverrideCreate, StateRuleOverrideResponse
from app.schemas.common import ResponseEnvelope
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/versions", response_model=ResponseEnvelope[List[RuleVersionResponse]], summary="List All Rule Versions")
def list_rule_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    versions = db.query(RuleVersion).order_by(RuleVersion.published_at.desc()).all()
    return ResponseEnvelope(
        success=True,
        message="Rule versions retrieved successfully",
        data=versions
    )


@router.get("/active", response_model=ResponseEnvelope[RuleVersionResponse], summary="Get Currently Active Rule Version & Rules")
def get_active_rule_version(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    active_version = db.query(RuleVersion).filter(RuleVersion.is_active == True).order_by(RuleVersion.published_at.desc()).first()
    if not active_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active Legal Metrology rule version found."
        )
    return ResponseEnvelope(
        success=True,
        message="Active rule version retrieved",
        data=active_version
    )


@router.get("/", response_model=ResponseEnvelope[List[RuleResponse]], summary="List Rules (with optional state override filter)")
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    version_id: Optional[str] = Query(None, description="Filter by Rule Version ID"),
    field: Optional[str] = Query(None, description="Filter by validated field (e.g. mrp, net_quantity)"),
    state: Optional[str] = Query(None, description="Filter rules applying to a specific state")
) -> Any:
    query = db.query(Rule).filter(Rule.is_active == True)
    if version_id:
        query = query.filter(Rule.version_id == version_id)
    else:
        # Default to active version rules
        active_ver = db.query(RuleVersion).filter(RuleVersion.is_active == True).first()
        if active_ver:
            query = query.filter(Rule.version_id == active_ver.id)
            
    if field:
        query = query.filter(Rule.field_to_validate == field)
    if state:
        query = query.filter((Rule.state_override == None) | (Rule.state_override.ilike(f"%{state}%")))

    rules = query.all()
    return ResponseEnvelope(
        success=True,
        message="Legal Metrology rules retrieved successfully",
        data=rules
    )


@router.post("/", response_model=ResponseEnvelope[RuleResponse], summary="Create or Add New Rule (Admin only)")
def create_rule(
    rule_in: RuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    version = db.query(RuleVersion).filter(RuleVersion.id == rule_in.version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified Rule Version does not exist."
        )

    rule = Rule(
        version_id=rule_in.version_id,
        rule_code=rule_in.rule_code,
        title=rule_in.title,
        statutory_source=rule_in.statutory_source,
        statutory_penalty_source=rule_in.statutory_penalty_source,
        penalty_first_offence=rule_in.penalty_first_offence,
        penalty_repeat_offence=rule_in.penalty_repeat_offence,
        description=rule_in.description,
        field_to_validate=rule_in.field_to_validate,
        is_mandatory=rule_in.is_mandatory,
        validation_type=rule_in.validation_type,
        validation_parameters=rule_in.validation_parameters,
        severity=rule_in.severity,
        state_override=rule_in.state_override,
        is_active=rule_in.is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    audit_service.log(
        db=db,
        action="RULE_CREATED",
        entity_name="Rule",
        entity_id=rule.id,
        user_id=current_admin.id,
        request=request,
        details={"rule_code": rule.rule_code, "source": rule.statutory_source}
    )

    return ResponseEnvelope(
        success=True,
        message="Rule created successfully",
        data=rule
    )


# ===========================================================================
# State-Specific Jurisdiction Rule Overrides (Section 53 LM Act 2009)
# ===========================================================================

@router.get(
    "/state-overrides",
    response_model=ResponseEnvelope[List[StateRuleOverrideResponse]],
    summary="List State-Specific Rule Overrides & Exemptions",
)
def list_state_overrides(
    state_code: Optional[str] = Query(None, description="Filter by state code e.g. MH, TN"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    List all active state-level amendments, exemptions, and local language mandates
    gazetted under Section 53 of the Legal Metrology Act, 2009.
    """
    query = db.query(StateRuleOverride).filter(StateRuleOverride.is_active == True)
    if state_code:
        query = query.filter(StateRuleOverride.state_code == state_code.upper())
    overrides = query.order_by(StateRuleOverride.created_at.desc()).all()
    return ResponseEnvelope(
        success=True,
        message="State rule overrides retrieved",
        data=overrides,
    )


@router.post(
    "/state-overrides",
    response_model=ResponseEnvelope[StateRuleOverrideResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create State-Specific Rule Override or Exemption",
)
def create_state_override(
    override_in: StateRuleOverrideCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
) -> Any:
    """
    Create a state-level statutory override or local exemption under Section 53.
    Restricted to Enforcement Directors (admin).
    """
    override = StateRuleOverride(
        state_code=override_in.state_code.upper(),
        state_name=override_in.state_name,
        rule_code=override_in.rule_code,
        override_type=override_in.override_type,
        description=override_in.description,
        parameters=override_in.parameters,
        gazette_notification_ref=override_in.gazette_notification_ref,
        is_active=override_in.is_active,
        created_by_email=current_admin.email,
    )
    db.add(override)
    db.commit()
    db.refresh(override)

    return ResponseEnvelope(
        success=True,
        message=f"State override for {override.state_code} created successfully",
        data=override,
    )
