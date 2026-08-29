from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    require_admin,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.schemas.common import ResponseEnvelope
from app.services.audit_service import audit_service

router = APIRouter()


@router.post("/login", response_model=Token, summary="Inspector & Admin Login (OAuth2 Form)")
def login_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        extra_claims={"role": user.role, "email": user.email, "district": user.jurisdiction_district}
    )
    
    audit_service.log(
        db=db,
        action="USER_LOGIN",
        entity_name="User",
        entity_id=user.id,
        user_id=user.id,
        request=request,
        details={"email": user.email, "role": user.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }


@router.post("/login/json", response_model=Token, summary="JSON Body Login (for Mobile / Web Client)")
def login_json(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        extra_claims={"role": user.role, "email": user.email, "district": user.jurisdiction_district}
    )

    audit_service.log(
        db=db,
        action="USER_LOGIN_JSON",
        entity_name="User",
        entity_id=user.id,
        user_id=user.id,
        request=request,
        details={"email": user.email, "role": user.role}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
    }


@router.get("/me", response_model=ResponseEnvelope[UserResponse], summary="Get Current Authenticated User")
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return ResponseEnvelope(
        success=True,
        message="User profile fetched successfully",
        data=current_user
    )


@router.post("/register-inspector", response_model=ResponseEnvelope[UserResponse], summary="Register New Inspector (Admin only)")
def register_inspector(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    if user_in.badge_number:
        existing_badge = db.query(User).filter(User.badge_number == user_in.badge_number).first()
        if existing_badge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this badge number already exists."
            )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        badge_number=user_in.badge_number,
        phone_number=user_in.phone_number,
        jurisdiction_district=user_in.jurisdiction_district,
        jurisdiction_state=user_in.jurisdiction_state,
        is_active=user_in.is_active if user_in.is_active is not None else True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    audit_service.log(
        db=db,
        action="INSPECTOR_REGISTERED",
        entity_name="User",
        entity_id=user.id,
        user_id=current_admin.id,
        request=request,
        details={"new_user_email": user.email, "role": user.role, "badge": user.badge_number}
    )

    return ResponseEnvelope(
        success=True,
        message="Inspector registered successfully",
        data=user
    )
